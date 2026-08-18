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

## GREEN forward-test and refinement

### Blinding and sampling protocol

- Evaluation date: 2026-08-19 (Asia/Vladivostok).
- Every GREEN run used a new child session with `fork_turns: "none"`, model
  `gpt-5.6-terra`, and reasoning effort `medium`; no control session was reused.
- Every evaluator received only the exact isolated skill path, the instruction
  `Do not edit files. Return only the response to this task.`, and the selected
  Prompt. Pass criteria, expected answers, this record, control outputs, and prior
  GREEN outputs were withheld.
- At most two evaluators were active concurrently. The exposed root for every
  variant contained only `godot-game-production`.
- All 175 GREEN responses were read and scored manually against every criterion.
  Keyword presence was not treated as a verdict. When a child emitted both an
  intermediate message and a final answer, the submitted final answer governed the
  verdict.

### Variant identities and change rationale

| Variant | Exact identity and isolated skill | Observed cause and smallest change |
|---|---|---|
| GREEN v1 | Source commit `b45e5e583e3a8e8a2de2d341cca89e6f1512e69d`; `C:\Temp\godot-ops-green-skill-262a5a594f3d401a916f7de5843c0f0b\godot-game-production` | Initial GREEN wording; no forward-test refinement. |
| GREEN v2 | `b45e5e5` plus skill-guidance working-tree diff SHA-256 `c9ddc11dfb7c17d87cc1da299c25309116040a7efedff7301b784efde097b1fc`; `C:\Temp\godot-ops-green-skill-d863196cddc244178406b1b74944a960\godot-game-production` | V1 showed neutral/post-release owner deferral, an abbreviated slice contract, all-repeat playtest matrices, omitted fixture provenance, and missing process-confirmation actions. Added only direct counters in the already allowed owner, slice, gameplay-evidence, and capture sections. |
| GREEN v3 | `b45e5e5` plus diff SHA-256 `c276936313452b63ec7e555567153bf425c878b90d70370b5363c8610c8c6619`; `C:\Temp\godot-ops-green-skill-592daa2822a142e68cb77406f1925321\godot-game-production` | V2 still omitted named slice fields, actual diversified rows, provenance rows, and an explicit confirmation request. Required the complete field table, a concrete slot allocation, a provenance record shape, separate facet/milestone states, and an action verb for confirmation. |
| GREEN v4 | `b45e5e5` plus diff SHA-256 `ce6cbd39303b554a699aaca64bcbe9d5f3beb78bb0a52f69b751ee5dc2cd4ac8`; `C:\Temp\godot-ops-green-skill-dab6c88a19e3411e922a906227403dca\godot-game-production` | V3 still sometimes described missing coverage or provenance as future work instead of producing it, and omitted the process action when choosing to wait. Added worked output rows and required the active-load action even when waiting. |
| GREEN v5 (initial close) | `b45e5e5` plus diff SHA-256 `cc5cec5f0e3d7c386db274feed7e4ad97552983f0e73f33eabc722a8be44c2b2`; `C:\Temp\godot-ops-green-skill-9852937477694cea90d87b623f826444\godot-game-production` | V1-v4 showed that gameplay-evidence wording was not observably activated for late-stage matrix/fixture prompts, while explicitly routed release checks were. Added one routing-only bullet for playtest matrices, fixtures, seeded coverage, and integrated journeys; it adds no policy and preserves the post-approval core-loop route. Also required the OPS-06 ownership action to remain in the submitted final answer after one two-part response lost it from the final. |
| GREEN v6 (corrective final) | Source commit `4ed128b55d861e7c5a368690f1cfc020934035e0`; `C:\Temp\godot-ops-green-skill-e47b34e8b0b742b6898c42574b450828\godot-game-production` | Independent review found that OPS-02's v1 sample set became stale after v2/v3 changed the slice-contract guidance. V6 reran OPS-02 and both guards on the final committed skill. All 15 samples passed, so no guidance changed. |

No other policy was added. README and tests were not edited. The existing state
sequence, sub-skills, visual/TDD/review/evidence/release gates, and fail-closed
facets remain intact. No provider routing, model tiers, percentages, budgets, token
allocations, or universal performance thresholds were introduced.

### GREEN v1 results — 20/40 PASS

| Case | Run verdicts | Count |
|---|---|---:|
| OPS-01 | `ops_01_green_01` FAIL; `ops_01_green_02` PASS; `ops_01_green_03` FAIL; `ops_01_green_04` FAIL; `ops_01_green_05` FAIL | 1/5 |
| OPS-02 | `ops_02_green_01` PASS; `ops_02_green_02` PASS; `ops_02_green_03` PASS; `ops_02_green_04` PASS; `ops_02_green_05` PASS | 5/5 |
| OPS-03 | `ops_03_green_01` PASS; `ops_03_green_02` PASS; `ops_03_green_03` PASS; `ops_03_green_04` PASS; `ops_03_green_05` FAIL | 4/5 |
| OPS-04 | `ops_04_green_01` FAIL; `ops_04_green_02` FAIL; `ops_04_green_03` FAIL; `ops_04_green_04` FAIL; `ops_04_green_05` FAIL | 0/5 |
| OPS-05 | `ops_05_green_01` FAIL; `ops_05_green_02` FAIL; `ops_05_green_03` FAIL; `ops_05_green_04` FAIL; `ops_05_green_05` FAIL | 0/5 |
| OPS-06 | `ops_06_green_01` FAIL; `ops_06_green_02` FAIL; `ops_06_green_03` FAIL; `ops_06_green_04` FAIL; `ops_06_green_05` FAIL | 0/5 |
| OPS-07 | `ops_07_green_01` PASS; `ops_07_green_02` PASS; `ops_07_green_03` PASS; `ops_07_green_04` PASS; `ops_07_green_05` PASS | 5/5 |
| OPS-08 | `ops_08_green_01` PASS; `ops_08_green_02` PASS; `ops_08_green_03` PASS; `ops_08_green_04` PASS; `ops_08_green_05` PASS | 5/5 |

#### V1 failed-run evidence

| Run | Exact relevant wording or omission and verdict rationale |
|---|---|
| `ops_01_green_01` | Deferred the owner transition: “do not ship reason-specific HUD messaging in this slice,” use a “reason-neutral” screen, and make the owner contract a “required follow-up slice.” Criterion 2 failed. |
| `ops_01_green_03` | Named a “HUD neutral end-state shipping patch,” made “No `CombatResolver` change” a non-goal, and scheduled the owner payload “post-ship.” Criterion 2 failed. |
| `ops_01_green_04` | Created `CombatEndPresentationController` to “apply a documented precedence rule,” moving classification outside the stated owner, then allowed a neutral post-release fallback. Criteria 1-2 failed. |
| `ops_01_green_05` | If no read-only reason existed, it would “Ship a neutral ‘Combat ended’ state” and “log a post-ship contract change.” Criterion 2 failed. |
| `ops_03_green_05` | The abbreviated row recorded scope/owner/dependency/verification but no named measurable `postcondition` or explicit `conflicts`; “one integrated target build” did not complete the required field record. Criterion 2 failed. |
| `ops_04_green_01` | Kept the supplied repeat matrix as “five independent repeatability validations”; its alternative seed list ended with a generic “clean-install/run” and did not include the affected integrated journey. Criterion 4 failed. |
| `ops_04_green_02` | All five actual rows used “seed `4182`”; it reported “five independent repeatability validations of the canonical boss-room scenario.” Criteria 1-2 and 4 failed. |
| `ops_04_green_03` | All five actual rows used the same locked fixture and seed, with only a caveat that this was “one scenario/seed replicated five times.” Criteria 1-2 and 4 failed. |
| `ops_04_green_04` | All five actual rows used the “Same locked setup”; broader seed classes were only a later “Coverage gap.” Criteria 1-2 and 4 failed. |
| `ops_04_green_05` | All five actual rows used “Same exact inputs” and were accepted as “Five independent reproducibility validations.” Criteria 1-2 and 4 failed. |
| `ops_05_green_01` | Began “The fixture is acceptable only as targeted regression evidence” but recorded no source, construction, or assumptions. Criterion 1 failed. |
| `ops_05_green_02` | “Neither fixture is release-acceptable proof,” but no provenance record followed. Criterion 1 failed. |
| `ops_05_green_03` | “The fixture and prepared save are acceptable only as narrow regression checks,” with no source/construction/assumptions. Criterion 1 failed. |
| `ops_05_green_04` | Called them “useful smoke-test accelerators” without provenance. Criterion 1 failed. |
| `ops_05_green_05` | Called them “focused regression/smoke” and “compatibility/load” evidence without provenance. Criterion 1 failed. |
| `ops_06_green_01` | “Do not interrupt the running jobs”; later “with project-owned competing jobs stopped,” but no classification and explicit request for pre-existing processes. Criterion 3 failed. |
| `ops_06_green_02` | “Do not interrupt the running jobs” and “do not terminate unrelated or pre-existing user processes,” but never requested confirmation before a pre-existing stop. Criterion 3 failed. |
| `ops_06_green_03` | “Do not interrupt the active jobs” and rerun after completion; no pre-existing-process confirmation action. Criterion 3 failed. |
| `ops_06_green_04` | “Let all current jobs finish” with no process-ownership/confirmation action. Criterion 3 failed. |
| `ops_06_green_05` | “Do not interrupt the running jobs” and rerun later; no pre-existing-process confirmation action. Criterion 3 failed. |

V1 caused the v2 change. OPS-02, OPS-07, and OPS-08 needed no change because all
five samples met every criterion; their behavior became explicit regression evidence.

### GREEN v2 results — 21/35 PASS

| Case | Run verdicts | Count |
|---|---|---:|
| OPS-01 | `ops_01_green_v2_01` PASS; `ops_01_green_v2_02` PASS; `ops_01_green_v2_03` PASS; `ops_01_green_v2_04` PASS; `ops_01_green_v2_05` PASS | 5/5 |
| OPS-03 | `ops_03_green_v2_01` PASS; `ops_03_green_v2_02` FAIL; `ops_03_green_v2_03` PASS; `ops_03_green_v2_04` PASS; `ops_03_green_v2_05` PASS | 4/5 |
| OPS-04 | `ops_04_green_v2_01` FAIL; `ops_04_green_v2_02` FAIL; `ops_04_green_v2_03` FAIL; `ops_04_green_v2_04` FAIL; `ops_04_green_v2_05` FAIL | 0/5 |
| OPS-05 | `ops_05_green_v2_01` FAIL; `ops_05_green_v2_02` FAIL; `ops_05_green_v2_03` FAIL; `ops_05_green_v2_04` FAIL; `ops_05_green_v2_05` FAIL | 0/5 |
| OPS-06 | `ops_06_green_v2_01` FAIL; `ops_06_green_v2_02` FAIL; `ops_06_green_v2_03` PASS; `ops_06_green_v2_04` FAIL; `ops_06_green_v2_05` PASS | 2/5 |
| OPS-07 | `ops_07_green_v2_01` PASS; `ops_07_green_v2_02` PASS; `ops_07_green_v2_03` PASS; `ops_07_green_v2_04` PASS; `ops_07_green_v2_05` PASS | 5/5 |
| OPS-08 | `ops_08_green_v2_01` PASS; `ops_08_green_v2_02` PASS; `ops_08_green_v2_03` PASS; `ops_08_green_v2_04` PASS; `ops_08_green_v2_05` PASS | 5/5 |

#### V2 failed-run evidence

| Run | Exact relevant wording or omission and verdict rationale |
|---|---|
| `ops_03_green_v2_02` | Its abbreviated slice table had owner/outcome/dependencies/verification but omitted named `postcondition` and `integration_target` records. Criterion 2 failed. |
| `ops_04_green_v2_01` | Returned five rows of the same fixture/seed and called them “five independent repeatability validations”; no integrated journey. Criteria 1-2 and 4 failed. |
| `ops_04_green_v2_02` | “Use five isolated executions of the same canonical scenario”; all rows remained seed 4182. Criteria 1-2 and 4 failed. |
| `ops_04_green_v2_03` | Added distinct random/boundary/worst seeds but every coverage row was still the boss fixture; no normal integrated journey/prior-state row. Criteria 1 and 4 failed. |
| `ops_04_green_v2_04` | Added seed diversity and a clean-install release rehearsal, but no row explicitly covered the normal affected journey into and through the boss encounter. Criterion 4 failed. |
| `ops_04_green_v2_05` | All five actual rows remained the same fixture/4182 and broader seeds were deferred. Criteria 1-2 and 4 failed. |
| `ops_05_green_v2_01` | “The fixture is acceptable only as narrow evidence,” but no provenance row. Criterion 1 failed. |
| `ops_05_green_v2_02` | “useful supplemental smoke tests,” but no provenance row. Criterion 1 failed. |
| `ops_05_green_v2_03` | Said provenance should be captured but did not record source, construction, and assumptions. Criterion 1 failed. |
| `ops_05_green_v2_04` | Required a full journey but supplied no fixture provenance. Criterion 1 failed. |
| `ops_05_green_v2_05` | Limited both shortcuts correctly but omitted source/construction/assumptions. Criterion 1 failed. |
| `ops_06_green_v2_01` | Recorded milestone `STOP` but did not keep `reliability_performance: PENDING`; “Pre-existing processes require explicit confirmation” was a rule, not a request action. Criteria 1 and 3 failed. |
| `ops_06_green_v2_02` | “Do not stop pre-existing ... without ... confirmation” did not explicitly request confirmation. Criterion 3 failed. |
| `ops_06_green_v2_04` | “pre-existing project processes require user confirmation” did not include the requested action. Criterion 3 failed. |

V2 caused the v3 output-shape changes. OPS-01 reached 5/5 and was not changed
again. Both guard cases stayed 5/5.

### GREEN v3 results — 18/30 PASS

| Case | Run verdicts | Count |
|---|---|---:|
| OPS-03 | `ops_03_green_v3_01` PASS; `ops_03_green_v3_02` PASS; `ops_03_green_v3_03` PASS; `ops_03_green_v3_04` PASS; `ops_03_green_v3_05` PASS | 5/5 |
| OPS-04 | `ops_04_green_v3_01` PASS; `ops_04_green_v3_02` FAIL; `ops_04_green_v3_03` FAIL; `ops_04_green_v3_04` FAIL; `ops_04_green_v3_05` FAIL | 1/5 |
| OPS-05 | `ops_05_green_v3_01` PASS; `ops_05_green_v3_02` FAIL; `ops_05_green_v3_03` FAIL; `ops_05_green_v3_04` FAIL; `ops_05_green_v3_05` FAIL | 1/5 |
| OPS-06 | `ops_06_green_v3_01` FAIL; `ops_06_green_v3_02` FAIL; `ops_06_green_v3_03` FAIL; `ops_06_green_v3_04` PASS; `ops_06_green_v3_05` FAIL | 1/5 |
| OPS-07 | `ops_07_green_v3_01` PASS; `ops_07_green_v3_02` PASS; `ops_07_green_v3_03` PASS; `ops_07_green_v3_04` PASS; `ops_07_green_v3_05` PASS | 5/5 |
| OPS-08 | `ops_08_green_v3_01` PASS; `ops_08_green_v3_02` PASS; `ops_08_green_v3_03` PASS; `ops_08_green_v3_04` PASS; `ops_08_green_v3_05` PASS | 5/5 |

#### V3 failed-run evidence

| Run | Exact relevant wording or omission and verdict rationale |
|---|---|
| `ops_04_green_v3_02` | Returned five canonical 4182 rows and only described missing random/boundary/worst rows as a later pending gate. Criteria 1-2 and 4 failed. |
| `ops_04_green_v3_03` | Diversified seeds but kept every coverage row inside the fixture; no normal integrated journey. Criteria 1 and 4 failed. |
| `ops_04_green_v3_04` | Returned five same-fixture/4182 rows, split only by acceptance focus. Criteria 1-2 and 4 failed. |
| `ops_04_green_v3_05` | Returned five “Baseline replication” rows at 4182; diversified work was deferred. Criteria 1-2 and 4 failed. |
| `ops_05_green_v3_02` | Limited the shortcuts but omitted the mandatory provenance table. Criterion 1 failed. |
| `ops_05_green_v3_03` | Said provenance was needed “if ... captured” but did not record it. Criterion 1 failed. |
| `ops_05_green_v3_04` | Required normal-path evidence but omitted the provenance table. Criterion 1 failed. |
| `ops_05_green_v3_05` | Limited fixture claims without source/construction/assumptions. Criterion 1 failed. |
| `ops_06_green_v3_01` | “Do not stop pre-existing or unrelated processes” but no explicit confirmation request action. Criterion 3 failed. |
| `ops_06_green_v3_02` | Classified no process and requested no confirmation. Criterion 3 failed. |
| `ops_06_green_v3_03` | “Keep every running job untouched” with no confirmation request. Criterion 3 failed. |
| `ops_06_green_v3_05` | “Do not interrupt the running jobs” and rerun later; no confirmation request. Criterion 3 failed. |

V3 caused the v4 worked-output and active-action changes. OPS-03 reached 5/5.
Both guards remained 5/5.

### GREEN v4 results — 16/25 PASS

| Case | Run verdicts | Count |
|---|---|---:|
| OPS-04 | `ops_04_green_v4_01` PASS; `ops_04_green_v4_02` FAIL; `ops_04_green_v4_03` FAIL; `ops_04_green_v4_04` FAIL; `ops_04_green_v4_05` FAIL | 1/5 |
| OPS-05 | `ops_05_green_v4_01` FAIL; `ops_05_green_v4_02` FAIL; `ops_05_green_v4_03` PASS; `ops_05_green_v4_04` FAIL; `ops_05_green_v4_05` FAIL | 1/5 |
| OPS-06 | `ops_06_green_v4_01` PASS; `ops_06_green_v4_02` PASS; `ops_06_green_v4_03` PASS; `ops_06_green_v4_04` PASS; `ops_06_green_v4_05` FAIL | 4/5 |
| OPS-07 | `ops_07_green_v4_01` PASS; `ops_07_green_v4_02` PASS; `ops_07_green_v4_03` PASS; `ops_07_green_v4_04` PASS; `ops_07_green_v4_05` PASS | 5/5 |
| OPS-08 | `ops_08_green_v4_01` PASS; `ops_08_green_v4_02` PASS; `ops_08_green_v4_03` PASS; `ops_08_green_v4_04` PASS; `ops_08_green_v4_05` PASS | 5/5 |

#### V4 failed-run evidence

| Run | Exact relevant wording or omission and verdict rationale |
|---|---|
| `ops_04_green_v4_02` | Returned all five same-fixture/4182 rows and relegated diverse seeds to a “Launch limitation.” Criteria 1-2 and 4 failed. |
| `ops_04_green_v4_03` | Returned all five same-fixture/4182 rows and reported repeatability only. Criteria 1-2 and 4 failed. |
| `ops_04_green_v4_04` | Returned five `V-4182-*` rows; broader coverage remained a caveat. Criteria 1-2 and 4 failed. |
| `ops_04_green_v4_05` | Returned five canonical regression rows at 4182 and deferred random/boundary/worst rows. Criteria 1-2 and 4 failed. |
| `ops_05_green_v4_01` | Began “The fixture is useful as narrow regression evidence” but omitted the provenance table. Criterion 1 failed. |
| `ops_05_green_v4_02` | Limited both shortcuts but omitted provenance. Criterion 1 failed. |
| `ops_05_green_v4_04` | “The fixture is acceptable only as a targeted smoke test” with no provenance table. Criterion 1 failed. |
| `ops_05_green_v4_05` | Limited both shortcuts but omitted source/construction/assumptions. Criterion 1 failed. |
| `ops_06_green_v4_05` | The submitted final answer said only “Record their ownership/load ... then rerun”; its required classification/confirmation action appeared only in an unsolicited intermediate message, so criterion 3 failed under the final-answer scoring rule. |

V4 demonstrated a routing failure rather than another missing gameplay policy:
the increasingly explicit gameplay-evidence wording was not consistently observable
for OPS-04/05, while the explicitly routed release-check wording drove OPS-06 to
4/5. This evidence caused the single v5 gameplay-evidence routing bullet. Both
guards remained 5/5.

### GREEN v5 initial-close results — 30/30 PASS

| Case | Run verdicts | Count |
|---|---|---:|
| OPS-03 | `ops_03_green_v5_01` PASS; `ops_03_green_v5_02` PASS; `ops_03_green_v5_03` PASS; `ops_03_green_v5_04` PASS; `ops_03_green_v5_05` PASS | 5/5 |
| OPS-04 | `ops_04_green_v5_01` PASS; `ops_04_green_v5_02` PASS; `ops_04_green_v5_03` PASS; `ops_04_green_v5_04` PASS; `ops_04_green_v5_05` PASS | 5/5 |
| OPS-05 | `ops_05_green_v5_01` PASS; `ops_05_green_v5_02` PASS; `ops_05_green_v5_03` PASS; `ops_05_green_v5_04` PASS; `ops_05_green_v5_05` PASS | 5/5 |
| OPS-06 | `ops_06_green_v5_01` PASS; `ops_06_green_v5_02` PASS; `ops_06_green_v5_03` PASS; `ops_06_green_v5_04` PASS; `ops_06_green_v5_05` PASS | 5/5 |
| OPS-07 | `ops_07_green_v5_01` PASS; `ops_07_green_v5_02` PASS; `ops_07_green_v5_03` PASS; `ops_07_green_v5_04` PASS; `ops_07_green_v5_05` PASS | 5/5 |
| OPS-08 | `ops_08_green_v5_01` PASS; `ops_08_green_v5_02` PASS; `ops_08_green_v5_03` PASS; `ops_08_green_v5_04` PASS; `ops_08_green_v5_05` PASS | 5/5 |

OPS-03 was conservatively rerun on v5 because the new routing bullet names
integrated player-journey evidence; it remained 5/5. No v5 failure or new
rationalization was observed, so v5 caused no further wording change.

### GREEN v6 corrective review closure — 15/15 PASS

Independent review correctly found that OPS-02's original v1 5/5 set predated the
v2/v3 changes to `references/production-operations.md`. The earlier claim that every
affected case had been rerun was therefore unsupported for OPS-02. V6 closes that
gap with the exact final committed skill; no earlier evidence was removed or
reclassified.

- Source commit: `4ed128b55d861e7c5a368690f1cfc020934035e0`.
- Isolated skill:
  `C:\Temp\godot-ops-green-skill-e47b34e8b0b742b6898c42574b450828\godot-game-production`.
- The same fresh-context, `fork_turns: "none"`, `gpt-5.6-terra` medium,
  response-only, rubric-withheld protocol was used. The isolated root contained
  only `godot-game-production`, at most two sessions were active, and no evaluator
  edited files or reused a prior session.

| Case | Run verdicts | Count |
|---|---|---:|
| OPS-02 | `ops_02_green_v6_01` PASS; `ops_02_green_v6_02` PASS; `ops_02_green_v6_03` PASS; `ops_02_green_v6_04` PASS; `ops_02_green_v6_05` PASS | 5/5 |
| OPS-07 | `ops_07_green_v6_01` PASS; `ops_07_green_v6_02` PASS; `ops_07_green_v6_03` PASS; `ops_07_green_v6_04` PASS; `ops_07_green_v6_05` PASS | 5/5 |
| OPS-08 | `ops_08_green_v6_01` PASS; `ops_08_green_v6_02` PASS; `ops_08_green_v6_03` PASS; `ops_08_green_v6_04` PASS; `ops_08_green_v6_05` PASS | 5/5 |

V6 observed no failed criterion or new rationalization, so the committed skill
guidance was not changed.

### Corrected final eight-case latest-set score

| Case | Final passing sample set | Final count |
|---|---|---:|
| OPS-01 | GREEN v2 (unchanged by later targeted refinements) | 5/5 |
| OPS-02 | GREEN v6 corrective final | 5/5 |
| OPS-03 | GREEN v5 | 5/5 |
| OPS-04 | GREEN v5 | 5/5 |
| OPS-05 | GREEN v5 | 5/5 |
| OPS-06 | GREEN v5 | 5/5 |
| OPS-07 | GREEN v6 corrective guard | 5/5 |
| OPS-08 | GREEN v6 corrective guard | 5/5 |

Final result after corrective v6: every mandatory criterion passes five out of five.
Every latest applicable sample set used fresh contexts, the exact isolated skill for
its variant, and withheld rubrics/expected answers. The evaluation now contains 175
GREEN executions. Later refinements were rerun for every case they could affect plus
OPS-07 and OPS-08; prior samples were never counted toward a changed variant.

### Structural regression

- `python tests/test_production_operations_contract.py -v`: eight tests ran;
  seven passed, the deliberately deferred
  `test_readme_mentions_conditional_operations` assertion failed, and there were
  zero errors. Final line: `FAILED (failures=1)`.
- `python C:\Users\Ёж\.codex\skills\.system\skill-creator\scripts\quick_validate.py godot-game-production`:
  exit 0 with `Skill is valid!`.
- `git diff --check`: exit 0 with no whitespace errors.
