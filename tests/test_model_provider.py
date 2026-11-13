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
SCRIPT = ROOT / "godot-game-production" / "scripts" / "model_provider.py"
PRODUCTION_REGISTRY = ROOT / "godot-game-production" / "model-providers" / "registry.json"

REGISTRY = {
    "schema_version": "model-provider-registry/v1",
    "providers": {
        "tripo": {
            "adapter_path": "references/model-providers/tripo.md",
            "default_for_runtimes": ["kimi"],
        },
        "custom": {
            "adapter_path": "references/model-providers/custom.md",
            "default_for_runtimes": [],
        },
    },
}
PRODUCTION_REGISTRY_VALUE = {
    "schema_version": "model-provider-registry/v1",
    "providers": {
        "tripo": {
            "adapter_path": "references/model-providers/tripo.md",
            "default_for_runtimes": ["kimi"],
        }
    },
}


class ModelProviderTests(unittest.TestCase):
    def setUp(self) -> None:
        self.assertTrue(SCRIPT.is_file(), "model provider resolver script is missing")
        spec = importlib.util.spec_from_file_location("model_provider_under_test", SCRIPT)
        self.assertIsNotNone(spec)
        assert spec is not None and spec.loader is not None
        self.module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.module)

        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.skill = self.root / "skill"
        self.project = self.root / "project"
        self.project.mkdir()
        original_module_file = self.module.__file__
        self.addCleanup(setattr, self.module, "__file__", original_module_file)
        self.module.__file__ = str(self.skill / "scripts" / "model_provider.py")
        self.write_registry(REGISTRY)
        for provider in ("tripo", "custom"):
            adapter = self.skill / "references" / "model-providers" / f"{provider}.md"
            adapter.parent.mkdir(parents=True, exist_ok=True)
            adapter.write_text(f"<!-- provider-kind: model -->\n# {provider.title()} model provider\n", encoding="utf-8")

    def write_registry(self, value: object) -> None:
        path = self.skill / "model-providers" / "registry.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(value), encoding="utf-8")

    def write_raw_registry(self, value: str) -> None:
        path = self.skill / "model-providers" / "registry.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(value, encoding="utf-8")

    def selection_path(self) -> Path:
        return self.project / "docs" / "visual-contract" / "model-provider.json"

    def write_selection(self, value: object) -> None:
        path = self.selection_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(value), encoding="utf-8")

    def make_external_selection(self) -> Path:
        external = self.root / "external-docs"
        target = external / "visual-contract" / "model-provider.json"
        target.parent.mkdir(parents=True)
        target.write_text(
            json.dumps(
                {"schema_version": "model-provider-selection/v1", "provider_id": "custom"}
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

    def run_main(self, *args: str, runtime: str = "kimi") -> int:
        return self.invoke(
            [
                "resolve",
                "--runtime",
                runtime,
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
        registry["providers"]["tripo"]["adapter_path"] = adapter_path
        self.write_registry(registry)
        return self.run_main()

    def run_fixture_subprocess(self) -> subprocess.CompletedProcess[str]:
        fixture_script = self.skill / "scripts" / "model_provider.py"
        fixture_script.parent.mkdir(parents=True, exist_ok=True)
        fixture_script.write_bytes(SCRIPT.read_bytes())
        return subprocess.run(
            [
                sys.executable,
                "-B",
                str(fixture_script),
                "resolve",
                "--runtime",
                "kimi",
                "--project-root",
                str(self.project),
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=20,
            check=False,
        )

    def assert_subprocess_malformed(
        self, completed: subprocess.CompletedProcess[str], description: str
    ) -> None:
        self.assertEqual(completed.returncode, 3, completed.stderr)
        self.assertEqual(completed.stdout, "")
        self.assertNotEqual(completed.stderr, "")
        self.assertIn(description, completed.stderr)
        self.assertNotIn("Traceback", completed.stderr)

    def test_real_subprocess_registry_large_integer_unknown_field_exits_three(self) -> None:
        huge_integer = "1" + "0" * 4999
        registry_text = json.dumps(REGISTRY, separators=(",", ":"))
        self.write_raw_registry(registry_text[:-1] + ',"extra":' + huge_integer + "}")
        completed = self.run_fixture_subprocess()
        self.assert_subprocess_malformed(completed, "model provider registry")

    def test_real_subprocess_selection_large_integer_unknown_field_exits_three(self) -> None:
        huge_integer = "1" + "0" * 4999
        selection_text = json.dumps(
            {"schema_version": "model-provider-selection/v1", "provider_id": "tripo"},
            separators=(",", ":"),
        )
        path = self.selection_path()
        path.parent.mkdir(parents=True)
        path.write_text(
            selection_text[:-1] + ',"extra":' + huge_integer + "}", encoding="utf-8"
        )
        completed = self.run_fixture_subprocess()
        self.assert_subprocess_malformed(completed, "model provider selection")

    def test_real_subprocess_large_float_unknown_fields_exit_three(self) -> None:
        huge_float = "1." + "2" * 5000
        registry_text = json.dumps(REGISTRY, separators=(",", ":"))
        self.write_raw_registry(registry_text[:-1] + ',"extra":' + huge_float + "}")
        registry_result = self.run_fixture_subprocess()
        self.assert_subprocess_malformed(registry_result, "model provider registry")

        self.write_registry(REGISTRY)
        selection_text = json.dumps(
            {"schema_version": "model-provider-selection/v1", "provider_id": "tripo"},
            separators=(",", ":"),
        )
        path = self.selection_path()
        path.parent.mkdir(parents=True)
        path.write_text(
            selection_text[:-1] + ',"extra":' + huge_float + "}", encoding="utf-8"
        )
        selection_result = self.run_fixture_subprocess()
        self.assert_subprocess_malformed(selection_result, "model provider selection")

    def test_large_numbers_do_not_change_global_integer_digit_limit(self) -> None:
        before = sys.get_int_max_str_digits() if hasattr(sys, "get_int_max_str_digits") else None
        huge_integer = "1" + "0" * 4999
        registry_text = json.dumps(REGISTRY, separators=(",", ":"))
        self.write_raw_registry(registry_text[:-1] + ',"extra":' + huge_integer + "}")
        self.assert_cli_failure(self.run_main(), 3)
        after = sys.get_int_max_str_digits() if hasattr(sys, "get_int_max_str_digits") else None
        self.assertEqual(after, before)

    def test_wildcard_adapter_is_malformed_before_availability_check(self) -> None:
        code = self.resolve_with_adapter_path("references/model-providers/tripo?.md")
        self.assert_cli_failure(code, 3)
        self.assertIn("nonportable", self.stderr.getvalue())
        self.assertNotIn("unavailable", self.stderr.getvalue())

    def test_colon_and_wildcards_in_any_adapter_component_exit_three(self) -> None:
        for adapter_path in (
            "references:/model-providers/tripo.md",
            "references/model-providers/tripo:stream.md",
            "references?/model-providers/tripo.md",
            "references/model-providers?/tripo.md",
            "references/model-providers/tripo?.md",
            "references/model-providers/tripo*.md",
        ):
            with self.subTest(adapter_path=adapter_path):
                self.assert_cli_failure(self.resolve_with_adapter_path(adapter_path), 3)

    def test_windows_forbidden_and_control_adapter_characters_exit_three(self) -> None:
        for character in ('<', '>', '"', '|', "\x01", "\x1f"):
            for adapter_path in (
                f"references{character}/model-providers/tripo.md",
                f"references/model-providers/tripo{character}.md",
            ):
                with self.subTest(adapter_path=adapter_path):
                    self.assert_cli_failure(self.resolve_with_adapter_path(adapter_path), 3)

    def test_trailing_dot_space_and_reserved_adapter_components_exit_three(self) -> None:
        for adapter_path in (
            "references./model-providers/tripo.md",
            "references /model-providers/tripo.md",
            "CON/model-providers/tripo.md",
            "references/model-providers/con.md",
            "references/model-providers/PRN.md",
            "references/model-providers/AUX.txt/tripo.md",
            "references/model-providers/NUL.md",
            "references/model-providers/COM1.md",
            "references/model-providers/lpt9.txt/tripo.md",
            "references/model-providers/COM9.md",
        ):
            with self.subTest(adapter_path=adapter_path):
                self.assert_cli_failure(self.resolve_with_adapter_path(adapter_path), 3)

    def test_superscript_reserved_adapter_components_exit_three(self) -> None:
        for prefix in ("COM", "LPT"):
            for suffix in ("¹", "²", "³"):
                for adapter_path in (
                    f"references/{prefix}{suffix}/tripo.md",
                    f"references/model-providers/{prefix.lower()}{suffix}.md",
                    f"references/model-providers/{prefix}{suffix}.txt/tripo.md",
                ):
                    with self.subTest(adapter_path=adapter_path):
                        self.assert_cli_failure(self.resolve_with_adapter_path(adapter_path), 3)

    def test_nonreserved_lookalike_missing_adapters_remain_unavailable(self) -> None:
        for name in ("CONSOLE.md", "COM0.md", "model.con.md", "COM⁴.md", "LPT0.md", "ordinary-missing.md"):
            with self.subTest(ordinary_missing=name):
                code = self.resolve_with_adapter_path(f"references/model-providers/{name}")
                self.assert_cli_failure(code, 2)

    def test_nonreserved_lookalike_existing_adapters_succeed(self) -> None:
        for name in ("CONSOLE.md", "COM0.md", "model.con.md", "COM⁴.md", "LPT0.md"):
            adapter = self.skill / "references" / "model-providers" / name
            adapter.write_text(f"<!-- provider-kind: model -->\n# {name}\n", encoding="utf-8")
            with self.subTest(valid_existing=name):
                code = self.resolve_with_adapter_path(f"references/model-providers/{name}")
                self.assertEqual(code, 0, self.stderr.getvalue())

    def test_runtime_default_and_explicit_override(self) -> None:
        default = self.module.resolve_provider("kimi", self.project, skill_root=self.skill)
        self.assertEqual(default["source"], "runtime_default")
        self.assertEqual(default["provider_id"], "tripo")
        override = self.module.resolve_provider(
            "kimi", self.project, override="custom", skill_root=self.skill
        )
        self.assertEqual(override["source"], "override")
        self.assertEqual(override["provider_id"], "custom")

    def test_codex_has_no_default(self) -> None:
        self.assert_cli_failure(self.run_main(runtime="codex"), 2)

    def test_project_selection_precedes_runtime_default(self) -> None:
        self.write_selection(
            {"schema_version": "model-provider-selection/v1", "provider_id": "custom"}
        )
        resolved = self.module.resolve_provider("kimi", self.project, skill_root=self.skill)
        self.assertEqual(resolved["source"], "project")
        self.assertEqual(resolved["provider_id"], "custom")

    def test_override_bypasses_malformed_selection(self) -> None:
        path = self.selection_path()
        path.parent.mkdir(parents=True)
        path.write_text("{not json", encoding="utf-8")
        resolved = self.module.resolve_provider(
            "kimi", self.project, override="tripo", skill_root=self.skill
        )
        self.assertEqual(resolved["provider_id"], "tripo")
        self.assertEqual(resolved["source"], "override")

    def test_custom_provider_may_have_empty_defaults(self) -> None:
        override = self.module.resolve_provider(
            "other", self.project, override="custom", skill_root=self.skill
        )
        self.assertEqual(override["provider_id"], "custom")
        self.assertEqual(override["source"], "override")
        self.write_selection(
            {"schema_version": "model-provider-selection/v1", "provider_id": "custom"}
        )
        project = self.module.resolve_provider("other", self.project, skill_root=self.skill)
        self.assertEqual(project["provider_id"], "custom")
        self.assertEqual(project["source"], "project")

    def test_exact_success_fields(self) -> None:
        resolved = self.module.resolve_provider("kimi", self.project, skill_root=self.skill)
        self.assertEqual(
            resolved,
            {
                "schema_version": "model-provider-resolution/v1",
                "provider_id": "tripo",
                "source": "runtime_default",
                "runtime": "kimi",
                "adapter_path": "references/model-providers/tripo.md",
            },
        )

    def test_compact_sorted_json_stdout(self) -> None:
        code = self.run_main()
        self.assertEqual(code, 0)
        self.assertEqual(self.stderr.getvalue(), "")
        self.assertEqual(
            self.stdout.getvalue(),
            '{"adapter_path":"references/model-providers/tripo.md","provider_id":"tripo",'
            '"runtime":"kimi","schema_version":"model-provider-resolution/v1",'
            '"source":"runtime_default"}\n',
        )

    def test_unknown_override_exits_two(self) -> None:
        self.assert_cli_failure(self.run_main("--provider", "unknown"), 2)

    def test_unknown_project_provider_exits_two(self) -> None:
        self.write_selection(
            {"schema_version": "model-provider-selection/v1", "provider_id": "unknown"}
        )
        self.assert_cli_failure(self.run_main(), 2)

    def test_malformed_selection_exits_three(self) -> None:
        path = self.selection_path()
        path.parent.mkdir(parents=True)
        path.write_text("{not json", encoding="utf-8")
        self.assert_cli_failure(self.run_main(), 3)

    def test_unknown_runtime_default_exits_two(self) -> None:
        self.assert_cli_failure(self.run_main(runtime="other"), 2)

    def test_duplicate_runtime_defaults_exit_two(self) -> None:
        registry = copy.deepcopy(REGISTRY)
        registry["providers"]["custom"]["default_for_runtimes"] = ["kimi"]
        self.write_registry(registry)
        self.assert_cli_failure(self.run_main("--provider", "tripo"), 2)

    def test_duplicate_default_inside_provider_is_malformed(self) -> None:
        registry = copy.deepcopy(REGISTRY)
        registry["providers"]["tripo"]["default_for_runtimes"] = ["kimi", "kimi"]
        self.write_registry(registry)
        self.assert_cli_failure(self.run_main(), 3)

    def test_missing_adapter_exits_two(self) -> None:
        (self.skill / "references" / "model-providers" / "tripo.md").unlink()
        self.assert_cli_failure(self.run_main(), 2)

    def test_non_regular_adapter_exits_two(self) -> None:
        adapter = self.skill / "references" / "model-providers" / "tripo.md"
        adapter.unlink()
        adapter.mkdir()
        self.assert_cli_failure(self.run_main(), 2)

    def test_parent_traversal_adapter_paths_exit_three(self) -> None:
        for adapter_path in (
            "../outside.md",
            "references/../outside.md",
            "references/model-providers/../../outside.md",
        ):
            with self.subTest(adapter_path=adapter_path):
                self.assert_cli_failure(self.resolve_with_adapter_path(adapter_path), 3)

    def test_absolute_adapter_paths_exit_three(self) -> None:
        for adapter_path in (
            "/tmp/tripo.md",
            "C:/tmp/tripo.md",
            "C:\\tmp\\tripo.md",
            "\\\\server\\share\\tripo.md",
        ):
            with self.subTest(adapter_path=adapter_path):
                self.assert_cli_failure(self.resolve_with_adapter_path(adapter_path), 3)

    def test_non_markdown_and_non_portable_adapter_paths_exit_three(self) -> None:
        for adapter_path in (
            "references/model-providers/tripo.txt",
            "references/model-providers/tripo",
            "references\\model-providers\\tripo.md",
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
            {"schema_version": "model-provider-selection/v1", "provider_id": "custom"}
        )
        code = self.run_main()
        self.assertEqual(code, 0)
        self.assertEqual(self.stderr.getvalue(), "")
        resolved = json.loads(self.stdout.getvalue())
        self.assertEqual(resolved["provider_id"], "custom")
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
        code = self.run_main("--provider", "tripo")
        self.assertEqual(code, 0)
        self.assertEqual(self.stderr.getvalue(), "")
        resolved = json.loads(self.stdout.getvalue())
        self.assertEqual(resolved["provider_id"], "tripo")
        self.assertEqual(resolved["source"], "override")

    def test_adapter_parent_junction_exits_three(self) -> None:
        external = self.root / "junction-providers"
        external.mkdir()
        (external / "tripo.md").write_text("# external junction\n", encoding="utf-8")
        providers = self.skill / "references" / "model-providers"
        (providers / "tripo.md").unlink()
        (providers / "custom.md").unlink()
        providers.rmdir()
        self.make_junction(providers, external)
        self.assert_cli_failure(self.run_main(), 3)

    def test_trailing_slash_adapter_path_exits_three(self) -> None:
        self.assert_cli_failure(
            self.resolve_with_adapter_path("references/model-providers/tripo.md/"), 3
        )

    def test_dot_segment_adapter_path_exits_three(self) -> None:
        self.assert_cli_failure(
            self.resolve_with_adapter_path("references/model-providers/tripo.md/."), 3
        )

    def test_nul_adapter_path_exits_three(self) -> None:
        self.assert_cli_failure(
            self.resolve_with_adapter_path("references/model-providers/tripo\x00.md"), 3
        )

    def test_symlink_adapter_file_exits_three(self) -> None:
        adapter = self.skill / "references" / "model-providers" / "tripo.md"
        target = self.root / "actual-tripo.md"
        target.write_text("# Tripo\n", encoding="utf-8")
        adapter.unlink()
        try:
            adapter.symlink_to(target)
        except (OSError, NotImplementedError) as error:
            self.skipTest(f"Symlink creation is unavailable: {error}")
        self.assert_cli_failure(self.run_main(), 3)

    def test_dangling_symlink_adapter_file_exits_three(self) -> None:
        adapter = self.skill / "references" / "model-providers" / "tripo.md"
        adapter.unlink()
        try:
            adapter.symlink_to(self.root / "missing-tripo.md")
        except (OSError, NotImplementedError) as error:
            self.skipTest(f"Symlink creation is unavailable: {error}")
        self.assert_cli_failure(self.run_main(), 3)

    def test_symlink_adapter_path_component_exits_three(self) -> None:
        actual = self.root / "actual-providers"
        actual.mkdir()
        (actual / "tripo.md").write_text("# Tripo\n", encoding="utf-8")
        providers = self.skill / "references" / "model-providers"
        (providers / "tripo.md").unlink()
        (providers / "custom.md").unlink()
        providers.rmdir()
        try:
            providers.symlink_to(actual, target_is_directory=True)
        except (OSError, NotImplementedError) as error:
            self.skipTest(f"Directory symlink creation is unavailable: {error}")
        self.assert_cli_failure(self.run_main(), 3)

    def test_duplicate_registry_json_keys_exit_three(self) -> None:
        self.write_raw_registry(
            '{"schema_version":"model-provider-registry/v1",'
            '"schema_version":"model-provider-registry/v1","providers":{}}'
        )
        self.assert_cli_failure(self.run_main(), 3)

    def test_duplicate_nested_registry_json_keys_exit_three(self) -> None:
        self.write_raw_registry(
            '{"schema_version":"model-provider-registry/v1","providers":{"tripo":'
            '{"adapter_path":"references/model-providers/tripo.md",'
            '"adapter_path":"references/model-providers/tripo.md",'
            '"default_for_runtimes":["kimi"]}}}'
        )
        self.assert_cli_failure(self.run_main(), 3)

    def test_duplicate_selection_json_keys_exit_three(self) -> None:
        path = self.selection_path()
        path.parent.mkdir(parents=True)
        path.write_text(
            '{"schema_version":"model-provider-selection/v1",'
            '"provider_id":"tripo","provider_id":"custom"}',
            encoding="utf-8",
        )
        self.assert_cli_failure(self.run_main(), 3)

    def test_registry_schema_and_exact_fields(self) -> None:
        cases = []
        wrong_schema = copy.deepcopy(REGISTRY)
        wrong_schema["schema_version"] = "model-provider-registry/v2"
        cases.append(wrong_schema)
        extra_top = copy.deepcopy(REGISTRY)
        extra_top["extra"] = True
        cases.append(extra_top)
        missing_top = copy.deepcopy(REGISTRY)
        del missing_top["providers"]
        cases.append(missing_top)
        extra_provider = copy.deepcopy(REGISTRY)
        extra_provider["providers"]["tripo"]["extra"] = True
        cases.append(extra_provider)
        missing_provider = copy.deepcopy(REGISTRY)
        del missing_provider["providers"]["tripo"]["adapter_path"]
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
            {"schema_version": "model-provider-selection/v2", "provider_id": "tripo"},
            {"schema_version": "model-provider-selection/v1"},
            {"provider_id": "tripo"},
            {
                "schema_version": "model-provider-selection/v1",
                "provider_id": "tripo",
                "extra": True,
            },
        ):
            with self.subTest(selection=selection):
                self.write_selection(selection)
                self.assert_cli_failure(self.run_main(), 3)

    def test_invalid_identifiers_exit_three(self) -> None:
        for runtime in ("", "Kimi", "1kimi", "kimi_runtime", "kimi.."):
            with self.subTest(runtime=runtime):
                self.assert_cli_failure(self.run_main(runtime=runtime), 3)
        for provider in ("", "Tripo", "1tripo", "model_provider"):
            with self.subTest(provider=provider):
                self.assert_cli_failure(self.run_main("--provider", provider), 3)
        self.write_selection(
            {"schema_version": "model-provider-selection/v1", "provider_id": "Tripo"}
        )
        self.assert_cli_failure(self.run_main(), 3)

    def test_registry_identifier_and_default_shapes_exit_three(self) -> None:
        invalid_registries = []
        bad_provider_id = copy.deepcopy(REGISTRY)
        bad_provider_id["providers"]["Tripo"] = bad_provider_id["providers"].pop("tripo")
        invalid_registries.append(bad_provider_id)
        bad_runtime_id = copy.deepcopy(REGISTRY)
        bad_runtime_id["providers"]["tripo"]["default_for_runtimes"] = ["Kimi"]
        invalid_registries.append(bad_runtime_id)
        non_list_defaults = copy.deepcopy(REGISTRY)
        non_list_defaults["providers"]["tripo"]["default_for_runtimes"] = "kimi"
        invalid_registries.append(non_list_defaults)
        non_string_default = copy.deepcopy(REGISTRY)
        non_string_default["providers"]["tripo"]["default_for_runtimes"] = [1]
        invalid_registries.append(non_string_default)
        non_object_providers = copy.deepcopy(REGISTRY)
        non_object_providers["providers"] = []
        invalid_registries.append(non_object_providers)
        non_object_entry = copy.deepcopy(REGISTRY)
        non_object_entry["providers"]["tripo"] = None
        invalid_registries.append(non_object_entry)
        non_string_path = copy.deepcopy(REGISTRY)
        non_string_path["providers"]["tripo"]["adapter_path"] = 1
        invalid_registries.append(non_string_path)
        for registry in invalid_registries:
            with self.subTest(registry=registry):
                self.write_registry(registry)
                self.assert_cli_failure(self.run_main(), 3)

    def test_malformed_missing_and_unreadable_registry_exit_three(self) -> None:
        self.write_raw_registry("{not json")
        self.assert_cli_failure(self.run_main(), 3)
        (self.skill / "model-providers" / "registry.json").unlink()
        self.assert_cli_failure(self.run_main(), 3)
        (self.skill / "model-providers" / "registry.json").write_bytes(b"\xff")
        self.assert_cli_failure(self.run_main(), 3)

    def test_project_root_must_be_an_existing_directory(self) -> None:
        project_file = self.root / "not-a-directory"
        project_file.write_text("not a directory", encoding="utf-8")
        for root in (project_file, self.root / "missing-project"):
            with self.subTest(root=root):
                code = self.invoke(
                    ["resolve", "--runtime", "kimi", "--project-root", str(root)]
                )
                self.assert_cli_failure(code, 3)

    def test_override_does_not_bypass_project_root_validation(self) -> None:
        project_file = self.root / "not-a-directory"
        project_file.write_text("not a directory", encoding="utf-8")
        code = self.invoke(
            [
                "resolve",
                "--runtime",
                "kimi",
                "--project-root",
                str(project_file),
                "--provider",
                "tripo",
            ]
        )
        self.assert_cli_failure(code, 3)

    def test_project_root_symlink_exits_three(self) -> None:
        actual = self.root / "actual-project"
        actual.mkdir()
        linked = self.root / "linked-project"
        try:
            linked.symlink_to(actual, target_is_directory=True)
        except (OSError, NotImplementedError) as error:
            self.skipTest(f"Directory symlink creation is unavailable: {error}")
        code = self.invoke(
            ["resolve", "--runtime", "kimi", "--project-root", str(linked)]
        )
        self.assert_cli_failure(code, 3)

    def test_project_root_junction_exits_three(self) -> None:
        actual = self.root / "actual-project"
        actual.mkdir()
        linked = self.root / "linked-project"
        self.make_junction(linked, actual)
        code = self.invoke(
            ["resolve", "--runtime", "kimi", "--project-root", str(linked)]
        )
        self.assert_cli_failure(code, 3)

    def test_selection_parent_non_directory_exits_three(self) -> None:
        (self.project / "docs").write_text("not a directory", encoding="utf-8")
        self.assert_cli_failure(self.run_main(), 3)

    def test_selection_non_file_exits_three(self) -> None:
        self.selection_path().mkdir(parents=True)
        self.assert_cli_failure(self.run_main(), 3)

    def test_adapter_parent_non_directory_exits_three(self) -> None:
        adapter = self.skill / "references" / "model-providers" / "tripo.md"
        adapter.unlink()
        (self.skill / "references" / "model-providers" / "custom.md").unlink()
        (self.skill / "references" / "model-providers").rmdir()
        (self.skill / "references" / "model-providers").write_text(
            "not a directory", encoding="utf-8"
        )
        self.assert_cli_failure(self.run_main(), 3)

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
            '{"schema_version":"model-provider-selection/v1","provider_id":"tripo",'
            '"credential":"secret-value"}',
            encoding="utf-8",
        )
        self.assert_cli_failure(self.run_main(), 3)
        self.assertNotIn("secret-value", self.stderr.getvalue())

    def test_resolution_does_not_write_files(self) -> None:
        before = {path.relative_to(self.root) for path in self.root.rglob("*")}
        code = self.run_main("--provider", "custom")
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
        self.assertEqual(resolved["provider_id"], "tripo")
        self.assertEqual(resolved["adapter_path"], "references/model-providers/tripo.md")
        self.assertEqual(
            json.loads(PRODUCTION_REGISTRY.read_text(encoding="utf-8")),
            PRODUCTION_REGISTRY_VALUE,
        )
        adapter = (
            ROOT
            / "godot-game-production"
            / "references"
            / "model-providers"
            / "tripo.md"
        )
        self.assertTrue(adapter.is_file())

    def test_real_subprocess_cli_success_and_failure(self) -> None:
        success = subprocess.run(
            [
                sys.executable,
                "-B",
                str(SCRIPT),
                "resolve",
                "--runtime",
                "kimi",
                "--project-root",
                str(self.project),
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=20,
            check=False,
        )
        self.assertEqual(success.returncode, 0, success.stderr)
        self.assertEqual(success.stderr, "")
        self.assertEqual(
            success.stdout,
            '{"adapter_path":"references/model-providers/tripo.md","provider_id":"tripo",'
            '"runtime":"kimi","schema_version":"model-provider-resolution/v1",'
            '"source":"runtime_default"}\n',
        )
        failure = subprocess.run(
            [
                sys.executable,
                "-B",
                str(SCRIPT),
                "resolve",
                "--runtime",
                "codex",
                "--project-root",
                str(self.project),
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=20,
            check=False,
        )
        self.assertEqual(failure.returncode, 2)
        self.assertEqual(failure.stdout, "")
        self.assertNotEqual(failure.stderr, "")


if __name__ == "__main__":
    unittest.main()
