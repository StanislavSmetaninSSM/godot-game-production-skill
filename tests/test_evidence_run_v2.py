import importlib.util
import hashlib
import copy
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "godot-game-production" / "scripts" / "evidence_run.py"
sys.path.insert(0, str(SCRIPT.parent))
import visual_contract
SPEC = importlib.util.spec_from_file_location("evidence_run_under_test", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
EVIDENCE_RUN = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(EVIDENCE_RUN)


def target_approval(
    recorded_at: str = "2026-08-20T10:00:00+10:00",
    binding_sha256: str = "0" * 64,
    approval_artifact_id: str = "scope-approval-artifact",
) -> dict[str, object]:
    return {
        "approval_artifact_id": approval_artifact_id,
        "reviewer_id": "visual-user",
        "decision": "approved",
        "recorded_at": recorded_at,
        "binding_sha256": binding_sha256,
    }


def slot(
    slot_id: str = "REF-01",
    *,
    change_kind: str = "initial",
    supersedes_target_id: str | None = None,
) -> dict[str, object]:
    return {
        "reference_slot_id": slot_id,
        "target_kind": "gameplay_state",
        "subject": "normal traversal",
        "visual_question": "canonical play-distance composition",
        "coverage": ["exploration/default"],
        "composition": {
            "camera": "side view",
            "angle": "canonical gameplay angle",
            "environment": "one-room test space",
            "characters": "player and one readable hazard",
            "ui": "gameplay HUD",
            "vfx": "interaction cue",
        },
        "motion_cue": "player movement direction",
        "sound_cue": "interaction confirmation",
        "dependent_work": ["core-loop presentation"],
        "rationale": "No approved target resolves this composition.",
        "presentation": {
            "title": "Primary traversal state",
            "image_description": (
                "Side-view gameplay with the player crossing a compact room "
                "past one readable hazard, with the HUD and interaction effect visible"
            ),
            "purpose": "The reference settles the core gameplay composition",
        },
        "image_count": 1,
        "change_kind": change_kind,
        "supersedes_target_id": supersedes_target_id,
    }


def plan() -> dict[str, object]:
    return {
        "plan_id": "vrp-001",
        "revision": 1,
        "kind": "initial",
        "base_contract_id": None,
        "rows": [slot()],
        "approval": None,
    }


class EvidenceRunV2SchemaTests(unittest.TestCase):
    def manifest(self) -> dict[str, object]:
        return EVIDENCE_RUN._manifest_template(
            builder_id="builder",
            dimension="2d",
            procedural_mode="none",
        )

    def test_template_uses_only_v2_visual_records(self) -> None:
        manifest = self.manifest()
        self.assertEqual(manifest["schema_version"], "evidence-run/v2")
        self.assertEqual(manifest["reference_plans"], [])
        self.assertEqual(manifest["visual_decisions"], [])
        self.assertEqual(manifest["visual_scope_approvals"], [])
        self.assertEqual(manifest["visual_correction_approvals"], [])
        self.assertEqual(manifest["visual_generation_authorizations"], [])
        self.assertEqual(manifest["visual_contract_versions"], [])
        self.assertIsNone(manifest["active_visual_contract_id"])
        self.assertNotIn("approved_visual_contract", manifest)

    def test_v1_manifest_is_rejected(self) -> None:
        manifest = self.manifest()
        manifest["schema_version"] = "evidence-run/v1"
        with self.assertRaisesRegex(EVIDENCE_RUN.SchemaError, "wrong schema version"):
            EVIDENCE_RUN._validate_schema(manifest)

    def test_plan_row_requires_exactly_one_image(self) -> None:
        manifest = self.manifest()
        invalid = plan()
        invalid["rows"][0]["image_count"] = 2
        manifest["reference_plans"] = [invalid]
        with self.assertRaisesRegex(EVIDENCE_RUN.SchemaError, "image_count"):
            EVIDENCE_RUN._validate_schema(manifest)

    def test_target_artifact_requires_slot_and_generation_time(self) -> None:
        manifest = self.manifest()
        manifest["artifacts"] = [
            {
                "id": "target-artifact-01",
                "kind": "target_gameplay_image",
                "provenance": "imagegen_target",
                "path": "docs/visual-contract/vc-001/targets/target-01.png",
                "sha256": "0" * 64,
                "media_type": "image/png",
                "target_id": "TARGET-01",
                "coverage": ["exploration/default"],
            }
        ]
        with self.assertRaisesRegex(EVIDENCE_RUN.SchemaError, "target image fields"):
            EVIDENCE_RUN._validate_schema(manifest)

    def initial_decision(self) -> dict[str, object]:
        return {
            "schema_version": "visual-decision/v2",
            "decision_id": "00000000-0000-4000-8000-000000000001",
            "builder_id": "builder",
            "created_at": "2026-08-20T09:00:00+10:00",
            "decision_kind": "initial_scope",
            "state": "REFERENCE_SCOPE_PENDING",
            "generation_status": "not_started",
            "reference_plan": plan(),
            "user_interface": {
                "language": "en",
                "scope_question": (
                    "Do you approve this exact image set for generation?"
                ),
                "target_question": (
                    "Do you approve this exact displayed image set?"
                ),
            },
        }

    def scope_approval(self, decision: dict[str, object]) -> dict[str, object]:
        return {
            "schema_version": "visual-scope-approval/v1",
            "approval_artifact_id": "scope-approval-artifact",
            "decision_id": decision["decision_id"],
            "reviewer_id": "visual-user",
            "decision": "approved",
            "recorded_at": "2026-08-20T10:00:00+10:00",
            "decision_sha256": visual_contract.canonical_sha256(decision),
            "plan_sha256": visual_contract.canonical_plan_sha256(
                decision["reference_plan"]
            ),
            "approved_slot_ids": ["REF-01"],
        }

    def complete_visual_sources(self) -> dict[str, object]:
        manifest = self.manifest()
        decision = self.initial_decision()
        approval = self.scope_approval(decision)
        stored_plan = copy.deepcopy(decision["reference_plan"])
        stored_plan["approval"] = approval
        manifest["visual_decisions"] = [decision]
        manifest["visual_scope_approvals"] = [approval]
        manifest["reference_plans"] = [stored_plan]
        return manifest

    def target_artifact(self) -> dict[str, object]:
        return {
            "id": "target-artifact-01", "kind": "target_gameplay_image",
            "provenance": "imagegen_target", "path": "target.png",
            "sha256": "0" * 64, "media_type": "image/png",
            "target_id": "TARGET-01", "reference_slot_id": "REF-01",
            "generated_at": "2026-08-20T10:05:00+10:00",
            "coverage": ["exploration/default"], "plan_id": "vrp-001",
            "plan_revision": 1, "authorization_id": "vga-001",
        }

    def review_artifact(self) -> dict[str, object]:
        return {
            "id": "review-artifact-01", "kind": "review_record",
            "provenance": "review_record", "path": "review.txt",
            "sha256": "0" * 64, "media_type": "text/plain",
        }

    def test_manifest_rejects_missing_visual_source_array(self) -> None:
        for field in (
            "visual_decisions", "visual_scope_approvals",
            "visual_correction_approvals", "visual_generation_authorizations",
        ):
            with self.subTest(field=field):
                manifest = self.manifest()
                del manifest[field]
                with self.assertRaisesRegex(EVIDENCE_RUN.SchemaError, "top-level manifest fields differ"):
                    EVIDENCE_RUN._validate_schema(manifest)

    def test_generated_artifact_requires_authorization_id(self) -> None:
        manifest = self.manifest()
        row = self.target_artifact()
        row.pop("authorization_id", None)
        manifest["artifacts"] = [row]
        with self.assertRaisesRegex(EVIDENCE_RUN.SchemaError, "target image authorization_id"):
            EVIDENCE_RUN._validate_schema(manifest)

    def test_non_generated_artifact_rejects_authorization_id(self) -> None:
        manifest = self.manifest()
        row = self.review_artifact()
        row["authorization_id"] = "vga-001"
        manifest["artifacts"] = [row]
        with self.assertRaisesRegex(EVIDENCE_RUN.SchemaError, "only generated target artifacts may carry authorization_id"):
            EVIDENCE_RUN._validate_schema(manifest)

    def test_reference_plan_resolves_decision_and_scope_approval(self) -> None:
        evidence_run = EVIDENCE_RUN
        evidence_run._validate_schema(self.complete_visual_sources())

    def test_reference_plan_rejects_unresolvable_scope_approval(self) -> None:
        manifest = self.complete_visual_sources()
        manifest["visual_scope_approvals"] = []
        with self.assertRaisesRegex(EVIDENCE_RUN.SchemaError, "reference plan scope approval does not resolve"):
            EVIDENCE_RUN._validate_schema(manifest)

    def test_scope_approval_rejects_reference_not_proof_decision(self) -> None:
        manifest = self.manifest()
        decision = {
            "schema_version": "visual-decision/v2",
            "decision_id": "00000000-0000-4000-8000-000000000002",
            "builder_id": "builder",
            "created_at": "2026-08-20T09:00:00+10:00",
            "decision_kind": "reference_not_proof",
            "state": "UNCHANGED",
            "generation_status": "not_authorized",
            "verdict": "rejected",
            "preserved_evidence": list(visual_contract.CANONICAL_PROOF_GATES),
            "user_interface": {
                "language": "en",
                "message": (
                    "This reference guides visual direction but does not replace "
                    "runtime or release evidence."
                ),
            },
        }
        approval = {
            "schema_version": "visual-scope-approval/v1",
            "approval_artifact_id": "scope-approval-artifact",
            "decision_id": decision["decision_id"],
            "reviewer_id": "visual-user",
            "decision": "approved",
            "recorded_at": "2026-08-20T10:00:00+10:00",
            "decision_sha256": visual_contract.canonical_sha256(decision),
            "plan_sha256": visual_contract.canonical_plan_sha256(plan()),
            "approved_slot_ids": ["REF-01"],
        }
        manifest["visual_decisions"] = [decision]
        manifest["visual_scope_approvals"] = [approval]
        with self.assertRaisesRegex(
            EVIDENCE_RUN.SchemaError,
            "reference_not_proof decision may not be referenced by a scope approval",
        ):
            EVIDENCE_RUN._validate_schema(manifest)

    def test_decision_embedded_plan_must_match_stored_plan(self) -> None:
        manifest = self.complete_visual_sources()
        manifest["reference_plans"][0]["rows"][0]["subject"] = "drifted"
        with self.assertRaisesRegex(EVIDENCE_RUN.SchemaError, "decision reference plan differs"):
            EVIDENCE_RUN._validate_schema(manifest)


class InitialVisualContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        (self.root / "project.godot").write_text("[application]\n", encoding="utf-8")

    def tearDown(self) -> None:
        self.temp.cleanup()

    def artifact(
        self,
        artifact_id: str,
        kind: str,
        provenance: str,
        relative_path: str,
        content: bytes,
        **extra: object,
    ) -> dict[str, object]:
        path = self.root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
        return {
            "id": artifact_id,
            "kind": kind,
            "provenance": provenance,
            "path": relative_path,
            "sha256": hashlib.sha256(content).hexdigest(),
            "media_type": "image/png" if kind == "target_gameplay_image" else "text/plain",
            **(
                {"plan_id": "vrp-001", "plan_revision": 1}
                if kind == "target_gameplay_image" else {}
            ),
            **extra,
        }

    def initial_sources(self, manifest: dict[str, object]) -> tuple[dict[str, object], dict[str, object]]:
        decision = {
            "schema_version": "visual-decision/v2",
            "decision_id": "00000000-0000-4000-8000-000000000011",
            "builder_id": "builder",
            "created_at": "2026-08-20T09:00:00+10:00",
            "decision_kind": "initial_scope",
            "state": "REFERENCE_SCOPE_PENDING",
            "generation_status": "not_started",
            "reference_plan": plan(),
            "user_interface": {
                "language": "en",
                "scope_question": (
                    "Do you approve this exact image set for generation?"
                ),
                "target_question": (
                    "Do you approve this exact displayed image set?"
                ),
            },
        }
        scope_approval = {
            "schema_version": "visual-scope-approval/v1",
            "approval_artifact_id": "scope-approval-artifact",
            "decision_id": decision["decision_id"],
            "reviewer_id": "visual-user",
            "decision": "approved",
            "recorded_at": "2026-08-20T10:00:00+10:00",
            "decision_sha256": visual_contract.canonical_sha256(decision),
            "plan_sha256": visual_contract.canonical_plan_sha256(decision["reference_plan"]),
            "approved_slot_ids": ["REF-01"],
        }
        authorization = visual_contract.build_generation_authorization(
            decision, scope_approval,
            authorization_id="vga-001", issued_at="2026-08-20T10:01:00+10:00",
        )
        stored_plan = copy.deepcopy(decision["reference_plan"])
        stored_plan["approval"] = scope_approval
        manifest["visual_decisions"] = [decision]
        manifest["visual_scope_approvals"] = [scope_approval]
        manifest["visual_generation_authorizations"] = [authorization]
        manifest["reference_plans"] = [stored_plan]
        return decision, scope_approval

    def refresh_initial_source_bindings(self, manifest: dict[str, object]) -> None:
        decision = manifest["visual_decisions"][0]
        approval = manifest["visual_scope_approvals"][0]
        approval["decision_sha256"] = visual_contract.canonical_sha256(decision)
        approval["plan_sha256"] = visual_contract.canonical_plan_sha256(decision["reference_plan"])
        manifest["reference_plans"][0]["approval"] = approval

    def candidate(self) -> dict[str, object]:
        manifest = EVIDENCE_RUN._manifest_template(
            builder_id="builder", dimension="2d", procedural_mode="none"
        )
        scope_record = self.artifact(
            "scope-approval-artifact",
            "review_record",
            "review_record",
            "docs/visual-contract/vc-001/scope-approval.txt",
            b"scope approved",
        )
        target_record = self.artifact(
            "target-approval-artifact",
            "review_record",
            "review_record",
            "docs/visual-contract/vc-001/target-approval.txt",
            b"targets approved",
        )
        target = self.artifact(
            "target-artifact-01",
            "target_gameplay_image",
            "imagegen_target",
            "docs/visual-contract/vc-001/targets/target-01.png",
            b"target-01",
            target_id="TARGET-01",
            reference_slot_id="REF-01",
            generated_at="2026-08-20T10:05:00+10:00",
            coverage=["exploration/default"],
            authorization_id="vga-001",
        )
        manifest["artifacts"] = [scope_record, target, target_record]
        self.initial_sources(manifest)
        initial_version = {
            "contract_id": "vc-001",
            "base_contract_id": None,
            "plan_id": "vrp-001",
            "plan_revision": 1,
            "targets": [
                {
                    "reference_slot_id": "REF-01",
                    "target_id": "TARGET-01",
                    "artifact_id": "target-artifact-01",
                    "sha256": target["sha256"],
                    "path": target["path"],
                }
            ],
            "approval": None,
        }
        initial_version["approval"] = target_approval(
            recorded_at="2026-08-20T10:10:00+10:00",
            binding_sha256=visual_contract.canonical_sha256(
                {
                    key: value
                    for key, value in initial_version.items()
                    if key != "approval"
                }
            ),
            approval_artifact_id="target-approval-artifact",
        )
        manifest["visual_contract_versions"] = [initial_version]
        manifest["active_visual_contract_id"] = "vc-001"
        return EVIDENCE_RUN._validate_schema(manifest)

    def state(self, manifest: dict[str, object]):
        artifact_index, artifact_errors = EVIDENCE_RUN._artifact_index(
            self.root, manifest["artifacts"]
        )
        self.assertEqual(artifact_errors, [])
        return EVIDENCE_RUN._active_visual_contract_state(manifest, artifact_index)

    def rejected_attempt_candidate(self) -> dict[str, object]:
        manifest = self.candidate()
        rejected = manifest["artifacts"][1]
        rejected["kind"] = "rejected_target_image"
        rejected.update(
            {
                "plan_id": "vrp-001",
                "plan_revision": 1,
                "rejected_at": "2026-08-20T10:06:00+10:00",
                "rejection_artifact_id": "rejection-artifact-01",
                "rejection_reviewer_id": "visual-user",
            }
        )
        rejection_record = self.artifact(
            "rejection-artifact-01",
            "review_record",
            "review_record",
            "docs/visual-contract/vc-001/rejected/target-01-rejection.txt",
            b"target-01 rejected with one corrected retry authorized",
        )
        replacement = self.artifact(
            "target-artifact-02",
            "target_gameplay_image",
            "imagegen_target",
            "docs/visual-contract/vc-001/targets/target-02.png",
            b"target-02",
            target_id="TARGET-02",
            reference_slot_id="REF-01",
            generated_at="2026-08-20T10:07:00+10:00",
            coverage=["exploration/default"],
            authorization_id="vga-002",
        )
        correction = {
            "schema_version": "visual-correction-approval/v1",
            "approval_artifact_id": "correction-approval-artifact-01",
            "reviewer_id": "visual-user",
            "decision": "approved",
            "recorded_at": "2026-08-20T10:06:30+10:00",
            "plan_id": "vrp-001",
            "plan_revision": 1,
            "reference_slot_id": "REF-01",
            "rejected_target_id": "TARGET-01",
            "rejected_target_sha256": rejected["sha256"],
            "correction_direction": "Increase readability of the interaction cue.",
        }
        decision = manifest["visual_decisions"][0]
        rejected_input = {
            key: rejected[key] for key in visual_contract.REJECTED_AUTH_INPUT_FIELDS
        }
        correction_authorization = visual_contract.build_generation_authorization(
            decision, manifest["visual_scope_approvals"][0],
            authorization_id="vga-002", issued_at="2026-08-20T10:06:45+10:00",
            rejected_target=rejected_input, correction=correction,
        )
        manifest["visual_correction_approvals"] = [correction]
        manifest["visual_generation_authorizations"].append(correction_authorization)
        manifest["artifacts"].extend([rejection_record, replacement])
        target = manifest["visual_contract_versions"][0]["targets"][0]
        target.update(
            {
                "target_id": "TARGET-02",
                "artifact_id": "target-artifact-02",
                "sha256": replacement["sha256"],
                "path": replacement["path"],
            }
        )
        version = manifest["visual_contract_versions"][0]
        version["approval"]["binding_sha256"] = visual_contract.canonical_sha256(
            {key: value for key, value in version.items() if key != "approval"}
        )
        return manifest

    def add_delta(
        self,
        manifest: dict[str, object],
        *,
        change_kind: str,
        supersedes_target_id: str | None,
    ) -> dict[str, object]:
        scope = self.artifact(
            "scope-approval-artifact-02",
            "review_record",
            "review_record",
            "docs/visual-contract/vc-002/scope-approval.txt",
            b"delta scope approved",
        )
        target_review = self.artifact(
            "target-approval-artifact-02",
            "review_record",
            "review_record",
            "docs/visual-contract/vc-002/target-approval.txt",
            b"delta targets approved",
        )
        target = self.artifact(
            "target-artifact-02",
            "target_gameplay_image",
            "imagegen_target",
            "docs/visual-contract/vc-002/targets/target-02.png",
            b"target-02",
            target_id="TARGET-02",
            reference_slot_id="REF-02",
            generated_at="2026-08-20T11:05:00+10:00",
            coverage=["boss escalation"],
            plan_id="vrp-002",
            plan_revision=1,
            authorization_id="vga-003",
        )
        delta_plan = {
            "plan_id": "vrp-002",
            "revision": 1,
            "kind": "delta",
            "base_contract_id": "vc-001",
            "rows": [
                slot(
                    "REF-02",
                    change_kind=change_kind,
                    supersedes_target_id=supersedes_target_id,
                )
            ],
            "approval": None,
        }
        delta_plan["rows"][0]["coverage"] = ["boss escalation"]
        delta_decision = {
            "schema_version": "visual-decision/v2",
            "decision_id": "00000000-0000-4000-8000-000000000012",
            "builder_id": "builder",
            "created_at": "2026-08-20T10:30:00+10:00",
            "decision_kind": "delta_scope",
            "state": "VISUAL_DELTA_PENDING",
            "generation_status": "not_started",
            "change_scope": "local",
            "reference_plan": copy.deepcopy(delta_plan),
            "blocked_work": ["boss escalation"],
            "continuing_work": ["core-loop presentation"],
            "preserved_bindings": [],
            "affected_targets": [{
                "target_id": (
                    supersedes_target_id
                    if change_kind == "replace"
                    else "TARGET-02"
                ),
                "dependent_work": ["boss escalation"],
                "change_kind": change_kind,
            }],
            "target_approval_scope": "complete_delta_batch_only",
            "user_interface": {
                "language": "en",
                "scope_question": (
                    "Do you approve this exact image set for generation?"
                ),
                "target_question": (
                    "Do you approve this exact displayed image set?"
                ),
            },
        }
        delta_scope_approval = {
            "schema_version": "visual-scope-approval/v1",
            "approval_artifact_id": "scope-approval-artifact-02",
            "decision_id": delta_decision["decision_id"],
            "reviewer_id": "visual-user",
            "decision": "approved",
            "recorded_at": "2026-08-20T11:00:00+10:00",
            "decision_sha256": visual_contract.canonical_sha256(delta_decision),
            "plan_sha256": visual_contract.canonical_plan_sha256(delta_decision["reference_plan"]),
            "approved_slot_ids": ["REF-02"],
        }
        delta_authorization = visual_contract.build_generation_authorization(
            delta_decision, delta_scope_approval,
            authorization_id="vga-003", issued_at="2026-08-20T11:01:00+10:00",
        )
        delta_version = {
            "contract_id": "vc-002",
            "base_contract_id": "vc-001",
            "plan_id": "vrp-002",
            "plan_revision": 1,
            "targets": [
                {
                    "reference_slot_id": "REF-02",
                    "target_id": "TARGET-02",
                    "artifact_id": "target-artifact-02",
                    "sha256": target["sha256"],
                    "path": target["path"],
                }
            ],
            "approval": None,
        }
        delta_plan["approval"] = delta_scope_approval
        delta_version["approval"] = target_approval(
            recorded_at="2026-08-20T11:10:00+10:00",
            binding_sha256=visual_contract.canonical_sha256(
                {
                    key: value
                    for key, value in delta_version.items()
                    if key != "approval"
                }
            ),
            approval_artifact_id="target-approval-artifact-02",
        )
        manifest["artifacts"].extend([scope, target, target_review])
        manifest["visual_decisions"].append(delta_decision)
        manifest["visual_scope_approvals"].append(delta_scope_approval)
        manifest["visual_generation_authorizations"].append(delta_authorization)
        manifest["reference_plans"].append(delta_plan)
        manifest["visual_contract_versions"].append(delta_version)
        manifest["active_visual_contract_id"] = "vc-002"
        return EVIDENCE_RUN._validate_schema(manifest)

    def test_valid_initial_contract_returns_one_active_target(self) -> None:
        active, errors, reviewer = self.state(self.candidate())
        self.assertEqual(errors, [])
        self.assertEqual(set(active), {"TARGET-01"})
        self.assertEqual(reviewer, "visual-user")

    def test_generation_before_scope_approval_fails(self) -> None:
        manifest = self.candidate()
        manifest["artifacts"][1]["generated_at"] = "2026-08-20T09:59:00+10:00"
        _, errors, _ = self.state(manifest)
        self.assertIn("target TARGET-01 was generated before scope approval", errors)

    def test_target_approval_before_generation_fails(self) -> None:
        manifest = self.candidate()
        manifest["visual_contract_versions"][0]["approval"]["recorded_at"] = (
            "2026-08-20T10:04:00+10:00"
        )
        _, errors, _ = self.state(manifest)
        self.assertIn("target TARGET-01 was generated after target approval", errors)

    def test_duplicate_target_slot_fails(self) -> None:
        manifest = self.candidate()
        duplicate = dict(manifest["visual_contract_versions"][0]["targets"][0])
        duplicate["target_id"] = "TARGET-02"
        manifest["visual_contract_versions"][0]["targets"].append(duplicate)
        _, errors, _ = self.state(EVIDENCE_RUN._validate_schema(manifest))
        self.assertIn("visual target slot ids are duplicate", errors)

    def test_missing_target_for_approved_slot_fails(self) -> None:
        manifest = self.candidate()
        manifest["reference_plans"][0]["rows"].append(slot("REF-02"))
        manifest["visual_decisions"][0]["reference_plan"]["rows"].append(slot("REF-02"))
        manifest["visual_scope_approvals"][0]["approved_slot_ids"].append("REF-02")
        self.refresh_initial_source_bindings(manifest)
        _, errors, _ = self.state(EVIDENCE_RUN._validate_schema(manifest))
        self.assertIn(
            "visual targets do not exactly cover approved reference slots",
            errors,
        )

    def test_scope_approval_binding_drift_fails(self) -> None:
        manifest = self.candidate()
        manifest["reference_plans"][0]["rows"][0]["subject"] = "changed after approval"
        with self.assertRaisesRegex(EVIDENCE_RUN.SchemaError, "decision reference plan differs"):
            EVIDENCE_RUN._validate_schema(manifest)

    def test_target_hash_or_path_binding_drift_fails(self) -> None:
        for field, value in (
            ("sha256", "f" * 64),
            ("path", "docs/visual-contract/vc-001/targets/moved.png"),
        ):
            with self.subTest(field=field):
                manifest = self.candidate()
                manifest["visual_contract_versions"][0]["targets"][0][field] = value
                _, errors, _ = self.state(EVIDENCE_RUN._validate_schema(manifest))
                self.assertIn("target TARGET-01 mapping or bytes drifted", errors)
                self.assertIn("target approval binding drifted", errors)

    def test_target_coverage_drift_fails(self) -> None:
        manifest = self.candidate()
        manifest["artifacts"][1]["coverage"] = ["different obligation"]
        _, errors, _ = self.state(manifest)
        self.assertIn("target TARGET-01 mapping or bytes drifted", errors)

    def test_unapproved_generated_target_fails(self) -> None:
        manifest = self.candidate()
        manifest["artifacts"].append(
            self.artifact(
                "orphan-target",
                "target_gameplay_image",
                "imagegen_target",
                "docs/visual-contract/vc-001/targets/orphan.png",
                b"orphan",
                target_id="TARGET-X",
                reference_slot_id="REF-X",
                generated_at="2026-08-20T10:06:00+10:00",
                coverage=["unapproved"],
                authorization_id="vga-orphan",
            )
        )
        _, errors, _ = self.state(EVIDENCE_RUN._validate_schema(manifest))
        self.assertIn(
            "generated target artifact orphan-target is outside an approved plan",
            errors,
        )

    def test_rejected_attempt_and_fresh_candidate_remain_valid(self) -> None:
        manifest = EVIDENCE_RUN._validate_schema(self.rejected_attempt_candidate())
        active, errors, _ = self.state(manifest)
        self.assertEqual(errors, [])
        self.assertEqual(set(active), {"TARGET-02"})
        rejected = next(
            row for row in manifest["artifacts"] if row["id"] == "target-artifact-01"
        )
        replacement = next(
            row for row in manifest["artifacts"] if row["id"] == "target-artifact-02"
        )
        self.assertEqual(rejected["kind"], "rejected_target_image")
        self.assertTrue((self.root / rejected["path"]).is_file())
        self.assertTrue((self.root / replacement["path"]).is_file())

    def test_replacement_generation_requires_prior_rejection_authorization(self) -> None:
        manifest = self.rejected_attempt_candidate()
        replacement = next(
            row
            for row in manifest["artifacts"]
            if row["id"] == "target-artifact-02"
        )
        replacement["generated_at"] = "2026-08-20T10:05:30+10:00"
        manifest = EVIDENCE_RUN._validate_schema(manifest)
        _, errors, _ = self.state(manifest)
        self.assertIn(
            "target TARGET-02 was generated before prior rejection authorization",
            errors,
        )

    def test_rejected_attempt_requires_authorization_and_time_order(self) -> None:
        missing = self.rejected_attempt_candidate()
        rejected = next(
            row for row in missing["artifacts"] if row["id"] == "target-artifact-01"
        )
        del rejected["rejection_artifact_id"]
        with self.assertRaisesRegex(
            EVIDENCE_RUN.SchemaError, "rejected target fields differ"
        ):
            EVIDENCE_RUN._validate_schema(missing)

        inverted = self.rejected_attempt_candidate()
        rejected = next(
            row for row in inverted["artifacts"] if row["id"] == "target-artifact-01"
        )
        rejected["rejected_at"] = rejected["generated_at"]
        with self.assertRaisesRegex(
            EVIDENCE_RUN.SchemaError, "rejected before it was generated"
        ):
            EVIDENCE_RUN._validate_schema(inverted)

        naive_time = self.rejected_attempt_candidate()
        rejected = next(
            row
            for row in naive_time["artifacts"]
            if row["id"] == "target-artifact-01"
        )
        rejected["rejected_at"] = "2026-08-20T10:06:00"
        with self.assertRaisesRegex(
            EVIDENCE_RUN.SchemaError, "rejected_at is not a timezone-aware"
        ):
            EVIDENCE_RUN._validate_schema(naive_time)

        bad_revision = self.rejected_attempt_candidate()
        rejected = next(
            row
            for row in bad_revision["artifacts"]
            if row["id"] == "target-artifact-01"
        )
        rejected["plan_revision"] = True
        with self.assertRaisesRegex(
            EVIDENCE_RUN.SchemaError, "plan_revision must be a positive integer"
        ):
            EVIDENCE_RUN._validate_schema(bad_revision)

        before_scope = EVIDENCE_RUN._validate_schema(
            self.rejected_attempt_candidate()
        )
        rejected = next(
            row
            for row in before_scope["artifacts"]
            if row["id"] == "target-artifact-01"
        )
        rejected["generated_at"] = "2026-08-20T09:59:00+10:00"
        _, errors, _ = self.state(before_scope)
        self.assertIn(
            "rejected target TARGET-01 was generated before scope approval",
            errors,
        )

        missing_plan = self.rejected_attempt_candidate()
        rejected = next(
            row
            for row in missing_plan["artifacts"]
            if row["id"] == "target-artifact-01"
        )
        rejected["plan_revision"] = 2
        missing_plan = EVIDENCE_RUN._validate_schema(missing_plan)
        _, errors, _ = self.state(missing_plan)
        self.assertIn("rejected target TARGET-01 plan revision is missing", errors)

        binding_drift = EVIDENCE_RUN._validate_schema(
            self.rejected_attempt_candidate()
        )
        binding_drift["reference_plans"][0]["approval"]["plan_sha256"] = "0" * 64
        _, errors, _ = self.state(binding_drift)
        self.assertIn(
            "rejected target TARGET-01 scope approval binding drifted",
            errors,
        )

    def test_rejected_attempt_requires_review_record_and_non_builder(self) -> None:
        missing = EVIDENCE_RUN._validate_schema(self.rejected_attempt_candidate())
        missing["artifacts"] = [
            row for row in missing["artifacts"] if row["id"] != "rejection-artifact-01"
        ]
        _, errors, _ = self.state(missing)
        self.assertIn("rejected target TARGET-01 rejection record is missing", errors)

        wrong_kind = EVIDENCE_RUN._validate_schema(self.rejected_attempt_candidate())
        record = next(
            row
            for row in wrong_kind["artifacts"]
            if row["id"] == "rejection-artifact-01"
        )
        record["kind"] = "content_analysis"
        _, errors, _ = self.state(wrong_kind)
        self.assertIn("rejected target TARGET-01 rejection record is missing", errors)

        builder = EVIDENCE_RUN._validate_schema(self.rejected_attempt_candidate())
        rejected = next(
            row for row in builder["artifacts"] if row["id"] == "target-artifact-01"
        )
        rejected["rejection_reviewer_id"] = "builder"
        _, errors, _ = self.state(builder)
        self.assertIn("rejected target TARGET-01 reviewer is the builder", errors)

    def test_rejected_attempt_cannot_be_a_contract_target(self) -> None:
        manifest = EVIDENCE_RUN._validate_schema(self.rejected_attempt_candidate())
        rejected = next(
            row for row in manifest["artifacts"] if row["id"] == "target-artifact-01"
        )
        target = manifest["visual_contract_versions"][0]["targets"][0]
        target.update(
            {
                "target_id": rejected["target_id"],
                "artifact_id": rejected["id"],
                "sha256": rejected["sha256"],
                "path": rejected["path"],
            }
        )
        version = manifest["visual_contract_versions"][0]
        version["approval"]["binding_sha256"] = visual_contract.canonical_sha256(
            {key: value for key, value in version.items() if key != "approval"}
        )
        _, errors, _ = self.state(manifest)
        self.assertIn(
            "rejected target artifact target-artifact-01 is referenced by a visual contract",
            errors,
        )

    def test_rejected_target_id_is_permanently_reserved(self) -> None:
        approved_reuse = EVIDENCE_RUN._validate_schema(
            self.rejected_attempt_candidate()
        )
        replacement = next(
            row
            for row in approved_reuse["artifacts"]
            if row["id"] == "target-artifact-02"
        )
        replacement["target_id"] = "TARGET-01"
        target = approved_reuse["visual_contract_versions"][0]["targets"][0]
        target["target_id"] = "TARGET-01"
        version = approved_reuse["visual_contract_versions"][0]
        version["approval"]["binding_sha256"] = visual_contract.canonical_sha256(
            {key: value for key, value in version.items() if key != "approval"}
        )
        _, errors, _ = self.state(approved_reuse)
        self.assertIn("target id TARGET-01 is reused in visual contract history", errors)

        rejected_reuse = self.rejected_attempt_candidate()
        duplicate = self.artifact(
            "target-artifact-03",
            "rejected_target_image",
            "imagegen_target",
            "docs/visual-contract/vc-001/rejected/target-03.png",
            b"target-03",
            target_id="TARGET-01",
            reference_slot_id="REF-01",
            generated_at="2026-08-20T10:07:30+10:00",
            coverage=["exploration/default"],
            plan_id="vrp-001",
            plan_revision=1,
            rejected_at="2026-08-20T10:08:00+10:00",
            rejection_artifact_id="rejection-artifact-01",
            rejection_reviewer_id="visual-user",
            authorization_id="vga-004",
        )
        rejected_reuse["artifacts"].append(duplicate)
        rejected_reuse = EVIDENCE_RUN._validate_schema(rejected_reuse)
        _, errors, _ = self.state(rejected_reuse)
        self.assertIn("rejected target id TARGET-01 is reused", errors)

    def test_additive_delta_preserves_base_target(self) -> None:
        manifest = self.add_delta(
            self.candidate(), change_kind="add", supersedes_target_id=None
        )
        active, errors, _ = self.state(manifest)
        self.assertEqual(errors, [])
        self.assertEqual(set(active), {"TARGET-01", "TARGET-02"})

    def test_replacement_supersedes_only_named_target(self) -> None:
        manifest = self.add_delta(
            self.candidate(),
            change_kind="replace",
            supersedes_target_id="TARGET-01",
        )
        active, errors, _ = self.state(manifest)
        self.assertEqual(errors, [])
        self.assertEqual(set(active), {"TARGET-02"})

    def test_delta_cycle_fails(self) -> None:
        manifest = self.add_delta(
            self.candidate(), change_kind="add", supersedes_target_id=None
        )
        manifest["visual_contract_versions"][1]["base_contract_id"] = "vc-002"
        _, errors, _ = self.state(manifest)
        self.assertIn("visual contract ancestry contains a cycle", errors)

    def test_approved_branch_outside_active_chain_fails(self) -> None:
        manifest = self.add_delta(
            self.candidate(), change_kind="add", supersedes_target_id=None
        )
        branch = dict(manifest["visual_contract_versions"][1])
        branch["contract_id"] = "vc-003"
        manifest["visual_contract_versions"].append(branch)
        _, errors, _ = self.state(EVIDENCE_RUN._validate_schema(manifest))
        self.assertIn("approved visual contract history branches or is stale", errors)

    def test_replacement_of_unknown_target_fails(self) -> None:
        manifest = self.add_delta(
            self.candidate(),
            change_kind="replace",
            supersedes_target_id="TARGET-404",
        )
        _, errors, _ = self.state(manifest)
        self.assertIn(
            "replacement target TARGET-404 is not active",
            errors,
        )

    def test_carried_base_binding_drift_fails(self) -> None:
        manifest = self.add_delta(
            self.candidate(), change_kind="add", supersedes_target_id=None
        )
        manifest["visual_contract_versions"][0]["targets"][0]["sha256"] = "f" * 64
        _, errors, _ = self.state(EVIDENCE_RUN._validate_schema(manifest))
        self.assertIn("target TARGET-01 mapping or bytes drifted", errors)

    def test_target_id_reuse_across_versions_fails(self) -> None:
        manifest = self.add_delta(
            self.candidate(),
            change_kind="replace",
            supersedes_target_id="TARGET-01",
        )
        manifest["visual_contract_versions"][1]["targets"][0]["target_id"] = (
            "TARGET-01"
        )
        manifest["artifacts"][4]["target_id"] = "TARGET-01"
        _, errors, _ = self.state(EVIDENCE_RUN._validate_schema(manifest))
        self.assertIn("target id TARGET-01 is reused in visual contract history", errors)


class GenerationAuthorizationChainTests(unittest.TestCase):
    """The authorization record, not incidental plan shape, licenses each result."""

    setUp = InitialVisualContractTests.setUp
    tearDown = InitialVisualContractTests.tearDown
    artifact = InitialVisualContractTests.artifact
    initial_sources = InitialVisualContractTests.initial_sources
    refresh_initial_source_bindings = InitialVisualContractTests.refresh_initial_source_bindings
    candidate = InitialVisualContractTests.candidate
    state = InitialVisualContractTests.state
    rejected_attempt_candidate = InitialVisualContractTests.rejected_attempt_candidate
    add_delta = InitialVisualContractTests.add_delta

    def chain_errors(self, manifest: dict[str, object]) -> list[str]:
        manifest = EVIDENCE_RUN._validate_schema(manifest)
        index, index_errors = EVIDENCE_RUN._artifact_index(self.root, manifest["artifacts"])
        return index_errors + EVIDENCE_RUN._generation_authorization_errors(manifest, index)

    def assert_clean(self, manifest: dict[str, object]) -> None:
        self.assertEqual(self.chain_errors(manifest), [])

    def assert_chain_error(self, fragment: str, manifest: dict[str, object]) -> None:
        self.assertTrue(any(fragment in error for error in self.chain_errors(manifest)))

    def test_valid_initial_authorization_chain_passes(self) -> None:
        self.assert_clean(self.candidate())

    def test_unknown_artifact_authorization_fails(self) -> None:
        manifest = self.candidate(); self.assert_clean(manifest)
        manifest["artifacts"][1]["authorization_id"] = "vga-missing"
        self.assert_chain_error("authorization does not resolve", manifest)

    def test_artifact_slot_outside_authorization_fails(self) -> None:
        manifest = self.candidate(); self.assert_clean(manifest)
        manifest["artifacts"][1]["reference_slot_id"] = "REF-X"
        self.assert_chain_error("slot is outside its authorization", manifest)

    def test_authorization_plan_binding_drift_fails(self) -> None:
        manifest = self.candidate(); self.assert_clean(manifest)
        manifest["visual_generation_authorizations"][0]["plan_sha256"] = "f" * 64
        self.assert_chain_error("authorization plan binding drifted", manifest)

    def test_full_batch_authorization_cannot_omit_approved_slot(self) -> None:
        manifest = self.candidate(); self.assert_clean(manifest)
        manifest["reference_plans"][0]["rows"].append(slot("REF-02"))
        manifest["visual_decisions"][0]["reference_plan"]["rows"].append(slot("REF-02"))
        manifest["visual_scope_approvals"][0]["approved_slot_ids"].append("REF-02")
        self.refresh_initial_source_bindings(manifest)
        self.assert_chain_error("authorization slot set differs from approved plan", manifest)

    def test_one_authorization_budget_cannot_produce_two_results(self) -> None:
        manifest = self.candidate(); self.assert_clean(manifest)
        duplicate = copy.deepcopy(manifest["artifacts"][1]); duplicate.update({"id": "target-artifact-02", "target_id": "TARGET-02", "path": "docs/visual-contract/vc-001/targets/target-02.png"})
        (self.root / duplicate["path"]).write_bytes(b"target-02")
        duplicate["sha256"] = hashlib.sha256(b"target-02").hexdigest(); manifest["artifacts"].append(duplicate)
        self.assert_chain_error("authorization slot result budget exceeded", manifest)

    def test_generation_must_follow_authorization(self) -> None:
        manifest = self.candidate(); self.assert_clean(manifest)
        manifest["artifacts"][1]["generated_at"] = "2026-08-20T10:00:30+10:00"
        self.assert_chain_error("generated before authorization", manifest)

    def test_rejected_attempt_consumes_authorization(self) -> None:
        manifest = self.rejected_attempt_candidate(); self.assert_clean(manifest)
        replacement = next(row for row in manifest["artifacts"] if row["id"] == "target-artifact-02")
        replacement["authorization_id"] = "vga-001"
        self.assert_chain_error("authorization slot result budget exceeded", manifest)

    def test_retry_requires_correction_authorization(self) -> None:
        manifest = self.rejected_attempt_candidate(); self.assert_clean(manifest)
        manifest["visual_correction_approvals"] = []
        manifest["visual_generation_authorizations"] = manifest["visual_generation_authorizations"][:1]
        self.assert_chain_error("replacement target lacks correction authorization", manifest)

    def test_correction_binds_exact_rejected_target(self) -> None:
        manifest = self.rejected_attempt_candidate(); self.assert_clean(manifest)
        manifest["visual_correction_approvals"][0]["rejected_target_sha256"] = "f" * 64
        self.assert_chain_error("correction target binding drifted", manifest)

    def test_correction_authorization_must_follow_rejection(self) -> None:
        manifest = self.rejected_attempt_candidate(); self.assert_clean(manifest)
        manifest["visual_generation_authorizations"][1]["issued_at"] = "2026-08-20T10:05:30+10:00"
        self.assert_chain_error("correction authorization precedes rejection", manifest)

    def test_valid_rejection_correction_replacement_chain_passes(self) -> None:
        self.assert_clean(self.rejected_attempt_candidate())

    def test_orphan_authorization_fails_complete_evidence(self) -> None:
        manifest = self.candidate(); self.assert_clean(manifest)
        orphan = copy.deepcopy(manifest["visual_generation_authorizations"][0]); orphan["authorization_id"] = "vga-orphan"; manifest["visual_generation_authorizations"].append(orphan)
        self.assert_chain_error("authorization has no generated result", manifest)

    def test_visual_contract_target_must_be_registered_artifact(self) -> None:
        manifest = self.candidate(); self.assert_clean(manifest)
        manifest["visual_contract_versions"][0]["targets"][0]["artifact_id"] = "missing-artifact"
        _, errors, _ = self.state(manifest)
        self.assertTrue(any("target artifact is missing" in error for error in errors))

    def test_target_approval_must_follow_complete_authorized_batch(self) -> None:
        manifest = self.candidate(); self.assert_clean(manifest)
        manifest["visual_contract_versions"][0]["approval"]["recorded_at"] = "2026-08-20T10:04:00+10:00"
        _, errors, _ = self.state(manifest)
        self.assertTrue(any("target approval precedes complete authorized batch" in error for error in errors))

    def test_delta_authorization_preserves_exact_supersession_set(self) -> None:
        manifest = self.add_delta(self.candidate(), change_kind="replace", supersedes_target_id="TARGET-01"); self.assert_clean(manifest)
        manifest["visual_generation_authorizations"][-1]["supersedes_target_ids"] = []
        self.assert_chain_error("authorization supersession set differs", manifest)

    def test_replacement_after_rejection_requires_correction_authorization(self) -> None:
        manifest = self.rejected_attempt_candidate(); self.assert_clean(manifest)
        decision = manifest["visual_decisions"][0]
        scope = manifest["visual_scope_approvals"][0]
        replacement = next(row for row in manifest["artifacts"] if row["id"] == "target-artifact-02")
        replacement["authorization_id"] = "vga-003"
        manifest["visual_generation_authorizations"][1:] = [
            visual_contract.build_generation_authorization(
                decision, scope, authorization_id="vga-003",
                issued_at="2026-08-20T10:06:45+10:00",
            )
        ]
        manifest["visual_correction_approvals"] = []
        self.assert_chain_error("replacement target lacks correction authorization", manifest)

    def test_correction_authorization_requires_exact_rejected_slot(self) -> None:
        manifest = self.rejected_attempt_candidate(); self.assert_clean(manifest)
        authorization = manifest["visual_generation_authorizations"][1]
        authorization["authorized_slots"].append({"reference_slot_id": "REF-X", "result_budget": 1})
        self.assert_chain_error("correction authorization slot set differs", manifest)

    def test_target_artifact_requires_explicit_plan_binding(self) -> None:
        for field in ("plan_id", "plan_revision"):
            with self.subTest(field=field):
                manifest = self.candidate(); self.assert_clean(manifest)
                manifest["artifacts"][1].update({"plan_id": "vrp-001", "plan_revision": 1})
                self.assert_clean(manifest)
                del manifest["artifacts"][1][field]
                with self.assertRaisesRegex(EVIDENCE_RUN.SchemaError, "target image fields"):
                    EVIDENCE_RUN._validate_schema(manifest)


if __name__ == "__main__":
    unittest.main()
