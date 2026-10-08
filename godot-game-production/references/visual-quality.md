# Visual analysis and comparable Godot captures

Use after the relevant target is approved, when reproducing it in Godot or
diagnosing a material visual gap. This adds measurements to the existing visual
contract; it does not authorize a new direction or change the approval chain.

## Build a measured passport

Inspect the actual approved images and record a short table in the existing
production task or asset notes. Separate observed values from chosen budgets.

| Axis | Record at the intended gameplay view |
| --- | --- |
| Composition | Camera/projection, framing, focal subject, subject height as a fraction of the viewport, important region bounds. |
| Values and colour | Foreground/play/background value relationships, material/role palette, shadow/light colour, contrast at the smallest supported viewport. |
| Shape and detail | Silhouette cues, proportions, edge/outline treatment, focal detail and quiet areas. |
| Rendering | Pixel grid or line/brush scale for 2D; material response, lighting and depth cues for 3D; deliberate mixtures recorded explicitly. |
| Motion and feedback | Drawing cadence or pose timing, important contacts, event/feedback relationships and effects whose appearance changes over time. |

Use the approved target as the source. Exact visual copying is required only when
the user's contract says so. A generated target may not have recoverable engine
settings: record that uncertainty and the production mapping instead of inventing
an exact FOV, light power or material value from a picture.

## Capture before measuring

Identify the candidate revision/build, target image and hashes, Godot version,
renderer, viewport/aspect ratio, import/filtering, camera transform/projection,
lighting/environment/exposure, render/post settings, state, time and seed. Store
these beside the capture using existing evidence records. Compare the same
subject and state at the same scale. Keep the original files.

- For 2D, capture native pixels and use nearest-neighbour enlargement for viewing
  pixel art. A blurred enlarged capture cannot establish native-pixel defects.
- For 3D, match camera and lighting conditions before attributing a difference to
  geometry, material or colour. Use extra representative views and motion to
  check forms hidden in the comparison view. Preserve any intentional differences.
- For both, normalize colour space to sRGB explicitly. Composite transparent
  references against a declared background. Any registration, crop or conversion
  produces a derived diagnostic image with the original identity and transform
  retained; it must not silently improve the result or replace runtime evidence.

When settings or states are unmatched, label the pair non-comparable for that
claim and obtain a useful capture. Do not tune several confounded variables at
once to chase a score.

## Compare and diagnose

Use `python scripts/frame_compare.py` as documented in `quality-tools.md` for
same-sized opaque images. Select important regions explicitly when a uniform
grid would mix unrelated objects. Inspect the side-by-side at gameplay scale and
the magnified suspect regions. The report provides RGB error, linear-luminance
change, coarse palette overlap and edge-density change; its ranked regions tell
you where to look, not which frame is artistically better.

Metrics cannot prove silhouette identity, readability, good composition, correct
materials, motion or gameplay. A small error can hide a critical missing cue; a
large error can be intentional animation. Use motion evidence from
`motion-quality.md` for temporal claims. Test seams, occlusion and readability
under the actual consuming camera rather than accepting an isolated asset crop.

## Review and bounded correction

Give the independent reviewer exact captures and comparison conditions before
builder rationale. Use one review for a coherent completed block; additional
specialists are useful only for a concrete unresolved risk.

Record each actionable finding as:

`criterion | capture/frame/region | observed vs expected (units) | player impact |
owner/asset | concrete correction | repeatable verification | priority`

Fix the largest player-visible gaps first, rerender the same controlled case,
then check an affected alternate state/view. Keep adverse results. A changed
approved direction follows the existing visual delta procedure; an implementation
repair within it remains ordinary authorized production work. Attach diagnostics
to the existing target-build evidence; they never grant visual or release PASS.

Method inspiration: ref2game's measured reference study and region comparison,
commit `61d8f9e5457b9b3a379fa016621efcf1904ce249`:
https://github.com/studioigor/ref2game/blob/61d8f9e5457b9b3a379fa016621efcf1904ce249/codex/references/study.md
The bundled implementation is independent and does not require ref2game.
