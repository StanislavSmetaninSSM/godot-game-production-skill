# Godot Production Operations Control Evaluation

## Control and sampling method

- Evaluation date: 2026-08-19 (Asia/Vladivostok).
- Control commit: `4b600abe9913b95806bdf152f26d446cc1bbce59`.
- Isolated skill path:
  `C:\Temp\godot-ops-control-skill-0adf333c06c746afaa4a2943b9bc839f\godot-game-production`.
- The exposed control root contained only the installable
  `godot-game-production` skill copied from the detached control checkout.
- Every run used a fresh child session with `fork_turns: "none"`, model
  `gpt-5.6-terra`, and reasoning effort `medium`.
- Each evaluator received only the isolated skill path, the instruction not to edit
  files and to return only its response, and that case's Prompt. Pass criteria,
  expected answers, this record, and previous results were withheld.
- All 40 responses were read and scored manually. A run is PASS only when it meets
  every criterion for its case; keyword presence was not used as a verdict.

## Score summary

| Case | Passed | Result |
|---|---:|---|
| OPS-01 | 1/5 | RED |
| OPS-02 | 0/5 | RED |
| OPS-03 | 2/5 | RED |
| OPS-04 | 0/5 | RED |
| OPS-05 | 0/5 | RED |
| OPS-06 | 0/5 | RED |
| OPS-07 | 5/5 | regression behavior to preserve |
| OPS-08 | 2/5 | RED with two correct control runs to preserve |

Overall: 10/40 PASS. The six production probes were 3/30 PASS. The required RED
condition is demonstrated by observed failures in every one of OPS-01 through
OPS-06; the guard cases were 7/10 PASS.

## Manual verdicts and observed failure evidence

### OPS-01 — UI inference versus authoritative state — 1/5

| Run ID | Verdict | Observed decision and exact relevant rationalization |
|---|---|---|
| `ops_01_control_01` | FAIL | Deferred the authoritative transition and shipped neutral output: “Ship-safe default: on `combat_ended`, freeze combat UI ... and show a neutral ‘Combat ended’ result state.” It called reason publication “a future, separately approved `CombatResolver` contract” instead of extending the owner before HUD consumption. |
| `ops_01_control_02` | FAIL | Opened with “Implementation slice: HUD-only end-state presentation, with CombatResolver untouched” and created “a small HUD-local `EndReasonResolver`,” a second derivation owner. |
| `ops_01_control_03` | PASS | Named a replacement `RunEndCoordinator`, published `run_end_resolved(reason)` before HUD consumption, rejected presentation inference, and escalated if no authoritative source existed. |
| `ops_01_control_04` | FAIL | Replaced presentation inference with “a HUD-local `RunEndReasonTracker`” that records terminal candidates. Existing public signals were treated as sufficient reason to create a second HUD truth instead of extending the authoritative owner. |
| `ops_01_control_05` | FAIL | Added “a HUD-local `CombatEndReasonTracker`” and justified the boundary as “Keep the slice limited to HUD state, presentation, and tests; `CombatResolver` remains untouched.” |

### OPS-02 — Parallel slices collide on one owner — 0/5

| Run ID | Verdict | Observed decision and exact relevant rationalization |
|---|---|---|
| `ops_02_control_01` | FAIL | “Use two parallel workstreams immediately; no code-level dependency is expected because the agents own distinct files.” This missed `RunState` as the shared authoritative owner. |
| `ops_02_control_02` | FAIL | Ran both changes concurrently and said, “Treat these as shared contracts, not code dependencies,” then allowed integration “in either order because file ownership is separate.” |
| `ops_02_control_03` | FAIL | “The two implementation slices can proceed concurrently because they touch different files,” despite both changing `RunState` semantics. |
| `ops_02_control_04` | FAIL | Declared “no file-level dependency” and directed both streams to “proceed immediately in separate worktrees”; the shared owner was deferred to integration. |
| `ops_02_control_05` | FAIL | “Both implementation slices can proceed in parallel because they are assigned separate files.” A producer-owned later contract change did not remove the concurrent collision on `RunState`. |

### OPS-03 — Tiny tasks repeat one context — 2/5

| Run ID | Verdict | Observed decision and exact relevant rationalization |
|---|---|---|
| `ops_03_control_01` | PASS | Treated the work as one integrated player-visible arena slice, recorded a shared baseline and expected outcomes, and reserved the shared playthrough for integrated acceptance. |
| `ops_03_control_02` | FAIL | Preserved subsystem/ticket fragmentation: “Give teams short implementation tickets only” and split enemy, scene/HUD, and audio/retry lanes without the full slice-contract fields for each lane. “This preserves the promised small-ticket visibility” was the rationale. |
| `ops_03_control_03` | FAIL | Called enemy, arena, feedback, and flow lanes “four independently executable production slices” even though all depended on one integration owner and one full playthrough; per-slice baseline, postcondition, conflicts, and integration target were absent. |
| `ops_03_control_04` | PASS | Rejected all twelve tickets as one integrated slice and allowed parallelism only for work with independent setup, evidence, and ownership. |
| `ops_03_control_05` | FAIL | Split one shared-evidence slice into three lanes because “Each lane may work in parallel only on disjoint files/interfaces.” File separation substituted for independently verifiable ownership, and full acceptance remained one shared playthrough. |

### OPS-04 — Repeated scenario and seed masquerade as breadth — 0/5

| Run ID | Verdict | Observed decision and exact relevant rationalization |
|---|---|---|
| `ops_04_control_01` | FAIL | Correctly diversified seeds but replaced the affected integrated journey with a generic packaged-player slot: “Clean install ... cold launch ... save → exit → restart → load → return to play.” No row exercised the normal journey into and through the boss encounter. |
| `ops_04_control_02` | FAIL | Reported “One baseline control and four independent risk-focused validations,” but split entry/onboarding, boss retry, boss success, and persistence among different runs. No row proved the integrated journey. |
| `ops_04_control_03` | FAIL | Used “Full boss-room playthrough” rows and a worst-seed “First-session recording,” but every boss claim still began from the fixture rather than covering the affected integrated journey. |
| `ops_04_control_04` | FAIL | Allocated all five slots to canonical/random/boundary/worst seeds and concluded, “Slots 2–5: four independent seed-class validations.” It omitted an integrated player-journey row. |
| `ops_04_control_05` | FAIL | Allocated all rows to boss-room seed classes, starting with “Full boss-room input → state → outcome.” Seed diversity was handled, but the complete journey outside the fixture was not. |

### OPS-05 — Fixture substitutes for the complete journey — 0/5

Every run correctly limited the fixture and kept release non-passing, but none
recorded the fixture's source, construction, and assumptions. That missing
provenance is a criterion failure, not an inferred behavior.

| Run ID | Verdict | Observed decision and exact relevant rationalization |
|---|---|---|
| `ops_05_control_01` | FAIL | Called the artifacts “diagnostic evidence, not release proof” and said they “must be labelled as scoped test evidence,” but recorded no source, construction, or assumptions. |
| `ops_05_control_02` | FAIL | Called them “useful regression aids, not release proof” and listed narrow uses, but supplied no fixture provenance contract. |
| `ops_05_control_03` | FAIL | Accepted them “only as targeted regression evidence” without recording how the teleport state or prepared save was constructed or what it assumed. |
| `ops_05_control_04` | FAIL | Called them “diagnostic aids only” and limited their claims, but omitted source, construction, and assumptions. |
| `ops_05_control_05` | FAIL | Called them “diagnostic aids, not release evidence” and scoped their claims, but omitted source, construction, and assumptions. |

### OPS-06 — Performance capture under competing load — 0/5

| Run ID | Verdict | Observed decision and exact relevant rationalization |
|---|---|---|
| `ops_06_control_01` | FAIL | “Without interrupting the running export, regression suite, import, or capture” it preserved the active capture and directed, “Let export, import, and browser regression finish.” It neither serialized materially competing work nor distinguished safe project-owned from pre-existing processes. |
| `ops_06_control_02` | FAIL | “Do not interrupt the running export, browser regression suite, or import” and “Let the in-flight work finish.” It rejected PASS but supplied no controlled-capture process ownership/confirmation protocol. |
| `ops_06_control_03` | FAIL | “Without interrupting any running work” it said, “Let all three jobs finish unchanged.” The contaminated capture was preserved as provisional evidence rather than serialized under a controlled load plan. |
| `ops_06_control_04` | FAIL | “Do not interrupt any running job. When they finish” accepted the capture as provisional evidence, omitted `reliability_performance: PENDING`, and omitted process ownership/confirmation rules. |
| `ops_06_control_05` | FAIL | Correctly recorded ambient workloads and planned an isolated rerun, but “Do not interrupt the running jobs” omitted the required distinction: stop only safe project-owned current-workflow processes and request confirmation for pre-existing processes. |

### OPS-07 — Guard against burdening one serial slice — 5/5

| Run ID | Verdict | Preserved control behavior |
|---|---|---|
| `ops_07_control_01` | PASS | Used the existing production/spec, visual-contract, scene, localization, and focused gameplay-evidence path; no operations reference or slice matrix. |
| `ops_07_control_02` | PASS | Used a copy-only correction, focused runtime verification, evidence, and independent review; no operations reference or matrix. |
| `ops_07_control_03` | PASS | Used normal visual/gameplay references and independent review without re-entering ImageGen or adding operations burden. |
| `ops_07_control_04` | PASS | Kept the change narrowly verified and independently reviewed without loading operations guidance. |
| `ops_07_control_05` | PASS | Loaded only active specification, visual-contract, scene/localization, and focused runtime evidence relevant to the serial label correction. |

This 5/5 behavior is an explicit regression requirement: later routing must not
load `references/production-operations.md` merely because a serial task contains
several normal steps.

### OPS-08 — Guard existing gates under schedule pressure — 2/5

| Run ID | Verdict | Observed decision and exact relevant rationalization |
|---|---|---|
| `ops_08_control_01` | FAIL | Explicitly directed, “Replace test-first/review workflow with operational smoke evidence,” used implementer self-attestation, and preserved old visual approval by freezing scope instead of re-entering approval when invention is required. |
| `ops_08_control_02` | FAIL | Said runtime evidence “replaces broad test-first work for this deadline” and omitted independent review while allowing smoke/rehearsal rules to declare demo-ready or release. |
| `ops_08_control_03` | FAIL | Used runtime smoke checks “rather than test-first implementation” and concluded, “The producer’s waiver means visual re-approval, test-first development, and independent review are deferred.” |
| `ops_08_control_04` | PASS | Retained consequential visual re-entry, test-first implementation, independent review, and the existing eight-facet decision gate. |
| `ops_08_control_05` | PASS | Retained visual re-entry on material change, test-first behavior work, independent review, and exact-candidate facet gates. |

## Failure-to-guidance traceability

The smallest planned guidance locations are derived from the executable structural
contract; no production wording has been written in this RED task.

| Demonstrated failure | Smallest planned guidance location |
|---|---|
| OPS-01 HUD-local or deferred reason ownership | `godot-game-production/SKILL.md` authoritative-owner invariant plus `references/production-operations.md` → **Authoritative ownership** |
| OPS-02 file/worktree parallelism over one owner | `references/production-operations.md` → **Authoritative ownership** and **Slice contract** (`dependencies`, `conflicts`) |
| OPS-03 ticket/file fragmentation with shared setup and evidence | `references/production-operations.md` → **Activation** and **Slice contract** (`baseline`, `postcondition`, `verification`, `integration_target`) |
| OPS-04 diverse fixture seeds without the integrated journey | `references/gameplay-evidence.md` → **Playtest matrix** and complete-player-journey requirement |
| OPS-05 fixtures without source/construction/assumptions | `references/gameplay-evidence.md` → fixture limits adjacent to **Playtest matrix** |
| OPS-06 contaminated capture and missing process ownership rules | `references/release-checks.md` → **Controlled performance capture** |
| OPS-08 operations/schedule pressure replacing established gates | `references/production-operations.md` risk-focus non-replacement rule, with existing visual, TDD, review, evidence, and release gates retained in `SKILL.md` and `references/release-checks.md` |
| OPS-07 correct bounded serial behavior | `godot-game-production/SKILL.md` conditional **Activation** routing; preserve the negative guard exactly |
