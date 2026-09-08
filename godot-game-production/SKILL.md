---
name: godot-game-production
description: Use when creating, continuing, repairing, or broadly developing a Godot 2D, 2.5D, or 3D game across game intent, visual direction, mechanics, production, or release. Do not use for one isolated asset or a narrow one-facet audit.
---

# Godot Game Production

## Required sub-skills

**REQUIRED SUB-SKILL:** Use `brainstorming` before creative definition or behavior changes.

**REQUIRED SUB-SKILL:** Use `spec-kit-superpowers-bridge`; Spec Kit owns durable constitution, spec, plan, tasks, and consistency, while Superpowers owns execution.

**REQUIRED SUB-SKILL:** Use `imagegen` for the initial visual contract, every material visual re-entry, and production bitmap assets when generation or editing is the suitable authoring method. Invoke its built-in image generation path by default.

For implementation use `test-driven-development`; for failures use `systematic-debugging`; before completion use `requesting-code-review` and `verification-before-completion`.

## Start or resume

For an existing project, preserve reality before planning. Do not reset, clean, overwrite, or regenerate user work. Record the initial working-tree status before any write; inspect `project.godot`, engine/import settings, entry scenes, autoloads, input actions, save data, logs, and current specs; then run the existing game before changing it. Actual target-build behavior outranks status prose. Retain an old pass only when its exact artifacts, hashes, review coverage, and requirement still match. Reopen stale, missing, changed, unreviewed, or runtime-contradicted evidence. Resume the first unpassed gate without rebuilding already verified work. If safe inspection is blocked, report the pending audit instead of guessing.

For a new project, establish the bounded experience promise, player, platform, input, dimension, camera, session, mechanics, failure/retry, persistence, target hardware, references, exclusions, and risks. Ask only consequential unresolved decisions, one at a time.

## Mandatory state sequence

`AUDIT -> SPECIFY -> VISUAL_PENDING -> VISUAL_APPROVED -> GODOT_FEASIBILITY ->
CORE_LOOP -> PRODUCTION -> RELEASE`

When the brief and core mechanics are sufficient and no consequential specification decision remains, read `references/visual-contract.md` and `references/evidence-ledger.md` before creating or changing a visual decision.

The numbered approval procedure below governs reference images that establish or change visual direction. Working textures, sprites, decals, and other production assets implementing approved direction follow **Production asset authoring** below; they do not consume reference slots or require per-image user approval.

1. Before writing any pending `visual-decision/v2`, read `references/visual-contract.md` and `references/evidence-ledger.md` in the current turn. Construct it from the exact complete `visual-decision/v2` schema in `references/visual-contract.md`; abbreviated, invented aliases, and short objects are invalid. Derive a needs-based initial or delta row set; a requested image count is not an input to cardinality. Every row has one complete localized `presentation`, and each `user_interface` string uses the user's current conversation language. If that language genuinely cannot be inferred, ask once before constructing the decision. Write the complete object with `approval: null` and no invented supplied value to `docs/visual-contract/pending/<decision-id>/decision.json`.
2. Run `scripts/visual_gate.py check-decision` with that decision path and sibling `decision-report.json`. A nonzero exit blocks presentation. Only a hash-bound `VALID_PENDING` report permits the next step; it never permits image generation.
3. For pending `initial_scope` or `delta_scope` decisions, run `present-decision` against those two files and copy its stdout verbatim into chat. The projection has one numbered item per row, in plan order. Each item says what the image is, what the image visibly contains and how it is composed, and why production needs it. The final line is the localized scope question stored in the decision. Wait for explicit full-set approval; partial approval changes nothing.
4. Normal chat contains only that human projection. Never paste decision JSON, a JSON code fence, internal IDs, hashes, schema names, or artifact paths into chat. A premature or scope-invalid request for a pending `initial_scope` or `delta_scope` may be explicitly refused, but the same response must continue the file-first gate with the validated localized projection, never refusal-only prose. If writing, validation, report binding, or rendering fails, explain the failure in the user's language without JSON; ask no approval question and do not invoke ImageGen.
5. After the user's exact full-set approval, write the exact `visual-scope-approval/v1` record and run `authorize-generation` against the unchanged decision and approval bytes.
6. For reference generation, only when the emitted immutable `visual-generation-authorization/v1` says `AUTHORIZED`, invoke ImageGen. Make at most one call for every authorized slot and no call for any other slot in that reference batch.
7. Save and hash every result, and put the authorization's exact `authorization_id` on its `target_gameplay_image` or `rejected_target_image` artifact row. Raw output without that chain is retained for audit but cannot validate or enter an approved visual contract.
8. Present the complete authorized candidate batch, then run `present-target-question` against the bound decision and report and copy its localized stdout verbatim. Target approval remains separate and occurs only after generation and display of the complete exact batch.
9. A later uncovered material question uses a new delta decision and repeats both approval gates. Treat a missing or changed player-visible state in an approved production, including a phase transformation, camera, environment, character, UI, or VFX treatment, as sufficient to reopen the visual gate. Write and validate the complete `delta_scope` decision before any implementation-detail question or game change; unresolved machine-only bindings stay as pending placeholders, while every user-facing `presentation` field remains complete. Never announce or reopen a visual delta in prose only. A missing base contract or target identity uses `<required-value>` or an indexed `<required-value:label>` in the complete pending object; put stated independent work in `continuing_work`. The localized scope question is the only user question in that response.
10. Local deltas block only dependent work. A global change uses one independently useful visual question per row and one `affected_targets` entry per affected target—never one representative or catch-all row or target for style, camera, UI, or other non-combinable questions. When exact target IDs are unavailable, use distinct placeholder identities such as `<required-value:style-target>` and remain pending. Replacements bind exact supersession.
11. User rejection consumes the old authorization and authorizes no retry. Record the rejected attempt, obtain a distinct `visual-correction-approval/v1`, then use the correction form of `authorize-generation`; the new authorization permits exactly one replacement result for that slot.
12. A `reference_not_proof` decision rejects references as runtime/release proof and preserves all canonical evidence gates. `reference_not_proof` writes its complete decision to the pending path, renders only its localized stored message, does not ask the scope question, and cannot reach authorization.

Reference images cannot enter an approved visual contract without the exact approved authorization chain. Production assets are project source files; their integration is checked through Godot runtime evidence. The decision validator is `scripts/visual_gate.py`; the behavioral acceptance scorer for pending reference proposals is `tests/behavioral/score_dynamic_visual_reference.py`.

Remain `VISUAL_PENDING` until the initial contract receives exact target approval. If image generation is unavailable, expose the pending gate; prose, code, an unrelated generator, or a source render does not replace it.

Generated targets are design evidence only. After approval, reproduce one representative target in the actual Godot project. Read `references/gameplay-evidence.md` and prove a complete causal core loop before content multiplication.

When broad enemy, level, UI, asset, or content production is requested before exact target approval, explicitly state this order: `complete target gameplay pack with per-frame buildability accounts -> exact user approval -> one representative target reproduced in the actual Godot project -> asset and content multiplication`.

## Production asset authoring

After target approval, choose how to implement each needed asset or coherent asset family: suitable existing/library assets, procedural or native authoring, ImageGen, or a combination. Explicitly consider ImageGen when choosing how to make bitmap art; use it when it materially helps achieve the approved appearance, rather than treating reference generation as its only role. Record the choice briefly in the existing production task or asset notes. Do not generate images merely to satisfy a tool-use quota.

Read `references/production-assets.md` when producing textures, materials, sprites, tiles, decals, portraits, or other game art. Independently generate, edit, integrate, and refine working assets within approved direction and the user's task and budget; do not ask the user to approve the method, prompt, each texture, or routine revisions. This also applies to assets needed for representative Godot feasibility before broad production.

Judge the boundary by what the image decides, not its filename: a texture implementing approved costume fabric is production work; a proposed new costume identity or material language needs reference re-entry. New or changed visual direction, an uncovered material visual question, or a user-requested redesign repeats scope and target approval. A rejected implementation can be corrected autonomously while its direction remains approved. Reference rejection still follows the reference correction gate. Communicate progress and results in the user's language; displaying a working asset is not an approval request.

## Route only what is needed

- Read `references/production-operations.md` when the current production interval has two or more implementation slices scheduled to overlap or be delegated concurrently, or when multiple agents or worktrees will implement related parts of the same candidate. Do not read it merely for several serial steps in one bounded slice.
- Read `references/gameplay-evidence.md` when planning or judging playtest matrices, fixtures, seeded coverage, or integrated player-journey evidence. This routing complements the existing post-approval core-loop use of that reference.
- Read `references/procedural-art.md` for generated visual systems or repeated assets.
- For 2D or 2.5D, read `references/godot-2d.md` and do not read the 3D reference.
- For 3D, read `references/godot-3d.md` and do not read the 2D reference.
- Load both only for an explicitly hybrid pipeline. State the next user-visible approval or evidence gate after routing.
- Read `references/evidence-ledger.md` when creating or validating milestone evidence.
- Read `references/release-checks.md` for milestone or release decisions.

## Stop rules

- Give every mutable state, decision, event, timer, and persisted save fact exactly one authoritative owner. Consumers read or subscribe to that owner; they must not infer, shadow, or independently write a competing version. When an owner knows a fact but does not publish it, the implementation slice must extend the owner's transition before a consumer uses that fact. A neutral consumer fallback or post-release owner change does not complete requested fact-specific behavior; if the owner change is forbidden, stop and escalate the conflict instead of moving or deferring the authority boundary.
- A screenshot never proves mechanics; require input, state, outcome, and filmstrip/video evidence from the target Godot build.
- Core play, systems/holism, content, visual, audio/feedback, UX/onboarding, reliability/performance, and ship each fail closed; never average them.
- Translate commercial references into bounded experience and quality attributes, never their inventory. Before feature implementation, record a feasibility decision and bounded production contract based on the promised session, target hardware, pipeline, risks, and demonstrated production rate.
- Count a repair only when it fixes one foundation/gate, declares its hypothesis, records the bounded change, captures representative Godot evidence, and receives independent review. After two qualified attempts with the same structural failure, pivot the foundation.
- Validate procedural canonical, random, boundary, and worst-observed seeds.
- Default story-driven 3D casts to readable stylized world faces. Use coherent 2D portraits for expressive dialogue. Conceal faces only when role, faction, or premise justifies it.
- A path, hash, count, manifest, `BLOCKED`, or builder-authored PASS is not acceptance.
