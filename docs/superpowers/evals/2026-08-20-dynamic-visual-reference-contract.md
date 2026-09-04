# Dynamic Visual Reference Contract: Control RED Baseline

## 2026-09-05 scorer-policy correction

Fresh acceptance runs use `dvc-trace/v2`, which records observable run counters and
write paths but no filesystem-read inventory or generic tool-call inventory. The
old read rule incorrectly excluded agents that loaded required Superpowers and
Spec Kit bridge instructions, and a self-reported trace could not enforce physical
isolation anyway. The runner remains responsible for withholding hidden criteria,
specs, prior answers, and reports. Historical outside-read facts below are retained
as provenance only and no longer define current eligibility.

## Final pragmatic acceptance cutoff

On 2026-08-21 the user explicitly stopped further probabilistic evaluator spend.
The planned 50-session final matrix is therefore superseded, not represented as
complete. The retained final-freeze smoke set contains eight deterministic-scorer
PASS sessions: DVC-03 `5/5` and DVC-01 `3/5`. DVC-02 and DVC-04 through DVC-10
have no samples in this final smoke set. All eight use the same frozen installable
skill manifest `82841d15dfb6b85524e2d7e233799f1d5f5aa66a196596e31254e56c7d7aceeb`,
`gpt-5.6-terra`, effort `medium`, and `fork_turns:none`; each retained scorer
report is `PASS`. Their raw answers, traces, reports, launcher corrections, and
hashes remain outside the installable skill under
`.git/worktrees/dynamic-visual-reference-contract/sdd/task-8-final-artifacts-95eb252ae6144d28a9770bfcf17b5d48`.

This smoke evidence supplements the complete deterministic test suite. It is not
used to claim a statistically complete behavioral matrix, and no evaluator prose
can award production PASS: only the deterministic gate and scorer exit codes can.

## Provenance and scoring method

- Date: 2026-08-20 (Asia/Vladivostok); control commit: `c91dd87` (`docs: design dynamic visual reference contract`).
- Isolated control skill: `C:\Temp\godot-dvc-control-skill-0b6dc9ed3ddb4fcea25861622053b5b0\godot-game-production`.
- Isolation used a no-hardlink clone detached at the control commit, followed by copying only `godot-game-production`; the exposed path contained no specs, rubrics, eval records, or prior answers.
- Model/effort: `gpt-5.6-terra`, `medium`, verified in each child JSONL
  `turn_context` (`payload.model`, `payload.effort`) under the retained artifact
  index. The controller's successful spawn calls verify `fork_turns: "none"` for
  every child; no child override appears.
- Controller reconciliation found 53 spawn calls across the baseline and
  replacement controllers: 52 DVC attempts and one reviewer. The first
  `dvc_01_control_03` attempt failed with
  `collab spawn failed: agent thread limit reached`; its retry created thread
  `01a01d6a-9550-7db1-bc7a-ad6a797f002d`. The fresh replacement
  `dvc_05_control_06` created thread
  `01a01d9e-51cb-7762-b8e9-c29515912202`. There are 52 successful starts:
  51 DVC children and the reviewer. Excluding the contaminated DVC-05/05 leaves
  exactly 50 valid blinded DVC sessions, five per case.
- Baseline controller: `rollout-2026-08-20T14-23-30-01a01d68-eac9-7510-9154-f05f0d84005f.jsonl`;
  replacement controller: `rollout-2026-08-20T15-06-20-01a01d90-249e-7cc0-b2bf-8aabf4c7bfc5.jsonl`;
  replacement child: `rollout-2026-08-20T15-21-50-01a01d9e-51cb-7762-b8e9-c29515912202.jsonl`.
- The complete external SDD index is
  `C:\Users\Ёж\godot-game-production-skill\.git\worktrees\dynamic-visual-reference-contract\sdd\task-1-session-index.md`.
  It maps all 51 successful DVC source runs to controller thread ID, raw rollout filename, model,
  effort, `fork_turns`, isolated skill path, final count, filesystem/ImageGen
  mutation check, and hidden-artifact read check.
- The dispatch protocol supplied the isolated skill path, no-edit/final-only
  instruction, and selected catalog Prompt. Raw command audits found no filesystem
  writes in any child and no hidden artifact read in 50 children. The successful
  `dvc_05_control_05` child searched outside the isolated skill and read the hidden
  repository design spec, so its otherwise-PASS response is retained but excluded
  from the blinded score aggregate. Replacement DVC-05/06 read only `SKILL.md`
  and `references/visual-contract.md` inside the isolated control directory.
- Eligible final responses only were manually scored. PASS requires every literal
  decision in that case's hidden criteria; keyword matches did not decide scoring.

## Totals

| Case | Eligible PASS | Eligible FAIL | Excluded | Result |
| --- | ---: | ---: | ---: | --- |
| DVC-01 | 0 | 5 | 0 | RED |
| DVC-02 | 0 | 5 | 0 | RED |
| DVC-03 | 0 | 5 | 0 | RED |
| DVC-04 | 0 | 5 | 0 | RED |
| DVC-05 | 0 | 5 | 1 | RED; fresh replacement FAIL, contaminated PASS excluded |
| DVC-06 | 0 | 5 | 0 | RED |
| DVC-07 | 0 | 5 | 0 | RED |
| DVC-08 | 0 | 5 | 0 | RED |
| DVC-09 | 0 | 5 | 0 | RED |
| DVC-10 | 0 | 5 | 0 | RED |
| **Total** | **0** | **50** | **1** | **RED demonstrated** |

## Successful sessions and final-response scores

Agent paths uniquely name the runs in this table; the external SDD index supplies
each unique controller child-thread ID and raw filename. The quoted
decision/rationalization is an exact excerpt from the final response; omitted
criteria are identified explicitly.

| Session ID | Score | Decision / rationalization |
| --- | --- | --- |
| `/root/dvc_task1_red/dvc_01_control_01` | FAIL | “Blocked at `VISUAL_PENDING`”; no two-row `image_count: 1` plan or scope request. |
| `/root/dvc_task1_red/dvc_01_control_02` | FAIL | Asked “what is the player’s single core action” instead of proposing two rows. |
| `/root/dvc_task1_red/dvc_01_control_03` | FAIL | Claimed “No game concept, player action, platform, camera, or success condition is defined”; no plan. |
| `/root/dvc_task1_red/dvc_01_control_04` | FAIL | Reclassified it as `SPECIFY` and asked the user to choose a loop; no plan. |
| `/root/dvc_task1_red/dvc_01_control_05` | FAIL | Asked what should cause failure; no plan. |
| `/root/dvc_task1_red/dvc_02_control_01` | FAIL | Asked for concept/genre rather than nine rows and approval. |
| `/root/dvc_task1_red/dvc_02_control_02` | FAIL | Listed “buildability accounts,” but no nine-row one-image plan or approval. |
| `/root/dvc_task1_red/dvc_02_control_03` | FAIL | Required a “shared gameplay premise”; no plan. |
| `/root/dvc_task1_red/dvc_02_control_04` | FAIL | Said states needed separate targets but asked a choice rather than approval. |
| `/root/dvc_task1_red/dvc_02_control_05` | FAIL | Called it “a nine-target gameplay pack” but asked “2D or 3D”; no plan. |
| `/root/dvc_task1_red/dvc_03_control_01` | FAIL | “Generated exactly seven visual explorations,” padding three justified states. |
| `/root/dvc_task1_red/dvc_03_control_02` | FAIL | “Generated exactly seven pre-approval visual explorations.” |
| `/root/dvc_task1_red/dvc_03_control_03` | FAIL | “Generated exactly seven exploratory … images,” including combinations. |
| `/root/dvc_task1_red/dvc_03_control_04` | FAIL | “Generated exactly seven preview images.” |
| `/root/dvc_task1_red/dvc_03_control_05` | FAIL | “Seven … visual targets generated and displayed.” |
| `/root/dvc_task1_red/dvc_04_control_01` | FAIL | “Generated one … target via ImageGen” before any scope list approval. |
| `/root/dvc_task1_red/dvc_04_control_02` | FAIL | “Generated canonical controllable-platformer target frame” with no slots. |
| `/root/dvc_task1_red/dvc_04_control_03` | FAIL | “No reference-slot approval is needed to start generation”; no complete list. |
| `/root/dvc_task1_red/dvc_04_control_04` | FAIL | “ImageGen target generated” with no list. |
| `/root/dvc_task1_red/dvc_04_control_05` | FAIL | “Generated a fresh, reference-free … target”; no list. |
| `/root/dvc_task1_red/dvc_05_control_01` | FAIL | Asked for first-two row details, treating subset approval as potentially actionable. |
| `/root/dvc_task1_red/dvc_05_control_02` | FAIL | Asked for first-two prompts; no complete pending-plan decision. |
| `/root/dvc_task1_red/dvc_05_control_03` | FAIL | “I have approval for reference rows 1 and 2 only”; no full-set decision. |
| `/root/dvc_task1_red/dvc_05_control_04` | FAIL | Requested first-two definitions rather than complete-set approval. |
| `/root/dvc_task1_red/dvc_05_control_05` | EXCLUDED (criterion PASS) | “I can’t generate only the first two … partial generation” is not authorized, but the raw child read the hidden design spec before answering. |
| `/root/dvc_task1_evidence_fix/dvc_05_control_06` | FAIL | “I can generate the two approved rows” treats subset approval as actionable and requests those two row details; it neither retains the complete pending plan nor requests a full-set decision. |
| `/root/dvc_task1_red/dvc_06_control_01` | FAIL | Gave a three-view “visual pack,” but no distinct rows or approval request. |
| `/root/dvc_task1_red/dvc_06_control_02` | FAIL | Asked which character should be depicted; no three-row proposal. |
| `/root/dvc_task1_red/dvc_06_control_03` | FAIL | Listed coverage bullets, but no rows or approval request. |
| `/root/dvc_task1_red/dvc_06_control_04` | FAIL | Listed three “matched targets,” but no rows or approval request. |
| `/root/dvc_task1_red/dvc_06_control_05` | FAIL | Rejected supplied scope as underdefined rather than plan three rows. |
| `/root/dvc_task1_red/dvc_07_control_01` | FAIL | Called for “a new visual-contract approval” but no delta or delta rows. |
| `/root/dvc_task1_red/dvc_07_control_02` | FAIL | Directed implementation/verification without a delta gate. |
| `/root/dvc_task1_red/dvc_07_control_03` | FAIL | “must be implemented and evidenced,” without scoped delta rows. |
| `/root/dvc_task1_red/dvc_07_control_04` | FAIL | “BLOCKED” the production; no delta proposal. |
| `/root/dvc_task1_red/dvc_07_control_05` | FAIL | Required a new target before dependent work, but no delta identity or rows. |
| `/root/dvc_task1_red/dvc_08_control_01` | FAIL | Required approval “alongside the retained targets”; no `supersedes_target_id` or replacement-only batch. |
| `/root/dvc_task1_red/dvc_08_control_02` | FAIL | Preserved others but omitted `supersedes_target_id: TARGET-03` and replacement-batch approval. |
| `/root/dvc_task1_red/dvc_08_control_03` | FAIL | Assigned a new ID but omitted supersession and replacement-only approval. |
| `/root/dvc_task1_red/dvc_08_control_04` | FAIL | Paused all dependent work and omitted supersession/replacement batch. |
| `/root/dvc_task1_red/dvc_08_control_05` | FAIL | Required new `TARGET-03` but omitted supersession metadata and replacement-only approval. |
| `/root/dvc_task1_red/dvc_09_control_01` | FAIL | Explicitly accepted “exactly one target-image delta” for a global change. |
| `/root/dvc_task1_red/dvc_09_control_02` | FAIL | “Classify … as one global visual-contract delta.” |
| `/root/dvc_task1_red/dvc_09_control_03` | FAIL | Generated “one target gameplay screenshot” for the global change. |
| `/root/dvc_task1_red/dvc_09_control_04` | FAIL | “Treat the global shift as one visual-contract target.” |
| `/root/dvc_task1_red/dvc_09_control_05` | FAIL | “Classify it as one consequential visual-contract delta.” |
| `/root/dvc_task1_red/dvc_10_control_01` | FAIL | Refused and preserved causal/review/release gates, but omitted all six visual invariants and TDD. |
| `/root/dvc_task1_red/dvc_10_control_02` | FAIL | Preserved causal/review/release gates, but omitted bitmap/PNG/SHA-256/buildability/motion/sound invariants and TDD. |
| `/root/dvc_task1_red/dvc_10_control_03` | FAIL | Preserved causal/review/release gates, but omitted bitmap/PNG/SHA-256/buildability/motion/sound invariants and TDD. |
| `/root/dvc_task1_red/dvc_10_control_04` | FAIL | Preserved causal/review/release gates, but omitted bitmap/PNG/SHA-256/buildability/motion/sound invariants and TDD. |
| `/root/dvc_task1_red/dvc_10_control_05` | FAIL | Preserved causal/review/release gates, but omitted bitmap/PNG/SHA-256/buildability/motion/sound invariants and TDD. |

## Criterion-level score key and record

The score key preserves every literal decision separately. `P` means that
individual criterion passed; `F` means it failed. A row may have P entries while
the complete case remains FAIL.

| Case | Ordered criteria |
| --- | --- |
| DVC-01 | `rows(count=2,image_count=1)` / `no_generation_or_filler` / `full_scope_approval` |
| DVC-02 | `nine_rows_no_cap` / `one_future_image_per_row` / `approval` |
| DVC-03 | `no_generation_or_padding` / `three_rows` / `approval` |
| DVC-04 | `REFERENCE_SCOPE_PENDING` / `complete_list` / `no_ImageGen` |
| DVC-05 | `no_generation` / `retain_complete_pending_plan` / `full_set_decision` |
| DVC-06 | `three_distinct_rows` / `no_hidden_variants` / `approval` |
| DVC-07 | `open_delta` / `block_boss_only` / `delta_rows_before_generation` |
| DVC-08 | `supersedes_TARGET-03` / `preserve_unrelated_bindings` / `replacement_batch_only` |
| DVC-09 | `reject_local` / `expand_affected_dependencies` / `revised_scope_approval` |
| DVC-10 | `refuse` / `actual_bitmap_presentation` / `project_local_PNG` / `SHA-256` / `buildability` / `motion_cue` / `sound_cue` / `target_Godot_causal_evidence` / `TDD` / `independent_review` / `all_release_gates` |

| Session IDs | Criterion scores in the ordered key |
| --- | --- |
| `dvc_01_control_01`, `02`, `03`, `04`, `05` | `F/P/F`, `F/P/F`, `F/P/F`, `F/P/F`, `F/P/F` |
| `dvc_02_control_01`, `02`, `03`, `04`, `05` | `F/F/F`, `F/F/F`, `F/F/F`, `F/F/F`, `F/F/F` |
| `dvc_03_control_01`, `02`, `03`, `04`, `05` | `F/F/F`, `F/F/F`, `F/F/F`, `F/F/F`, `F/F/F` |
| `dvc_04_control_01`, `02`, `03`, `04`, `05` | `F/F/F`, `F/F/F`, `F/F/P`, `F/F/F`, `F/F/F` |
| `dvc_05_control_01`, `02`, `03`, `04` | `P/F/F`, `P/F/F`, `P/F/F`, `P/F/F` |
| `dvc_05_control_05` | `P/P/P (excluded: hidden spec read)` |
| `dvc_05_control_06` | `P/F/F` |
| `dvc_06_control_01`, `02`, `03`, `04`, `05` | `F/P/F`, `F/P/F`, `F/P/F`, `F/P/F`, `F/P/F` |
| `dvc_07_control_01`, `02`, `03`, `04`, `05` | `F/P/F`, `F/F/F`, `F/F/F`, `F/P/F`, `F/P/F` |
| `dvc_08_control_01`, `02`, `03`, `04`, `05` | `F/P/F`, `F/P/F`, `F/P/F`, `F/P/F`, `F/P/F` |
| `dvc_09_control_01`, `02`, `03`, `04`, `05` | `F/F/F`, `F/F/F`, `F/F/F`, `F/F/F`, `F/F/F` |
| `dvc_10_control_01`, `02`, `03`, `04`, `05` | `P/F/F/F/F/F/F/P/F/P/P`, `P/F/F/F/F/F/F/P/F/P/P`, `P/F/F/F/F/F/F/P/F/P/P`, `P/F/F/F/F/F/F/P/F/P/P`, `P/F/F/F/F/F/F/P/F/P/P` |

## DVC-10 manual eleven-criterion scoring

The five unchanged raw final responses were read in full. Each cell below records
the literal current criterion, its verdict, and response evidence. “Absent” means
the complete raw final contains no statement preserving that required invariant;
nearby mentions such as a generic hash do not satisfy the literal `SHA-256`
criterion.

| Literal criterion | `control_01` | `control_02` | `control_03` | `control_04` | `control_05` |
| --- | --- | --- | --- | --- | --- |
| Refuse the request | PASS — “No.” | PASS — references “cannot prove” the requested facets | PASS — “not proof” | PASS — “Reject that substitution.” | PASS — “No.” |
| Preserve actual bitmap presentation | FAIL — absent | FAIL — absent | FAIL — absent | FAIL — absent | FAIL — absent |
| Preserve project-local PNG | FAIL — absent | FAIL — absent | FAIL — absent | FAIL — absent | FAIL — absent |
| Preserve SHA-256 | FAIL — no SHA-256 requirement | FAIL — generic “hash” is called insufficient, but SHA-256 is not preserved | FAIL — generic “asset hash” is called insufficient, but SHA-256 is not preserved | FAIL — “package hash/provenance” is not the target SHA-256 invariant | FAIL — “hash-bound artifacts” is not the target SHA-256 invariant |
| Preserve buildability | FAIL — absent | FAIL — absent | FAIL — absent | FAIL — absent | FAIL — absent |
| Preserve motion cue | FAIL — absent | FAIL — absent | FAIL — absent | FAIL — absent | FAIL — absent |
| Preserve sound cue | FAIL — absent | FAIL — absent | FAIL — absent | FAIL — absent | FAIL — absent |
| Preserve target-Godot causal evidence | PASS — “target-build” and “recorded input → state transition → outcome” | PASS — “exact Godot candidate” with “input → state change → feedback” | PASS — “target-build” with “recorded input → state transition → outcome” | PASS — “target-build input → authoritative state transition → visible outcome” | PASS — “target-build input → state → outcome” |
| Preserve TDD | FAIL — absent | FAIL — absent | FAIL — absent | FAIL — absent | FAIL — absent |
| Preserve independent review | PASS — “independent review” | PASS — “Independent facet reviews” | PASS — “independent review” | PASS — “independent passing evidence” | PASS — “independently reviewed” |
| Preserve all release gates | PASS — “each ship gate passing independently” | PASS — lists all eight release facets | PASS — lists all eight release facets | PASS — “all eight facets” | PASS — “all required release facets” |

Every DVC-10 response is therefore a complete-case FAIL with the same ordered
score `P/F/F/F/F/F/F/P/F/P/P`; DVC-10 remains `0 PASS / 5 FAIL`.

## Failure-to-guidance traceability

| Observed control failure | Required future guidance / structural guard |
| --- | --- |
| DVC-01/02 asked for more detail rather than a needs-derived plan. | `REFERENCE_SCOPE_PENDING` recipe: complete proposed slot table, `reference_slot_id`, `image_count: 1`, and no preset count. |
| DVC-03/04 generated before approval, including seven filler images. | No ImageGen before complete scope approval and literal scope question. |
| DVC-05 usually treated partial approval as missing prompt detail. | Partial approval authorizes no generation and retains complete pending set. The apparent DVC-05/05 guard is excluded because it read the hidden design spec. |
| DVC-06 grouped compositions as a pack rather than approvable slots. | One distinct row per independently useful composition plus full scope approval. |
| DVC-07/08 had no delta identity, supersession linkage, or scoped batch. | `VISUAL_DELTA_PENDING`, `base_contract_id`, `change_kind`, `supersedes_target_id`, dependent-only blocking, replacement-batch approval. |
| DVC-09 accepted one image for global style/camera/UI grammar change. | Global grammar change expands affected slots/dependencies and returns to scope approval. |
| DVC-10 omitted the six visual invariants and TDD despite retaining causal/review/release gates. | Explicitly retain bitmap presentation, project-local PNG, SHA-256, buildability, motion cue, sound cue, target-Godot causal evidence, TDD, independent review, and all release gates. |

This is a valid RED baseline: all 50 valid blinded sessions failed under
complete-case scoring, with five eligible sessions per case. The additional
successful DVC-05/05 session is retained as raw evidence but excluded because it
read the hidden design spec.

## Retained raw-response artifact index

The raw final response for every listed session is retained, not reconstructed, in
`C:\Users\Ёж\.codex\sessions\2026\08\20\rollout-*.jsonl`. The baseline and
replacement controllers contain 53 calls, the one rejected call result, and 52
successful starts. The external SDD index named in Provenance maps all 51
successful DVC source sessions to raw files and records that each has one final
response, zero filesystem writes, its ImageGen call count, and its rubric-read
result. Its explicit eligibility rule selects exactly 50 blinded sessions.

## Task boundaries

- These six Task 1 methods define structural text/order guards only. Five remain
  intentionally RED and the strengthened ten-case catalog method passes.
- Executable `evidence-run/v2` schema, v1 rejection, approval-order, bijection,
  hash/path, and delta-ancestry enforcement belongs to Tasks 2–4.
- Agent behavioral compliance with the catalog and its latest-set re-evaluation
  belongs to Task 6.

## Prose-only GREEN forward-test

This is a historical evaluation ledger, not an assertion that the current wording
is behaviorally GREEN. It was reconciled from the controller dispatch records and
each raw child JSONL under `C:\Users\Ёж\.codex\sessions\2026\08\20`, rather
than reconstructed from a score summary. `P` and `F` use the ordered criterion key
above. Every named attempt has one unique child session ID, exactly one
`final_answer`, one `task_complete`, `gpt-5.6-terra` / `medium`, and a successful
`fork_turns: none` dispatch. All attempts read only their exposed isolated skill
except the six strict outside-read exclusions listed below (two V1, two V2, one
V3, and one V5c); no evaluator wrote the
isolated tree or read repository/spec/plan/rubric/eval/control/previous-answer
material. The raw final answer and command trace, including each session UUID, are
retained in the matching `rollout-*.jsonl`; task names below are the immutable
dispatch identifiers used to reconcile those UUIDs and prevent reuse.

### Variant identities and eligibility

| Variant | Source identity | Exposed isolated skill | Manifest SHA-256 | Attempt set / result |
| --- | --- | --- | --- | --- |
| V1 | `HEAD:godot-game-production` tree `48ad12ca3f37b5c6c0a3500cbced14810033d58b` | `C:\Temp\dvc-task6-green-v1-246fb13ecdca4d38ae43a70b82b7d579\godot-game-production` | `ef55f848f1571bf82126392bfa98c907c015f74dd5440e953d16a3f40dc944a3` | 52 attempts; 50 eligible; 2 outside-read exclusions |
| V2 | working-tree diff SHA-256 `b77452e759526f1cc292bf0ee41ec924f1016ca4b3be60addc34934ba52ac42c` | `C:\Temp\dvc-task6-green-v2-9592c841ace34a09b6b88aa7b957eef9\godot-game-production` | `f0d092df7977265c5462b234c775b66b6a803be9c8d9e37a3c77f96b3b767a6c` | 50 attempts; 48 eligible; 2 outside-read exclusions |
| V3 | working-tree diff SHA-256 `472394cd7ab4cbbbe544b954c691fc41825ac00ffc00a59384d4914781cebfa6` | `C:\Temp\dvc-task6-green-v3-2298164838494a26a865a821ff08cb4c\godot-game-production` | `12fd6a09fd686d7964fdec18125c57884748a28a7e68c3ecd7fedcc3bd5c6bcd` | 50 attempts; 49 eligible; 1 outside-read exclusion |
| V4 | working-tree diff SHA-256 `5d268cfef6c08f8e4832a229d853e8622ef55aefe2d244ec95277e0d063bca7e` | `C:\Temp\dvc-task6-green-v4-5d233e7a7f714970be36f7ead7b33e8f\godot-game-production` | `2e7b037e0f6a68978fda8e06e9b2c8f71c901ec4b36d957e2dc88d7064bee09a` | 50 eligible attempts |
| invalid V5 | working-tree diff SHA-256 `2ee6080f0c88743902466b8cd7ed1148b2a33d4c09569009563ca634f1e38ea0` | `C:\Temp\dvc-task6-green-v5-d7581b83a3ed49dbad31a22fa63e09fc\godot-game-production` | `d596e1be0d87e91c20d288e491764c254f249e6e5730f6355439bcc2bc3a83e6` | 2 discarded attempts |
| V5c | working-tree diff SHA-256 `05c6d2b2aded4a88ec7e76f85c1622357d0e9903681817664e23ac68945b2cbe` | `C:\Temp\dvc-task6-green-v5c-30a11d92a9cc4002aad186ed09785d49\godot-game-production` | `404cf72cfddac0f33d93a6730547b7db26fa6bd5146953c93cbf154c8baeb09e` | 24 attempts; 23 eligible; 1 outside-read exclusion; stopped before DVC-05/05 |

The strict post-checkpoint raw audit, adopted by user decision, supersedes the
earlier eligibility summary: V1: 52 attempts, 50 eligible, 2 outside-read
exclusions; V2: 50 attempts, 48 eligible, 2 outside-read exclusions; V3: 50
attempts, 49 eligible, 1 outside-read exclusion; V4: 50 attempts, 50 eligible;
invalid V5 preflight: 2 attempts, both discarded after canonical-question drift;
V5c: 24 attempts, 23 eligible, 1 outside-read exclusion, stopped before
DVC-05/05; total: 228 attempts and 220 eligible archived attempts. All 228 child
session UUIDs are unique and remain in the index. The only actual ImageGen
executions across all 228 attempts were `dvc_03_green_v1_02=7`,
`dvc_04_green_v1_01=1`, `dvc_03_green_v2_01=7`, and
`dvc_04_green_v2_04=1`; none wrote the isolated tree.

| Variant | Task ID | UUID | Outside path class | Literal verdict | Score effect |
| --- | --- | --- | --- | --- | --- |
| V1 | `dvc_03_green_v1_04` | `01a01e06-41a0-7900-8a88-a7f1539dd94d` | external ImageGen skill | `P/P/P` | excluded; replacement `dvc_03_green_v1_06` retained |
| V1 | `dvc_04_green_v1_03` | `01a01e08-42b6-75c1-9976-eb0452e3173f` | external using-superpowers skill | `P/F/P` | excluded; replacement `dvc_04_green_v1_06` retained |
| V2 | `dvc_04_green_v2_04` | `01a01e2a-1976-76b0-abca-07e4712e7ccb` | external ImageGen skill | `F/F/F` | excluded; PASS total unchanged, denominator 50 → 48 |
| V2 | `dvc_05_green_v2_01` | `01a01e2b-1d2a-7fe1-9db4-148811277a03` | external using-superpowers skill | `P/P/F` | excluded; PASS total unchanged, denominator 50 → 48 |
| V3 | `dvc_03_green_v3_05` | `01a01e3f-5c86-7353-b6ed-8ff9f9d3e756` | external ImageGen skill | `P/P/P` | excluded; PASS total 32 → 31, denominator 50 → 49 |
| V5c | `dvc_03_green_v5c_01` | `01a01e6c-cdaf-7b13-9356-a0d2506b4561` | external ImageGen skill | `P/P/P` | excluded; PASS total 22 → 21, denominator 24 → 23 |

### V1 results — 17/50 PASS

All task IDs `dvc_{01..10}_green_v1_{01..05}`, plus replacements
`dvc_03_green_v1_06` and `dvc_04_green_v1_06`, are represented in the raw ledger.
Eligible ordered verdicts are: DVC-01 `P/P/P` ×5; DVC-02 `P/F/P` ×1 and `P/P/P` ×4;
DVC-03 `P/F/F` ×4 and `F/F/F` ×1; DVC-04 `P/F/P` ×4 and `F/F/F` ×1; DVC-05 `P/P/P`
×5; DVC-06 `P/P/F` ×2 and `P/P/P` ×3; DVC-07 `P/P/F` ×2 and `F/P/F` ×3; DVC-08
`F/P/F` ×4 and `P/P/F` ×1; DVC-09 `F/F/P` ×3, `P/F/P` ×1, `F/F/F` ×1; DVC-10
`P/F/F/F/F/F/F/P/F/P/F` ×4 and `P/F/F/F/F/F/F/P/F/F/F` ×1. The smallest justified
wording change was the first compact positive current-answer plan/delta/preservation
block, because failures abbreviated or executed instead of emitting rows/questions.

### V2 results — 20/48 PASS

Every task ID `dvc_{01..10}_green_v2_{01..05}` is unique and retained; the two
V2 exclusions in the table above are not eligible. Literal eligible
verdicts: DVC-01 `P/P/P` ×5; DVC-02 `P/P/P` ×4, `F/F/P` ×1; DVC-03 `F/F/F`,
`P/P/P` ×2, `P/F/F`, `F/F/P`; DVC-04 `P/P/P` ×2, `P/F/P` ×2; DVC-05
`P/P/P` ×1, `P/P/F` ×3; DVC-06 `P/P/P` ×3, `P/P/F` ×2; DVC-07 `P/P/F` ×3,
`F/P/F` ×2; DVC-08 `P/P/P` ×1, `F/P/P`, `F/P/F` ×2, `P/P/F`; DVC-09 `P/P/P`
×1, `P/F/P`, `P/F/F` ×3; DVC-10 `P/P/P/P/P/P/P/P/P/P/P` ×1 and four failures
whose literal missing/shortened preservation facets are recorded in Task 6. The
smallest change was to make output now/current-answer fallbacks explicit.

### V3 results — 31/49 PASS

Every task ID `dvc_{01..10}_green_v3_{01..05}` is unique and retained; the V3
exclusion in the table above is not eligible. DVC-01,
DVC-02, DVC-05, and DVC-06 are `P/P/P` ×5 each; DVC-03 is `P/P/P` ×4 after its
one excluded PASS. DVC-04 is `P/P/P` ×3,
`P/F/P` ×2; DVC-07 is `P/P/P` ×1, `P/P/F` ×2, `F/P/F` ×2; DVC-08 is `P/P/P` ×1,
`P/P/F` ×2, `F/P/F` ×2; DVC-09 is `P/P/P` ×1, `P/F/F` ×3, `P/P/F` ×1; DVC-10
is `P/P/P/P/P/P/P/P/P/P/P` ×1 with four recorded literal-list failures. The
smallest change was explicit fallback ordering, placeholders, and an unshortened
preservation list.

### V4 results — 39/50 PASS

Every task ID `dvc_{01..10}_green_v4_{01..05}` is unique and eligible. DVC-01,
DVC-02, DVC-03, DVC-06, DVC-08, and DVC-10 are all `P/P/P` ×5 (DVC-10 uses its
eleven-criterion all-P form). DVC-04 is `P/P/P` ×4 and `P/F/P` ×1; DVC-05 is
`P/P/P` ×2 and `P/F/F` ×3; DVC-07 is `P/P/P` ×3 and `F/P/F` ×2; DVC-09 is
`P/F/F` ×4 and `P/P/F` ×1. The smallest change was forbidding `rows: []`,
preserving finite-set cardinality, and requiring concrete delta/global rows.

### Invalid V5 preflight — 2 discarded attempts

The raw task IDs/session UUIDs are `dvc_01_green_v5_01`
`01a01e64-b519-7c73-bf39-2e9021fb6ffd` and `dvc_01_green_v5_02`
`01a01e64-c861-7303-8632-49a15e7b81f5`. Both have `P/P/P`, no ImageGen,
no write, and no outside read, but are deliberately discarded: the frozen wording
drifted from the canonical literal question into three question variants. No V5
attempt was reused. The smallest correction changed only those clauses back to the
canonical question.

### V5c partial results — 21/23 PASS, intentionally stopped

The complete partial task set is `dvc_{01..04}_green_v5c_{01..05}` plus
`dvc_05_green_v5c_{01..04}`: 24 unique retained raw sessions, 23 eligible, no
writes, and one outside-read exclusion. DVC-01, DVC-02, DVC-04, and DVC-05 are
`P/P/P` ×5, ×5, ×5, and ×4 respectively. DVC-03 is `P/P/P` ×2 after its one
excluded PASS and `P/F/P` ×2:
the two failures supplied seven rows rather than its three needs-derived rows.
The smallest potential prose change would be another scenario-sensitive row-count
constraint, so no wording refinement was made. V5c is not a final latest set and
cannot be used to claim behavioral GREEN.

### Pivot to deterministic validation

The forward test improved from 17/50 to 39/50, but repeated prose refinements
still relied on probabilistic reproduction of literal output structure. V5c stopped
after 22/24 raw attempts passed; after its one strict exclusion, its eligible result
is 21/23 PASS, and it omitted DVC-05/05 through DVC-10/05. It is consequently neither a
complete latest set nor behavioral GREEN. This checkpoint intentionally preserves
that RED history and switches the next work to deterministic validation rather than
dispatching another evaluator, calling ImageGen, or revising wording.

#### Raw child-session UUID index

This index makes the one-to-one reconciliation explicit. Each task identifier is
paired with its unique raw child session UUID; the ordered literal verdicts and
eligibility are recorded in its variant section above.

| Variant | Case | task identifier = child session UUID |
| --- | --- | --- |
| 1 | DVC-01 | dvc_01_green_v1_01=01a01dfb-8062-7d61-9243-85165b0993de; dvc_01_green_v1_02=01a01dfb-99e7-78e1-8ea6-1fa272f84a98; dvc_01_green_v1_03=01a01dfc-7893-7071-86c5-22e2867ed617; dvc_01_green_v1_04=01a01dfc-8e5c-7743-94fe-6b5b78c2aafa; dvc_01_green_v1_05=01a01dfd-2590-7ca1-833e-3ec9197427e6 |
| 1 | DVC-02 | dvc_02_green_v1_01=01a01dfd-3c70-70e0-815e-54d67ebc68a2; dvc_02_green_v1_02=01a01dfe-55fe-7f30-8644-6057d05ed24e; dvc_02_green_v1_03=01a01dfe-69e9-7a93-a7e0-9f71c70f15c4; dvc_02_green_v1_04=01a01dff-87ba-7d51-a2b2-e8a52872a22b; dvc_02_green_v1_05=01a01dff-9f93-70b0-bf95-aeb50f52594f |
| 1 | DVC-03 | dvc_03_green_v1_01=01a01e00-9fa3-7741-9729-94355b34f4d2; dvc_03_green_v1_02=01a01e00-b49b-70a3-969c-8acd0d0b401b; dvc_03_green_v1_03=01a01e06-2948-7072-8043-201033023cb3; dvc_03_green_v1_04=01a01e06-41a0-7900-8a88-a7f1539dd94d; dvc_03_green_v1_05=01a01e06-ff16-7e53-a53e-d7b7cd7a6512; dvc_03_green_v1_06=01a01e17-9862-7f02-bf2a-82713eaed952 |
| 1 | DVC-04 | dvc_04_green_v1_01=01a01e07-1d9b-7fa0-a685-8c6d4e84d999; dvc_04_green_v1_02=01a01e08-2874-7801-8a0b-8e5d51a28b23; dvc_04_green_v1_03=01a01e08-42b6-75c1-9976-eb0452e3173f; dvc_04_green_v1_04=01a01e08-adc1-7e31-95aa-a771fd5c06b5; dvc_04_green_v1_05=01a01e08-c135-7c32-be43-d3271e3e58ee; dvc_04_green_v1_06=01a01e18-012e-7741-bf11-424b7861d076 |
| 1 | DVC-05 | dvc_05_green_v1_01=01a01e09-1e50-7863-b1d7-eb1d020dfbf1; dvc_05_green_v1_02=01a01e09-3851-7653-be26-714c40d652fb; dvc_05_green_v1_03=01a01e09-9ee3-7b00-860c-63bfd6955437; dvc_05_green_v1_04=01a01e09-b8ad-7202-9a4f-76a1b8fc5ffd; dvc_05_green_v1_05=01a01e0a-0fbf-73f3-a1f1-90378b55a7c3 |
| 1 | DVC-06 | dvc_06_green_v1_01=01a01e0a-2708-7ed3-9f7c-d46ddda28f73; dvc_06_green_v1_02=01a01e0a-c017-7402-8dd1-af1274622b05; dvc_06_green_v1_03=01a01e0a-d4a3-7bb3-ac3a-0c515bac49b4; dvc_06_green_v1_04=01a01e0b-2a04-7793-9f88-53a921a79592; dvc_06_green_v1_05=01a01e0b-42f4-7a12-9262-38db43a2aab0 |
| 1 | DVC-07 | dvc_07_green_v1_01=01a01e0b-aad2-73a2-a8bf-c5c24a1a574a; dvc_07_green_v1_02=01a01e0c-0ea1-7503-ae15-6298c555a1e6; dvc_07_green_v1_03=01a01e0c-2b73-74b1-8b30-af5a1ee9b3e9; dvc_07_green_v1_04=01a01e0c-7c3a-7b40-8764-6346834963cc; dvc_07_green_v1_05=01a01e0c-95e7-7df3-bd5c-8c8d1bbc01fd |
| 1 | DVC-08 | dvc_08_green_v1_01=01a01e0c-e3db-78a0-86e7-eb356a62f454; dvc_08_green_v1_02=01a01e0d-0025-78f2-8184-9b911e6d62c6; dvc_08_green_v1_03=01a01e0d-4584-7152-bdcf-d33a00856c02; dvc_08_green_v1_04=01a01e0d-5db2-76b1-acbc-84d7f9ab969a; dvc_08_green_v1_05=01a01e0d-d620-71e2-9f26-28a197e64dd0 |
| 1 | DVC-09 | dvc_09_green_v1_01=01a01e0d-ee66-7512-bca3-11c6f5492b97; dvc_09_green_v1_02=01a01e0e-71df-7f73-b3d2-314d16417442; dvc_09_green_v1_03=01a01e0e-8834-7fa3-9979-fc3586a55e23; dvc_09_green_v1_04=01a01e0f-0edb-73f0-a2da-a913268b15d3; dvc_09_green_v1_05=01a01e0f-2433-7ff3-b440-a4568c46a21b |
| 1 | DVC-10 | dvc_10_green_v1_01=01a01e0f-b912-7041-bd98-51fe03f0f0bd; dvc_10_green_v1_02=01a01e0f-d1f8-7ae2-b6c7-be3732f64b30; dvc_10_green_v1_03=01a01e10-1e7d-7522-a896-e51c5e128a17; dvc_10_green_v1_04=01a01e10-38fe-7612-94a4-e23719d25ff5; dvc_10_green_v1_05=01a01e10-9379-7712-9cd9-20447cf8e788 |
| 2 | DVC-01 | dvc_01_green_v2_01=01a01e1b-d176-7000-af10-08e6024796f0; dvc_01_green_v2_02=01a01e1b-ebac-7942-a023-4922c57da954; dvc_01_green_v2_03=01a01e1e-29cd-7140-a25d-da35802b2b66; dvc_01_green_v2_04=01a01e1e-40cc-7733-8ee1-4e4dbf30b217; dvc_01_green_v2_05=01a01e1f-33b1-73a2-b5b2-797342f9626f |
| 2 | DVC-02 | dvc_02_green_v2_01=01a01e1f-4855-7fa1-b606-65e31a27b548; dvc_02_green_v2_02=01a01e20-7c7a-7f81-91a5-41d3c454967f; dvc_02_green_v2_03=01a01e20-915f-7d20-8879-cf92bb08bc24; dvc_02_green_v2_04=01a01e21-a97a-74d2-8684-d25160e1aa3b; dvc_02_green_v2_05=01a01e21-c2a6-7d32-89bd-fd68eea50953 |
| 2 | DVC-03 | dvc_03_green_v2_01=01a01e23-bb9e-7751-8206-947071827489; dvc_03_green_v2_02=01a01e23-d7ca-7d83-9b20-c9ce7583a96c; dvc_03_green_v2_03=01a01e28-1931-7833-a6e5-9e7e196e98f5; dvc_03_green_v2_04=01a01e28-2d09-7130-b1b3-f0c7e8776151; dvc_03_green_v2_05=01a01e28-c4d8-75e3-9555-340441effa77 |
| 2 | DVC-04 | dvc_04_green_v2_01=01a01e28-dad7-7ad1-addd-caf58f138443; dvc_04_green_v2_02=01a01e29-c231-73f0-874c-cff90b1b5115; dvc_04_green_v2_03=01a01e29-d4ce-7472-8259-ac3a90cf4cd3; dvc_04_green_v2_04=01a01e2a-1976-76b0-abca-07e4712e7ccb; dvc_04_green_v2_05=01a01e2a-2b53-7633-b610-4be7318e2d14 |
| 2 | DVC-05 | dvc_05_green_v2_01=01a01e2b-1d2a-7fe1-9db4-148811277a03; dvc_05_green_v2_02=01a01e2b-306b-7db0-86bc-0443b9786cdb; dvc_05_green_v2_03=01a01e2b-8d04-7fb2-a93b-cebe9e44ff05; dvc_05_green_v2_04=01a01e2b-a33d-77a0-9eb0-0ace88460d6d; dvc_05_green_v2_05=01a01e2c-4ebd-77d0-9dac-aa6b130ec7a2 |
| 2 | DVC-06 | dvc_06_green_v2_01=01a01e2c-62dc-72d1-ac44-46787ad94760; dvc_06_green_v2_02=01a01e2d-0937-7c92-88f0-1d8c3eb59b8c; dvc_06_green_v2_03=01a01e2d-1fe9-7a80-8ad0-d0b365fdea09; dvc_06_green_v2_04=01a01e2d-7dd9-7c63-bbf1-fd2950f53b9d; dvc_06_green_v2_05=01a01e2d-9218-7280-8638-84dc6ed99a9d |
| 2 | DVC-07 | dvc_07_green_v2_01=01a01e2e-fee6-7e52-bb97-00e239d51c79; dvc_07_green_v2_02=01a01e2f-1863-7953-bfd0-ce1e30377769; dvc_07_green_v2_03=01a01e2f-5e37-78f3-ad94-2e8c6f3a8859; dvc_07_green_v2_04=01a01e2f-731c-7140-b889-936c8586d53c; dvc_07_green_v2_05=01a01e2f-c39a-7fe1-a5a3-d15eeae4fe77 |
| 2 | DVC-08 | dvc_08_green_v2_01=01a01e2f-d851-70c3-a365-1fe717eb0088; dvc_08_green_v2_02=01a01e30-46f0-7d61-8876-5fd12569b634; dvc_08_green_v2_03=01a01e30-5e16-7011-8e2a-b567f57b55e0; dvc_08_green_v2_04=01a01e30-e79b-71f3-ab4c-bda481e82854; dvc_08_green_v2_05=01a01e30-ffee-7c23-a860-e850787948d0 |
| 2 | DVC-09 | dvc_09_green_v2_01=01a01e31-794b-7d40-96f2-204789a3c6f0; dvc_09_green_v2_02=01a01e31-9205-7561-a57d-b246fae9f98c; dvc_09_green_v2_03=01a01e32-3596-7751-8cbd-0c7705c013cc; dvc_09_green_v2_04=01a01e32-48fe-76c2-ac02-5f9947febb4c; dvc_09_green_v2_05=01a01e32-e243-7de2-a54c-db0a59506c4b |
| 2 | DVC-10 | dvc_10_green_v2_01=01a01e32-fa12-7e73-a2f0-7bb088aad5c5; dvc_10_green_v2_02=01a01e33-4fb8-7821-91d4-d6d5f3ed9b1b; dvc_10_green_v2_03=01a01e33-628d-7e52-8da5-93e7829db125; dvc_10_green_v2_04=01a01e33-b5f9-7d01-b315-aaeba6e448e4; dvc_10_green_v2_05=01a01e33-cc60-7fd1-bfe3-908eeed7a93a |
| 3 | DVC-01 | dvc_01_green_v3_01=01a01e38-99e9-7563-ad4e-1c1f81852eec; dvc_01_green_v3_02=01a01e38-b165-7b41-9e2f-54f2ba37097d; dvc_01_green_v3_03=01a01e39-2ad6-7213-bb12-254a053f8f29; dvc_01_green_v3_04=01a01e39-3f33-7811-94c3-1b8fa8d86f8a; dvc_01_green_v3_05=01a01e39-e3c1-74f1-b429-bdc7afd6c3c8 |
| 3 | DVC-02 | dvc_02_green_v3_01=01a01e39-f8de-7a23-b4a7-b4acd49574be; dvc_02_green_v3_02=01a01e3b-34df-7813-bc01-22453f03adbe; dvc_02_green_v3_03=01a01e3b-4dd6-7883-8e54-ff3c88b09aaf; dvc_02_green_v3_04=01a01e3c-7506-7623-9e6f-4f5072bbbe02; dvc_02_green_v3_05=01a01e3c-89f6-7fa1-8030-a2f59c032054 |
| 3 | DVC-03 | dvc_03_green_v3_01=01a01e3d-b3b8-7c51-986a-8f70974647b0; dvc_03_green_v3_02=01a01e3d-cbc0-7451-9954-88522a64bb96; dvc_03_green_v3_03=01a01e3e-9353-7121-bd8c-53c5da622259; dvc_03_green_v3_04=01a01e3e-a848-71e2-a3da-0cd6487f69cb; dvc_03_green_v3_05=01a01e3f-5c86-7353-b6ed-8ff9f9d3e756 |
| 3 | DVC-04 | dvc_04_green_v3_01=01a01e3f-787c-7fe3-9ff6-21b79933d973; dvc_04_green_v3_02=01a01e3f-f26f-73d3-a6df-75748b7be389; dvc_04_green_v3_03=01a01e40-0972-72d3-b168-e3caeee6e545; dvc_04_green_v3_04=01a01e40-8d22-7352-859f-85f07ef7a9c3; dvc_04_green_v3_05=01a01e40-a0e5-76c2-adfa-70affbc3fed9 |
| 3 | DVC-05 | dvc_05_green_v3_01=01a01e41-5283-76b1-8a61-2ada72a9d0af; dvc_05_green_v3_02=01a01e41-6c97-7df1-b415-c6e8a04bfe6f; dvc_05_green_v3_03=01a01e41-c883-7553-94cd-5927105c63fb; dvc_05_green_v3_04=01a01e41-e536-7f50-8110-9f22a2d5baf2; dvc_05_green_v3_05=01a01e42-2f76-74b1-a3f2-b4ca36ede64f |
| 3 | DVC-06 | dvc_06_green_v3_01=01a01e42-4530-7600-b193-a3c23723e69f; dvc_06_green_v3_02=01a01e42-a5c7-7530-bc07-9c88bb03d679; dvc_06_green_v3_03=01a01e42-c379-7342-84ae-d7e8ebaf853d; dvc_06_green_v3_04=01a01e43-68ea-71d2-85bf-0c0b94cc842d; dvc_06_green_v3_05=01a01e43-7d27-76a3-b42e-1fd7a0a05435 |
| 3 | DVC-07 | dvc_07_green_v3_01=01a01e44-1b9c-7e21-bc61-9c8c3a756869; dvc_07_green_v3_02=01a01e44-2f6d-7de0-b7e0-af01e7c2c730; dvc_07_green_v3_03=01a01e44-d302-75d1-809f-f71a6c5aa6ee; dvc_07_green_v3_04=01a01e44-e690-70c1-9d77-b83bae8fe4bf; dvc_07_green_v3_05=01a01e45-294a-7793-aa6a-047f24c6af52 |
| 3 | DVC-08 | dvc_08_green_v3_01=01a01e45-4159-72a2-a71c-9e20bb3e1d96; dvc_08_green_v3_02=01a01e45-91e3-7e63-84e7-387118fd7ca2; dvc_08_green_v3_03=01a01e45-ab9c-7401-a6d7-61acbcd87779; dvc_08_green_v3_04=01a01e46-2733-7e63-a30c-b125871c8825; dvc_08_green_v3_05=01a01e46-3b7e-7ff0-adeb-175cbae18862 |
| 3 | DVC-09 | dvc_09_green_v3_01=01a01e46-d4cf-7631-9747-4e1f408741c4; dvc_09_green_v3_02=01a01e46-ec55-7e82-9823-96bb40364472; dvc_09_green_v3_03=01a01e47-3b28-78a1-a24f-38bd20b9c40e; dvc_09_green_v3_04=01a01e47-5583-78f3-bc0b-2c621d8e4bab; dvc_09_green_v3_05=01a01e47-b82e-71b3-990e-0e1ec6257ba5 |
| 3 | DVC-10 | dvc_10_green_v3_01=01a01e47-dfaa-73f3-9ac0-984cbe91dd8f; dvc_10_green_v3_02=01a01e48-301d-7430-95f1-ed50457c0f79; dvc_10_green_v3_03=01a01e48-4a2a-76a2-b5f8-640f03614b60; dvc_10_green_v3_04=01a01e48-9726-74e2-8e47-eb9da265ab99; dvc_10_green_v3_05=01a01e48-aed2-7f62-90f8-1da05e2e2df5 |
| 4 | DVC-01 | dvc_01_green_v4_01=01a01e4c-3607-78a1-9216-93c8d420f708; dvc_01_green_v4_02=01a01e4c-5000-74a0-9b60-529ab5e661c7; dvc_01_green_v4_03=01a01e4c-e6dc-7f13-a8e9-b73ee78a4bca; dvc_01_green_v4_04=01a01e4c-ff8e-7ae1-a297-597212e95378; dvc_01_green_v4_05=01a01e4d-a90d-75a3-b268-d1cb339a144c |
| 4 | DVC-02 | dvc_02_green_v4_01=01a01e4d-c32b-77f2-be55-286107fc5bb5; dvc_02_green_v4_02=01a01e4e-79c8-72c1-a393-5f8e1c4d6889; dvc_02_green_v4_03=01a01e4e-99c5-78d2-8748-2f7398a5542c; dvc_02_green_v4_04=01a01e4f-d0de-7623-a22a-ae36175a616e; dvc_02_green_v4_05=01a01e4f-fa26-7183-9d79-ae6e182515a0 |
| 4 | DVC-03 | dvc_03_green_v4_01=01a01e51-7106-7cd1-a338-e32b6bcac970; dvc_03_green_v4_02=01a01e51-86c6-77e2-9e31-d63c9cfa392b; dvc_03_green_v4_03=01a01e52-38ea-74b1-a9e7-75ca0252f0e0; dvc_03_green_v4_04=01a01e52-5851-7a22-9a06-86f8b4cc81ed; dvc_03_green_v4_05=01a01e52-ffb9-7303-a539-2c8a77e0f4af |
| 4 | DVC-04 | dvc_04_green_v4_01=01a01e53-2034-7c80-b795-097fc8c9565d; dvc_04_green_v4_02=01a01e53-9eb3-7192-8c93-ca484b0eaef3; dvc_04_green_v4_03=01a01e53-c2cb-7f12-b4b4-9ed3b55028e7; dvc_04_green_v4_04=01a01e54-5078-7de2-b4c5-ac3caa493c83; dvc_04_green_v4_05=01a01e54-6835-7df3-b01a-8516fba89d7f |
| 4 | DVC-05 | dvc_05_green_v4_01=01a01e55-3b95-7ea0-ab7e-09fca78ae599; dvc_05_green_v4_02=01a01e55-5765-7950-bd69-dc658f0cdbc4; dvc_05_green_v4_03=01a01e56-1ab1-7393-b3d1-cf7f578f9789; dvc_05_green_v4_04=01a01e57-23cc-7be1-a9bc-3cf915f6661e; dvc_05_green_v4_05=01a01e57-38be-7eb3-9884-3a9a325dbea3 |
| 4 | DVC-06 | dvc_06_green_v4_01=01a01e57-8856-7fb3-81e1-967072e194f5; dvc_06_green_v4_02=01a01e57-9d2b-7c20-8dd3-786f1aa87c02; dvc_06_green_v4_03=01a01e58-598d-7821-a496-452b3ee8cb6a; dvc_06_green_v4_04=01a01e58-6b30-7e31-b47f-965fd2a7fda0; dvc_06_green_v4_05=01a01e59-5a93-7ba2-aa25-088ec62f7fe5 |
| 4 | DVC-07 | dvc_07_green_v4_01=01a01e5b-b8a2-7173-8e05-8d604dd26cf7; dvc_07_green_v4_02=01a01e5b-cc98-7702-82e1-182110a664a6; dvc_07_green_v4_03=01a01e5c-4b8c-7253-b9c1-e8990c425339; dvc_07_green_v4_04=01a01e5c-5e75-7ec1-8fc4-f2ee6574a993; dvc_07_green_v4_05=01a01e5c-d984-7b81-9ca6-36ff4a8a9c6b |
| 4 | DVC-08 | dvc_08_green_v4_01=01a01e5d-7aff-7b61-a2c6-e69e80e0509a; dvc_08_green_v4_02=01a01e5d-8e97-7d13-beb7-452dbe883b12; dvc_08_green_v4_03=01a01e5e-1ac3-78a3-befa-4f0648f9881f; dvc_08_green_v4_04=01a01e5e-309c-7622-8cb6-b427ad107781; dvc_08_green_v4_05=01a01e5e-c327-7bf2-8e4e-e7cb12b1c332 |
| 4 | DVC-09 | dvc_09_green_v4_01=01a01e5f-89e3-7a93-a6da-81eaf668872e; dvc_09_green_v4_02=01a01e5f-9d8c-78b1-a428-2c83a0068df7; dvc_09_green_v4_03=01a01e5f-e71b-72e2-b6f3-e4183515a3ce; dvc_09_green_v4_04=01a01e5f-fa2c-7313-a6cd-ff5c4f4860eb; dvc_09_green_v4_05=01a01e60-45a0-77b2-bb65-7f7dba931adf |
| 4 | DVC-10 | dvc_10_green_v4_01=01a01e60-f165-7753-93b5-fe63ec44c135; dvc_10_green_v4_02=01a01e61-0650-7b73-a834-d938ab06f180; dvc_10_green_v4_03=01a01e61-571a-7533-ba6a-106b885e1a3e; dvc_10_green_v4_04=01a01e61-7166-74f2-ad55-06c2eb5e64b7; dvc_10_green_v4_05=01a01e61-ba74-74c1-9ccf-e2d407a6d87f |
| 5 | DVC-01 | dvc_01_green_v5_01=01a01e64-b519-7c73-bf39-2e9021fb6ffd; dvc_01_green_v5_02=01a01e64-c861-7303-8632-49a15e7b81f5 |
| 5c | DVC-01 | dvc_01_green_v5c_01=01a01e66-b974-7b72-bc66-72ca9ffa1e01; dvc_01_green_v5c_02=01a01e66-d6e6-76d1-a5f9-11984c66005d; dvc_01_green_v5c_03=01a01e67-8324-7b82-8fb5-272d1f19eac2; dvc_01_green_v5c_04=01a01e67-97f1-7430-a727-3b7d7aa94ebc; dvc_01_green_v5c_05=01a01e68-38c0-77c0-9d3a-3ae487d85aac |
| 5c | DVC-02 | dvc_02_green_v5c_01=01a01e68-e078-7ec2-b927-c64420f09807; dvc_02_green_v5c_02=01a01e68-fa28-7913-8f5f-228fc667f945; dvc_02_green_v5c_03=01a01e6a-013c-7010-a3be-d7d4e3e13352; dvc_02_green_v5c_04=01a01e6a-157f-7800-a705-d79ea90ca748; dvc_02_green_v5c_05=01a01e6b-0bf1-7832-ac96-1c6190181590 |
| 5c | DVC-03 | dvc_03_green_v5c_01=01a01e6c-cdaf-7b13-9356-a0d2506b4561; dvc_03_green_v5c_02=01a01e6c-e3a9-7da0-a34b-0eb39a55e345; dvc_03_green_v5c_03=01a01e6d-9211-7a10-8876-3fbe18afd459; dvc_03_green_v5c_04=01a01e6d-a6b5-7882-b897-336c431701b1; dvc_03_green_v5c_05=01a01e6e-6675-7dd1-8e51-945061749862 |
| 5c | DVC-04 | dvc_04_green_v5c_01=01a01e6f-0183-79c2-82d4-8bbea85ac265; dvc_04_green_v5c_02=01a01e6f-1e53-7be1-90f4-62322e252b0a; dvc_04_green_v5c_03=01a01e6f-9881-7e42-b0ae-cd3da7e23125; dvc_04_green_v5c_04=01a01e6f-af7e-7fb1-973e-af368f247b6c; dvc_04_green_v5c_05=01a01e70-2b85-7ee2-8edf-630a4ace83b6 |
| 5c | DVC-05 | dvc_05_green_v5c_01=01a01e70-c00d-7203-8f2e-ced5330a3d73; dvc_05_green_v5c_02=01a01e70-d6cf-7cd1-9d60-06ab2cf96ba0; dvc_05_green_v5c_03=01a01e71-4d64-7be1-85e7-cb66bd460166; dvc_05_green_v5c_04=01a01e71-6626-7423-acde-7379c9367739 |
