import contextlib
import copy
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "godot-game-production" / "scripts" / "image_provider.py"
PRODUCTION_REGISTRY = ROOT / "godot-game-production" / "providers" / "registry.json"

REGISTRY = {
    "schema_version": "image-provider-registry/v1",
    "providers": {
        "kimi": {
            "adapter_path": "references/providers/kimi.md",
            "default_for_runtimes": ["kimi"],
        },
        "codex": {
            "adapter_path": "references/providers/codex.md",
            "default_for_runtimes": ["codex"],
        },
    },
}


class ImageProviderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        spec = importlib.util.spec_from_file_location("image_provider_under_test", SCRIPT)
        assert spec is not None and spec.loader is not None
        cls.module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.module)

    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.skill = self.root / "skill"
        self.project = self.root / "project"
        self.project.mkdir()
        original_module_file = self.module.__file__
        self.addCleanup(setattr, self.module, "__file__", original_module_file)
        self.module.__file__ = str(self.skill / "scripts" / "image_provider.py")
        self.write_registry(REGISTRY)
        for provider in ("kimi", "codex"):
            adapter = self.skill / "references" / "providers" / f"{provider}.md"
            adapter.parent.mkdir(parents=True, exist_ok=True)
            adapter.write_text(f"# {provider.title()} provider\n", encoding="utf-8")

    def write_registry(self, value: object) -> None:
        path = self.skill / "providers" / "registry.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(value), encoding="utf-8")

    def write_raw_registry(self, value: str) -> None:
        path = self.skill / "providers" / "registry.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(value, encoding="utf-8")

    def selection_path(self) -> Path:
        return self.project / "docs" / "visual-contract" / "image-provider.json"

    def write_selection(self, value: object) -> None:
        path = self.selection_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(value), encoding="utf-8")

    def make_external_selection(self) -> Path:
        external = self.root / "external-docs"
        target = external / "visual-contract" / "image-provider.json"
        target.parent.mkdir(parents=True)
        target.write_text(
            json.dumps(
                {"schema_version": "image-provider-selection/v1", "provider_id": "codex"}
            ),
            encoding="utf-8",
        )
        return external

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

    def invoke(self, argv: list[str]) -> int:
        self.stdout = io.StringIO()
        self.stderr = io.StringIO()
        with contextlib.redirect_stdout(self.stdout), contextlib.redirect_stderr(self.stderr):
            code = self.module.main(argv)
        return code

    def run_main(self, *args: str) -> int:
        return self.invoke(
            [
                "resolve",
                "--runtime",
                "kimi",
                "--project-root",
                str(self.project),
                *args,
            ]
        )

    def assert_cli_failure(self, code: int, expected: int) -> None:
        self.assertEqual(code, expected)
        self.assertEqual(self.stdout.getvalue(), "")
        self.assertNotEqual(self.stderr.getvalue(), "")

    def resolve_with_adapter_path(self, adapter_path: str) -> int:
        registry = copy.deepcopy(REGISTRY)
        registry["providers"]["kimi"]["adapter_path"] = adapter_path
        self.write_registry(registry)
        return self.run_main()

    def test_runtime_defaults_and_override(self) -> None:
        kimi = self.module.resolve_provider("kimi", self.project, skill_root=self.skill)
        self.assertEqual(kimi["source"], "runtime_default")
        self.assertEqual(kimi["provider_id"], "kimi")
        codex = self.module.resolve_provider("codex", self.project, skill_root=self.skill)
        self.assertEqual(codex["source"], "runtime_default")
        self.assertEqual(codex["provider_id"], "codex")
        override = self.module.resolve_provider(
            "kimi", self.project, override="codex", skill_root=self.skill
        )
        self.assertEqual(override["source"], "override")
        self.assertEqual(override["provider_id"], "codex")

    def test_project_selection_and_override_bypass(self) -> None:
        self.write_selection(
            {"schema_version": "image-provider-selection/v1", "provider_id": "codex"}
        )
        resolved = self.module.resolve_provider("kimi", self.project, skill_root=self.skill)
        self.assertEqual(resolved["source"], "project")
        self.assertEqual(resolved["provider_id"], "codex")
        self.selection_path().write_text("{not json", encoding="utf-8")
        resolved = self.module.resolve_provider(
            "kimi", self.project, override="kimi", skill_root=self.skill
        )
        self.assertEqual(resolved["provider_id"], "kimi")
        self.assertEqual(resolved["source"], "override")

    def test_exact_success_fields(self) -> None:
        resolved = self.module.resolve_provider("kimi", self.project, skill_root=self.skill)
        self.assertEqual(
            resolved,
            {
                "schema_version": "image-provider-resolution/v1",
                "provider_id": "kimi",
                "source": "runtime_default",
                "runtime": "kimi",
                "adapter_path": "references/providers/kimi.md",
            },
        )

    def test_compact_sorted_json_stdout(self) -> None:
        code = self.run_main()
        self.assertEqual(code, 0)
        self.assertEqual(self.stderr.getvalue(), "")
        self.assertEqual(
            self.stdout.getvalue(),
            '{"adapter_path":"references/providers/kimi.md","provider_id":"kimi",'
            '"runtime":"kimi","schema_version":"image-provider-resolution/v1",'
            '"source":"runtime_default"}\n',
        )

    def test_unknown_provider_exits_two_without_resolution(self) -> None:
        code = self.run_main("--provider", "unknown")
        self.assert_cli_failure(code, 2)

    def test_unknown_project_provider_exits_two(self) -> None:
        self.write_selection(
            {"schema_version": "image-provider-selection/v1", "provider_id": "unknown"}
        )
        self.assert_cli_failure(self.run_main(), 2)

    def test_malformed_configuration_exits_three(self) -> None:
        path = self.selection_path()
        path.parent.mkdir(parents=True)
        path.write_text("{not json", encoding="utf-8")
        self.assert_cli_failure(self.run_main(), 3)

    def test_unknown_runtime_default_exits_two(self) -> None:
        code = self.invoke(
            ["resolve", "--runtime", "other", "--project-root", str(self.project)]
        )
        self.assert_cli_failure(code, 2)

    def test_duplicate_runtime_defaults_exit_two(self) -> None:
        registry = copy.deepcopy(REGISTRY)
        registry["providers"]["codex"]["default_for_runtimes"] = ["kimi"]
        self.write_registry(registry)
        self.assert_cli_failure(self.run_main("--provider", "kimi"), 2)

    def test_duplicate_default_inside_provider_is_malformed(self) -> None:
        registry = copy.deepcopy(REGISTRY)
        registry["providers"]["kimi"]["default_for_runtimes"] = ["kimi", "kimi"]
        self.write_registry(registry)
        self.assert_cli_failure(self.run_main(), 3)

    def test_missing_adapter_exits_two(self) -> None:
        (self.skill / "references" / "providers" / "kimi.md").unlink()
        self.assert_cli_failure(self.run_main(), 2)

    def test_non_regular_adapter_exits_two(self) -> None:
        adapter = self.skill / "references" / "providers" / "kimi.md"
        adapter.unlink()
        adapter.mkdir()
        self.assert_cli_failure(self.run_main(), 2)

    def test_parent_traversal_adapter_paths_exit_three(self) -> None:
        for adapter_path in (
            "../outside.md",
            "references/../outside.md",
            "references/providers/../../outside.md",
        ):
            with self.subTest(adapter_path=adapter_path):
                self.assert_cli_failure(self.resolve_with_adapter_path(adapter_path), 3)

    def test_absolute_adapter_paths_exit_three(self) -> None:
        for adapter_path in (
            "/tmp/kimi.md",
            "C:/tmp/kimi.md",
            "C:\\tmp\\kimi.md",
            "\\\\server\\share\\kimi.md",
        ):
            with self.subTest(adapter_path=adapter_path):
                self.assert_cli_failure(self.resolve_with_adapter_path(adapter_path), 3)

    def test_non_markdown_and_non_portable_adapter_paths_exit_three(self) -> None:
        for adapter_path in (
            "references/providers/kimi.txt",
            "references/providers/kimi",
            "references\\providers\\kimi.md",
            "",
        ):
            with self.subTest(adapter_path=adapter_path):
                self.assert_cli_failure(self.resolve_with_adapter_path(adapter_path), 3)

    def test_dangling_selection_symlink_exits_three(self) -> None:
        selection = self.selection_path()
        selection.parent.mkdir(parents=True)
        try:
            selection.symlink_to(self.root / "missing-selection-target.json")
        except (OSError, NotImplementedError) as error:
            self.skipTest(f"Symlink creation is unavailable: {error}")
        self.assert_cli_failure(self.run_main(), 3)

    def test_valid_in_root_selection_with_ordinary_components(self) -> None:
        self.write_selection(
            {"schema_version": "image-provider-selection/v1", "provider_id": "codex"}
        )
        code = self.run_main()
        self.assertEqual(code, 0)
        self.assertEqual(self.stderr.getvalue(), "")
        resolved = json.loads(self.stdout.getvalue())
        self.assertEqual(resolved["provider_id"], "codex")
        self.assertEqual(resolved["source"], "project")

    def test_selection_parent_symlink_exits_three(self) -> None:
        external = self.make_external_selection()
        try:
            (self.project / "docs").symlink_to(external, target_is_directory=True)
        except (OSError, NotImplementedError) as error:
            self.skipTest(f"Directory symlink creation is unavailable: {error}")
        self.assert_cli_failure(self.run_main(), 3)

    def test_selection_parent_junction_exits_three(self) -> None:
        external = self.make_external_selection()
        self.make_junction(self.project / "docs", external)
        self.assert_cli_failure(self.run_main(), 3)

    def test_override_bypasses_selection_parent_symlink(self) -> None:
        external = self.make_external_selection()
        try:
            (self.project / "docs").symlink_to(external, target_is_directory=True)
        except (OSError, NotImplementedError) as error:
            self.skipTest(f"Directory symlink creation is unavailable: {error}")
        code = self.run_main("--provider", "kimi")
        self.assertEqual(code, 0)
        self.assertEqual(self.stderr.getvalue(), "")
        resolved = json.loads(self.stdout.getvalue())
        self.assertEqual(resolved["provider_id"], "kimi")
        self.assertEqual(resolved["source"], "override")

    def test_adapter_parent_junction_exits_three(self) -> None:
        external = self.root / "junction-providers"
        external.mkdir()
        (external / "kimi.md").write_text("# external junction\n", encoding="utf-8")
        providers = self.skill / "references" / "providers"
        (providers / "kimi.md").unlink()
        (providers / "codex.md").unlink()
        providers.rmdir()
        self.make_junction(providers, external)
        self.assert_cli_failure(self.run_main(), 3)

    def test_trailing_slash_adapter_path_exits_three(self) -> None:
        code = self.resolve_with_adapter_path("references/providers/kimi.md/")
        self.assert_cli_failure(code, 3)

    def test_dot_segment_adapter_path_exits_three(self) -> None:
        code = self.resolve_with_adapter_path("references/providers/kimi.md/.")
        self.assert_cli_failure(code, 3)

    def test_nul_adapter_path_exits_three(self) -> None:
        code = self.resolve_with_adapter_path("references/providers/kimi\x00.md")
        self.assert_cli_failure(code, 3)

    def test_symlink_adapter_file_exits_three(self) -> None:
        adapter = self.skill / "references" / "providers" / "kimi.md"
        target = self.root / "actual-kimi.md"
        target.write_text("# Kimi\n", encoding="utf-8")
        adapter.unlink()
        try:
            adapter.symlink_to(target)
        except (OSError, NotImplementedError) as error:
            self.skipTest(f"Symlink creation is unavailable: {error}")
        self.assert_cli_failure(self.run_main(), 3)

    def test_symlink_adapter_path_component_exits_three(self) -> None:
        actual = self.root / "actual-providers"
        actual.mkdir()
        (actual / "kimi.md").write_text("# Kimi\n", encoding="utf-8")
        providers = self.skill / "references" / "providers"
        (providers / "kimi.md").unlink()
        (providers / "codex.md").unlink()
        providers.rmdir()
        try:
            providers.symlink_to(actual, target_is_directory=True)
        except (OSError, NotImplementedError) as error:
            self.skipTest(f"Directory symlink creation is unavailable: {error}")
        self.assert_cli_failure(self.run_main(), 3)

    def test_duplicate_registry_json_keys_exit_three(self) -> None:
        self.write_raw_registry(
            '{"schema_version":"image-provider-registry/v1",'
            '"schema_version":"image-provider-registry/v1","providers":{}}'
        )
        self.assert_cli_failure(self.run_main(), 3)

    def test_duplicate_nested_registry_json_keys_exit_three(self) -> None:
        self.write_raw_registry(
            '{"schema_version":"image-provider-registry/v1","providers":{"kimi":'
            '{"adapter_path":"references/providers/kimi.md",'
            '"adapter_path":"references/providers/kimi.md",'
            '"default_for_runtimes":["kimi"]}}}'
        )
        self.assert_cli_failure(self.run_main(), 3)

    def test_duplicate_selection_json_keys_exit_three(self) -> None:
        path = self.selection_path()
        path.parent.mkdir(parents=True)
        path.write_text(
            '{"schema_version":"image-provider-selection/v1",'
            '"provider_id":"kimi","provider_id":"codex"}',
            encoding="utf-8",
        )
        self.assert_cli_failure(self.run_main(), 3)

    def test_registry_schema_and_exact_fields(self) -> None:
        cases = []
        wrong_schema = copy.deepcopy(REGISTRY)
        wrong_schema["schema_version"] = "image-provider-registry/v2"
        cases.append(wrong_schema)
        extra_top = copy.deepcopy(REGISTRY)
        extra_top["extra"] = True
        cases.append(extra_top)
        missing_top = copy.deepcopy(REGISTRY)
        del missing_top["providers"]
        cases.append(missing_top)
        extra_provider = copy.deepcopy(REGISTRY)
        extra_provider["providers"]["kimi"]["extra"] = True
        cases.append(extra_provider)
        missing_provider = copy.deepcopy(REGISTRY)
        del missing_provider["providers"]["kimi"]["adapter_path"]
        cases.append(missing_provider)
        empty_providers = copy.deepcopy(REGISTRY)
        empty_providers["providers"] = {}
        cases.append(empty_providers)
        for registry in cases:
            with self.subTest(registry=registry):
                self.write_registry(registry)
                self.assert_cli_failure(self.run_main(), 3)

    def test_selection_schema_and_exact_fields(self) -> None:
        for selection in (
            {"schema_version": "image-provider-selection/v2", "provider_id": "kimi"},
            {"schema_version": "image-provider-selection/v1"},
            {"provider_id": "kimi"},
            {
                "schema_version": "image-provider-selection/v1",
                "provider_id": "kimi",
                "extra": True,
            },
        ):
            with self.subTest(selection=selection):
                self.write_selection(selection)
                self.assert_cli_failure(self.run_main(), 3)

    def test_invalid_identifiers_exit_three(self) -> None:
        for runtime in ("", "Kimi", "1kimi", "kimi_runtime", "kimi.."):
            with self.subTest(runtime=runtime):
                code = self.invoke(
                    ["resolve", "--runtime", runtime, "--project-root", str(self.project)]
                )
                self.assert_cli_failure(code, 3)
        for provider in ("", "Kimi", "1kimi", "kimi_runtime"):
            with self.subTest(provider=provider):
                self.assert_cli_failure(self.run_main("--provider", provider), 3)
        self.write_selection(
            {"schema_version": "image-provider-selection/v1", "provider_id": "Kimi"}
        )
        self.assert_cli_failure(self.run_main(), 3)

    def test_registry_identifier_and_default_shapes_exit_three(self) -> None:
        invalid_registries = []
        bad_provider_id = copy.deepcopy(REGISTRY)
        bad_provider_id["providers"]["Kimi"] = bad_provider_id["providers"].pop("kimi")
        invalid_registries.append(bad_provider_id)
        bad_runtime_id = copy.deepcopy(REGISTRY)
        bad_runtime_id["providers"]["kimi"]["default_for_runtimes"] = ["Kimi"]
        invalid_registries.append(bad_runtime_id)
        empty_defaults = copy.deepcopy(REGISTRY)
        empty_defaults["providers"]["kimi"]["default_for_runtimes"] = []
        invalid_registries.append(empty_defaults)
        non_list_defaults = copy.deepcopy(REGISTRY)
        non_list_defaults["providers"]["kimi"]["default_for_runtimes"] = "kimi"
        invalid_registries.append(non_list_defaults)
        non_string_default = copy.deepcopy(REGISTRY)
        non_string_default["providers"]["kimi"]["default_for_runtimes"] = [1]
        invalid_registries.append(non_string_default)
        non_object_providers = copy.deepcopy(REGISTRY)
        non_object_providers["providers"] = []
        invalid_registries.append(non_object_providers)
        non_object_entry = copy.deepcopy(REGISTRY)
        non_object_entry["providers"]["kimi"] = None
        invalid_registries.append(non_object_entry)
        non_string_path = copy.deepcopy(REGISTRY)
        non_string_path["providers"]["kimi"]["adapter_path"] = 1
        invalid_registries.append(non_string_path)
        for registry in invalid_registries:
            with self.subTest(registry=registry):
                self.write_registry(registry)
                self.assert_cli_failure(self.run_main(), 3)

    def test_malformed_missing_and_unreadable_registry_exit_three(self) -> None:
        self.write_raw_registry("{not json")
        self.assert_cli_failure(self.run_main(), 3)
        (self.skill / "providers" / "registry.json").unlink()
        self.assert_cli_failure(self.run_main(), 3)
        (self.skill / "providers" / "registry.json").write_bytes(b"\xff")
        self.assert_cli_failure(self.run_main(), 3)

    def test_project_root_must_be_a_directory(self) -> None:
        project_file = self.root / "not-a-directory"
        project_file.write_text("not a directory", encoding="utf-8")
        code = self.invoke(
            ["resolve", "--runtime", "kimi", "--project-root", str(project_file)]
        )
        self.assert_cli_failure(code, 3)

    def test_argument_errors_exit_three_without_stdout(self) -> None:
        for argv in (
            [],
            ["unknown"],
            ["resolve", "--runtime", "kimi"],
            ["resolve", "--project-root", str(self.project)],
            [
                "resolve",
                "--runtime",
                "kimi",
                "--project-root",
                str(self.project),
                "--unknown",
            ],
        ):
            with self.subTest(argv=argv):
                self.assert_cli_failure(self.invoke(argv), 3)

    def test_diagnostics_do_not_echo_configuration_secrets(self) -> None:
        path = self.selection_path()
        path.parent.mkdir(parents=True)
        path.write_text(
            '{"schema_version":"image-provider-selection/v1","provider_id":"kimi",'
            '"credential":"secret-value"}',
            encoding="utf-8",
        )
        self.assert_cli_failure(self.run_main(), 3)
        self.assertNotIn("secret-value", self.stderr.getvalue())

    def test_resolution_does_not_write_files(self) -> None:
        before = {path.relative_to(self.root) for path in self.root.rglob("*")}
        code = self.run_main("--provider", "codex")
        self.assertEqual(code, 0)
        after = {path.relative_to(self.root) for path in self.root.rglob("*")}
        self.assertEqual(after, before)

    def test_public_function_uses_specific_exceptions(self) -> None:
        with self.assertRaises(self.module.ResolutionError):
            self.module.resolve_provider(
                "kimi", self.project, override="unknown", skill_root=self.skill
            )
        with self.assertRaises(self.module.SchemaError):
            self.module.resolve_provider("Kimi", self.project, skill_root=self.skill)

    def test_default_skill_root_and_production_fixture(self) -> None:
        self.module.__file__ = str(SCRIPT)
        resolved = self.module.resolve_provider("kimi", self.project)
        self.assertEqual(resolved["provider_id"], "kimi")
        self.assertEqual(resolved["adapter_path"], "references/providers/kimi.md")
        self.assertEqual(json.loads(PRODUCTION_REGISTRY.read_text(encoding="utf-8")), REGISTRY)
        for provider in ("kimi", "codex"):
            adapter = ROOT / "godot-game-production" / "references" / "providers" / f"{provider}.md"
            self.assertTrue(adapter.is_file())
            self.assertTrue(adapter.read_text(encoding="utf-8").startswith("# "))


if __name__ == "__main__":
    unittest.main()
