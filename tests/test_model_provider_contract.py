import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]


def read(relative_path: str) -> str:
    path = ROOT / relative_path
    return path.read_text(encoding="utf-8") if path.is_file() else ""


class NeutralGenerationContractTests(unittest.TestCase):
    def setUp(self):
        self.text = read("godot-game-production/references/model-generation.md")

    def test_request_is_production_work_with_approved_target_and_task(self):
        for value in (
            "`work_kind`",
            "`production_asset`",
            "`asset_id`",
            "`approved_target_id`",
            "`task_budget_id`",
            "`operation`",
            "`generate`",
            "`provider_model`",
            "`input_images`",
            "`source_model`",
            "`source_task_id`",
            "`output_path`",
            "distinct project-local `.glb`",
            "not a new evidence schema",
            "does not create reference-image authorization",
        ):
            with self.subTest(value=value):
                self.assertIn(value, self.text)

    def test_result_preserves_native_identity_and_actual_artifact_paths(self):
        for value in (
            "`status`",
            "`succeeded`",
            "`failed`",
            "`unknown`",
            "`provider_id`",
            "`operation`",
            "`provider_model`",
            "`task_id`",
            "`raw_path`",
            "`accepted_glb_path`",
            "`preview_status`",
            "`preview_path`",
            "`log_path`",
            "`error`",
            "unavailable",
            "malformed",
        ):
            with self.subTest(value=value):
                self.assertIn(value, self.text)

    def test_observation_resumes_same_job_without_duplicate_or_provider_switch(self):
        for value in (
            "model3d_generation_launch.py",
            "model3d_generation_watch.py",
            "same log/PID",
            "no duplicate submission",
            "no provider switch",
            "launch success does not mean operation success",
        ):
            with self.subTest(value=value):
                self.assertIn(value, self.text)

    def test_only_successful_inspected_glb_enters_godot_import(self):
        for value in (
            "Only `succeeded`",
            "model_artifact.py inspect",
            "Godot import",
            "`failed`, `unknown`, `unavailable`, and `malformed`",
            "cannot enter acceptance",
            "provider preview",
            "source/design artifacts",
        ):
            with self.subTest(value=value):
                self.assertIn(value, self.text)


class TripoGenerationAdapterContractTests(unittest.TestCase):
    def setUp(self):
        self.text = read(
            "godot-game-production/references/model-providers/tripo.md"
        )

    def test_native_tripo_identity_and_launcher_are_exact(self):
        for value in (
            "model3d_generation:model3d_generation",
            "Tripo API",
            "model3d_generation_launch.py",
            "model3d_generation_watch.py",
            "`<plugin-root>/skills/model3d_generation/SKILL.md`",
            "two directory levels above",
            "kimi.plugin.json",
        ):
            with self.subTest(value=value):
                self.assertIn(value, self.text)
        self.assertNotIn("model3d_generation:image_generation", self.text)

    def test_native_scope_and_watcher_limits_are_not_overstated(self):
        for value in (
            "detailed 3D modeling of people and animals",
            "unless the user explicitly requests this plugin for another subject",
            "Rigging, animation, and format conversion need other suitable tools",
            "900 seconds since the last log update",
            "download started: fetching generated media",
            "no overall watcher timeout",
        ):
            with self.subTest(value=value):
                self.assertIn(value, self.text)

    def test_generate_supports_exact_text_image_and_multiview_modes(self):
        for value in (
            "`--description`",
            "`--image-url`",
            "`--multiview`",
            "`--front-url`",
            "at least one of `--left-url`, `--back-url`, or `--right-url`",
            "2–4 views",
            "exactly one input mode",
            "public and reachable",
        ):
            with self.subTest(value=value):
                self.assertIn(value, self.text)

    def test_generate_models_low_poly_and_texture_controls_are_truthful(self):
        for value in (
            "`v3.1`",
            "default",
            "`v3.0`",
            "`v2.5`",
            "`p1`",
            "50–20,000 faces",
            "`p2`",
            "48–50,000 faces",
            "48–25,000 with quad output",
            "`--quad` requires an explicit P2 model",
            "`--face-limit`",
            "target, not a hard ceiling",
            "`--no-texture`",
            "`--texture-quality fast|standard|detailed|extreme`",
            "default `standard`",
            "`detailed` is 4K",
            "`extreme` is 8K",
            "`--generate-parts`",
            "only on v3.1",
        ):
            with self.subTest(value=value):
                self.assertIn(value, self.text)

    def test_only_authorized_local_references_use_native_url_conversion(self):
        for value in (
            "image-to-url",
            "only authorized local reference images",
            "signed_url",
            "never unrelated inputs",
            "before starting the model job",
        ):
            with self.subTest(value=value):
                self.assertIn(value, self.text)

    def test_windows_uses_resolved_native_pythonw_in_separate_calls(self):
        for value in (
            "resolve_model3d_pythonw.ps1",
            "MODEL3D_PYTHONW_NOT_FOUND",
            "native `pythonw.exe`",
            "Do not invoke them through `python.exe`",
            "separate foreground",
            "unique report",
            "sys.executable",
        ):
            with self.subTest(value=value):
                self.assertIn(value, self.text)


class ModelRuntimeAndPortableRoutingTests(unittest.TestCase):
    def test_kimi_routes_tripo_through_native_skill_and_actual_plugin_root(self):
        text = read("godot-game-production/references/runtimes/kimi.md")
        for value in (
            "references/model-generation.md",
            "scripts/model_provider.py",
            "--runtime kimi",
            "Kimi host default is `tripo`",
            "native `Skill`",
            "model3d_generation:model3d_generation",
            "actual location",
            "adapter_path",
        ):
            with self.subTest(value=value):
                self.assertIn(value, text)

    def test_codex_requires_explicit_or_project_model_provider(self):
        text = read("godot-game-production/references/runtimes/codex.md")
        for value in (
            "references/model-generation.md",
            "scripts/model_provider.py",
            "--runtime codex",
            "explicit or persisted project selection",
            "Codex has no model-provider default",
            "does not acquire a Kimi credential",
        ):
            with self.subTest(value=value):
                self.assertIn(value, text)
        self.assertNotIn("Kimi host default is `tripo`", text)

    def test_installable_entry_point_routes_generation_before_invocation(self):
        text = read("godot-game-production/SKILL.md")
        route = "**REQUIRED MODEL ADAPTER:**"
        self.assertIn(route, text)
        self.assertIn("references/model-generation.md", text)
        self.assertIn("selected model provider", text)
        self.assertIn("`production_asset`", text)
        self.assertLess(
            text.index(route), text.index("## Production asset authoring")
        )


class TripoProcessingAdapterContractTests(unittest.TestCase):
    def setUp(self):
        self.text = read(
            "godot-game-production/references/model-providers/tripo.md"
        )

    def test_processing_source_and_output_rules_fail_closed(self):
        for value in (
            "`texture`, `segment`, and `decimate`",
            "exactly one source",
            "`--task-id`",
            "`--model-url`",
            "public GLB/GLTF/FBX/OBJ/STL URL",
            "at most 150 MB",
            "successful upstream model task",
            "All four commands require `--output`",
            "distinct local `.glb` path",
            "cannot overwrite",
        ):
            with self.subTest(value=value):
                self.assertIn(value, self.text)

    def test_texture_models_guidance_and_delight_rules_are_exact(self):
        for value in (
            "### Texture",
            "`--model v3.0`",
            "`--model v3.5`",
            "legacy `v2.5`",
            "`--prompt`",
            "`--style-image-url`",
            "requires the prompt",
            "Four images",
            "all four are required",
            "mutually exclusive",
            "`--no-delight`",
            "v3.5-only",
            "does not select a model automatically",
            "Texture seed, per-part texturing, and texture-quality controls are not exposed",
        ):
            with self.subTest(value=value):
                self.assertIn(value, self.text)

    def test_segment_models_and_reference_precedence_are_exact(self):
        for value in (
            "### Segment and complete",
            "geometric segmentation",
            "`--model v1.0`",
            "semantic segmentation",
            "`--model v2.0`",
            "`--granularity simple|balanced|detailed`",
            "default `balanced`",
            "`--no-split-by-connectivity`",
            "`--ref-image-url`",
            "overrides granularity and connectivity",
            "flags alone do not select v2.0",
        ):
            with self.subTest(value=value):
                self.assertIn(value, self.text)

    def test_complete_requires_successful_segment_task_identity(self):
        for value in (
            "successful `segment`",
            "returned segment ID",
            "not the source generation ID",
            "not a model URL or local GLB",
            "`complete --task-id`",
            "`--completion-mode ai_completion`",
            "`quick_cap`",
            "`--part-names`",
            "actual names from the segmentation",
            "Completion's model override is `v1.0`",
            "Preserve both the segmented and completed files",
        ):
            with self.subTest(value=value):
                self.assertIn(value, self.text)

    def test_decimate_models_ranges_and_targets_are_exact(self):
        for value in (
            "### Decimate",
            "v2.0 (`--model v2.0`)",
            "Optional; 500–20,000 when supplied",
            "adaptive reduction",
            "v1.0 (`--model v1.0`)",
            "Required, positive integer up to 2,000,000",
            "Basic decimation",
            "a larger target does not auto-switch the model",
            "does not expose them",
            "no quad selector",
            "target, not a hard ceiling",
            "unverified",
        ):
            with self.subTest(value=value):
                self.assertIn(value, self.text)


class NeutralProcessingAndProvenanceTests(unittest.TestCase):
    def setUp(self):
        self.text = read("godot-game-production/references/model-generation.md")

    def test_processing_preserves_raw_source_and_writes_distinct_output(self):
        for value in (
            "For processing",
            "`raw_path` is the preserved input",
            "distinct processed output",
            "source model and source/task linkage",
            "No operation may overwrite its input",
            "Both are retained and hashed",
        ):
            with self.subTest(value=value):
                self.assertIn(value, self.text)

    def test_independent_workers_all_launch_before_any_watch(self):
        for value in (
            "For independent parallel operations",
            "launch every worker before watching any worker",
            "Monitor each job separately",
            "distinct output and log",
        ):
            with self.subTest(value=value):
                self.assertIn(value, self.text)

    def test_preview_failure_does_not_fail_saved_model_or_duplicate_work(self):
        for value in (
            "`available`, `unavailable`, or `failed`",
            "saved valid model remains successful",
            "preview download fails",
            "Report model and preview outcomes separately",
            "never resubmit",
            "Display preview only when its download is confirmed and the file exists",
        ):
            with self.subTest(value=value):
                self.assertIn(value, self.text)

    def test_face_targets_require_truthful_delivered_mesh_accounting(self):
        for value in (
            "targets, not proof",
            "delivered GLB",
            "`triangle_count_status=verified`",
            "`triangle_count_status=unavailable`",
            "`triangle_count=null`",
            "cannot be verified",
            "strict budget",
        ):
            with self.subTest(value=value):
                self.assertIn(value, self.text)


class ProcessingRawSourceAdmissionRegressionTests(unittest.TestCase):
    def setUp(self):
        self.neutral = read("godot-game-production/references/model-generation.md")
        self.adapter = read(
            "godot-game-production/references/model-providers/tripo.md"
        )

    def source_row(self, source_case: str):
        for line in self.neutral.splitlines():
            cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
            if len(cells) == 3 and cells[0] == source_case:
                return cells[1], cells[2]
        return None

    def assert_native_preflight_is_enforceable(self):
        for value in (
            "Before any processing operation",
            "existing project-local raw source",
            "verified path and SHA-256",
            "explicitly acquire the authorized source",
            "distinct project-local raw path",
            "Neither a public URL nor a task ID is `raw_path`",
            "If neither path is possible, fail preflight without submission",
        ):
            with self.subTest(value=value):
                self.assertIn(value, self.adapter)

    def test_public_model_url_without_local_raw_glb_blocks_submission(self):
        self.assertEqual(
            (
                "Block preflight without submission",
                "No processing artifact; URL is not raw_path; optional explicit acquisition to a distinct project-local raw path with verified path/hash must finish before a new preflight",
            ),
            self.source_row("Public model URL without project-local raw source"),
        )
        self.assert_native_preflight_is_enforceable()

    def test_external_task_id_without_retained_raw_glb_blocks_submission(self):
        self.assertEqual(
            (
                "Block preflight without submission",
                "No processing artifact; task ID is not raw_path; optional explicit acquisition to a distinct project-local raw path with verified path/hash must finish before a new preflight",
            ),
            self.source_row(
                "Externally owned successful task ID without workflow-retained raw source"
            ),
        )
        self.assert_native_preflight_is_enforceable()

    def test_workflow_owned_task_with_hashed_raw_glb_preserves_artifact_set(self):
        self.assertEqual(
            (
                "Allow after raw path/hash verification",
                "raw_path=<project-local raw GLB>; raw_sha256=<verified>; accepted_glb_path=<distinct processed GLB>; accepted_sha256=<computed after save>; retain source task/log",
            ),
            self.source_row(
                "Workflow-owned successful task ID with project-local raw GLB and verified SHA-256"
            ),
        )
        self.assert_native_preflight_is_enforceable()


class ModelProductionSourceAndEvidenceTests(unittest.TestCase):
    def test_production_assets_route_models_and_record_full_provenance(self):
        text = read("godot-game-production/references/production-assets.md")
        for value in (
            "selected model provider",
            "references/model-generation.md",
            "3D model generation",
            "provider/model/operation/task/log",
            "raw and processed paths",
            "preview outcome",
            "hashes",
            "triangle-count status",
            "consuming scene",
            "Godot integration evidence",
        ):
            with self.subTest(value=value):
                self.assertIn(value, text)

    def test_model_refinement_boundary_preserves_visual_approval(self):
        text = read("godot-game-production/references/production-assets.md")
        for value in (
            "Routine model refinements remain autonomous",
            "approved direction and the user's task and budget",
            "New or changed visual direction",
            "reopens reference approval",
            "source/design artifacts",
        ):
            with self.subTest(value=value):
                self.assertIn(value, text)

    def test_model_inspection_precedes_import_without_replacing_runtime_gates(self):
        text = read("godot-game-production/references/production-assets.md")
        for value in (
            "model_artifact.py inspect",
            "Only a successfully inspected local GLB enters Godot import",
            "cannot replace Godot import inspection",
            "consuming-scene capture",
            "independent review",
            "gameplay/release evidence",
        ):
            with self.subTest(value=value):
                self.assertIn(value, text)

    def test_evidence_ledger_does_not_repurpose_image_schemas_for_models(self):
        text = read("godot-game-production/references/evidence-ledger.md")
        for value in (
            "Generated GLB and provider previews",
            "not `target_gameplay_image`",
            "not `imagegen_target`",
            "no new evidence fields",
            "Godot import",
            "consuming-scene capture",
            "independent review",
            "gameplay/release evidence",
        ):
            with self.subTest(value=value):
                self.assertIn(value, text)


def normalized_contract_text(text: str) -> str:
    return " ".join(text.split())


def contract_errors(text: str, required=(), forbidden=()):
    normalized = normalized_contract_text(text)
    errors = [
        f"missing normative clause: {clause}"
        for clause in required
        if clause not in normalized
    ]
    errors.extend(
        f"contradictory clause matched: {label}"
        for label, pattern in forbidden
        if re.search(pattern, normalized, flags=re.IGNORECASE)
    )
    return errors


def custom_provider_section(text: str):
    headings = list(
        re.finditer(r"(?m)^## Add a custom model provider$", text)
    )
    if len(headings) != 1:
        return None
    remainder = text[headings[0].end() :]
    return re.split(r"(?m)^## ", remainder, maxsplit=1)[0]


def custom_artifact_errors(text: str):
    section = custom_provider_section(text)
    if section is None:
        return ["custom provider section must occur exactly once"]
    errors = contract_errors(
        section,
        required=(
            "Adding a custom model provider requires exactly two integration artifacts:",
            "One `model-providers/registry.json` entry",
            "Add one neutral adapter document at the registered path.",
            "No edit to the portable visual-approval sequence is needed or permitted.",
            "There is no common model-generation CLI:",
            "Do not add a third prepared production provider merely to test this extension;",
        ),
        forbidden=(
            (
                "common generation CLI is required",
                r"\bcommon (?:`[^`]+` |model-generation |model generation )?CLI is required",
            ),
            (
                "a common generation CLI is required",
                r"\brequires (?:a )?common (?:`[^`]+` |model-generation |model generation )?CLI\b",
            ),
        ),
    )
    numbered_artifacts = re.findall(r"(?m)^(\d+)\.\s+", section)
    if numbered_artifacts != ["1", "2"]:
        errors.append(
            "integration artifacts must be exactly numbered 1 and 2; observed: "
            + repr(numbered_artifacts)
        )
    return errors


def custom_registration_errors(text: str):
    section = custom_provider_section(text)
    if section is None:
        return ["custom provider section must occur exactly once"]
    return contract_errors(
        section,
        required=(
            "top level to exactly `schema_version` and `providers`",
            "`model-provider-registry/v1`",
            "Provider and runtime IDs must match `[a-z][a-z0-9-]*`.",
            "Each provider entry has exactly `adapter_path` and `default_for_runtimes`.",
            "Set `adapter_path` to an existing portable skill-relative Markdown path beneath the installed skill root.",
            "Reject absolute paths, backslashes, NUL, trailing slashes, and `.`/`..` segments;",
            "without a symlink, junction, or other reparse-point component,",
            "The required `default_for_runtimes` may be empty for an explicit/project-only custom provider.",
            "at most one provider may claim a runtime default across the complete registry.",
        ),
        forbidden=(
            (
                "empty defaults are forbidden",
                r"\bempty (?:arrays|defaults) (?:are|is) (?:forbidden|prohibited|not allowed)\b",
            ),
            (
                "default_for_runtimes must be nonempty",
                r"`default_for_runtimes` (?:must|may) not be empty",
            ),
        ),
    )


def cross_kind_documentation_errors(text: str):
    section = custom_provider_section(text)
    if section is None:
        return ["custom provider section must occur exactly once"]
    return contract_errors(
        section,
        required=(
            "Custom selection uses only `docs/visual-contract/model-provider.json` with `model-provider-selection/v1`",
            "Image `providers/registry.json`, `docs/visual-contract/image-provider.json`, and `image_provider.py` remain separate with their existing image selection precedence.",
            "A model provider ID never selects an image generator, and an image provider ID never selects a model generator.",
        ),
        forbidden=(
            (
                "cross-kind selection is allowed",
                r"\b(?:model|image) provider ID (?:may|can|is allowed to) select an? (?:model|image) generator\b",
            ),
        ),
    )


def readme_selection_errors(text: str):
    return contract_errors(
        text,
        required=(
            "Model-provider precedence is **explicit current-user choice → persisted project choice → host default**.",
            "The Kimi host default is `tripo`. Codex has no model-provider default and therefore requires an explicit or persisted project choice.",
            "docs/visual-contract/model-provider.json",
            '"schema_version": "model-provider-selection/v1"',
            '"provider_id": "tripo"',
            "godot-game-production/scripts/model_provider.py resolve --runtime kimi --project-root .",
            "godot-game-production/scripts/model_provider.py resolve --runtime codex --project-root . --provider tripo",
            "fail closed with no automatic fallback",
        ),
        forbidden=(
            (
                "Codex automatically selects tripo",
                r"\bcodex (?:automatically (?:uses|selects)|defaults to|uses by default) `?tripo`?",
            ),
        ),
    )


def readme_live_boundary_errors(text: str):
    return contract_errors(
        text,
        required=(
            "Live provider testing is not part of the default validation.",
            "requires separate explicit authorization and the native prerequisites above.",
        ),
        forbidden=(
            (
                "live authorization removed",
                r"\bdoes not require separate explicit authorization\b",
            ),
            (
                "live authorization not required",
                r"\bno separate explicit authorization is required\b",
            ),
            (
                "live authorization bypassed",
                r"\bwithout separate explicit authorization\b",
            ),
        ),
    )


class CustomModelProviderExtensionTests(unittest.TestCase):
    def setUp(self):
        self.neutral = read("godot-game-production/references/model-generation.md")
        self.model_registry = json.loads(
            read("godot-game-production/model-providers/registry.json")
        )
        self.image_registry = json.loads(
            read("godot-game-production/providers/registry.json")
        )

    def test_custom_provider_requires_exactly_two_integration_artifacts(self):
        self.assertEqual([], custom_artifact_errors(self.neutral))

    def test_custom_registration_has_exact_fields_safe_paths_and_optional_defaults(self):
        self.assertEqual([], custom_registration_errors(self.neutral))

    def test_custom_provider_does_not_change_image_configuration_or_add_a_third_provider(self):
        self.assertEqual([], cross_kind_documentation_errors(self.neutral))
        self.assertEqual("model-provider-registry/v1", self.model_registry["schema_version"])
        self.assertEqual(["tripo"], list(self.model_registry["providers"]))
        self.assertEqual(
            {
                "adapter_path": "references/model-providers/tripo.md",
                "default_for_runtimes": ["kimi"],
            },
            self.model_registry["providers"]["tripo"],
        )
        self.assertEqual("image-provider-registry/v1", self.image_registry["schema_version"])
        self.assertEqual(["kimi", "codex"], list(self.image_registry["providers"]))


class ReadmeModelProviderDocumentationTests(unittest.TestCase):
    def setUp(self):
        self.text = read("README.md")

    def test_installation_prerequisites_and_prepared_adapter_are_linked(self):
        for value in (
            "Python 3.10+",
            "model3d_generation:model3d_generation",
            "Tripo API",
            "credentials",
            "not vendored",
            "godot-game-production/references/model-generation.md",
            "godot-game-production/references/model-providers/tripo.md",
        ):
            with self.subTest(value=value):
                self.assertIn(value, self.text)

    def test_model_selection_documents_defaults_override_project_json_and_fail_closed(self):
        self.assertEqual([], readme_selection_errors(self.text))

    def test_operations_artifacts_glb_inspection_and_live_boundary_are_complete(self):
        self.assertEqual([], readme_live_boundary_errors(self.text))
        for value in (
            "`generate`",
            "`texture`",
            "`segment`",
            "`complete`",
            "`decimate`",
            "raw model",
            "processed model",
            "preview",
            "provenance",
            'godot-game-production/scripts/model_artifact.py inspect --project-root "<project-root>" --model "<portable-relative.glb>"',
            "Godot import",
            "no common model-generation CLI",
        ):
            with self.subTest(value=value):
                self.assertIn(value, self.text)


NEUTRAL_PATH = "godot-game-production/references/model-generation.md"
README_PATH = "README.md"


def run_group4_documentation_tests(mutations=None):
    mutations = mutations or {}
    original_read = read

    def mutated_read(relative_path: str) -> str:
        return mutations.get(relative_path, original_read(relative_path))

    globals()["read"] = mutated_read
    try:
        suite = unittest.TestSuite()
        for test_class in (
            CustomModelProviderExtensionTests,
            ReadmeModelProviderDocumentationTests,
        ):
            suite.addTests(unittest.defaultTestLoader.loadTestsFromTestCase(test_class))
        result = unittest.TestResult()
        suite.run(result)
        return result
    finally:
        globals()["read"] = original_read


def surviving_review_mutations(neutral: str, readme: str):
    return (
        (
            "fourth_integration_artifact",
            {
                NEUTRAL_PATH: neutral
                + "\n4. Add a generated provider manifest as another required integration artifact.\n"
            },
        ),
        (
            "common_generation_cli_required",
            {
                NEUTRAL_PATH: neutral
                + "\nA common `model_generate.py` CLI is required to invoke every custom provider.\n"
            },
        ),
        (
            "empty_defaults_forbidden",
            {
                NEUTRAL_PATH: neutral.replace(
                    "`default_for_runtimes` may be empty for an explicit/project-only custom provider.",
                    "`default_for_runtimes` may be empty for an explicit/project-only custom provider. Empty arrays are forbidden.",
                )
            },
        ),
        (
            "cross_kind_selection_allowed",
            {
                NEUTRAL_PATH: neutral.replace(
                    "A model provider ID never selects an image generator, and an image provider ID never\nselects a model generator.",
                    "A model provider ID may select an image generator, and an image provider ID may\nselect a model generator.",
                )
            },
        ),
        (
            "image_registry_reference_removed",
            {NEUTRAL_PATH: neutral.replace("Image `providers/registry.json`,", "Image configuration,")},
        ),
        (
            "codex_default_contradiction",
            {
                README_PATH: readme.replace(
                    "The Kimi host default is `tripo`. Codex has no model-provider default and therefore\nrequires an explicit or persisted project choice.",
                    "The Kimi host default is `tripo`. Codex has no model-provider default and therefore\nrequires an explicit or persisted project choice. Codex automatically uses `tripo` when no selection exists.",
                )
            },
        ),
        (
            "live_testing_without_explicit_authorization",
            {
                README_PATH: readme.replace(
                    "requires separate explicit authorization",
                    "does not require separate explicit authorization",
                )
            },
        ),
    )


class Group4DocumentationMutationTests(unittest.TestCase):
    def test_current_documents_pass_all_six_group4_documentation_tests(self):
        result = run_group4_documentation_tests()
        self.assertEqual(6, result.testsRun)
        self.assertTrue(
            result.wasSuccessful(),
            "\n".join(str(test) for test, _ in result.failures + result.errors),
        )

    def test_all_seven_previous_surviving_mutants_are_rejected(self):
        neutral = read(NEUTRAL_PATH)
        readme = read(README_PATH)
        originals = {NEUTRAL_PATH: neutral, README_PATH: readme}
        for name, mutations in surviving_review_mutations(neutral, readme):
            with self.subTest(mutant=name):
                for path, changed in mutations.items():
                    self.assertNotEqual(originals[path], changed)
                result = run_group4_documentation_tests(mutations)
                self.assertEqual(6, result.testsRun)
                self.assertFalse(
                    result.wasSuccessful(), f"documentation mutant survived: {name}"
                )


class CrossKindProviderCliRegressionTests(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory(
            prefix="group4-cross-kind-"
        )
        self.addCleanup(self.temporary_directory.cleanup)
        self.project_root = self.temporary_directory.name

    def run_resolver(self, script_name: str, provider: str):
        environment = os.environ.copy()
        environment["PYTHONDONTWRITEBYTECODE"] = "1"
        return subprocess.run(
            [
                sys.executable,
                "-B",
                str(ROOT / "godot-game-production" / "scripts" / script_name),
                "resolve",
                "--runtime",
                "kimi",
                "--project-root",
                self.project_root,
                "--provider",
                provider,
            ],
            cwd=ROOT,
            env=environment,
            text=True,
            capture_output=True,
            timeout=20,
            check=False,
        )

    def assert_cross_kind_rejection(self, result):
        self.assertEqual(2, result.returncode, result.stderr)
        self.assertEqual("", result.stdout)
        self.assertNotEqual("", result.stderr)

    def test_model_resolver_rejects_image_provider_kimi(self):
        self.assert_cross_kind_rejection(self.run_resolver("model_provider.py", "kimi"))

    def test_image_resolver_rejects_model_provider_tripo(self):
        self.assert_cross_kind_rejection(self.run_resolver("image_provider.py", "tripo"))

    def test_model_resolver_accepts_tripo(self):
        result = self.run_resolver("model_provider.py", "tripo")
        self.assertEqual(0, result.returncode, result.stderr)
        resolution = json.loads(result.stdout)
        self.assertEqual("tripo", resolution["provider_id"])
        self.assertEqual("override", resolution["source"])

    def test_image_resolver_accepts_kimi(self):
        result = self.run_resolver("image_provider.py", "kimi")
        self.assertEqual(0, result.returncode, result.stderr)
        resolution = json.loads(result.stdout)
        self.assertEqual("kimi", resolution["provider_id"])
        self.assertEqual("override", resolution["source"])


if __name__ == "__main__":
    unittest.main()
