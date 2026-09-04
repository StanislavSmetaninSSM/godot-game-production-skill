# Dynamic Visual Reference Contract

**Date:** 2026-08-20
**Status:** Approved design; implementation pending

## Decision

Replace the current one-stage visual-generation gate with a needs-derived,
two-stage reference contract:

1. Codex proposes the exact visual reference slots it considers necessary.
2. The user approves the complete slot set before ImageGen is called.
3. Codex generates exactly one image for each approved slot.
4. The user approves the exact generated target set.

There is no preset minimum, maximum, or preferred pack size. The required image
count is exactly the number of approved reference-slot rows. Later discoveries use
the same two-stage protocol as a versioned delta and block only dependent work.

## Context

The current skill already derives target coverage from a matrix rather than stating
a literal six- or seven-image quota. It nevertheless freezes that matrix internally
and proceeds directly to ImageGen. The user approves generated files, but does not
first approve the agent's judgment about which visual targets are necessary.

The current late-ambiguity rule also says to re-enter ImageGen without defining a
new scope-approval gate, an exact additive or replacement delta, or machine-checked
ordering. This permits several undesirable outcomes:

- an agent can pad a small game to an assumed pack size;
- an agent can cap a large game at an arbitrary number;
- unnecessary variants can be generated before the user sees the proposed scope;
- a late reference can silently invalidate unrelated approved work;
- evidence can record target approval without proving that scope approval preceded
  generation.

## Goals

- Make reference quantity dynamic and needs-derived.
- Give the user control over the exact list before generation spends time or budget.
- Cover any visually consequential target: location, gameplay state, UI mode,
  character, or asset family.
- Make one approved row map to exactly one generated image.
- Allow late additive or replacement references without stopping unrelated work.
- Preserve stable target IDs, hashes, paths, buildability accounts, motion and sound
  cues, and exact bitmap presentation.
- Validate scope approval, generation, target approval, and delta ancestry in code.

## Non-goals

- Do not define a universal reference count or a fixed catalogue of target types.
- Do not generate several choices for one approved row.
- Do not treat generated targets as runtime or mechanics evidence.
- Do not relax existing visual, feasibility, TDD, review, gameplay-evidence, or
  release gates.
- Do not preserve compatibility with `evidence-run/v1`; the skill has no production
  users or existing project manifests that require migration.

## Lifecycle

The top-level state sequence remains:

`AUDIT -> SPECIFY -> VISUAL_PENDING -> VISUAL_APPROVED -> GODOT_FEASIBILITY ->
CORE_LOOP -> PRODUCTION -> RELEASE`

`VISUAL_PENDING` gains two required substates.

### `REFERENCE_SCOPE_PENDING`

When the brief and core mechanics are sufficient, Codex derives the smallest
adequate set of visual targets and publishes a versioned reference plan. It must
not call ImageGen in this substate.

Codex ends the plan with the literal question:

`Do you exactly approve the proposed reference slot ID set?`

Rejection or any requested row change keeps the state pending. Codex republishes
the complete revised plan; approval of only a subset does not authorize partial
generation.

### `REFERENCE_TARGETS_PENDING`

Exact approval of the complete plan authorizes one ImageGen call per approved row.
Codex generates no other targets or variants. Target approval remains fail closed
until every approved slot has exactly one displayed, saved, and recorded image with
a complete buildability account.

Codex ends the complete target presentation with the existing literal question:

`Do you exactly approve the displayed target ID set?`

For the initial contract, only exact approval of the complete current set advances
the top-level state to `VISUAL_APPROVED`. For a delta, exact approval covers the
complete generated delta set; unchanged targets remain bound by the approved base
and are not presented as newly approved results.

## Reference plan contract

Each plan has a stable `plan_id`, integer `revision`, `kind` (`initial` or `delta`),
optional `base_contract_id`, ordered rows, and a separate scope-approval record.

Each row represents exactly one future image and records:

| Field | Required content |
|---|---|
| `reference_slot_id` | Stable identity preserved through generation and approval. |
| `target_kind` | Location, gameplay state, UI mode, character, or asset family. |
| `subject` | Exact visual subject or state that must be shown. |
| `visual_question` | The uncertainty or production decision this target resolves. |
| `coverage` | One or more required gameplay states, asset families, or visual obligations. |
| `composition` | Required camera, angle, environment, characters, UI, and VFX. |
| `motion_cue` | Motion information that the still target must imply and later runtime evidence must prove. |
| `sound_cue` | Audio or feedback information recorded because a still cannot prove it. |
| `dependent_work` | Exact tasks or production slices blocked by this target. |
| `rationale` | Why existing approved targets cannot answer the visual question. |
| `image_count` | Literal integer `1`. |
| `change_kind` | `initial`, `add`, or `replace`. |
| `supersedes_target_id` | Required only for `replace`; otherwise `null`. |

One row may cover several related obligations when one coherent image naturally
answers them. Codex must not create redundant rows merely to reach a familiar pack
size. A distinct angle, state, or variant is a distinct row and requires approval.

Scope approval binds the complete ordered slot-ID set and the full row contents,
not merely the count. Adding, deleting, reordering, or materially changing a row
creates a new plan revision and reopens scope approval.

## Generation and target approval

For every approved plan row, Codex:

1. makes exactly one ImageGen call;
2. presents the actual bitmap through the required image result channel;
3. copies the selected result into the versioned project contract directory;
4. computes SHA-256 from the final project-local PNG;
5. records a timezone-aware generation timestamp;
6. maps `reference_slot_id -> target_id -> SHA-256 -> project-relative path`;
7. records coverage, buildability, motion cue, and sound cue.

The target set is approval-ready only when the mapping is bijective: every approved
slot maps to one target and every target maps to one approved slot. Missing,
duplicate, extra, or unmapped targets keep the gate pending.

If a generation fails, successful results remain available and Codex resumes only
the missing rows. It must not regenerate a completed result merely to repair its
presentation or to provide unapproved alternatives.

When the user requests a correction that preserves the row's visual question and
composition, only that target is regenerated. If the requested correction changes
the subject, angle, state, coverage, or other scope, that row returns to
`REFERENCE_SCOPE_PENDING`. Before final approval, Codex presents the complete
current candidate batch again: the full initial set for an initial contract or the
full added/replacement set for a delta.

Target approval binds the exact target IDs, final hashes, and project-relative
paths. Missing or moved files, changed bytes, or changed mappings reopen approval.

## Unapproved generations

An image generated without an approved slot is outside the contract. Codex must
show and report the protocol error but cannot add the image to an approvable target
set. To use it, Codex first adds a corresponding row to a new plan revision and
obtains scope approval. Silent adoption, silent deletion from the evidence record,
or retroactive scope approval is invalid.

## Late visual re-entry

Late re-entry is required when Codex finds a visual decision that cannot be derived
from the active approved targets without making a material new art-direction
choice.

A missing or changed player-visible state in an approved production is itself
sufficient to reopen the gate. Codex emits the complete pending delta before an
implementation-detail question or game change; it never announces the re-entry in
prose only. Unknown base or target identities and unresolved presentation details
remain explicit pending placeholders, while stated independent work is recorded as
continuing work.

Pending text or identity placeholders use `<required-value>` or a distinct indexed
`<required-value:label>` form. Authorization also rejects common natural-language
unresolved markers (`unspecified`, `unknown`, `TBD`, `TODO`, `PENDING_*`, or a
`PLACEHOLDER` token) anywhere in the complete decision, so pending prose outside
the reference plan cannot silently become generation authority.

Codex records the missing information, affected tasks or slices, classification as
an addition or replacement, and a delta plan. Only dependent work enters
`VISUAL_DELTA_PENDING`. Independent work may continue. The blocked scope may
perform analysis or reversible greyboxing, but it must not create final assets or
code that commits the unresolved visual choice.

The delta then follows the same gates:

`delta scope proposal -> scope approval -> exact generation -> target approval`

An approved delta:

- references one active base contract version;
- adds new targets or explicitly supersedes named old targets;
- binds its target approval to the complete added/replacement set only;
- preserves unchanged target IDs, hashes, and paths;
- keeps superseded files and records as immutable history;
- produces a new active contract version;
- unblocks only work covered by the approved delta.

Within a delta, preserved target IDs and affected target IDs are unique and
disjoint; blocked and continuing work are disjoint; and the affected replacement
set exactly matches the plan's named supersessions. These invariants are checked
before generation authorization rather than deferred to final evidence review.

If the change affects global visual grammar, including the primary art style,
canonical gameplay camera, or shared UI language, Codex expands the affected target
set accordingly. A nominally local delta cannot hide a global revision.

Global expansion keeps one independently useful visual question per row and one
affected-target entry per affected target. A representative or catch-all row or
target cannot combine non-combinable style, camera, UI, or other questions. When
exact target IDs are unavailable, distinct placeholder identities preserve the
required cardinality until the real bindings are known.

## Evidence model and schema break

`evidence-run/v2` is the only supported schema after this change. The initializer
creates v2 manifests and the validator rejects v1. No migration or legacy branch is
implemented.

The v2 manifest replaces the single one-stage `approved_visual_contract` model with
records sufficient to validate:

- versioned reference plans and their exact scope approvals;
- target-generation records keyed by reference slot;
- versioned visual-contract approvals;
- the active contract version;
- delta ancestry, additions, replacements, and superseded targets.

Every scope approval, target generation, and target approval has a timezone-aware
timestamp. Validation requires this strict order:

`scope approval < every covered generation < target approval`

For a delta, validation also requires an already approved active base, an approved
delta plan, exact target mappings, and a target approval before the new version can
become active. Cycles, missing bases, branching from an inactive base, target-ID
reuse, and mutation of unchanged target bindings fail.

## Failure handling

Keep the relevant visual gate pending when any of the following is true:

- the complete plan is not exactly approved;
- plan fields are missing or `image_count` differs from `1`;
- generation began before scope approval;
- target count and approved slot count differ;
- a target is missing, duplicated, extra, or unmapped;
- a completed bitmap was not shown;
- a final file, stable ID, hash, path, or buildability account is absent;
- approval timestamps are absent, malformed, or out of order;
- target bytes or paths drift after approval;
- a delta lacks an active base or obscures a replacement;
- a local delta contradicts a global visual rule without expanding its impact set.

These failures do not authorize automatic retries, invented approvals, or progress
to dependent Godot production.

## File-level design

### `godot-game-production/SKILL.md`

- Add the scope-approval subgate before every initial ImageGen pack.
- Prohibit fixed quotas, padding, capping, partial generation, and unapproved
  variants.
- Add scoped late re-entry and dependency blocking.
- Preserve the top-level state sequence and all existing non-visual gates.

### `godot-game-production/references/visual-contract.md`

- Define reference-plan rows, exact scope approval, generation mapping, corrections,
  deltas, replacements, and global-impact expansion.
- Retain actual-bitmap presentation, project-local files, hashes, buildability,
  motion/sound cues, and exact target approval.

### `godot-game-production/scripts/evidence_run.py`

- Change initialization and strict validation to `evidence-run/v2` only.
- Validate plans, approvals, slot-to-target bijection, event ordering, delta ancestry,
  active-set derivation, and immutable carried-forward bindings.

### `godot-game-production/references/evidence-ledger.md`

- Document the v2 records, order constraints, delta chain, and failure states.

### `README.md`

- Describe needs-derived counts and the two user approvals without duplicating the
  detailed protocol.

### Tests and evaluation

- Add focused Python tests for v2 initialization, schema validation, ordering,
  bijection, deltas, supersession, and drift.
- Extend structural tests for routing and preservation of established gates.
- Add blinded behavioral cases and durable evaluation evidence.

## Behavioral evaluation

Record the current skill as RED before editing guidance or validation. Then run five
fresh blinded samples per affected case and fresh guard samples after every wording
change that could affect the case.

Required cases include:

1. A small game needs two targets; the agent does not pad to six or seven.
2. A broad game needs more than seven targets; the agent does not cap the plan.
3. A user requests an arbitrary fixed count; the agent first proposes a justified
   needs-derived plan.
4. Generation is requested before scope approval; the agent remains pending.
5. Only part of a plan is accepted; the agent does not start partial generation.
6. Multiple angles or variants become separate approved rows.
7. A late gap blocks only dependent work and creates a delta.
8. A replacement preserves unrelated approved bindings.
9. A global style change expands the affected set.
10. Existing bitmap, hash, path, buildability, gameplay, and release gates remain.

The final latest set must pass every affected case and both small- and large-pack
guards. Stale samples from an earlier guidance or schema variant do not count.

## Acceptance criteria

- No normative fixed reference count remains or is introduced.
- The agent proposes every initial and delta reference plan before ImageGen.
- Exact full-plan approval is required; partial approval does not authorize work.
- Approved rows and generated targets have an exact one-to-one mapping.
- Initial and delta image counts equal their approved row counts.
- Only dependent work pauses for a local late gap.
- Global changes cannot masquerade as local deltas.
- `evidence-run/v2` machine-validates approval order and delta ancestry.
- v1 is rejected and no compatibility branch exists.
- Existing visual presentation, hash/path, feasibility, mechanics-evidence, TDD,
  review, and release gates remain intact.
- Structural tests, v2 validator tests, behavioral latest-set evaluation, official
  skill validation, and diff checks pass.
