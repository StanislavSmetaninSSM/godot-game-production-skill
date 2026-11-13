"""Inspect one contained local GLB without generation or Godot import."""

import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath, PureWindowsPath
import stat
import struct
import sys


_JSON_CHUNK = 0x4E4F534A
_BIN_CHUNK = 0x004E4942
_WINDOWS_FORBIDDEN = frozenset('<>:"|?*')
_WINDOWS_RESERVED = {"CON", "PRN", "AUX", "NUL"} | {
    f"COM{number}" for number in range(1, 10)
} | {f"LPT{number}" for number in range(1, 10)} | {
    f"{prefix}{suffix}" for prefix in ("COM", "LPT") for suffix in "¹²³"
}


class ArtifactUnavailable(Exception):
    """The selected local model is missing or is not an ordinary file."""


class ArtifactMalformed(Exception):
    """The invocation, portable path, or GLB structure is malformed or unsafe."""


def _is_reparse_point(path: Path) -> bool:
    try:
        info = path.lstat()
    except FileNotFoundError:
        return False
    attributes = getattr(info, "st_file_attributes", 0)
    return stat.S_ISLNK(info.st_mode) or bool(
        attributes & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0)
    )


def _resolve_project_root(project_root: Path) -> Path:
    try:
        if _is_reparse_point(project_root) or not project_root.is_dir():
            raise ArtifactMalformed("project root must be an existing ordinary directory")
        return project_root.resolve(strict=True)
    except ArtifactMalformed:
        raise
    except (OSError, RuntimeError):
        raise ArtifactMalformed("cannot inspect project root") from None


def _model_parts(model_path: object) -> tuple[str, ...]:
    if (
        not isinstance(model_path, str)
        or not model_path
        or "\\" in model_path
        or "\x00" in model_path
        or model_path.endswith("/")
    ):
        raise ArtifactMalformed("model path must be a portable relative GLB path")
    parts = model_path.split("/")
    if any(part in {"", ".", ".."} for part in parts):
        raise ArtifactMalformed("model path contains an unsafe segment")
    for part in parts:
        if any(character in _WINDOWS_FORBIDDEN or ord(character) < 32 for character in part):
            raise ArtifactMalformed("model path contains a nonportable character")
        if part.endswith((".", " ")):
            raise ArtifactMalformed("model path component has a trailing dot or space")
        if part.split(".", 1)[0].upper() in _WINDOWS_RESERVED:
            raise ArtifactMalformed("model path contains a reserved device name")
    posix_path = PurePosixPath(model_path)
    windows_path = PureWindowsPath(model_path)
    if (
        posix_path.is_absolute()
        or windows_path.is_absolute()
        or windows_path.drive
        or posix_path.suffix != ".glb"
    ):
        raise ArtifactMalformed("model path must be a portable relative .glb path")
    return tuple(parts)


def _resolve_model(project_root: Path, model_path: str) -> tuple[Path, str]:
    parts = _model_parts(model_path)
    candidate = project_root
    try:
        for index, part in enumerate(parts):
            candidate = candidate / part
            if _is_reparse_point(candidate):
                raise ArtifactMalformed("model path contains a reparse point")
            if not candidate.exists():
                raise ArtifactUnavailable("model is unavailable")
            if index < len(parts) - 1 and not candidate.is_dir():
                raise ArtifactMalformed("model path has a non-directory parent")
        if not candidate.is_file():
            raise ArtifactUnavailable("model is not an ordinary file")
        candidate.resolve(strict=True).relative_to(project_root)
    except (ArtifactMalformed, ArtifactUnavailable):
        raise
    except ValueError:
        raise ArtifactMalformed("model path escapes project root") from None
    except (OSError, RuntimeError):
        raise ArtifactMalformed("cannot inspect model path") from None
    return candidate, PurePosixPath(*parts).as_posix()


def _read_glb(path: Path) -> bytes:
    try:
        size = path.stat().st_size
        with path.open("rb") as stream:
            header = stream.read(12)
            if len(header) != 12:
                raise ArtifactMalformed("GLB header is truncated")
            _, _, declared_length = struct.unpack("<4sII", header)
            if declared_length != size:
                raise ArtifactMalformed("GLB declared length differs from file length")
            payload = stream.read(declared_length - 12) if declared_length >= 12 else b""
            if declared_length < 12 or len(payload) != declared_length - 12 or stream.read(1):
                raise ArtifactMalformed("GLB is truncated or has trailing bytes")
            return header + payload
    except ArtifactMalformed:
        raise
    except OSError:
        raise ArtifactUnavailable("model cannot be read") from None


class _JsonLexeme(str):
    """An ignored JSON numeric lexeme retained without numeric conversion."""

    __slots__ = ()

    def is_finite(self) -> bool:
        """JSON numeric lexemes are finite; nonstandard constants are rejected."""
        return True


def _parse_json_int(value: str) -> int:
    negative = value.startswith("-")
    digits = value[1:] if negative else value
    first_length = len(digits) % 9 or 9
    number = int(digits[:first_length])
    for offset in range(first_length, len(digits), 9):
        number = number * 1_000_000_000 + int(digits[offset : offset + 9])
    return -number if negative else number


def _reject_json_constant(value: str) -> object:
    raise ArtifactMalformed(f"non-standard JSON numeric constant: {value}")


def _glb_chunks(data: bytes) -> tuple[object, bytes | None]:
    if len(data) < 20:
        raise ArtifactMalformed("GLB has no complete JSON chunk")
    magic, version, declared_length = struct.unpack("<4sII", data[:12])
    if magic != b"glTF":
        raise ArtifactMalformed("GLB magic is not glTF")
    if version != 2:
        raise ArtifactMalformed("GLB version is not 2")
    if declared_length != len(data):
        raise ArtifactMalformed("GLB declared length differs from actual length")

    offset = 12
    json_payload: bytes | None = None
    binary: bytes | None = None
    chunk_index = 0
    while offset < len(data):
        if len(data) - offset < 8:
            raise ArtifactMalformed("GLB chunk header is truncated")
        chunk_length, chunk_type = struct.unpack("<II", data[offset : offset + 8])
        offset += 8
        if chunk_length % 4:
            raise ArtifactMalformed("GLB chunk length is not four-byte aligned")
        if chunk_length > len(data) - offset:
            raise ArtifactMalformed("GLB chunk exceeds declared file length")
        payload = data[offset : offset + chunk_length]
        if chunk_index == 0 and chunk_type != _JSON_CHUNK:
            raise ArtifactMalformed("first GLB chunk is not JSON")
        if chunk_type == _JSON_CHUNK:
            if chunk_index != 0 or json_payload is not None:
                raise ArtifactMalformed("GLB must contain exactly one JSON chunk first")
            json_payload = payload
        elif chunk_type == _BIN_CHUNK:
            if chunk_index != 1 or binary is not None:
                raise ArtifactMalformed("GLB BIN chunk must occur at most once, second")
            binary = payload
        chunk_index += 1
        offset += chunk_length
    if json_payload is None:
        raise ArtifactMalformed("GLB has no JSON chunk")

    try:
        text = json_payload.decode("utf-8")
        decoder = json.JSONDecoder(
            parse_int=_parse_json_int,
            parse_float=_JsonLexeme,
            parse_constant=_reject_json_constant,
        )
        start = len(text) - len(text.lstrip(" \t\r\n"))
        value, end = decoder.raw_decode(text, start)
        if any(character != " " for character in text[end:]):
            raise ArtifactMalformed("GLB JSON trailing padding must contain spaces only")
        return value, binary
    except (UnicodeDecodeError, json.JSONDecodeError, RecursionError, ValueError):
        raise ArtifactMalformed("GLB JSON is malformed") from None


def _json_chunk(data: bytes) -> object:
    return _glb_chunks(data)[0]


def _integer(value: object, label: str, minimum: int = 0) -> int:
    if type(value) is not int or value < minimum:
        raise ArtifactMalformed(f"{label} must be an integer >= {minimum}")
    return value


def _array_item(value: object, index: object, label: str) -> dict[str, object]:
    selected = _integer(index, f"{label} index")
    if not isinstance(value, list) or selected >= len(value):
        raise ArtifactMalformed(f"{label} index is out of bounds")
    item = value[selected]
    if not isinstance(item, dict):
        raise ArtifactMalformed(f"{label} must be an object")
    return item


def _extensions(value: dict[str, object]) -> bool:
    extensions = value.get("extensions", {})
    if not isinstance(extensions, dict):
        raise ArtifactMalformed("extensions must be an object")
    return bool(extensions)


def _storage(
    document: dict[str, object], binary: bytes | None
) -> tuple[list[tuple[int, int, int | None, bool]], list[object]]:
    """Validate declared buffers/views without opening any referenced resources."""
    buffers = document.get("buffers", [])
    views = document.get("bufferViews", [])
    accessors = document.get("accessors", [])
    if not all(isinstance(items, list) for items in (buffers, views, accessors)):
        raise ArtifactMalformed("buffers, bufferViews and accessors must be arrays")
    buffer_info = []
    for index, buffer in enumerate(buffers):
        if not isinstance(buffer, dict):
            raise ArtifactMalformed("buffer must be an object")
        length = _integer(buffer.get("byteLength"), "buffer.byteLength", 1)
        supported = index == 0 and "uri" not in buffer and not _extensions(buffer)
        if "uri" in buffer and (not isinstance(buffer["uri"], str) or not buffer["uri"]):
            raise ArtifactMalformed("buffer.uri must be a nonempty string")
        if supported and (binary is None or not 0 <= len(binary) - length <= 3):
            raise ArtifactMalformed("embedded buffer length differs from BIN bytes")
        buffer_info.append((length, supported))
    view_info = []
    for view in views:
        if not isinstance(view, dict):
            raise ArtifactMalformed("bufferView must be an object")
        buffer_index = _integer(view.get("buffer"), "bufferView.buffer")
        if buffer_index >= len(buffer_info):
            raise ArtifactMalformed("bufferView buffer index is out of bounds")
        offset = _integer(view.get("byteOffset", 0), "bufferView.byteOffset")
        length = _integer(view.get("byteLength"), "bufferView.byteLength", 1)
        stride = None
        if "byteStride" in view:
            stride = _integer(view["byteStride"], "bufferView.byteStride", 4)
            if stride > 252 or stride % 4:
                raise ArtifactMalformed("bufferView.byteStride must be a multiple of 4 <= 252")
        buffer_length, supported = buffer_info[buffer_index]
        if offset + length > buffer_length:
            raise ArtifactMalformed("bufferView exceeds declared buffer storage")
        view_info.append((offset, length, stride, supported and not _extensions(view)))
    return view_info, accessors


def _accessor_storage(
    accessor: dict[str, object], views: list[tuple[int, int, int | None, bool]],
    *, vertex: bool,
) -> tuple[int, int, int, bool]:
    """Return count, absolute byte offset, stride and supported-backing status."""
    count = _integer(accessor.get("count"), "accessor.count", 1)
    component = _integer(accessor.get("componentType"), "accessor.componentType")
    sizes = {5120: 1, 5121: 1, 5122: 2, 5123: 2, 5125: 4, 5126: 4}
    shape = accessor.get("type")
    shapes = {"SCALAR": (1, 1), "VEC2": (1, 2), "VEC3": (1, 3), "VEC4": (1, 4),
              "MAT2": (2, 2), "MAT3": (3, 3), "MAT4": (4, 4)}
    if component not in sizes or type(shape) is not str or shape not in shapes:
        raise ArtifactMalformed("accessor componentType or type is invalid")
    size = sizes[component]
    columns, rows = shapes[shape]
    column_size = size * rows
    if columns > 1:
        column_size += (-column_size) % 4
    element_size = column_size * columns
    offset = _integer(accessor.get("byteOffset", 0), "accessor.byteOffset")
    if offset % size or (vertex and offset % 4):
        raise ArtifactMalformed("accessor byteOffset is misaligned")
    if "normalized" in accessor and type(accessor["normalized"]) is not bool:
        raise ArtifactMalformed("accessor.normalized must be boolean")
    supported = not _extensions(accessor)
    if "sparse" in accessor:
        sparse = accessor["sparse"]
        if not isinstance(sparse, dict) or _integer(sparse.get("count"), "sparse.count", 1) > count:
            raise ArtifactMalformed("sparse count exceeds accessor count")
        for name in ("indices", "values"):
            part = sparse.get(name)
            if not isinstance(part, dict):
                raise ArtifactMalformed(f"sparse.{name} must be an object")
            view_index = _integer(part.get("bufferView"), f"sparse.{name}.bufferView")
            if view_index >= len(views):
                raise ArtifactMalformed(f"sparse.{name} bufferView index is out of bounds")
            part_size = size
            part_element_size = element_size
            if name == "indices":
                part_component = _integer(part.get("componentType"), "sparse.indices.componentType")
                if part_component not in (5121, 5123, 5125):
                    raise ArtifactMalformed("sparse indices must use unsigned components")
                part_size = part_element_size = sizes[part_component]
            part_offset = _integer(part.get("byteOffset", 0), f"sparse.{name}.byteOffset")
            view_offset, view_length, view_stride, _ = views[view_index]
            if (view_stride is not None or part_offset % part_size
                    or (view_offset + part_offset) % part_size
                    or part_offset + sparse["count"] * part_element_size > view_length):
                raise ArtifactMalformed(f"sparse.{name} storage is out of bounds or misaligned")
        # Sparse decoding is deliberately outside the supported accounting subset.
        supported = False
    if "bufferView" not in accessor:
        if offset:
            raise ArtifactMalformed("accessor without bufferView cannot have a byteOffset")
        return count, 0, element_size, False
    index = _integer(accessor["bufferView"], "accessor.bufferView")
    if index >= len(views):
        raise ArtifactMalformed("accessor bufferView index is out of bounds")
    view_offset, length, stride, backed = views[index]
    effective_stride = element_size if stride is None else stride
    if (view_offset + offset) % size or effective_stride % size or effective_stride < element_size:
        raise ArtifactMalformed("accessor storage alignment or stride is invalid")
    if not vertex and stride is not None:
        raise ArtifactMalformed("index bufferView cannot define byteStride")
    if offset + effective_stride * (count - 1) + element_size > length:
        raise ArtifactMalformed("accessor exceeds bufferView storage")
    return count, view_offset + offset, effective_stride, supported and backed


def _triangle_count(
    document: dict[str, object], primitives: list[object], binary: bytes | None
) -> tuple[int | None, str]:
    views, accessors = _storage(document, binary)
    total = 0
    complete = not bool(document.get("extensionsRequired"))
    for primitive in primitives:
        if not isinstance(primitive, dict):
            raise ArtifactMalformed("mesh primitive must be an object")
        attributes = primitive.get("attributes")
        if not isinstance(attributes, dict) or not attributes:
            raise ArtifactMalformed("mesh primitive must have nonempty attributes")
        mode = _integer(primitive.get("mode", 4), "primitive.mode")
        if mode > 6:
            raise ArtifactMalformed("primitive.mode must be between 0 and 6")
        dependent = _extensions(primitive) or bool(document.get("extensionsRequired"))
        position = None
        position_storage = None
        attribute_count = None
        attributes_backed = True
        for semantic, index in attributes.items():
            accessor = _array_item(accessors, index, "attribute accessor")
            storage = _accessor_storage(accessor, views, vertex=True)
            if attribute_count is not None and storage[0] != attribute_count:
                raise ArtifactMalformed("primitive vertex attribute counts must match")
            attribute_count = storage[0]
            attributes_backed = attributes_backed and storage[3]
            if semantic == "POSITION":
                position, position_storage = accessor, storage
                if not dependent and (accessor["componentType"] != 5126 or accessor["type"] != "VEC3" or accessor.get("normalized", False)):
                    raise ArtifactMalformed("POSITION must be unnormalized FLOAT VEC3")
        indices = None
        index_storage = None
        if "indices" in primitive:
            indices = _array_item(accessors, primitive["indices"], "indices accessor")
            index_storage = _accessor_storage(indices, views, vertex=False)
            if not dependent and (indices["componentType"] not in (5121, 5123, 5125) or indices["type"] != "SCALAR" or indices.get("normalized", False)):
                raise ArtifactMalformed("indices must be unnormalized unsigned SCALAR")
        available = (not dependent and attributes_backed and position_storage is not None
                     and (index_storage is None or index_storage[3]))
        if not dependent and index_storage is not None and index_storage[3]:
            assert binary is not None and indices is not None
            index_count, start, stride, _ = index_storage
            fmt = {5121: "<B", 5123: "<H", 5125: "<I"}[indices["componentType"]]
            reserved = {5121: 255, 5123: 65535, 5125: 4294967295}[indices["componentType"]]
            for offset in range(start, start + stride * index_count, stride):
                index_value = struct.unpack_from(fmt, binary, offset)[0]
                if index_value == reserved:
                    raise ArtifactMalformed("index uses reserved primitive-restart value")
                if position_storage is not None and index_value >= position_storage[0]:
                    raise ArtifactMalformed("index value exceeds POSITION count")
        if mode != 4 or not available:
            complete = False
            continue
        assert position_storage is not None
        count = position_storage[0] if index_storage is None else index_storage[0]
        if count % 3:
            raise ArtifactMalformed("TRIANGLES count must be divisible by three")
        total += count // 3
    return (total, "verified") if complete else (None, "unavailable")


def inspect_model(project_root: Path, model_path: str) -> dict[str, object]:
    """Return local structural, hash, and triangle evidence for one GLB."""
    resolved_root = _resolve_project_root(project_root)
    path, accepted_path = _resolve_model(resolved_root, model_path)
    data = _read_glb(path)
    value, binary = _glb_chunks(data)
    if not isinstance(value, dict):
        raise ArtifactMalformed("GLB JSON root must be an object")
    asset = value.get("asset")
    if (
        not isinstance(asset, dict)
        or type(asset.get("version")) is not str
        or asset.get("version") != "2.0"
    ):
        raise ArtifactMalformed("GLB asset.version must be 2.0")

    meshes = value.get("meshes")
    if not isinstance(meshes, list):
        raise ArtifactMalformed("GLB meshes must be an array")
    primitives: list[object] = []
    for mesh in meshes:
        if (not isinstance(mesh, dict) or not isinstance(mesh.get("primitives"), list)
                or not mesh["primitives"]):
            raise ArtifactMalformed("each GLB mesh must contain a nonempty primitives array")
        primitives.extend(mesh["primitives"])
    if not primitives:
        raise ArtifactMalformed("GLB must contain at least one mesh primitive")

    triangle_count, triangle_status = _triangle_count(value, primitives, binary)
    return {
        "accepted_glb_path": accepted_path,
        "media_type": "model/gltf-binary",
        "mesh_count": len(meshes),
        "primitive_count": len(primitives),
        "schema_version": "model-artifact-inspection/v1",
        "sha256": hashlib.sha256(data).hexdigest(),
        "triangle_count": triangle_count,
        "triangle_count_status": triangle_status,
    }


def _format_json_integer(value: int) -> str:
    if value == 0:
        return "0"
    negative = value < 0
    remaining = -value if negative else value
    chunks: list[int] = []
    while remaining:
        remaining, chunk = divmod(remaining, 1_000_000_000)
        chunks.append(chunk)
    text = str(chunks.pop())
    while chunks:
        text += f"{chunks.pop():09d}"
    return "-" + text if negative else text


def _compact_inspection_json(inspection: dict[str, object]) -> str:
    parts: list[str] = []
    for key in sorted(inspection):
        value = inspection[key]
        if type(value) is int:
            encoded = _format_json_integer(value)
        elif value is None:
            encoded = "null"
        elif type(value) is str:
            encoded = json.dumps(value)
        else:
            raise TypeError(f"unsupported inspection output type: {type(value).__name__}")
        parts.append(f"{json.dumps(key)}:{encoded}")
    return "{" + ",".join(parts) + "}"


def _argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="model_artifact.py")
    subparsers = parser.add_subparsers(dest="command", required=True)
    inspect = subparsers.add_parser("inspect")
    inspect.add_argument("--project-root", required=True, type=Path)
    inspect.add_argument("--model", required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    try:
        args = _argument_parser().parse_args(argv)
    except SystemExit as error:
        return 3 if error.code else 0

    try:
        inspection = inspect_model(project_root=args.project_root, model_path=args.model)
    except ArtifactUnavailable as error:
        print(str(error), file=sys.stderr)
        return 2
    except ArtifactMalformed as error:
        print(str(error), file=sys.stderr)
        return 3

    print(_compact_inspection_json(inspection))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
