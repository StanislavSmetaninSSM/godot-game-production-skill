import json
import sys
import tempfile
import unittest
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT_DIR = ROOT / "godot-game-production" / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))

import visual_contract  # noqa: E402
import visual_gate  # noqa: E402


def slot(slot_id: str = "REF-01") -> dict[str, object]:
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
            "characters": "player and one hazard",
            "ui": "gameplay HUD",
            "vfx": "interaction cue",
        },
        "motion_cue": "player movement direction",
        "sound_cue": "interaction confirmation",
        "dependent_work": ["core-loop presentation"],
        "rationale": "No approved target resolves this composition.",
        "image_count": 1,
        "change_kind": "initial",
        "supersedes_target_id": None,
    }


def initial_decision() -> dict[str, object]:
    return {
        "schema_version": "visual-decision/v1",
        "decision_id": str(uuid.UUID("11111111-1111-1111-1111-111111111111")),
        "builder_id": "codex-builder",
        "created_at": "2020-01-01T10:00:00+10:00",
        "decision_kind": "initial_scope",
        "state": "REFERENCE_SCOPE_PENDING",
        "generation_status": "not_started",
        "reference_plan": {
            "plan_id": "vrp-001",
            "revision": 1,
            "kind": "initial",
            "base_contract_id": None,
            "rows": [slot()],
            "approval": None,
        },
        "scope_question": visual_contract.CANONICAL_SCOPE_QUESTION,
    }


def scope_approval(decision: dict[str, object]) -> dict[str, object]:
    plan = decision["reference_plan"]
    return {
        "schema_version": "visual-scope-approval/v1",
        "approval_artifact_id": "scope-approval-01",
        "decision_id": decision["decision_id"],
        "reviewer_id": "visual-user",
        "decision": "approved",
        "recorded_at": "2020-01-01T10:01:00+10:00",
        "decision_sha256": visual_contract.canonical_sha256(decision),
        "plan_sha256": visual_contract.canonical_plan_sha256(plan),
        "approved_slot_ids": [
            row["reference_slot_id"] for row in plan["rows"]
        ],
    }


def rejected_target() -> dict[str, object]:
    return {
        "target_id": "TARGET-REJECTED-01",
        "reference_slot_id": "REF-01",
        "sha256": "a" * 64,
        "plan_id": "vrp-001",
        "plan_revision": 1,
        "authorization_id": "vga-initial-01",
        "generated_at": "2020-01-01T10:02:00+10:00",
        "rejected_at": "2020-01-01T10:03:00+10:00",
    }


def correction_approval() -> dict[str, object]:
    rejected = rejected_target()
    return {
        "schema_version": "visual-correction-approval/v1",
        "approval_artifact_id": "correction-approval-01",
        "reviewer_id": "visual-user",
        "decision": "approved",
        "recorded_at": "2020-01-01T10:04:00+10:00",
        "plan_id": "vrp-001",
        "plan_revision": 1,
        "reference_slot_id": "REF-01",
        "rejected_target_id": rejected["target_id"],
        "rejected_target_sha256": rejected["sha256"],
        "correction_direction": "Increase player silhouette contrast.",
    }


class VisualDecisionTests(unittest.TestCase):
    def test_array_discriminators_fail_closed_as_schema_errors(self) -> None:
        cases: list[tuple[str, dict[str, object]]] = []

        decision_kind = initial_decision()
        decision_kind["decision_kind"] = []
        cases.append(("decision_kind", decision_kind))

        plan_kind = initial_decision()
        plan_kind["reference_plan"]["kind"] = []
        cases.append(("reference_plan.kind", plan_kind))

        target_kind = initial_decision()
        target_kind["reference_plan"]["rows"][0]["target_kind"] = []
        cases.append(("row.target_kind", target_kind))

        row_change_kind = initial_decision()
        row_change_kind["reference_plan"]["rows"][0]["change_kind"] = []
        cases.append(("row.change_kind", row_change_kind))

        delta_change_scope = initial_decision()
        delta_change_scope.update({
            "decision_kind": "delta_scope",
            "state": "VISUAL_DELTA_PENDING",
            "change_scope": [],
            "blocked_work": ["boss presentation"],
            "continuing_work": ["save menu"],
            "preserved_bindings": [],
            "affected_targets": [{
                "target_id": visual_contract.PLACEHOLDER,
                "dependent_work": ["boss presentation"],
                "change_kind": "add",
            }],
            "target_approval_scope": "complete_delta_batch_only",
        })
        delta_change_scope["reference_plan"]["kind"] = "delta"
        delta_change_scope["reference_plan"]["base_contract_id"] = "vc-001"
        delta_change_scope["reference_plan"]["rows"][0]["change_kind"] = "add"
        cases.append(("delta.change_scope", delta_change_scope))

        affected_change_kind = initial_decision()
        affected_change_kind.update({
            "decision_kind": "delta_scope",
            "state": "VISUAL_DELTA_PENDING",
            "change_scope": "local",
            "blocked_work": ["boss presentation"],
            "continuing_work": ["save menu"],
            "preserved_bindings": [],
            "affected_targets": [{
                "target_id": visual_contract.PLACEHOLDER,
                "dependent_work": ["boss presentation"],
                "change_kind": [],
            }],
            "target_approval_scope": "complete_delta_batch_only",
        })
        affected_change_kind["reference_plan"]["kind"] = "delta"
        affected_change_kind["reference_plan"]["base_contract_id"] = "vc-001"
        affected_change_kind["reference_plan"]["rows"][0]["change_kind"] = "add"
        cases.append(("affected_target.change_kind", affected_change_kind))

        for label, decision in cases:
            with self.subTest(label=label):
                with self.assertRaises(
                    (visual_contract.SchemaError, visual_contract.InvariantError)
                ):
                    visual_contract.validate_visual_decision(decision)

    def test_array_discriminator_cli_returns_input_error_without_report(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            decision = initial_decision()
            decision["decision_kind"] = []
            decision_path = root / "decision.json"
            report_path = root / "report.json"
            decision_path.write_text(json.dumps(decision), encoding="utf-8")

            self.assertEqual(
                visual_gate.main([
                    "check-decision",
                    "--decision", str(decision_path),
                    "--report", str(report_path),
                ]),
                3,
            )
            self.assertFalse(report_path.exists())

    def test_valid_initial_decision_is_valid_pending(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            decision_path = root / "decision.json"
            report_path = root / "report.json"
            decision_path.write_text(
                json.dumps(initial_decision()), encoding="utf-8"
            )
            code = visual_gate.main([
                "check-decision",
                "--decision", str(decision_path),
                "--report", str(report_path),
            ])
            self.assertEqual(code, 0)
            report = json.loads(report_path.read_text(encoding="utf-8"))
            self.assertEqual(report["status"], "VALID_PENDING")
            self.assertEqual(
                report["decision_sha256"],
                visual_contract.canonical_sha256(initial_decision()),
            )

    def test_empty_rows_are_rejected(self) -> None:
        decision = initial_decision()
        decision["reference_plan"]["rows"] = []
        with self.assertRaisesRegex(
            visual_contract.InvariantError, "rows are empty"
        ):
            visual_contract.validate_visual_decision(decision)

    def test_image_count_must_equal_integer_one(self) -> None:
        for invalid in (2, True):
            with self.subTest(invalid=invalid):
                decision = initial_decision()
                decision["reference_plan"]["rows"][0]["image_count"] = invalid
                with self.assertRaisesRegex(
                    visual_contract.InvariantError, "image_count"
                ):
                    visual_contract.validate_visual_decision(decision)

    def test_canonical_scope_question_is_exact(self) -> None:
        decision = initial_decision()
        decision["scope_question"] = "Do you approve?"
        with self.assertRaisesRegex(
            visual_contract.InvariantError, "scope question"
        ):
            visual_contract.validate_visual_decision(decision)

    def test_duplicate_json_keys_are_invalid_input(self) -> None:
        with self.assertRaisesRegex(
            visual_contract.SchemaError, "duplicate JSON key: decision_id"
        ):
            visual_contract.loads_json(
                '{"decision_id":"one","decision_id":"two"}'
            )

    def test_placeholder_is_allowed_only_for_missing_pending_value(self) -> None:
        decision = initial_decision()
        decision["reference_plan"]["rows"][0]["subject"] = (
            visual_contract.PLACEHOLDER
        )
        validated = visual_contract.validate_visual_decision(decision)
        self.assertEqual(
            validated["reference_plan"]["rows"][0]["subject"],
            visual_contract.PLACEHOLDER,
        )
        with self.assertRaisesRegex(
            visual_contract.InvariantError, "unresolved placeholder"
        ):
            visual_contract.validate_reference_plan(
                decision["reference_plan"], allow_placeholders=False
            )

    def test_delta_decision_requires_exact_variant_fields(self) -> None:
        decision = initial_decision()
        decision.update({
            "decision_kind": "delta_scope",
            "state": "VISUAL_DELTA_PENDING",
            "change_scope": "local",
            "blocked_work": ["boss presentation"],
            "continuing_work": ["save menu"],
            "preserved_bindings": [],
            "affected_targets": [{
                "target_id": visual_contract.PLACEHOLDER,
                "dependent_work": ["boss presentation"],
                "change_kind": "add",
            }],
            "target_approval_scope": "complete_delta_batch_only",
        })
        decision["reference_plan"]["kind"] = "delta"
        decision["reference_plan"]["base_contract_id"] = "vc-001"
        decision["reference_plan"]["rows"][0]["change_kind"] = "add"
        validated = visual_contract.validate_visual_decision(decision)
        self.assertEqual(validated["change_scope"], "local")
        decision["preserved_bindings"] = [{
            "target_id": "TARGET-01",
            "sha256": "a" * 64,
            "path": "C:\\outside.png",
        }]
        with self.assertRaisesRegex(
            visual_contract.InvariantError, "preserved path is not portable"
        ):
            visual_contract.validate_visual_decision(decision)
        decision["preserved_bindings"] = []
        del decision["affected_targets"]
        with self.assertRaisesRegex(
            visual_contract.SchemaError, "delta decision fields differ"
        ):
            visual_contract.validate_visual_decision(decision)

    def test_reference_not_proof_requires_canonical_gate_list(self) -> None:
        decision = {
            "schema_version": "visual-decision/v1",
            "decision_id": "22222222-2222-2222-2222-222222222222",
            "builder_id": "codex-builder",
            "created_at": "2020-01-01T10:00:00+10:00",
            "decision_kind": "reference_not_proof",
            "state": "UNCHANGED",
            "generation_status": "not_authorized",
            "verdict": "rejected",
            "preserved_evidence": list(
                visual_contract.CANONICAL_PROOF_GATES
            ),
        }
        visual_contract.validate_visual_decision(decision)
        decision["preserved_evidence"].remove("systems/holism")
        with self.assertRaisesRegex(
            visual_contract.InvariantError, "proof gates differ"
        ):
            visual_contract.validate_visual_decision(decision)


class VisualAuthorizationTests(unittest.TestCase):
    def build_full(self) -> dict[str, object]:
        decision = initial_decision()
        return visual_contract.build_generation_authorization(
            decision,
            scope_approval(decision),
            authorization_id="vga-001",
            issued_at="2020-01-01T10:01:30+10:00",
        )

    def test_full_batch_authorizes_exact_approved_slots(self) -> None:
        authorization = self.build_full()
        self.assertEqual(authorization["status"], "AUTHORIZED")
        self.assertEqual(authorization["batch_kind"], "initial")
        self.assertEqual(
            authorization["authorized_slots"],
            [{"reference_slot_id": "REF-01", "result_budget": 1}],
        )
        visual_contract.validate_generation_authorization(authorization)

    def test_authorization_batch_kind_requires_text_before_membership(self) -> None:
        authorization = self.build_full()
        authorization["batch_kind"] = []
        with self.assertRaises(visual_contract.SchemaError):
            visual_contract.validate_generation_authorization(authorization)

    def test_cli_existing_authorization_with_array_batch_kind_returns_input_error(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            decision = initial_decision()
            decision_path = root / "decision.json"
            approval_path = root / "approval.json"
            authorization_path = root / "authorization.json"
            decision_path.write_text(json.dumps(decision), encoding="utf-8")
            approval_path.write_text(
                json.dumps(scope_approval(decision)), encoding="utf-8"
            )
            args = [
                "authorize-generation",
                "--decision", str(decision_path),
                "--approval", str(approval_path),
                "--authorization", str(authorization_path),
            ]
            self.assertEqual(visual_gate.main(args), 0)
            existing = json.loads(authorization_path.read_text(encoding="utf-8"))
            existing["batch_kind"] = []
            authorization_path.write_text(json.dumps(existing), encoding="utf-8")
            self.assertEqual(visual_gate.main(args), 3)

    def test_partial_scope_approval_is_rejected(self) -> None:
        decision = initial_decision()
        decision["reference_plan"]["rows"].append(slot("REF-02"))
        approval = scope_approval(decision)
        approval["approved_slot_ids"] = ["REF-01"]
        with self.assertRaisesRegex(
            visual_contract.InvariantError, "approved slot set differs"
        ):
            visual_contract.build_generation_authorization(
                decision,
                approval,
                authorization_id="vga-001",
                issued_at="2020-01-01T10:01:30+10:00",
            )

    def test_builder_cannot_approve_its_own_decision(self) -> None:
        decision = initial_decision()
        approval = scope_approval(decision)
        approval["reviewer_id"] = decision["builder_id"]
        with self.assertRaisesRegex(
            visual_contract.InvariantError, "reviewer is the builder"
        ):
            visual_contract.build_generation_authorization(
                decision,
                approval,
                authorization_id="vga-001",
                issued_at="2020-01-01T10:01:30+10:00",
            )

    def test_approval_must_follow_decision(self) -> None:
        decision = initial_decision()
        approval = scope_approval(decision)
        approval["recorded_at"] = "2020-01-01T09:59:00+10:00"
        with self.assertRaisesRegex(
            visual_contract.InvariantError, "approval precedes decision"
        ):
            visual_contract.build_generation_authorization(
                decision,
                approval,
                authorization_id="vga-001",
                issued_at="2020-01-01T10:01:30+10:00",
            )

    def test_authorization_rejects_unresolved_placeholder(self) -> None:
        decision = initial_decision()
        decision["reference_plan"]["rows"][0]["subject"] = (
            visual_contract.PLACEHOLDER
        )
        with self.assertRaisesRegex(
            visual_contract.InvariantError, "unresolved placeholder"
        ):
            visual_contract.build_generation_authorization(
                decision,
                scope_approval(decision),
                authorization_id="vga-001",
                issued_at="2020-01-01T10:01:30+10:00",
            )

    def test_correction_authorizes_only_rejected_slot(self) -> None:
        decision = initial_decision()
        authorization = visual_contract.build_generation_authorization(
            decision,
            scope_approval(decision),
            authorization_id="vga-correction-01",
            issued_at="2020-01-01T10:04:30+10:00",
            rejected_target=rejected_target(),
            correction=correction_approval(),
        )
        self.assertEqual(authorization["batch_kind"], "correction")
        self.assertEqual(
            authorization["authorized_slots"],
            [{"reference_slot_id": "REF-01", "result_budget": 1}],
        )
        self.assertEqual(
            authorization["rejected_target_id"], "TARGET-REJECTED-01"
        )

    def test_full_batch_rejects_only_one_correction_input(self) -> None:
        decision = initial_decision()
        with self.assertRaisesRegex(
            visual_contract.SchemaError, "correction inputs must appear together"
        ):
            visual_contract.build_generation_authorization(
                decision,
                scope_approval(decision),
                authorization_id="vga-001",
                issued_at="2020-01-01T10:01:30+10:00",
                rejected_target=rejected_target(),
            )

    def test_cli_is_idempotent_but_never_overwrites_different_binding(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            decision = initial_decision()
            decision_path = root / "decision.json"
            approval_path = root / "approval.json"
            authorization_path = root / "authorization.json"
            decision_path.write_text(json.dumps(decision), encoding="utf-8")
            approval_path.write_text(
                json.dumps(scope_approval(decision)), encoding="utf-8"
            )
            args = [
                "authorize-generation",
                "--decision", str(decision_path),
                "--approval", str(approval_path),
                "--authorization", str(authorization_path),
            ]
            self.assertEqual(visual_gate.main(args), 0)
            first = authorization_path.read_bytes()
            self.assertEqual(visual_gate.main(args), 0)
            self.assertEqual(authorization_path.read_bytes(), first)
            authorization_path.write_text("{}\n", encoding="utf-8")
            self.assertEqual(visual_gate.main(args), 3)

    def test_correction_rejected_target_must_bind_current_approved_plan(self) -> None:
        cases = [
            ("outside slot", "reference_slot_id", "REF-OUTSIDE", "rejected target slot is not approved"),
            ("plan id", "plan_id", "other-plan", "rejected target plan differs"),
            ("plan revision", "plan_revision", 2, "rejected target plan differs"),
            ("boolean plan revision", "plan_revision", True, "rejected target plan revision is invalid"),
        ]
        for label, field, value, message in cases:
            with self.subTest(label=label):
                rejected = rejected_target()
                rejected[field] = value
                with self.assertRaisesRegex(visual_contract.InvariantError, message):
                    visual_contract.build_generation_authorization(
                        initial_decision(),
                        scope_approval(initial_decision()),
                        authorization_id="vga-correction-01",
                        issued_at="2020-01-01T10:04:30+10:00",
                        rejected_target=rejected,
                        correction=correction_approval(),
                    )

    def test_correction_rejected_target_requires_well_formed_bindings(self) -> None:
        cases = [
            ("sha", "sha256", "bad", "rejected target SHA-256 is malformed"),
            ("target id", "target_id", "", "rejected target target_id is empty"),
            ("malformed target id", "target_id", [], "rejected target target_id is empty"),
            ("slot id", "reference_slot_id", "", "rejected target reference_slot_id is empty"),
            ("malformed slot id", "reference_slot_id", [], "rejected target reference_slot_id is empty"),
            ("plan id", "plan_id", "", "rejected target plan_id is empty"),
            ("malformed plan id", "plan_id", [], "rejected target plan_id is empty"),
            ("origin authorization", "authorization_id", "", "rejected target authorization_id is empty"),
            ("malformed origin authorization", "authorization_id", [], "rejected target authorization_id is empty"),
        ]
        for label, field, value, message in cases:
            with self.subTest(label=label):
                rejected = rejected_target()
                rejected[field] = value
                correction = correction_approval()
                correction["reference_slot_id"] = rejected["reference_slot_id"]
                with self.assertRaisesRegex(visual_contract.InvariantError, message):
                    visual_contract.build_generation_authorization(
                        initial_decision(),
                        scope_approval(initial_decision()),
                        authorization_id="vga-correction-01",
                        issued_at="2020-01-01T10:04:30+10:00",
                        rejected_target=rejected,
                        correction=correction,
                    )

    def test_correction_rejected_target_requires_chronological_aware_times(self) -> None:
        cases = [
            ("invalid generated", "generated_at", "not-a-time", "rejected target generated timestamp is invalid"),
            ("unaware generated", "generated_at", "2020-01-01T10:02:00", "rejected target generated timestamp is invalid"),
            ("invalid rejected", "rejected_at", "not-a-time", "rejected target rejected timestamp is invalid"),
            ("unaware rejected", "rejected_at", "2020-01-01T10:03:00", "rejected target rejected timestamp is invalid"),
            ("equal times", "generated_at", "2020-01-01T10:03:00+10:00", "rejected target does not follow generation"),
            ("generated after rejection", "generated_at", "2020-01-01T10:03:01+10:00", "rejected target does not follow generation"),
        ]
        for label, field, value, message in cases:
            with self.subTest(label=label):
                rejected = rejected_target()
                rejected[field] = value
                with self.assertRaisesRegex(visual_contract.InvariantError, message):
                    visual_contract.build_generation_authorization(
                        initial_decision(),
                        scope_approval(initial_decision()),
                        authorization_id="vga-correction-01",
                        issued_at="2020-01-01T10:04:30+10:00",
                        rejected_target=rejected,
                        correction=correction_approval(),
                    )

    def test_correction_requires_fresh_authorization_and_direction(self) -> None:
        with self.assertRaisesRegex(
            visual_contract.InvariantError, "reuses rejected target authorization"
        ):
            visual_contract.build_generation_authorization(
                initial_decision(),
                scope_approval(initial_decision()),
                authorization_id=rejected_target()["authorization_id"],
                issued_at="2020-01-01T10:04:30+10:00",
                rejected_target=rejected_target(),
                correction=correction_approval(),
            )
        correction = correction_approval()
        correction["correction_direction"] = visual_contract.PLACEHOLDER
        with self.assertRaisesRegex(
            visual_contract.InvariantError, "unresolved placeholder"
        ):
            visual_contract.build_generation_authorization(
                initial_decision(),
                scope_approval(initial_decision()),
                authorization_id="vga-correction-01",
                issued_at="2020-01-01T10:04:30+10:00",
                rejected_target=rejected_target(),
                correction=correction,
            )

    def test_cli_rejects_outside_slot_correction_without_output(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            decision = initial_decision()
            approval = scope_approval(decision)
            rejected = rejected_target()
            rejected["reference_slot_id"] = "REF-OUTSIDE"
            correction = correction_approval()
            correction["reference_slot_id"] = "REF-OUTSIDE"
            paths = {
                "decision": root / "decision.json",
                "approval": root / "approval.json",
                "rejected": root / "rejected.json",
                "correction": root / "correction.json",
                "authorization": root / "authorization.json",
            }
            for name, value in {
                "decision": decision,
                "approval": approval,
                "rejected": rejected,
                "correction": correction,
            }.items():
                paths[name].write_text(json.dumps(value), encoding="utf-8")
            self.assertEqual(visual_gate.main([
                "authorize-generation", "--decision", str(paths["decision"]),
                "--approval", str(paths["approval"]),
                "--authorization", str(paths["authorization"]),
                "--rejected-target", str(paths["rejected"]),
                "--correction-approval", str(paths["correction"]),
            ]), 2)
            self.assertFalse(paths["authorization"].exists())
