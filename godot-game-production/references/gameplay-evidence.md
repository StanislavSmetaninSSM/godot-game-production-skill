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

Give reviewers the exact captures without builder rationale first. Require a user
review for the visual contract, a cold player for onboarding, and independent
reviews for the other submitted facets. A rejection, missing capture, wrong build,
or incomplete evidence set keeps that facet failed or pending.
