---
name: godot-game-production
description: Use when creating, continuing, repairing, or broadly developing a Godot 2D, 2.5D, or 3D game across game intent, visual direction, mechanics, production, or release. Do not use for one isolated asset or a narrow one-facet audit.
---

# Godot Game Production

## Required sub-skills

**REQUIRED SUB-SKILL:** Use `brainstorming` before creative definition or behavior
changes.

**REQUIRED SUB-SKILL:** Use `spec-kit-superpowers-bridge`; Spec Kit owns durable
constitution, spec, plan, tasks, and consistency, while Superpowers owns execution.

**REQUIRED SUB-SKILL:** Use `imagegen` for the initial visual contract and every
material visual re-entry. Invoke its built-in image generation path by default.

For implementation use `test-driven-development`; for failures use
`systematic-debugging`; before completion use `requesting-code-review` and
`verification-before-completion`.

## Start or resume

For an existing project, preserve reality before planning. Do not reset, clean,
overwrite, or regenerate user work. Record the initial working-tree status before
any write; inspect `project.godot`, engine/import settings, entry scenes, autoloads,
input actions, save data, logs, and current specs; then run the existing game before
changing it. Actual target-build behavior outranks status prose. Retain an old pass
only when its exact artifacts, hashes, review coverage, and requirement still match.
Reopen stale, missing, changed, unreviewed, or runtime-contradicted evidence. Resume
the first unpassed gate without rebuilding already verified work. If safe inspection
is blocked, report the pending audit instead of guessing.

For a new project, establish the bounded experience promise, player, platform,
input, dimension, camera, session, mechanics, failure/retry, persistence, target
hardware, references, exclusions, and risks. Ask only consequential unresolved
decisions, one at a time.

## Mandatory state sequence

`AUDIT -> SPECIFY -> VISUAL_PENDING -> VISUAL_APPROVED -> GODOT_FEASIBILITY ->
CORE_LOOP -> PRODUCTION -> RELEASE`

When the brief and core mechanics are sufficient and no consequential decision
remains, the next production action is Codex `imagegen`: generate and show the
target-gameplay screenshot pack, then request the user's exact approval of those
files. Announce this gate and execute the following protocol in the same turn;
do not ask whether screenshots should be created and do not wait for the user to
request images.

Freeze the required coverage matrix before ImageGen. The pack is complete only
when every required coverage row maps to at least one displayed target and every
displayed target has a complete buildability account. Do not ask for approval
until the complete required target pack is ready. A missing required state, asset
family, buildability account, motion cue, or sound cue leaves `VISUAL_PENDING`.

1. Make one ImageGen call per requested target or variant. In code mode, make the
   initial call with the first line
   `// @exec: {"yield_time_ms": 120000}`. If it yields a cell, continue `wait` on
   that exact cell with the same 120-second yield until completion.
2. The same code cell must call exactly `generatedImage(result)` for each result.
   Never use `text`, JSON serialization, `image(...)`, or another substitute to
   present the result; those substitutes are not presentation. Do not make a
   corrective or replacement ImageGen call
   merely to repair presentation. Showing requires the actual bitmap as an actual
   `input_image` in the Codex image result channel.
3. Every completed generation in the gate must be displayed and covered by
   exactly one target row. Copy every selected result into the versioned project
   directory before approval, compute SHA-256 from the final project-local PNG,
   confirm it matches the displayed bitmap bytes, and list its final
   project-relative path. Assign stable, unique IDs in generation order.
   Immediately before the approval question, list one strict row per completed
   result and no other target rows, for example:
   `TARGET-PACK-01 | SHA-256: <64 lowercase hex> | PATH: docs/visual-contract/vc-001/targets/<file>.png`.
4. End the response with this literal final line:
   `Do you exactly approve the displayed target ID set?`

Then stop in `VISUAL_PENDING`. Do not start dependent Godot code or asset
production first. A missing tool result, actual `input_image`, saved file, matching
hash, unique ID, complete row set, or literal final question leaves the gate
pending. If any completed generation lacks its exact `input_image` or target row,
stay `VISUAL_PENDING`, do not ask for approval, and do not retry it yourself.
Approval binds the complete target ID/SHA-256/project-relative PATH set; a
temporary ImageGen output path is not approvable. A missing or moved file, changed
path, or changed bytes reopens approval.

Read `references/visual-contract.md` and remain `VISUAL_PENDING` until exact
approval. If ImageGen is unavailable, expose the pending gate; prose, code, an
unrelated generator, or a source render does not replace it.

If a later scene, camera, light, character presentation, effect, or UI state
requires consequential visual invention outside the approved contract, stop that
slice and repeat `imagegen -> generate -> show -> iterate -> exact approval`, using
the same executable protocol including hash-bound stable ID rows, before dependent
implementation resumes.

Generated targets are design evidence only. After approval, reproduce one
representative target in the actual Godot project. Read
`references/gameplay-evidence.md` and prove a complete causal core loop before
content multiplication.

When broad enemy, level, UI, asset, or content production is requested before
exact target approval, explicitly state this order: `complete target gameplay pack
with per-frame buildability accounts -> exact user approval -> one representative
target reproduced in the actual Godot project -> asset and content multiplication`.
Do not abbreviate this to an approval-only refusal.

## Route only what is needed

- Read `references/production-operations.md` when the current production interval
  has two or more implementation slices scheduled to overlap or be delegated
  concurrently, or when multiple agents or worktrees will implement related parts
  of the same candidate. Do not read it merely for several serial steps in one
  bounded slice.
- Read `references/gameplay-evidence.md` when planning or judging playtest matrices,
  fixtures, seeded coverage, or integrated player-journey evidence. This routing
  complements the existing post-approval core-loop use of that reference.
- Read `references/procedural-art.md` for generated visual systems or repeated assets.
- For 2D or 2.5D, read `references/godot-2d.md` and do not read the 3D reference.
- For 3D, read `references/godot-3d.md` and do not read the 2D reference.
- Load both only for an explicitly hybrid pipeline. State the next user-visible
  approval or evidence gate after routing.
- Read `references/evidence-ledger.md` when creating or validating milestone evidence.
- Read `references/release-checks.md` for milestone or release decisions.

## Stop rules

- Give every mutable state, decision, event, timer, and persisted save fact
  exactly one authoritative owner. Consumers read or subscribe to that owner;
  they must not infer, shadow, or independently write a competing version.
  When an owner knows a fact but does not publish it, the implementation slice
  must extend the owner's transition before a consumer uses that fact. A neutral
  consumer fallback or post-release owner change does not complete requested
  fact-specific behavior; if the owner change is forbidden, stop and escalate the
  conflict instead of moving or deferring the authority boundary.
- A screenshot never proves mechanics; require input, state, outcome, and
  filmstrip/video evidence from the target Godot build.
- Core play, systems/holism, content, visual, audio/feedback, UX/onboarding,
  reliability/performance, and ship each fail closed; never average them.
- Translate commercial references into bounded experience and quality attributes,
  never their inventory. Before feature implementation, record a feasibility
  decision and bounded production contract based on the promised session, target
  hardware, pipeline, risks, and demonstrated production rate.
- Count a repair only when it fixes one foundation/gate, declares its hypothesis,
  records the bounded change, captures representative Godot evidence, and receives
  independent review. After two qualified attempts with the same structural failure,
  pivot the foundation.
- Validate procedural canonical, random, boundary, and worst-observed seeds.
- Default story-driven 3D casts to readable stylized world faces. Use coherent 2D
  portraits for expressive dialogue. Conceal faces only when role, faction, or
  premise justifies it.
- A path, hash, count, manifest, `BLOCKED`, or builder-authored PASS is not acceptance.
