# Godot 2D / 2.5D Production

Use this reference only after the dimension, camera, approved visual contract, and
core mechanic are known. Record the tested Godot major/minor version, renderer,
target platforms, and import settings before choosing engine-specific nodes or
features. Prefer the APIs and import behavior of the project's locked version;
do not silently upgrade the project to follow newer guidance.

## Build in this order

1. Reproduce the approved composition as a gray-box scene at the intended window,
   aspect ratio, zoom, and camera behavior. Judge readability at the gameplay
   camera distance, not in an enlarged asset viewer.
2. Prove the causal core loop with placeholder visuals. Do not multiply content
   because one target frame looks close.
3. Define one shared grammar for sprites, vector-like shapes, tiles, materials,
   and effects: palette/value bands, outline or edge rules, shape families,
   scale increments, animation cadence, and layer order.
4. Generate or assemble the smallest representative asset set. Keep deterministic
   seed and parameter records for every procedural result.
5. Derive collision and navigation from the same source parameters used for the
   visible tile, prop, or region whenever practical. Inspect debug overlays,
   one-way surfaces, gaps, corners, moving bodies, and tile seams in motion.
6. Add lighting, particles, camera motion, and post effects only after action,
   hazards, interactables, and feedback remain legible at play speed.

For 2.5D, declare which depth, sorting, collision, camera, and lighting rules are
2D and which are 3D. Load the 3D reference only when the implementation actually
uses that pipeline.

## Visual and motion diagnostics

Use `visual-quality.md` for native-pixel comparisons and `motion-quality.md` for
the coverage matrix. Preserve the chosen rendering family: true pixel art, HD
pixel, painted and vector-like art need different filtering, contour and cadence
rules. Capture native pixels before enlargement; verify texel/line density,
sorting, occlusion, tile seams and the smallest supported viewport.

Choose frame-by-frame animation, cut-out rigs or procedural motion to fit the
approved art. Review all relevant facings and transitions, including mirrored
anchors. Separate held drawings from simulation ticks; do not interpolate a
deliberate low drawing rate to satisfy a continuous-motion metric. Measure foot
contact in ground/support space, and source/effect alignment in the same space.
Check pause/resume, worst supported HUD strings and effect onset/settling with
runtime sequences. The offline helpers and their limits are in `quality-tools.md`.

Inspect the whole actor as well as numeric anchors: attached limbs/equipment can
look disconnected while sampled points pass. Exercise mirrored projectile origins,
near/inside-target spawning and fast crossings; confirm the visible warning, hit
region and actual hit/interruption agree. Check support/sorting at relevant overlaps.
Use screen or support-plane units deliberately; a 2D pixel tolerance is not a 3D
world-distance rule. Select actor-specific checks for grounded, flying or rigid art.

## Runtime acceptance

Set project-specific target-hardware budgets for frame time, draw calls, node and
canvas-item count, texture memory, particle count, generation time, and load
stalls. Derive limits from the promised scene and hardware, then capture profiler
evidence on that hardware class; do not import universal thresholds.

Review procedural output as canonical, random, boundary, and worst_observed seed
classes. Record the population, selection method, rejected outputs, generation
errors, and measured viable rate. Verify spawning, save/load, and regeneration
when seeds affect persistent play.

For each milestone keep canonical Godot runtime captures at the approved camera,
plus input/state/outcome filmstrips or video for mechanics. A zoomed source asset
or editor preview is not acceptance evidence. Compare the runtime capture to the
approved target by role, composition, legibility, and buildability; pixel identity
is neither required nor sufficient.

State the next user-visible gate before continuing: exact approval if a visual
decision changed, representative Godot feasibility if the target is approved but
unproven, complete-loop evidence if mechanics are incomplete, or a milestone
review if all dependent evidence exists.
