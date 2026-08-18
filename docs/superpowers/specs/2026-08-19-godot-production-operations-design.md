# Conditional Production Operations for Godot Game Production

- **Status:** Draft for repository review
- **Decision date:** 2026-08-19
- **Target skill:** `godot-game-production`
- **Baseline:** `StanislavSmetaninSSM/godot-game-production-skill` at
  `4b600abe9913b95806bdf152f26d446cc1bbce59`
- **Comparison input:** `studioigor/gamestudio` at
  `bb9aef78b11bc488b7ead34f929a662a584d955c`

## Decision

Add a small, conditional production-operations layer to the existing skill.
Keep one authoritative-owner invariant in `SKILL.md` because it applies to every
implementation task. Route to a new operations reference only when work contains
multiple concurrent implementation slices, agents, or worktrees. Extend the
existing gameplay-evidence and release-check references with diversified playtest
and controlled performance-capture rules.

This is an independent adaptation of useful production concepts, not a port of the
comparison repository. The current visual-contract, feasibility, TDD, independent
review, evidence-integrity, and release gates remain authoritative.

## Context

The current skill has strong product and evidence gates, but it does not explicitly
define how broad production work should be divided and coordinated. Under concurrent
work this leaves four recurring risks:

1. Two slices can mutate or reinterpret the same gameplay fact, creating competing
   sources of truth.
2. A backlog can be fragmented into tiny file-oriented tasks that repeatedly reload
   the same context without producing a complete player-visible result.
3. Repeated playtests can exercise the same scenario and seed, creating volume
   without meaningful coverage.
4. Performance evidence can be captured while unrelated heavy work is running,
   making the result neither reproducible nor suitable for a release decision.

The comparison repository contains useful ideas for these problems, but also embeds
provider-specific orchestration, fixed task weights, shell commands, and review/test
policies that conflict with this skill. Only the general production concepts belong
in this design.

## Goals

- Give each mutable gameplay fact one explicit authoritative owner.
- Make parallel production slices coherent, measurable, and conflict-aware.
- Require an integrated candidate check after individually verified slices.
- Increase playtest information by varying scenario, state, seed, and input.
- Preserve the distinction between fixture-based checks and a complete player
  journey.
- Make performance evidence reproducible by recording and controlling ambient load.
- Keep the common single-slice workflow compact through progressive disclosure.
- Preserve every existing mandatory gate and fail-closed decision rule.

## Non-goals

- Replacing Spec Kit task ownership or Superpowers execution workflows.
- Introducing an agent provider, model router, orchestration CLI, or worktree manager.
- Assigning universal percentages, numerical task weights, production-task
  line-count quotas, or preferred model classes.
- Reducing test, review, documentation, or evidence requirements for speed.
- Treating unit tests, fixtures, manifests, screenshots, or individual slice passes
  as substitutes for integrated runtime proof.
- Changing the evidence manifest schema or `evidence_run.py` in the first iteration.
- Copying text or shell code from the MIT-licensed comparison repository.

## Activation and progressive disclosure

The design has an always-on invariant and a conditional reference. A production
interval is the set of slices intended to land in one integrated candidate before
the next milestone evidence decision.

### Always-on invariant

For every mutable production fact, identify exactly one authoritative owner. A fact
includes gameplay state, a decision, an emitted event, a timer, and a persisted save
value. Other systems may read the fact or react to its published transition, but
must not infer, shadow, or independently write a competing version.

This invariant belongs in `SKILL.md` as a stop rule because it is relevant even to a
single narrow change.

### Conditional operations reference

Load `references/production-operations.md` when either observable condition is true:

- the current production interval contains two or more implementation slices
  scheduled to overlap or be delegated concurrently; or
- multiple agents or worktrees will implement related parts of the same candidate.

Do not load it merely because a task has several serial steps. A single bounded
slice implemented in one working context continues through the normal routed
workflow. The always-on ownership invariant still applies.

If the conditions become true after work starts, load the reference before assigning
or starting the additional slice.

## Authoritative-owner contract

An owner is a concrete Godot system boundary: for example, a player-state machine,
combat resolver, quest service, save repository, or run clock. It is not the human
or agent performing the task.

For each fact changed by a production slice, the slice must name:

- the fact or transition;
- its authoritative system;
- the write path;
- the read, signal, or subscription path used by consumers; and
- the persistence owner when the fact survives process exit.

Consumers must render or react to authoritative state. A UI element must not invent
a failure reason from animation state, input timing, text, or a second boolean when
the owning system already exposes the result. A save adapter must not become a
second gameplay authority merely because it serializes the value.

No concurrent slices may change the same authoritative owner or its public
derivation contract. When overlap is discovered, merge the work into one coherent
slice or sequence the slices behind an explicit dependency. Renaming files or
assigning different agents does not remove an ownership conflict.

## Production-slice contract

A production slice is a bounded, independently verifiable unit that produces one
coherent player-visible or release-visible outcome. Slice boundaries follow shared
context and ownership, not arbitrary file size.

Before a concurrent slice begins, record all of these fields:

| Field | Required content |
|---|---|
| `slice_id` | Stable identifier used by task, evidence, and integration records. |
| `zone` | Coherent gameplay, content, UI, platform, or release boundary. |
| `authoritative_owner` | The principal system whose fact or transition changes; list every additional changed authority if the outcome cannot remain within one. |
| `player_visible_outcome` | What the player or release operator can observe when the slice succeeds. |
| `baseline` | Current measured behavior, including the evidence source. |
| `postcondition` | Measurable required result and any requirement-derived margin. |
| `non_goals` | Adjacent behavior deliberately excluded from the slice. |
| `dependencies` | Inputs or predecessor slices that must already be valid. |
| `conflicts` | Owners, files, assets, scenes, or contracts that cannot change concurrently. |
| `verification` | Exact applicable automated commands and exact target-Godot runtime actions. |
| `runtime_artifacts` | Expected logs, traces, captures, saves, telemetry, or packages. |
| `integration_target` | Branch, commit, build, scene, or package into which the slice must be combined. |

The `postcondition` must derive from the game specification, target hardware, or a
measured baseline. The skill must not invent a universal percentage or score.

Group changes when they share the same owner, setup, runtime journey, or evidence
capture. Split them when they have independent ownership, outcomes, and verification
paths. A list of tiny edits that all require the same scene and playthrough is one
slice, not artificial parallelism.

Risk focus may determine which hazards receive extra review attention. It never
waives test-first implementation, independent review, visual approval, gameplay
evidence, or release checks.

## Integrated-candidate contract

An individually passing slice is not a passing production candidate. After all
selected slices are combined in the declared integration target:

1. Verify that the integrated revision contains each expected `slice_id` and no
   unresolved ownership or file conflict.
2. Run the relevant automated suite from the integrated revision.
3. Run the complete affected player journey in the target Godot build.
4. Capture the required cross-system runtime artifacts from that exact candidate.
5. Reopen every facet invalidated by integration changes or contradictory evidence.

Only the existing milestone and release gates may declare the integrated candidate
passing.

## Gameplay-evidence extension

Add a playtest matrix to `references/gameplay-evidence.md`. Each planned run records:

| Field | Meaning |
|---|---|
| `scenario` | Player goal or risk being exercised. |
| `prior_state` | Exact starting gameplay and persistence state. |
| `seed` | Exact procedural seed, or `not_applicable` for non-seeded behavior. |
| `input` | Exact player or automation input sequence. |
| `expected_transition` | Authoritative state change and visible outcome. |
| `artifact` | Target-build capture, trace, save, or telemetry identity. |

Independent coverage rows must vary scenario or prior state. Seeded rows intended to
broaden coverage must also use distinct seeds. A repeated seed is valid for bug
reproduction or regression proof, but must be labelled as such and does not count as
diversified coverage.

Fixtures may accelerate a focused test only when their source, construction, and
assumptions are recorded. A fixture does not prove entry, onboarding, progression,
persistence, or return to play. Every affected milestone still requires the complete
integrated journey defined by the existing gameplay-evidence contract.

When several failures are found, group them by authoritative owner and zone before
creating repair slices. Similar visible symptoms with different owners remain
separate defects; different symptoms caused by one owner should not become competing
parallel repairs.

## Performance-evidence extension

Add controlled-capture rules to `references/release-checks.md`. For each performance
run, record:

- exact candidate, Godot version, export profile, target hardware, and environment;
- relevant CPU, GPU, memory, thermal, and power state available on that platform;
- foreground and background load before and during capture;
- project-owned Godot editor, import, build, test, capture, and browser-test
  processes that were stopped or intentionally retained; and
- the measurement command, duration, scenario, seed, raw artifact, and budget source.

Heavy build, import, browser-test, and performance-capture jobs must not overlap when
they can materially contend for the measured resource. Stop only processes known to
belong to the in-scope project. Processes launched by the current workflow may be
stopped when safe; pre-existing processes require user confirmation. Never terminate
unrelated user processes to obtain a clean number.

If competing load cannot be safely controlled, changes materially during the run,
or is not recorded, do not submit the capture and keep or reopen the
`reliability_performance` facet as `PENDING` until the run is repeated under a
controlled environment. Contaminated data may diagnose a problem but cannot support
a milestone or release pass.

Performance budgets remain requirement- and hardware-derived. No threshold from the
comparison repository is adopted as a default.

## File-level design

### `godot-game-production/SKILL.md`

- Add the authoritative-owner invariant to the stop rules.
- Add one conditional routing bullet for `references/production-operations.md` using
  the two observable activation conditions above.
- Keep the new main-file wording compact; detailed contracts live in the reference.
- Do not change frontmatter, the mandatory state sequence, or required sub-skills.

### `godot-game-production/references/production-operations.md`

Create a concise reference containing:

- activation reminder;
- authoritative-owner and collision rules;
- the production-slice contract;
- coherent grouping and dependency rules;
- integrated-candidate verification; and
- the rule that risk focus does not replace existing tests or reviews.

The reference must be self-contained enough to apply without reading the comparison
repository and should target roughly 70–100 lines.

### `godot-game-production/references/gameplay-evidence.md`

Add the playtest matrix, diversity rules, fixture provenance and limitations, and
failure grouping by owner and zone. Preserve the current causal journey and facet
separation.

### `godot-game-production/references/release-checks.md`

Add ambient-load recording, safe process control, serialized heavy capture, and
fail-closed handling of contaminated performance evidence. Preserve the eight-facet
release contract.

### Files intentionally unchanged in the first iteration

- `godot-game-production/scripts/evidence_run.py`
- `godot-game-production/references/evidence-ledger.md`
- `godot-game-production/agents/openai.yaml`

The current artifact kinds can carry the added records. A schema change is allowed
only if behavioral evaluation shows that prose requirements are repeatedly skipped
or cannot be validated with existing artifacts.

After implementation and verification, update `README.md` with one short paragraph
describing conditional production operations. Do not duplicate the full reference.

## Behavioral evaluation strategy

Skill changes follow RED–GREEN–REFACTOR. Run baseline scenarios against the unchanged
skill before editing it, record the observed decisions and rationalizations, and
write only enough guidance to correct demonstrated failures.

The evaluation set contains six intended failure probes followed by two guard cases:

1. A UI slice attempts to infer a failure reason instead of reading the owning
   gameplay state.
2. Two proposed parallel slices change the same authoritative owner.
3. A broad backlog is split into tiny tasks that repeatedly require the same scene,
   setup, and evidence capture.
4. Independent playtests are assigned the same scenario and procedural seed.
5. A fixture is presented as proof of the complete player journey.
6. Performance capture runs concurrently with build or browser-test load.
7. Guard: a single narrow serial task must not be burdened with the conditional
   operations reference.
8. Guard: new operations guidance must not weaken the visual contract, TDD, or
   independent review.

Run every case against the unchanged skill and record the baseline observation. A
probe that already behaves correctly becomes a regression case; do not add guidance
for a failure that the control does not exhibit. At least one relevant baseline
failure must be observed before editing the skill, and each new rule must trace to an
observed failure or an existing behavior that must be preserved.

For wording-sensitive guidance:

- use the current unchanged skill as the no-guidance control;
- use one fresh context per sample;
- run at least five repetitions per wording variant;
- manually inspect every result instead of relying only on keyword scoring; and
- require every mandatory final behavior to pass in all five GREEN repetitions.

Full pressure scenarios remain the final gate for discipline rules. Fresh child
sessions may be used only after the user explicitly authorizes subagent evaluation;
otherwise use an approved isolated evaluation mechanism or stop before changing the
skill. Evaluation constraints are not permission to skip RED.

## Compatibility and migration

- Existing projects need no manifest migration.
- Existing evidence remains valid only under the current artifact identity and
  invalidation rules; the new guidance does not retroactively bless or reject it.
- The conditional reference applies when the next qualifying production interval
  begins. In-flight concurrent work must declare owners and conflicts before another
  slice starts.
- Existing single-slice behavior remains unchanged except for the always-on
  authoritative-owner invariant.
- No Orca command, provider/model mapping, fixed weighting scheme, shell script, or
  limited-review policy from the comparison repository is introduced.

## Licensing

The comparison repository is MIT-licensed and this repository uses the Unlicense.
Implementation must independently express the general concepts documented here.
Do not copy substantial prose, scripts, command sequences, tables, or distinctive
templates from the comparison repository.

## Acceptance criteria

The change is ready when all of the following are true:

- `SKILL.md` contains one unambiguous authoritative-owner stop rule and one
  observable conditional route to the operations reference.
- The operations reference contains every required production-slice field and
  rejects overlapping concurrent owners.
- The gameplay reference requires meaningful scenario/state diversity, seed
  diversity where applicable, fixture provenance, and an integrated journey.
- The release reference records ambient load, serializes materially competing work,
  and keeps contaminated evidence non-passing.
- Integrated-candidate verification is explicit and individual slice success cannot
  imply milestone or release success.
- No universal weights, provider mappings, orchestration commands, reduced-review
  policies, or copied comparison text are introduced.
- All eight behavioral cases have recorded control observations and final results;
  each new rule traces to an observed baseline failure, and mandatory behaviors pass
  five out of five final repetitions.
- Existing visual-contract, feasibility, TDD, independent-review, evidence-integrity,
  and eight-facet release behaviors remain mandatory in regression scenarios.
- Every reference link resolves, `quick_validate.py` reports `Skill is valid!`, and
  repository checks complete without warnings attributable to the change.

## Delivery boundaries

This document is the only deliverable in the specification commit. It does not
authorize or contain skill implementation.

After written-spec approval, create a separate implementation plan. That plan must
put behavioral RED evaluation before any skill edit, keep guidance changes separate
from verification evidence where practical, and end with validation, regression
evaluation, independent review, and the concise README update.
