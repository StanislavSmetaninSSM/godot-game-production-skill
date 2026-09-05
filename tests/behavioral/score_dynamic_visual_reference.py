"""Fail-closed deterministic scorer for file-first visual proposals."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
import types
from pathlib import Path


HERE = Path(__file__).resolve().parent
CATALOG_PATH = HERE / "dynamic-visual-reference-expectations.json"
CASE_IDS = {f"DVC-{number:02d}" for number in range(1, 11)}
CASE_FIELDS = {
    "decision_kind",
    "state",
    "row_count",
    "row_count_min",
    "required_distinct_row_terms",
    "change_scope",
    "blocked_work_terms",
    "continuing_work_terms",
    "required_preserved_target_ids",
    "required_supersedes_target_ids",
    "affected_targets_min",
    "require_nonempty_affected_dependencies",
    "target_approval_scope",
    "required_proof_gates",
    "requires_scope_question",
}
TRACE_FIELDS = {
    "schema_version",
    "session_id",
    "model",
    "reasoning_effort",
    "fork_turns",
    "final_answer_count",
    "task_complete_count",
    "imagegen_call_count",
    "write_paths",
}
CRITERIA = (
    "decision_schema",
    "decision_report",
    "decision_kind",
    "decision_state",
    "row_count",
    "distinct_rows",
    "change_scope",
    "blocked_work",
    "continuing_work",
    "preserved_targets",
    "supersedes_targets",
    "affected_targets",
    "affected_dependencies",
    "target_approval_scope",
    "proof_gates",
    "human_presentation",
    "raw_machine_leakage",
    "trace_policy",
)
class Unsafe(ValueError):
    pass


def _unique(pairs):
    value = {}
    for key, item in pairs:
        if key in value:
            raise Unsafe("duplicate JSON key")
        value[key] = item
    return value


def _loads(text):
    try:
        return json.loads(text, object_pairs_hook=_unique)
    except json.JSONDecodeError as error:
        raise Unsafe("malformed JSON") from error


def _sha(value):
    return hashlib.sha256(value).hexdigest()


def _canonical(value):
    return json.dumps(
        value, ensure_ascii=False, separators=(",", ":"), sort_keys=True
    ).encode("utf-8")


def _regular(path):
    if not path.exists() or not path.is_file() or path.is_symlink():
        raise Unsafe("not a regular file")


def _within(path, root):
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def _load_contract(root):
    source = root / "scripts" / "visual_contract.py"
    _regular(source)
    module = types.ModuleType("isolated_visual_contract")
    module.__file__ = str(source)
    exec(compile(source.read_bytes(), str(source), "exec"), module.__dict__)
    return module


def _manifest(root):
    rows = []
    for path in root.rglob("*"):
        if path.is_symlink():
            raise Unsafe("symlink in isolated root")
        if path.is_file():
            rows.append((path.relative_to(root).as_posix(), _sha(path.read_bytes())))
    if not rows:
        raise Unsafe("empty isolated root")
    rows.sort(key=lambda row: row[0])
    return _sha(_canonical(rows))


def _text_list(value):
    return isinstance(value, list) and all(
        isinstance(item, str) and item for item in value
    )


def _nullable_int(value):
    return value is None or (
        isinstance(value, int) and not isinstance(value, bool) and value >= 0
    )


def _catalog(contract):
    _regular(CATALOG_PATH)
    try:
        value = contract.loads_json(CATALOG_PATH.read_text(encoding="utf-8"))
    except (contract.SchemaError, json.JSONDecodeError) as error:
        raise Unsafe("catalog JSON") from error
    if (
        not isinstance(value, dict)
        or set(value) != {"schema_version", "cases"}
        or value["schema_version"] != "dvc-expectations/v1"
        or not isinstance(value["cases"], dict)
        or set(value["cases"]) != CASE_IDS
    ):
        raise Unsafe("catalog schema")
    for case in value["cases"].values():
        if (
            not isinstance(case, dict)
            or set(case) != CASE_FIELDS
            or not isinstance(case["decision_kind"], str)
            or not isinstance(case["state"], str)
            or not _nullable_int(case["row_count"])
            or not _nullable_int(case["row_count_min"])
        ):
            raise Unsafe("catalog scalar")
        groups = case["required_distinct_row_terms"]
        if not isinstance(groups, list) or not all(
            _text_list(group) and group for group in groups
        ):
            raise Unsafe("catalog terms")
        for key in (
            "blocked_work_terms",
            "continuing_work_terms",
            "required_preserved_target_ids",
            "required_supersedes_target_ids",
            "required_proof_gates",
        ):
            if not _text_list(case[key]):
                raise Unsafe("catalog lists")
        if case["change_scope"] is not None and not isinstance(
            case["change_scope"], str
        ):
            raise Unsafe("catalog scope")
        if case["target_approval_scope"] is not None and not isinstance(
            case["target_approval_scope"], str
        ):
            raise Unsafe("catalog approval")
        if case["affected_targets_min"] is not None and not _nullable_int(
            case["affected_targets_min"]
        ):
            raise Unsafe("catalog targets")
        if case["require_nonempty_affected_dependencies"] is not None and not isinstance(
            case["require_nonempty_affected_dependencies"], bool
        ):
            raise Unsafe("catalog dependencies")
        if not isinstance(case["requires_scope_question"], bool):
            raise Unsafe("catalog question")
    return value["cases"]


def _validate_trace(trace):
    if not isinstance(trace, dict) or set(trace) != TRACE_FIELDS:
        raise Unsafe("trace fields")
    for key in (
        "schema_version", "session_id", "model", "reasoning_effort", "fork_turns"
    ):
        if not isinstance(trace[key], str) or not trace[key]:
            raise Unsafe("trace scalar")
    for key in (
        "final_answer_count", "task_complete_count", "imagegen_call_count"
    ):
        if (
            not isinstance(trace[key], int)
            or isinstance(trace[key], bool)
            or trace[key] < 0
        ):
            raise Unsafe("trace counter")
    if not isinstance(trace["write_paths"], list) or not all(
        isinstance(path, str) and path for path in trace["write_paths"]
    ):
        raise Unsafe("write paths")


def _canonical_pending_paths(decision_path, decision_report_path, decision_id):
    expected_tail = (
        "docs",
        "visual-contract",
        "pending",
        decision_id,
        "decision.json",
    )
    actual_tail = tuple(part.casefold() for part in decision_path.parts[-5:])
    return (
        actual_tail
        == tuple(part.casefold() for part in expected_tail)
        and decision_report_path.parent == decision_path.parent
        and decision_report_path.name.casefold() == "decision-report.json"
    )


def _trace_policy(trace, decision_path, decision_report_path, decision_id):
    _validate_trace(trace)
    expected_writes = {decision_path, decision_report_path}
    actual_writes = [Path(value).resolve() for value in trace["write_paths"]]
    return (
        (
            trace["schema_version"],
            trace["model"],
            trace["reasoning_effort"],
            trace["fork_turns"],
            trace["final_answer_count"],
            trace["task_complete_count"],
            trace["imagegen_call_count"],
        )
        == ("dvc-trace/v2", "gpt-5.6-terra", "medium", "none", 1, 1, 0)
        and len(actual_writes) == 2
        and set(actual_writes) == expected_writes
        and _canonical_pending_paths(
            decision_path, decision_report_path, decision_id
        )
    )


def _distinct(rows, groups):
    text = [
        json.dumps(
            row, ensure_ascii=False, sort_keys=True, separators=(",", ":")
        ).casefold()
        for row in rows
    ]
    graph = [
        [
            index
            for index, item in enumerate(text)
            if any(token.casefold() in item for token in group)
        ]
        for group in groups
    ]
    matched = {}

    def visit(group, seen):
        for row in graph[group]:
            if row not in seen:
                seen.add(row)
                if row not in matched or visit(matched[row], seen):
                    matched[row] = group
                    return True
        return False

    return all(visit(index, set()) for index in range(len(graph)))


def _normalized_answer(value):
    return value.replace("\r\n", "\n").rstrip("\n")


def _leaks_machine_data(answer, decision, contract):
    if contract.user_text_contains_machine_content(answer):
        return True
    if isinstance(decision, dict):
        rows = decision.get("reference_plan", {}).get("rows", [])
        for row in rows:
            slot_id = row.get("reference_slot_id")
            if isinstance(slot_id, str) and slot_id.casefold() in answer.casefold():
                return True
    return False


def _evaluate(
    case,
    answer,
    trace,
    decision_value,
    decision_report_value,
    decision_path,
    decision_report_path,
    contract,
):
    failed = []

    def require(name, result):
        if not result:
            failed.append(name)

    try:
        decision = contract.validate_visual_decision(decision_value)
    except contract.SchemaError:
        decision = None
        failed.append("decision_schema")

    report_valid = False
    if decision is not None:
        try:
            contract.validate_decision_report(decision_report_value, decision)
            report_valid = True
        except contract.SchemaError:
            failed.append("decision_report")

        require("decision_kind", decision["decision_kind"] == case["decision_kind"])
        require("decision_state", decision["state"] == case["state"])
        rows = decision.get("reference_plan", {}).get("rows", [])
        if case["row_count"] is not None:
            require("row_count", len(rows) == case["row_count"])
        if case["row_count_min"] is not None:
            require("row_count", len(rows) >= case["row_count_min"])
        require(
            "distinct_rows",
            _distinct(rows, case["required_distinct_row_terms"]),
        )
        if case["change_scope"] is not None:
            require("change_scope", decision.get("change_scope") == case["change_scope"])
        for field, name in (
            ("blocked_work_terms", "blocked_work"),
            ("continuing_work_terms", "continuing_work"),
        ):
            require(
                name,
                all(
                    term.casefold()
                    in " ".join(decision.get(name, [])).casefold()
                    for term in case[field]
                ),
            )
        require(
            "preserved_targets",
            set(case["required_preserved_target_ids"]).issubset(
                {
                    item.get("target_id")
                    for item in decision.get("preserved_bindings", [])
                }
            ),
        )
        require(
            "supersedes_targets",
            set(case["required_supersedes_target_ids"]).issubset(
                {row.get("supersedes_target_id") for row in rows}
            ),
        )
        affected = decision.get("affected_targets", [])
        if case["affected_targets_min"] is not None:
            require(
                "affected_targets",
                len(affected) >= case["affected_targets_min"],
            )
        if case["require_nonempty_affected_dependencies"]:
            require(
                "affected_dependencies",
                all(item.get("dependent_work") for item in affected),
            )
        if case["target_approval_scope"] is not None:
            require(
                "target_approval_scope",
                decision.get("target_approval_scope")
                == case["target_approval_scope"],
            )
        if case["required_proof_gates"]:
            require(
                "proof_gates",
                decision.get("preserved_evidence")
                == case["required_proof_gates"],
            )

        if report_valid:
            expected = contract.render_decision_presentation(
                decision, decision_report_value
            )
            require(
                "human_presentation",
                _normalized_answer(answer) == expected,
            )

    require(
        "raw_machine_leakage",
        not _leaks_machine_data(answer, decision_value, contract),
    )
    decision_id = (
        decision_value.get("decision_id", "")
        if isinstance(decision_value, dict)
        else ""
    )
    require(
        "trace_policy",
        _trace_policy(
            trace,
            decision_path,
            decision_report_path,
            decision_id,
        ),
    )
    return [item for item in CRITERIA if item in failed]


def _publish(path, report):
    payload = json.dumps(
        report, ensure_ascii=False, separators=(",", ":")
    ).encode("utf-8")
    path.parent.mkdir(parents=True, exist_ok=True)
    file_descriptor, temporary = tempfile.mkstemp(
        prefix=".dvc-", suffix=".tmp", dir=path.parent
    )
    try:
        with os.fdopen(file_descriptor, "wb") as output:
            output.write(payload)
            output.flush()
            os.fsync(output.fileno())
        try:
            os.link(temporary, path)
        except FileExistsError:
            pass
        finally:
            os.unlink(temporary)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)
    _regular(path)
    if _loads(path.read_text(encoding="utf-8")) != report:
        raise Unsafe("report collision")


def main(argv=None):
    parser = argparse.ArgumentParser(add_help=False)
    for name in (
        "case",
        "answer",
        "trace",
        "decision",
        "decision-report",
        "skill-root",
        "report",
    ):
        parser.add_argument("--" + name, required=True)
    try:
        args = parser.parse_args(argv)
    except SystemExit:
        return 3
    try:
        answer = Path(args.answer).resolve()
        trace = Path(args.trace).resolve()
        decision = Path(args.decision).resolve()
        decision_report = Path(args.decision_report).resolve()
        root = Path(args.skill_root).resolve()
        report = Path(args.report).resolve()
        inputs = (answer, trace, decision, decision_report, report)
        if (
            args.case not in CASE_IDS
            or not root.is_dir()
            or report.suffix.lower() != ".json"
            or len(set(inputs)) != len(inputs)
            or any(_within(path, root) for path in inputs)
        ):
            raise Unsafe("unsafe overlap")
        for path in (answer, trace, decision, decision_report):
            _regular(path)
        contract = _load_contract(root)
        cases = _catalog(contract)
        try:
            trace_value = contract.loads_json(trace.read_text(encoding="utf-8"))
            decision_value = contract.loads_json(
                decision.read_text(encoding="utf-8")
            )
            decision_report_value = contract.loads_json(
                decision_report.read_text(encoding="utf-8")
            )
        except contract.SchemaError as error:
            raise Unsafe("duplicate machine JSON key") from error
        _validate_trace(trace_value)
        failed = _evaluate(
            cases[args.case],
            answer.read_text(encoding="utf-8"),
            trace_value,
            decision_value,
            decision_report_value,
            decision,
            decision_report,
            contract,
        )
        value = {
            "schema_version": "dvc-score-report/v2",
            "case_id": args.case,
            "session_id": trace_value["session_id"],
            "answer_sha256": _sha(answer.read_bytes()),
            "trace_sha256": _sha(trace.read_bytes()),
            "decision_sha256": _sha(decision.read_bytes()),
            "decision_report_sha256": _sha(decision_report.read_bytes()),
            "skill_manifest_sha256": _manifest(root),
            "status": "PASS" if not failed else "FAIL",
            "passed_criteria": [item for item in CRITERIA if item not in failed],
            "failed_criteria": failed,
        }
        _publish(report, value)
        return 0 if not failed else 2
    except (Unsafe, OSError, UnicodeError, json.JSONDecodeError):
        return 3


if __name__ == "__main__":
    raise SystemExit(main())
