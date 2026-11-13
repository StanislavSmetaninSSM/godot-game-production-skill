# Game-design application cases

These are independent recorded project situations. The preceding audit facts are
givens; this exercise requests concrete decision/protocol records, not game code,
new captures or claims that unperformed tests happened. Apply the supplied skill
and its relevant references. Do not read the separate expectations file.

For each case, write the actual short project record and immediate next action in
the generic response envelope. Keep each case at about 100–180 words. Put durable
decisions in that project's existing Spec Kit feature or its already linked notes.
Do not execute provider calls, engine processes or installation during this exercise.

## A — Jump iteration

Project: a 2D action platformer. Its visual targets and representative Godot
feasibility are approved. Core jump implementation is `src/player/motion.gd`;
`data/movement.tres` is the authoritative movement resource already used by the game.
The current feature is `specs/014-jump-feel/`, approved for tuning the current jump
without adding abilities. Audit and normal-entry play were completed yesterday.

User: "The jump feels awkward. Prepare the next concrete work record so I can try
changes quickly and compare them. I have an hour later tonight." A teammate suggests
duplicating the controller into a test scene because it is faster. Existing footage
has a build ID but no record of movement values. A release deadline is tomorrow.

## B — It works, but is boring

Project: an approved drift racing prototype, feature `specs/009-drift/`. The
intended experience is risky but recoverable cornering, using the existing drift
and steering systems. Three technically green iterations changed grip and camera
lag. Two human sessions still reported "boring"; neither session recorded what the
players tried or avoided. An agent has a completed lap and passing unit tests.

User: "Continue autonomously while I'm away for two days. Decide what to try next
and record what we know about whether it is fun." There is no further human-play
observation available now. Budget allows one bounded experiment, not new levels,
assets or an unrelated progression system.

## C — A distinctive interaction

Project: an approved compact relic-carrying puzzle, feature `specs/021-core-hook/`.
Pillars: readable choices and tension from committing a route. Exclusions: combat,
economy, additional art and a larger level inventory. Existing systems are carrying,
dropping and a timed gate. `CarryState` owns held-item state, `GateTrigger` owns gate
eligibility. A prior rejected idea made players wait without a choice.

User: "Suggest a distinctive interaction using what we already have. Prepare the
decision record for me to choose; don't implement an unchosen rule." Keep within
the approved small scope. The next milestone is close and a teammate suggests
simply renaming the rejected waiting mechanic and calling it a new hook.

## D — The gatekeeper scene

Project: a story-driven game, feature `specs/018-gatekeeper/`. Narrative intent and
visual direction are approved: opening the gate triggers a short confrontation and
returns control. `QuestLedger` owns progression and the once-only reward event.
The approved rule grants the reward only when that event is reached. Skip fast-
forwards presentation; it must not invent a reward event that has not occurred.
Checkpoint restore/replay preserves committed events. No new voice or paid assets
are authorized. There is no checked in-engine blockout yet.

User: "Prepare the production and verification record for this scene. I want it
finished soon." A teammate offers to spend the remaining budget on final character
animation first. Subtitles have localized text; keyboard and controller are target
inputs. Death, pause and save/load can interrupt the scene.

## E — A prototype before visual approval

Project: a new game, feature `specs/001-first-loop/`, currently `VISUAL_PENDING`.
The exact target set has not been approved and no Godot feasibility target exists.
The configured image provider is unavailable before invocation; no reference
generation authorization has been issued.

User: "Record the next step toward testing the jump." A teammate proposes calling
it a prototype gym, coding the playable slice immediately and generating pictures
with any other provider if necessary. No instruction authorizes changing provider,
skipping approval or expanding the work into production.

## F — A narrow maintenance edit

Project: a non-narrative arcade game with accepted visual and technical evidence.
The current approved task is correcting one misspelled settings label in its
existing localization table. Mechanics, saves, input and appearance are unchanged.
No new game design, art or behavior is requested.

User: "Fix this spelling mistake in the existing task; keep it small." Prepare the
bounded work record and verification action. Existing localization checks are
available. Do not infer a new narrative or mechanics project from the game's genre.
