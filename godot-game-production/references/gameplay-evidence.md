# Gameplay Evidence

Prove the smallest complete player journey before multiplying content:

`playable entry -> goal comprehension -> input -> state transition -> feedback -> risk -> failure/retry -> success -> persistence -> return to play`

For each mechanic claim, record the exact input, prior state, resulting state, and
player-visible outcome. Bind those records to a filmstrip or video captured from
the target Godot build. Include the canonical path plus failure, retry, and success;
an isolated happy-path action is not a complete loop.

A still screenshot never proves a mechanic. Generated targets and source renders
are not runtime evidence. Unit tests may support a claim, but they do not replace
the causal in-game capture.

## Early exported preflight

Once the smallest loop is playable, export a development candidate and exercise
normal entry, the central interaction, danger/interruption, loss/retry and success
where implemented. Check the actual win trigger (including exit entry when required).
Unimplemented outcomes stay explicit gaps; revisit them before candidate freeze.
Verify the capture/input adapter in that package with a short clip and owner trace:
readable frames, real inputs, matching state/outcome, and an audible event through
its tail. A harness that works in the editor may be unavailable in an export.

Run one representative `SUBMITTED` evidence path early, using real captures and
available review records. Inspect its actual binding/path/coverage diagnostics;
validating only a PENDING ledger does not exercise those checks. Other facets can
remain pending. Neither this preflight nor a synthetic validator fixture is final
acceptance. Preserve candidate identity and fix the adapter before long captures.

## Playtest matrix

Before repeated playtests, record one row per planned run:

| Field | Required content |
|---|---|
| `scenario` | Player goal or risk being exercised. |
| `prior_state` | Exact starting gameplay and persistence state. |
| `seed` | Exact procedural seed, or `not_applicable` for non-seeded behavior. |
| `input` | Exact player or automation input sequence. |
| `expected_transition` | Authoritative state change and visible outcome. |
| `artifact` | Target-build capture, trace, save, or telemetry identity. |

Before candidate freeze, add a small risk-based set of **mechanic intersections**.
Choose shared owners/resources and transition boundaries, not every Cartesian pair.
Examples: carry + drop at an interaction zone; damage + held interaction; pause +
partial work; suppression expiry + hazard warning; moving pickup + speed/acceleration
change. Record priority when multiple actions are eligible, release/repress behavior,
resource/progress retention and the route back to playable state. Validate numeric
invariants alongside visible outcomes; a passing isolated mechanic is insufficient.

Independent coverage rows vary scenario or prior state. Seeded rows intended to
broaden coverage also use distinct seeds. A repeated seed is valid for reproduction
or regression proof when labelled as such; it does not count as diversified coverage.
When asked to design independent validation, redesign the actual slot matrix; do not
preserve every row as the repeated fixture and merely narrow the report wording. The
coverage matrix must include the affected integrated player journey as a row, while
other independent rows vary scenario or prior state and use distinct seeds when
seeded breadth is claimed.
Allocate limited slots to the integrated journey from its normal entry/prior state,
then to a labelled canonical reproduction if useful, and to distinct random,
boundary, and worst-observed cases as applicable. Never allocate all
independent-validation slots to the same fixture and seed.
For a five-slot seeded matrix, write these as the actual planned rows rather than
future gaps: `(normal-entry integrated journey, a seed distinct from the fixture)`,
`(canonical fixture reproduction, known seed, reproduction only)`, `(random case,
distinct seed)`, `(boundary case, distinct seed)`, and `(worst-observed case,
distinct seed plus population and selection artifact)`. Give the independent rows
different scenarios or prior states; do not return the rejected all-repetition
matrix before suggesting diversified work later.

Fixtures may accelerate a focused test only when their source, construction, and
assumptions are recorded. A fixture does not prove the complete player journey:
entry, onboarding, progression, persistence, and return to play still require the
integrated target-build journey applicable to the milestone.
When deciding whether fixture evidence is acceptable, record those three provenance
fields for each fixture first; if they are unavailable, record them as required
unknowns. Naming only the fixture's focused use is not a provenance record.
Use an explicit `fixture | source | construction | assumptions | focused claim`
record before the acceptance decision. Write `unknown - required before use` for
details the prompt or evidence does not provide instead of omitting the field.
Every fixture-evidence decision must begin with that table and contain one completed
row for each fixture or prepared save under consideration. A prose conclusion, a
request to capture provenance later, or a row for only one shortcut is incomplete.

Group observed failures by authoritative owner and zone before creating repair
slices. Keep similar symptoms with different owners separate; combine different
symptoms from one owner so they do not become competing parallel repairs.

## Keep the product facets separate

Core play, systems/holism, and content answer different questions:

- Core play asks whether input produces the intended readable loop.
- Systems/holism asks whether progression, strategy, economy, and dominant choices
  behave across a representative session.
- Content asks whether pacing, variety, volume, and the complete-session arc meet
  the bounded promise.

Also capture action, danger, success, failure, and ambience audio/feedback; target
hardware telemetry; clean install and save/restart; and cold-player first-session
evidence for onboarding. Do not infer one facet from another or average failures.

## Review gate

Use `visual-quality.md` for measured frame findings and `motion-quality.md` for
motion/event/coverage diagnostics when those claims are part of the slice.
Register supporting captures and reports against the same candidate using the
existing ledger; a diagnostic CHECKS_PASSED is not a facet or milestone decision.
Missing required observations remain pending even when other measurements pass.

Give reviewers the exact captures without builder rationale first. Require a user
or explicitly delegated independent review for the visual contract (see
`evidence-ledger.md`), a cold player for onboarding, and independent
reviews for the other submitted facets. A rejection, missing capture, wrong build,
or incomplete evidence set keeps that facet failed or pending.

## Bounded cold-player protocol

Before dispatch, record the question, exact build, normal entry, permitted inputs,
attempt and wall-time limits, and a stop condition for repeated no-progress states.
Choose limits for the promised session and available budget. A cold player gets
player-visible instructions and pixels, without source, telemetry, route coaching,
prepared progression or the builder's explanation. Developer-assisted routes remain
useful but are labelled separately. Preserve losses, confusion and abandoned attempts.

Record simulation play time, wall time, pause policy and input transport separately.
At the limit, report observations and unresolved claims; a timeout is not acceptance
or proof of poor game design. Reasoning pauses alter reaction pressure and pacing.
A paused screenshot-driven agent route supports discoverability only within that
protocol; it does not establish continuous human feel, accessibility or native
hardware input. If those are promised, obtain the corresponding test or leave the
claim unverified. Keep continuous audio/performance runs separate under
`release-checks.md`; do not record hours of pause silence as gameplay coverage.
