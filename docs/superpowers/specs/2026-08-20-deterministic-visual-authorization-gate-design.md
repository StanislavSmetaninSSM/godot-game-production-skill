# Deterministic Visual Decision and Generation Authorization Gate

**Date:** 2026-08-20
**Status:** Approved design; implementation pending

## Decision

Add two deterministic gates to the dynamic visual-reference workflow:

1. a decision validator that accepts a machine-readable visual decision and makes
   behavioral PASS/FAIL independent of an agent's self-assessment;
2. a generation authorization validator that hash-binds exact user-approved plan
   rows to the only ImageGen results that may enter an accepted evidence ledger.

The gates complement rather than replace user judgment. Code validates structure,
identity, ordering, cardinality, and bindings. The user decides whether the proposed
needs-derived slot set is semantically complete and whether the generated targets
are acceptable.

An unvalidated response may remain an explanation, but it cannot count as a passed
behavioral case, authorize ImageGen, advance visual state, enter an approved visual
contract, or contribute to an `evidence_run.py validate` result of `VERIFIED`.

## Context

The unreleased dynamic-reference implementation already validates complete
`evidence-run/v2` manifests. It rejects empty plan rows, `image_count` other than
`1`, approval-binding drift, generation before scope approval, targets outside the
approved plan, invalid delta ancestry, target reuse, and approval before generation.

That validator runs too late for two decisions:

- a pending chat response can omit rows, pad a requested count, omit an approval
  question, or summarize a delta without producing its current plan;
- an agent can call ImageGen before it has assembled an accepted manifest.

Behavioral forward-testing demonstrated both failures. Repeated prose refinements
improved compliance but still produced refusal-only answers, empty row collections,
requested-count padding, incomplete delta output, omitted approval boundaries, and
unapproved ImageGen calls. A second model then had to score those answers manually,
which is expensive and does not create a hard acceptance boundary.

## Goals

- Make behavioral PASS a deterministic program result, not an agent verdict.
- Validate the pending initial, delta, and reference-is-not-proof response shapes.
- Make scope approval bind the exact complete plan bytes and ordered slot set.
- Require every accepted generated or rejected ImageGen target to resolve to an
  authorization for its exact plan revision and slot.
- Preserve one approved row to one generated image and no preset pack size.
- Preserve local-delta isolation, replacement identity, retry chronology, and all
  existing visual, gameplay-evidence, TDD, independent-review, and release gates.
- Reuse recorded behavioral failures as deterministic regression fixtures.
- Replace repeated speculative model sampling with unit tests, followed by one
  final five-per-case behavioral acceptance matrix on the finished skill.

## Non-goals and trust boundary

- The skill cannot intercept or disable the platform's built-in ImageGen tool. A
  raw unauthorized call may still occur, but none of its results can become an
  accepted target, approval, verified evidence artifact, or release signal.
- Local files cannot cryptographically prove that a reviewer is a human. The gate
  validates reviewer separation, exact bindings, timestamps, and immutable records;
  it does not authenticate platform identity or provenance truth.
- The gate does not decide artistic quality, fun, or whether the agent found every
  semantically useful visual question. Exact user scope and target approval remain
  mandatory.
- The gate does not infer arbitrary natural-language meaning. Behavioral cases
  provide hidden machine expectations for facts that must be scored exactly.
- This design does not wrap, replace, or reimplement ImageGen.
- Compatibility with intermediate unreleased fixtures is not required. The skill
  has no production users; all `evidence-run/v2` fixtures may move atomically to
  the final schema in this branch.

## Alternatives considered

### Behavioral scorer only

This would remove self-grading but would not bind actual generation to approval.
It is insufficient because an invalid ImageGen result could still be recorded later.

### Production authorization only

This would protect accepted evidence but retain manual behavioral scoring and the
expensive wording loop. It would not prove that the skill reliably emits the
decision object required to reach the gate.

### Two deterministic gates

This is the selected approach. The same canonical plan contract drives response
validation, generation authorization, evidence validation, and behavioral scoring.

## Components

### Shared visual-contract module

Extract the canonical visual schemas, canonical JSON hashing, and visual-plan
validation into one sibling Python module under
`godot-game-production/scripts/`. Both command-line entrypoints import it so plan
rules cannot drift between preflight and full-ledger validation.

The shared module has no filesystem side effects. It accepts parsed objects and
returns typed results or deterministic errors.

### `visual_gate.py`

Add a project-independent CLI that can run before a Godot project or evidence
manifest exists. It has two commands:

```text
visual_gate.py check-decision --decision DECISION --report REPORT
visual_gate.py authorize-generation --decision DECISION --approval APPROVAL \
  --authorization AUTHORIZATION
visual_gate.py authorize-generation --decision DECISION --approval APPROVAL \
  --rejected-target REJECTED --correction-approval CORRECTION \
  --authorization AUTHORIZATION
```

Both commands reject duplicate JSON keys, unknown fields, malformed timestamps,
non-portable paths, and output paths that would overwrite an input. Writes are
atomic. An existing output must be a valid prior report for the same input binding
or the command fails closed.

Exit codes are stable:

| Code | Meaning |
|---:|---|
| `0` | The requested command passed. For `check-decision`, the report status is `VALID_PENDING`; for `authorize-generation`, it is `AUTHORIZED`. |
| `1` | A later-state validation is structurally valid but still pending because a required approval, result, or review is absent. `check-decision` does not use this code for a valid pending proposal. |
| `2` | A contract invariant was rejected. |
| `3` | Input, schema, path, JSON, or I/O is invalid. |

Every report also carries a machine status; prose must not infer authorization from
exit code `0` returned by the decision-only command.

### Full evidence validator

`evidence_run.py validate` continues to own complete evidence and release results.
It imports the same shared module and additionally requires every
`target_gameplay_image` and `rejected_target_image` to resolve one generation
authorization by exact authorization ID, plan ID, plan revision, slot ID, plan
binding, and scope-approval binding.

An approved visual contract without a complete valid authorization chain is
`FAILED`; it can never be `PENDING` or `VERIFIED` merely because target files exist.

### Behavioral scorer

Add a test-only deterministic scorer that accepts:

- the evaluator's final answer;
- the hidden machine expectations for exactly one DVC case;
- a normalized observable-run trace for that evaluator session.

It extracts exactly one fenced `visual-decision/v1` JSON object, invokes the same
decision validator, checks the final literal approval question when applicable,
checks case-specific exact facts, and rejects any pre-authorization ImageGen call,
write, or extra final answer. Filesystem reads and generic tool calls are not scorer
inputs; the evaluation runner owns prompt and hidden-material isolation. This avoids
penalizing required reads of Superpowers, Spec Kit bridge, or ImageGen instructions.

Only scorer exit code `0` is PASS. The evaluator, implementation agent, and eval
ledger cannot override that result. Semantic commentary outside the decision object
is ignored except for the required literal final question.

## Machine-readable decision contract

Every visual-gate final response contains exactly one fenced JSON object with
`schema_version: "visual-decision/v1"`. A concise human explanation may precede it.
When scope approval is required, the canonical literal question is the final line:

`Do you exactly approve the proposed reference slot ID set?`

The object uses a discriminated `decision_kind`.

### `initial_scope`

Required fields are:

- `schema_version`, stable UUID `decision_id`, non-empty `builder_id`,
  timezone-aware `created_at`, `decision_kind`, and `state`;
- `generation_status: "not_started"`;
- one complete `reference_plan` with `approval: null`;
- `scope_question` equal to the canonical literal question.

The plan reuses the exact reference-plan and row schemas already defined for the
dynamic contract. Rows are non-empty whenever the brief establishes a visual need.
A user-requested image count never determines plan cardinality. A previously
proposed finite set is repeated only when the source supplies the actual rows or
stable row identities; a bare number is not a proposed set.

When the user refers to an existing plan but does not supply one of its values, a
decision may retain `<required-value>` at that exact field and remain
`VALID_PENDING`. The validator does not mistake this for a completed plan:
`authorize-generation`, full evidence validation, and any generated-target mapping
reject every unresolved placeholder. A supplied value may never be replaced by a
placeholder.

### `delta_scope`

Required fields are:

- all common identity, state, and not-started generation fields;
- `change_scope` equal to `local` or `global`;
- a complete non-empty delta `reference_plan`;
- non-empty `blocked_work` and `continuing_work` arrays where local isolation is
  applicable;
- `preserved_bindings` for unchanged targets;
- `affected_targets`, each with its exact target ID, `dependent_work`, and change
  kind;
- `target_approval_scope: "complete_delta_batch_only"`;
- the canonical scope question.

An observed uncovered material visual question opens the delta in the current
decision. A replacement row names its exact `supersedes_target_id`. A global
visual-grammar change enumerates every affected known binding instead of declaring
that expansion will happen later.

### `reference_not_proof`

This variant records a rejected proof claim and the canonical evidence gates that
remain required. Its exact machine list covers:

- actual bitmap presentation;
- project-local PNG and SHA-256 binding;
- buildability, motion cue, and sound cue;
- target-Godot input/state/outcome evidence;
- TDD and independent review;
- core play, systems/holism, content, visual, audio/feedback, UX/onboarding,
  reliability/performance, and ship release facets.

It cannot authorize generation or advance a visual or release state.

## Scope approval contract

`visual-scope-approval/v1` records:

- approval artifact and reviewer IDs;
- `decision: "approved"`;
- a timezone-aware `recorded_at` timestamp;
- the exact canonical decision and plan SHA-256 bindings;
- the complete approved ordered slot-ID set.

Partial approval, reordered or missing slots, binding drift, a builder reviewer, or
an approval timestamp preceding the decision fails authorization.

## Generation authorization contract

`visual-generation-authorization/v1` is written only by the authorization command.
It records:

- a stable authorization ID and issuance timestamp;
- decision, plan, revision, and scope-approval bindings;
- the exact authorized ordered slot IDs;
- exactly one result budget per slot;
- `batch_kind`: initial, delta, or correction; add/replace operations remain on
  the individual delta rows so one approved delta may contain both;
- base-contract and supersession identities where applicable;
- the previous rejected target and correction approval for a retry.

The authorization object is immutable. It does not contain generated target IDs or
paths because those do not exist yet; later artifacts bind themselves to its slots.

The final `evidence-run/v2` manifest adds exact `visual_decisions`,
`visual_scope_approvals`, `visual_correction_approvals`, and
`visual_generation_authorizations` arrays. An initial or delta decision's embedded
plan must equal the corresponding `reference_plans` row after the latter's separate
approval field is removed. Every approval and authorization hash must resolve
against these stored source objects rather than trusting an unresolvable digest.

ImageGen-derived artifact rows add the required `authorization_id`; no other
artifact kind may carry it. Because this schema is still unreleased, fixtures
change atomically and no compatibility branch or migration reader is retained.

For an initial or approved delta batch, authorization covers the complete approved
slot set. It cannot authorize a subset. A correction authorization covers exactly
one rejected slot and is valid only after its concrete rejection and a separate
`visual-correction-approval/v1` record. That record binds the reviewer, timestamp,
plan revision, slot ID, rejected target ID/hash, and non-empty correction direction.
The correction form of `authorize-generation` requires both records explicitly;
the ordinary full-batch form rejects those extra inputs.

## Accepted generation invariants

The full evidence validator enforces:

- every ImageGen-derived target names exactly one authorization ID;
- authorization, plan revision, slot, approval binding, and timestamps agree;
- no authorization contains an unknown, duplicate, or omitted approved slot;
- each current slot has exactly one accepted target;
- rejected attempts remain immutable audit history and consume their attempt;
- a later attempt is bound to a fresh correction authorization issued after the
  preceding rejection;
- target IDs are never reused;
- unapproved or unregistered generated files cannot become contract targets;
- exact target approval occurs only after the complete authorized batch exists.

## Behavioral expectations

Move the hidden DVC criteria into a machine-readable companion catalog. Each case
specifies only deterministic expectations, such as:

- decision kind and state;
- exact row count when the brief itself determines it;
- required coverage labels or supplied row identities;
- required/forbidden supersession and preserved bindings;
- required affected dependencies;
- expected canonical question;
- required reference-not-proof gates;
- forbidden ImageGen and write events.

Evaluator sessions still receive only the prompt and isolated installable skill.
They never receive the expectation catalog, reports, specs, plans, prior responses,
or another evaluator's answer.

## Data flow

1. Codex derives a decision JSON and presents a readable rendering from the same
   object.
2. `check-decision` validates it and writes a bound report.
3. The user approves or rejects the exact displayed slot set.
4. Exact approval is recorded against the decision and plan hashes.
5. `authorize-generation` validates the full approval and atomically writes the
   immutable authorization.
6. Codex may now call ImageGen once per authorized slot and records each result with
   the authorization ID.
7. The user approves or rejects the complete generated batch.
8. `evidence_run.py validate` rejects any missing, extra, stale, reordered,
   pre-authorized, or post-rejection-unapproved result.
9. Later discoveries repeat the same flow as an add, replace, or correction delta.

## Failure behavior

- A malformed decision does not create a report that can be mistaken for PASS.
- A valid pending decision does not create generation authorization.
- A failed authorization command leaves no partial output.
- Existing valid output bound to different bytes is never overwritten.
- Tool unavailability leaves the state pending and preserves the failed report.
- A raw unauthorized ImageGen call is retained as audit evidence when observed, but
  its output cannot enter an active or approved visual contract.
- Any disagreement between decision, approval, authorization, target artifact, or
  evidence manifest fails closed with the exact mismatched identity.

## Testing strategy and evaluation budget

Implementation follows strict RED-GREEN-REFACTOR.

### Deterministic RED

Before production code, add failing tests for:

- omitted, empty, padded, duplicate, and malformed rows;
- a bare requested number incorrectly treated as a proposed set;
- missing or changed canonical approval question;
- partial approval and decision/plan binding drift;
- unresolved placeholders accepted as pending but rejected for authorization and
  full evidence;
- missing delta row, supersession, preserved binding, affected dependency, or
  complete-delta target-approval scope;
- shortened reference-not-proof gates;
- authorization before approval, for a subset, or with duplicate slots;
- generated/rejected targets without authorization;
- stale/reused authorization and retry before correction approval;
- duplicate keys, unsafe paths, overwrite attempts, and atomic-write failures;
- scorer rejection of ImageGen calls, writes, malformed run traces, and multiple
  final answers; the runner owns hidden-material isolation separately.

Selected saved behavioral failures become regression fixtures or exact assertions;
their original session IDs remain in the durable eval ledger.

### Deterministic GREEN

Run focused command tests, the full evidence validator suite, structural contract
tests, legacy production-operations regressions, compilation, official skill
validation, and diff/protected-file checks.

### Final behavioral acceptance

Do not run a new 50-session matrix after every wording edit. Use deterministic
tests while iterating. Once all machine gates and documentation are final, freeze
one isolated skill and run exactly five fresh Terra-medium samples for each
`DVC-01` through `DVC-10`.

The deterministic scorer must report five of five for every case. Any subsequent
skill wording or schema change that can affect a case makes its sample stale and
requires fresh samples for that case plus the mandatory small-pack, large-pack, and
reference-not-proof guards.

## Documentation impact

- Keep only the gate order and commands in `SKILL.md`.
- Put the detailed decision and authorization schemas in the visual-contract and
  evidence-ledger references.
- Document that machine authorization is necessary but not sufficient for user
  approval, artistic quality, runtime proof, or release readiness.
- Remove the accumulated behavioral workaround block once equivalent machine
  fields and commands make it redundant; do not keep both a long prose checklist
  and the deterministic schema.

## Acceptance criteria

- An agent cannot award PASS to its own behavioral output.
- No target or rejected attempt without exact authorization can validate.
- Requested image counts cannot override needs-derived rows.
- Partial scope approval cannot authorize a subset.
- Initial, local delta, global delta, replacement, and correction flows are
  deterministic and fail closed.
- The user still approves exact scope before generation and exact targets afterward.
- All existing mechanics, target-build, TDD, review, evidence, and release gates
  remain independent and mandatory.
- Iterative correctness is established primarily by programmatic tests; model
  sampling is reserved for one final acceptance matrix.
