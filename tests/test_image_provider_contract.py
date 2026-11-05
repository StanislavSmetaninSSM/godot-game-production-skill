from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


def read(relative_path: str) -> str:
    return (ROOT / relative_path).read_text(encoding="utf-8")


class KimiRuntimeAndProviderContractTests(unittest.TestCase):
    def test_kimi_runtime_uses_real_kimi_capabilities(self):
        text = read("godot-game-production/references/runtimes/kimi.md")
        for value in (
            "superpowers:brainstorming",
            "spec-kit-superpowers-bridge",
            "image_generation:image_generation",
            "ReadMediaFile",
            "native `Skill`",
            "godot-game-production/scripts/image_provider.py",
            "adapter_path",
            "references/image-generation.md",
        ):
            with self.subTest(value=value):
                self.assertIn(value, text)

    def test_kimi_runtime_is_public_and_portable(self):
        text = read("godot-game-production/references/runtimes/kimi.md")
        for value in ("C:/Users/Eja", "daimon-share", "private credential"):
            with self.subTest(value=value):
                self.assertNotIn(value, text)

    def test_kimi_provider_preserves_job_and_png_boundaries(self):
        text = read("godot-game-production/references/providers/kimi.md")
        for value in (
            "image_generation_launch.py",
            "image_generation_watch.py",
            "image-to-url",
            "same log and PID",
            "raw file",
            "project-local PNG",
            "no automatic retry",
            "no provider switch",
            "bounded concurrency",
            "serial execution",
            "launch success is not generation success",
        ):
            with self.subTest(value=value):
                self.assertIn(value, text)

    def test_kimi_provider_preflights_dependencies_and_credentials(self):
        text = read("godot-game-production/references/providers/kimi.md")
        for value in (
            "image_generation:image_generation",
            "agent-gw Python SDK",
            "0.2.6 or newer",
            "KIMI_API_KEY",
            "~/.kimi/agent-gw.json",
            "without generating",
            "absolute path",
        ):
            with self.subTest(value=value):
                self.assertIn(value, text)

    def test_kimi_provider_enforces_dimension_and_background_rules(self):
        text = read("godot-game-production/references/providers/kimi.md")
        for value in (
            "positive multiples of 16",
            "at most 3840",
            "at most 3:1",
            "655,360",
            "8,294,400",
            "transparent output requires PNG",
        ):
            with self.subTest(value=value):
                self.assertIn(value, text)

    def test_kimi_provider_uploads_only_authorized_work_inputs(self):
        text = read("godot-game-production/references/providers/kimi.md")
        for value in (
            "public URL",
            "only files belonging to the authorized work",
            "never unrelated inputs",
        ):
            with self.subTest(value=value):
                self.assertIn(value, text)

    def test_kimi_provider_normalizes_outcomes_without_fabrication(self):
        text = read("godot-game-production/references/providers/kimi.md")
        for value in (
            "succeeded",
            "failed",
            "unknown",
            "unavailable",
            "malformed",
            "provider_id",
            "job_id",
            "media_type",
            "accepted_png_path",
            "no fabricated file/path",
            "cannot enter subsequent evidence steps",
        ):
            with self.subTest(value=value):
                self.assertIn(value, text)


class CodexRuntimeAndProviderContractTests(unittest.TestCase):
    def test_codex_runtime_retains_native_workflow_capabilities(self):
        path = ROOT / "godot-game-production/references/runtimes/codex.md"
        self.assertTrue(path.is_file(), "Codex runtime adapter is missing")
        text = path.read_text(encoding="utf-8")
        for value in (
            "brainstorming",
            "spec-kit-superpowers-bridge",
            "test-driven-development",
            "native Codex",
            "actual bitmap",
        ):
            with self.subTest(value=value):
                self.assertIn(value, text)

    def test_codex_provider_uses_builtin_imagegen_without_kimi_launcher(self):
        text = read("godot-game-production/references/providers/codex.md")
        for value in (
            "built-in `imagegen`",
            "AUTHORIZED",
            "authorization_id",
            "one generation request",
            "SHA-256",
        ):
            with self.subTest(value=value):
                self.assertIn(value, text)
        self.assertNotIn("image_generation_launch.py", text)
        self.assertNotIn("Kimi launcher", text)

    def test_prepared_adapters_share_outcome_contract(self):
        for provider in ("kimi", "codex"):
            with self.subTest(provider=provider):
                text = read(
                    f"godot-game-production/references/providers/{provider}.md"
                )
                for value in (
                    "succeeded", "failed", "unknown", "unavailable",
                    "malformed", "Only `succeeded`", "no automatic retry",
                ):
                    with self.subTest(value=value):
                        self.assertIn(value, text)

    def test_codex_remains_the_codex_host_default(self):
        self.assertIn("Codex host default is `codex`", read("README.md"))


class NeutralImageGenerationContractTests(unittest.TestCase):
    def setUp(self):
        self.text = read("godot-game-production/references/image-generation.md")

    def test_request_fields_and_reference_authorization_boundary(self):
        for value in (
            "`work_kind`",
            "`reference`",
            "`production_asset`",
            "`subject_id`",
            "`authorization_id`",
            "`description`",
            "`size`",
            "`background`",
            "`reference_images`",
            "`output_path`",
            "required for reference",
            "absent for ordinary production assets",
        ):
            with self.subTest(value=value):
                self.assertIn(value, self.text)

    def test_result_fields_and_success_gate(self):
        for value in (
            "`status`",
            "`succeeded`",
            "`failed`",
            "`unknown`",
            "`provider_id`",
            "`job_id`",
            "`raw_path`",
            "`accepted_png_path`",
            "`media_type`",
            "`error`",
            "Only `succeeded`",
            "readable project-local accepted PNG",
            "authorization",
            "slot binding",
            "actual bitmap display, SHA-256 binding",
        ):
            with self.subTest(value=value):
                self.assertIn(value, self.text)

    def test_unsuccessful_or_malformed_results_fail_closed(self):
        for value in ("failed", "unknown", "unavailable", "malformed"):
            with self.subTest(value=value):
                self.assertIn(value, self.text)
        self.assertIn("cannot enter subsequent visual evidence", self.text)
        self.assertIn("partial batches", self.text)
        self.assertIn("no target approval", self.text)

    def test_failure_recovery_requires_new_complete_batch_authorization(self):
        for value in (
            "NEW decision ID",
            "COMPLETE affected batch",
            "fresh authorization",
            "retain consumed decision/authorization",
            "no automatic retry",
            "no provider switch",
            "same job",
            "technical failure is not image rejection",
        ):
            with self.subTest(value=value):
                self.assertIn(value, self.text)

    def test_reference_and_production_budgets_remain_distinct(self):
        for value in (
            "one authorized result per reference slot",
            "complete candidate batch",
            "autonomous refinement",
            "approved direction/task budget",
            "without inventing reference authorization",
            "preflight failure before invocation consumes no result budget",
        ):
            with self.subTest(value=value):
                self.assertIn(value, self.text)

    def test_existing_evidence_schemas_and_provenance_stay_unchanged(self):
        for value in (
            "visual-decision/v2",
            "visual-generation-authorization/v1",
            "evidence-run/v2",
            "imagegen_target",
            "remain unchanged",
        ):
            with self.subTest(value=value):
                self.assertIn(value, self.text)


class PortableCoreContractTests(unittest.TestCase):
    def test_portable_core_has_no_codex_imagegen_requirement(self):
        for path in (
            "godot-game-production/SKILL.md",
            "godot-game-production/references/production-assets.md",
        ):
            with self.subTest(path=path):
                text = read(path)
                self.assertNotIn("Use `imagegen`", text)
                self.assertNotIn("invoke ImageGen", text)
                self.assertIn("references/image-generation.md", text)
                self.assertIn("selected image provider", text)

    def test_visual_contract_routes_through_neutral_adapter(self):
        text = read("godot-game-production/references/visual-contract.md")
        self.assertNotIn("ImageGen", text)
        self.assertIn("references/image-generation.md", text)
        self.assertIn("selected image provider", text)

    def test_skill_retains_reference_authorization_and_correction_gates(self):
        text = read("godot-game-production/SKILL.md")
        for value in (
            "AUTHORIZED",
            "one generation request",
            "authorized slot",
            "authorization_id",
            "complete authorized candidate batch",
            "visual-correction-approval/v1",
            "fresh authorization",
            "target approval",
        ):
            with self.subTest(value=value):
                self.assertIn(value, text)

    def test_existing_godot_evidence_gates_are_retained(self):
        skill = read("godot-game-production/SKILL.md")
        visual = read("godot-game-production/references/visual-contract.md")
        for value in (
            "actual bitmap presentation",
            "project-local PNG",
            "SHA-256 binding",
            "buildability",
            "motion cue",
            "sound cue",
            "target-Godot input/state/outcome evidence",
            "TDD",
            "independent review",
            "core play",
            "systems/holism",
            "content",
            "visual",
            "audio/feedback",
            "UX/onboarding",
            "reliability/performance",
            "ship",
        ):
            with self.subTest(value=value):
                self.assertIn(value, visual)
        for value in ("input, state, outcome", "independent review", "A screenshot never proves mechanics"):
            with self.subTest(value=value):
                self.assertIn(value, skill)

    def test_legacy_imagegen_target_is_provider_neutral_not_renamed(self):
        text = read("godot-game-production/references/evidence-ledger.md")
        self.assertIn("imagegen_target", text)
        self.assertIn("legacy identifier is provider-neutral", text)
        self.assertIn("references/image-generation.md", text)


class KimiReadmeContractTests(unittest.TestCase):
    def test_kimi_installation_invocation_and_prerequisites(self):
        text = read("README.md")
        for value in (
            "## Kimi Work installation and invocation",
            "~/.agents/skills/godot-game-production/",
            "godot-game-production/SKILL.md",
            "new session",
            "reload",
            "$godot-game-production",
            "image_generation:image_generation",
            "credentials are prerequisites",
            "not vendored secrets",
        ):
            with self.subTest(value=value):
                self.assertIn(value, text)

    def test_existing_codex_installation_and_update_docs_remain(self):
        text = read("README.md")
        for value in (
            "install-skill-from-github.py",
            "### Windows (PowerShell)",
            "### macOS and Linux (shell)",
            "## Safe updates",
            "Restart or reload Codex",
        ):
            with self.subTest(value=value):
                self.assertIn(value, text)


class ProviderSelectionDocumentationContractTests(unittest.TestCase):
    def setUp(self):
        self.readme = read("README.md")
        self.neutral = read("godot-game-production/references/image-generation.md")

    def test_readme_documents_selection_precedence_and_host_defaults(self):
        self.assertIn(
            "explicit current-user choice → persisted project choice → host default",
            self.readme,
        )
        self.assertIn("Kimi host default is `kimi`", self.readme)
        self.assertIn("Codex host default is `codex`", self.readme)

    def test_readme_documents_project_selection_schema_and_example(self):
        for value in (
            "docs/visual-contract/image-provider.json",
            "image-provider-selection/v1",
            "exactly `schema_version` and `provider_id` fields",
            "prepared provider IDs are `kimi` and `codex`",
            '''{
  "schema_version": "image-provider-selection/v1",
  "provider_id": "kimi"
}''',
        ):
            with self.subTest(value=value):
                self.assertIn(value, self.readme)

    def test_readme_documents_override_commands_and_fail_closed_resolution(self):
        for value in (
            "python godot-game-production/scripts/image_provider.py resolve --runtime kimi --project-root .",
            "python godot-game-production/scripts/image_provider.py resolve --runtime codex --project-root .",
            "python godot-game-production/scripts/image_provider.py resolve --runtime kimi --project-root . --provider codex",
            "override bypasses project configuration, including malformed persisted configuration",
            "unknown, ambiguous, or unavailable selection",
            "no fallback occurs",
            "only selects and validates the adapter",
            "performs no generation or provider availability check",
            "adapter performs its own preflight",
        ):
            with self.subTest(value=value):
                self.assertIn(value, self.readme)

    def test_neutral_contract_documents_two_artifact_custom_provider_extension(self):
        for value in (
            "exactly two integration artifacts",
            "godot-game-production/providers/registry.json",
            "adapter path",
            "unique runtime defaults",
            "one provider adapter document implementing the neutral request/result contract",
            "does not need or permit any edit to the portable visual-approval sequence",
            "image-provider-registry/v1",
            "`adapter_path`",
            "`default_for_runtimes`",
            "required nonempty array",
            "Do not add a common generation CLI",
        ):
            with self.subTest(value=value):
                self.assertIn(value, self.neutral)

    def test_neutral_contract_maps_resolution_failures_to_exit_classes(self):
        for value in (
            "malformed configuration | exit `3`",
            "unknown provider | exit `2`",
            "missing adapter | exit `2`",
            "duplicate runtime default | exit `2`",
            "unsafe path | exit `3`",
            "without automatic provider switching",
        ):
            with self.subTest(value=value):
                self.assertIn(value, self.neutral)


class ReviewRemediationContractTests(unittest.TestCase):
    def test_entry_point_routes_kimi_before_dependent_phases_and_generation(self):
        text = read("godot-game-production/SKILL.md")
        route = "On Kimi Work, read `references/runtimes/kimi.md`"
        self.assertIn(route, text)
        self.assertIn("before dependent phase skills/generation", text)
        self.assertLess(
            text.index(route),
            text.index("**REQUIRED SUB-SKILL:** Use `brainstorming`"),
        )
        self.assertLess(text.index(route), text.index("**REQUIRED IMAGE ADAPTER:**"))

    def test_entry_point_routes_codex_before_dependent_phases_and_generation(self):
        text = read("godot-game-production/SKILL.md")
        route = "On Codex, read `references/runtimes/codex.md`"
        self.assertIn(route, text)
        self.assertIn("before dependent phase skills/generation", text)
        self.assertLess(
            text.index(route),
            text.index("**REQUIRED SUB-SKILL:** Use `brainstorming`"),
        )
        self.assertLess(text.index(route), text.index("**REQUIRED IMAGE ADAPTER:**"))

    def test_readme_shared_workflow_has_no_global_codex_imagegen_requirement(self):
        text = read("README.md")
        shared = text.split("## Installation", 1)[0]
        for value in (
            "is a Codex skill",
            "before ImageGen",
            "ImageGen, or a combination",
            "considers ImageGen",
            "Codex with skill loading enabled",
            "available to Codex",
            "the skill uses Codex `imagegen`",
        ):
            with self.subTest(value=value):
                self.assertNotIn(value, shared)
        for value in (
            "shared skill for Kimi Work and Codex",
            "selected image provider",
            "godot-game-production/references/image-generation.md",
            "A supported host (Kimi Work or Codex) with skill loading enabled",
        ):
            with self.subTest(value=value):
                self.assertIn(value, shared)

    def test_unavailable_preflight_maps_to_failed_neutral_status(self):
        text = read("godot-game-production/references/providers/kimi.md")
        for value in (
            "`status: failed`",
            "unavailable-provider `error`",
            "`unknown` is reserved for an unresolved invoked job",
        ):
            with self.subTest(value=value):
                self.assertIn(value, text)
        self.assertNotIn("preflight failure is `unavailable` or `failed`", text)

    def test_legacy_imagegen_note_is_historical_not_test_oriented(self):
        text = read("godot-game-production/SKILL.md")
        self.assertIn("historical ImageGen name is provider-neutral", text)
        self.assertNotIn("contract checks", text)


if __name__ == "__main__":
    unittest.main()
