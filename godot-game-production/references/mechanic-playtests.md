# Mechanic gyms and experience hypotheses

Contents: [workflow](#place-in-the-current-workflow), [gym](#build-a-gym-around-the-real-mechanic),
[hypothesis](#state-a-falsifiable-experience-hypothesis), [stalled tuning](#respond-to-stalled-tuning), [integration](#carry-the-result-into-the-game).

Use for a new or substantially reworked core/signature mechanic, or when repeated
tuning fails to improve its intended experience. Reuse a suitable existing gym.
A narrow unrelated fix stays in its existing task without a new playtest program.

## Place in the current workflow

Record the mechanic and experiment in the active Spec Kit feature. Keep the existing
visual approval and representative Godot feasibility order before playable production.
While a required gate is pending, prepare the protocol; calling work a gym/prototype
does not authorize implementation. A focused gym supports CORE_LOOP/PRODUCTION and
feeds the integrated journey in `gameplay-evidence.md`; it is not a replacement stage
or release gate. Keep the existing visual, provider and independent-review contracts.

## Build a gym around the real mechanic

Create a directly launchable scene that exercises one approved mechanic without menu
navigation. Instantiate the production player/system; keep its rules in production
code and its parameters under the same authoritative owner used by normal play.
The normal game must not import its implementation from the gym.

Write this concrete gym record in the existing plan/task before implementing it:

| Required slot | Record for this project |
|---|---|
| Purpose and entry | Approved mechanic, focused question, direct scene/entry path. |
| Production binding | Real implementation path, parameter/state owner and both gym/game consumers. |
| Live tuning flow | Panel control → authoritative runtime value → mechanic read; verify the value actually consumed after a change. |
| Reproduction | Initial state, seed when relevant, timestep/input transport, labelled distances/timing markers and restart/reset action. |
| Comparison | Named baseline/variant presets, what changes and what is held fixed; restore the exact baseline. |
| Saved dump | Writable capture destination, retained project-local snapshot path, checked collection if they differ, and explicit apply/revert; preserve baseline and player saves. |
| Evidence | Build and effective parameter values/hash, input/state/outcome capture, observation and integrated follow-up. |
| Debug boundary | Deliberate developer entry, input ownership and exclusion/disablement in ordinary player exports. |

A matching filename alone does not prove shared tuning: a copied resource or UI-only
value can leave the real controller unchanged. Check one live adjustment in the gym,
then its intended application through normal game entry. Save a distinct parameter
dump; applying it to the production source is a tracked change, never an implicit
overwrite. Choose exposed controls from the mechanic and budget. Useful controls are
restart, panel/measurement visibility, preset comparison and optional slow motion;
bind them to the project's supported keyboard/controller actions without stealing
normal gameplay input. Mark altered time/input protocols in the observations.

For example, retain the selected dump as `specs/014-jump-feel/artifacts/jump-parameters.json`.
Godot's `user://` is separate user data, not a project-relative evidence path; `res://`
can be read-only in an export. If capture uses a writable developer-only `user://`
destination, name both that raw destination and the retained project path, plus the
authorized collection and path/hash check before binding evidence. A `user://` path
alone does not complete the record. Leave collection pending if it is not available
within authorization. See [Godot data paths](https://docs.godotengine.org/en/stable/tutorials/io/data_paths.html).

## State a falsifiable experience hypothesis

Use a concrete record, not just a goal such as "make jumping responsive":

| Required slot | Meaning |
|---|---|
| Action and context | What the player does, starting state and relevant mechanic rule. |
| Intended experience | What that action is meant to feel like within the approved promise. |
| Predicted behavior | An observable choice/attempt/retry pattern that would support it. |
| Disconfirmation | What observed behavior would count against that prediction. |
| Bounded protocol | Exact candidate/parameters, participants, entry/input conditions, observation method and task-specific limit. |
| Observations and limits | What actually happened, including confusion/abandonment; who played and what was not observed. |
| Disposition | Retain, revise, investigate, pivot or cut, with reason, authority and next task. |

Keep the **human-experience row** even when its observation is unavailable: write
`action → intended experience → predicted player choice → disconfirming player choice
→ bounded future human protocol → actual observations/unknowns → disposition`.
Put recovery time, successful inputs and other technical outcomes in a separate
supporting test row. They do not fill the human prediction or disconfirmation slots.

Example for an existing jump: "Choosing when to release the button should make
landing feel controllable; players should deliberately vary release timing to reach
two existing ledges. Repeated unchanged presses or avoidance after understood
failures would count against it." Compare recorded presets on the same route with
the user, retaining failed attempts. Choose timing/ranges and attempt limits from
the approved project and observations; an example's numbers are not universal rules.

Technical tests establish rule/state correctness. Coached human gym trials establish
only their stated observation; they are not cold-player onboarding or continuous
native-input proof. An agent route, completed lap or agent's self-assessed preference
cannot establish human enjoyment. Retain an actual participant's reported preference
with the observed session/candidate and its limits; it supports that scoped account,
not an unqualified claim about every player. If a player is unavailable, write `human experience:
unverified`, keep the bounded test ready and continue independent authorized work.
Do not fabricate a session or repeatedly ask for approval of the same scope.

## Respond to stalled tuning

When observations contradict the prediction or numeric iterations stop helping,
record the failed hypothesis and reconsider choice, risk/reward, feedback, rule or
control model before another coefficient adjustment. Explain a causal reason if a
parameter-only experiment is still warranted; technical green is not evidence of fun.
Use one bounded experiment within the current scope. An unresolved material design
change goes through the existing Spec Kit approval path; a faithful record of an
already approved change and routine tuning need no second approval. Keep rejected
options and reasons so the next session does not repeat them. Apply existing stop
rules; do not import a universal hours/rounds/pivots quota.

## Carry the result into the game

Record selected values and their actual application to the production owner. A
changed build or effective parameter state invalidates dependent earlier evidence.
Bind new observations through the existing ledger, then exercise the normal-entry
journey, failure/retry and relevant mechanic intersections on the target build.
Gym readiness is not integrated acceptance; all existing facets and independent
reviews still apply. See `mechanic-ideas.md` for a material redesign and
`release-checks.md` for the limits of experience claims.

Source attribution and license: `third-party-notices.md`.
