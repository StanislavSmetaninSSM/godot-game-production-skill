# Narrative beats and staged scene production

Use when story, dialogue, a scripted beat or a cutscene is in the approved game
scope. Non-narrative games and narrow unrelated edits acquire no narrative work.
Keep records in the active Spec Kit feature or its existing linked story/asset notes.

## Bind the beat to play

Record what gameplay event makes the beat happen, its purpose for the player, its
entry/prior state and what playable state follows. Name the authoritative quest,
event/save owner and expected effects. Story intent and rewarded actions should be
consistent. Prefer an interactive beat when it serves the approved experience;
do not take control away merely because a cutscene tool is available.

## Storyboard → checked engine blockout → final

| Stage | Visible artifact | Recorded advance decision |
|---|---|---|
| Storyboard | Short ordered shot/beat cards: action, camera, line/cue, intended timing and return to play. Text or existing approved assets suffice. | Does it express approved intent within scope? Name the existing approval/review authority and unresolved material choices. |
| Engine blockout | Actual consuming Godot scene with rough movement/cameras, temporary timing and available assets; capture the target build. | Check staging, event boundaries, interruption and return of control against the approved contract before final animation. Record actual review/findings. |
| Final | Finished assets/animation/audio within the checked sequence and approved budget. | Repeat affected runtime, state, readability and integration checks on the resulting candidate; retain unresolved gaps. |

Do not spend final-animation effort before the blockout is checked. A storyboard or
generated image is design evidence, not proof that the scene runs. Use the existing
visual/production-asset distinction: an established direction may be implemented
autonomously; a materially new visual direction re-enters its exact-set gates. Image
generation, when appropriate, follows the selected provider and existing authorization
rules, never a new storyboard allowance. A pending visual gate is not bypassed by a
blockout/gym label.

Each handoff records the artifact, scope/build where applicable, actual check,
remaining issue and who/which existing decision authorizes proceeding. These are
project notes, not new approval schemas or a requirement for three new user approvals.
Routine work within approved intent proceeds under that approval; resolve only the
material difference if staging changes narrative, visual direction or task scope.

Write all three handoff rows in the production record, with unperformed work marked
planned/pending: `storyboard artifact → intent check → advance authority/decision`;
`blockout candidate/capture → state and staging checks → reviewer/findings/advance`;
`final candidate → affected recapture/state/readability/integration checks → final
reviewer and acceptance/gaps`. Even when blockout is the immediate next task, keep
the final-candidate row explicit. Final animation/audio/timing changes require fresh
affected evidence and review on that final candidate; a blockout pass is not reused
as acceptance of the finished scene.

## Make state and interruption expectations explicit

Before wiring presentation to gameplay, write the expected state for applicable
normal completion, skip, pause, death/interruption, save/load and replay. The approved
contract determines whether an event commits, cancels or remains pending; skipping
does not universally mean "finish every quest" or "undo every event". Resolve an
unspecified material rule before implementing it.

Use the existing authoritative event/save owner for once-only effects. Presentation
reads/subscribes to that owner, never grants a duplicate reward or invents a shadow
progress flag. Test both sides of each consequential event boundary, including
repeated skip/retrigger and restoring a checkpoint with an already committed event.

Record a causal validation row for each relevant path:

`entry/save state → exact input/event → expected owner commitment(s) → visible and
audible outcome → camera/input/focus recipient → replay/return-to-play result`

| Coverage | Check against the approved scene |
|---|---|
| Normal finish | Beat/event occurs in order, effects commit once, intended play resumes. |
| Skip | Discoverable target-device action, before/after event boundaries, no invented or duplicate effect, correct presentation exit. |
| Pause/death/interruption | Defined cancel/resume behavior; camera, input, focus and audio reach the correct current owner/state rather than blindly re-enabling a dead/paused player. |
| Save/load/replay | Committed effects preserved exactly once, uncommitted effects handled by the contract, no replay reward farming or stranded controls. |
| Subtitles/locales | Text is readable at supported sizes/locales, timing and speaker cues work, skip/focus/controller paths remain usable. |
| Integrated return | Actual normal-entry journey and affected intersections work on the target candidate; storyboard or an editor-only shortcut is insufficient. |

Example: if QuestLedger grants a reward only at its committed event, skipping before
that event cannot synthesize the reward. Restoring a save after the event retains it
without granting it again. Capture the owner state, input and outcome for both paths,
then verify the correct camera/input recipient after the scene exits.

## Report the achieved claim

Bind actual captures, state traces and reviews through the existing ledger and
`gameplay-evidence.md`. Human pacing/interest and continuous audio/input claims need
the matching observations under `release-checks.md`; absent human play remains
unverified. A technical blockout review permits only its recorded scope, not final
scene or milestone acceptance. Continue independent authorized production without
inventing feedback or reopening already approved routine decisions.

Source attribution and license: `third-party-notices.md`.
