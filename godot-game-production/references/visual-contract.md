# Visual Contract

`scripts/visual_gate.py` is authoritative. JSON keys are unique, SHA-256 values are lowercase 64-hex digests, and every timestamp is timezone-aware ISO-8601. Canonical hashes use UTF-8 JSON, sorted object keys, and compact separators.

## File-first command flow

1. Write one complete pending `visual-decision/v2` to `docs/visual-contract/pending/<decision-id>/decision.json`.
2. Validate it and write its sibling report:

   ```text
   python godot-game-production/scripts/visual_gate.py check-decision --decision docs/visual-contract/pending/<decision-id>/decision.json --report docs/visual-contract/pending/<decision-id>/decision-report.json
   ```

3. Only a hash-bound `VALID_PENDING` report permits presentation. Render the human proposal:

   ```text
   python godot-game-production/scripts/visual_gate.py present-decision --decision docs/visual-contract/pending/<decision-id>/decision.json --report docs/visual-contract/pending/<decision-id>/decision-report.json
   ```

   Copy stdout verbatim into chat. The machine files and JSON examples in this reference must never be pasted into chat.
4. A reviewer distinct from the builder approves the complete proposed set in `visual-scope-approval/v1`. Run `authorize-generation` using the unchanged decision and approval bytes.
5. Only `visual-generation-authorization/v1` with `AUTHORIZED` permits generation. One authorized row has one result budget.
6. Bind every displayed, saved, hashed result to `authorization_id`, and present the complete authorized candidate batch.
7. After displaying the complete batch, render the stored localized target question:

   ```text
   python godot-game-production/scripts/visual_gate.py present-target-question --decision docs/visual-contract/pending/<decision-id>/decision.json --report docs/visual-contract/pending/<decision-id>/decision-report.json
   ```

8. Rejection consumes its authorization. A retry needs `visual-correction-approval/v1` and correction authorization.

| Command | Exit code `0` | Exit code `2` | Exit code `3` |
| --- | --- | --- | --- |
| `check-decision` | valid pending report written or already identical | invariant failure | JSON, schema, path, or output-binding error |
| `present-decision` | localized projection written to stdout | not used | invalid, unbound, unreadable, or overlapping input |
| `present-target-question` | localized target question written to stdout | not used | invalid, unbound, unreadable, proof-only, or overlapping input |
| `authorize-generation` | authorization written or already identical | decision or approval invariant failure | JSON, schema, path, input-pairing, or output-binding error |

Any nonzero exit blocks the next step. Presentation commands build their entire output before writing stdout, so a failure cannot emit a partial proposal or approval question.

## `visual-decision/v2`

`visual-decision/v1` is rejected. There is no compatibility reader or migration path.

All v2 variants contain exactly `schema_version`, UUID `decision_id`, `builder_id`, aware `created_at`, `decision_kind`, `state`, and `generation_status`, plus the exact variant fields below.

| `decision_kind` | Extra exact fields | Required values |
| --- | --- | --- |
| `initial_scope` | `reference_plan`, `user_interface` | `REFERENCE_SCOPE_PENDING`, `not_started`, initial plan |
| `delta_scope` | `change_scope`, `reference_plan`, `blocked_work`, `continuing_work`, `preserved_bindings`, `affected_targets`, `target_approval_scope`, `user_interface` | `VISUAL_DELTA_PENDING`, `not_started`, `local` or `global`, `complete_delta_batch_only`, delta plan |
| `reference_not_proof` | `verdict`, `preserved_evidence`, `user_interface` | `UNCHANGED`, `not_authorized`, `rejected`, complete canonical evidence-gate list |

For `initial_scope` and `delta_scope`, `user_interface` has exactly:

- `language`: a BCP-47-like tag for the user's current conversation language;
- `scope_question`: a nonempty localized question approving generation of the proposed image set;
- `target_question`: a nonempty localized question approving the exact displayed generated set.

Both questions end in a question mark. Russian (`ru` or `ru-*`) values contain Cyrillic; English (`en` or `en-*`) values contain Latin text. For every language, the agent—not a fixed English constant—owns correct localization.

For `reference_not_proof`, `user_interface` has exactly `language` and localized `message`. It has no scope or target question and cannot authorize generation.

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

A local delta blocks only dependent work. A global grammar change enumerates every affected target and dependency. A preserved binding has exactly `target_id`, `sha256`, and portable project-relative `path`; an affected target has exactly `target_id`, non-empty `dependent_work`, and `change_kind` of `add` or `replace`. Preserved and affected target IDs are each unique and disjoint. Blocked and continuing work are disjoint. The affected `replace` target set exactly equals the plan's `supersedes_target_id` set.

Treat a missing or changed player-visible state in an approved production, including a phase transformation, camera, environment, character, UI, or VFX treatment, as sufficient to reopen the visual gate. Write and validate the complete `delta_scope` decision before any implementation-detail question or game change; unresolved machine-only bindings stay as pending placeholders, while all localized presentation text stays complete. Never announce or reopen a visual delta in prose only. A missing base contract or target identity uses `<required-value>` or an indexed `<required-value:label>` in the complete pending object; put stated independent work in `continuing_work`. The localized scope question is the only user question in that response.

A global change uses one independently useful visual question per row and one `affected_targets` entry per affected target—never one representative or catch-all row or target for style, camera, UI, or other non-combinable questions. When exact target IDs are unavailable, use distinct placeholder identities and remain pending rather than merging affected targets.

## Reference plan and human presentation

`reference_plan` has exactly `plan_id`, positive integer `revision`, `kind`, `base_contract_id`, non-empty ordered `rows`, and `approval`. Initial uses `initial`, null base, and initial rows. Delta uses `delta`, non-empty base, and add/replace rows. Replacement requires non-empty `supersedes_target_id`; otherwise it is null. Pending approval is `null`.

Each row has exactly `reference_slot_id`, `target_kind`, `subject`, `visual_question`, `coverage`, `composition`, `motion_cue`, `sound_cue`, `dependent_work`, `rationale`, `presentation`, `image_count`, `change_kind`, and `supersedes_target_id`.

- `target_kind` is `location`, `gameplay_state`, `ui_mode`, `character`, or `asset_family`.
- `coverage` and `dependent_work` are non-empty string arrays.
- `composition` has exactly `camera`, `angle`, `environment`, `characters`, `ui`, and `vfx`.
- `presentation` has exactly `title`, `image_description`, and `purpose`. Each is nonempty localized text. `image_description` states what the proposed picture visibly contains and how it is composed; `purpose` states which production decision it settles. All `presentation` and `user_interface` text rejects control characters or embedded line breaks and rejects machine-facing content such as schema fields, hashes, internal IDs, JSON syntax, code fences, and artifact paths. This preserves one physical paragraph per numbered item. Placeholders, an internal slot ID, or a value consisting only of a technical ID are invalid.
- `image_count` is integer `1`, never a boolean.

Cardinality is needs-derived: one row maps to one proposed image and one numbered item. There is no minimum, maximum, or preferred pack size. A late visual discovery creates a new delta with only the independently needed rows; then repeat the same approval procedure. Never pad or truncate a plan to a requested or conventional count.

`present-decision` validates the decision and report, then emits each row in order as `N) <title>. <image_description>. <purpose>.` with a blank line between items. For scope variants the last nonempty line is the stored localized `scope_question`; for `reference_not_proof` the output is only its stored localized message. The output contains no JSON, code fence, schema name, hash, artifact path, or internal slot ID.

Placeholders are allowed only in missing machine-facing pending values. `presentation` and `user_interface` never allow them. Authorization rejects unresolved placeholders anywhere in the complete decision. Canonical placeholder forms are `<required-value>` and indexed `<required-value:label>`; `unspecified`, `unknown`, `TBD`, `TODO`, `PENDING_*`, and `PLACEHOLDER` markers also block authorization.

## Remaining machine schemas

### `visual-decision-report/v1`

The report has exactly `schema_version`, `decision_id`, `decision_sha256`, `status`, and `errors`. `VALID_PENDING` has an empty errors array. Its ID and canonical hash match the complete decision. Both presentation commands reject a stale or mismatched report.

### `visual-scope-approval/v1`

The record has exactly `schema_version`, `approval_artifact_id`, `decision_id`, `reviewer_id`, `decision`, `recorded_at`, `decision_sha256`, `plan_sha256`, and `approved_slot_ids`. Its reviewer differs from the builder; `decision` is `approved`; `recorded_at` is aware and after creation; the ordered IDs exactly equal plan rows. `decision_sha256` binds the complete decision; `plan_sha256` binds its plan after omitting `approval`.

### `visual-correction-approval/v1`

The record has exactly `schema_version`, `approval_artifact_id`, `reviewer_id`, `decision`, `recorded_at`, `plan_id`, `plan_revision`, `reference_slot_id`, `rejected_target_id`, `rejected_target_sha256`, and `correction_direction`. It is approved by a non-builder after the rejected target timestamp; it repeats the exact plan, slot, target, and hash. `correction_direction` has no placeholder.

### `visual-generation-authorization/v1`

The immutable record has exactly `schema_version`, `authorization_id`, `status`, `batch_kind`, `issued_at`, `decision_id`, `decision_sha256`, `plan_id`, `plan_revision`, `plan_sha256`, `approval_artifact_id`, `approval_sha256`, `authorized_slots`, `base_contract_id`, `supersedes_target_ids`, `rejected_target_id`, and `correction_approval_artifact_id`.

`status` is `AUTHORIZED`; `batch_kind` is `initial`, `delta`, or `correction`; `issued_at` is aware and after its approval. Every `authorized_slots` row is exactly `reference_slot_id` and integer `result_budget: 1`; IDs are unique. Initial has null base. Delta has its exact base. Only correction has non-null rejected target and correction IDs, and it contains exactly the rejected slot. `supersedes_target_ids` is the ordered unique replacement set. Decision, plan, and approval hashes are canonical bindings.

## Complete machine-file example

This is valid `decision.json` content for an English two-row initial proposal. It belongs in the pending file and must never be pasted into chat.

```json
{
  "schema_version": "visual-decision/v2",
  "decision_id": "11111111-1111-1111-1111-111111111111",
  "builder_id": "builder",
  "created_at": "2026-08-20T10:00:00+10:00",
  "decision_kind": "initial_scope",
  "state": "REFERENCE_SCOPE_PENDING",
  "generation_status": "not_started",
  "reference_plan": {
    "plan_id": "vrp-001",
    "revision": 1,
    "kind": "initial",
    "base_contract_id": null,
    "rows": [
      {
        "reference_slot_id": "REF-01",
        "target_kind": "gameplay_state",
        "subject": "normal traversal",
        "visual_question": "canonical play-distance composition",
        "coverage": ["exploration/default"],
        "composition": {"camera":"side view","angle":"canonical","environment":"forest room","characters":"player and hazard","ui":"gameplay HUD","vfx":"interaction cue"},
        "motion_cue": "walk direction",
        "sound_cue": "footstep response",
        "dependent_work": ["core loop"],
        "rationale": "No approved target resolves normal play.",
        "presentation": {
          "title": "Exploring the forest room",
          "image_description": "Side-view gameplay with the player moving between trees and a readable hazard, with camera distance, environment scale, HUD, and interaction effect visible",
          "purpose": "This reference settles the primary gameplay composition"
        },
        "image_count": 1,
        "change_kind": "initial",
        "supersedes_target_id": null
      },
      {
        "reference_slot_id": "REF-02",
        "target_kind": "gameplay_state",
        "subject": "failure and retry",
        "visual_question": "failure-state composition",
        "coverage": ["failure/retry"],
        "composition": {"camera":"side view","angle":"impact","environment":"forest room","characters":"player and hazard","ui":"retry overlay","vfx":"hit cue"},
        "motion_cue": "knockback",
        "sound_cue": "failure response",
        "dependent_work": ["retry flow"],
        "rationale": "Failure must read independently from normal play.",
        "presentation": {
          "title": "Character defeat",
          "image_description": "The same room at the moment of damage, with the character knocked back, the hazard clearly readable, and the retry overlay visible over the scene",
          "purpose": "This reference settles the visual treatment of defeat and return to play"
        },
        "image_count": 1,
        "change_kind": "initial",
        "supersedes_target_id": null
      }
    ],
    "approval": null
  },
  "user_interface": {
    "language": "en",
    "scope_question": "Do you approve this exact image set for generation?",
    "target_question": "Do you approve this exact displayed image set?"
  }
}
```

## Artifact binding and failure

Display the actual bitmap, copy it to a project-local PNG, verify SHA-256, and record buildability, motion cue, and sound cue. Each result is a `target_gameplay_image` artifact with its exact `authorization_id`. A rejected result becomes `rejected_target_image`, preserving target ID, slot, path, hash, bytes, coverage, and `generated_at` with plan/revision and rejection provenance. Present the complete authorized candidate batch before target approval; that approval binds the complete ID/hash/path set.

Fail closed for missing or partial scope approval, generation before authorization, missing, duplicate, extra, unbound, unshown, moved, or hash-drifted targets, timestamp inversion, invalid base, hidden replacement, global contradiction, or incomplete batch. Writing, validation, report binding, or rendering failure emits no approval question and permits no ImageGen call. The platform may return raw ImageGen bytes, but they cannot obtain verified evidence or release status without this authorization chain.
