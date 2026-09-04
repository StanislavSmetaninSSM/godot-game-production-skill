# Visual Contract

`scripts/visual_gate.py` is authoritative. JSON keys are unique, SHA-256 values are lowercase 64-hex digests, and every timestamp is timezone-aware ISO-8601. Canonical hashes use UTF-8 JSON, sorted object keys, and compact separators.

## Command flow

1. Write one pending `visual-decision/v1`, then run `check-decision`.
2. Only `VALID_PENDING` permits presenting it and asking `Do you exactly approve the proposed reference slot ID set?`.
3. A reviewer distinct from the builder writes `visual-scope-approval/v1`; run `authorize-generation` using unchanged decision and approval bytes.
4. Only `visual-generation-authorization/v1` with `AUTHORIZED` permits generation. One authorized row has one result budget.
5. Bind every displayed, saved, hashed result to `authorization_id`, then present the complete authorized candidate batch and ask `Do you exactly approve the displayed target ID set?`.
6. Rejection consumes its authorization. A retry needs `visual-correction-approval/v1` and correction authorization.

| Command | Exit code `0` | Exit code `2` | Exit code `3` |
| --- | --- | --- | --- |
| `check-decision` | valid pending decision | invariant failure | JSON, schema, path, or output-binding error |
| `authorize-generation` | written or byte-identical authorization | decision or approval invariant failure | JSON, schema, path, input-pairing, or output-binding error |

Any nonzero exit blocks the next step.

## Schema tables

### `visual-decision/v1`

All variants contain `schema_version`, UUID `decision_id`, `builder_id`, aware `created_at`, `decision_kind`, `state`, and `generation_status`.

| `decision_kind` | Extra exact fields | Values |
| --- | --- | --- |
| `initial_scope` | `reference_plan`, `scope_question` | `REFERENCE_SCOPE_PENDING`, `not_started`, initial plan |
| `delta_scope` | `change_scope`, `reference_plan`, `blocked_work`, `continuing_work`, `preserved_bindings`, `affected_targets`, `target_approval_scope`, `scope_question` | `VISUAL_DELTA_PENDING`, `not_started`, `local` or `global`, `complete_delta_batch_only`, delta plan |
| `reference_not_proof` | `verdict`, `preserved_evidence` | `UNCHANGED`, `not_authorized`, `rejected`, complete canonical evidence-gate list |

The exact ordered canonical proof gates are:

- `actual bitmap presentation`
- `project-local PNG`
- `SHA-256 binding`
- `buildability`
- `motion cue`
- `sound cue`
- `target-Godot input/state/outcome evidence`
- `TDD`
- `independent review`
- `core play`
- `systems/holism`
- `content`
- `visual`
- `audio/feedback`
- `UX/onboarding`
- `reliability/performance`
- `ship`

The scope question is exactly `Do you exactly approve the proposed reference slot ID set?`. `reference_not_proof` cannot reach authorization. A local delta blocks only dependent work. A global grammar change enumerates every affected target and dependency. A preserved binding has exactly `target_id`, `sha256`, and portable project-relative `path`; an affected target has exactly `target_id`, non-empty `dependent_work`, and `change_kind` of `add` or `replace`. Preserved and affected target IDs are each unique and disjoint. Blocked and continuing work are disjoint. The affected `replace` target set exactly equals the plan's `supersedes_target_id` set.

Treat a missing or changed player-visible state in an approved production, including a phase transformation, camera, environment, character, UI, or VFX treatment, as sufficient to reopen the visual gate. Emit and validate the complete `delta_scope` decision before any implementation-detail question or game change; unresolved presentation details stay as pending placeholders. Never announce or reopen a visual delta in prose only. A missing base contract or target identity uses `<required-value>` or an indexed `<required-value:label>` in the complete pending object; put stated independent work in `continuing_work`. The canonical scope question is the only user question in that response.

A global change uses one independently useful visual question per row and one `affected_targets` entry per affected target—never one representative or catch-all row or target for style, camera, UI, or other non-combinable questions. When exact target IDs are unavailable, use distinct placeholder identities and remain pending rather than merging affected targets.

`reference_plan` has exactly `plan_id`, positive integer `revision`, `kind`, `base_contract_id`, non-empty ordered `rows`, and `approval`. Initial uses `initial`, null base, and initial rows. Delta uses `delta`, non-empty base, and add/replace rows. Replacement requires non-empty `supersedes_target_id`; otherwise it is null. Pending approval is `null`. Placeholders are allowed only while decision validation is pending; authorization rejects unresolved placeholders anywhere in the complete decision, not only in the reference plan. Canonical text/identity forms are `<required-value>` and indexed `<required-value:label>`. Common unresolved markers such as `unspecified`, `unknown`, `TBD`, `TODO`, `PENDING_*`, and a `PLACEHOLDER` token also block authorization.

Each row has exactly `reference_slot_id`, `target_kind`, `subject`, `visual_question`, `coverage`, `composition`, `motion_cue`, `sound_cue`, `dependent_work`, `rationale`, `image_count`, `change_kind`, and `supersedes_target_id`. `target_kind` is `location`, `gameplay_state`, `ui_mode`, `character`, or `asset_family`; `coverage` and `dependent_work` are non-empty string arrays; composition has exactly `camera`, `angle`, `environment`, `characters`, `ui`, and `vfx`. `image_count` is integer `1`, never a boolean. There is no preset minimum, maximum, or preferred pack size: every approved row maps to exactly one generated target and every generated target maps to exactly one approved row.

### `visual-decision-report/v1`

The report has exactly `schema_version`, `decision_id`, `decision_sha256`, `status`, and `errors`. `VALID_PENDING` has an empty errors array. The hash is the canonical hash of the complete decision.

### `visual-scope-approval/v1`

The record has exactly `schema_version`, `approval_artifact_id`, `decision_id`, `reviewer_id`, `decision`, `recorded_at`, `decision_sha256`, `plan_sha256`, and `approved_slot_ids`. Its reviewer differs from the builder; `decision` is `approved`; `recorded_at` is aware and after creation; the ordered IDs exactly equal plan rows. `decision_sha256` binds the complete decision; `plan_sha256` binds its plan after omitting `approval`.

### `visual-correction-approval/v1`

The record has exactly `schema_version`, `approval_artifact_id`, `reviewer_id`, `decision`, `recorded_at`, `plan_id`, `plan_revision`, `reference_slot_id`, `rejected_target_id`, `rejected_target_sha256`, and `correction_direction`. It is approved by a non-builder after the rejected target timestamp; it repeats the exact plan, slot, target, and hash. `correction_direction` has no placeholder.

### `visual-generation-authorization/v1`

The immutable record has exactly `schema_version`, `authorization_id`, `status`, `batch_kind`, `issued_at`, `decision_id`, `decision_sha256`, `plan_id`, `plan_revision`, `plan_sha256`, `approval_artifact_id`, `approval_sha256`, `authorized_slots`, `base_contract_id`, `supersedes_target_ids`, `rejected_target_id`, and `correction_approval_artifact_id`.

`status` is `AUTHORIZED`; `batch_kind` is `initial`, `delta`, or `correction`; `issued_at` is aware and after its approval. Every `authorized_slots` row is exactly `reference_slot_id` and integer `result_budget: 1`; IDs are unique. Initial has null base. Delta has its exact base. Only correction has non-null rejected target and correction IDs, and it contains exactly the rejected slot. `supersedes_target_ids` is the ordered unique replacement set. Decision, plan, and approval hashes are canonical bindings.

## Complete valid JSON examples

Two-row initial decision:

```json
{"schema_version":"visual-decision/v1","decision_id":"11111111-1111-1111-1111-111111111111","builder_id":"builder","created_at":"2026-08-20T10:00:00+10:00","decision_kind":"initial_scope","state":"REFERENCE_SCOPE_PENDING","generation_status":"not_started","reference_plan":{"plan_id":"vrp-001","revision":1,"kind":"initial","base_contract_id":null,"rows":[{"reference_slot_id":"REF-01","target_kind":"gameplay_state","subject":"traversal","visual_question":"play composition","coverage":["exploration/default"],"composition":{"camera":"side","angle":"canonical","environment":"forest","characters":"player and hazard","ui":"HUD","vfx":"motion"},"motion_cue":"walk","sound_cue":"step","dependent_work":["core loop"],"rationale":"play framing","image_count":1,"change_kind":"initial","supersedes_target_id":null},{"reference_slot_id":"REF-02","target_kind":"gameplay_state","subject":"retry","visual_question":"failure composition","coverage":["failure/retry"],"composition":{"camera":"side","angle":"failure","environment":"forest","characters":"player and hazard","ui":"retry","vfx":"impact"},"motion_cue":"knockback","sound_cue":"failure","dependent_work":["retry"],"rationale":"recovery framing","image_count":1,"change_kind":"initial","supersedes_target_id":null}],"approval":null},"scope_question":"Do you exactly approve the proposed reference slot ID set?"}
```

Mixed add/replace delta:

```json
{"schema_version":"visual-decision/v1","decision_id":"22222222-2222-2222-2222-222222222222","builder_id":"builder","created_at":"2026-08-20T11:00:00+10:00","decision_kind":"delta_scope","state":"VISUAL_DELTA_PENDING","generation_status":"not_started","change_scope":"local","reference_plan":{"plan_id":"vrp-002","revision":2,"kind":"delta","base_contract_id":"vc-001","rows":[{"reference_slot_id":"REF-03","target_kind":"ui_mode","subject":"inventory","visual_question":"inventory layout","coverage":["inventory"],"composition":{"camera":"screen","angle":"front","environment":"overlay","characters":"portrait","ui":"grid","vfx":"selection"},"motion_cue":"selection","sound_cue":"tick","dependent_work":["inventory"],"rationale":"new mode","image_count":1,"change_kind":"add","supersedes_target_id":null},{"reference_slot_id":"REF-04","target_kind":"gameplay_state","subject":"boss","visual_question":"phase two","coverage":["boss/phase-two"],"composition":{"camera":"side","angle":"combat","environment":"arena","characters":"player and boss","ui":"meter","vfx":"change"},"motion_cue":"lunge","sound_cue":"roar","dependent_work":["boss"],"rationale":"replace angle","image_count":1,"change_kind":"replace","supersedes_target_id":"TARGET-03"}],"approval":null},"blocked_work":["boss"],"continuing_work":["save menu"],"preserved_bindings":[{"target_id":"TARGET-01","sha256":"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa","path":"docs/visual-contract/vc-001/targets/target-01.png"}],"affected_targets":[{"target_id":"TARGET-03","dependent_work":["boss"],"change_kind":"replace"}],"target_approval_scope":"complete_delta_batch_only","scope_question":"Do you exactly approve the proposed reference slot ID set?"}
```

Full authorization:

```json
{"schema_version":"visual-generation-authorization/v1","authorization_id":"vga-001","status":"AUTHORIZED","batch_kind":"initial","issued_at":"2026-08-20T10:10:00+10:00","decision_id":"11111111-1111-1111-1111-111111111111","decision_sha256":"bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb","plan_id":"vrp-001","plan_revision":1,"plan_sha256":"cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc","approval_artifact_id":"scope-001","approval_sha256":"dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd","authorized_slots":[{"reference_slot_id":"REF-01","result_budget":1},{"reference_slot_id":"REF-02","result_budget":1}],"base_contract_id":null,"supersedes_target_ids":[],"rejected_target_id":null,"correction_approval_artifact_id":null}
```

Correction authorization:

```json
{"schema_version":"visual-generation-authorization/v1","authorization_id":"vga-002","status":"AUTHORIZED","batch_kind":"correction","issued_at":"2026-08-20T12:10:00+10:00","decision_id":"22222222-2222-2222-2222-222222222222","decision_sha256":"eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee","plan_id":"vrp-002","plan_revision":2,"plan_sha256":"ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff","approval_artifact_id":"scope-002","approval_sha256":"1111111111111111111111111111111111111111111111111111111111111111","authorized_slots":[{"reference_slot_id":"REF-04","result_budget":1}],"base_contract_id":"vc-001","supersedes_target_ids":["TARGET-03"],"rejected_target_id":"TARGET-09","correction_approval_artifact_id":"correction-001"}
```

## Artifact binding and failure

Display the actual bitmap, copy it to a project-local PNG, verify SHA-256, and record buildability, motion cue, and sound cue. Each result is a `target_gameplay_image` artifact with its exact `authorization_id`. A rejected result becomes `rejected_target_image`, preserving target ID, slot, path, hash, bytes, coverage, and `generated_at` with plan/revision and rejection provenance. Present the complete authorized candidate batch before target approval; that approval binds the complete ID/hash/path set.

Fail closed for missing or partial scope approval, generation before authorization, missing, duplicate, extra, unbound, unshown, moved, or hash-drifted targets, timestamp inversion, invalid base, hidden replacement, global contradiction, or incomplete batch. The platform may return raw ImageGen bytes, but they cannot obtain verified evidence or release status without this authorization chain.
