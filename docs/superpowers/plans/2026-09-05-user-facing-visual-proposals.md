# User-Facing Visual Proposals Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Keep complete visual decisions in project files while presenting users only a deterministic, detailed, localized numbered image list and localized approval question.

**Architecture:** Upgrade the decision contract to breaking `visual-decision/v2`, add localized presentation data to each row and decision, and make `visual_gate.py` the only renderer of user-facing proposal text. The behavioral scorer consumes the decision and validation report as separate files, compares chat text to that renderer, and rejects JSON leakage, drift, unexpected writes, or preapproval ImageGen calls.

**Tech Stack:** Python 3 standard library, `unittest`, Markdown skill/reference files, Git.

## Global Constraints

- The reference count is dynamic: one plan row equals one proposed image and one numbered item; there is no fixed minimum, maximum, or preferred pack size.
- Normal chat contains no JSON, code fence, schema name, hash, artifact path, internal slot ID, or machine-facing field.
- Every item contains localized `title`, `image_description`, and `purpose`; the two approval questions use the user's conversation language.
- Pending artifacts live at `docs/visual-contract/pending/<decision-id>/decision.json` and `decision-report.json` and are written before presentation.
- `visual-decision/v1` is rejected; no compatibility or migration path is implemented.
- Validation, report/hash binding, rendering, or writing failure prevents both the approval question and ImageGen.
- Existing scope authorization, immutable hashes, delta/replacement behavior, correction approvals, proof separation, evidence gates, and release gates remain fail-closed.

---

### Task 1: Visual-decision v2 schema and deterministic text projection

**Files:**
- Modify: `tests/test_visual_gate.py`
- Modify: `godot-game-production/scripts/visual_contract.py`

**Interfaces:**
- Consumes: existing `loads_json(text: str) -> object`, `canonical_sha256(value: object) -> str`, and decision validation functions.
- Produces: `validate_decision_report(value: object, decision: dict[str, object]) -> dict[str, object]`, `render_decision_presentation(decision: dict[str, object], report: dict[str, object]) -> str`, and `render_target_question(decision: dict[str, object], report: dict[str, object]) -> str`.

- [ ] **Step 1: Write failing v2 validation and Russian/English rendering tests**

Add fixtures whose rows contain:

```python
"presentation": {
    "title": "Поражение персонажа",
    "image_description": "Игровой вид сбоку в момент удара: героя отбрасывает от хорошо читаемой опасности, а поверх сцены появляется экран повторной попытки",
    "purpose": "Референс определяет подачу поражения и возврата в игру",
}
```

and whose pending decision contains:

```python
"user_interface": {
    "language": "ru",
    "scope_question": "Подтверждаете именно этот набор изображений для генерации?",
    "target_question": "Подтверждаете именно этот показанный набор изображений?",
}
```

Assert that v2 validates, v1 fails, placeholders and `REF-01`-only presentation values fail, Russian UI with the former English question fails, the report hash must bind, numbered rows preserve order, the scope question is the final non-empty line, the target renderer returns the localized target question, and `reference_not_proof` renders only its localized message.

- [ ] **Step 2: Run the focused tests and verify RED**

Run:

```powershell
python -B -m unittest tests.test_visual_gate.VisualDecisionTests -v
```

Expected: FAIL because the v2 fields and renderer functions do not exist and v1 is still accepted.

- [ ] **Step 3: Implement the v2 schema and renderers**

Use these exact field shapes:

```python
PRESENTATION_FIELDS = {"title", "image_description", "purpose"}
SCOPE_USER_INTERFACE_FIELDS = {
    "language", "scope_question", "target_question",
}
PROOF_USER_INTERFACE_FIELDS = {"language", "message"}
DECISION_REPORT_FIELDS = {
    "schema_version", "decision_id", "decision_sha256", "status", "errors",
}
```

Add `presentation` to `REFERENCE_SLOT_FIELDS`, replace top-level `scope_question` with `user_interface`, require `visual-decision/v2`, require a BCP-47-like language tag, nonempty localized text, no placeholder or technical-ID-only presentation field, and Cyrillic user-facing text for `ru` language tags. Validate a report with exact `visual-decision-report/v1`, `VALID_PENDING`, empty errors, matching decision ID, and matching canonical hash.

Render each row deterministically as:

```python
def _sentence(value: str) -> str:
    text = value.strip()
    return text if text.endswith((".", "!", "?", "…")) else text + "."

def _render_row(index: int, row: dict[str, object]) -> str:
    presentation = row["presentation"]
    body = " ".join(_sentence(presentation[key]) for key in (
        "title", "image_description", "purpose",
    ))
    return f"{index}) {body}"
```

`render_decision_presentation` validates both inputs, joins scope rows with blank lines and appends `scope_question`; for `reference_not_proof` it returns the localized message. `render_target_question` accepts only initial/delta decisions and returns the stored target question.

- [ ] **Step 4: Run the focused tests and verify GREEN**

Run:

```powershell
python -B -m unittest tests.test_visual_gate.VisualDecisionTests -v
```

Expected: all `VisualDecisionTests` pass.

- [ ] **Step 5: Commit the contract slice**

```powershell
git add tests/test_visual_gate.py godot-game-production/scripts/visual_contract.py
git commit -m "feat: add localized visual decision presentation"
```

### Task 2: File-bound presentation commands

**Files:**
- Modify: `tests/test_visual_gate.py`
- Modify: `godot-game-production/scripts/visual_gate.py`

**Interfaces:**
- Consumes: `render_decision_presentation` and `render_target_question` from Task 1.
- Produces: CLI commands `present-decision --decision PATH --report PATH` and `present-target-question --decision PATH --report PATH`.

- [ ] **Step 1: Write failing CLI tests**

Call `visual_gate.main(...)` with real temporary decision/report files and captured stdout. Assert the exact numbered Russian proposal, proof message, and target question are emitted; assert exit `3` with empty stdout for malformed JSON, invalid decisions, non-`VALID_PENDING` reports, ID/hash mismatches, missing files, and v1 inputs.

- [ ] **Step 2: Run the CLI tests and verify RED**

Run:

```powershell
python -B -m unittest tests.test_visual_gate.VisualGateCliTests -v
```

Expected: FAIL because both presentation subcommands are absent.

- [ ] **Step 3: Implement fail-closed presentation commands**

Add both parsers with required `--decision` and `--report`. Load each file through duplicate-key-safe `_load_json_file`, validate the decision and report, compute text with the corresponding renderer, and call `sys.stdout.write(text + "\n")` only after all checks succeed. Catch `OSError`, `UnicodeError`, `json.JSONDecodeError`, `SchemaError`, and `InvariantError` and return `3` without partial output.

- [ ] **Step 4: Run the CLI tests and verify GREEN**

Run:

```powershell
python -B -m unittest tests.test_visual_gate.VisualGateCliTests -v
```

Expected: all presentation CLI tests pass.

- [ ] **Step 5: Commit the CLI slice**

```powershell
git add tests/test_visual_gate.py godot-game-production/scripts/visual_gate.py
git commit -m "feat: render visual proposals from bound files"
```

### Task 3: Migrate evidence fixtures without weakening authorization

**Files:**
- Modify: `tests/test_evidence_run_v2.py`
- Modify: `godot-game-production/scripts/evidence_run.py` only if a shipped fixture/template contains v1 decision fields.

**Interfaces:**
- Consumes: the v2 decision shape from Task 1.
- Produces: unchanged evidence-run and authorization behavior using v2 decision hashes.

- [ ] **Step 1: Convert evidence tests to v2 and run them RED**

Replace each fixture's `schema_version` with `visual-decision/v2`, add row `presentation` objects, and replace `scope_question` with localized `user_interface`. Run:

```powershell
python -B -m unittest tests.test_evidence_run_v2 -v
```

Expected: at least one FAIL until every production fixture/template consumer understands v2; if all pass, record that authorization is schema-agnostic and no production edit is required.

- [ ] **Step 2: Make the minimal production fixture/template update**

Preserve the existing approval and authorization hashes and field names. Any generated pending decision must use:

```python
"schema_version": "visual-decision/v2",
"user_interface": {
    "language": "en",
    "scope_question": "Do you approve this exact set of images for generation?",
    "target_question": "Do you approve this exact displayed set of images?",
},
```

with a complete `presentation` object on each row.

- [ ] **Step 3: Run evidence and authorization tests GREEN**

Run:

```powershell
python -B -m unittest tests.test_evidence_run_v2 tests.test_visual_gate.VisualAuthorizationTests -v
```

Expected: all tests pass and unresolved placeholders remain unauthorized.

- [ ] **Step 4: Commit the migration slice**

```powershell
git add tests/test_evidence_run_v2.py godot-game-production/scripts/evidence_run.py
git commit -m "test: migrate evidence fixtures to visual decision v2"
```

### Task 4: Make the behavioral scorer file-first and leakage-proof

**Files:**
- Modify: `tests/test_dynamic_visual_behavioral_scorer.py`
- Modify: `tests/behavioral/score_dynamic_visual_reference.py`
- Modify: `tests/behavioral/dynamic-visual-reference-expectations.json`

**Interfaces:**
- Consumes: `decision.json`, `decision-report.json`, deterministic renderer, answer text, and trace.
- Produces: scorer CLI with additional required `--decision PATH` and `--decision-report PATH` arguments.

- [ ] **Step 1: Write failing scorer tests**

Build real v2 files beside each answer. Assert PASS only when the answer exactly equals `render_decision_presentation`; assert criteria failures for raw JSON/code fences/machine keys, wrong numbering, reordered rows, altered descriptions, missing scope question, wrong proof message, invalid report binding, unexpected write paths, and nonzero preapproval ImageGen calls. Assert unsafe path overlaps or malformed machine JSON return exit `3`.

- [ ] **Step 2: Run scorer tests and verify RED**

Run:

```powershell
python -B -m unittest tests.test_dynamic_visual_behavioral_scorer -v
```

Expected: FAIL because the scorer still extracts fenced JSON from chat and forbids all writes.

- [ ] **Step 3: Implement separate artifact inputs and exact projection checks**

Change the criteria to:

```python
CRITERIA = (
    "decision_schema", "decision_report", "decision_kind", "decision_state",
    "row_count", "distinct_rows", "change_scope", "blocked_work",
    "continuing_work", "preserved_targets", "supersedes_targets",
    "affected_targets", "affected_dependencies", "target_approval_scope",
    "proof_gates", "human_presentation", "raw_machine_leakage", "trace_policy",
)
```

Remove fenced-decision extraction. Validate the supplied decision/report directly, derive `expected_answer = contract.render_decision_presentation(decision, decision_report)`, require newline-normalized exact equality, and separately reject fences plus `schema_version`, `decision_id`, `reference_slot_id`, `visual-decision/`, hash-like values, and serialized object text. `_trace_policy` must require exactly the two normalized expected artifact paths, `imagegen_call_count == 0`, and the existing Terra/medium/none/single-final invariants.

- [ ] **Step 4: Run scorer tests and verify GREEN**

Run:

```powershell
python -B -m unittest tests.test_dynamic_visual_behavioral_scorer -v
```

Expected: all scorer tests pass.

- [ ] **Step 5: Commit the scorer slice**

```powershell
git add tests/test_dynamic_visual_behavioral_scorer.py tests/behavioral/score_dynamic_visual_reference.py tests/behavioral/dynamic-visual-reference-expectations.json
git commit -m "test: score localized visual proposals from files"
```

### Task 5: Teach the skill the user-facing workflow

**Files:**
- Modify: `tests/test_dynamic_visual_reference_contract.py`
- Modify: `tests/test_production_operations_contract.py`
- Modify: `godot-game-production/SKILL.md`
- Modify: `godot-game-production/references/visual-contract.md`
- Modify: `docs/superpowers/specs/2026-08-20-deterministic-visual-authorization-gate-design.md`
- Modify: `docs/superpowers/specs/2026-08-20-dynamic-visual-reference-contract-design.md`

**Interfaces:**
- Consumes: the v2 schema and two presentation commands.
- Produces: concise operational instructions that route schema detail to `references/visual-contract.md`.

- [ ] **Step 1: Invert contract tests and verify RED**

Assert that `SKILL.md` requires the canonical pending directory, validation before rendering, verbatim renderer output, one detailed numbered item per row, user-language scope and target questions, no JSON or machine fields in chat, and re-entry for delta references. Assert it no longer instructs an agent to emit fenced JSON or the fixed English questions.

Run:

```powershell
python -B -m unittest tests.test_dynamic_visual_reference_contract tests.test_production_operations_contract -v
```

Expected: FAIL on the old fenced-JSON and English-literal instructions.

- [ ] **Step 2: Update the entrypoint and visual contract reference**

In `SKILL.md`, state the positive response recipe in this order: write the complete v2 decision and report to the canonical pending directory; run `present-decision`; copy its output verbatim; wait for explicit scope approval; authorize/generate/display; run `present-target-question`; wait for target approval. State that failure yields a localized explanation without JSON and no approval question or ImageGen.

In `references/visual-contract.md`, document exact v2 fields and commands:

```powershell
python godot-game-production/scripts/visual_gate.py check-decision --decision docs/visual-contract/pending/<decision-id>/decision.json --report docs/visual-contract/pending/<decision-id>/decision-report.json
python godot-game-production/scripts/visual_gate.py present-decision --decision docs/visual-contract/pending/<decision-id>/decision.json --report docs/visual-contract/pending/<decision-id>/decision-report.json
python godot-game-production/scripts/visual_gate.py present-target-question --decision docs/visual-contract/pending/<decision-id>/decision.json --report docs/visual-contract/pending/<decision-id>/decision-report.json
```

Keep machine JSON examples inside the reference document only and label them as file contents that must never be pasted into chat. Mark the two 2026-08-20 design documents as superseded where their v1 chat contract conflicts with the approved 2026-09-05 design.

- [ ] **Step 3: Run contract tests and verify GREEN**

Run:

```powershell
python -B -m unittest tests.test_dynamic_visual_reference_contract tests.test_production_operations_contract -v
```

Expected: all contract tests pass.

- [ ] **Step 4: Commit the skill/documentation slice**

```powershell
git add tests/test_dynamic_visual_reference_contract.py tests/test_production_operations_contract.py godot-game-production/SKILL.md godot-game-production/references/visual-contract.md docs/superpowers/specs/2026-08-20-deterministic-visual-authorization-gate-design.md docs/superpowers/specs/2026-08-20-dynamic-visual-reference-contract-design.md
git commit -m "docs: make visual proposals user friendly"
```

### Task 6: Forward evaluation, full verification, integration, and installation

**Files:**
- Modify: the current behavioral-evaluation ledger or fixture paths referenced by `tests/behavioral/dynamic-visual-reference-cases.md` if required by the runner.
- Verify: entire repository and installed copy.

**Interfaces:**
- Consumes: Tasks 1–5.
- Produces: verified `main` on GitHub and a byte-matching installed skill at `C:\Users\Ёж\.codex\skills\godot-game-production`.

- [ ] **Step 1: Run affected behavioral forward cases**

Run the repository's existing behavioral runner for `DVC-01`, `DVC-07`, `DVC-09`, and `DVC-10` using isolated temporary workspaces and the v2 decision/report inputs. Expected: all four score reports have `status: PASS`, no preapproval ImageGen call, and only the two pending artifact writes.

- [ ] **Step 2: Run the full deterministic verification**

```powershell
python -B tests/test_production_operations_contract.py -v
python -B -m unittest discover -s tests -p "test_*.py" -v
python C:/Users/Ёж/.codex/skills/.system/skill-creator/scripts/quick_validate.py godot-game-production
git diff --check
git status --short
```

Expected: zero test failures, `Skill is valid!`, no whitespace errors, and only intentional files listed.

- [ ] **Step 3: Review the final diff against the approved spec**

Check every acceptance criterion in `docs/superpowers/specs/2026-09-05-user-facing-visual-proposals-design.md`; inspect `git diff main...HEAD`; verify `rg -n "visual-decision/v1|CANONICAL_SCOPE_QUESTION|CANONICAL_TARGET_QUESTION" godot-game-production tests` returns no active contract usage.

- [ ] **Step 4: Integrate and push**

```powershell
git checkout main
git merge --ff-only feat/user-facing-visual-proposals
git push origin main
```

Expected: GitHub `main` advances to the verified feature tip.

- [ ] **Step 5: Refresh the installed copy and verify equality**

Use the `skill-installer` update workflow to replace only `C:\Users\Ёж\.codex\skills\godot-game-production`, then compare recursive relative-path SHA-256 manifests between the repository's `godot-game-production` directory and the installed directory. Expected: manifests are identical and the installed copy passes `quick_validate.py`.
