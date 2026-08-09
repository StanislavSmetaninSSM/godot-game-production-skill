# Procedural Art

Use procedural generation to multiply an approved, buildable style—not to search
indefinitely for a style. Define the grammar and its evidence population before
content fill.

## Freeze a bounded visual grammar

Create one versioned grammar artifact per procedural system. Record:

- the foundation ID and generator version;
- the invariants shared by every output: shape language, contour treatment,
  value grouping, palette relationships, material response, detail density,
  camera assumptions, and animation constraints;
- every parameter's type, inclusive minimum and maximum, unit, quantization or
  step, distribution, and default;
- allowed dependencies between parameters and an explicit list of prohibited
  combinations;
- named gameplay roles and the silhouette/readability rule for each role;
- the deterministic seed contract and the Godot version, renderer, target
  hardware, viewport, camera, and lighting used for review.

Use real units. Geometry uses declared Godot world units or pixels; angles use
degrees; time uses seconds; speed uses world-units/second or pixels/second;
colors use a named color space; ratios and normalized controls state that they
are unitless. Do not accept labels such as `small`, `fast`, or `high variance`
without numeric bounds. A parameter outside its declared range is a grammar
violation, not a new variation.

Prohibited combinations are executable design constraints, not aesthetic notes.
Include pairwise or conditional exclusions that cause unreadable silhouettes,
z-fighting, clipping, collision mismatch, impossible animation, noisy value
grouping, inaccessible contrast, or budget overflow. Reject invalid combinations
before asset export and record the rejection reason under the original seed.

## Make roles readable at play distance

Assign each gameplay role a dominant silhouette cue, secondary cue, value or
color relationship, and minimum readable screen size. Cover at least player,
threat, objective, interactable, blocker, and background roles when present.
Test the canonical gameplay camera at native target resolution and at the
smallest supported viewport; a close-up editor view does not count.

Variation may change surface detail, proportions within range, accessories, or
palette accents, but must preserve the role's dominant cue and must not borrow a
cue reserved for a conflicting role. Detail cannot compensate for a collapsed
outline or value mass. Character identity must remain visible where the role or
story requires it; repeated concealment or camera avoidance is not a repair for
an unreadable character foundation.

## Deterministic seed contract

The same recorded seed, grammar version, generator version, source inputs, and
engine settings must reproduce the same logical output. Define seed
canonicalization, the pseudorandom algorithm and version, stream/substream
assignment, iteration order, and rounding rules. Never depend on wall-clock time,
filesystem order, locale, or unstable node ordering.

Persist the original integer or stable string seed with every generated artifact.
Changing the grammar, algorithm, or source inputs creates a new version even if
the visible output seems unchanged. A retry retains the seed and records the
failure; silently replacing it with a favorable seed is cherry-picking.

## Predeclare the review population

Freeze the population plan, seed list, sample count, camera set, acceptance rubric,
and stopping rule before inspecting outputs. The evidence suite contains all four
classes below; no class compensates for another:

| Class | Required selection and evidence |
| --- | --- |
| `canonical` | Stable authored seeds for the promised roles and ordinary states. Keep them fixed across revisions. |
| `random` | Seeds selected by the recorded deterministic sampling procedure, not by visual preference. Retain every result in draw order. |
| `boundary` | Declared minima, maxima, quantization edges, and risky allowed parameter interactions. Include rejected and failed builds. |
| `worst_observed` | The lowest-scoring output from the complete declared population under the frozen rubric. Record the population artifact and selection method. |

The population artifact lists every attempted seed, parameter vector, class,
generator outcome, Godot build outcome, rubric result, artifact IDs, and rejection
reason. Preserve timeouts, crashes, invalid combinations, import failures, and
unusable outputs in the denominator. Do not stop sampling after finding a good
seed, replace failed seeds, publish only a contact-sheet highlight, or redefine
the rubric after seeing results. Canonical, random, boundary, and worst-observed
must use four distinct seeds and distinct Godot output artifacts; relabeling one
seed, path, or byte-identical output as several classes fails the suite.

Measure build success separately from visual acceptance:

`build_success_rate = qualified Godot builds / all predeclared population attempts`

A qualified Godot build completes generation and import in the declared target
Godot version, instantiates the required runtime scene/resources without relevant
errors, and produces every required canonical-camera capture. Report numerator,
denominator, total rate, and rates by seed class; a percentage without counts is
insufficient. A visually weak but runnable case is a build success and a visual
failure. An invalid, crashed, timed-out, missing, or substituted case is not a
build success.

## Judge the target Godot result

For each reviewed seed, capture the representative runtime state from the actual
target Godot build at the declared camera, viewport, renderer, lighting, and
quality settings. Include representative motion or state transitions when they
affect silhouette, material response, layering, or effects.

Source-tool renders, generator previews, isolated sprites, and modeling turntables
may diagnose the pipeline, but they cannot pass the visual gate or substitute for
Godot runtime captures. Compare runtime captures to the approved visual contract
and preserve both favorable and adverse cases. A generated target image remains
design evidence, not proof that the procedural system works in Godot.

## Record qualified foundation attempts

Before a repair, create an attempt record containing:

- `attempt_id` and the unchanged `foundation_id`;
- the unchanged `acceptance_gate_id`;
- a predeclared hypothesis with a predicted observable improvement;
- the exact bounded change;
- representative target-Godot evidence IDs;
- an independent review covering that foundation, gate, and evidence;
- the normalized `observed_failure_signature`; and
- the decision: `improved`, `same_failure`, or `different_failure`.

An attempt is qualified only when every field is present, evidence integrity
passes, the bounded change tests the declared hypothesis, the same acceptance gate
is applied, representative Godot runtime captures exist, and an independent
review covers the exact evidence. Parameter churn, extra variants, a changed gate,
a replaced foundation under the same name, or an unreviewed source render does not
count.

Two qualified attempts with the same `foundation_id`, `acceptance_gate_id`, and
structural `observed_failure_signature` force a foundation pivot. Stop tuning and
change the basis responsible for the failure—such as shape language, topology,
rendering method, character abstraction, material model, or generator
architecture—then assign a new foundation ID and re-establish its grammar and
population plan. Sunk time, one attractive seed, or a higher variant count cannot
waive the pivot.
