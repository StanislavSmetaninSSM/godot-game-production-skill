import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "godot-game-production" / "scripts"))

import visual_contract  # noqa: E402


def read(relative_path: str) -> str:
    return (ROOT / relative_path).read_text(encoding="utf-8")


def assert_contains_all(
    case: unittest.TestCase, text: str, required: tuple[str, ...]
) -> None:
    for value in required:
        case.assertIn(value, text, f"missing required contract text: {value}")


class DynamicVisualReferenceContractTests(unittest.TestCase):
    def test_main_skill_writes_validates_and_renders_before_scope_approval(self) -> None:
        text = read("godot-game-production/SKILL.md")
        ordered = (
            "docs/visual-contract/pending/<decision-id>/decision.json",
            "check-decision",
            "VALID_PENDING",
            "present-decision",
            "copy its stdout verbatim into chat",
            "explicit full-set approval",
        )
        assert_contains_all(self, text, ordered)
        self.assertEqual(
            [text.index(value) for value in ordered],
            sorted(text.index(value) for value in ordered),
        )

    def test_main_skill_keeps_machine_decisions_out_of_chat(self) -> None:
        text = read("godot-game-production/SKILL.md")
        required = (
            "one numbered item per row",
            "what the image visibly contains",
            "why production needs it",
            "user's current conversation language",
            "Never paste decision JSON",
            "internal IDs, hashes, schema names, or artifact paths",
        )
        assert_contains_all(self, text, required)
        for banned in (
            "`json` fenced code block",
            "Do you exactly approve the proposed reference slot ID set?",
            "Do you exactly approve the displayed target ID set?",
        ):
            self.assertNotIn(banned, text)

    def test_main_skill_preserves_pending_decision_when_refusing_requests(self) -> None:
        text = read("godot-game-production/SKILL.md")
        required = (
            "premature or scope-invalid request for a pending `initial_scope` or `delta_scope`",
            "same response must continue the file-first gate with the validated localized projection",
            "never refusal-only prose",
            "`reference_not_proof` writes its complete decision to the pending path",
            "renders only its localized stored message",
            "does not ask the scope question",
        )
        assert_contains_all(self, text, required)
        self.assertLess(
            text.index("premature or scope-invalid request for a pending `initial_scope` or `delta_scope`"),
            text.index("After the user's exact full-set approval"),
        )

    def test_main_skill_requires_canonical_schema_before_pending_write(self) -> None:
        text = read("godot-game-production/SKILL.md")
        required = (
            "Before writing any pending `visual-decision/v2`",
            "read `references/visual-contract.md` and `references/evidence-ledger.md` in the current turn",
            "exact complete `visual-decision/v2` schema in `references/visual-contract.md`",
            "abbreviated, invented aliases, and short objects are invalid",
        )
        assert_contains_all(self, text, required)
        self.assertLess(
            text.index("Before writing any pending `visual-decision/v2`"),
            text.index("Derive a needs-based initial or delta row set"),
        )

    def test_main_skill_exempts_reference_not_proof_from_scope_question(self) -> None:
        text = read("godot-game-production/SKILL.md")
        assert_contains_all(
            self,
            text,
            (
                "pending `initial_scope` or `delta_scope` decisions",
                "`reference_not_proof` writes its complete decision to the pending path",
                "renders only its localized stored message",
                "does not ask the scope question",
            ),
        )

    def test_main_skill_requires_authorization_before_imagegen(self) -> None:
        text = read("godot-game-production/SKILL.md")
        authorization_flow = text[
            text.index("After the user's exact full-set approval"):
        ]
        ordered = (
            "visual-scope-approval/v1",
            "authorize-generation",
            "visual-generation-authorization/v1",
            "AUTHORIZED",
            "ImageGen",
        )
        assert_contains_all(self, authorization_flow, ordered)
        self.assertEqual(
            [authorization_flow.index(value) for value in ordered],
            sorted(authorization_flow.index(value) for value in ordered),
        )

    def test_main_skill_binds_generated_rows_to_authorization(self) -> None:
        text = read("godot-game-production/SKILL.md")
        assert_contains_all(
            self,
            text,
            (
                "one call for every authorized slot",
                "authorization_id",
                "target_gameplay_image",
                "rejected_target_image",
                "cannot validate or enter an approved visual contract",
            ),
        )

    def test_main_skill_requires_fresh_correction_authorization(self) -> None:
        text = read("godot-game-production/SKILL.md")
        assert_contains_all(
            self,
            text,
            (
                "User rejection consumes the old authorization",
                "visual-correction-approval/v1",
                "correction form of `authorize-generation`",
                "exactly one replacement result for that slot",
            ),
        )

    def test_main_skill_opens_late_visual_delta_before_implementation_questions(self) -> None:
        required = (
            "missing or changed player-visible state",
            "complete `delta_scope` decision before any implementation-detail question or game change",
            "unresolved machine-only bindings stay as pending placeholders",
            "Never announce or reopen a visual delta in prose only",
            "missing base contract or target identity uses `<required-value>`",
            "stated independent work in `continuing_work`",
        )
        for path in (
            "godot-game-production/SKILL.md",
            "godot-game-production/references/visual-contract.md",
        ):
            assert_contains_all(self, read(path), required)

    def test_global_delta_cannot_hide_questions_or_targets_in_one_catch_all(self) -> None:
        required = (
            "one independently useful visual question per row",
            "never one representative or catch-all row",
            "one `affected_targets` entry per affected target",
            "distinct placeholder identities",
        )
        for path in (
            "godot-game-production/SKILL.md",
            "godot-game-production/references/visual-contract.md",
        ):
            assert_contains_all(self, read(path), required)

    def test_visual_contract_documents_all_machine_schemas(self) -> None:
        text = read("godot-game-production/references/visual-contract.md")
        assert_contains_all(
            self,
            text,
            (
                "visual-decision/v1",
                "visual-decision/v2",
                "visual-decision-report/v1",
                "visual-scope-approval/v1",
                "visual-correction-approval/v1",
                "visual-generation-authorization/v1",
                "Exit code `0`",
                "Exit code `2`",
                "Exit code `3`",
                "`presentation`",
                "`title`, `image_description`, and `purpose`",
                "`user_interface`",
                "present-decision",
                "present-target-question",
                "must never be pasted into chat",
            ),
        )
        self.assertNotIn("### `visual-decision/v1`", text)

    def test_visual_contract_preserves_dynamic_cardinality(self) -> None:
        text = read("godot-game-production/references/visual-contract.md")
        assert_contains_all(
            self,
            text,
            (
                "one row maps to one proposed image and one numbered item",
                "no minimum, maximum, or preferred pack size",
                "late visual discovery",
                "repeat the same approval procedure",
            ),
        )

    def test_visual_contract_rejects_unsafe_user_facing_text(self) -> None:
        text = read("godot-game-production/references/visual-contract.md")
        assert_contains_all(
            self,
            text,
            (
                "control characters or embedded line breaks",
                "machine-facing content",
                "one physical paragraph per numbered item",
            ),
        )

    def test_visual_contract_enumerates_canonical_proof_gates_in_order(self) -> None:
        text = read("godot-game-production/references/visual-contract.md")
        marker = "The exact ordered canonical proof gates are:"
        self.assertIn(marker, text)
        proof_section = text[text.index(marker):]
        expected = tuple(
            f"- `{gate}`" for gate in visual_contract.CANONICAL_PROOF_GATES
        )
        assert_contains_all(self, proof_section, expected)
        self.assertEqual(
            [proof_section.index(gate) for gate in expected],
            sorted(proof_section.index(gate) for gate in expected),
        )

    def test_evidence_ledger_resolves_all_visual_source_arrays(self) -> None:
        text = read("godot-game-production/references/evidence-ledger.md")
        assert_contains_all(
            self,
            text,
            (
                "visual_decisions",
                "visual_scope_approvals",
                "visual_correction_approvals",
                "visual_generation_authorizations",
                "docs/evidence/visual/decisions/<decision-id>.json",
                "byte-for-byte",
                "authorization_id",
                "complete authorized candidate batch",
                "evidence-run/v1",
                "no compatibility reader",
            ),
        )

    def test_readme_describes_dynamic_authorized_batches(self) -> None:
        text = read("README.md")
        assert_contains_all(
            self,
            text,
            (
                "needs-derived",
                "complete slot set",
                "exact batch authorization",
                "one authorized row budgets one generated result",
                "late visual delta",
                "fresh authorization",
                "unauthorized raw output cannot enter verified evidence",
                "machine JSON stays in project files",
                "numbered image descriptions and approval questions in the user's language",
            ),
        )

    def test_atomic_prose_workaround_is_removed(self) -> None:
        text = read("godot-game-production/SKILL.md")
        for banned in (
            "atomic final-response validity gates",
            "OUTPUT NOW",
            "Current-answer fallback order",
            "A collective phrase, paraphrase, merged item",
        ):
            self.assertNotIn(banned, text)
        assert_contains_all(
            self,
            text,
            (
                "tests/behavioral/score_dynamic_visual_reference.py",
                "scripts/visual_gate.py",
            ),
        )


if __name__ == "__main__":
    unittest.main()
