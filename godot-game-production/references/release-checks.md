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
