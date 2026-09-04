# Behavioral Scorer Observable Policy Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Remove filesystem-read policing from the dynamic-visual behavioral scorer while preserving deterministic checks of observable run behavior.

**Architecture:** Replace the read-inventory-heavy `dvc-trace/v1` schema with a minimal `dvc-trace/v2` schema. Keep answer validation, model/run counters, ImageGen/write rejection, immutable report publication, and runner-owned isolation unchanged.

**Tech Stack:** Python 3 standard library, `unittest`, Markdown.

## Global Constraints

- Do not add a v1 compatibility branch.
- Do not weaken decision-schema, ImageGen, write, final-answer, or report-collision checks.
- Do not add dependency allowlists; reads are outside scorer responsibility.

---

### Task 1: Replace read policing with observable-run validation

**Files:**
- Modify: `tests/test_dynamic_visual_behavioral_scorer.py`
- Modify: `tests/behavioral/score_dynamic_visual_reference.py`
- Modify: `docs/superpowers/specs/2026-08-20-deterministic-visual-authorization-gate-design.md`
- Modify: `docs/superpowers/evals/2026-08-20-dynamic-visual-reference-contract.md`

**Interfaces:**
- Consumes: normalized evaluator trace JSON and the existing scorer CLI arguments.
- Produces: exact `dvc-trace/v2` validation without read telemetry; existing `dvc-score-report/v1` output remains unchanged.

- [ ] **Step 1: Write the failing v2 tests**

Change the valid fixture to:

```python
{
    "schema_version": "dvc-trace/v2",
    "session_id": "v5c-original-session",
    "model": "gpt-5.6-terra",
    "reasoning_effort": "medium",
    "fork_turns": "none",
    "final_answer_count": 1,
    "task_complete_count": 1,
    "imagegen_call_count": 0,
    "write_paths": [],
}
```

Delete read/tool-policy tests and add a regression asserting that adding legacy
`read_paths` and `tool_calls` makes the exact v2 schema unsafe.

- [ ] **Step 2: Confirm RED**

Run:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
python -B -m unittest tests.test_dynamic_visual_behavioral_scorer -v
```

Expected: the valid v2 scorer test fails because production still requires v1 read telemetry.

- [ ] **Step 3: Implement the minimal scorer change**

Set `TRACE_FIELDS` to the nine v2 observable fields, remove `BANNED`, remove
`Counter`, simplify `_validate_trace(trace)`, and make `_trace_policy(trace)` check
only exact v2 metadata, zero ImageGen calls, and an empty write list. Remove the
unused `root` parameter from `_evaluate`'s policy call.

- [ ] **Step 4: Confirm GREEN and regression safety**

Run the focused test followed by:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
python -B -m unittest discover -s tests
```

Expected: all tests pass, including retained ImageGen/write/final-count failures.

- [ ] **Step 5: Align durable documentation**

Amend the original scorer design and current eval ledger to state that read
isolation is runner-owned and fresh traces use v2. Preserve historical run facts.

- [ ] **Step 6: Validate and commit**

Run the official quick validator, `git diff --check`, inspect status/diff, and
commit the bounded change.
