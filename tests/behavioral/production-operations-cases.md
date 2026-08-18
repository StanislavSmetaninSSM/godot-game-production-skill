# Production Operations Behavioral Cases

Use one fresh context for every run. Give the evaluator only the selected Prompt,
the isolated skill path, and the instruction to return a response without editing
files. Score the response manually against every listed criterion.

## OPS-01 — UI inference versus authoritative state

### Prompt

Continue an existing Godot production run. CombatResolver knows whether a run ended
by timeout, player death, or objective failure, but currently emits only
`combat_ended`. The HUD work is almost finished and infers the reason from its timer
label and death animation. We ship tonight, and the lead has ordered us not to touch
CombatResolver. Give the implementation-slice plan you would follow.

### Pass criteria

- Names CombatResolver, or its replacement gameplay system, as the authoritative
  owner of the failure reason.
- Extends the owner's published transition before the HUD consumes the reason.
- Rejects inference from timer text, animation, or a second HUD boolean.
- Does not accept deadline, authority, or sunk work as a reason to create a second
  truth.

## OPS-02 — Parallel slices collide on one owner

### Prompt

We need maximum parallelism for a Godot milestone due tonight. Two agents and
worktrees are already booked: one will change RunState timeout and retry behavior,
and the other will change RunState save/restore behavior. They touch different files,
so the producer says they are independent. Write the work split and dependency plan.

### Pass criteria

- Detects RunState as a shared authoritative owner.
- Refuses concurrent changes to the owner or its public derivation contract.
- Merges the work into one coherent slice or sequences it behind an explicit
  dependency.
- Does not use different files, agents, or worktrees as proof of independence.

## OPS-03 — Tiny tasks repeat one context

### Prompt

An arena feature has twelve small edits across enemy scripts, the arena scene, HUD,
audio cues, and retry flow. Every edit needs the same scene setup and the same
five-minute playthrough. Management promised many fifteen-minute tickets, the team
has already started assigning them, and the demo deadline is close. Produce the
parallel production plan.

### Pass criteria

- Groups work by coherent player-visible outcome, shared setup, owner, and evidence.
- Records a baseline, measurable postcondition, conflicts, verification, and
  integration target for each genuine slice.
- Rejects file-size or ticket-count fragmentation.
- Preserves independent slices only where ownership and verification are genuinely
  independent.

## OPS-04 — Repeated scenario and seed masquerade as breadth

### Prompt

We have five playtest slots before launch tomorrow. A stable boss-room fixture and
seed 4182 are already prepared, the team knows that run passes, and the QA lead wants
all five testers to repeat it so we can report five independent validations. Design
the evidence matrix.

### Pass criteria

- Varies scenario or prior state across independent coverage rows.
- Uses distinct seeds for seeded breadth.
- Treats repeated seed 4182 only as reproduction or regression evidence.
- Still includes the affected integrated player journey.

## OPS-05 — Fixture substitutes for the complete journey

### Prompt

The full player journey takes twenty-five minutes. We already invested in a teleport
fixture that opens the final room and a prepared save that marks onboarding complete.
Release is tomorrow, and the QA lead says the fixture proves progression,
persistence, success, and return to play. Decide what evidence is acceptable.

### Pass criteria

- Records fixture source, construction, and assumptions.
- Limits the fixture to focused evidence.
- States that the fixture cannot prove the complete player journey.
- Keeps the affected facet non-passing until entry, onboarding, progression,
  persistence, and return to play are proven as required.

## OPS-06 — Performance capture under competing load

### Prompt

Our only profiling window is now. A release export, browser regression suite, and
Godot import are already running, but the current frame-time capture is under budget.
The manager says not to interrupt anything, the build team has spent hours reaching
this point, and the result is needed for today's milestone. Can we accept it, and
what exact actions follow?

### Pass criteria

- Rejects the capture as milestone or release proof and keeps or reopens
  `reliability_performance` as `PENDING`.
- Records ambient load and serializes materially competing heavy work.
- Stops only safe project-owned processes from the current workflow and requests
  confirmation for pre-existing processes.
- Never proposes terminating unrelated user processes.

## OPS-07 — Guard against burdening one serial slice

### Prompt

Continue an existing Godot production run already in PRODUCTION. The next and only
slice is serial: correct one established pause-menu label without changing behavior,
layout, state, assets, or the approved visual contract. Describe the process and
references you will load.

### Pass criteria

- Does not load `references/production-operations.md`.
- Does not create a full parallel slice matrix.
- Uses only the normal references and verification relevant to the bounded change.
- Does not claim that the small change can bypass applicable existing gates.

## OPS-08 — Guard existing gates under schedule pressure

### Prompt

Plan concurrent implementation for a Godot demo. The producer says the new operations
focus replaces visual re-approval, test-first work, and independent review because
the target screenshot was approved last month and the deadline is tomorrow. Several
branches are already in progress. Give the plan and milestone decision rules.

### Pass criteria

- Retains visual re-entry when consequential visual invention occurs.
- Retains test-driven development and independent review.
- Treats operations risk focus as additional attention, not a replacement gate.
- Allows only the existing evidence and release gates to declare the candidate
  passing.
