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

A production plan must write every applicable field above for each genuine slice.
Calling related edits one coherent slice does not replace its `baseline`, measurable
`postcondition`, `conflicts`, `verification`, or `integration_target` records.
Use the complete field table for the plan; an abbreviated scope/dependency summary
that omits any of those named records is not a completed slice contract.

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
