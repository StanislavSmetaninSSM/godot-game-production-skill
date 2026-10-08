# Evidence Ledger

Create a project-local ledger after the Godot project exists:

```text
python scripts/evidence_run.py init --project-root <root> --manifest <root>/evidence-run.json --builder-id <id> --dimension <2d|2.5d|3d> --procedural-mode <none|seeded>
python scripts/evidence_run.py validate --project-root <root> --manifest <root>/evidence-run.json --report <root>/evidence-report.json --strict
```

The manifest schema is `evidence-run/v2`. It has four visual source arrays:
`visual_decisions`, `visual_scope_approvals`, `visual_correction_approvals`, and
`visual_generation_authorizations`, plus `reference_plans`,
`visual_contract_versions`, and `active_visual_contract_id`. There is no
`evidence-run/v1` compatibility reader and no compatibility reader of another kind.

An additive optional `visual_review_delegations` list contains artifact IDs. Omit
it or use `[]` for the original user-review flow. Older v2 validators reject this
extension; use the updated validator when supplying it. No existing source approval
or generation-authorization schema changes.

## Explicit delegated visual approval

Use only when the user has actually delegated the relevant visual decisions and
that instruction still applies. Scope approval and exact target approval remain
separate; an independent reviewer performs them under the granted scope. Preserve
the source instruction in existing task records before exercising it. Do not ask
the user again within that scope or invent a human signature. Revocation or a new
decision outside the grant returns to user review. This is not permission to waive
evidence, independent review or any other facet.

For final submission, register a UTF-8 JSON artifact of kind
`visual_review_delegation`, provenance `user_instruction`, with the usual path and
SHA-256. Its immutable content has exactly these fields:

| Field | Value |
|---|---|
| `schema_version` | `visual-review-delegation/v1` |
| `run_id` | This ledger's run UUID. |
| `contract_id` | Exact active visual contract ID. |
| `contract_sha256` | `visual_contract.canonical_sha256` of the ordered root-to-active contract chain as a JSON array, omitting `approval` from each node. Even an initial contract uses a one-element array. This binds inherited and added/replaced target paths/hashes. |
| `reviewer_id` | Actual independent visual reviewer, distinct from builder and matching target approval. |
| `grantor_role` | `user` describes the source of authority, not the reviewing agent. |
| `scope` | `visual_review` |
| `source_ref` | Traceable conversation/message or saved instruction reference. |
| `authorization_quote` | Exact relevant user instruction, not an agent's inferred permission. |
| `recorded_at` | Aware ISO-8601 time this binding record was created. |

All strings are nonempty. The builder may transcribe the real source and bind the
chosen reviewer within the delegated scope; this record is not a new user message.
List its artifact ID exactly once in `visual_review_delegations`. The matching
visual review uses the existing role `independent_reviewer`; `user` remains reserved
for actual user review. Keep the independent accept/reject record and exact evidence
coverage. An unused/orphan, duplicate, missing, malformed, wrong-run/contract/reviewer
or hash-drifted grant fails; a builder grant cannot authorize self-review. New target
bytes anywhere in that chain require a new binding record under the still-applicable
user authority. Follow `base_contract_id` to order the chain; manifest storage order
is not the chain order. Missing, duplicate or cyclic bases cannot authorize a grant.

Validation proves local structure and byte integrity, not who spoke, whether the
quote really authorizes this scope, or whether the review occurred. The orchestrator
and independent reviewer must verify the source instruction and actual authorship.
Retain superseded/revoked grants in historical evidence outside the current ledger;
never rewrite them or use them for current acceptance.

## Store and resolve sources

Use these recommended project-relative paths:

```text
docs/evidence/visual/decisions/<decision-id>.json
docs/evidence/visual/approvals/<approval-id>.json
docs/evidence/visual/authorizations/<authorization-id>.json
docs/evidence/visual/reports/<report-id>.json
```

Angle brackets are metavariables, not literal filenames. Before a project exists,
the same objects may be in task-local scratch storage. Copy them byte-for-byte into
the project before final manifest resolution. The manifest resolves source objects
by exact IDs and validates their byte-equivalent canonical bindings: decision,
plan-without-approval, scope approval, and authorization hashes must all agree.
The same source object may not be rewritten under a new meaning.

## Reference authoring order

1. Add the pending decision to `visual_decisions` and its matching plan to
   `reference_plans`; both have `approval: null`.
2. Validate the decision, collect exact full-set scope approval, and add the
   immutable `visual-scope-approval/v1` record to `visual_scope_approvals`.
3. Run authorization and add the immutable
   `visual-generation-authorization/v1` record to
   `visual_generation_authorizations`. A decision, plan, scope approval, and
   authorization must resolve as one chain.
4. For every generated reference PNG, add one `target_gameplay_image` artifact with the
   exact authorization `authorization_id`, target ID, reference slot ID, plan ID,
   plan revision, aware `generated_at`, project-relative path, SHA-256, coverage,
   and `imagegen_target` provenance.
5. Assemble the complete authorized candidate batch, then record target approval
   on its contract version. Only after that approval may the manifest set the
   active visual contract ID.

Validation requires scope approval before authorization, authorization before each
target generation, and target generation before target approval. An authorization
must have exactly one generated result for every authorized slot, no other slot,
and no result above its budget. Initial authorization covers the full initial plan;
delta authorization covers only its add/replace batch. The active contract is the
linear base chain plus additions minus explicit supersessions.

Production textures, sprites, decals, and material inputs are project source
assets, managed as described in `production-assets.md`. They require no reference
authorization or per-image user approval when implementing approved direction.
Keep their provenance and approved-target linkage in the project's asset notes;
record their integrated Godot captures in this ledger. Do not label source assets
as target references or runtime evidence to make them fit the artifact schema.

## Reference rejection and correction

On rejection, preserve the generated bytes and reclassify its artifact as
`rejected_target_image`. Keep its target ID, slot ID, path, SHA-256, coverage,
`generated_at`, plan ID, and plan revision; add aware `rejected_at`,
`rejection_artifact_id`, and `rejection_reviewer_id`. Its `authorization_id` still
resolves to the consumed authorization. A rejected target cannot be adopted into a
visual-contract mapping or reused as a target ID.

Add the distinct `visual-correction-approval/v1` record to
`visual_correction_approvals` after rejection. A correction authorization names the
rejected target and contains only that slot. It permits exactly one replacement
result with a fresh target ID and non-overwriting path. A second retry repeats this
approval-and-authorization cycle. A user rejection alone never authorizes a retry.

## Failure states and trust boundary

Use `PENDING` before evidence exists and `SUBMITTED` only for a complete candidate
requesting validation. Never write `PASS` or `BLOCKED` as input; `FAILED`, `PIVOT`,
and `STOP` are non-passing. The validator exits `0` for structurally VERIFIED, `1`
for PENDING, `2` for FAILED, and `3` for invalid input.

Path traversal, symlink escape, missing files, duplicate IDs, hash drift, invalid
base chains, branch/cycle bases, missing source resolution, timestamp inversion,
unbound artifacts, partial batches, or approval of an incomplete batch fail. The
gate cannot prevent platform delivery of raw reference ImageGen bytes, but unbound
reference bytes cannot enter an approved visual contract. Source production assets
are assessed through the integrated build's evidence, not reference authorizations.

Retain inside-root, SHA-256, Godot-runtime capture, independent review, and
target-Godot input/state/outcome rules. A screenshot is design evidence, never
mechanics or release proof.
