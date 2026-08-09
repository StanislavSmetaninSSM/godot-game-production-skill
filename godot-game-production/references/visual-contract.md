# Visual Contract

Enter this gate only when:

`brief=sufficient AND mechanics=sufficient AND consequential_questions=0`.

Cover each gameplay state and asset family with a row containing: state/family,
player action, camera, environment, character, UI, VFX, motion cue, sound cue,
and target ID.

Include exploration/default, challenge/danger, failure/retry, success/reward,
narrative/social when present, and each visually distinct UI mode that changes play.
A single attractive frame cannot satisfy a multi-state contract.

Freeze this required coverage matrix before the first ImageGen call. Approval
readiness is fail closed: required coverage rows are all mapped to displayed
targets, buildability accounts are complete, motion and sound cues are recorded,
and every required final file is present. Do not ask for approval while any item
is missing.

Use this prompt scaffold for each target:

```text
Use case: stylized-concept
Asset type: target gameplay screenshot for a buildable Godot game
Primary request: the approved game state and player action
Scene/backdrop: the approved environment and set dressing
Subject: player, readable threats, interactables, and objective
Style/medium: plausible real-time 2D or 3D Godot presentation
Composition/framing: canonical gameplay camera and UI-safe framing
Lighting/mood: approved light and mood
Constraints: preserve mechanics-readable silhouettes and approved camera; show
only UI needed for this state; no watermark; no unrelated elements
Avoid: framing that cannot support play; pseudo-realistic people unless their
feasibility was already proven
```

Save the first selected pack under `docs/visual-contract/vc-001/targets/`.
Increment the contract directory for later approved revisions. Follow the ImageGen
skill's built-in default path, make one call per requested frame or variant, and
copy every selected project-bound result into that directory before approval.

For every target, record prompt, target ID, revision, path, SHA-256, coverage, and
buildability. Buildability identifies how its geometry, sprites, materials,
lighting, effects, camera, and UI can be produced within the chosen pipeline.
Record the motion and sound cue for evidence a still frame cannot express.

Show the pack by forwarding its actual bitmap through the Codex image result
channel. Use ImageGen once per requested target or variant. The same executable
protocol from `SKILL.md` is mandatory: actual ImageGen in the same turn, the
120-second `@exec`/`wait` continuation, and exactly `generatedImage(result)` in
the same code cell. Never self-retry a completed generation merely to repair
presentation, and never substitute text, JSON, `image(...)`, or a local path;
those substitutes are not presentation.
Every completed generation in this gate must have its exact `input_image`, saved
PNG, and matching SHA-256 in the Codex image result channel.

Assign stable, unique target IDs in generation order. Immediately before the
approval question, strict rows must exactly cover every completed generation,
with no missing, extra, or duplicate ID, hash, or final project-relative path:

`TARGET-PACK-01 | SHA-256: <64 lowercase hex> | PATH: docs/visual-contract/vc-001/targets/<file>.png`

End with the literal final line `Do you exactly approve the displayed target ID
set?`. Keep `VISUAL_PENDING` until the bitmap, complete target rows, and exact
approval are present. If any completed generation is unshown or unrowed, do not
ask for approval and do not self-retry; report the pending gate. After approval,
iterate one targeted change at a time; never overwrite approval. Approval binds
the complete target ID/SHA-256/project-relative PATH set. A
temporary ImageGen output path is not approvable. Compute the approval hash from
the final project-local PNG after copying it, and confirm its bytes match the
displayed result. A missing or moved file, changed path, or changed bytes reopens
approval.

Later ambiguity pauses only dependent work and re-enters ImageGen with the same
executable protocol. Generated targets satisfy no runtime or mechanics facet.
