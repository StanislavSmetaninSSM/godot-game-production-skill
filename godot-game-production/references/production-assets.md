# Production assets from approved direction

Use this workflow after the relevant visual targets are approved, including the
representative Godot feasibility slice. Keep the approved references available
while authoring; they constrain appearance, not the choice of authoring tool.

## Choose and make

For each asset or coherent family, inspect the project's existing art and compare
available library assets, procedural/native authoring, and ImageGen against the
approved style, required detail, editability, runtime budget, and production cost.
Reuse suitable assets with usable licensing; keep procedural materials where
parameter control helps. Use `imagegen` for bitmap detail it can supply well:
fabric or surface color textures, sprites, tiles, decals, portraits, and painted
elements. Combining generated color detail with procedural material parameters
is a valid choice. A new purchase or a separately billed tool still follows the
user's existing permissions; using the available built-in ImageGen needs no new
per-asset permission.

When ImageGen is selected, read its skill and use the built-in path by default.
Inspect the actual approved images and include relevant images as generation
references where supported. State the asset's intended use, preserved identity,
palette, pattern scale, dimensions/aspect ratio, transparency, and tiling or UV
constraints as applicable. Generate a usable source image, not another concept
sheet. Save selected outputs inside the project, connect the consuming resource,
and iterate on specific observed defects within the task and budget. If repeated
attempts stop improving the result, change the authoring method or report the
concrete limitation rather than generating indefinitely.

For example, after approval of a dark cloth costume with worn gold embroidery,
choose an existing cloth material if it fits. Otherwise generate the cloth color
texture and embroidery decal from those references, combine them with appropriate
roughness and other material settings, and test them on the costume. No separate
scope approval is needed for those working images. Replacing the cloth costume
with metal armor changes the approved direction and reopens reference approval.

## Verify the consuming asset

- For surface textures, inspect repetition and seams, pattern scale, UV placement,
  stretching, and texel density on the actual mesh. Request neutral illumination
  for color maps; remove unintended baked shadows or highlights. Do not assume a
  generated RGB picture supplies valid normal, roughness, metallic, or height
  data: author or derive appropriate maps and verify channel conventions and
  import/color-space settings in the project's Godot version.
- For sprites, tiles, decals, and portraits, verify alpha edges, padding, tile
  seams where relevant, consistent identity and scale, and filtering at the
  intended camera distance. Check animation/frame consistency when applicable.
- Inspect the result in Godot under representative camera, lighting, motion, and
  target-hardware constraints. Fix visible integration defects autonomously;
  source-image attractiveness alone is not acceptance.

## Record source work and evidence

Use the existing project asset inventory or production task notes to record the
saved asset path, source/license or generation prompt and input references,
approved visual target linkage, consuming scene/material, and integration checks.
Keep machine details in project files and give the user a concise localized
progress description. Follow `imagegen`'s delivery requirements when generating.
Seed reproducibility rules in `procedural-art.md` apply to procedural generators;
do not invent a deterministic seed or reproducibility guarantee for ImageGen.

These are source assets, not `target_gameplay_image` or `rejected_target_image`
records. Do not fabricate reference authorizations or inflate reference plans to
register them. The evidence ledger records the actual Godot captures and other
required evidence of the integrated build. A working texture cannot replace an
approved reference, runtime capture, independent review, or gameplay/release
proof. If the asset requires a visual decision outside the approved direction,
return to the reference approval procedure before implementing that change.
