import contextlib
import decimal
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import re
import struct
import subprocess
import sys
import tempfile
import unittest


sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT.parent
SCRATCH = WORKSPACE / ".work" / "tmp"
SCRIPT = ROOT / "godot-game-production" / "scripts" / "model_artifact.py"
JSON_CHUNK = 0x4E4F534A
BIN_CHUNK = 0x004E4942


def position_accessor(count: object = 3) -> dict[str, object]:
    return {"componentType": 5126, "count": count, "type": "VEC3"}


def index_accessor(count: object = 3) -> dict[str, object]:
    return {"componentType": 5123, "count": count, "type": "SCALAR"}


def document(
    primitives: list[dict[str, object]] | None = None,
    accessors: list[object] | None = None,
) -> dict[str, object]:
    if primitives is None:
        primitives = [{"attributes": {"POSITION": 0}}]
    if accessors is None:
        accessors = [position_accessor()]
    views = []
    offset = 0
    for accessor in accessors:
        if not isinstance(accessor, dict):
            continue
        count = accessor.get("count", 3)
        count = count if type(count) is int and 0 < count < 10000 else 3
        size = 2 if accessor.get("componentType") == 5123 else 12
        offset += (-offset) % 4
        accessor["bufferView"] = len(views)
        views.append({"buffer": 0, "byteOffset": offset, "byteLength": count * size})
        offset += count * size
    return {
        "asset": {"version": "2.0"},
        "accessors": accessors,
        "buffers": [{"byteLength": offset or 36}],
        "bufferViews": views,
        "meshes": [{"primitives": primitives}],
    }


def glb(
    value: object,
    *,
    magic: bytes = b"glTF",
    version: int = 2,
    declared_length: int | None = None,
    chunk_type: int = JSON_CHUNK,
    json_bytes: bytes | None = None,
    include_json_chunk: bool = True,
    pad_json: bool = True,
    json_pad: bytes = b" ",
    trailing_chunks: bytes = b"",
    bin_bytes: bytes | None = None,
    include_bin: bool = True,
) -> bytes:
    encoded = json.dumps(value, separators=(",", ":")).encode("utf-8")
    payload = encoded if json_bytes is None else json_bytes
    if pad_json:
        payload += json_pad * ((-len(payload)) % 4)
    chunks = b""
    if include_bin and isinstance(value, dict) and value.get("buffers"):
        buffer = value["buffers"][0]
        length = buffer.get("byteLength", 36)
        if "uri" not in buffer and type(length) is int and 0 < length < 1000000:
            binary = bytes(length) if bin_bytes is None else bin_bytes
            binary += b"\x00" * ((-len(binary)) % 4)
            chunks = struct.pack("<II", len(binary), BIN_CHUNK) + binary
    chunks += trailing_chunks
    if include_json_chunk:
        chunks = struct.pack("<II", len(payload), chunk_type) + payload + chunks
    total_length = 12 + len(chunks)
    if declared_length is not None:
        total_length = declared_length
    return struct.pack("<4sII", magic, version, total_length) + chunks


def raw_document_with_extra(raw_value: str) -> bytes:
    value = document()
    value["extras"] = {"probe": "RAW_VALUE"}
    return json.dumps(value).encode("ascii").replace(b'"RAW_VALUE"', raw_value.encode("ascii"))


def raw_document_with_position_count(raw_count: str, primitive_count: int = 1) -> bytes:
    value = document(primitives=[{"attributes": {"POSITION": 0}}] * primitive_count)
    value["accessors"][0]["count"] = "RAW_COUNT"
    return json.dumps(value).encode("ascii").replace(b'"RAW_COUNT"', raw_count.encode("ascii"))


def numeric_global_state() -> tuple[object, ...]:
    context = decimal.getcontext()
    return (
        sys.get_int_max_str_digits() if hasattr(sys, "get_int_max_str_digits") else None,
        context.prec,
        context.rounding,
        context.Emin,
        context.Emax,
        context.capitals,
        context.clamp,
        tuple(context.flags.values()),
        tuple(context.traps.values()),
    )


def expected_inspection(data: bytes, relative_path: str = "assets/model.glb") -> dict[str, object]:
    return {
        "accepted_glb_path": relative_path,
        "media_type": "model/gltf-binary",
        "mesh_count": 1,
        "primitive_count": 1,
        "schema_version": "model-artifact-inspection/v1",
        "sha256": hashlib.sha256(data).hexdigest(),
        "triangle_count": 1,
        "triangle_count_status": "verified",
    }


class ModelArtifactTests(unittest.TestCase):
    def setUp(self) -> None:
        self.assertTrue(SCRIPT.is_file(), "model artifact inspector script is missing")
        spec = importlib.util.spec_from_file_location("model_artifact_under_test", SCRIPT)
        self.assertIsNotNone(spec)
        assert spec is not None and spec.loader is not None
        self.module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.module)

        SCRATCH.mkdir(parents=True, exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(dir=SCRATCH)
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.project = self.root / "project"
        self.project.mkdir()

    def write_model(
        self,
        relative_path: str = "assets/model.glb",
        *,
        value: object | None = None,
        data: bytes | None = None,
    ) -> Path:
        path = self.project.joinpath(*relative_path.split("/"))
        path.parent.mkdir(parents=True, exist_ok=True)
        if data is None:
            data = glb(document() if value is None else value)
        path.write_bytes(data)
        return path

    def invoke(self, argv: list[str]) -> int:
        self.stdout = io.StringIO()
        self.stderr = io.StringIO()
        with contextlib.redirect_stdout(self.stdout), contextlib.redirect_stderr(self.stderr):
            code = self.module.main(argv)
        return code

    def run_main(
        self, model: str = "assets/model.glb", project_root: Path | None = None
    ) -> int:
        return self.invoke(
            [
                "inspect",
                "--project-root",
                str(self.project if project_root is None else project_root),
                "--model",
                model,
            ]
        )

    def assert_cli_failure(self, code: int, expected: int) -> None:
        self.assertEqual(code, expected)
        self.assertEqual(self.stdout.getvalue(), "")
        self.assertNotEqual(self.stderr.getvalue(), "")

    def make_junction(self, link: Path, target: Path) -> None:
        if sys.platform != "win32":
            self.skipTest("Windows junction creation requires Windows")
        completed = subprocess.run(
            ["cmd", "/c", "mklink", "/J", str(link), str(target)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=20,
            check=False,
        )
        if completed.returncode != 0:
            self.skipTest(
                f"Windows junction creation is unavailable: "
                f"{completed.stdout!r} {completed.stderr!r}"
            )
        self.assertTrue(link.exists())
        if hasattr(link, "is_junction"):
            self.assertTrue(link.is_junction())
        self.assertFalse(link.is_symlink())

    def test_indexed_triangles_have_exact_success_fields_and_hash(self) -> None:
        value = document(
            primitives=[{"attributes": {"POSITION": 0}, "indices": 1}],
            accessors=[position_accessor(3), index_accessor(6)],
        )
        path = self.write_model(value=value)
        inspected = self.module.inspect_model(self.project, "assets/model.glb")
        self.assertEqual(
            inspected,
            {
                "accepted_glb_path": "assets/model.glb",
                "media_type": "model/gltf-binary",
                "mesh_count": 1,
                "primitive_count": 1,
                "schema_version": "model-artifact-inspection/v1",
                "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                "triangle_count": 2,
                "triangle_count_status": "verified",
            },
        )
        self.assertRegex(inspected["sha256"], re.compile(r"[0-9a-f]{64}"))

    def test_position_only_triangles_use_position_accessor_count(self) -> None:
        value = document(accessors=[position_accessor(9)])
        self.write_model(value=value)
        inspected = self.module.inspect_model(self.project, "assets/model.glb")
        self.assertEqual(inspected["triangle_count"], 3)
        self.assertEqual(inspected["triangle_count_status"], "verified")

    def test_explicit_triangle_mode_and_multiple_meshes_are_summed(self) -> None:
        value = document(accessors=[position_accessor(3), index_accessor(3), position_accessor(6)])
        value["meshes"] = [
                {"primitives": [{"attributes": {"POSITION": 0}, "indices": 1, "mode": 4}]},
                {"primitives": [{"attributes": {"POSITION": 2}}]},
            ]
        self.write_model(value=value)
        inspected = self.module.inspect_model(self.project, "assets/model.glb")
        self.assertEqual(inspected["mesh_count"], 2)
        self.assertEqual(inspected["primitive_count"], 2)
        self.assertEqual(inspected["triangle_count"], 3)
        self.assertEqual(inspected["triangle_count_status"], "verified")

    def test_repeated_inspection_is_deterministic(self) -> None:
        path = self.write_model()
        first = self.module.inspect_model(self.project, "assets/model.glb")
        second = self.module.inspect_model(self.project, "assets/model.glb")
        self.assertEqual(first, second)
        self.assertEqual(first["sha256"], hashlib.sha256(path.read_bytes()).hexdigest())

    def test_known_chunks_have_strict_multiplicity_and_order(self) -> None:
        extra_json = struct.pack("<II", 4, JSON_CHUNK) + b"{}  "
        extra_bin = struct.pack("<II", 4, BIN_CHUNK) + bytes(4)
        unknown = struct.pack("<II", 4, 1234) + bytes(4)
        for data in (
            glb(document(), trailing_chunks=extra_json),
            glb(document(), trailing_chunks=extra_bin),
            glb(document(), include_bin=False, trailing_chunks=unknown + extra_bin),
        ):
            with self.subTest(data=data[-24:]):
                self.write_model(data=data)
                self.assert_cli_failure(self.run_main(), 3)
        self.write_model(data=glb(document(), trailing_chunks=unknown))
        self.assertEqual(self.run_main(), 0)

    def test_null_primitive_and_missing_or_empty_attributes_are_malformed(self) -> None:
        for primitive in (None, [], {}, {"attributes": None}, {"attributes": {}}, {"attributes": []}):
            with self.subTest(primitive=primitive):
                value = document()
                value["meshes"][0]["primitives"] = [primitive]
                self.write_model(value=value)
                self.assert_cli_failure(self.run_main(), 3)

    def test_missing_truncated_or_overpadded_embedded_buffer_is_malformed(self) -> None:
        for data in (
            glb(document(), include_bin=False),
            glb(document(), bin_bytes=bytes(32)),
            glb(document(), bin_bytes=bytes(40)),
        ):
            with self.subTest(length=len(data)):
                self.write_model(data=data)
                self.assert_cli_failure(self.run_main(), 3)

    def test_supported_storage_contradictions_are_malformed(self) -> None:
        cases = []
        for section, index, key, values in (
            ("buffers", 0, "byteLength", (0, -1, True, "36")),
            ("bufferViews", 0, "buffer", (1, -1, True)),
            ("bufferViews", 0, "byteLength", (0, 37, -1, True)),
            ("bufferViews", 0, "byteOffset", (4, -1, True)),
            ("bufferViews", 0, "byteStride", (0, 8, 14, 256, True)),
            ("accessors", 0, "bufferView", (1, -1, True)),
            ("accessors", 0, "byteOffset", (1, 4, -1, True)),
            ("accessors", 0, "count", (0, 300, True)),
            ("accessors", 0, "componentType", (9999, "5126", True)),
            ("accessors", 0, "type", ("OTHER", 3)),
        ):
            for bad in values:
                value = document()
                value[section][index][key] = bad
                cases.append((f"{section}.{key}={bad!r}", value))
        for name, value in cases:
            with self.subTest(name=name):
                self.write_model(data=glb(value, bin_bytes=bytes(36)))
                self.assert_cli_failure(self.run_main(), 3)

    def test_unsigned_index_bytes_are_checked_against_position_count(self) -> None:
        for component, fmt in ((5121, "B"), (5123, "H"), (5125, "I")):
            for indices, valid in (((0, 1, 2), True), ((0, 1, 3), False)):
                with self.subTest(component=component, indices=indices):
                    binary = bytes(36) + struct.pack("<" + fmt * 3, *indices)
                    value = document()
                    value["buffers"] = [{"byteLength": len(binary)}]
                    value["bufferViews"].append({"buffer": 0, "byteOffset": 36, "byteLength": len(binary) - 36})
                    value["accessors"].append({"bufferView": 1, "componentType": component, "type": "SCALAR", "count": 3})
                    value["meshes"][0]["primitives"][0]["indices"] = 1
                    self.write_model(data=glb(value, bin_bytes=binary))
                    if valid:
                        self.assertEqual(self.run_main(), 0)
                        self.assertEqual(json.loads(self.stdout.getvalue())["triangle_count"], 1)
                    else:
                        self.assert_cli_failure(self.run_main(), 3)

    def test_indexed_geometry_requires_position_and_correct_accessor_roles(self) -> None:
        for change in ("missing_position", "position_shape", "position_component", "index_shape", "index_component", "index_stride"):
            with self.subTest(change=change):
                value = document([{"attributes": {"POSITION": 0}, "indices": 1}], [position_accessor(), index_accessor()])
                if change == "missing_position":
                    value["meshes"][0]["primitives"][0]["attributes"] = {"NORMAL": 0}
                elif change == "position_shape":
                    value["accessors"][0]["type"] = "VEC2"
                elif change == "position_component":
                    value["accessors"][0]["componentType"] = 5123
                elif change == "index_shape":
                    value["accessors"][1]["type"] = "VEC2"
                elif change == "index_component":
                    value["accessors"][1]["componentType"] = 5122
                else:
                    value["bufferViews"][1]["byteStride"] = 4
                self.write_model(value=value)
                if change == "missing_position":
                    self.assertEqual(self.run_main(), 0)
                    self.assertEqual(json.loads(self.stdout.getvalue())["triangle_count_status"], "unavailable")
                else:
                    self.assert_cli_failure(self.run_main(), 3)

    def test_interleaved_positions_with_offsets_and_padded_indices_are_verified(self) -> None:
        value = document()
        value["buffers"] = [{"byteLength": 63}]
        value["bufferViews"] = [
            {"buffer": 0, "byteOffset": 4, "byteLength": 52, "byteStride": 16},
            {"buffer": 0, "byteOffset": 60, "byteLength": 3},
        ]
        value["accessors"][0]["byteOffset"] = 4
        value["accessors"].append({"bufferView": 1, "type": "SCALAR", "componentType": 5121, "count": 3})
        value["meshes"][0]["primitives"][0]["indices"] = 1
        self.write_model(data=glb(value, bin_bytes=bytes(60) + bytes((0, 1, 2))))
        self.assertEqual(self.run_main(), 0)
        self.assertEqual(json.loads(self.stdout.getvalue())["triangle_count"], 1)

    def test_unsupported_storage_never_produces_verified_count(self) -> None:
        for kind in ("external", "zero_initialized", "sparse", "draco", "meshopt", "mixed_external"):
            with self.subTest(kind=kind):
                value = document()
                if kind == "external":
                    value["buffers"][0]["uri"] = "https://invalid.example/model.bin"
                elif kind == "zero_initialized":
                    del value["accessors"][0]["bufferView"]
                elif kind == "sparse":
                    value["accessors"][0]["sparse"] = {"count": 1, "indices": {"bufferView": 0, "componentType": 5121}, "values": {"bufferView": 0}}
                elif kind == "draco":
                    value["meshes"][0]["primitives"][0]["extensions"] = {"KHR_draco_mesh_compression": {"bufferView": 0, "attributes": {"POSITION": 0}}}
                elif kind == "meshopt":
                    value["bufferViews"][0]["extensions"] = {"EXT_meshopt_compression": {}}
                else:
                    value["buffers"].append({"byteLength": 36, "uri": "missing.bin"})
                    value["bufferViews"].append({"buffer": 1, "byteLength": 36})
                    value["accessors"].append({"bufferView": 1, "type": "VEC3", "componentType": 5126, "count": 3})
                    value["meshes"][0]["primitives"].append({"attributes": {"POSITION": 1}})
                self.write_model(value=value)
                self.assertEqual(self.run_main(), 0, self.stderr.getvalue())
                result = json.loads(self.stdout.getvalue())
                self.assertIsNone(result["triangle_count"])
                self.assertEqual(result["triangle_count_status"], "unavailable")

    def test_unsupported_primitive_does_not_hide_later_provable_malformed_storage(self) -> None:
        value = document(primitives=[{"attributes": {"POSITION": 0}, "mode": 1}, {"attributes": {"POSITION": 1}}])
        value["accessors"].append({"bufferView": 0, "componentType": 5126, "type": "VEC3", "count": 300})
        self.write_model(value=value)
        self.assert_cli_failure(self.run_main(), 3)

    def test_sparse_unsupported_storage_still_rejects_provable_reference_errors(self) -> None:
        for change in ("indices_view", "values_view", "indices_offset", "values_offset", "indices_component", "missing_values"):
            with self.subTest(change=change):
                value = document()
                sparse = {"count": 1, "indices": {"bufferView": 0, "componentType": 5121}, "values": {"bufferView": 0}}
                value["accessors"][0]["sparse"] = sparse
                if change == "indices_view":
                    sparse["indices"]["bufferView"] = 1
                elif change == "values_view":
                    sparse["values"]["bufferView"] = True
                elif change == "indices_offset":
                    sparse["indices"]["byteOffset"] = 36
                elif change == "values_offset":
                    sparse["values"]["byteOffset"] = 28
                elif change == "indices_component":
                    sparse["indices"]["componentType"] = 5126
                else:
                    del sparse["values"]
                self.write_model(value=value)
                self.assert_cli_failure(self.run_main(), 3)

    def test_each_mesh_requires_at_least_one_primitive(self) -> None:
        value = document()
        value["meshes"].append({"primitives": []})
        self.write_model(value=value)
        self.assert_cli_failure(self.run_main(), 3)

    def test_unsigned_short_index_accessor_offset_is_respected(self) -> None:
        value = document([{"attributes": {"POSITION": 0}, "indices": 1}], [position_accessor(), index_accessor()])
        value["buffers"][0]["byteLength"] = 44
        value["bufferViews"][1]["byteLength"] = 8
        value["accessors"][1]["byteOffset"] = 2
        self.write_model(data=glb(value, bin_bytes=bytes(36) + struct.pack("<4H", 999, 0, 1, 2)))
        self.assertEqual(self.run_main(), 0)
        self.assertEqual(json.loads(self.stdout.getvalue())["triangle_count"], 1)

    def test_all_vertex_attributes_require_matching_counts_and_supported_backing(self) -> None:
        for kind in ("valid", "short", "external", "sparse", "zero_initialized", "compressed"):
            with self.subTest(kind=kind):
                value = document(
                    [{"attributes": {"POSITION": 0, "NORMAL": 1}}],
                    [position_accessor(), position_accessor(1 if kind == "short" else 3)],
                )
                normal = value["accessors"][1]
                if kind == "external":
                    value["buffers"].append({"byteLength": 36, "uri": "https://invalid.example/normals.bin"})
                    value["bufferViews"][1]["buffer"] = 1
                    value["bufferViews"][1]["byteOffset"] = 0
                elif kind == "sparse":
                    normal["sparse"] = {"count": 1, "indices": {"bufferView": 0, "componentType": 5121}, "values": {"bufferView": 0}}
                elif kind == "zero_initialized":
                    del normal["bufferView"]
                elif kind == "compressed":
                    value["bufferViews"][1]["extensions"] = {"EXT_meshopt_compression": {}}
                self.write_model(value=value)
                if kind == "short":
                    self.assert_cli_failure(self.run_main(), 3)
                else:
                    self.assertEqual(self.run_main(), 0)
                    inspected = json.loads(self.stdout.getvalue())
                    self.assertEqual(inspected["triangle_count_status"], "verified" if kind == "valid" else "unavailable")
                    self.assertEqual(inspected["triangle_count"], 1 if kind == "valid" else None)

    def test_reserved_unsigned_primitive_restart_indices_are_rejected(self) -> None:
        for component, fmt, maximum in ((5121, "B", 255), (5123, "H", 65535), (5125, "I", 4294967295)):
            # Both smaller component types have real POSITION storage large enough
            # that range checking alone would incorrectly accept the sentinel.
            position_count = maximum + 1 if component != 5125 else 3
            position_bytes = bytes(position_count * 12)
            for index_value in (maximum - 1 if component != 5125 else 2, maximum):
                with self.subTest(component=component, index_value=index_value):
                    indices = struct.pack("<" + fmt * 3, 0, 1, index_value)
                    binary = position_bytes + indices
                    value = document()
                    value["buffers"] = [{"byteLength": len(binary)}]
                    value["bufferViews"] = [{"buffer": 0, "byteLength": len(position_bytes)}, {"buffer": 0, "byteOffset": len(position_bytes), "byteLength": len(indices)}]
                    value["accessors"] = [{"bufferView": 0, "componentType": 5126, "type": "VEC3", "count": position_count}, {"bufferView": 1, "componentType": component, "type": "SCALAR", "count": 3}]
                    value["meshes"][0]["primitives"][0]["indices"] = 1
                    self.write_model(data=glb(value, bin_bytes=binary))
                    if index_value == maximum:
                        self.assert_cli_failure(self.run_main(), 3)
                        self.assertIn("reserved primitive-restart", self.stderr.getvalue())
                    else:
                        self.assertEqual(self.run_main(), 0)
                        self.assertEqual(json.loads(self.stdout.getvalue())["triangle_count"], 1)

    def test_supported_index_sentinel_is_malformed_even_when_count_is_unavailable(self) -> None:
        for kind in ("lines", "unbacked_normal", "external_position"):
            with self.subTest(kind=kind):
                value = document([{"attributes": {"POSITION": 0}, "indices": 1}], [position_accessor(), index_accessor()])
                value["accessors"][1]["componentType"] = 5121
                if kind == "lines":
                    value["meshes"][0]["primitives"][0]["mode"] = 1
                elif kind == "unbacked_normal":
                    value["accessors"].append(position_accessor())
                    value["meshes"][0]["primitives"][0]["attributes"]["NORMAL"] = 2
                else:
                    value["buffers"].append({"byteLength": 36, "uri": "missing.bin"})
                    value["bufferViews"][0]["buffer"] = 1
                self.write_model(data=glb(value, bin_bytes=bytes(36) + bytes((0, 1, 255, 0, 0, 0))))
                self.assert_cli_failure(self.run_main(), 3)
                self.assertIn("reserved primitive-restart", self.stderr.getvalue())

    def test_compact_sorted_json_stdout(self) -> None:
        path = self.write_model()
        code = self.run_main()
        self.assertEqual(code, 0)
        self.assertEqual(self.stderr.getvalue(), "")
        expected = {
            "accepted_glb_path": "assets/model.glb",
            "media_type": "model/gltf-binary",
            "mesh_count": 1,
            "primitive_count": 1,
            "schema_version": "model-artifact-inspection/v1",
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            "triangle_count": 1,
            "triangle_count_status": "verified",
        }
        self.assertEqual(
            self.stdout.getvalue(),
            json.dumps(expected, sort_keys=True, separators=(",", ":")) + "\n",
        )

    def test_zero_primitives_are_malformed(self) -> None:
        for value in (
            {"asset": {"version": "2.0"}, "meshes": []},
            {"asset": {"version": "2.0"}, "meshes": [{"primitives": []}]},
            {"asset": {"version": "2.0"}},
            {"asset": {"version": "2.0"}, "meshes": {}},
            {"asset": {"version": "2.0"}, "meshes": [{"primitives": {}}]},
        ):
            with self.subTest(value=value):
                self.write_model(value=value)
                self.assert_cli_failure(self.run_main(), 3)

    def test_mixed_triangle_and_non_triangle_modes_are_unavailable(self) -> None:
        value = document(
            primitives=[
                {"attributes": {"POSITION": 0}},
                {"attributes": {"POSITION": 0}, "mode": 1},
            ],
            accessors=[position_accessor(6)],
        )
        self.write_model(value=value)
        inspected = self.module.inspect_model(self.project, "assets/model.glb")
        self.assertEqual(inspected["primitive_count"], 2)
        self.assertIsNone(inspected["triangle_count"])
        self.assertEqual(inspected["triangle_count_status"], "unavailable")

    def test_every_non_default_non_triangle_mode_is_unavailable(self) -> None:
        for mode in (0, 1, 2, 3, 5, 6):
            with self.subTest(mode=mode):
                value = document(
                    primitives=[{"attributes": {"POSITION": 0}, "mode": mode}]
                )
                self.write_model(value=value)
                inspected = self.module.inspect_model(self.project, "assets/model.glb")
                self.assertIsNone(inspected["triangle_count"])
                self.assertEqual(inspected["triangle_count_status"], "unavailable")

    def test_invalid_indices_accessors_are_malformed(self) -> None:
        invalid_counts: list[object] = [True, False, -3, 1, 2, 1.5, "3", None]
        cases: list[tuple[list[object], dict[str, object]]] = []
        for count in invalid_counts:
            cases.append(
                (
                    [position_accessor(), index_accessor(count)],
                    {"attributes": {"POSITION": 0}, "indices": 1},
                )
            )
        cases.extend(
            [
                ([position_accessor()], {"attributes": {"POSITION": 0}, "indices": 1}),
                ([position_accessor(), None], {"attributes": {"POSITION": 0}, "indices": 1}),
                ([position_accessor(), {}], {"attributes": {"POSITION": 0}, "indices": 1}),
                ([position_accessor(), index_accessor()], {"attributes": {"POSITION": 0}, "indices": True}),
                ([position_accessor(), index_accessor()], {"attributes": {"POSITION": 0}, "indices": "1"}),
            ]
        )
        for accessors, primitive in cases:
            with self.subTest(accessors=accessors, primitive=primitive):
                self.write_model(value=document([primitive], accessors))
                self.assert_cli_failure(self.run_main(), 3)

    def test_invalid_position_accessors_are_malformed(self) -> None:
        cases: list[tuple[object, object]] = [
            ([position_accessor()], {}),
            ([position_accessor()], {"attributes": {}}),
            ([position_accessor()], {"attributes": {"POSITION": 1}}),
            ([position_accessor()], {"attributes": {"POSITION": True}}),
            ([None], {"attributes": {"POSITION": 0}}),
            ([{}], {"attributes": {"POSITION": 0}}),
            ([], {"attributes": {"POSITION": 0}}),
            (None, {"attributes": {"POSITION": 0}}),
            ([position_accessor()], None),
        ]
        for count in (True, False, -3, 1, 2, 1.5, "3", None):
            cases.append(([position_accessor(count)], {"attributes": {"POSITION": 0}}))
        for accessors, primitive in cases:
            with self.subTest(accessors=accessors, primitive=primitive):
                value = document(accessors=accessors)
                value["accessors"] = accessors
                value["meshes"] = [{"primitives": [primitive]}]
                self.write_model(value=value)
                self.assert_cli_failure(self.run_main(), 3)

    def test_bad_magic_version_and_declared_lengths_exit_three(self) -> None:
        valid = glb(document())
        cases = [
            b"",
            valid[:11],
            glb(document(), magic=b"BAD!"),
            glb(document(), version=1),
            glb(document(), version=3),
            glb(document(), declared_length=len(valid) - 1),
            glb(document(), declared_length=len(valid) + 1),
            valid + b"extra",
        ]
        for data in cases:
            with self.subTest(data=data[:20], length=len(data)):
                self.write_model(data=data)
                self.assert_cli_failure(self.run_main(), 3)

    def test_missing_wrong_or_out_of_bounds_json_chunk_exits_three(self) -> None:
        valid = glb(document())
        cases = [
            glb(document(), include_json_chunk=False),
            glb(document(), chunk_type=BIN_CHUNK),
            valid[:12] + struct.pack("<II", 100, JSON_CHUNK) + valid[20:],
            valid[:16] + struct.pack("<I", len(valid)) + valid[20:],
        ]
        for data in cases:
            with self.subTest(length=len(data)):
                self.write_model(data=data)
                self.assert_cli_failure(self.run_main(), 3)

    def test_invalid_json_utf8_root_and_asset_version_exit_three(self) -> None:
        cases = [
            glb(document(), json_bytes=b"{not json"),
            glb(document(), json_bytes=b"\xff\xff\xff\xff"),
            glb([]),
            glb(None),
            glb({"meshes": [{"primitives": [{}]}]}),
            glb({"asset": {}, "meshes": [{"primitives": [{}]}]}),
            glb({"asset": {"version": "1.0"}, "meshes": [{"primitives": [{}]}]}),
            glb({"asset": {"version": 2.0}, "meshes": [{"primitives": [{}]}]}),
            glb({"asset": "2.0", "meshes": [{"primitives": [{}]}]}),
        ]
        for data in cases:
            with self.subTest(data=data[:40]):
                self.write_model(data=data)
                self.assert_cli_failure(self.run_main(), 3)

    def test_duplicate_bin_chunk_is_malformed(self) -> None:
        payload = b"\x00\x01\x02\x03"
        data = glb(
            document(),
            trailing_chunks=struct.pack("<II", len(payload), BIN_CHUNK) + payload,
        )
        self.write_model(data=data)
        self.assert_cli_failure(self.run_main(), 3)

    def test_nonstandard_nonfinite_json_constants_exit_three(self) -> None:
        for constant in ("NaN", "Infinity", "-Infinity"):
            with self.subTest(constant=constant):
                data = glb(document(), json_bytes=raw_document_with_extra(constant))
                self.write_model(data=data)
                self.assert_cli_failure(self.run_main(), 3)

    def test_unaligned_json_chunk_length_exits_three(self) -> None:
        raw = json.dumps(document(), separators=(",", ":")).encode("utf-8")
        if len(raw) % 4 == 0:
            raw += b" "
        self.assertNotEqual(len(raw) % 4, 0)
        data = glb(document(), json_bytes=raw, pad_json=False)
        self.write_model(data=data)
        self.assert_cli_failure(self.run_main(), 3)

    def test_unaligned_bin_chunk_length_exits_three(self) -> None:
        payload = b"\x00"
        data = glb(
            document(),
            trailing_chunks=struct.pack("<II", len(payload), BIN_CHUNK) + payload,
        )
        self.assertNotEqual(len(data) % 4, 0)
        self.write_model(data=data)
        self.assert_cli_failure(self.run_main(), 3)

    def test_tab_json_trailing_padding_exits_three(self) -> None:
        raw = json.dumps(document(), separators=(",", ":")).encode("utf-8")
        padding = (-len(raw)) % 4 or 4
        padded = raw + b"\t" * padding
        data = glb(document(), json_bytes=padded)
        self.assertIn(b"\t", data[20:])
        self.write_model(data=data)
        self.assert_cli_failure(self.run_main(), 3)

    def test_space_padding_and_escaped_string_whitespace_remain_valid(self) -> None:
        value = document()
        value["extras"] = {"probe": "\t\n  "}
        raw = json.dumps(value, separators=(",", ":")).encode("utf-8")
        padding = (-len(raw)) % 4 or 4
        data = glb(value, json_bytes=raw + b" " * padding)
        self.write_model(data=data)
        code = self.run_main()
        self.assertEqual(code, 0)
        self.assertEqual(self.stderr.getvalue(), "")
        self.assertEqual(json.loads(self.stdout.getvalue())["triangle_count"], 1)

    def test_valid_large_json_integer_in_extras_succeeds_with_exact_output(self) -> None:
        digit_limit = sys.get_int_max_str_digits() if hasattr(sys, "get_int_max_str_digits") else 0
        digits = max(5000, digit_limit + 50)
        huge_number = "1" + "0" * (digits - 1)
        data = glb(document(), json_bytes=raw_document_with_extra(huge_number))
        path = self.write_model(data=data)
        completed = subprocess.run(
            [
                sys.executable,
                "-B",
                str(SCRIPT),
                "inspect",
                "--project-root",
                str(self.project),
                "--model",
                "assets/model.glb",
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=20,
            check=False,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertEqual(completed.stderr, "")
        expected = {
            "accepted_glb_path": "assets/model.glb",
            "media_type": "model/gltf-binary",
            "mesh_count": 1,
            "primitive_count": 1,
            "schema_version": "model-artifact-inspection/v1",
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            "triangle_count": 1,
            "triangle_count_status": "verified",
        }
        self.assertEqual(json.loads(completed.stdout), expected)
        self.assertEqual(
            completed.stdout,
            json.dumps(expected, sort_keys=True, separators=(",", ":")) + "\n",
        )

    def test_oversized_backed_count_is_malformed_without_numeric_state_change(self) -> None:
        for count_text, primitives in (("3" + "0" * 4999, 1), ("3" + "0" * 4299, 10)):
            data = glb(document(), json_bytes=raw_document_with_position_count(count_text, primitives))
            self.write_model(data=data)
            before = numeric_global_state()
            parsed = self.module._json_chunk(data)
            self.assertIs(type(parsed["accessors"][0]["count"]), int)
            self.assert_cli_failure(self.run_main(), 3)
            self.assertEqual(numeric_global_state(), before)
            completed = subprocess.run(
                [sys.executable, "-B", str(SCRIPT), "inspect", "--project-root", str(self.project), "--model", "assets/model.glb"],
                capture_output=True, text=True, check=False, timeout=20,
            )
            self.assertEqual(completed.returncode, 3)
            self.assertEqual(completed.stdout, "")
            self.assertNotIn("Traceback", completed.stderr)

    def test_oversized_negative_json_integer_remains_builtin_int_without_state_change(self) -> None:
        data = glb(
            document(),
            json_bytes=raw_document_with_extra("-" + "9" * 5000),
        )
        before = numeric_global_state()
        parsed = self.module._json_chunk(data)
        self.assertIs(type(parsed["extras"]["probe"]), int)
        self.assertEqual(parsed["extras"]["probe"], -(10**5000 - 1))
        self.assertEqual(numeric_global_state(), before)

    def test_ordinary_counts_parse_exactly_but_require_real_backing(self) -> None:
        for count in (0, 3, 3 * 10**30):
            with self.subTest(count=count):
                data = glb(document(), json_bytes=raw_document_with_position_count(str(count)))
                self.write_model(data=data)
                before = numeric_global_state()
                parsed = self.module._json_chunk(data)
                self.assertIs(type(parsed["accessors"][0]["count"]), int)
                if count == 3:
                    self.assertEqual(self.module.inspect_model(self.project, "assets/model.glb"), expected_inspection(data))
                else:
                    self.assert_cli_failure(self.run_main(), 3)
                self.assertEqual(numeric_global_state(), before)

    def test_large_exponent_in_extras_direct_api_succeeds_without_state_change(self) -> None:
        data = glb(document(), json_bytes=raw_document_with_extra("1e1000000"))
        self.write_model(data=data)
        before = numeric_global_state()
        inspected = self.module.inspect_model(self.project, "assets/model.glb")
        self.assertEqual(inspected, expected_inspection(data))
        self.assertEqual(numeric_global_state(), before)

    def test_extreme_exponent_direct_api_succeeds_exactly_without_state_change(self) -> None:
        data = glb(
            document(),
            json_bytes=raw_document_with_extra("1e9999999999999999999"),
        )
        self.write_model(data=data)
        before = numeric_global_state()
        failures = []
        inspected = None
        try:
            inspected = self.module.inspect_model(self.project, "assets/model.glb")
        except Exception as error:
            failures.append(f"direct API raised {type(error).__name__}: {error}")
        after = numeric_global_state()
        if after != before:
            failures.append(f"global numeric state changed: {before!r} -> {after!r}")
        if inspected != expected_inspection(data):
            failures.append(f"unexpected direct result: {inspected!r}")
        self.assertEqual(failures, [])

    def test_extreme_exponent_cli_succeeds_with_exact_output(self) -> None:
        data = glb(
            document(),
            json_bytes=raw_document_with_extra("1e9999999999999999999"),
        )
        self.write_model(data=data)
        before = numeric_global_state()
        completed = subprocess.run(
            [
                sys.executable,
                "-B",
                str(SCRIPT),
                "inspect",
                "--project-root",
                str(self.project),
                "--model",
                "assets/model.glb",
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=20,
            check=False,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertEqual(completed.stderr, "")
        expected = expected_inspection(data)
        self.assertEqual(json.loads(completed.stdout), expected)
        self.assertEqual(
            completed.stdout,
            json.dumps(expected, sort_keys=True, separators=(",", ":")) + "\n",
        )
        self.assertEqual(numeric_global_state(), before)

    def test_colon_and_wildcards_in_any_path_component_exit_three(self) -> None:
        for model in (
            "assets:alternate/model.glb",
            "assets/model:stream.glb",
            "assets?/model.glb",
            "assets*/model.glb",
            "assets/model?.glb",
            "assets/model*.glb",
        ):
            with self.subTest(model=model):
                self.assert_cli_failure(self.run_main(model), 3)

    def test_windows_forbidden_and_control_characters_exit_three(self) -> None:
        for character in ('<', '>', '"', '|', "\x01", "\x1f"):
            for model in (
                f"assets{character}/model.glb",
                f"assets/model{character}.glb",
            ):
                with self.subTest(model=model):
                    self.assert_cli_failure(self.run_main(model), 3)

    def test_trailing_dot_space_and_reserved_device_components_exit_three(self) -> None:
        for model in (
            "assets./model.glb",
            "assets /model.glb",
            "CON/model.glb",
            "assets/con.glb",
            "assets/PRN.glb",
            "assets/AUX.txt/model.glb",
            "assets/NUL.glb",
            "assets/COM1.glb",
            "assets/lpt9.txt/model.glb",
            "assets/COM9.glb",
        ):
            with self.subTest(model=model):
                self.assert_cli_failure(self.run_main(model), 3)
        for model in ("assets/CONSOLE.glb", "assets/COM0.glb", "assets/model.con.glb"):
            with self.subTest(ordinary_missing=model):
                self.assert_cli_failure(self.run_main(model), 2)

    def test_superscript_reserved_device_components_exit_three(self) -> None:
        for prefix in ("COM", "LPT"):
            for suffix in ("¹", "²", "³"):
                for model in (
                    f"{prefix}{suffix}/model.glb",
                    f"assets/{prefix.lower()}{suffix}.glb",
                    f"assets/{prefix}{suffix}.txt/model.glb",
                ):
                    with self.subTest(model=model):
                        self.assert_cli_failure(self.run_main(model), 3)
        for model in ("assets/COM⁴.glb", "assets/LPT0.glb"):
            with self.subTest(ordinary_missing=model):
                self.assert_cli_failure(self.run_main(model), 2)
        for model in ("CONSOLE.glb", "COM0.glb", "model.con.glb", "COM⁴.glb"):
            with self.subTest(valid_existing=model):
                data = glb(document())
                self.write_model(relative_path=model, data=data)
                code = self.run_main(model)
                self.assertEqual(code, 0)
                self.assertEqual(self.stderr.getvalue(), "")
                self.assertEqual(
                    json.loads(self.stdout.getvalue()),
                    expected_inspection(data, model),
                )

    def test_missing_and_non_file_models_exit_two(self) -> None:
        self.assert_cli_failure(self.run_main("assets/missing.glb"), 2)
        self.write_model()
        (self.project / "assets" / "model.glb").unlink()
        (self.project / "assets" / "model.glb").mkdir()
        self.assert_cli_failure(self.run_main(), 2)

    def test_non_directory_model_parent_exits_three(self) -> None:
        (self.project / "assets").write_text("not a directory", encoding="utf-8")
        self.assert_cli_failure(self.run_main(), 3)

    def test_absolute_drive_and_traversal_paths_exit_three(self) -> None:
        for model in (
            "/tmp/model.glb",
            "C:/tmp/model.glb",
            "C:model.glb",
            "../model.glb",
            "assets/../../model.glb",
            "assets/./model.glb",
            "./assets/model.glb",
        ):
            with self.subTest(model=model):
                self.assert_cli_failure(self.run_main(model), 3)

    def test_backslash_nul_trailing_slash_and_suffix_paths_exit_three(self) -> None:
        for model in (
            "assets\\model.glb",
            "assets/model\x00.glb",
            "assets/model.glb/",
            "assets/model.glb/.",
            "assets/model.txt",
            "assets/model",
            "assets/model.GLB",
            "",
        ):
            with self.subTest(model=model):
                self.assert_cli_failure(self.run_main(model), 3)

    def test_project_root_must_be_existing_ordinary_directory(self) -> None:
        project_file = self.root / "project-file"
        project_file.write_text("not a directory", encoding="utf-8")
        for root in (self.root / "missing-project", project_file):
            with self.subTest(root=root):
                self.assert_cli_failure(self.run_main(project_root=root), 3)

    def test_project_root_symlink_exits_three(self) -> None:
        self.write_model()
        linked = self.root / "linked-project"
        try:
            linked.symlink_to(self.project, target_is_directory=True)
        except (OSError, NotImplementedError) as error:
            self.skipTest(f"Directory symlink creation is unavailable: {error}")
        self.assert_cli_failure(self.run_main(project_root=linked), 3)

    def test_project_root_junction_exits_three(self) -> None:
        self.write_model()
        linked = self.root / "junction-project"
        self.make_junction(linked, self.project)
        self.assert_cli_failure(self.run_main(project_root=linked), 3)

    def test_model_parent_symlink_exits_three_even_when_target_is_inside(self) -> None:
        actual = self.project / "actual"
        actual.mkdir()
        (actual / "model.glb").write_bytes(glb(document()))
        try:
            (self.project / "assets").symlink_to(actual, target_is_directory=True)
        except (OSError, NotImplementedError) as error:
            self.skipTest(f"Directory symlink creation is unavailable: {error}")
        self.assert_cli_failure(self.run_main(), 3)

    def test_model_parent_symlink_escape_exits_three(self) -> None:
        external = self.root / "external"
        external.mkdir()
        (external / "model.glb").write_bytes(glb(document()))
        try:
            (self.project / "assets").symlink_to(external, target_is_directory=True)
        except (OSError, NotImplementedError) as error:
            self.skipTest(f"Directory symlink creation is unavailable: {error}")
        self.assert_cli_failure(self.run_main(), 3)

    def test_model_parent_junction_exits_three(self) -> None:
        external = self.root / "external"
        external.mkdir()
        (external / "model.glb").write_bytes(glb(document()))
        self.make_junction(self.project / "assets", external)
        self.assert_cli_failure(self.run_main(), 3)

    def test_dangling_model_parent_junction_exits_three_and_missing_stays_two(self) -> None:
        target = self.root / "empty-junction-target"
        target.mkdir()
        link = self.project / "assets"
        self.make_junction(link, target)
        # Remove only the empty target; keep the actual dangling reparse point.
        target.rmdir()
        self.addCleanup(link.rmdir)
        self.assertFalse(link.exists())
        self.assert_cli_failure(self.run_main(), 3)
        self.assert_cli_failure(self.run_main("ordinary-missing/model.glb"), 2)

    def test_model_file_and_dangling_symlinks_exit_three(self) -> None:
        target = self.root / "actual.glb"
        target.write_bytes(glb(document()))
        path = self.project / "assets" / "model.glb"
        path.parent.mkdir()
        for destination in (target, self.root / "missing-target.glb"):
            with self.subTest(destination=destination):
                if path.is_symlink():
                    path.unlink()
                try:
                    path.symlink_to(destination)
                except (OSError, NotImplementedError) as error:
                    self.skipTest(f"Symlink creation is unavailable: {error}")
                self.assert_cli_failure(self.run_main(), 3)

    def test_argument_errors_exit_three_without_stdout(self) -> None:
        for argv in (
            [],
            ["unknown"],
            ["inspect", "--project-root", str(self.project)],
            ["inspect", "--model", "assets/model.glb"],
            [
                "inspect",
                "--project-root",
                str(self.project),
                "--model",
                "assets/model.glb",
                "--unknown",
            ],
        ):
            with self.subTest(argv=argv):
                self.assert_cli_failure(self.invoke(argv), 3)

    def test_inspection_does_not_write_project_files(self) -> None:
        self.write_model()
        before = {path.relative_to(self.project) for path in self.project.rglob("*")}
        code = self.run_main()
        self.assertEqual(code, 0)
        after = {path.relative_to(self.project) for path in self.project.rglob("*")}
        self.assertEqual(after, before)

    def test_real_subprocess_cli_success_and_failure(self) -> None:
        path = self.write_model()
        base = [
            sys.executable,
            "-B",
            str(SCRIPT),
            "inspect",
            "--project-root",
            str(self.project),
        ]
        success = subprocess.run(
            [*base, "--model", "assets/model.glb"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=20,
            check=False,
        )
        self.assertEqual(success.returncode, 0, success.stderr)
        self.assertEqual(success.stderr, "")
        self.assertEqual(
            json.loads(success.stdout)["sha256"], hashlib.sha256(path.read_bytes()).hexdigest()
        )
        failure = subprocess.run(
            [*base, "--model", "../outside.glb"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=20,
            check=False,
        )
        self.assertEqual(failure.returncode, 3)
        self.assertEqual(failure.stdout, "")
        self.assertNotEqual(failure.stderr, "")


if __name__ == "__main__":
    unittest.main()
