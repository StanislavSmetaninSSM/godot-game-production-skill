"""Deterministic tests for the file-first dynamic visual scorer."""

from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import shutil
import tempfile
import unittest
import uuid
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCORER_PATH = (
    ROOT / "tests" / "behavioral" / "score_dynamic_visual_reference.py"
)


def load_scorer():
    spec = importlib.util.spec_from_file_location("dvc_scorer", SCORER_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(module)
    return module


class DynamicVisualBehavioralScorerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name)
        self.skill = self.directory / "isolated" / "godot-game-production"
        (self.skill / "scripts").mkdir(parents=True)
        shutil.copy2(
            ROOT
            / "godot-game-production"
            / "scripts"
            / "visual_contract.py",
            self.skill / "scripts" / "visual_contract.py",
        )
        (self.skill / "SKILL.md").write_text("# isolated", encoding="utf-8")
        self.contract = load_scorer()._load_contract(self.skill)

    def row(
        self,
        term: str,
        index: int,
        *,
        change_kind: str = "initial",
        supersedes_target_id: str | None = None,
    ) -> dict[str, object]:
        return {
            "reference_slot_id": f"SLOT-{index}",
            "target_kind": "gameplay_state",
            "subject": term,
            "visual_question": f"How should {term} read?",
            "coverage": [term],
            "composition": {
                "camera": "side view",
                "angle": "play angle",
                "environment": f"room for {term}",
                "characters": "player and readable hazard",
                "ui": "relevant HUD state",
                "vfx": "readable interaction cue",
            },
            "motion_cue": "clear movement direction",
            "sound_cue": "clear response cue",
            "dependent_work": [term],
            "rationale": f"No approved target settles {term}.",
            "presentation": {
                "title": f"Reference for {term}",
                "image_description": (
                    f"A side-view gameplay image showing {term}, the player, "
                    "environment, HUD state, and the readable interaction effect"
                ),
                "purpose": (
                    f"This reference settles the production presentation for {term}"
                ),
            },
            "image_count": 1,
            "change_kind": change_kind,
            "supersedes_target_id": supersedes_target_id,
        }

    def decision(self, case: str = "DVC-01") -> dict[str, object]:
        terms = {
            "DVC-01": ["normal default play", "failure retry"],
            "DVC-02": [
                "overworld", "town", "interior", "stealth", "combat",
                "boss", "failure retry", "reward", "inventory",
            ],
            "DVC-03": ["exploration", "danger", "failure retry"],
            "DVC-04": ["normal play"],
            "DVC-05": ["exploration", "combat", "failure", "reward"],
            "DVC-06": ["front", "side silhouette", "action in-game"],
            "DVC-07": ["boss phase two"],
            "DVC-08": ["boss replacement"],
            "DVC-09": ["global style", "global camera", "global UI"],
        }[case]
        rows = [self.row(term, index) for index, term in enumerate(terms, 1)]
        decision: dict[str, object] = {
            "schema_version": "visual-decision/v2",
            "decision_id": str(uuid.uuid4()),
            "builder_id": "test-builder",
            "created_at": "2026-01-01T00:00:00Z",
            "decision_kind": "initial_scope",
            "state": "REFERENCE_SCOPE_PENDING",
            "generation_status": "not_started",
            "reference_plan": {
                "plan_id": "plan-under-test",
                "revision": 1,
                "kind": "initial",
                "base_contract_id": None,
                "rows": rows,
                "approval": None,
            },
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
        if case in {"DVC-07", "DVC-08", "DVC-09"}:
            for row in rows:
                row["change_kind"] = "add"
            preserved: list[dict[str, object]] = []
            affected = [
                {
                    "target_id": f"TARGET-GLOBAL-{index}",
                    "dependent_work": [term],
                    "change_kind": "add",
                }
                for index, term in enumerate(terms, 1)
            ]
            if case == "DVC-08":
                rows[0]["change_kind"] = "replace"
                rows[0]["supersedes_target_id"] = "TARGET-03"
                preserved = [
                    {
                        "target_id": target_id,
                        "sha256": "a" * 64,
                        "path": f"targets/{target_id.casefold()}.png",
                    }
                    for target_id in ("TARGET-01", "TARGET-02", "TARGET-04")
                ]
                affected = [{
                    "target_id": "TARGET-03",
                    "dependent_work": ["boss replacement"],
                    "change_kind": "replace",
                }]
            decision.update({
                "decision_kind": "delta_scope",
                "state": "VISUAL_DELTA_PENDING",
                "change_scope": "global" if case == "DVC-09" else "local",
                "reference_plan": {
                    "plan_id": "plan-under-test",
                    "revision": 1,
                    "kind": "delta",
                    "base_contract_id": "base-contract",
                    "rows": rows,
                    "approval": None,
                },
                "blocked_work": ["boss"] if case == "DVC-07" else [],
                "continuing_work": (
                    ["save", "town"] if case == "DVC-07" else []
                ),
                "preserved_bindings": preserved,
                "affected_targets": affected,
                "target_approval_scope": "complete_delta_batch_only",
            })
        return decision

    def proof_decision(self) -> dict[str, object]:
        return {
            "schema_version": "visual-decision/v2",
            "decision_id": str(uuid.uuid4()),
            "builder_id": "test-builder",
            "created_at": "2026-01-01T00:00:00Z",
            "decision_kind": "reference_not_proof",
            "state": "UNCHANGED",
            "generation_status": "not_authorized",
            "verdict": "rejected",
            "preserved_evidence": list(self.contract.CANONICAL_PROOF_GATES),
            "user_interface": {
                "language": "en",
                "message": (
                    "The references guide visual direction but cannot replace "
                    "runtime, gameplay, performance, or release evidence."
                ),
            },
        }

    def trace(
        self, decision_path: Path, decision_report_path: Path
    ) -> dict[str, object]:
        return {
            "schema_version": "dvc-trace/v2",
            "session_id": "v6-file-first-session",
            "model": "gpt-5.6-terra",
            "reasoning_effort": "medium",
            "fork_turns": "none",
            "final_answer_count": 1,
            "task_complete_count": 1,
            "imagegen_call_count": 0,
            "write_paths": [str(decision_path), str(decision_report_path)],
        }

    def score(
        self,
        case: str = "DVC-01",
        *,
        decision: dict[str, object] | None = None,
        decision_report: dict[str, object] | None = None,
        trace: dict[str, object] | None = None,
        text: str | None = None,
        score_report: Path | None = None,
        decision_text: str | None = None,
    ) -> tuple[int, Path]:
        value = decision or (
            self.proof_decision() if case == "DVC-10" else self.decision(case)
        )
        pending = (
            self.directory
            / "workspace"
            / "docs"
            / "visual-contract"
            / "pending"
            / str(value["decision_id"])
        )
        pending.mkdir(parents=True, exist_ok=True)
        decision_path = pending / "decision.json"
        decision_report_path = pending / "decision-report.json"
        decision_path.write_text(
            decision_text
            if decision_text is not None
            else json.dumps(value, ensure_ascii=False),
            encoding="utf-8",
        )
        report_value = decision_report or self.contract.build_decision_report(value)
        decision_report_path.write_text(
            json.dumps(report_value, ensure_ascii=False), encoding="utf-8"
        )
        answer_path = self.directory / "answer.txt"
        answer_path.write_text(
            text
            if text is not None
            else self.contract.render_decision_presentation(value, report_value),
            encoding="utf-8",
        )
        trace_path = self.directory / "trace.json"
        trace_path.write_text(
            json.dumps(
                trace or self.trace(decision_path, decision_report_path),
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )
        report_path = score_report or self.directory / "score-report.json"
        code = load_scorer().main([
            "--case", case,
            "--answer", str(answer_path),
            "--trace", str(trace_path),
            "--decision", str(decision_path),
            "--decision-report", str(decision_report_path),
            "--skill-root", str(self.skill),
            "--report", str(report_path),
        ])
        return code, report_path

    def assert_fail(self, criterion: str, **kwargs: object) -> None:
        code, report_path = self.score(**kwargs)
        self.assertEqual(code, 2)
        report = json.loads(report_path.read_text(encoding="utf-8"))
        self.assertEqual(report["status"], "FAIL")
        self.assertIn(criterion, report["failed_criteria"])

    def test_valid_scope_projection_returns_machine_pass(self) -> None:
        code, report_path = self.score()
        self.assertEqual(code, 0)
        self.assertEqual(
            json.loads(report_path.read_text(encoding="utf-8"))["status"],
            "PASS",
        )

    def test_raw_json_and_code_fences_fail_leakage_policy(self) -> None:
        decision = self.decision()
        for text in (
            json.dumps(decision, ensure_ascii=False),
            "```json\n" + json.dumps(decision, ensure_ascii=False) + "\n```",
        ):
            with self.subTest(text=text[:8]):
                self.assert_fail(
                    "raw_machine_leakage", decision=decision, text=text,
                    score_report=(
                        self.directory / f"leak-{uuid.uuid4().hex}.json"
                    ),
                )

    def test_numbering_order_and_description_drift_fail(self) -> None:
        decision = self.decision()
        report = self.contract.build_decision_report(decision)
        rendered = self.contract.render_decision_presentation(decision, report)
        rows, question = rendered.rsplit("\n\n", 1)
        first, second = rows.split("\n\n")
        variants = (
            rendered.replace("1)", "9)", 1),
            "\n\n".join((second, first, question)),
            rendered.replace("side-view gameplay", "top-down gameplay", 1),
            rows,
        )
        for index, text in enumerate(variants):
            with self.subTest(index=index):
                self.assert_fail(
                    "human_presentation",
                    decision=decision,
                    decision_report=report,
                    text=text,
                    score_report=self.directory / f"drift-{index}.json",
                )

    def test_invalid_decision_report_binding_fails(self) -> None:
        decision = self.decision()
        report = self.contract.build_decision_report(decision)
        report["decision_sha256"] = "a" * 64
        self.assert_fail(
            "decision_report",
            decision=decision,
            decision_report=report,
            text="No proposal is safe to present.",
        )

    def test_v1_and_empty_rows_fail_decision_schema(self) -> None:
        for index, decision in enumerate((self.decision(), self.decision())):
            if index == 0:
                decision["schema_version"] = "visual-decision/v1"
            else:
                decision["reference_plan"]["rows"] = []
            self.assert_fail(
                "decision_schema",
                decision=decision,
                text="Invalid decision",
                score_report=self.directory / f"schema-{index}.json",
            )

    def test_requested_seven_does_not_pad_three_row_plan(self) -> None:
        decision = self.decision("DVC-03")
        extra = self.row("filler", 4)
        decision["reference_plan"]["rows"].append(extra)
        report = self.contract.build_decision_report(decision)
        self.assert_fail(
            "row_count",
            case="DVC-03",
            decision=decision,
            decision_report=report,
            text=self.contract.render_decision_presentation(decision, report),
        )

    def test_delta_and_global_semantics_still_fail_closed(self) -> None:
        delta = self.decision("DVC-08")
        delta["reference_plan"]["rows"][0]["supersedes_target_id"] = "TARGET-X"
        delta["affected_targets"][0]["target_id"] = "TARGET-X"
        report = self.contract.build_decision_report(delta)
        self.assert_fail(
            "supersedes_targets",
            case="DVC-08",
            decision=delta,
            decision_report=report,
            text=self.contract.render_decision_presentation(delta, report),
        )
        global_delta = self.decision("DVC-09")
        global_delta["affected_targets"][0]["dependent_work"] = []
        self.assert_fail(
            "decision_schema",
            case="DVC-09",
            decision=global_delta,
            text="Invalid global delta",
            score_report=self.directory / "global-schema.json",
        )

    def test_reference_not_proof_uses_localized_message(self) -> None:
        decision = self.proof_decision()
        code, _ = self.score(case="DVC-10", decision=decision)
        self.assertEqual(code, 0)
        decision["preserved_evidence"].pop()
        self.assert_fail(
            "decision_schema",
            case="DVC-10",
            decision=decision,
            text="Invalid proof decision",
            score_report=self.directory / "proof-fail.json",
        )

    def test_trace_allows_only_the_two_bound_artifact_writes(self) -> None:
        decision = self.decision()
        pending = (
            self.directory / "workspace" / "docs" / "visual-contract"
            / "pending" / str(decision["decision_id"])
        )
        expected = self.trace(
            pending / "decision.json", pending / "decision-report.json"
        )
        variants = []
        missing = dict(expected)
        missing["write_paths"] = missing["write_paths"][:1]
        variants.append(missing)
        extra = dict(expected)
        extra["write_paths"] = extra["write_paths"] + [str(self.directory / "x")]
        variants.append(extra)
        generated = dict(expected)
        generated["imagegen_call_count"] = 1
        variants.append(generated)
        repeated = dict(expected)
        repeated["final_answer_count"] = 2
        variants.append(repeated)
        for index, trace in enumerate(variants):
            with self.subTest(index=index):
                self.assert_fail(
                    "trace_policy",
                    decision=decision,
                    trace=trace,
                    score_report=self.directory / f"trace-{index}.json",
                )

    def test_malformed_or_unsafe_inputs_return_three(self) -> None:
        self.assertEqual(
            self.score(decision_text='{"decision_id":"one","decision_id":"two"}')[0],
            3,
        )
        trace = self.trace(Path("decision.json"), Path("decision-report.json"))
        trace["final_answer_count"] = True
        self.assertEqual(
            self.score(trace=trace, score_report=self.directory / "bad-trace.json")[0],
            3,
        )

    def test_answer_or_trace_inside_skill_root_is_unsafe(self) -> None:
        decision = self.decision()
        report = self.contract.build_decision_report(decision)
        pending = (
            self.directory / "workspace" / "docs" / "visual-contract"
            / "pending" / str(decision["decision_id"])
        )
        pending.mkdir(parents=True)
        decision_path = pending / "decision.json"
        decision_report_path = pending / "decision-report.json"
        decision_path.write_text(json.dumps(decision), encoding="utf-8")
        decision_report_path.write_text(json.dumps(report), encoding="utf-8")
        answer = self.skill / "answer.txt"
        trace_path = self.directory / "trace.json"
        score_report = self.directory / "unsafe-score.json"
        answer.write_text(
            self.contract.render_decision_presentation(decision, report),
            encoding="utf-8",
        )
        trace_path.write_text(
            json.dumps(self.trace(decision_path, decision_report_path)),
            encoding="utf-8",
        )
        code = load_scorer().main([
            "--case", "DVC-01", "--answer", str(answer),
            "--trace", str(trace_path), "--decision", str(decision_path),
            "--decision-report", str(decision_report_path),
            "--skill-root", str(self.skill), "--report", str(score_report),
        ])
        self.assertEqual(code, 3)

    def test_report_collision_and_argument_parse_fail_closed(self) -> None:
        code, score_report = self.score()
        self.assertEqual(code, 0)
        self.assertEqual(
            self.score(text="changed", score_report=score_report)[0], 3
        )
        with contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(load_scorer().main(["--pass", "yes"]), 3)

    def test_contract_load_does_not_create_bytecode(self) -> None:
        self.assertEqual(self.score()[0], 0)
        self.assertFalse((self.skill / "scripts" / "__pycache__").exists())

    def test_score_report_binds_both_machine_artifacts(self) -> None:
        code, report_path = self.score()
        self.assertEqual(code, 0)
        self.assertEqual(
            list(json.loads(report_path.read_text(encoding="utf-8")).keys()),
            [
                "schema_version", "case_id", "session_id", "answer_sha256",
                "trace_sha256", "decision_sha256", "decision_report_sha256",
                "skill_manifest_sha256", "status", "passed_criteria",
                "failed_criteria",
            ],
        )


if __name__ == "__main__":
    unittest.main()
