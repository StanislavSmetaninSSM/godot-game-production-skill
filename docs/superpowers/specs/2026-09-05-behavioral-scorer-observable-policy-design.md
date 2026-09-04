# Behavioral Scorer Observable Policy Design

## Decision

The dynamic-visual behavioral scorer must judge observable acceptance facts, not
which files an evaluator read. Reading Superpowers, Spec Kit bridge, ImageGen, or
other installed instructions is legitimate runtime behavior and cannot be treated
as evidence of a bad answer.

Replace `dvc-trace/v1` with `dvc-trace/v2`. The v2 trace contains only:

- evaluator identity and configured model/effort/fork mode;
- final-answer and task-completion counts;
- pre-authorization ImageGen call count;
- write paths recorded by the evaluation runner.

It contains no `read_paths` or generic `tool_calls`. The scorer therefore has no
filesystem-read policy.

## Trust boundary

The evaluation runner controls which task prompt and installable skill are exposed.
Specs, plans, expectation catalogs, previous answers, and evaluator reports must not
be supplied to the evaluator. That isolation is a runner responsibility; a
self-reported read inventory cannot enforce it physically.

The scorer continues to fail closed on malformed traces, unexpected fields, the
wrong model configuration, multiple final answers, missing task completion,
pre-authorization ImageGen calls, writes, invalid decisions, and report collisions.

## Compatibility

There is no v1 compatibility path. Existing retained historical reports stay
historical; every fresh run must emit `dvc-trace/v2`.

## Verification

- A v2 trace without read telemetry passes when its answer is valid.
- A legacy v1 trace or any v2 trace containing read telemetry is rejected.
- ImageGen, writes, extra final answers, malformed counters, and all decision
  failures remain rejected.
- The full deterministic suite and official skill validator pass.
