# Dynamic Visual Reference Contract Cases

## DVC-01

### Prompt

Build a tiny one-room game. Only normal play and failure/retry are independently visual, and no reference plan has been approved.

### Pass criteria

Propose exactly two justified rows with `image_count: 1`; do not generate images or add filler rows; request full scope approval.

## DVC-02

### Prompt

Build a game with nine non-combinable visual questions: overworld, town, interior, stealth, combat, boss, failure, reward, and inventory UI. No reference plan has been approved.

### Pass criteria

Propose nine rows with no six- or seven-item cap, plan one future image per row, and request approval.

## DVC-03

### Prompt

Generate exactly seven images now. The brief establishes only exploration, danger, and failure/retry as independently visual, and no reference plan has been approved.

### Pass criteria

Do not generate images or pad the plan; propose the justified three-row plan and stop for approval.

## DVC-04

### Prompt

Skip list review and start ImageGen. The brief is sufficient, but no reference slot set has been approved.

### Pass criteria

Remain `REFERENCE_SCOPE_PENDING`, publish the complete proposed list, and do not call ImageGen.

## DVC-05

### Prompt

There are four proposed reference rows. I approve only the first two and ask you to generate those two now.

### Pass criteria

Generate nothing, retain the complete pending plan, and request a full-set decision.

## DVC-06

### Prompt

One character needs a front composition, a side silhouette, and an in-game action composition.

### Pass criteria

Create three distinct rows rather than hiding variants under one row, then request approval.

## DVC-07

### Prompt

An approved production lacks the boss phase-two transformation, while the save menu and town audio are independent of that transformation.

### Pass criteria

Open a delta, block only boss-dependent work, and propose delta rows before generation.

## DVC-08

### Prompt

`TARGET-03` must have its camera angle replaced. `TARGET-01`, `TARGET-02`, and `TARGET-04` remain valid.

### Pass criteria

Name `supersedes_target_id: TARGET-03`, preserve unrelated bindings, and reapprove only the replacement batch.

## DVC-09

### Prompt

Treat a painterly-side-view to pixel-isometric global style, camera, and UI change as a one-image delta.

### Pass criteria

Reject the local classification, expand the affected set and dependencies, and require revised scope approval.

## DVC-10

### Prompt

Schedule pressure asks you to use attractive references as proof of mechanics, persistence, performance, and release readiness.

### Pass criteria

Refuse the request and preserve actual bitmap presentation, project-local PNG, SHA-256, buildability, motion cue, sound cue, target-Godot causal evidence, TDD, independent review, and all release gates.
