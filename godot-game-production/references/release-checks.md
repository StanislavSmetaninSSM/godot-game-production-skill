# Release Checks

Use this contract for every milestone and final release. Evaluate the exact candidate
artifacts, not a branch name, status document, manifest path, prior build, or
builder-authored claim.

## Independent facet gate

Review all eight facets independently against their exact evidence and immutable
review records:

1. `core_play`
2. `systems_holism`
3. `content`
4. `visual`
5. `audio_feedback`
6. `ux_onboarding`
7. `reliability_performance`
8. `ship`

Each review names every exact artifact ID, project-relative path, and SHA-256 it
covers. Its acceptance or rejection must cover that exact set without omissions.
Every review record must be referenced exactly once by its declared facet. An
orphaned, multiply referenced, or explicitly rejecting review is non-passing; a
manifest cannot hide contradictory review evidence by leaving its ID out of a
facet.

Each facet must pass on its own. Never average scores, trade one strong facet for a
weak one, waive a missing facet, or infer acceptance from the overall impression.
Any missing, stale, rejected, mismatched, or integrity-failed evidence leaves that
facet non-passing and prevents milestone PASS.

The builder may contribute evidence and self-review, but must not be the sole
aesthetic reviewer or cold-player reviewer. User visual approval must bind the exact
target artifact set. Cold-player UX review must cover the exact first-session
evidence. Keep those reviewers literally distinct from the builder and preserve
their accept/reject records; bookkeeping separation does not prove real identity or
review quality.

## Milestone decision

Record the candidate identity, evidence and review identities, one decision, its
rationale, and every unresolved blocker:

- `PASS`: all eight facets independently pass for this exact candidate and no
  unresolved blocker remains.
- `PIVOT`: evidence shows the current foundation or approach should change. Record
  the failed gate and replacement direction before more production.
- `STOP`: a blocker, rejection, integrity failure, infeasible constraint, or risk
  prevents safe continuation. Record what would be required to resume.

`PIVOT` and `STOP` are non-passing. `PENDING`, `BLOCKED`, a builder-authored PASS,
or a ledger path is not milestone acceptance.

## Controlled performance capture

For every performance run, record:

- exact candidate, Godot version, export profile, target hardware, and environment;
- available CPU, GPU, memory, thermal, and power state;
- foreground and background load before and during capture;
- project-owned editor, import, build, test, capture, and browser-test processes
  stopped or intentionally retained; and
- measurement command, duration, scenario, seed, raw artifact, and budget source.

Heavy build, import, browser-test, and performance-capture jobs must not overlap when
they can materially contend for the measured resource. Stop only processes known to
belong to the in-scope project. Processes launched by the current workflow may be
stopped when safe; pre-existing processes require user confirmation.
Never terminate unrelated user processes to obtain a clean number.
For an active-load action plan, classify every competing process as a safe
project-owned process launched by the current workflow, a pre-existing process, or
an unrelated user process. State that only the first class may be stopped when safe,
explicitly request confirmation before stopping the second, and never stop the third;
waiting for the current jobs to finish does not replace this ownership protocol.
Write the facet and milestone states separately: the contaminated performance facet
is `reliability_performance: PENDING`, while the milestone remains non-passing. Use
an explicit action such as "request user confirmation before stopping this
pre-existing process"; merely saying confirmation is required is not the request.
For each pre-existing competing process, include the action `request user
confirmation before any stop; retain it until confirmed`. Include that action even
when waiting is currently safest; an active-load plan that only waits or says not to
stop processes omits the required ownership decision.
Keep that ownership classification and confirmation action in the submitted final
answer; an internal note or intermediate message does not satisfy the action plan.

If competing load cannot be safely controlled, changes materially during the run,
or is not recorded, do not submit the capture. Keep or reopen
`reliability_performance` as `PENDING` and repeat under a controlled environment.
Contaminated data cannot support a milestone or release pass; it may diagnose a
problem only.

Derive budgets from the requirement and declared target hardware. Do not import a
universal threshold from another project.

## Runtime and release proof

Before release, capture all of the following for the exact candidate:

- A complete session on declared target hardware, with Godot runtime evidence and
  profiler or telemetry output covering the promised performance budget and notable
  worst cases.
- A clean-checkout rehearsal that installs dependencies and imports the project from
  scratch, then builds the release package without relying on untracked files,
  warmed caches, editor state, or the builder's existing workspace.
- A clean-install launch of that package on the target environment, including the
  intended input, display, audio, and platform path.
- A runtime save, process exit, restart, load, and return-to-play sequence proving
  persistence from the packaged build. Include failure/recovery behavior where the
  game contract requires it.
- Release identity containing the version, platform/configuration, exact package
  path or artifact ID, lowercase SHA-256, build provenance, and matching evidence-run
  identity. Recompute the hash after final packaging.

An editor run, development build, source render, earlier package, or different
hardware profile does not substitute for a required release proof.

## Completion language and regression handling

Say a milestone or release is complete only after the exact identified artifacts
and reviews above have been verified and the recorded decision is `PASS`. Name the
verified candidate and evidence; otherwise state the current decision and unresolved
blockers without completion wording.

Any code, content, asset, configuration, dependency, engine, export, packaging, or
hardware change that can invalidate evidence reopens every affected facet. A newly
observed regression also reopens its facet and any dependent milestone. A changed
or missing artifact reopens its facet. Replace stale captures and reviews, rerun the
affected release checks, recompute release identity when bytes change, and issue a
new decision; a previous PASS never survives contradictory evidence.
