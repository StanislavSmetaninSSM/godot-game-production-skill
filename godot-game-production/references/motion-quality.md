# Motion, feedback and coverage

Use for character motion, contacts, attacks, transitions, reactive surroundings
and time-driven effects. Preserve the approved technique: frame-by-frame sprites,
2D rigs, 3D skeletal animation and physical/procedural motion are all valid.
Do not replace a style with cut-out rigs merely to simplify measurement.

## Declare the coverage before capture

Extend the existing playtest matrix with one row per meaningful claim. Give each
row a stable check ID, actor/object, action and transition, direction/view/support
condition, input/prior state, expected outcome, measurement and units, justified
tolerance, capture/trace identity, and applicability. Cover only the promised
features. Include affected failure/retry paths and the integrated journey under
`gameplay-evidence.md`; focused diagnostic fixtures retain its provenance rules.

Distinguish required rows, reasoned non-applicability, and unverified rows. Missing
data is not non-applicability. Review the planned IDs against actor/action/state
inventories: a tool cannot discover a direction or character omitted from both
the plan and the trace. Preserve that plan's identity with the diagnostic inputs.

## Choose useful measurements

| Claim | Measurement and conditions |
| --- | --- |
| Planted contact | Point drift relative to the actual support during confirmed continuous stance; separate swing and support changes. |
| Pose continuity | Root-relative motion across sampled transitions; inspect frame strips for discontinuity and attachment errors. |
| Attack and effect alignment | Authoritative attack/hit timestamp versus visible contact/feedback; source point versus visible emitter in each relevant pose/facing. |
| HUD | Supported viewport/text-scale extremes and actual longest localized messages, simultaneous overlays and transitions. Inspect clipping, wrapping and overlap. |
| Temporal effects | Time-spaced captures through onset, steady state and fade; check frozen motion, phase jumps, occlusion and disappearance. |

Define tolerances from the approved style, gameplay contract, pixel/world scale,
sampling cadence and noise. Do not import an unexplained one-pixel, percentage,
FPS or human-gait threshold. For intentionally stepped art, preserve holds and
designed pose changes; a continuous-motion acceleration bound may be inapplicable.
Record that reason and use cadence/contact/transition frame review instead.

Capture state, event and animation samples on a shared simulation clock. Record
tick/sample intervals, dropped frames, pause/time-scale behavior and coordinate
space. Do not align an unsynchronized wall-clock recording by guessing. A hit
cannot be inferred from a sword-near-enemy still.

Use `python scripts/motion_check.py` with `quality-tools.md` for four scoped
measurements: contact drift, relative pose acceleration, anchor distance and
event offset. It checks declared coverage and numeric observations. HUD layout,
frozen effects, visual attachment, ground penetration and aesthetic quality still
need project instrumentation or frame/video review; do not claim the helper
automates them. Missing required observations keep the affected claim pending.

## Instrument the authoritative owner

Reuse the project's capture harness and extend the owner of a fact when needed.
Gameplay owns movement/contact/hit decisions; animation and effects consume the
published transition. Export those facts and the rendered points used by the
consumer, linked to the same frame/time. Never make the diagnostic collector a
second state machine or infer an unavailable damage event from a visual effect.

Point/reference vectors must share a declared space and units. For moving or
rotating supports, use a contact anchor transported by the full support transform
or express both points in support-local coordinates. Subtracting the platform
origin alone does not remove rotation. End a stance at support changes; mark a
non-contact boundary between intervals so the checker does not join them.
For pose continuity, use root-local coordinates when root rotation matters.
Project-specific export code must be tested against the locked Godot version;
the helper neither connects to Godot nor authenticates its declared provenance.

## Make reactions share a cause

For each promised action, record its authoritative event and the applicable
immediate/short/settling responses: pose, contact sound, VFX, world response and
camera response. Set their order/timing from the action, preserving accessibility
and camera preferences. Do not add shake, particles or ambient creatures to meet
a universal quota. A shared wind/time/event source can coordinate vegetation,
cloth and sound when those systems belong to the game; consumers retain their
own appropriate response, not competing causes.

Inspect response onset, peak and settling, interrupted actions, pause/resume and
representative adverse views. A user-reported defect gets a reproduction and a
check of the affected class: for a mirrored muzzle error, inspect other relevant
facings and held items. A passing synthetic trace proves the diagnostic algorithm;
only target-build captures can establish the game's behavior. Submit findings
in the measured review format from `visual-quality.md`.
