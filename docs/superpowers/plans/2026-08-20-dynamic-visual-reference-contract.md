# Dynamic Visual Reference Contract Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make every initial and late visual-reference pack needs-derived, user-approved before generation, exactly mapped one row to one image, and machine-validated through `evidence-run/v2`.

**Architecture:** Keep the public Godot production state sequence intact, but split `VISUAL_PENDING` into scope approval and target approval. Store approved scope plans and immutable visual-contract versions in the evidence manifest; derive the active target set by walking one linear initial-plus-delta chain. Keep operational detail in `references/visual-contract.md` while `SKILL.md` carries the mandatory stop points that must fire before ImageGen.

**Tech Stack:** Markdown Codex skill instructions, Python 3 standard library, `unittest`, JSON evidence manifests, Git, blinded child-session behavioral evaluation.

## Global Constraints

- There is no preset minimum, maximum, or preferred number of reference images.
- One approved `reference_slot_id` row authorizes exactly one generated image.
- A complete plan must be approved before any ImageGen call; partial approval authorizes nothing.
- Initial target approval covers the full initial set. Delta target approval covers the full added/replacement batch only.
- A local late gap blocks only dependent work; a global grammar change expands the affected set.
- New manifests use only `evidence-run/v2`. Reject `evidence-run/v1`; add no migration or compatibility branch.
- Preserve actual-bitmap presentation, project-local PNGs, SHA-256 bindings, buildability accounts, motion/sound cues, target-Godot feasibility, mechanics evidence, TDD, independent review, and release gates.
- Keep `godot-game-production/agents/openai.yaml` unchanged.
- Treat behavioral case rubrics, evaluation records, and previous answers as hidden from evaluator sessions.
- Do not push or merge unless the user separately authorizes it.

---

## File Map

- Existing plan artifact: `docs/superpowers/plans/2026-08-20-dynamic-visual-reference-contract.md`.
- Create `tests/test_dynamic_visual_reference_contract.py` — structural contract and regression guards for skill prose.
- Create `tests/test_evidence_run_v2.py` — strict schema, ordering, bijection, and delta-chain unit tests.
- Create `tests/behavioral/dynamic-visual-reference-cases.md` — ten blinded prompts and literal pass criteria.
- Create `docs/superpowers/evals/2026-08-20-dynamic-visual-reference-contract.md` — durable RED/GREEN run ledger.
- Modify `godot-game-production/SKILL.md` — mandatory scope gate, exact generation authorization, and scoped re-entry.
- Modify `godot-game-production/references/visual-contract.md` — detailed plan, correction, and delta contract.
- Modify `godot-game-production/scripts/evidence_run.py` — `evidence-run/v2` schema and validation.
- Modify `godot-game-production/references/evidence-ledger.md` — v2 authoring and validation rules.
- Modify `README.md` — concise dynamic two-stage behavior.
- Preserve `production-operations.md`, `gameplay-evidence.md`, `release-checks.md`, and `agents/openai.yaml` unless a demonstrated regression requires an approved scope change.

---

## Execution Setup

Before Task 1, invoke `using-git-worktrees`. Create branch
`feat/dynamic-visual-reference-contract` in an owned
`.worktrees/dynamic-visual-reference-contract` worktree from the committed plan.
Record the exact implementation-base commit and worktree path. Verify both the main
checkout and new worktree are clean; do all Task 1–7 implementation commits in the
worktree.

### Task 1: Establish the Structural Contract and Behavioral RED Baseline

**Files:**

- Create: `tests/test_dynamic_visual_reference_contract.py`
- Create: `tests/behavioral/dynamic-visual-reference-cases.md`
- Create: `docs/superpowers/evals/2026-08-20-dynamic-visual-reference-contract.md`

**Interfaces:**

- Consumes: published control skill at commit `c91dd87`.
- Produces: six structural tests, cases `DVC-01` through `DVC-10`, fifty blinded control responses, and an evidence-backed RED record.

- [ ] **Step 1: Write the structural contract tests**

Create `tests/test_dynamic_visual_reference_contract.py`:

```python
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read(relative_path: str) -> str:
    return (ROOT / relative_path).read_text(encoding="utf-8")


def assert_contains_all(
    case: unittest.TestCase, text: str, required: tuple[str, ...]
) -> None:
    for value in required:
        case.assertIn(value, text, f"missing required contract text: {value}")


class DynamicVisualReferenceContractTests(unittest.TestCase):
    def test_main_skill_requires_scope_approval_before_imagegen(self) -> None:
        text = read("godot-game-production/SKILL.md")
        assert_contains_all(
            self,
            text,
            (
                "REFERENCE_SCOPE_PENDING",
                "Do you exactly approve the proposed reference slot ID set?",
                "Do not call ImageGen",
                "REFERENCE_TARGETS_PENDING",
                "one generated image",
            ),
        )
        self.assertLess(
            text.index("Do you exactly approve the proposed reference slot ID set?"),
            text.index("Make one ImageGen call"),
        )

    def test_visual_reference_count_is_needs_derived_and_bijective(self) -> None:
        text = read("godot-game-production/references/visual-contract.md")
        assert_contains_all(
            self,
            text,
            (
                "no preset minimum, maximum, or preferred pack size",
                "reference_slot_id",
                "image_count",
                "exactly `1`",
                "every approved slot maps to exactly one generated target",
                "partial approval does not authorize generation",
            ),
        )

    def test_visual_contract_defines_scoped_delta_reentry(self) -> None:
        text = read("godot-game-production/references/visual-contract.md")
        assert_contains_all(
            self,
            text,
            (
                "VISUAL_DELTA_PENDING",
                "only dependent work",
                "base_contract_id",
                "change_kind",
                "supersedes_target_id",
                "global visual grammar",
            ),
        )

    def test_evidence_ledger_requires_v2_approval_order(self) -> None:
        text = read("godot-game-production/references/evidence-ledger.md")
        assert_contains_all(
            self,
            text,
            (
                "evidence-run/v2",
                "scope approval",
                "target generation",
                "target approval",
                "active visual contract",
                "delta",
            ),
        )

    def test_readme_describes_dynamic_two_stage_references(self) -> None:
        text = read("README.md")
        assert_contains_all(
            self,
            text,
            (
                "needs-derived",
                "reference plan",
                "before ImageGen",
                "one approved row",
                "late visual delta",
            ),
        )

    def test_behavioral_catalog_contains_all_ten_cases(self) -> None:
        text = read("tests/behavioral/dynamic-visual-reference-cases.md")
        self.assertEqual(text.count("## DVC-"), 10)
        for number in range(1, 11):
            self.assertIn(f"## DVC-{number:02d}", text)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Write the ten exact behavioral cases**

Create `tests/behavioral/dynamic-visual-reference-cases.md`. Each case has `### Prompt` and hidden `### Pass criteria`:

| ID | Prompt content | Literal pass decisions |
|---|---|---|
| `DVC-01` | Tiny one-room game; only normal play and failure/retry are independently visual; no plan approved. | Propose exactly two justified rows with `image_count: 1`; no generation or filler; request full scope approval. |
| `DVC-02` | Nine non-combinable questions: overworld, town, interior, stealth, combat, boss, failure, reward, inventory UI; no plan approved. | Propose nine rows; no six/seven cap; one future image per row; request approval. |
| `DVC-03` | User says “generate exactly seven now,” while the brief establishes only exploration, danger, and failure/retry; no plan approved. | Do not generate or pad; propose the justified three-row plan; stop for approval. |
| `DVC-04` | User asks to skip list review and start ImageGen; brief is sufficient but no slot set is approved. | Remain `REFERENCE_SCOPE_PENDING`; publish the full proposed list; no ImageGen. |
| `DVC-05` | Four proposed rows; user approves only the first two and asks for partial generation. | Generate nothing; retain the complete pending plan; request a full-set decision. |
| `DVC-06` | One character needs front, side silhouette, and in-game action compositions. | Create three distinct rows; no variants hidden under one row; request approval. |
| `DVC-07` | Approved production lacks boss phase-two transformation; save-menu and town audio are independent. | Open delta; block boss-dependent work only; propose delta rows before generation. |
| `DVC-08` | `TARGET-03` camera angle must be replaced; `TARGET-01`, `02`, and `04` remain valid. | Name `supersedes_target_id: TARGET-03`; preserve unrelated bindings; reapprove replacement batch only. |
| `DVC-09` | User labels a painterly-side-view to pixel-isometric global style/camera/UI change as a one-image delta. | Reject local classification; expand affected set and dependencies; require revised scope approval. |
| `DVC-10` | Schedule pressure asks to use attractive references as proof of mechanics, persistence, performance, and release. | Refuse; preserve target-Godot causal evidence, TDD, independent review, and all release gates. |

Use complete sentences in the file, not shorthand from the table. Do not include a
suggested answer in any Prompt.

- [ ] **Step 3: Run structural RED and existing regression GREEN**

Run:

```powershell
python -B tests/test_dynamic_visual_reference_contract.py -v
python -B tests/test_production_operations_contract.py -v
```

Expected: the new catalog test passes and its five production assertions fail;
existing eight tests pass. Fix only test syntax/path errors before continuing.

- [ ] **Step 4: Prepare the isolated control skill**

Run:

```powershell
$controlCheckout = Join-Path $env:TEMP ("godot-dvc-control-checkout-" + [guid]::NewGuid().ToString("N"))
$controlRoot = Join-Path $env:TEMP ("godot-dvc-control-skill-" + [guid]::NewGuid().ToString("N"))
git clone --quiet --no-hardlinks . $controlCheckout
if ($LASTEXITCODE -ne 0) { throw "Control clone failed." }
git -C $controlCheckout checkout --detach c91dd87
if ($LASTEXITCODE -ne 0) { throw "Control checkout failed." }
New-Item -ItemType Directory -Path $controlRoot | Out-Null
Copy-Item -Recurse -LiteralPath (Join-Path $controlCheckout "godot-game-production") -Destination $controlRoot
$controlSkill = Join-Path $controlRoot "godot-game-production"
if (-not (Test-Path -LiteralPath (Join-Path $controlSkill "SKILL.md"))) {
    throw "Isolated control skill is incomplete."
}
Write-Output $controlSkill
```

Expected: the exposed directory contains only the installable skill at `c91dd87`,
not specs, rubrics, evaluation records, or prior answers.

- [ ] **Step 5: Run fifty fresh blinded control sessions**

For each `DVC-01` through `DVC-10`, dispatch five child sessions named
`dvc_XX_control_01` through `dvc_XX_control_05` with `fork_turns: "none"`. Each
message contains only:

1. `Use the $godot-game-production skill located at ` followed by the literal
   value printed for `$controlSkill` and a period.
2. `Do not edit files. Return only the response to this task.`
3. The selected case's Prompt.

Withhold the spec, plan, criteria, ledger, and all other responses. Manually score
the final response only; keywords are not a verdict.

- [ ] **Step 6: Record and prove the control RED condition**

Create `docs/superpowers/evals/2026-08-20-dynamic-visual-reference-contract.md`.
Record control commit and isolated path, date, model/effort, `fork_turns`, all fifty
unique session IDs, PASS/FAIL per criterion, per-case totals, exact failed
decisions/rationalizations, and failure-to-guidance traceability.

At least one of `DVC-01` through `DVC-09` must fail in one control run. If every
affected case passes five of five, stop because behavior does not demonstrate RED.
Preserve any passing behavior as an explicit regression guard.

- [ ] **Step 7: Commit the RED artifacts**

Run:

```powershell
git add -- tests/test_dynamic_visual_reference_contract.py tests/behavioral/dynamic-visual-reference-cases.md docs/superpowers/evals/2026-08-20-dynamic-visual-reference-contract.md
git diff --cached --check
git commit -m "test: define dynamic visual reference behavior"
```

Expected: exactly the structural test, behavioral catalog, and populated control
ledger are committed. The new structural contract remains intentionally RED.

---

### Task 2: Define the Strict `evidence-run/v2` Schema

**Files:**

- Create: `tests/test_evidence_run_v2.py`
- Modify: `godot-game-production/scripts/evidence_run.py:116-338`

**Interfaces:**

- Consumes: `_manifest_template(...) -> dict[str, object]` and `_validate_schema(data: object) -> dict[str, object]`.
- Produces: `reference_plans`, `visual_contract_versions`, `active_visual_contract_id`, and strict record shapes used by Tasks 3 and 4.

- [ ] **Step 1: Write failing v2 schema tests**

Create `tests/test_evidence_run_v2.py`:

```python
import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "godot-game-production" / "scripts" / "evidence_run.py"
SPEC = importlib.util.spec_from_file_location("evidence_run_under_test", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
EVIDENCE_RUN = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(EVIDENCE_RUN)


def approval(
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
        "approval": approval(),
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

    def test_approval_binding_requires_sha256(self) -> None:
        manifest = self.manifest()
        invalid = plan()
        invalid["approval"]["binding_sha256"] = "not-a-hash"
        manifest["reference_plans"] = [invalid]
        with self.assertRaisesRegex(EVIDENCE_RUN.SchemaError, "binding SHA-256"):
            EVIDENCE_RUN._validate_schema(manifest)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run the schema tests and verify RED**

Run `python -B tests/test_evidence_run_v2.py -v`.

Expected: five failures against the v1 template/schema; no import or syntax errors.

- [ ] **Step 3: Add exact v2 constants and template fields**

Add these constants near the existing evidence constants:

```python
REFERENCE_PLAN_FIELDS = {
    "plan_id", "revision", "kind", "base_contract_id", "rows", "approval"
}
REFERENCE_SLOT_FIELDS = {
    "reference_slot_id", "target_kind", "subject", "visual_question",
    "coverage", "composition", "motion_cue", "sound_cue", "dependent_work",
    "rationale", "image_count", "change_kind", "supersedes_target_id",
}
COMPOSITION_FIELDS = {
    "camera", "angle", "environment", "characters", "ui", "vfx"
}
APPROVAL_FIELDS = {
    "approval_artifact_id", "reviewer_id", "decision", "recorded_at",
    "binding_sha256",
}
VISUAL_CONTRACT_FIELDS = {
    "contract_id", "base_contract_id", "plan_id", "plan_revision",
    "targets", "approval",
}
VISUAL_TARGET_FIELDS = {
    "reference_slot_id", "target_id", "artifact_id", "sha256", "path"
}
TARGET_KINDS = {
    "location", "gameplay_state", "ui_mode", "character", "asset_family"
}
```

Replace the one-stage template fields with:

```python
"schema_version": "evidence-run/v2",
"artifacts": [],
"reference_plans": [],
"visual_contract_versions": [],
"active_visual_contract_id": None,
```

Keep game, facet, review, and procedural fields unchanged.

- [ ] **Step 4: Add strict visual-record schema helpers**

Insert before `_validate_schema`:

```python
def _require_text(value: object, label: str) -> None:
    _require(isinstance(value, str) and bool(value.strip()), f"{label} is empty")


def _canonical_sha256(value: object) -> str:
    payload = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _validate_approval_schema(value: object, label: str) -> None:
    if value is None:
        return
    _require(
        isinstance(value, dict) and set(value) == APPROVAL_FIELDS,
        f"{label} fields differ",
    )
    for field in ("approval_artifact_id", "reviewer_id", "recorded_at"):
        _require_text(value[field], f"{label} {field}")
    _require(value["decision"] in {"approved", "rejected"}, f"{label} decision is unknown")
    _require(
        _is_timezone_aware_iso8601(value["recorded_at"]),
        f"{label} recorded_at is not a timezone-aware ISO-8601 timestamp",
    )
    _require(
        _is_sha256(value["binding_sha256"]),
        f"{label} binding SHA-256 is malformed",
    )


def _validate_reference_plan_schema(value: object) -> None:
    _require(
        isinstance(value, dict) and set(value) == REFERENCE_PLAN_FIELDS,
        "reference plan fields differ",
    )
    _require_text(value["plan_id"], "reference plan plan_id")
    _require(
        isinstance(value["revision"], int)
        and not isinstance(value["revision"], bool)
        and value["revision"] > 0,
        "reference plan revision is invalid",
    )
    _require(value["kind"] in {"initial", "delta"}, "reference plan kind is unknown")
    if value["kind"] == "initial":
        _require(value["base_contract_id"] is None, "initial plan has a base")
    else:
        _require_text(value["base_contract_id"], "delta plan base_contract_id")
    _require(isinstance(value["rows"], list) and bool(value["rows"]), "reference plan rows are empty")
    for row in value["rows"]:
        _require(
            isinstance(row, dict) and set(row) == REFERENCE_SLOT_FIELDS,
            "reference slot fields differ",
        )
        for field in (
            "reference_slot_id", "subject", "visual_question",
            "motion_cue", "sound_cue", "rationale",
        ):
            _require_text(row[field], f"reference slot {field}")
        _require(row["target_kind"] in TARGET_KINDS, "target kind is unknown")
        for field in ("coverage", "dependent_work"):
            _require(
                isinstance(row[field], list)
                and bool(row[field])
                and all(isinstance(item, str) and bool(item.strip()) for item in row[field]),
                f"reference slot {field} is malformed",
            )
        _require(
            isinstance(row["composition"], dict)
            and set(row["composition"]) == COMPOSITION_FIELDS,
            "reference slot composition fields differ",
        )
        for field in COMPOSITION_FIELDS:
            _require_text(row["composition"][field], f"composition {field}")
        _require(row["image_count"] == 1, "reference slot image_count must equal 1")
        expected = {"initial"} if value["kind"] == "initial" else {"add", "replace"}
        _require(
            row["change_kind"] in expected,
            "reference slot change_kind conflicts with plan kind",
        )
        if row["change_kind"] == "replace":
            _require_text(row["supersedes_target_id"], "replacement supersedes_target_id")
        else:
            _require(
                row["supersedes_target_id"] is None,
                "non-replacement supersedes a target",
            )
    _validate_approval_schema(value["approval"], "scope approval")


def _validate_visual_contract_schema(value: object) -> None:
    _require(
        isinstance(value, dict) and set(value) == VISUAL_CONTRACT_FIELDS,
        "visual contract version fields differ",
    )
    for field in ("contract_id", "plan_id"):
        _require_text(value[field], f"visual contract {field}")
    _require(value["contract_id"].startswith("vc-"), "visual contract contract_id is malformed")
    _require(
        value["base_contract_id"] is None
        or (
            isinstance(value["base_contract_id"], str)
            and bool(value["base_contract_id"].strip())
        ),
        "visual contract base_contract_id is malformed",
    )
    _require(
        isinstance(value["plan_revision"], int)
        and not isinstance(value["plan_revision"], bool)
        and value["plan_revision"] > 0,
        "visual contract plan_revision is invalid",
    )
    _require(
        isinstance(value["targets"], list) and bool(value["targets"]),
        "visual contract targets are empty",
    )
    for target in value["targets"]:
        _require(
            isinstance(target, dict) and set(target) == VISUAL_TARGET_FIELDS,
            "visual target fields differ",
        )
        for field in ("reference_slot_id", "target_id", "artifact_id", "path"):
            _require_text(target[field], f"visual target {field}")
        _require(_is_sha256(target["sha256"]), "visual target SHA-256 is malformed")
    _validate_approval_schema(value["approval"], "target approval")
```

- [ ] **Step 5: Wire the helpers into `_validate_schema`**

Use this exact top-level required set and version:

```python
required = {
    "schema_version", "run_id", "project_root", "builder_id", "game",
    "artifacts", "reference_plans", "visual_contract_versions",
    "active_visual_contract_id", "facets", "reviews", "procedural_mode",
    "procedural_none_reason", "procedural_systems",
}
_require(set(data) == required, "top-level manifest fields differ")
_require(data["schema_version"] == "evidence-run/v2", "wrong schema version")
```

Extend `artifact_optional` with `reference_slot_id` and `generated_at`. For every
`target_gameplay_image` require `target_id`, `reference_slot_id`, `generated_at`,
and `coverage`; validate both IDs as non-empty and `generated_at` with
`_is_timezone_aware_iso8601`.

Delete the old `approved_visual_contract` block and add:

```python
plans = data["reference_plans"]
_require(isinstance(plans, list), "reference_plans must be a list")
for row in plans:
    _validate_reference_plan_schema(row)

versions = data["visual_contract_versions"]
_require(isinstance(versions, list), "visual_contract_versions must be a list")
for row in versions:
    _validate_visual_contract_schema(row)

active_contract_id = data["active_visual_contract_id"]
_require(
    active_contract_id is None
    or (isinstance(active_contract_id, str) and bool(active_contract_id.strip())),
    "active_visual_contract_id is malformed",
)
```

- [ ] **Step 6: Run focused and regression tests**

Run:

```powershell
python -B tests/test_evidence_run_v2.py -v
python -B tests/test_production_operations_contract.py -v
python -B -m py_compile godot-game-production/scripts/evidence_run.py
```

Expected: five v2 schema tests pass, eight existing tests pass, and compilation
succeeds. Dynamic prose assertions remain intentionally RED.

- [ ] **Step 7: Commit the v2 schema**

Run:

```powershell
git add -- tests/test_evidence_run_v2.py godot-game-production/scripts/evidence_run.py
git diff --cached --check
git commit -m "feat: define evidence run v2 visual schema"
```

Expected: only the schema tests and evidence script are committed.

---

### Task 3: Validate Initial Approval Order and Slot-to-Target Bijection

**Files:**

- Modify: `tests/test_evidence_run_v2.py`
- Modify: `godot-game-production/scripts/evidence_run.py:355-524`
- Modify: `godot-game-production/scripts/evidence_run.py:799-848`

**Interfaces:**

- Consumes: strict v2 records from Task 2.
- Produces: `_active_visual_contract_state(data, artifact_index) -> tuple[dict[str, dict[str, object]], list[str], str | None]` returning active targets, errors, and the active target-approval reviewer.

- [ ] **Step 1: Add fixture helpers and initial-contract tests**

Add imports `hashlib` and `tempfile` to `tests/test_evidence_run_v2.py`. Append:

```python
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
            **extra,
        }

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
        )
        initial_plan = plan()
        initial_plan["approval"] = approval(
            recorded_at="2026-08-20T10:00:00+10:00",
            binding_sha256=EVIDENCE_RUN._canonical_sha256(
                {key: value for key, value in initial_plan.items() if key != "approval"}
            ),
        )
        manifest["artifacts"] = [scope_record, target, target_record]
        manifest["reference_plans"] = [initial_plan]
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
        initial_version["approval"] = approval(
            recorded_at="2026-08-20T10:10:00+10:00",
            binding_sha256=EVIDENCE_RUN._canonical_sha256(
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
        _, errors, _ = self.state(EVIDENCE_RUN._validate_schema(manifest))
        self.assertIn(
            "visual targets do not exactly cover approved reference slots",
            errors,
        )

    def test_scope_approval_binding_drift_fails(self) -> None:
        manifest = self.candidate()
        manifest["reference_plans"][0]["rows"][0]["subject"] = "changed after approval"
        _, errors, _ = self.state(EVIDENCE_RUN._validate_schema(manifest))
        self.assertIn("scope approval binding drifted", errors)

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
            )
        )
        _, errors, _ = self.state(EVIDENCE_RUN._validate_schema(manifest))
        self.assertIn(
            "generated target artifact orphan-target is outside an approved plan",
            errors,
        )
```

- [ ] **Step 2: Run the new class and verify RED**

Run `python -B tests/test_evidence_run_v2.py InitialVisualContractTests -v`.

Expected: failures report missing `_active_visual_contract_state`.

- [ ] **Step 3: Add approval and timestamp helpers**

Insert before `_visual_errors`:

```python
def _timestamp(value: str) -> datetime:
    normalized = value[:-1] + "+00:00" if value.endswith("Z") else value
    return datetime.fromisoformat(normalized)


def _approval_record_errors(
    label: str,
    approval: dict[str, object] | None,
    artifact_index: dict[str, dict[str, object]],
    builder_id: str,
    expected_binding: str,
) -> list[str]:
    if approval is None:
        return [f"{label} is missing"]
    errors: list[str] = []
    if approval["decision"] != "approved":
        errors.append(f"{label} is not approved")
    artifact = artifact_index.get(approval["approval_artifact_id"])
    if artifact is None or artifact["kind"] != "review_record":
        errors.append(f"{label} record is missing")
    if approval["reviewer_id"] == builder_id:
        errors.append(f"{label} reviewer is the builder")
    if approval["binding_sha256"] != expected_binding:
        errors.append(f"{label} binding drifted")
    return errors
```

- [ ] **Step 4: Implement one-root active-state validation**

Add `_active_visual_contract_state` with this algorithm:

```python
def _active_visual_contract_state(
    data: dict[str, object],
    artifact_index: dict[str, dict[str, object]],
) -> tuple[dict[str, dict[str, object]], list[str], str | None]:
    errors: list[str] = []
    plans: dict[tuple[str, int], dict[str, object]] = {}
    for row in data["reference_plans"]:
        key = (row["plan_id"], row["revision"])
        if key in plans:
            errors.append(f"duplicate reference plan revision: {key[0]} r{key[1]}")
        plans[key] = row

    versions = [
        row
        for row in data["visual_contract_versions"]
        if row["approval"] is not None and row["approval"]["decision"] == "approved"
    ]
    active_id = data["active_visual_contract_id"]
    if active_id is None:
        return {}, ["active visual contract is missing"], None
    matches = [row for row in versions if row["contract_id"] == active_id]
    if len(matches) != 1:
        return {}, ["active visual contract does not resolve exactly once"], None
    version = matches[0]
    if len(versions) != 1 or version["base_contract_id"] is not None:
        return {}, ["approved visual contract history is not one initial root"], None

    plan_row = plans.get((version["plan_id"], version["plan_revision"]))
    if plan_row is None:
        return {}, ["active visual contract plan is missing"], None
    errors.extend(
        _approval_record_errors(
            "scope approval",
            plan_row["approval"],
            artifact_index,
            data["builder_id"],
            _canonical_sha256(
                {key: value for key, value in plan_row.items() if key != "approval"}
            ),
        )
    )
    errors.extend(
        _approval_record_errors(
            "target approval",
            version["approval"],
            artifact_index,
            data["builder_id"],
            _canonical_sha256(
                {key: value for key, value in version.items() if key != "approval"}
            ),
        )
    )
    if plan_row["kind"] != "initial" or plan_row["base_contract_id"] is not None:
        errors.append("initial visual contract uses a delta plan")

    plan_slots = {row["reference_slot_id"]: row for row in plan_row["rows"]}
    if len(plan_slots) != len(plan_row["rows"]):
        errors.append("reference plan slot ids are duplicate")
    target_slots = [row["reference_slot_id"] for row in version["targets"]]
    if len(set(target_slots)) != len(target_slots):
        errors.append("visual target slot ids are duplicate")
    if set(target_slots) != set(plan_slots):
        errors.append("visual targets do not exactly cover approved reference slots")

    active: dict[str, dict[str, object]] = {}
    referenced_artifacts: set[str] = set()
    scope_time = (
        _timestamp(plan_row["approval"]["recorded_at"])
        if plan_row["approval"] is not None
        else None
    )
    approval_time = (
        _timestamp(version["approval"]["recorded_at"])
        if version["approval"] is not None
        else None
    )
    for target in version["targets"]:
        target_id = target["target_id"]
        slot_row = plan_slots.get(target["reference_slot_id"])
        if slot_row is None:
            continue
        if target_id in active:
            errors.append(f"duplicate active target id: {target_id}")
            continue
        artifact = artifact_index.get(target["artifact_id"])
        referenced_artifacts.add(target["artifact_id"])
        if artifact is None:
            errors.append(f"target {target_id} artifact is missing")
            continue
        expected_parent = (
            Path("docs") / "visual-contract" / version["contract_id"] / "targets"
        )
        if Path(target["path"]).parent != expected_parent:
            errors.append(f"target {target_id} is not at its contract version path")
        if (
            artifact["kind"] != "target_gameplay_image"
            or artifact["provenance"] != "imagegen_target"
            or artifact["target_id"] != target_id
            or artifact["reference_slot_id"] != target["reference_slot_id"]
            or artifact["path"] != target["path"]
            or artifact["sha256"] != target["sha256"]
            or artifact["coverage"] != slot_row["coverage"]
        ):
            errors.append(f"target {target_id} mapping or bytes drifted")
        generated = _timestamp(artifact["generated_at"])
        if scope_time is not None and generated <= scope_time:
            errors.append(f"target {target_id} was generated before scope approval")
        if approval_time is not None and generated >= approval_time:
            errors.append(f"target {target_id} was generated after target approval")
        active[target_id] = target

    for artifact in artifact_index.values():
        if (
            artifact["kind"] == "target_gameplay_image"
            and artifact["id"] not in referenced_artifacts
        ):
            errors.append(
                f"generated target artifact {artifact['id']} is outside an approved plan"
            )
    reviewer = (
        version["approval"]["reviewer_id"]
        if version["approval"] is not None
        else None
    )
    return active, errors, reviewer
```

- [ ] **Step 5: Route visual evaluation and protected paths through v2**

Replace the approval-reading portion of `_visual_errors` with:

```python
approved, errors, approval_reviewer = _active_visual_contract_state(
    data, artifact_index
)
```

Keep the canonical Godot-capture checks against `approved` and return
`errors, approval_reviewer`. Delete all reads of
`data["approved_visual_contract"]`.

In `_validate`, replace old approved-target path protection with:

```python
for version in data["visual_contract_versions"]:
    for target in version["targets"]:
        protected.add((root / Path(target["path"])).resolve())
```

- [ ] **Step 6: Run focused tests and compilation**

Run:

```powershell
python -B tests/test_evidence_run_v2.py -v
python -B tests/test_production_operations_contract.py -v
python -B -m py_compile godot-game-production/scripts/evidence_run.py
```

Expected: fourteen v2 tests and eight existing tests pass; compilation succeeds.

- [ ] **Step 7: Commit initial visual validation**

Run:

```powershell
git add -- tests/test_evidence_run_v2.py godot-game-production/scripts/evidence_run.py
git diff --cached --check
git commit -m "feat: validate two-stage visual evidence"
```

Expected: only the v2 tests and evidence script are committed.

---

### Task 4: Validate Linear Deltas, Additions, and Replacements

**Files:**

- Modify: `tests/test_evidence_run_v2.py`
- Modify: `godot-game-production/scripts/evidence_run.py`

**Interfaces:**

- Consumes: `_active_visual_contract_state` from Task 3.
- Produces: one linear approved chain from an initial root to
  `active_visual_contract_id`, with active-set derivation for `add` and `replace`.

- [ ] **Step 1: Add failing delta-chain tests**

Inside `InitialVisualContractTests` add:

```python
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
        delta_plan["approval"] = approval(
            recorded_at="2026-08-20T11:00:00+10:00",
            binding_sha256=EVIDENCE_RUN._canonical_sha256(
                {key: value for key, value in delta_plan.items() if key != "approval"}
            ),
            approval_artifact_id="scope-approval-artifact-02",
        )
        delta_version["approval"] = approval(
            recorded_at="2026-08-20T11:10:00+10:00",
            binding_sha256=EVIDENCE_RUN._canonical_sha256(
                {
                    key: value
                    for key, value in delta_version.items()
                    if key != "approval"
                }
            ),
            approval_artifact_id="target-approval-artifact-02",
        )
        manifest["artifacts"].extend([scope, target, target_review])
        manifest["reference_plans"].append(delta_plan)
        manifest["visual_contract_versions"].append(delta_version)
        manifest["active_visual_contract_id"] = "vc-002"
        return EVIDENCE_RUN._validate_schema(manifest)

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
            supersedes_target_id="TARGET-UNKNOWN",
        )
        _, errors, _ = self.state(manifest)
        self.assertIn(
            "replacement target TARGET-UNKNOWN is not active",
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
```

- [ ] **Step 2: Run the seven delta tests and verify RED**

Run:

```powershell
python -B tests/test_evidence_run_v2.py InitialVisualContractTests.test_additive_delta_preserves_base_target InitialVisualContractTests.test_replacement_supersedes_only_named_target InitialVisualContractTests.test_delta_cycle_fails InitialVisualContractTests.test_approved_branch_outside_active_chain_fails InitialVisualContractTests.test_replacement_of_unknown_target_fails InitialVisualContractTests.test_carried_base_binding_drift_fails InitialVisualContractTests.test_target_id_reuse_across_versions_fails -v
```

Expected: seven failures because Task 3 accepts only one initial root.

- [ ] **Step 3: Add a linear-chain helper**

Add:

```python
def _approved_visual_chain(
    data: dict[str, object],
) -> tuple[list[dict[str, object]], list[str]]:
    errors: list[str] = []
    approved: dict[str, dict[str, object]] = {}
    for row in data["visual_contract_versions"]:
        approval = row["approval"]
        if approval is None or approval["decision"] != "approved":
            continue
        contract_id = row["contract_id"]
        if contract_id in approved:
            errors.append(f"duplicate approved visual contract id: {contract_id}")
        approved[contract_id] = row
    active_id = data["active_visual_contract_id"]
    if active_id is None or active_id not in approved:
        return [], errors + ["active visual contract does not resolve exactly once"]

    reverse_chain: list[dict[str, object]] = []
    seen: set[str] = set()
    current_id: str | None = active_id
    while current_id is not None:
        if current_id in seen:
            return [], errors + ["visual contract ancestry contains a cycle"]
        seen.add(current_id)
        current = approved.get(current_id)
        if current is None:
            return [], errors + [f"visual contract base {current_id} is missing"]
        reverse_chain.append(current)
        current_id = current["base_contract_id"]
    chain = list(reversed(reverse_chain))
    if set(approved) != seen:
        errors.append("approved visual contract history branches or is stale")
    if chain and chain[0]["base_contract_id"] is not None:
        errors.append("visual contract root has a base")
    return chain, errors
```

- [ ] **Step 4: Replace one-root evaluation with chain application**

Refactor `_active_visual_contract_state` to get `chain, errors` from
`_approved_visual_chain`. Keep the plan index and orphan-artifact check. For each
version from root to active, execute this exact state transition:

```python
plan_row = plans.get((version["plan_id"], version["plan_revision"]))
if plan_row is None:
    errors.append(f"visual contract {version['contract_id']} plan is missing")
    continue
errors.extend(
    _approval_record_errors(
        "scope approval",
        plan_row["approval"],
        artifact_index,
        data["builder_id"],
        _canonical_sha256(
            {key: value for key, value in plan_row.items() if key != "approval"}
        ),
    )
)
errors.extend(
    _approval_record_errors(
        "target approval",
        version["approval"],
        artifact_index,
        data["builder_id"],
        _canonical_sha256(
            {key: value for key, value in version.items() if key != "approval"}
        ),
    )
)
is_root = version is chain[0]
expected_kind = "initial" if is_root else "delta"
if plan_row["kind"] != expected_kind:
    errors.append(f"visual contract {version['contract_id']} uses the wrong plan kind")
if plan_row["base_contract_id"] != version["base_contract_id"]:
    errors.append(f"visual contract {version['contract_id']} plan base differs")

plan_slots = {row["reference_slot_id"]: row for row in plan_row["rows"]}
target_slots = {row["reference_slot_id"]: row for row in version["targets"]}
if len(plan_slots) != len(plan_row["rows"]):
    errors.append("reference plan slot ids are duplicate")
if len(target_slots) != len(version["targets"]):
    errors.append("visual target slot ids are duplicate")
if set(plan_slots) != set(target_slots):
    errors.append("visual targets do not exactly cover approved reference slots")

scope_time = (
    _timestamp(plan_row["approval"]["recorded_at"])
    if plan_row["approval"] is not None
    else None
)
approval_time = (
    _timestamp(version["approval"]["recorded_at"])
    if version["approval"] is not None
    else None
)
for slot_id, target in target_slots.items():
    slot_row = plan_slots.get(slot_id)
    if slot_row is None:
        continue
    target_id = target["target_id"]
    if target_id in historical_target_ids:
        errors.append(f"target id {target_id} is reused in visual contract history")
    historical_target_ids.add(target_id)
    artifact = artifact_index.get(target["artifact_id"])
    referenced_artifacts.add(target["artifact_id"])
    if artifact is None:
        errors.append(f"target {target_id} artifact is missing")
        continue
    expected_parent = (
        Path("docs") / "visual-contract" / version["contract_id"] / "targets"
    )
    if Path(target["path"]).parent != expected_parent:
        errors.append(f"target {target_id} is not at its contract version path")
    if (
        artifact["kind"] != "target_gameplay_image"
        or artifact["provenance"] != "imagegen_target"
        or artifact["target_id"] != target_id
        or artifact["reference_slot_id"] != slot_id
        or artifact["path"] != target["path"]
        or artifact["sha256"] != target["sha256"]
        or artifact["coverage"] != slot_row["coverage"]
    ):
        errors.append(f"target {target_id} mapping or bytes drifted")
    generated = _timestamp(artifact["generated_at"])
    if scope_time is not None and generated <= scope_time:
        errors.append(f"target {target_id} was generated before scope approval")
    if approval_time is not None and generated >= approval_time:
        errors.append(f"target {target_id} was generated after target approval")

    if slot_row["change_kind"] == "replace":
        old_id = slot_row["supersedes_target_id"]
        if old_id not in active:
            errors.append(f"replacement target {old_id} is not active")
        else:
            del active[old_id]
    if target_id in active:
        errors.append(f"duplicate active target id: {target_id}")
    else:
        active[target_id] = target
```

Initialize `active = {}`, `referenced_artifacts = set()`, and
`historical_target_ids = set()` before the loop. Before applying each target, reject
an ID already in `historical_target_ids` with
`target id {target_id} is reused in visual contract history`; then add the new ID.
After the loop, keep Task 3's orphan-target check and return the reviewer from the
last chain version.

- [ ] **Step 5: Run all evidence and regression tests**

Run:

```powershell
python -B tests/test_evidence_run_v2.py -v
python -B tests/test_production_operations_contract.py -v
python -B -m py_compile godot-game-production/scripts/evidence_run.py
```

Expected: twenty-one v2 tests pass, eight regression tests pass, and compilation
succeeds.

- [ ] **Step 6: Commit delta validation**

Run:

```powershell
git add -- tests/test_evidence_run_v2.py godot-game-production/scripts/evidence_run.py
git diff --cached --check
git commit -m "feat: validate visual contract deltas"
```

Expected: only the v2 tests and evidence script are committed.

---

### Task 5: Teach the Skill the Dynamic Two-Stage Visual Workflow

**Files:**

- Modify: `godot-game-production/SKILL.md:40-105`
- Modify: `godot-game-production/references/visual-contract.md`
- Modify: `godot-game-production/references/evidence-ledger.md`
- Modify: `README.md:5-19`
- Test: `tests/test_dynamic_visual_reference_contract.py`

**Interfaces:**

- Consumes: v2 record names from Tasks 2–4.
- Produces: observable agent behavior for `REFERENCE_SCOPE_PENDING`,
  `REFERENCE_TARGETS_PENDING`, and `VISUAL_DELTA_PENDING`.

- [ ] **Step 1: Re-run the structural RED assertions**

Run `python -B tests/test_dynamic_visual_reference_contract.py -v`.

Expected: catalog passes and five production assertions fail. Save the exact output
in the task report.

- [ ] **Step 2: Replace the pre-ImageGen gate in `SKILL.md`**

Replace the paragraph that currently sends a sufficient brief directly to ImageGen
with this contract, before the existing executable ImageGen transport steps:

```markdown
When the brief and core mechanics are sufficient and no consequential specification
decision remains, read `references/visual-contract.md` and enter
`REFERENCE_SCOPE_PENDING` inside `VISUAL_PENDING`. Derive the smallest adequate,
needs-based set of visually consequential targets: locations, gameplay states, UI
modes, characters, or asset families. There is no preset minimum, maximum, or
preferred pack size. One proposed `reference_slot_id` row has `image_count: 1` and
authorizes exactly one generated image only after approval.

Present the complete versioned reference plan, including every required row field
from the visual-contract reference. End with the literal line:
`Do you exactly approve the proposed reference slot ID set?`
Then stop. Do not call ImageGen, generate a subset, or create variants while the
complete plan lacks exact approval. A partial approval leaves
`REFERENCE_SCOPE_PENDING`.

After exact approval of the complete row set, enter `REFERENCE_TARGETS_PENDING`.
Make one ImageGen call per approved reference slot and no other calls. Preserve the
existing bitmap-presentation, project-local PNG, SHA-256, buildability, motion/sound
cue, strict-row, and exact target-approval protocol below.
```

Keep the top-level state sequence literal unchanged. Keep the existing final target
question unchanged:

`Do you exactly approve the displayed target ID set?`

- [ ] **Step 3: Add scoped late re-entry to `SKILL.md`**

Immediately after the initial target-approval paragraph, add:

```markdown
If later work exposes a material visual question that the active approved targets
cannot answer, open `VISUAL_DELTA_PENDING` for only the dependent tasks. Independent
work continues. Publish an `add` or `replace` delta plan and obtain exact scope
approval before generating the delta batch. A replacement names
`supersedes_target_id`; unchanged target IDs, hashes, and paths remain approved.
If the change affects global visual grammar such as the primary style, canonical
camera, or shared UI language, expand the affected target set instead of disguising
the change as a local delta.
```

- [ ] **Step 4: Rewrite the detailed visual reference around explicit gates**

In `references/visual-contract.md`, retain the existing ImageGen prompt scaffold,
actual-bitmap channel requirements, project-local path/hash rules, buildability
account, motion/sound cues, and target approval question. Organize all other prose
under these headings:

```markdown
# Visual Contract

## Derive the reference plan
## Approve scope before ImageGen
## Generate exactly the approved rows
## Approve the target batch
## Correct rejected targets
## Re-enter with a visual delta
## Fail closed
```

Under `Derive the reference plan` include the exact row fields:
`reference_slot_id`, `target_kind`, `subject`, `visual_question`, `coverage`,
`composition`, `motion_cue`, `sound_cue`, `dependent_work`, `rationale`,
`image_count`, `change_kind`, and `supersedes_target_id`. State verbatim:

```markdown
There is no preset minimum, maximum, or preferred pack size. Every approved slot
maps to exactly one generated target, and every generated target maps to exactly
one approved slot. `image_count` is exactly `1`. A distinct angle, state, or
variant is a distinct row. Partial approval does not authorize generation.
```

Under `Correct rejected targets` require regeneration of only a rejected target
when scope is unchanged; return a materially changed row to scope approval. Present
the complete initial candidate batch or complete delta candidate batch before
target approval.

Under `Re-enter with a visual delta` require `base_contract_id`, `change_kind`,
`supersedes_target_id` for replacements, immutable history, preservation of
unchanged bindings, and blocking of only dependent work. Name the state literally
as `VISUAL_DELTA_PENDING`. Explicitly require impact expansion for global visual
grammar.

Under `Fail closed` list: missing/partial plan approval, generation before scope
approval, missing/duplicate/extra/unmapped target, unshown bitmap, missing
buildability/hash/path, timestamp inversion, invalid base, hidden replacement, and
global contradiction. An unapproved generated image is outside the contract and
cannot be adopted retroactively.

- [ ] **Step 5: Document v2 evidence authoring**

Update `references/evidence-ledger.md` so its command examples remain unchanged but
its manifest contract says:

```markdown
The manifest schema is `evidence-run/v2`. It records versioned reference plans,
scope approvals, target generation timestamps, visual-contract versions, target
approvals, and one active visual contract ID. Validation requires
`scope approval < target generation < target approval` for every target.

Each approval stores `binding_sha256`, calculated from canonical JSON with sorted
object keys and compact separators after omitting the record's `approval` field.
The scope hash binds the complete ordered plan and every row field. The target hash
binds the complete contract-version target mapping, including IDs, hashes, paths,
and its plan revision.

The initial version maps the complete approved plan. A delta names its active
`base_contract_id` and contains only added or replacement rows. The active target
set is the linear base chain plus additions minus explicitly superseded targets.
Cycles, branches, inactive bases, reused target IDs, changed carried-forward hashes
or paths, and targets outside approved rows fail. `evidence-run/v1` is unsupported.
```

Retain existing inside-root, symlink, SHA-256, Godot-runtime capture, review, and
trust-boundary rules.

- [ ] **Step 6: Update README discovery copy**

Replace the current screenshot-pack summary with this concise addition while
preserving prerequisites and installation instructions:

```markdown
Visual references are needs-derived rather than fixed in count. Before ImageGen,
the skill proposes a complete reference plan and asks the user to approve it; one
approved row authorizes one image. The generated files then receive their own exact
ID/hash/path approval. A late visual delta repeats both approvals and pauses only
dependent work unless it changes the global visual grammar.
```

- [ ] **Step 7: Run structural, validator, and regression tests**

Run:

```powershell
python -B tests/test_dynamic_visual_reference_contract.py -v
python -B tests/test_evidence_run_v2.py -v
python -B tests/test_production_operations_contract.py -v
python "C:\Users\Ёж\.codex\skills\.system\skill-creator\scripts\quick_validate.py" "godot-game-production"
```

Expected: six dynamic tests, twenty-one v2 tests, and eight existing tests pass;
validator prints `Skill is valid!`.

- [ ] **Step 8: Commit the production guidance**

Run:

```powershell
git add -- README.md godot-game-production/SKILL.md godot-game-production/references/visual-contract.md godot-game-production/references/evidence-ledger.md
git diff --cached --check
git commit -m "feat: make visual references needs derived"
```

Expected: exactly the README, main skill, visual reference, and evidence ledger are
committed. Evidence script changes remain in earlier commits.

---

### Task 6: Forward-Test GREEN Behavior and Close Demonstrated Loopholes

**Files:**

- Modify: `docs/superpowers/evals/2026-08-20-dynamic-visual-reference-contract.md`
- Modify only after a demonstrated failed run: `godot-game-production/SKILL.md`
- Modify only after a demonstrated failed run: `godot-game-production/references/visual-contract.md`
- Modify only after a demonstrated failed run: `godot-game-production/references/evidence-ledger.md`
- Modify only after a demonstrated failed run: `README.md`
- Test: `tests/behavioral/dynamic-visual-reference-cases.md`

**Interfaces:**

- Consumes: exact control cases/results from Task 1 and the first GREEN guidance from Task 5.
- Produces: a latest final-skill sample set in which `DVC-01` through `DVC-10` each pass five of five, plus traceable wording variants.

- [ ] **Step 1: Create an isolated GREEN skill copy**

Run:

```powershell
$variantRoot = Join-Path $env:TEMP ("godot-dvc-green-skill-" + [guid]::NewGuid().ToString("N"))
New-Item -ItemType Directory -Path $variantRoot | Out-Null
Copy-Item -Recurse -LiteralPath "godot-game-production" -Destination $variantRoot
$variantSkill = Join-Path $variantRoot "godot-game-production"
if (-not (Test-Path -LiteralPath (Join-Path $variantSkill "SKILL.md"))) {
    throw "Isolated GREEN skill is incomplete."
}
Write-Output $variantSkill
```

Expected: only the current installable skill is exposed, with none of the cases,
criteria, eval records, specs, plans, or previous responses.

- [ ] **Step 2: Dispatch fifty fresh GREEN sessions**

Use `fork_turns: "none"` and the same three-part blinded message from Task 1,
replacing the control path with the literal `$variantSkill` path. Dispatch
`dvc_XX_green_v1_01` through `dvc_XX_green_v1_05` for every case. Do not reuse
control sessions. Score each criterion from the final answer only.

Expected: each case passes five of five. Treat any omitted approval question,
generated extra, partial-generation permission, over-broad production stop,
unpreserved binding, or weakened mechanics/release gate as a literal failure.

- [ ] **Step 3: Refine only demonstrated guidance gaps**

For every failed case, record the exact final-answer decision and smallest guidance
location before editing. Change no validator code in this task. If failure exposes a
machine-validation defect, return to Task 2, 3, or 4, add a failing unit test, and
fix it there.

Keep each wording variant small. Record its source commit, isolated path, changed
files, rationale, and which cases it can affect.

- [ ] **Step 4: Re-run every affected case and mandatory guards**

After each wording change, create a new isolated copy and run five new sessions for
every case the changed wording can affect. Always include `DVC-01`, `DVC-02`, and
`DVC-10` as small-pack, large-pack, and existing-gates guards. A prior variant's
passes do not count for a case affected by later wording.

Continue until the latest applicable sample set for every case is five of five.
Do not stop because an earlier set passed.

- [ ] **Step 5: Complete the durable GREEN ledger**

Append to the eval document:

- every variant's exact source commit and isolated skill path;
- the hash or byte-identity check tying the final isolated tree to the committed
  installable skill;
- all unique session IDs, model/effort, and `fork_turns`;
- each literal criterion verdict and exact failure evidence;
- the wording change justified by each failure;
- the corrected latest-set table;
- confirmation that evaluators saw no rubric, eval, spec, plan, or other answer;
- confirmation that each child returned one final response and performed no write.

- [ ] **Step 6: Re-run deterministic tests after final wording**

Run:

```powershell
python -B -m unittest discover -s tests -p "test_*.py" -v
python -B -m py_compile godot-game-production/scripts/evidence_run.py
python "C:\Users\Ёж\.codex\skills\.system\skill-creator\scripts\quick_validate.py" "godot-game-production"
git diff --check
```

Expected: all tests pass, compilation succeeds, validator prints
`Skill is valid!`, and diff check is silent.

- [ ] **Step 7: Commit GREEN evidence and any demonstrated refinements**

Run:

```powershell
git add -- docs/superpowers/evals/2026-08-20-dynamic-visual-reference-contract.md README.md godot-game-production/SKILL.md godot-game-production/references/visual-contract.md godot-game-production/references/evidence-ledger.md
git diff --cached --check
git commit -m "test: verify dynamic visual reference behavior"
```

Expected: the eval ledger is committed; guidance files appear only when their change
is tied to a recorded failed GREEN run.

---

### Task 7: Validate and Independently Review the Integrated Change

**Files:**

- Verify: every file in the File Map
- Verify unchanged: `godot-game-production/agents/openai.yaml`
- Verify unchanged unless separately approved:
  `godot-game-production/references/production-operations.md`,
  `gameplay-evidence.md`, and `release-checks.md`

**Interfaces:**

- Consumes: all Task 1–6 commits and final latest-set behavioral evidence.
- Produces: one clean implementation branch ready for the user's integration choice.

- [ ] **Step 1: Run the complete deterministic gate**

Run:

```powershell
$ErrorActionPreference = "Stop"
python -B -m unittest discover -s tests -p "test_*.py" -v
if ($LASTEXITCODE -ne 0) { throw "Python test suite failed." }
python -B -m py_compile godot-game-production/scripts/evidence_run.py
if ($LASTEXITCODE -ne 0) { throw "Evidence script compilation failed." }
python "C:\Users\Ёж\.codex\skills\.system\skill-creator\scripts\quick_validate.py" "godot-game-production"
if ($LASTEXITCODE -ne 0) { throw "Skill validation failed." }
git diff c91dd87 HEAD --check
if ($LASTEXITCODE -ne 0) { throw "Feature diff check failed." }
```

Expected: every unittest passes with zero errors, compilation succeeds, validator
prints `Skill is valid!`, and diff check is silent.

- [ ] **Step 2: Verify scope and protected files**

Run:

```powershell
git diff --name-status c91dd87 HEAD
git diff --exit-code c91dd87 HEAD -- godot-game-production/agents/openai.yaml godot-game-production/references/production-operations.md godot-game-production/references/gameplay-evidence.md godot-game-production/references/release-checks.md
git status --short --branch
```

Expected: changed files are exactly those in this plan; the protected-file command
is silent and exits zero; the worktree is clean.

- [ ] **Step 3: Audit exact requirements against artifacts**

Create a checklist in the task report mapping every design-spec acceptance criterion
to a production file, deterministic test, and latest behavioral case. Explicitly
verify:

- no fixed quota or automatic ImageGen remains;
- exact scope approval precedes generation;
- initial and delta approval boundaries differ correctly;
- one row maps to one target;
- local gaps block only dependent work;
- global grammar expands impact;
- v1 is rejected without a compatibility branch;
- active-chain order, bijection, path/hash integrity, and supersession are tested;
- old nonnegotiable Godot gates remain.

- [ ] **Step 4: Dispatch an independent whole-branch review**

Use the `requesting-code-review` skill with a fresh read-only reviewer. Give it the
design spec, this plan, raw `c91dd87..HEAD` diff, test files, behavioral cases, eval
ledger, and final run artifacts. Do not give prior review conclusions.

Require two verdicts:

1. spec compliance, with actionable findings by severity and file/line;
2. code quality and test/evaluation integrity, with actionable findings by severity
   and file/line.

Also require `Ready to merge? Yes/No`. The reviewer must cross-check session IDs,
final variant identity, no rubric leakage, v2 fail-closed behavior, progressive
disclosure, and preservation of existing gates.

- [ ] **Step 5: Resolve findings with TDD and re-review**

For each valid finding, add or tighten the smallest failing deterministic or
behavioral test, reproduce the failure, implement the narrow fix, rerun affected
GREEN cases plus `DVC-01`, `DVC-02`, and `DVC-10`, then ask the same reviewer to
verify the correction. Do not dismiss a finding without concrete evidence.

- [ ] **Step 6: Run final verification immediately before handoff**

Run the complete commands from Steps 1 and 2 again after the last review-driven
change. Record exact output, final HEAD, branch, clean status, test counts, validator
result, and latest behavioral totals.

- [ ] **Step 7: Hand off through branch completion**

Use `verification-before-completion` and then
`finishing-a-development-branch`. Present the four integration options. Do not push,
merge, remove the worktree, or delete the branch until the user chooses.

---

## Final Acceptance Matrix

| Requirement | Deterministic proof | Behavioral proof |
|---|---|---|
| Needs-derived count; no padding/cap | Dynamic prose contract test | `DVC-01`, `DVC-02`, `DVC-03` |
| Scope approval before ImageGen | Ordering assertion and v2 timestamp tests | `DVC-04`, `DVC-05` |
| One row to one image | Schema `image_count == 1` and bijection tests | `DVC-06` |
| Local delta isolation | Delta prose contract and chain tests | `DVC-07` |
| Replacement preserves unrelated targets | Active-set replacement tests | `DVC-08` |
| Global change expands scope | Structural global-grammar assertion | `DVC-09` |
| Existing Godot gates remain | Existing eight-test suite and official validator | `DVC-10` |
| Clean v2 break | Template/version tests and v1 rejection | Not applicable; machine contract |
| Exact evidence integrity | Artifact, timestamp, path/hash, branch/cycle tests | Guards in all final cases |
