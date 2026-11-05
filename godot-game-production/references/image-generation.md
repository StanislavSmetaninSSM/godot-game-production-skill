# Neutral image-generation adapter contract

The portable core resolves one registered provider before generation and reads its
adapter. The adapter maps the neutral request to its native capability and normalizes
the result. It does not approve scope, expand a batch, authorize a retry, or turn raw
output into accepted evidence.

## Provider resolution failures and custom providers

Resolution failures close the selection path without automatic provider switching:

| Failure | Resolver result |
| --- | --- |
| malformed configuration | exit `3` |
| unknown provider | exit `2` |
| missing adapter | exit `2` |
| duplicate runtime default | exit `2` |
| unsafe path | exit `3` |

Adding a custom provider requires exactly two integration artifacts:

1. One entry in `godot-game-production/providers/registry.json` containing its
   adapter path and any unique runtime defaults. Keep the registry top level to exactly
   `schema_version` and `providers`, with `schema_version` set to
   `image-provider-registry/v1`. Add the custom ID under `providers`; provider and
   runtime IDs must match `[a-z][a-z0-9-]*`. Each provider entry has exactly
   `adapter_path` and `default_for_runtimes`. Set `adapter_path` to an existing,
   skill-relative, non-symlink Markdown file without absolute or parent-traversing
   path segments. Set `default_for_runtimes` to a required nonempty array of runtime
   IDs, with no duplicates inside the array and no runtime already claimed as another
   provider's default.
2. Add one provider adapter document implementing the neutral request/result contract defined below, including native preflight and truthful outcome normalization.

Adding a provider does not need or permit any edit to the portable visual-approval sequence.
Do not add a common generation CLI: the selected adapter still owns the native
invocation, while the portable authorization and evidence gates remain unchanged.

## Neutral generation request

This conceptual request is not a new stored evidence schema.

| Field | Contract |
| --- | --- |
| `work_kind` | `reference` or `production_asset`. |
| `subject_id` | Exact reference slot or production asset identifier. |
| `authorization_id` | The value is required for reference work and equal to its immutable authorization; absent for ordinary production assets. |
| `description` | Complete visual prompt derived from the approved direction. |
| `size` | Provider-valid width and height. |
| `background` | `opaque` or `transparent`, subject to provider constraints. |
| `reference_images` | Only inputs belonging to the authorized work or approved production direction. |
| `output_path` | Project-local destination chosen before invocation. |

The adapter preflights its native capability, dependencies, credentials, request
constraints, reference handling, and destination without generating. For reference
work, the existing decision, full-set scope approval, and
`visual-generation-authorization/v1` with `AUTHORIZED` must already bind the request.
One authorized reference slot produces exactly one generation request and one authorized result per reference slot.

## Neutral generation result

| Field | Contract |
| --- | --- |
| `status` | `succeeded`, `failed`, or `unknown`. |
| `provider_id` | Actual invoked provider. |
| `job_id` | Available provider job/reference identity, or a truthful explanation when unavailable. |
| `raw_path` | Actual returned raw file when one exists. |
| `accepted_png_path` | Readable project-local accepted PNG after any recorded conversion. |
| `media_type` | Observed returned and accepted media types, never inferred only from extension. |
| `error` | Concrete failure or unresolved-outcome explanation when unsuccessful. |

Only `succeeded` with a readable project-local accepted PNG may enter subsequent
visual evidence. Exact authorization and slot binding still apply to references,
followed by actual bitmap display, SHA-256 binding, complete-batch review, and the
existing target and Godot evidence gates. `failed`, `unknown`, provider-`unavailable`,
and `malformed` results cannot enter subsequent visual evidence. There is no
fabricated successful path or accepted artifact.

Preserve the raw file and observed media type. If conversion is needed, retain the
raw file, create a separate accepted PNG, verify readability and media type, and
record the conversion and both paths in generation work notes. Display and hash the
accepted PNG, not a disguised or renamed non-PNG payload.

## Batch and production-asset boundaries

Display the complete candidate batch for the authorized reference set. Fail closed for
partial batches, missing slots, duplicates, extras, and unbound results: no target approval is permitted for a partial batch. Rejected images continue through the
existing `visual-correction-approval/v1` and fresh correction authorization flow.

Production assets retain the existing autonomous refinement within the approved direction/task budget, without inventing reference authorization. They follow the
same truthful file, conversion, and readable-result requirements, but do not consume
reference slots or require per-image target approval. Their integration still needs
the existing Godot evidence.

## Failure, observation, and reauthorization

A preflight failure before invocation consumes no result budget. After generator
invocation, there is no automatic retry and no provider switch. An `unknown` outcome
resumes observation of the same job through the adapter; it never launches a
replacement job.

A definite technical failure without a result is not image rejection. Before another
reference attempt, create a NEW decision ID, obtain renewed approval of the COMPLETE affected batch, and issue fresh authorization. You must retain consumed decision/authorization records for audit; never reuse them for the replacement
attempt. A technical failure is not image rejection and must not be routed through
the visual-correction flow as though the user rejected an image.

## Preserved evidence contracts

`visual-decision/v2`, `visual-generation-authorization/v1`, `evidence-run/v2`, and the
stored provenance `imagegen_target` remain unchanged. Provider identity, job identity,
raw/accepted paths, observed media types, and conversion details are generation work
notes and audit metadata, not replacements for any existing evidence field or gate.
