# Generated frames for 2D animation

Use when approved production needs frame-based 2D animation. This example authors
one right-facing, in-place walk for an already-approved character. Adapt the poses,
cadence, size and facings to that game; six frames and the numbers below are example
choices, not quality quotas. Keep the mechanic promise/transition dependency in
`mechanic-playtests.md` and actual-build checks in `motion-quality.md`.

## Choose from real capabilities

Inspect the current host's tools and adapters before choosing the source:

| Available capability | Production source |
| --- | --- |
| A working, authorized text/image-to-video generator that creates new motion | Generate a short clip on a flat purple background; extract its real decoded frames. |
| No genuine video generator, but the selected native image provider works | Generate each planned animation frame individually with pose/reference anchoring. |
| Neither is available | Record the missing capability and keep this asset pending; continue independent work. Use another already-authorized suitable method only if the task permits it; a proxy rig/static pose cannot complete a required generated-frame deliverable. |

Video editing, resizing, timeline rendering, slideshow/export and highlight-cut tools
do not establish video generation. Do not invent an endpoint, service, API key or
paid dependency. Use the host's actual native video capability and its contract
when one exists; the image-provider registry does not magically supply video.
For the image branch, read `image-generation.md`, resolve the selected provider and
use its native adapter. Do not substitute a convenient different image provider.

These are `production_asset` sources within approved direction, task and budget,
not extra reference slots or a new route around exact-set approval. New identity,
costume/style or a materially uncovered visual state returns to the existing visual
gate. Technical frame extraction/keying does not require a new visual decision when
already authorized. Failed/unknown generation or an incomplete frame set remains
pending under the provider's failure/retry rules; do not conceal it with copied
poses, automatic switching or additional unaccounted requests.

## Lock the drawing and timing contract

Inspect the approved character image, intended Godot view and existing movement.
Record the source image, camera/facing, silhouette/limb and costume landmarks,
palette, scale, canvas, root/pivot, floor and necessary margins in the current asset
task. Fix them across the sequence. Keep the full body, weapon/cloak and extremities
inside the canvas in every pose. Crop a common union rectangle only if needed;
independent tight crops/recentering make a stationary root appear to jump.

Distinguish the **provider-native source canvas** from the **registered Godot output
cell**. Preflight source dimensions against the selected adapter before requesting
a frame. For this example, author on a provider-valid 1024×1024 source canvas with
root (512,896) and floor y=896; derive 512×512 output cells with root (256,448) and
floor y=448 using one shared 0.5 scale transform. For a provider with a 655,360-pixel
minimum, 512²=262,144 fails while 1024²=1,048,576 meets that floor; also check its
edge/aspect/format constraints. Another provider may require different native dimensions: choose a supported
canvas and explicitly map its root/floor to the same output contract. Do not submit
the output-cell dimensions as a native request without that preflight.

Keep ample head/foot/cloak margins and unchanged approved fastener/trim. At normal
playback the example's output-cell sequence has this 0.60-second cycle:

| Output | Start / hold | Pose to author or select |
| --- | --- | --- |
| walk_00.png | 0.00 / 0.08 s | Left forward contact, right trailing; clear foot silhouettes. |
| walk_01.png | 0.08 / 0.12 s | Left down/support, right leg beginning its forward swing. |
| walk_02.png | 0.20 / 0.10 s | Left support passes under/behind root, right passing/rising. |
| walk_03.png | 0.30 / 0.08 s | Right forward contact, left trailing; opposite arm swing. |
| walk_04.png | 0.38 / 0.12 s | Right down/support, left leg beginning forward swing. |
| walk_05.png | 0.50 / 0.10 s | Right support passes behind root, left passing/rising into 00. |

The root is fixed in the source; a stance foot sweeps backward relative to it.
During translated gameplay, that sweep should counter the character's forward
travel while contact lasts. A stationary foot in root-local art moves with the
body in the world and slides. Tune stride length and cadence against the existing
controller's intended speed, not by silently changing approved movement to fit art.

## Branch A — video on purple, then actual frames

Use the real native video generator with authorized character references. An
adaptable prompt is:

> Production animation source of this exact approved character: one complete
> right-facing in-place walk cycle, unchanged face/costume/cloak/prop identity,
> fixed orthographic side camera, stationary root and consistent full-body scale,
> all extremities inside a fixed canvas, clear contact/down/passing poses and
> natural follow-through. Uniform flat purple background (#8000FF), no scenery,
> gradients, ground shadow, camera motion, zoom, text, cuts or identity morphing.
> Return actual animated motion, with a clean cycle boundary.

Use only settings that the actual generator supports; requested duration/rate is
not proof of returned cadence or loop quality. Preserve the returned clip unchanged
under a chosen project-local raw path, with actual provider/job, prompt, authorized
reference identities and hash. Inspect the motion before extracting: if it morphs,
crops feet or never contains the needed transition, extraction cannot repair it.

If local FFmpeg/FFprobe is available, create new empty derived directories and use
the following commands from this example asset directory. These tools are optional
technical dependencies, not new generation providers; if absent, use an available
frame-export tool that preserves frame order/timing, or report extraction pending.

```sh
ffprobe -v error -select_streams v:0 -show_streams -show_frames -of json raw/walk-purple.mp4 > derived/source-timing.json
ffmpeg -n -i raw/walk-purple.mp4 -map 0:v:0 -fps_mode passthrough derived/decoded/frame_%06d.png
```

Retain every decoded source frame and map its zero-based decoded order to FFprobe's
frame/timestamp list; PNG numbering above starts at 000001. Verify the count and
timestamps rather than inferring duration from a filename or average FPS. For
variable-rate footage, keep per-frame timing. Do not add `-r`/FPS conversion to this
source extraction: it may insert/drop frames. Select a coherent complete cycle,
record selected source indices/timestamps and intentional holds, then make distinct
working copies named walk_00…05 for this example. A duplicate closing pose can be
removed from the selected loop without deleting it from raw extraction. If six
poses cannot represent the approved motion, adapt the frame count within authority;
do not disguise an inadequate sequence with interpolation or duplicated images.

For a separable opaque foreground, test RGB color keying on a single copied frame:

```sh
ffmpeg -n -i derived/decoded/frame_000001.png -vf "format=rgba,colorkey=0x8000FF:0.08:0.04" -frames:v 1 derived/key-test.png
```

Sample the actual background color; the example similarity/blend are starting
values, not universal settings. Inspect alpha and RGB on black, white and a
representative game background before applying settings to the selected sequence.
Check thin limbs, hair/cloak edges, holes between limbs, purple spill and halos.
Do not erode the silhouette or recolor approved fabric merely to remove fringes.
If foreground includes purple trim or translucent cloth, blanket keying destroys
subject pixels: protect those regions with tracked masks/rotoscoping and suitable
matting, preserving fractional alpha and edge color. A flattened clip may not
contain enough information to recover the original transparency; record that
limitation and repair using an authorized suitable source/method. Do not claim a
matte succeeded from a purple-background preview. Keep key tests, masks and final
RGBA separately; preserve the original clip and decoded frames.

## Branch B — individually generated image frames

When video generation is unavailable, author each table row with the selected
native image provider. Supply the approved identity image for every call and, where
supported, a checked neighboring pose as an additional continuity reference. Use
the host adapter's real reference-image mechanism, not just a textual filename.
Generate one usable full-body frame for the chosen row, not another concept sheet
or an unregistered sprite grid. Request transparency when supported, and keep the
same preflighted source canvas/root/floor and rendering treatment throughout;
the smaller Godot output cell is a technical derivative, not this native request.

For example, the prompt for 02 preserves the locked contract above and requests:

> Frame 02, right-facing walk passing pose at 0.20 seconds: left stance foot under
> or just behind the root, right knee swinging forward, opposite arm swing; retain
> exact character/cloak construction from the identity reference and continuity
> with checked frame 01. Fixed full-body camera, preflighted 1024×1024 source
> canvas, root (512,896), floor y=896, no camera shift, per-pose rescaling or
> cropped extremities. Transparent
> background. This is a distinct animation drawing, not a duplicate of frame 01.

Numeric prompt anchors are requests, not guarantees: inspect and register actual
results. Review a contact sheet and timed preview as frames arrive. Correct actual
pose/anatomy, scale, identity and cloak continuity defects within approved authority
and the provider's retry rules. Keep returned originals and separately registered
RGBA files with the actual prompt/reference/provider lineage for each. Duplicating
a static pose or tweening/crossfading it is not individually generated animation.
Intentional holds remain valid timing choices and are recorded as holds.

## Converge in Godot and judge the actual result

Inspect actual returned dimensions and root/floor placement before registration;
prompt numbers are not evidence of correct output. Preserve raw files unchanged.
For the 1024² example, apply the same recorded 0.5 scale, crop/padding and filtering
choice to every selected RGBA frame to produce 512² cells; root/floor map to
(256,448)/y=448. If a different source canvas is required, record its shared mapping.
Do not independently fit, stretch or recenter each pose to hide size/placement
drift. Correct inconsistent sources within authority or keep the asset pending.
Retain source/derived identities and transform with the existing asset notes.

Put the selected, equal-canvas RGBA output cells in the consuming project's art directory.
Preserve a short ordered frame/hold/source table in existing asset notes; no new
mandatory JSON schema is needed. In Godot 4's SpriteFrames editor, create `walk`,
add files in numeric order 00…05 and enable looping. At base speed 10 FPS and
playback speed 1, set relative frame durations to 0.8,1.2,1.0,0.8,1.2,1.0 to obtain
the table's holds. Godot duration is a relative multiplier: seconds = duration /
(animation FPS × absolute playing speed), not a seconds-valued duration field.
Verify the installed Godot version and actual playback after import.

Use AnimatedSprite2D with the declared shared pivot. For unscaled 512×512 cells and
a parent origin at ground/root, one explicit mapping is `centered=false` and sprite
position (-256,-448); apply the game's chosen art/world scale consistently. An
existing rig/root setup can supply the equivalent mapping. Keep filtering/padding
appropriate to the approved art; mirrored facings still require prop/contact review.
If AnimationPlayer drives sprite frame changes, key discrete indices/textures at
the table's start times, set loop length 0.60s and avoid interpolating pose indices.
Choose one playback owner: do not let AnimatedSprite2D autoplay and AnimationPlayer
compete for the same frames. Gameplay's authoritative movement/hit/contact owner
publishes state; animation consumes it, including idle, interruption and retry.

Capture the actual consuming Godot build at intended size and speed: the entire
cycle, 05→00 seam, start/stop, relevant facings and action transitions. Check identity,
silhouette, root/camera jitter, loop cadence, foot/support-space drift, contact and
cloak/prop continuity, alpha holes/spill and transparent foreground on actual scene
backgrounds. Compare its appearance with the approved reference using
`visual-quality.md`, and bind inputs/state/outcomes through the existing ledger and
independent review. A source preview, clean matte or correct resource duration does
not prove the promised movement, visual fidelity, human feel or release quality.

Technical references: [FFmpeg frame-rate modes](https://ffmpeg.org/ffmpeg.html),
[FFprobe frame metadata](https://ffmpeg.org/ffprobe.html),
[FFmpeg RGB keying](https://ffmpeg.org/ffmpeg-filters.html#colorkey), and
[Godot SpriteFrames durations](https://docs.godotengine.org/en/stable/classes/class_spriteframes.html).
