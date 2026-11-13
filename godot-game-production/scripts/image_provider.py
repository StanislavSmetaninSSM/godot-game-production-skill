"""Resolve a registered image-provider adapter without invoking generation."""

import argparse
import json
from pathlib import Path, PurePosixPath, PureWindowsPath
import re
import stat
import sys


_ID = re.compile(r"[a-z][a-z0-9-]*")


class SchemaError(Exception):
    """The registry, selection, path, or invocation is malformed or unsafe."""


class ResolutionError(Exception):
    """A valid selection cannot be resolved to one available provider."""


def _object_without_duplicate_keys(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise SchemaError("duplicate JSON key")
        result[key] = value
    return result


def _read_json(path: Path, description: str) -> dict[str, object]:
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError):
        raise SchemaError(f"cannot read {description}") from None
    try:
        value = json.loads(text, object_pairs_hook=_object_without_duplicate_keys)
    except SchemaError:
        raise
    except (json.JSONDecodeError, RecursionError):
        raise SchemaError(f"malformed {description} JSON") from None
    if not isinstance(value, dict):
        raise SchemaError(f"{description} must be a JSON object")
    return value


def _validate_id(value: object, description: str) -> str:
    if not isinstance(value, str) or _ID.fullmatch(value) is None:
        raise SchemaError(f"invalid {description} ID")
    return value


def _adapter_parts(value: object) -> tuple[str, ...]:
    if (
        not isinstance(value, str)
        or not value
        or "\\" in value
        or "\x00" in value
        or value.endswith("/")
    ):
        raise SchemaError("adapter path must be a portable relative Markdown path")
    if any(part in {".", ".."} for part in value.split("/")):
        raise SchemaError("unsafe adapter path")
    posix_path = PurePosixPath(value)
    windows_path = PureWindowsPath(value)
    if (
        posix_path.is_absolute()
        or windows_path.is_absolute()
        or windows_path.drive
        or ".." in posix_path.parts
        or posix_path.suffix != ".md"
    ):
        raise SchemaError("unsafe or non-Markdown adapter path")
    return posix_path.parts


def _load_registry(skill_root: Path) -> tuple[dict[str, object], dict[str, list[str]]]:
    registry_path = skill_root / "providers" / "registry.json"
    registry = _read_json(registry_path, "provider registry")
    if set(registry) != {"schema_version", "providers"}:
        raise SchemaError("provider registry has invalid fields")
    if registry["schema_version"] != "image-provider-registry/v1":
        raise SchemaError("unsupported provider registry schema")
    providers = registry["providers"]
    if not isinstance(providers, dict) or not providers:
        raise SchemaError("provider registry must contain providers")

    defaults: dict[str, list[str]] = {}
    for provider_id, entry in providers.items():
        _validate_id(provider_id, "provider")
        if not isinstance(entry, dict) or set(entry) != {
            "adapter_path",
            "default_for_runtimes",
        }:
            raise SchemaError("provider registry entry has invalid fields")
        _adapter_parts(entry["adapter_path"])
        runtimes = entry["default_for_runtimes"]
        if not isinstance(runtimes, list) or not runtimes:
            raise SchemaError("provider defaults must be a nonempty array")
        seen: set[str] = set()
        for runtime in runtimes:
            runtime_id = _validate_id(runtime, "runtime")
            if runtime_id in seen:
                raise SchemaError("duplicate runtime in provider defaults")
            seen.add(runtime_id)
            defaults.setdefault(runtime_id, []).append(provider_id)

    if any(len(owners) != 1 for owners in defaults.values()):
        raise ResolutionError("runtime has duplicate default providers")
    return providers, defaults


def _is_reparse_point(path: Path) -> bool:
    try:
        status = path.lstat()
    except FileNotFoundError:
        return False
    attributes = getattr(status, "st_file_attributes", 0)
    return stat.S_ISLNK(status.st_mode) or bool(
        attributes & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0)
    )


def _resolve_project_root(project_root: Path) -> Path:
    try:
        if _is_reparse_point(project_root) or not project_root.is_dir():
            raise SchemaError("unsafe project root")
        return project_root.resolve(strict=True)
    except (OSError, RuntimeError):
        raise SchemaError("cannot inspect project root") from None


def _read_selection(resolved_root: Path) -> str | None:
    selection_path = resolved_root / "docs" / "visual-contract" / "image-provider.json"
    candidate = resolved_root
    try:
        parts = ("docs", "visual-contract", "image-provider.json")
        for index, part in enumerate(parts):
            candidate = candidate / part
            if _is_reparse_point(candidate):
                raise SchemaError("unsafe provider selection")
            if not candidate.exists():
                return None
            if index < len(parts) - 1 and not candidate.is_dir():
                raise SchemaError("unsafe provider selection")
        if not candidate.is_file():
            raise SchemaError("unsafe provider selection")
        candidate.resolve(strict=True).relative_to(resolved_root)
    except ValueError:
        raise SchemaError("provider selection escapes project root") from None
    except (OSError, RuntimeError):
        raise SchemaError("cannot inspect provider selection") from None

    selection = _read_json(selection_path, "provider selection")
    if set(selection) != {"schema_version", "provider_id"}:
        raise SchemaError("provider selection has invalid fields")
    if selection["schema_version"] != "image-provider-selection/v1":
        raise SchemaError("unsupported provider selection schema")
    return _validate_id(selection["provider_id"], "provider")



def _validate_adapter_kind(path: Path) -> None:
    """Check routing metadata without interpreting the adapter's instructions."""
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError):
        raise SchemaError("cannot read provider adapter") from None
    declarations = [
        match for match in re.finditer(r"<!--(.*?)(?:-->|$)", text, re.DOTALL)
        if re.match(r"\s*provider-kind\b", match.group(1), re.IGNORECASE)
    ]
    expected = "<!-- provider-kind: image -->"
    if declarations:
        if (len(declarations) != 1 or declarations[0].start() != 0
                or declarations[0].group(0) != expected
                or text.splitlines()[0] != expected):
            raise SchemaError("provider adapter kind is conflicting or malformed")


def _validate_adapter(skill_root: Path, adapter_path: object) -> str:
    parts = _adapter_parts(adapter_path)
    try:
        resolved_root = skill_root.resolve(strict=True)
    except (OSError, RuntimeError):
        raise SchemaError("cannot inspect provider adapter") from None

    candidate = resolved_root
    try:
        for part in parts:
            candidate = candidate / part
            if _is_reparse_point(candidate):
                raise SchemaError("adapter path contains a reparse point")
            if not candidate.exists():
                raise ResolutionError("provider adapter is unavailable")
        if not candidate.is_file():
            raise ResolutionError("provider adapter is unavailable")
        candidate.resolve(strict=True).relative_to(resolved_root)
    except ValueError:
        raise SchemaError("provider adapter escapes skill root") from None
    except OSError:
        raise SchemaError("cannot inspect provider adapter") from None
    _validate_adapter_kind(candidate)
    return PurePosixPath(*parts).as_posix()


def resolve_provider(
    runtime: str,
    project_root: Path,
    override: str | None = None,
    skill_root: Path | None = None,
) -> dict[str, str]:
    """Resolve a provider using local configuration and adapter metadata only."""
    runtime_id = _validate_id(runtime, "runtime")
    resolved_project_root = _resolve_project_root(project_root)
    root = skill_root if skill_root is not None else Path(__file__).resolve().parent.parent
    providers, defaults = _load_registry(root)

    if override is not None:
        provider_id = _validate_id(override, "provider")
        source = "override"
    else:
        selected = _read_selection(resolved_project_root)
        if selected is not None:
            provider_id = selected
            source = "project"
        else:
            owners = defaults.get(runtime_id, [])
            if len(owners) != 1:
                raise ResolutionError("runtime has no unique default provider")
            provider_id = owners[0]
            source = "runtime_default"

    entry = providers.get(provider_id)
    if entry is None:
        raise ResolutionError("selected provider is not registered")
    if not isinstance(entry, dict):
        raise SchemaError("provider registry entry has invalid fields")
    adapter_path = _validate_adapter(root, entry["adapter_path"])
    return {
        "schema_version": "image-provider-resolution/v1",
        "provider_id": provider_id,
        "source": source,
        "runtime": runtime_id,
        "adapter_path": adapter_path,
    }


def _argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="image_provider.py")
    subparsers = parser.add_subparsers(dest="command", required=True)
    resolve = subparsers.add_parser("resolve")
    resolve.add_argument("--runtime", required=True)
    resolve.add_argument("--project-root", required=True, type=Path)
    resolve.add_argument("--provider")
    return parser


def main(argv: list[str] | None = None) -> int:
    try:
        args = _argument_parser().parse_args(argv)
    except SystemExit as error:
        return 3 if error.code else 0

    try:
        resolution = resolve_provider(
            runtime=args.runtime,
            project_root=args.project_root,
            override=args.provider,
        )
    except SchemaError as error:
        print(str(error), file=sys.stderr)
        return 3
    except ResolutionError as error:
        print(str(error), file=sys.stderr)
        return 2

    print(json.dumps(resolution, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
