---
name: godot-game-production
description: Use when creating, continuing, repairing, or broadly developing a Godot 2D, 2.5D, or 3D game across game intent, visual direction, mechanics, production, or release. Do not use for one isolated asset or a narrow one-facet audit.
---

# Godot Game Production

## Required sub-skills

**REQUIRED SUB-SKILL:** Use `brainstorming` before creative definition or behavior changes.

**REQUIRED SUB-SKILL:** Use `spec-kit-superpowers-bridge`; Spec Kit owns durable constitution, spec, plan, tasks, and consistency, while Superpowers owns execution.

**REQUIRED SUB-SKILL:** Use `imagegen` for the initial visual contract and every material visual re-entry. Invoke its built-in image generation path by default.

For implementation use `test-driven-development`; for failures use `systematic-debugging`; before completion use `requesting-code-review` and `verification-before-completion`.

## Start or resume

For an existing project, preserve reality before planning. Do not reset, clean, overwrite, or regenerate user work. Record the initial working-tree status before any write; inspect `project.godot`, engine/import settings, entry scenes, autoloads, input actions, save data, logs, and current specs; then run the existing game before changing it. Actual target-build behavior outranks status prose. Retain an old pass only when its exact artifacts, hashes, review coverage, and requirement still match. Reopen stale, missing, changed, unreviewed, or runtime-contradicted evidence. Resume the first unpassed gate without rebuilding already verified work. If safe inspection is blocked, report the pending audit instead of guessing.

For a new project, establish the bounded experience promise, player, platform, input, dimension, camera, session, mechanics, failure/retry, persistence, target hardware, references, exclusions, and risks. Ask only consequential unresolved decisions, one at a time.

## Mandatory state sequence

`AUDIT -> SPECIFY -> VISUAL_PENDING -> VISUAL_APPROVED -> GODOT_FEASIBILITY ->
CORE_LOOP -> PRODUCTION -> RELEASE`

When the brief and core mechanics are sufficient and no consequential specification decision remains, read `references/visual-contract.md` and `references/evidence-ledger.md` before creating or changing a visual decision.

1. Before emitting any pending `visual-decision/v1`, read `references/visual-contract.md` and `references/evidence-ledger.md` in the current turn. Construct it from the exact complete `visual-decision/v1` schema in `references/visual-contract.md`; abbreviated, invented aliases, and short objects are invalid. Derive a needs-based initial or delta row set; a requested image count is not an input to cardinality. Write exactly one `visual-decision/v1` JSON object with `approval: null` and no invented supplied value.
2. Run `scripts/visual_gate.py check-decision`. A nonzero exit blocks the response. `VALID_PENDING` permits presenting the proposal only; it never permits image generation.
3. For pending `initial_scope` or `delta_scope` decisions, emit exactly one complete validated `visual-decision/v1` object in a `json` fenced code block immediately before the literal scope question. End with `Do you exactly approve the proposed reference slot ID set?` as the final line. Prose summary cannot substitute for that object. Partial approval changes nothing. A premature or scope-invalid request for a pending `initial_scope` or `delta_scope` may be explicitly refused, but the same response must continue this gate with its complete validated fenced decision and canonical scope question, never refusal-only prose; `reference_not_proof` remains a fenced refusal decision without a scope question.
4. After the user's exact full-set approval, write the exact `visual-scope-approval/v1` record and run `authorize-generation` against the unchanged decision and approval bytes.
5. Only when the emitted immutable `visual-generation-authorization/v1` says `AUTHORIZED`, invoke ImageGen. Make at most one call for every authorized slot and no call for any other slot.
6. Save and hash every result, and put the authorization's exact `authorization_id` on its `target_gameplay_image` or `rejected_target_image` artifact row. Raw output without that chain is retained for audit but cannot validate or enter an approved visual contract.
7. Present the complete authorized candidate batch and stop on the canonical target question: `Do you exactly approve the displayed target ID set?` Target approval remains separate and occurs after generation.
8. A later uncovered material question uses a new delta decision and repeats both gates. Treat a missing or changed player-visible state in an approved production, including a phase transformation, camera, environment, character, UI, or VFX treatment, as sufficient to reopen the visual gate. Emit and validate the complete `delta_scope` decision before any implementation-detail question or game change; unresolved presentation details stay as pending placeholders. Never announce or reopen a visual delta in prose only. A missing base contract or target identity uses `<required-value>` or an indexed `<required-value:label>` in the complete pending object; put stated independent work in `continuing_work`. The canonical scope question is the only user question in that response.
9. Local deltas block only dependent work. A global change uses one independently useful visual question per row and one `affected_targets` entry per affected target—never one representative or catch-all row or target for style, camera, UI, or other non-combinable questions. When exact target IDs are unavailable, use distinct placeholder identities such as `<required-value:style-target>` and remain pending. Replacements bind exact supersession.
10. User rejection consumes the old authorization and authorizes no retry. Record the rejected attempt, obtain a distinct `visual-correction-approval/v1`, then use the correction form of `authorize-generation`; the new authorization permits exactly one replacement result for that slot.
11. A `reference_not_proof` decision rejects references as runtime/release proof and preserves all canonical evidence gates. `reference_not_proof` emits its complete fenced decision but does not ask the scope question and cannot reach authorization.

The gate does not prevent the platform from returning raw ImageGen bytes, but no such bytes can receive a verified evidence or release result without the exact approved authorization chain. The decision validator is `scripts/visual_gate.py`; the behavioral acceptance scorer is `tests/behavioral/score_dynamic_visual_reference.py`.

Remain `VISUAL_PENDING` until the initial contract receives exact target approval. If image generation is unavailable, expose the pending gate; prose, code, an unrelated generator, or a source render does not replace it.

Generated targets are design evidence only. After approval, reproduce one representative target in the actual Godot project. Read `references/gameplay-evidence.md` and prove a complete causal core loop before content multiplication.

When broad enemy, level, UI, asset, or content production is requested before exact target approval, explicitly state this order: `complete target gameplay pack with per-frame buildability accounts -> exact user approval -> one representative target reproduced in the actual Godot project -> asset and content multiplication`.

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
