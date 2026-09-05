# User-Facing Visual Proposal Design

## Problem

The current visual-reference gate exposes its complete `visual-decision/v1` JSON
object in chat. The object is useful to scripts, hashes, approvals, and evidence,
but it is not a usable interface for a person deciding which images should be
generated. The fixed English approval questions make the same workflow hostile in
non-English conversations.

## Decision

Keep the complete visual decision as a machine artifact, but never use serialized
JSON as the user-facing proposal. The agent writes and validates the decision in a
project-local file, renders a numbered plain-language projection from that file,
and sends only the projection and a localized approval question to the user.

The reference count remains dynamic. One decision row still maps to one proposed
image and one numbered item; the design introduces no minimum, maximum, or preferred
pack size.

## User Experience

For a Russian-language conversation, a normal response has this shape:

```text
1) Исследование лесной локации. Игровой вид сбоку: персонаж движется между
деревьями и преодолевает опасность; в кадре видны рабочая дистанция камеры,
масштаб окружения, HUD и эффект взаимодействия. Референс нужен для утверждения
основной игровой композиции.

2) Поражение персонажа. Та же локация в момент получения урона: персонажа
отбрасывает назад, опасность хорошо читается, появляется экран повторной попытки.
Референс определяет визуальную подачу поражения и восстановления игры.

Подтверждаете именно этот набор изображений для генерации?
```

Every numbered item is a standalone description of its proposed image. It states:

- what scene, state, character, interface, or asset family the image depicts;
- the visible composition or presentation choices the image must establish; and
- why production needs this reference.

The response contains no JSON, code fence, schema name, hash, artifact path,
internal slot ID, or other machine-facing field. A title or ID without an image
description is invalid.

The agent uses the language of the user's current conversation for every numbered
description and for both approval questions. If the language genuinely cannot be
inferred, the agent asks once before creating the decision. It does not silently
fall back to English.

The scope question asks whether the proposed image set may be generated. After the
images are generated and displayed, the target question asks whether the exact
displayed image set is approved. Both questions are localized; the existing fixed
English literals are removed from the user interface.

## Machine Artifact

Before presenting a proposal, the agent writes exactly one decision to:

```text
docs/visual-contract/pending/<decision-id>/decision.json
```

The validator report is written beside it as `decision-report.json`. These are
project-relative workflow artifacts. They remain available across turns and bind
later approval and generation records; normal chat does not mention their paths.

The breaking schema becomes `visual-decision/v2`. No v1 compatibility path or
migration is required because the skill has no users or retained production
decisions.

Each reference-plan row gains one `presentation` object with exactly `title`,
`image_description`, and `purpose`. All three values are non-empty localized text.
`image_description` says what the proposed picture visibly contains and how it is
composed; `purpose` says which production choice the reference settles. The
validator rejects placeholders and values consisting only of a technical ID. The
three fields are the canonical user-facing content rendered for that image.

Pending `initial_scope` and `delta_scope` decisions also carry a top-level
`user_interface` object with exactly:

- `language`: the language used for the current user conversation;
- `scope_question`: the localized question that approves generation of the
  proposed set; and
- `target_question`: the localized question that approves the exact displayed
  generated set.

The decision kind, state, approved slot IDs, hashes, and approval artifacts retain
the machine meaning of approval. Approval correctness never depends on matching an
English sentence.

A `reference_not_proof` decision is also stored rather than shown as JSON. Its
`user_interface` contains `language` and a localized `message` explaining why the
existing reference cannot replace runtime or release evidence. It has no scope or
target question and cannot authorize generation.

## Rendering and Data Flow

The visual gate gains a deterministic presentation command. For an initial or
delta decision it:

1. loads the decision file with duplicate-key rejection;
2. validates the complete pending decision;
3. loads the matching `VALID_PENDING` report and verifies its decision hash;
4. joins each row's localized `title`, `image_description`, and `purpose` into one
   complete numbered paragraph and emits items `1)` through `N)` in plan order;
5. emits the stored localized `scope_question` as the final non-empty line.

The renderer never emits the raw decision. The agent copies the renderer's output
verbatim into chat instead of manually paraphrasing it. This makes the approved
human-readable set and the hashed machine decision the same artifact projection.

After generation, the existing complete-batch presentation remains mandatory. The
agent displays the actual images and ends with the decision's localized
`target_question` rather than the old English literal.

The complete flow is:

```text
write decision JSON -> validate file -> render localized numbered list ->
user approves scope -> authorize/generate exact batch -> display images ->
ask localized target question -> user approves targets
```

Late visual discoveries use the same file-first renderer for `delta_scope`. The
agent continues unrelated work exactly as before. A global delta still expands
non-combinable questions and affected targets rather than hiding them in a catch-all
item.

## Failure Behaviour

If writing, validation, report binding, or rendering fails, the agent does not ask
for approval and does not invoke ImageGen. It reports the failure in the user's
language without dumping the JSON. An unresolved placeholder may appear in the
stored pending decision, but generation authorization continues to reject it.

Partial approval, rejection, correction authorization, immutable hashes, and the
separation between reference evidence and runtime proof remain unchanged.

## Behavioral Scorer

The behavioral scorer stops extracting a fenced decision from the answer. It
receives the decision file as a separate input and validates it directly. For scope
proposals it verifies:

- the decision and report are valid and hash-bound;
- the answer contains no JSON/code fence or raw machine schema fields;
- there is exactly one numbered item per plan row, in plan order;
- each item equals the deterministic rendering of its row's complete `presentation`
  object rather than an ID-only label;
- the final non-empty line equals the decision's localized `scope_question`;
- only the expected decision and report artifacts were written; and
- ImageGen was not called before approval.

`reference_not_proof` is checked against its localized stored message and likewise
rejects raw JSON. Existing decision semantics, dynamic row counts, delta impact,
replacement, proof-gate, report-collision, and run-policy checks remain.

## Verification

Deterministic tests cover at least Russian and English proposals, raw-JSON leakage,
missing or ID-only descriptions, wrong numbering, row-order drift, list/file drift,
an English question in a Russian decision, an invalid decision/report binding,
unexpected writes, late delta presentation, target-question localization, and
`reference_not_proof` presentation.

Behavioral forward tests rerun the affected initial, late-delta, global-delta, and
reference-not-proof cases. The full unit suite and official skill validator must
pass before the repository and installed copy are updated.

## Acceptance Criteria

- A user never receives raw visual-decision JSON in normal chat.
- Every proposed image appears as one detailed numbered description in the user's
  language.
- Scope and target approval questions use the user's language.
- The displayed list is deterministically derived from the validated decision file.
- Approval and generation remain fail-closed and bound to the exact dynamic set.
- Initial, delta, correction, evidence, and release gates retain their current
  safety properties.
