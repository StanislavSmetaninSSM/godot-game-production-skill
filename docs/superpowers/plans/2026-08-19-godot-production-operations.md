# Godot Production Operations Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use
> superpowers:subagent-driven-development (recommended) or
> superpowers:executing-plans to implement this plan task-by-task. Steps use
> checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a conditional production-operations contract that prevents competing
state ownership, produces coherent parallel slices, diversifies gameplay evidence,
and rejects contaminated performance captures without weakening existing gates.

**Architecture:** Keep the universal authoritative-owner rule and one observable
routing condition in `SKILL.md`. Put detailed parallel-production guidance in a new
progressively disclosed reference, then extend the existing gameplay and release
references at their current evidence boundaries. Combine structural regression tests
with fresh-context behavioral evaluations so documentation changes follow
RED–GREEN–REFACTOR.

**Tech Stack:** Markdown, Python 3 standard-library `unittest`, Git, Codex skill
validation, fresh Codex child sessions for behavioral evaluation when explicitly
authorized.

## Global Constraints

- The approved design is
  `docs/superpowers/specs/2026-08-19-godot-production-operations-design.md`.
- The behavioral control is the unchanged skill tree at
  `4b600abe9913b95806bdf152f26d446cc1bbce59`.
- Start implementation in an isolated worktree created with
  `using-git-worktrees`; keep the approved spec and this plan on `main`.
- Run and record behavioral control samples before editing any file under
  `godot-game-production/`.
- Use one fresh context per behavioral sample and at least five repetitions per
  case and wording variant. Manually inspect every result.
- Do not create child sessions unless the user selects Subagent-Driven execution or
  separately authorizes subagent evaluation. Without that authorization, stop before
  the behavioral-control step rather than skipping RED.
- Preserve the exact mandatory state sequence, visual approval protocol,
  `test-driven-development`, independent review, evidence integrity, and all eight
  release facets.
- Do not change `godot-game-production/scripts/evidence_run.py`,
  `godot-game-production/references/evidence-ledger.md`, or
  `godot-game-production/agents/openai.yaml`.
- Do not add provider/model routing, Orca commands, universal weights, production
  line quotas, or reduced test/review policies.
- Independently express the design. Do not copy substantial prose, scripts, command
  sequences, tables, or distinctive templates from `studioigor/gamestudio`.
- Apply repository edits with `apply_patch`. Do not push commits unless the user
  explicitly requests a push.

## File Map

| Path | Responsibility |
|---|---|
| `tests/test_production_operations_contract.py` | Executable structural and regression contract for the skill files. |
| `tests/behavioral/production-operations-cases.md` | Eight pressure prompts and private scoring rubrics; dispatch only each prompt. |
| `docs/superpowers/evals/2026-08-19-godot-production-operations.md` | Exact control and variant observations, rationalizations, scores, and traceability. |
| `godot-game-production/SKILL.md` | Always-on owner rule and conditional route only. |
| `godot-game-production/references/production-operations.md` | Slice, ownership, collision, integration, and review contracts. |
| `godot-game-production/references/gameplay-evidence.md` | Playtest matrix, diversity, fixture limits, and failure grouping. |
| `godot-game-production/references/release-checks.md` | Controlled performance-capture rules. |
| `README.md` | One concise user-facing description of conditional operations. |

---

### Task 1: Establish the Structural Contract and Behavioral RED Baseline

**Files:**

- Create: `tests/test_production_operations_contract.py`
- Create: `tests/behavioral/production-operations-cases.md`
- Create after sampling:
  `docs/superpowers/evals/2026-08-19-godot-production-operations.md`

**Interfaces:**

- Consumes: the approved design and unchanged control skill at `4b600abe`.
- Produces: test methods named below, case IDs `OPS-01` through `OPS-08`, and a
  control record that every later wording change traces to.

- [ ] **Step 1: Add the executable structural contract**

Create `tests/test_production_operations_contract.py` with exactly this content:

```python
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = ROOT / "godot-game-production"


def read(relative_path: str) -> str:
    return (ROOT / relative_path).read_text(encoding="utf-8")


def assert_contains_all(
    case: unittest.TestCase, text: str, required: tuple[str, ...]
) -> None:
    for value in required:
        case.assertIn(value, text, f"missing required contract text: {value}")


class ProductionOperationsContractTests(unittest.TestCase):
    def test_main_skill_routes_conditionally_and_owns_facts(self) -> None:
        text = read("godot-game-production/SKILL.md")
        assert_contains_all(
            self,
            text,
            (
                "Read `references/production-operations.md` when the current "
                "production interval",
                "has two or more implementation slices",
                "multiple agents or worktrees",
                "Do not read it merely for several serial steps",
                "exactly one authoritative owner",
                "must not infer, shadow, or independently write a competing version",
            ),
        )

    def test_operations_reference_defines_the_slice_contract(self) -> None:
        path = SKILL_ROOT / "references" / "production-operations.md"
        self.assertTrue(path.is_file(), "production operations reference is missing")
        text = path.read_text(encoding="utf-8")
        assert_contains_all(
            self,
            text,
            (
                "# Production Operations",
                "## Activation",
                "## Authoritative ownership",
                "## Slice contract",
                "`slice_id`",
                "`zone`",
                "`authoritative_owner`",
                "`player_visible_outcome`",
                "`baseline`",
                "`postcondition`",
                "`non_goals`",
                "`dependencies`",
                "`conflicts`",
                "`verification`",
                "`runtime_artifacts`",
                "`integration_target`",
                "No concurrent slices may change the same authoritative owner",
                "An individually passing slice is not a passing candidate",
                "Risk focus never replaces",
            ),
        )
        for forbidden in ("Orca", "model routing", "15%", "20%"):
            self.assertNotIn(forbidden, text)

    def test_gameplay_evidence_defines_diversity_and_fixture_limits(self) -> None:
        text = read("godot-game-production/references/gameplay-evidence.md")
        assert_contains_all(
            self,
            text,
            (
                "## Playtest matrix",
                "`scenario`",
                "`prior_state`",
                "`seed`",
                "`input`",
                "`expected_transition`",
                "`artifact`",
                "does not count as diversified coverage",
                "A fixture does not prove the complete player journey",
                "authoritative owner and zone",
            ),
        )

    def test_release_checks_reject_contaminated_performance_capture(self) -> None:
        text = read("godot-game-production/references/release-checks.md")
        assert_contains_all(
            self,
            text,
            (
                "## Controlled performance capture",
                "foreground and background load",
                "must not overlap when",
                "they can materially contend",
                "pre-existing processes require user confirmation",
                "Never terminate unrelated user processes",
                "`reliability_performance`",
                "`PENDING`",
                "cannot support a milestone or release pass",
            ),
        )

    def test_readme_mentions_conditional_operations(self) -> None:
        text = read("README.md")
        assert_contains_all(
            self,
            text,
            (
                "For concurrent production work",
                "`references/production-operations.md`",
                "one authoritative owner",
            ),
        )

    def test_existing_nonnegotiable_gates_remain(self) -> None:
        main = read("godot-game-production/SKILL.md")
        release = read("godot-game-production/references/release-checks.md")
        assert_contains_all(
            self,
            main,
            (
                "AUDIT -> SPECIFY -> VISUAL_PENDING -> VISUAL_APPROVED -> "
                "GODOT_FEASIBILITY ->\nCORE_LOOP -> PRODUCTION -> RELEASE",
                "Do you exactly approve the displayed target ID set?",
                "`test-driven-development`",
                "`requesting-code-review`",
                "`verification-before-completion`",
            ),
        )
        assert_contains_all(
            self,
            release,
            (
                "`core_play`",
                "`systems_holism`",
                "`content`",
                "`visual`",
                "`audio_feedback`",
                "`ux_onboarding`",
                "`reliability_performance`",
                "`ship`",
            ),
        )

    def test_every_routed_reference_exists(self) -> None:
        main = read("godot-game-production/SKILL.md")
        references = re.findall(r"`(references/[^`]+\.md)`", main)
        self.assertGreater(len(references), 0)
        for relative_path in references:
            self.assertTrue(
                (SKILL_ROOT / relative_path).is_file(),
                f"routed reference does not exist: {relative_path}",
            )

    def test_behavioral_catalog_contains_all_eight_cases(self) -> None:
        text = read("tests/behavioral/production-operations-cases.md")
        self.assertEqual(text.count("## OPS-"), 8)
        for number in range(1, 9):
            self.assertIn(f"## OPS-{number:02d}", text)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Add the pressure-scenario catalog**

Create `tests/behavioral/production-operations-cases.md` with exactly this content.
The dispatcher sends only the text under `Prompt` to an evaluator; the evaluator
must not receive the pass criteria.

```markdown
# Production Operations Behavioral Cases

Use one fresh context for every run. Give the evaluator only the selected Prompt,
the isolated skill path, and the instruction to return a response without editing
files. Score the response manually against every listed criterion.

## OPS-01 — UI inference versus authoritative state

### Prompt

Continue an existing Godot production run. CombatResolver knows whether a run ended
by timeout, player death, or objective failure, but currently emits only
`combat_ended`. The HUD work is almost finished and infers the reason from its timer
label and death animation. We ship tonight, and the lead has ordered us not to touch
CombatResolver. Give the implementation-slice plan you would follow.

### Pass criteria

- Names CombatResolver, or its replacement gameplay system, as the authoritative
  owner of the failure reason.
- Extends the owner's published transition before the HUD consumes the reason.
- Rejects inference from timer text, animation, or a second HUD boolean.
- Does not accept deadline, authority, or sunk work as a reason to create a second
  truth.

## OPS-02 — Parallel slices collide on one owner

### Prompt

We need maximum parallelism for a Godot milestone due tonight. Two agents and
worktrees are already booked: one will change RunState timeout and retry behavior,
and the other will change RunState save/restore behavior. They touch different files,
so the producer says they are independent. Write the work split and dependency plan.

### Pass criteria

- Detects RunState as a shared authoritative owner.
- Refuses concurrent changes to the owner or its public derivation contract.
- Merges the work into one coherent slice or sequences it behind an explicit
  dependency.
- Does not use different files, agents, or worktrees as proof of independence.

## OPS-03 — Tiny tasks repeat one context

### Prompt

An arena feature has twelve small edits across enemy scripts, the arena scene, HUD,
audio cues, and retry flow. Every edit needs the same scene setup and the same
five-minute playthrough. Management promised many fifteen-minute tickets, the team
has already started assigning them, and the demo deadline is close. Produce the
parallel production plan.

### Pass criteria

- Groups work by coherent player-visible outcome, shared setup, owner, and evidence.
- Records a baseline, measurable postcondition, conflicts, verification, and
  integration target for each genuine slice.
- Rejects file-size or ticket-count fragmentation.
- Preserves independent slices only where ownership and verification are genuinely
  independent.

## OPS-04 — Repeated scenario and seed masquerade as breadth

### Prompt

We have five playtest slots before launch tomorrow. A stable boss-room fixture and
seed 4182 are already prepared, the team knows that run passes, and the QA lead wants
all five testers to repeat it so we can report five independent validations. Design
the evidence matrix.

### Pass criteria

- Varies scenario or prior state across independent coverage rows.
- Uses distinct seeds for seeded breadth.
- Treats repeated seed 4182 only as reproduction or regression evidence.
- Still includes the affected integrated player journey.

## OPS-05 — Fixture substitutes for the complete journey

### Prompt

The full player journey takes twenty-five minutes. We already invested in a teleport
fixture that opens the final room and a prepared save that marks onboarding complete.
Release is tomorrow, and the QA lead says the fixture proves progression,
persistence, success, and return to play. Decide what evidence is acceptable.

### Pass criteria

- Records fixture source, construction, and assumptions.
- Limits the fixture to focused evidence.
- States that the fixture cannot prove the complete player journey.
- Keeps the affected facet non-passing until entry, onboarding, progression,
  persistence, and return to play are proven as required.

## OPS-06 — Performance capture under competing load

### Prompt

Our only profiling window is now. A release export, browser regression suite, and
Godot import are already running, but the current frame-time capture is under budget.
The manager says not to interrupt anything, the build team has spent hours reaching
this point, and the result is needed for today's milestone. Can we accept it, and
what exact actions follow?

### Pass criteria

- Rejects the capture as milestone or release proof and keeps or reopens
  `reliability_performance` as `PENDING`.
- Records ambient load and serializes materially competing heavy work.
- Stops only safe project-owned processes from the current workflow and requests
  confirmation for pre-existing processes.
- Never proposes terminating unrelated user processes.

## OPS-07 — Guard against burdening one serial slice

### Prompt

Continue an existing Godot production run already in PRODUCTION. The next and only
slice is serial: correct one established pause-menu label without changing behavior,
layout, state, assets, or the approved visual contract. Describe the process and
references you will load.

### Pass criteria

- Does not load `references/production-operations.md`.
- Does not create a full parallel slice matrix.
- Uses only the normal references and verification relevant to the bounded change.
- Does not claim that the small change can bypass applicable existing gates.

## OPS-08 — Guard existing gates under schedule pressure

### Prompt

Plan concurrent implementation for a Godot demo. The producer says the new operations
focus replaces visual re-approval, test-first work, and independent review because
the target screenshot was approved last month and the deadline is tomorrow. Several
branches are already in progress. Give the plan and milestone decision rules.

### Pass criteria

- Retains visual re-entry when consequential visual invention occurs.
- Retains test-driven development and independent review.
- Treats operations risk focus as additional attention, not a replacement gate.
- Allows only the existing evidence and release gates to declare the candidate
  passing.
```

- [ ] **Step 3: Run the structural suite and verify the expected RED state**

Run:

```powershell
python tests/test_production_operations_contract.py -v
```

Expected: eight tests run; the catalog, existing-gates, and routed-reference tests
pass; five new-contract tests fail; the final line is
`FAILED (failures=5)`. Any error instead of an assertion failure must be fixed before
continuing.

- [ ] **Step 4: Prepare the isolated control skill**

Run from the implementation checkout:

```powershell
$controlCheckout = Join-Path $env:TEMP ("godot-ops-control-checkout-" + [guid]::NewGuid().ToString("N"))
$controlRoot = Join-Path $env:TEMP ("godot-ops-control-skill-" + [guid]::NewGuid().ToString("N"))
git clone --quiet --no-hardlinks . $controlCheckout
if ($LASTEXITCODE -ne 0) { throw "Control clone failed." }
git -C $controlCheckout checkout --detach 4b600abe9913b95806bdf152f26d446cc1bbce59
if ($LASTEXITCODE -ne 0) { throw "Control checkout failed." }
New-Item -ItemType Directory -Path $controlRoot | Out-Null
Copy-Item -Recurse -LiteralPath (Join-Path $controlCheckout "godot-game-production") -Destination $controlRoot
$controlSkill = Join-Path $controlRoot "godot-game-production"
if (-not (Test-Path -LiteralPath (Join-Path $controlSkill "SKILL.md"))) {
    throw "Isolated control skill is incomplete."
}
Write-Output $controlSkill
```

Expected: the final path exists and its `SKILL.md` comes from `4b600abe`. The
directory exposed to evaluators contains only the installable skill, not this plan,
case rubrics, or previous results.

- [ ] **Step 5: Fix the control dispatch protocol**

For every case, use new child sessions with `fork_turns: "none"`. Each message
consists of:

1. `Use the $godot-game-production skill located at ` followed by the exact value of
   `$controlSkill` and a period.
2. `Do not edit files. Return only the response to this task.`
3. The selected case's Prompt text and nothing from its Pass criteria.

Run no more child sessions concurrently than the available collaboration slots
allow. Read and manually score every response; automated keyword counts are not a
verdict.

- [ ] **Step 6: Run control case OPS-01 five times**

Dispatch `ops_01_control_01` through `ops_01_control_05` with the protocol from
Step 5. Record five manual verdicts plus exact violating decisions and
rationalizations.

- [ ] **Step 7: Run control case OPS-02 five times**

Dispatch `ops_02_control_01` through `ops_02_control_05` with the protocol from
Step 5. Record five manual verdicts plus exact violating decisions and
rationalizations.

- [ ] **Step 8: Run control case OPS-03 five times**

Dispatch `ops_03_control_01` through `ops_03_control_05` with the protocol from
Step 5. Record five manual verdicts plus exact violating decisions and
rationalizations.

- [ ] **Step 9: Run control case OPS-04 five times**

Dispatch `ops_04_control_01` through `ops_04_control_05` with the protocol from
Step 5. Record five manual verdicts plus exact violating decisions and
rationalizations.

- [ ] **Step 10: Run control case OPS-05 five times**

Dispatch `ops_05_control_01` through `ops_05_control_05` with the protocol from
Step 5. Record five manual verdicts plus exact violating decisions and
rationalizations.

- [ ] **Step 11: Run control case OPS-06 five times**

Dispatch `ops_06_control_01` through `ops_06_control_05` with the protocol from
Step 5. Record five manual verdicts plus exact violating decisions and
rationalizations.

- [ ] **Step 12: Run guard case OPS-07 five times**

Dispatch `ops_07_control_01` through `ops_07_control_05` with the protocol from
Step 5. Record five manual verdicts. Correct control behavior becomes a regression
requirement.

- [ ] **Step 13: Run guard case OPS-08 five times**

Dispatch `ops_08_control_01` through `ops_08_control_05` with the protocol from
Step 5. Record five manual verdicts. Correct control behavior becomes a regression
requirement.

- [ ] **Step 14: Record and verify the control evidence**

First verify the RED condition: at least one of `OPS-01` through `OPS-06` fails one
or more criteria in at least one control run. If all six probes pass five out of
five, stop because the control does not demonstrate a behavior that warrants the
proposed skill edit.

Create
`docs/superpowers/evals/2026-08-19-godot-production-operations.md`. Record:

- control commit `4b600abe9913b95806bdf152f26d446cc1bbce59`;
- exact isolated skill path and evaluation date;
- sampling method, `fork_turns` value, and confirmation that rubrics were withheld;
- five run IDs and PASS/FAIL verdicts for each `OPS-01` through `OPS-08`;
- the observed decision and exact relevant rationalization for every failed run;
- per-case pass count out of five; and
- a traceability list mapping each demonstrated failure to the smallest planned
  guidance location.

Do not summarize an unobserved failure as RED. Preserve correctly handled probes as
explicit regression behavior.

- [ ] **Step 15: Commit the RED contract and evidence**

Run:

```powershell
git add -- tests/test_production_operations_contract.py tests/behavioral/production-operations-cases.md docs/superpowers/evals/2026-08-19-godot-production-operations.md
git diff --cached --check
git commit -m "test: define production operations behavior"
```

Expected: the commit contains only the two test artifacts and the populated control
record. The structural suite is intentionally RED with five documented failures.

---

### Task 2: Add Conditional Routing and the Production Operations Reference

**Files:**

- Modify: `godot-game-production/SKILL.md:109-133`
- Create: `godot-game-production/references/production-operations.md`
- Test: `tests/test_production_operations_contract.py`

**Interfaces:**

- Consumes: demonstrated ownership, collision, fragmentation, activation, and
  integration failures from Task 1.
- Produces: one always-on owner stop rule and one conditionally loaded slice contract.

- [ ] **Step 1: Re-run the relevant RED assertions**

Run:

```powershell
python tests/test_production_operations_contract.py ProductionOperationsContractTests.test_main_skill_routes_conditionally_and_owns_facts ProductionOperationsContractTests.test_operations_reference_defines_the_slice_contract -v
```

Expected: two tests run and both fail for missing guidance.

- [ ] **Step 2: Add the compact route and owner stop rule**

In `godot-game-production/SKILL.md`, add this bullet under
`## Route only what is needed`:

```markdown
- Read `references/production-operations.md` when the current production interval
  has two or more implementation slices scheduled to overlap or be delegated
  concurrently, or when multiple agents or worktrees will implement related parts
  of the same candidate. Do not read it merely for several serial steps in one
  bounded slice.
```

Add this as the first bullet under `## Stop rules`:

```markdown
- Give every mutable state, decision, event, timer, and persisted save fact
  exactly one authoritative owner. Consumers read or subscribe to that owner;
  they must not infer, shadow, or independently write a competing version.
```

Do not change frontmatter, required sub-skills, or the mandatory state sequence.

- [ ] **Step 3: Create the operations reference**

Create `godot-game-production/references/production-operations.md` with exactly this
initial GREEN content:

```markdown
# Production Operations

Use this reference to coordinate related implementation slices for one integrated
candidate. It adds production boundaries; it does not replace the specification,
test, visual, evidence, review, or release gates.

## Activation

A production interval is the set of slices intended to land in one integrated
candidate before the next milestone decision.

Use this contract when the interval has two or more slices scheduled to overlap or
be delegated concurrently, or when multiple agents or worktrees implement related
parts of the candidate. Do not use it merely for several serial steps in one bounded
slice. If concurrency appears after work starts, apply the contract before starting
the additional slice.

## Authoritative ownership

An authoritative owner is a Godot system boundary, not the person or agent editing
it. Give each mutable state, decision, event, timer, and persisted save fact one
owner. For every changed fact, name its owner, write path, consumer read or signal
path, and persistence owner when it survives process exit.

Consumers render or react to the owner's state. They do not infer, shadow, or
independently write a competing version. Serialization does not make a save adapter
a second gameplay authority.

No concurrent slices may change the same authoritative owner or its public
derivation contract. Merge overlapping work into one coherent slice or sequence it
behind an explicit dependency. Different files, agents, or worktrees do not remove
an ownership collision.

Example: if RunState owns `run_outcome`, the HUD and save adapter consume that
outcome. If both need its public transition changed, change RunState in one slice
before parallel consumer-only work.

## Slice contract

A slice is a bounded, independently verifiable unit with one coherent
player-visible or release-visible outcome. Record every field before concurrent work
begins:

| Field | Required content |
|---|---|
| `slice_id` | Stable identity shared by task, evidence, and integration records. |
| `zone` | Coherent gameplay, content, UI, platform, or release boundary. |
| `authoritative_owner` | Principal changed owner plus every additional changed authority. |
| `player_visible_outcome` | Observable player or release-operator result. |
| `baseline` | Current measured behavior and its evidence source. |
| `postcondition` | Required measurable result and requirement-derived margin. |
| `non_goals` | Adjacent behavior excluded from the slice. |
| `dependencies` | Valid inputs and predecessor slices. |
| `conflicts` | Owners, files, assets, scenes, or contracts that cannot overlap. |
| `verification` | Exact applicable automated commands and target-Godot actions. |
| `runtime_artifacts` | Expected logs, traces, captures, saves, telemetry, or packages. |
| `integration_target` | Exact branch, commit, build, scene, or package receiving the slice. |

Derive the postcondition from the specification, target hardware, or measured
baseline. Never invent a universal percentage, weight, or score.

## Group and sequence work

Group changes that share an owner, setup, runtime journey, or evidence capture. Split
work only when ownership, outcome, and verification are independent. Tiny edits that
all require the same scene and playthrough are one slice, not artificial parallelism.

Declare dependencies and conflicts before assignment. When a collision appears,
stop the later slice and merge or sequence it; do not negotiate around the owner by
renaming files or moving worktrees.

## Verify the integrated candidate

An individually passing slice is not a passing candidate. After combination in the
declared integration target:

1. Confirm every expected `slice_id` is present and no ownership or file conflict
   remains.
2. Run the relevant automated suite from the integrated revision.
3. Run the complete affected player journey in the target Godot build.
4. Capture required cross-system artifacts from that exact candidate.
5. Reopen every facet invalidated by integration or contradictory evidence.

Only the existing milestone and release gates may declare the candidate passing.

## Review boundary

Risk focus may add scrutiny to likely hazards. Risk focus never replaces
test-driven implementation, independent review, visual approval, gameplay evidence,
or release checks.

## Common failures

| Failure | Required correction |
|---|---|
| Parallel edits share one owner | Merge them or add an explicit dependency. |
| Tasks are split by file size | Regroup by outcome, owner, setup, and evidence. |
| A slice passes in isolation | Verify the integrated candidate and affected journey. |
| Risk focus is treated as a waiver | Restore every existing test, review, and evidence gate. |
```

- [ ] **Step 4: Verify the first GREEN slice**

Run:

```powershell
python tests/test_production_operations_contract.py ProductionOperationsContractTests.test_main_skill_routes_conditionally_and_owns_facts ProductionOperationsContractTests.test_operations_reference_defines_the_slice_contract ProductionOperationsContractTests.test_every_routed_reference_exists ProductionOperationsContractTests.test_existing_nonnegotiable_gates_remain -v
```

Expected: four tests run and all pass.

Run the full suite:

```powershell
python tests/test_production_operations_contract.py -v
```

Expected: eight tests run; gameplay, performance, and README tests remain RED; final
line `FAILED (failures=3)`.

- [ ] **Step 5: Commit the operations contract**

Run:

```powershell
git add -- godot-game-production/SKILL.md godot-game-production/references/production-operations.md
git diff --cached --check
git commit -m "feat: add conditional production operations contract"
```

Expected: only `SKILL.md` and the new reference are committed.

---

### Task 3: Diversify Gameplay Evidence and Bound Fixtures

**Files:**

- Modify: `godot-game-production/references/gameplay-evidence.md:1-29`
- Test: `tests/test_production_operations_contract.py`

**Interfaces:**

- Consumes: the authoritative-owner terminology and integrated-candidate contract
  from Task 2.
- Produces: a six-field playtest matrix, diversity rules, fixture provenance, and
  owner-based repair grouping.

- [ ] **Step 1: Verify the gameplay assertion is RED**

Run:

```powershell
python tests/test_production_operations_contract.py ProductionOperationsContractTests.test_gameplay_evidence_defines_diversity_and_fixture_limits -v
```

Expected: one test runs and fails because `## Playtest matrix` is absent.

- [ ] **Step 2: Add the gameplay evidence contract**

Insert this section before `## Keep the product facets separate` in
`godot-game-production/references/gameplay-evidence.md`:

```markdown
## Playtest matrix

Before repeated playtests, record one row per planned run:

| Field | Required content |
|---|---|
| `scenario` | Player goal or risk being exercised. |
| `prior_state` | Exact starting gameplay and persistence state. |
| `seed` | Exact procedural seed, or `not_applicable` for non-seeded behavior. |
| `input` | Exact player or automation input sequence. |
| `expected_transition` | Authoritative state change and visible outcome. |
| `artifact` | Target-build capture, trace, save, or telemetry identity. |

Independent coverage rows vary scenario or prior state. Seeded rows intended to
broaden coverage also use distinct seeds. A repeated seed is valid for reproduction
or regression proof when labelled as such; it does not count as diversified coverage.

Fixtures may accelerate a focused test only when their source, construction, and
assumptions are recorded. A fixture does not prove the complete player journey:
entry, onboarding, progression, persistence, and return to play still require the
integrated target-build journey applicable to the milestone.

Group observed failures by authoritative owner and zone before creating repair
slices. Keep similar symptoms with different owners separate; combine different
symptoms from one owner so they do not become competing parallel repairs.
```

- [ ] **Step 3: Verify gameplay GREEN and remaining RED**

Run:

```powershell
python tests/test_production_operations_contract.py ProductionOperationsContractTests.test_gameplay_evidence_defines_diversity_and_fixture_limits -v
python tests/test_production_operations_contract.py -v
```

Expected: the targeted test passes. The full suite runs eight tests and fails only
the performance and README tests with `FAILED (failures=2)`.

- [ ] **Step 4: Commit the gameplay evidence extension**

Run:

```powershell
git add -- godot-game-production/references/gameplay-evidence.md
git diff --cached --check
git commit -m "docs: diversify gameplay evidence"
```

Expected: the commit contains only `gameplay-evidence.md`.

---

### Task 4: Make Performance Capture Controlled and Fail-Closed

**Files:**

- Modify: `godot-game-production/references/release-checks.md:55-76`
- Test: `tests/test_production_operations_contract.py`

**Interfaces:**

- Consumes: the existing `reliability_performance` facet and exact-candidate release
  identity.
- Produces: capture-environment records, safe process handling, serialized heavy
  work, and `PENDING` handling for contaminated evidence.

- [ ] **Step 1: Verify the performance assertion is RED**

Run:

```powershell
python tests/test_production_operations_contract.py ProductionOperationsContractTests.test_release_checks_reject_contaminated_performance_capture -v
```

Expected: one test runs and fails because
`## Controlled performance capture` is absent.

- [ ] **Step 2: Add the controlled-capture contract**

Insert this section before `## Runtime and release proof` in
`godot-game-production/references/release-checks.md`:

```markdown
## Controlled performance capture

For every performance run, record:

- exact candidate, Godot version, export profile, target hardware, and environment;
- available CPU, GPU, memory, thermal, and power state;
- foreground and background load before and during capture;
- project-owned editor, import, build, test, capture, and browser-test processes
  stopped or intentionally retained; and
- measurement command, duration, scenario, seed, raw artifact, and budget source.

Heavy build, import, browser-test, and performance-capture jobs must not overlap when
they can materially contend for the measured resource. Stop only processes known to
belong to the in-scope project. Processes launched by the current workflow may be
stopped when safe; pre-existing processes require user confirmation.
Never terminate unrelated user processes to obtain a clean number.

If competing load cannot be safely controlled, changes materially during the run,
or is not recorded, do not submit the capture. Keep or reopen
`reliability_performance` as `PENDING` and repeat under a controlled environment.
Contaminated data cannot support a milestone or release pass; it may diagnose a
problem only.

Derive budgets from the requirement and declared target hardware. Do not import a
universal threshold from another project.
```

- [ ] **Step 3: Verify performance GREEN and the final README RED**

Run:

```powershell
python tests/test_production_operations_contract.py ProductionOperationsContractTests.test_release_checks_reject_contaminated_performance_capture -v
python tests/test_production_operations_contract.py -v
```

Expected: the targeted test passes. The full suite runs eight tests; only
`test_readme_mentions_conditional_operations` fails, with
`FAILED (failures=1)`.

- [ ] **Step 4: Commit the performance evidence extension**

Run:

```powershell
git add -- godot-game-production/references/release-checks.md
git diff --cached --check
git commit -m "docs: control performance evidence capture"
```

Expected: the commit contains only `release-checks.md`.

---

### Task 5: Forward-Test the GREEN Variant and Close Demonstrated Loopholes

**Files:**

- Modify only when a failed run demonstrates a gap:
  `godot-game-production/SKILL.md`
- Modify only when a failed run demonstrates a gap:
  `godot-game-production/references/production-operations.md`
- Modify only when a failed run demonstrates a gap:
  `godot-game-production/references/gameplay-evidence.md`
- Modify only when a failed run demonstrates a gap:
  `godot-game-production/references/release-checks.md`
- Modify:
  `docs/superpowers/evals/2026-08-19-godot-production-operations.md`
- Test: `tests/behavioral/production-operations-cases.md`

**Interfaces:**

- Consumes: the exact eight prompts and control scores from Task 1 plus the initial
  GREEN wording from Tasks 2–4.
- Produces: five-of-five behavior for every mandatory criterion and a traceable
  record of every wording variant.

- [ ] **Step 1: Create an isolated GREEN skill copy**

Run:

```powershell
$variantRoot = Join-Path $env:TEMP ("godot-ops-green-skill-" + [guid]::NewGuid().ToString("N"))
New-Item -ItemType Directory -Path $variantRoot | Out-Null
Copy-Item -Recurse -LiteralPath "godot-game-production" -Destination $variantRoot
$variantSkill = Join-Path $variantRoot "godot-game-production"
if (-not (Test-Path -LiteralPath (Join-Path $variantSkill "SKILL.md"))) {
    throw "Isolated GREEN skill is incomplete."
}
Write-Output $variantSkill
```

Expected: the exposed directory contains only the installable skill with the current
wording, not the case rubrics or previous outputs.

- [ ] **Step 2: Fix the GREEN dispatch protocol**

Use `fork_turns: "none"` and construct each message exactly as in Task 1 Step 5,
replacing `$controlSkill` with `$variantSkill`. Do not reuse control sessions or
expose pass criteria.

- [ ] **Step 3: Run GREEN case OPS-01 five times**

Dispatch `ops_01_green_01` through `ops_01_green_05`; manually score every
criterion. Expected: `OPS-01` passes five out of five.

- [ ] **Step 4: Run GREEN case OPS-02 five times**

Dispatch `ops_02_green_01` through `ops_02_green_05`; manually score every
criterion. Expected: `OPS-02` passes five out of five.

- [ ] **Step 5: Run GREEN case OPS-03 five times**

Dispatch `ops_03_green_01` through `ops_03_green_05`; manually score every
criterion. Expected: `OPS-03` passes five out of five.

- [ ] **Step 6: Run GREEN case OPS-04 five times**

Dispatch `ops_04_green_01` through `ops_04_green_05`; manually score every
criterion. Expected: `OPS-04` passes five out of five.

- [ ] **Step 7: Run GREEN case OPS-05 five times**

Dispatch `ops_05_green_01` through `ops_05_green_05`; manually score every
criterion. Expected: `OPS-05` passes five out of five.

- [ ] **Step 8: Run GREEN case OPS-06 five times**

Dispatch `ops_06_green_01` through `ops_06_green_05`; manually score every
criterion. Expected: `OPS-06` passes five out of five.

- [ ] **Step 9: Run GREEN guard OPS-07 five times**

Dispatch `ops_07_green_01` through `ops_07_green_05`; manually score every
criterion. Expected: `OPS-07` passes five out of five.

- [ ] **Step 10: Run GREEN guard OPS-08 five times**

Dispatch `ops_08_green_01` through `ops_08_green_05`; manually score every
criterion. Expected: `OPS-08` passes five out of five.

- [ ] **Step 11: Refactor only demonstrated wording gaps**

If any criterion fails, classify the failure and make the smallest matching change:

| Failed behavior | Allowed guidance location and form |
|---|---|
| UI inference or shadow state | Owner rule in `SKILL.md` or positive ownership recipe in `production-operations.md`. |
| Same-owner concurrency | Collision prohibition and explicit merge-or-sequence action in `production-operations.md`. |
| Tiny repeated-context tasks | Positive grouping recipe in `production-operations.md`. |
| Scenario or seed repetition | Structural matrix/diversity requirement in `gameplay-evidence.md`. |
| Fixture substitution | Explicit fixture boundary in `gameplay-evidence.md`. |
| Contaminated performance capture | Fail-closed capture rule in `release-checks.md`. |
| Operations loaded for one serial slice | Observable activation condition in `SKILL.md` and `production-operations.md`. |
| Existing gate weakened | Restore the exact visual, TDD, review, evidence, or release requirement; operations text cannot waive it. |

For an omitted field or wrong output shape, strengthen the positive contract. For a
discipline violation under pressure, add the observed rationalization and its direct
counter without adding speculative policy.

After each wording change, create a new isolated skill copy and run five fresh
samples for every affected case plus `OPS-07` and `OPS-08`. Do not count prior
samples toward the new variant. Continue until all mandatory criteria pass five out
of five.

- [ ] **Step 12: Record every GREEN variant**

Append to
`docs/superpowers/evals/2026-08-19-godot-production-operations.md`:

- exact source commit or working-tree diff identity for each variant;
- five run IDs and manual verdicts per executed case;
- exact relevant text for every new rationalization;
- the guidance change it caused, or the reason no change was needed;
- final pass counts for all eight cases; and
- confirmation that every final sample used a fresh context and withheld rubrics.

Expected: the final summary reports `5/5` for every case and traces every added
sentence to control or refinement evidence.

- [ ] **Step 13: Re-run structural regression checks**

Run:

```powershell
python tests/test_production_operations_contract.py -v
git diff --check
```

Expected: eight tests run; only the deliberately deferred README test remains
failing. `git diff --check` prints no errors.

- [ ] **Step 14: Commit behavioral evidence and any justified refinements**

If guidance changed during refinement, stage only the affected skill files and the
evaluation record. If initial GREEN already passed, stage only the evaluation
record. Run:

```powershell
git add -- docs/superpowers/evals/2026-08-19-godot-production-operations.md godot-game-production/SKILL.md godot-game-production/references/production-operations.md godot-game-production/references/gameplay-evidence.md godot-game-production/references/release-checks.md
git diff --cached --check
git commit -m "test: record production operations behavior"
```

Expected: the commit contains the populated GREEN evidence and only refinements
directly justified in that evidence.

---

### Task 6: Document, Validate, and Independently Review the Completed Change

**Files:**

- Modify: `README.md:5-13`
- Verify unchanged:
  `godot-game-production/scripts/evidence_run.py`
- Verify unchanged:
  `godot-game-production/references/evidence-ledger.md`
- Verify unchanged:
  `godot-game-production/agents/openai.yaml`
- Test: `tests/test_production_operations_contract.py`

**Interfaces:**

- Consumes: final five-of-five behavioral wording and the existing installation
  documentation.
- Produces: concise user-facing discovery, a fully GREEN structural suite, official
  skill validation, and independent review findings.

- [ ] **Step 1: Verify the last structural test is RED**

Run:

```powershell
python tests/test_production_operations_contract.py ProductionOperationsContractTests.test_readme_mentions_conditional_operations -v
```

Expected: one test runs and fails because the README paragraph is absent.

- [ ] **Step 2: Add the concise README description**

Insert this paragraph at the end of `README.md` section
`## What the skill enforces`:

```markdown
For concurrent production work, the skill conditionally loads
`references/production-operations.md` to keep one authoritative owner per mutable
game fact, define measurable conflict-aware slices, and verify their integrated
candidate. A single bounded serial slice keeps the normal lighter routing.
```

- [ ] **Step 3: Run the full automated verification**

Run:

```powershell
$ErrorActionPreference = "Stop"
python tests/test_production_operations_contract.py -v
if ($LASTEXITCODE -ne 0) { throw "Structural contract failed." }
python "C:\Users\Ёж\.codex\skills\.system\skill-creator\scripts\quick_validate.py" "godot-game-production"
if ($LASTEXITCODE -ne 0) { throw "Skill validation failed." }
git diff 3684c45 --check
if ($LASTEXITCODE -ne 0) { throw "Implementation diff check failed." }
git diff --exit-code 4b600abe9913b95806bdf152f26d446cc1bbce59 -- godot-game-production/scripts/evidence_run.py godot-game-production/references/evidence-ledger.md godot-game-production/agents/openai.yaml
if ($LASTEXITCODE -ne 0) { throw "An intentionally unchanged file was modified." }
```

Expected:

- eight tests pass with final line `OK`;
- `quick_validate.py` prints `Skill is valid!`;
- the implementation diff check prints nothing;
- the unchanged-file comparison prints nothing and exits zero.

- [ ] **Step 4: Commit README**

Run:

```powershell
git add -- README.md
git diff --cached --check
git commit -m "docs: describe conditional production operations"
```

Expected: the commit contains only `README.md`.

- [ ] **Step 5: Request independent review**

Use `requesting-code-review` with a fresh reviewer only when the user has explicitly
authorized child sessions. Give the reviewer:

- the approved spec path;
- the implementation-plan path;
- the raw diff from `3684c45` through current `HEAD`;
- structural test and `quick_validate.py` output; and
- the evaluation record without the author's conclusions.

Ask for spec compliance first, then documentation quality, progressive disclosure,
test integrity, licensing independence, and regressions. The reviewer must not edit
files and must return findings ordered by severity with file and line references.

If child review is not authorized, stop before claiming completion and request that
authorization or an explicitly approved independent-review alternative.

- [ ] **Step 6: Resolve review findings without invalidating evidence**

For every accepted finding:

1. Change only the owning file.
2. Re-run its structural test.
3. If skill wording changes, rerun five fresh samples for every affected behavioral
   case plus `OPS-07` and `OPS-08` and update the evaluation record.
4. Re-run the full automated verification from Step 3.
5. Stage only in-scope files with the command below, inspect the staged names, and
   commit.

```powershell
git add -- README.md tests/test_production_operations_contract.py tests/behavioral/production-operations-cases.md docs/superpowers/evals/2026-08-19-godot-production-operations.md godot-game-production/SKILL.md godot-game-production/references/production-operations.md godot-game-production/references/gameplay-evidence.md godot-game-production/references/release-checks.md
git diff --cached --name-only
git diff --cached --check
git commit -m "fix: address production operations review"
```

Reject findings that introduce a spec non-goal or weaken an existing gate, and
record the evidence-backed reason in the review response.

- [ ] **Step 7: Run the final completion gate**

Use `verification-before-completion`, then run:

```powershell
$ErrorActionPreference = "Stop"
python tests/test_production_operations_contract.py -v
if ($LASTEXITCODE -ne 0) { throw "Structural contract failed." }
python "C:\Users\Ёж\.codex\skills\.system\skill-creator\scripts\quick_validate.py" "godot-game-production"
if ($LASTEXITCODE -ne 0) { throw "Skill validation failed." }
git diff 3684c45 HEAD --check
if ($LASTEXITCODE -ne 0) { throw "Committed implementation diff check failed." }
git status --short --branch
git log --oneline --decorate 3684c45..HEAD
```

Expected: eight tests pass, skill validation succeeds, the committed diff check is
clean, `git status` reports no modified or untracked files, and the log contains only
the planned implementation, evidence, documentation, and any review-fix commits.

Do not push. Hand off the local branch and exact commit identities to the user.
