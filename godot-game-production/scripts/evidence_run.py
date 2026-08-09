"""Initialize and validate project-local Godot evidence ledgers."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import uuid
from datetime import datetime
from pathlib import Path
from typing import Sequence


FACETS = (
    "core_play",
    "systems_holism",
    "content",
    "visual",
    "audio_feedback",
    "ux_onboarding",
    "reliability_performance",
    "ship",
)

KIND_PROVENANCES = {
    "target_gameplay_image": {"imagegen_target"},
    "canonical_godot_capture": {"godot_runtime"},
    "input_trace": {"input_trace"},
    "state_transition_trace": {"state_trace"},
    "outcome_record": {"godot_runtime", "state_trace"},
    "runtime_filmstrip": {"godot_runtime"},
    "runtime_video": {"godot_runtime"},
    "runtime_session": {"godot_runtime"},
    "systems_trace": {"godot_runtime", "state_trace"},
    "complete_session": {"godot_runtime"},
    "content_analysis": {"godot_runtime", "review_record"},
    "runtime_audio_video": {"godot_runtime"},
    "first_session_capture": {"godot_runtime"},
    "target_session_capture": {"godot_runtime"},
    "target_hardware_report": {"environment_report"},
    "telemetry": {"godot_runtime", "environment_report"},
    "release_build": {"build_output"},
    "clean_install_record": {"godot_runtime", "environment_report"},
    "save_restart_capture": {"godot_runtime"},
    "review_record": {"review_record"},
    "procedural_grammar": {"review_record"},
    "procedural_population": {"review_record"},
    "procedural_output": {"godot_runtime"},
}
ARTIFACT_KINDS = set(KIND_PROVENANCES)
PROVENANCES = {
    "imagegen_target",
    "godot_runtime",
    "build_output",
    "input_trace",
    "state_trace",
    "review_record",
    "environment_report",
}
REQUIRED_KINDS = {
    "core_play": {
        "input_trace",
        "state_transition_trace",
        "outcome_record",
        "runtime_filmstrip|runtime_video",
    },
    "systems_holism": {"runtime_session", "systems_trace"},
    "content": {"complete_session", "content_analysis"},
    "visual": {"canonical_godot_capture"},
    "audio_feedback": {"runtime_audio_video"},
    "ux_onboarding": {"first_session_capture"},
    "reliability_performance": {
        "target_session_capture",
        "target_hardware_report",
        "telemetry",
    },
    "ship": {"release_build", "clean_install_record", "save_restart_capture"},
}
HEX = set("0123456789abcdef")


class SchemaError(ValueError):
    """The manifest cannot be interpreted safely."""


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="evidence_run.py")
    commands = parser.add_subparsers(dest="command", required=True)
    init = commands.add_parser("init")
    init.add_argument("--project-root", required=True)
    init.add_argument("--manifest", required=True)
    init.add_argument("--builder-id", required=True)
    init.add_argument("--dimension", choices=("2d", "2.5d", "3d"), required=True)
    init.add_argument("--procedural-mode", choices=("none", "seeded"), required=True)
    validate = commands.add_parser("validate")
    validate.add_argument("--project-root", required=True)
    validate.add_argument("--manifest", required=True)
    validate.add_argument("--report", required=True)
    validate.add_argument(
        "--strict",
        action="store_true",
        help="compatibility flag; validation is always fail-closed",
    )
    return parser


def _inside(root: Path, candidate: Path) -> bool:
    try:
        candidate.relative_to(root)
    except ValueError:
        return False
    return True


def _manifest_template(
    *, builder_id: str, dimension: str, procedural_mode: str
) -> dict[str, object]:
    return {
        "schema_version": "evidence-run/v1",
        "run_id": str(uuid.uuid4()),
        "project_root": ".",
        "builder_id": builder_id,
        "game": {
            "godot_version": "",
            "dimension": dimension,
            "build_artifact_id": "",
            "target_hardware": "",
        },
        "artifacts": [],
        "approved_visual_contract": None,
        "facets": {
            name: {"intent": "PENDING", "evidence_ids": [], "review_ids": []}
            for name in FACETS
        },
        "reviews": [],
        "procedural_mode": procedural_mode,
        "procedural_none_reason": (
            "No procedural systems are declared for this evidence run."
            if procedural_mode == "none"
            else None
        ),
        "procedural_systems": [],
    }


def _atomic_json(path: Path, value: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{uuid.uuid4().hex}.tmp")
    try:
        with temporary.open("x", encoding="utf-8", newline="\n") as stream:
            json.dump(value, stream, ensure_ascii=False, indent=2, sort_keys=True)
            stream.write("\n")
        os.replace(temporary, path)
    finally:
        if temporary.exists():
            temporary.unlink()


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise SchemaError(message)


def _is_sha256(value: object) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and set(value).issubset(HEX)
    )


def _unique_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    value: dict[str, object] = {}
    for key, item in pairs:
        if key in value:
            raise SchemaError(f"duplicate JSON key: {key}")
        value[key] = item
    return value


def _loads_json(text: str) -> object:
    return json.loads(text, object_pairs_hook=_unique_object)


def _is_timezone_aware_iso8601(value: object) -> bool:
    if not isinstance(value, str) or "T" not in value:
        return False
    normalized = value[:-1] + "+00:00" if value.endswith("Z") else value
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError:
        return False
    return parsed.tzinfo is not None and parsed.utcoffset() is not None


def _validate_schema(data: object) -> dict[str, object]:
    _require(isinstance(data, dict), "manifest must be an object")
    required = {
        "schema_version",
        "run_id",
        "project_root",
        "builder_id",
        "game",
        "artifacts",
        "approved_visual_contract",
        "facets",
        "reviews",
        "procedural_mode",
        "procedural_none_reason",
        "procedural_systems",
    }
    _require(set(data) == required, "top-level manifest fields differ")
    _require(data["schema_version"] == "evidence-run/v1", "wrong schema version")
    try:
        uuid.UUID(data["run_id"])
    except (AttributeError, TypeError, ValueError) as error:
        raise SchemaError("run_id is not a UUID") from error
    _require(data["project_root"] == ".", "project_root must be portable")
    _require(isinstance(data["builder_id"], str) and bool(data["builder_id"].strip()), "builder_id is empty")
    game = data["game"]
    _require(isinstance(game, dict), "game must be an object")
    _require(
        set(game) == {"godot_version", "dimension", "build_artifact_id", "target_hardware"},
        "game fields differ",
    )
    _require(game["dimension"] in {"2d", "2.5d", "3d"}, "unsupported dimension")
    for field in ("godot_version", "build_artifact_id", "target_hardware"):
        _require(isinstance(game[field], str), f"game.{field} must be text")

    artifacts = data["artifacts"]
    _require(isinstance(artifacts, list), "artifacts must be a list")
    artifact_required = {"id", "kind", "provenance", "path", "sha256", "media_type"}
    artifact_optional = {"target_id", "approved_target_sha256", "coverage"}
    for row in artifacts:
        _require(isinstance(row, dict), "artifact must be an object")
        _require(artifact_required.issubset(row), "artifact fields are missing")
        _require(set(row).issubset(artifact_required | artifact_optional), "artifact fields are unknown")
        _require(isinstance(row["id"], str) and bool(row["id"].strip()), "artifact id is empty")
        _require(row["kind"] in ARTIFACT_KINDS, "artifact kind is unknown")
        _require(row["provenance"] in PROVENANCES, "artifact provenance is unknown")
        _require(isinstance(row["path"], str) and bool(row["path"]), "artifact path is empty")
        _require(_is_sha256(row["sha256"]), "artifact SHA-256 is malformed")
        _require(isinstance(row["media_type"], str) and bool(row["media_type"]), "media type is empty")
        if "approved_target_sha256" in row:
            _require(_is_sha256(row["approved_target_sha256"]), "approved target SHA-256 is malformed")
        if "coverage" in row:
            _require(
                isinstance(row["coverage"], list)
                and all(isinstance(item, str) and item for item in row["coverage"]),
                "artifact coverage is malformed",
            )

    facets = data["facets"]
    _require(isinstance(facets, dict), "facets must be an object")
    _require(set(facets).issubset(FACETS), "unknown facet")
    for row in facets.values():
        _require(isinstance(row, dict), "facet must be an object")
        _require(set(row) in ({"intent", "evidence_ids", "review_ids"}, {"intent", "evidence_ids", "review_ids", "blocker"}), "facet fields differ")
        _require(row["intent"] in {"SUBMITTED", "PENDING", "FAILED", "PIVOT", "STOP"}, "unknown facet intent")
        for field in ("evidence_ids", "review_ids"):
            _require(
                isinstance(row[field], list)
                and all(isinstance(item, str) and item for item in row[field]),
                f"facet {field} is malformed",
            )
        if "blocker" in row:
            _require(isinstance(row["blocker"], str), "facet blocker must be text")

    reviews = data["reviews"]
    _require(isinstance(reviews, list), "reviews must be a list")
    review_fields = {
        "id",
        "facet",
        "review_artifact_id",
        "reviewer_id",
        "role",
        "artifact_ids_reviewed",
        "verdict",
        "rationale",
    }
    for row in reviews:
        _require(isinstance(row, dict) and set(row) == review_fields, "review fields differ")
        _require(isinstance(row["id"], str) and bool(row["id"]), "review id is empty")
        _require(row["facet"] in FACETS, "review facet is unknown")
        _require(isinstance(row["review_artifact_id"], str) and bool(row["review_artifact_id"]), "review artifact id is empty")
        _require(isinstance(row["reviewer_id"], str) and bool(row["reviewer_id"].strip()), "reviewer id is empty")
        _require(row["role"] in {"user", "independent_reviewer", "cold_player"}, "review role is unknown")
        _require(
            isinstance(row["artifact_ids_reviewed"], list)
            and all(isinstance(item, str) and item for item in row["artifact_ids_reviewed"]),
            "review coverage is malformed",
        )
        _require(row["verdict"] in {"accept", "reject"}, "review verdict is unknown")
        _require(isinstance(row["rationale"], str) and bool(row["rationale"].strip()), "review rationale is empty")

    approval = data["approved_visual_contract"]
    if approval is not None:
        _require(isinstance(approval, dict), "visual approval must be an object")
        _require(
            set(approval)
            == {
                "contract_id",
                "approval_artifact_id",
                "reviewer_id",
                "decision",
                "approved_targets",
                "recorded_at",
            },
            "visual approval fields differ",
        )
        for field in ("contract_id", "approval_artifact_id", "reviewer_id", "recorded_at"):
            _require(isinstance(approval[field], str) and bool(approval[field].strip()), f"approval {field} is empty")
        _require(
            approval["contract_id"].startswith("vc-")
            and len(approval["contract_id"]) > len("vc-"),
            "visual approval contract_id is malformed",
        )
        _require(
            _is_timezone_aware_iso8601(approval["recorded_at"]),
            "visual approval recorded_at is not a timezone-aware ISO-8601 timestamp",
        )
        _require(approval["decision"] in {"approved", "rejected"}, "approval decision is unknown")
        _require(isinstance(approval["approved_targets"], list), "approved targets must be a list")
        for target in approval["approved_targets"]:
            _require(isinstance(target, dict) and set(target) == {"target_id", "sha256", "path"}, "approved target fields differ")
            _require(isinstance(target["target_id"], str) and bool(target["target_id"]), "target id is empty")
            _require(_is_sha256(target["sha256"]), "target SHA-256 is malformed")
            _require(isinstance(target["path"], str) and bool(target["path"]), "target path is empty")

    _require(data["procedural_mode"] in {"none", "seeded"}, "procedural mode is unknown")
    _require(
        data["procedural_none_reason"] is None
        or isinstance(data["procedural_none_reason"], str),
        "procedural none reason is malformed",
    )
    _require(isinstance(data["procedural_systems"], list), "procedural systems must be a list")
    return data


def _safe_artifact(root: Path, row: dict[str, object]) -> tuple[Path | None, str | None]:
    relative = Path(row["path"])
    if relative.is_absolute() or ".." in relative.parts:
        return None, f"artifact {row['id']} escapes the project root"
    candidate = root / relative
    try:
        resolved = candidate.resolve(strict=True)
    except OSError:
        return None, f"artifact {row['id']} is missing"
    if not _inside(root, resolved) or not resolved.is_file():
        return None, f"artifact {row['id']} is not an inside-root regular file"
    return resolved, None


def _artifact_index(
    root: Path, artifacts: list[dict[str, object]]
) -> tuple[dict[str, dict[str, object]], list[str]]:
    indexed: dict[str, dict[str, object]] = {}
    errors: list[str] = []
    hashes: dict[Path, str] = {}
    seen: set[str] = set()
    for row in artifacts:
        artifact_id = row["id"]
        if artifact_id in seen:
            errors.append(f"duplicate artifact id: {artifact_id}")
            indexed.pop(artifact_id, None)
            continue
        seen.add(artifact_id)
        artifact_errors: list[str] = []
        if row["provenance"] not in KIND_PROVENANCES[row["kind"]]:
            artifact_errors.append(
                f"artifact {artifact_id} has provenance incompatible with {row['kind']}"
            )
        resolved, error = _safe_artifact(root, row)
        if error:
            artifact_errors.append(error)
        else:
            assert resolved is not None
            digest = hashes.get(resolved)
            if digest is None:
                digest = hashlib.sha256(resolved.read_bytes()).hexdigest()
                hashes[resolved] = digest
            if digest != row["sha256"]:
                artifact_errors.append(f"artifact {artifact_id} SHA-256 mismatch")
        if artifact_errors:
            errors.extend(artifact_errors)
        else:
            indexed[artifact_id] = row
    return indexed, errors


def _review_index(reviews: list[dict[str, object]]) -> tuple[dict[str, dict[str, object]], list[str]]:
    indexed: dict[str, dict[str, object]] = {}
    errors: list[str] = []
    for row in reviews:
        if row["id"] in indexed:
            errors.append(f"duplicate review id: {row['id']}")
        else:
            indexed[row["id"]] = row
    return indexed, errors


def _required_kind_errors(facet: str, rows: list[dict[str, object]]) -> list[str]:
    kinds = {row["kind"] for row in rows}
    errors: list[str] = []
    for required in REQUIRED_KINDS[facet]:
        choices = set(required.split("|"))
        if not kinds & choices:
            errors.append(f"{facet} lacks {required}")
    if facet == "audio_feedback":
        audio = [row for row in rows if row["kind"] == "runtime_audio_video"]
        covered = {item for row in audio for item in row.get("coverage", [])}
        required_audio = {"action", "danger", "success", "failure", "ambience"}
        if covered != required_audio:
            errors.append("audio_feedback coverage is incomplete")
    return errors


def _review_errors(
    facet: str,
    facet_row: dict[str, object],
    review_index: dict[str, dict[str, object]],
    artifact_index: dict[str, dict[str, object]],
    builder_id: str,
    *,
    approval_reviewer: str | None = None,
) -> list[str]:
    errors: list[str] = []
    evidence_ids = set(facet_row["evidence_ids"])
    reviewed: set[str] = set()
    expected_role = "user" if facet == "visual" else "cold_player" if facet == "ux_onboarding" else "independent_reviewer"
    for review_id in facet_row["review_ids"]:
        review = review_index.get(review_id)
        if review is None:
            errors.append(f"{facet} references missing review {review_id}")
            continue
        if review["facet"] != facet:
            errors.append(f"review {review_id} belongs to another facet")
        if review["verdict"] != "accept":
            errors.append(f"review {review_id} rejected the evidence")
        if review["role"] != expected_role:
            errors.append(f"review {review_id} has the wrong role")
        if facet in {"visual", "ux_onboarding"} and review["reviewer_id"] == builder_id:
            errors.append(f"{facet} reviewer is the builder")
        if approval_reviewer is not None and review["reviewer_id"] != approval_reviewer:
            errors.append("visual review does not bind the approval reviewer")
        review_artifact = artifact_index.get(review["review_artifact_id"])
        if review_artifact is None or review_artifact["kind"] != "review_record":
            errors.append(f"review {review_id} lacks its immutable record")
        reviewed.update(review["artifact_ids_reviewed"])
    if reviewed != evidence_ids:
        errors.append(f"{facet} reviews do not cover the exact evidence set")
    return errors


def _visual_errors(
    data: dict[str, object],
    facet_row: dict[str, object],
    rows: list[dict[str, object]],
    artifact_index: dict[str, dict[str, object]],
) -> tuple[list[str], str | None]:
    errors: list[str] = []
    approval = data["approved_visual_contract"]
    if approval is None:
        return ["visual approval is missing"], None
    approval_reviewer = approval["reviewer_id"]
    if approval["decision"] != "approved":
        errors.append("visual contract is not approved")
    approval_artifact = artifact_index.get(approval["approval_artifact_id"])
    if approval_artifact is None or approval_artifact["kind"] != "review_record":
        errors.append("visual approval record is missing")
    if approval_reviewer == data["builder_id"]:
        errors.append("visual approval reviewer is the builder")

    approved: dict[str, dict[str, object]] = {}
    artifacts_by_path: dict[str, list[dict[str, object]]] = {}
    for artifact in artifact_index.values():
        artifacts_by_path.setdefault(artifact["path"], []).append(artifact)
    for target in approval["approved_targets"]:
        target_id = target["target_id"]
        if target_id in approved:
            errors.append(f"duplicate approved target id: {target_id}")
            continue
        approved[target_id] = target
        relative = Path(target["path"])
        parts = relative.parts
        if (
            relative.is_absolute()
            or ".." in parts
            or len(parts) < 5
            or parts[0:2] != ("docs", "visual-contract")
            or parts[2] != approval["contract_id"]
            or parts[3] != "targets"
        ):
            errors.append(f"approved target {target_id} is not at a versioned project path")
            continue
        matches = artifacts_by_path.get(target["path"], [])
        if len(matches) != 1:
            errors.append(f"approved target {target_id} does not bind one artifact")
            continue
        artifact = matches[0]
        if (
            artifact["kind"] != "target_gameplay_image"
            or artifact["provenance"] != "imagegen_target"
            or artifact["sha256"] != target["sha256"]
        ):
            errors.append(f"approved target {target_id} bytes or provenance drifted")

    captures = [row for row in rows if row["kind"] == "canonical_godot_capture"]
    captured_ids: set[str] = set()
    for capture in captures:
        target_id = capture.get("target_id")
        if not isinstance(target_id, str) or target_id in captured_ids:
            errors.append("visual capture target identity is missing or duplicate")
            continue
        captured_ids.add(target_id)
        target = approved.get(target_id)
        if target is None or capture.get("approved_target_sha256") != target["sha256"]:
            errors.append(f"visual capture {capture['id']} approval binding drifted")
        if capture["provenance"] != "godot_runtime":
            errors.append(f"visual capture {capture['id']} is not Godot runtime evidence")
    if captured_ids != set(approved):
        errors.append("visual captures do not cover every approved target")
    return errors, approval_reviewer


def _procedural_results(
    data: dict[str, object], artifact_index: dict[str, dict[str, object]]
) -> tuple[dict[str, dict[str, object]], list[str], bool]:
    results: dict[str, dict[str, object]] = {}
    errors: list[str] = []
    systems = data["procedural_systems"]
    if data["procedural_mode"] == "none":
        if systems or not isinstance(data["procedural_none_reason"], str) or not data["procedural_none_reason"].strip():
            errors.append("procedural none mode lacks its reason or contains systems")
        return results, errors, False
    if data["procedural_none_reason"] not in {None, ""}:
        errors.append("seeded mode still has a none reason")
    if not systems:
        return results, errors, not errors
    seen: set[str] = set()
    for system in systems:
        system_errors: list[str] = []
        seen_seeds: set[tuple[str, str]] = set()
        seen_outputs: set[str] = set()
        if not isinstance(system, dict) or set(system) != {"id", "grammar_artifact_id", "seed_cases"}:
            errors.append("procedural system fields differ")
            continue
        system_id = system["id"]
        if not isinstance(system_id, str) or not system_id or system_id in seen:
            errors.append("procedural system id is missing or duplicate")
            continue
        seen.add(system_id)
        grammar = artifact_index.get(system["grammar_artifact_id"])
        if grammar is None or grammar["kind"] != "procedural_grammar":
            system_errors.append("procedural grammar artifact is missing")
        cases = system["seed_cases"]
        if not isinstance(cases, list):
            system_errors.append("seed cases must be a list")
            cases = []
        required_classes = {"canonical", "random", "boundary", "worst_observed"}
        classes: list[str] = []
        for case in cases:
            if not isinstance(case, dict):
                system_errors.append("seed case is not an object")
                continue
            seed_class = case.get("class")
            if not isinstance(seed_class, str) or seed_class not in required_classes:
                system_errors.append("seed case class is unknown")
                continue
            classes.append(seed_class)
            expected_fields = {"class", "seed", "artifact_ids"}
            if seed_class == "worst_observed":
                expected_fields |= {"population_artifact_id", "selection_method"}
            if set(case) != expected_fields:
                system_errors.append(f"seed case {seed_class} fields differ")
                continue
            seed = case["seed"]
            if not (
                (isinstance(seed, int) and not isinstance(seed, bool))
                or (isinstance(seed, str) and bool(seed.strip()))
            ):
                system_errors.append(f"seed case {seed_class} has an invalid seed")
            else:
                seed_key = (type(seed).__name__, str(seed))
                if seed_key in seen_seeds:
                    system_errors.append(
                        f"seed case {seed_class} reuses another case seed"
                    )
                seen_seeds.add(seed_key)
            ids = case.get("artifact_ids")
            if (
                not isinstance(ids, list)
                or not ids
                or any(not isinstance(item, str) for item in ids)
                or len(set(ids)) != len(ids)
                or any(item not in artifact_index for item in ids)
            ):
                system_errors.append(f"seed case {seed_class} lacks existing artifacts")
                rows = []
                artifact_ids: list[str] = []
            else:
                rows = [artifact_index[item] for item in ids]
                artifact_ids = ids
            if not any(
                row["kind"] == "procedural_output"
                and row["provenance"] == "godot_runtime"
                for row in rows
            ):
                system_errors.append(
                    f"seed case {seed_class} lacks a Godot procedural output"
                )
            for row in rows:
                if (
                    row["kind"] == "procedural_output"
                    and row["provenance"] == "godot_runtime"
                ):
                    output_key = row["sha256"]
                    if output_key in seen_outputs:
                        system_errors.append(
                            f"seed case {seed_class} reuses another case output"
                        )
                    seen_outputs.add(output_key)
            if seed_class == "worst_observed":
                population_id = case.get("population_artifact_id")
                population = (
                    artifact_index.get(population_id)
                    if isinstance(population_id, str)
                    else None
                )
                if (
                    population is None
                    or population["kind"] != "procedural_population"
                    or population_id in artifact_ids
                    or not isinstance(case.get("selection_method"), str)
                    or not case["selection_method"].strip()
                ):
                    system_errors.append("worst_observed lacks population or selection method")
        if set(classes) != required_classes or len(classes) != len(required_classes):
            system_errors.append("procedural system lacks one exact four-class seed suite")
        result = "FAILED" if system_errors else "VERIFIED"
        results[system_id] = {"result": result, "errors": system_errors}
        errors.extend(f"{system_id}: {item}" for item in system_errors)
    return results, errors, False


def _candidate_errors(
    data: dict[str, object],
    artifact_index: dict[str, dict[str, object]],
    facet_results: dict[str, dict[str, object]],
    procedural_results: dict[str, dict[str, object]],
    procedural_pending: bool,
) -> list[str]:
    if (
        procedural_pending
        or any(row["result"] != "VERIFIED" for row in facet_results.values())
        or any(row["result"] != "VERIFIED" for row in procedural_results.values())
    ):
        return []
    errors: list[str] = []
    game = data["game"]
    for field in ("godot_version", "build_artifact_id", "target_hardware"):
        if not game[field].strip():
            errors.append(f"game.{field} is required for a verified candidate")
    build_id = game["build_artifact_id"]
    build = artifact_index.get(build_id)
    ship_ids = set(data["facets"]["ship"]["evidence_ids"])
    if (
        build is None
        or build["kind"] != "release_build"
        or build_id not in ship_ids
    ):
        errors.append("game.build_artifact_id is not the submitted ship release")
    return errors


def _evaluate(root: Path, data: dict[str, object]) -> dict[str, object]:
    artifact_index, global_errors = _artifact_index(root, data["artifacts"])
    review_index, review_index_errors = _review_index(data["reviews"])
    global_errors.extend(review_index_errors)
    review_references: dict[str, list[str]] = {}
    for facet_name, facet_row in data["facets"].items():
        for review_id in facet_row["review_ids"]:
            review_references.setdefault(review_id, []).append(facet_name)
    for review_id, review in review_index.items():
        references = review_references.get(review_id, [])
        if len(references) != 1:
            global_errors.append(
                f"review {review_id} must be referenced exactly once by its facet"
            )
        if review["verdict"] == "reject":
            global_errors.append(f"review {review_id} records a rejection")
    facet_results: dict[str, dict[str, object]] = {}
    for facet in FACETS:
        facet_row = data["facets"].get(facet)
        if facet_row is None or facet_row["intent"] == "PENDING":
            facet_results[facet] = {"result": "PENDING", "errors": ["facet is pending"]}
            continue
        if facet_row["intent"] in {"FAILED", "PIVOT", "STOP"}:
            facet_results[facet] = {"result": "FAILED", "errors": [f"facet intent is {facet_row['intent']}"]}
            continue
        errors: list[str] = []
        evidence_ids = facet_row["evidence_ids"]
        if len(set(evidence_ids)) != len(evidence_ids) or not evidence_ids:
            errors.append(f"{facet} evidence ids are empty or duplicate")
        rows = []
        for artifact_id in evidence_ids:
            artifact = artifact_index.get(artifact_id)
            if artifact is None:
                errors.append(f"{facet} references missing artifact {artifact_id}")
            else:
                rows.append(artifact)
        errors.extend(_required_kind_errors(facet, rows))
        approval_reviewer = None
        if facet == "visual":
            visual_errors, approval_reviewer = _visual_errors(
                data, facet_row, rows, artifact_index
            )
            errors.extend(visual_errors)
        errors.extend(
            _review_errors(
                facet,
                facet_row,
                review_index,
                artifact_index,
                data["builder_id"],
                approval_reviewer=approval_reviewer,
            )
        )
        facet_results[facet] = {
            "result": "FAILED" if errors else "VERIFIED",
            "errors": errors,
        }
    procedural_results, procedural_errors, procedural_pending = _procedural_results(
        data, artifact_index
    )
    global_errors.extend(procedural_errors)
    global_errors.extend(
        _candidate_errors(
            data,
            artifact_index,
            facet_results,
            procedural_results,
            procedural_pending,
        )
    )
    if (
        global_errors
        or any(row["result"] == "FAILED" for row in facet_results.values())
        or any(row["result"] == "FAILED" for row in procedural_results.values())
    ):
        overall = "FAILED"
    elif procedural_pending or any(
        row["result"] == "PENDING" for row in facet_results.values()
    ):
        overall = "PENDING"
    else:
        overall = "VERIFIED"
    return {
        "schema_version": "evidence-report/v1",
        "run_id": data["run_id"],
        "overall": overall,
        "facets": facet_results,
        "procedural_systems": procedural_results,
        "errors": global_errors,
        "trust_boundary": (
            "Structural completeness and local byte integrity do not prove human "
            "identity, provenance truth, artistic quality, fun, or shipping readiness."
        ),
    }


def _init(args: argparse.Namespace) -> int:
    builder_id = args.builder_id.strip()
    if not builder_id:
        return 3

    root = Path(args.project_root).resolve()
    manifest = Path(args.manifest).resolve()
    if not root.is_dir() or not (root / "project.godot").is_file():
        return 3
    if not _inside(root, manifest) or manifest.exists():
        return 3

    try:
        _atomic_json(
            manifest,
            _manifest_template(
                builder_id=builder_id,
                dimension=args.dimension,
                procedural_mode=args.procedural_mode,
            ),
        )
    except (OSError, ValueError):
        return 3
    return 0


def _validate(args: argparse.Namespace) -> int:
    root = Path(args.project_root).resolve()
    manifest = Path(args.manifest).resolve()
    report = Path(args.report).resolve()
    if (
        not root.is_dir()
        or not (root / "project.godot").is_file()
        or not _inside(root, manifest)
        or not manifest.is_file()
        or not _inside(root, report)
    ):
        return 3
    try:
        data = _validate_schema(_loads_json(manifest.read_text(encoding="utf-8")))
    except (OSError, UnicodeError, json.JSONDecodeError, SchemaError):
        return 3
    protected = {manifest, (root / "project.godot").resolve()}
    for artifact in data["artifacts"]:
        protected.add((root / Path(artifact["path"])).resolve())
    approval = data["approved_visual_contract"]
    if approval is not None:
        for target in approval["approved_targets"]:
            protected.add((root / Path(target["path"])).resolve())
    if report.suffix.lower() != ".json" or report in protected:
        return 3
    if report.exists():
        if not report.is_file():
            return 3
        try:
            previous = _loads_json(report.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError, SchemaError):
            return 3
        if not (
            isinstance(previous, dict)
            and previous.get("schema_version") == "evidence-report/v1"
            and isinstance(previous.get("run_id"), str)
            and previous.get("overall") in {"VERIFIED", "PENDING", "FAILED"}
            and isinstance(previous.get("facets"), dict)
        ):
            return 3
    try:
        result = _evaluate(root, data)
        _atomic_json(report, result)
    except (OSError, ValueError):
        return 3
    if result["overall"] == "VERIFIED":
        return 0
    if result["overall"] == "PENDING":
        return 1
    return 2


def main(argv: Sequence[str] | None = None) -> int:
    try:
        args = _parser().parse_args(argv)
    except SystemExit:
        return 3
    if args.command == "init":
        return _init(args)
    if args.command == "validate":
        return _validate(args)
    return 3


if __name__ == "__main__":
    sys.exit(main())
