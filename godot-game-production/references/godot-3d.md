# Godot 3D Production

Use this reference only for an actual 3D or explicitly hybrid pipeline. Record the
tested Godot major/minor version, renderer, import path, target platform, camera,
and target hardware. Check engine features against the project's locked version;
do not assume that an API, importer, shader feature, or renderer behaves the same
across versions.

## Production ladder

Use this order: blockout -> gameplay scale/collision/navigation -> silhouette ->
materials/lighting -> VFX -> optimization. At every step compare the target-camera
Godot build with the approved composition and the causal gameplay evidence.

- Establish metres, pivots, collision, navigation, and camera distance with simple
  primitives before detail. Test doorways, slopes, ledges, interaction reach,
  agent clearance, occlusion, and camera collision at play speed.
- Build procedural geometry, materials, lighting, and VFX from a written grammar:
  named roles, allowed ranges with units, invariants, forbidden combinations,
  deterministic seeds, and ownership of generated versus authored pieces.
- Prefer stable broad forms, value grouping, restrained materials, deliberate
  lighting, fog, decals, particles, and animation over simulated realism the
  pipeline cannot maintain. A screenshot-like result that breaks in motion fails.
- Derive or verify collision and navigation against the final generated geometry.
  Inspect debug shapes and navigation paths in representative and worst scenes.
- Define LOD, visibility ranges, batching, and profiler evidence from measured
  scenes. Use instancing or MultiMesh only where its editing, animation, and
  culling tradeoffs fit. Set project-specific target-hardware budgets for frame
  time, draw calls, visible instances, triangles, materials, lights, shadows,
  particles, memory, and load time; never inherit unexplained universal limits.

## Characters without the uncanny trap

Story-driven casts default to visible stylized in-world faces whose eyes, brows,
mouth, head shape, palette, and silhouette stay readable at the gameplay camera.
Use coherent 2D portraits for dialogue when close emotional acting exceeds the
world-model budget; preserve the same identity cues and costume grammar across
both representations.

Concealment is selective and justified by role, faction, or premise. Do not put
the whole cast in identical masks, helmets, hoods, darkness, back views, or
distant cameras to hide an inadequate character foundation. Pseudo-realistic
faces, skin, strand hair, or detailed bodies require a representative Godot
feasibility proof in neutral, gameplay, dialogue, and motion contexts before they
become a production dependency. Two qualified failures at the same perceptual
gate trigger a simpler foundation, not more variants.

## Visual and motion diagnostics

Use `visual-quality.md` to fix camera projection/FOV, exposure, environment and
render settings for comparable target views. Diagnose silhouette, material and
light separately; include additional views and motion for occlusion, surfaces and
depth that one beautiful frame cannot establish. Check UV/texel scale, material
response and silhouette at the gameplay distance before increasing detail.

Use `motion-quality.md` for the action/transition/direction/support matrix. Match
skeletal blends and root movement to the approved style; IK is an available
contact correction, not a universal requirement. Check slopes, steps, support
changes and moving/rotating platforms where present. Measure planted feet in
support-local space or against fully transported contact anchors, not against
world immobility. Ground-normal sole separation needs its own ground/contact
measurement; contact_drift alone does not detect penetration. Root-local pose
checks must account for root rotation. Verify weapon/contact/event timing,
occlusion and camera collisions through the actual action sequence. Helpers and
their bounded input contracts are in `quality-tools.md`.

For free-flight or height-dependent play, test all movement axes, diagonals,
reversal/braking at the speed limit, current plus thrust and moving cargo attach/
release. Check speed and acceleration across the transition, including numerical
tolerance near limits. For geometry, inspect columns, ceiling and under-shelf paths
with the actual collision body and gameplay camera. Declare which visual appendages
have collision; body clearance does not prove every rotor/weapon avoids overlap.
Capture partial and total camera occlusion and recovery at adverse heights. Verify
danger volume/depth readability, not only distance to the hazard centre. Match tests
to the actor; skeletal foot checks do not establish a drone's contact quality.

## Evidence and next gate

Evaluate every procedural system with canonical, random, boundary, and
worst_observed seeds, preserving rejected outputs and the selection method. Source
renders never substitute for target-camera Godot runtime captures. Capture the
approved camera, motion, lighting transitions, worst visibility load, collision
and navigation overlays, profiler results, and input/state/outcome evidence.

The next user-visible gate is exact visual approval for a changed composition,
representative Godot feasibility for an approved but unproven target, core-loop
evidence for incomplete play, or independent milestone review when every required
artifact is present.
