# Evidence Ledger

Create a project-local ledger after the Godot project exists:

```text
python scripts/evidence_run.py init --project-root <root> --manifest <root>/evidence-run.json --builder-id <id> --dimension <2d|2.5d|3d> --procedural-mode <none|seeded>
python scripts/evidence_run.py validate --project-root <root> --manifest <root>/evidence-run.json --report <root>/evidence-report.json --strict
```

The manifest always contains these independent facets:

`core_play, systems_holism, content, visual, audio_feedback, ux_onboarding, reliability_performance, ship`

Use `PENDING` before evidence exists. Use `SUBMITTED` only when its exact artifact
and review IDs are ready. `SUBMITTED` requests validation; it never declares PASS.
Never write `PASS` or `BLOCKED` as input. A declared `FAILED`, `PIVOT`, or `STOP`
remains non-passing. JSON object keys must be unique at every depth; contradictory
duplicate keys make the manifest invalid instead of allowing a last-value override.

## Integrity and approval

Keep every artifact at a project-relative path with its recomputed lowercase
SHA-256. Path traversal, symlink escape, missing files, and SHA-256 drift fail.
A report may replace only an existing `evidence-report/v1` JSON report; it must
never alias the manifest, `project.godot`, evidence, or an approved target. For
visual approval, bind the complete `(target_id, sha256, path)` set after copying
targets into the versioned project contract directory. The approval `contract_id`
must exactly equal that directory's `vc-*` version and `recorded_at` must be a
timezone-aware ISO-8601 timestamp. Require canonical Godot
captures for every approved target; ImageGen or source-render substitutes fail.

Reviews must cover the exact facet evidence set and refer to immutable review
records. Reference every review exactly once from its declared facet; an orphan,
duplicate reference, or any explicit rejection fails the candidate. Keep the
visual user and cold-player UX reviewer IDs distinct from the
builder. This is a literal bookkeeping check, not proof that two IDs are different
people.

For every seeded procedural system, include canonical, random, boundary, and
worst_observed cases. Bind the worst-observed case to its population artifact and
selection method. Every case needs its exact seed and a typed Godot procedural output;
all four classes require distinct seeds and distinct outputs, so aliases do not
count. The population
record is distinct from the selected worst output. Never omit a bad class because
another seed looks good.

For `VERIFIED`, require non-empty Godot version and target hardware and bind the
game build ID to the exact ship-facet release artifact. Artifact kinds must use
their allowlisted runtime, trace, build, environment, ImageGen, or review
provenance; a label from the wrong provenance fails.

Exit `0` means structurally VERIFIED, `1` PENDING, `2` FAILED, and `3` invalid input.
The report derives these states without a score or average. It proves local shape
and bytes only; it does not prove provenance truth, human identity, artistic quality,
fun, or shipping readiness.
