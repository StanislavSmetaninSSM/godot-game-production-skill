# Neutral model generation and processing

Use this contract for 3D production-source work after the relevant visual target is
approved and within the existing production task and budget. Model providers are
separate from image providers: their registries, selection files, resolver commands,
and adapters are not interchangeable.

Resolve the provider from the skill root and current Godot project root before any
native invocation:

```sh
python scripts/model_provider.py resolve --runtime <runtime-id> --project-root "<project-root>"
```

An explicit current-user choice may add `--provider <provider-id>`. Read the returned
skill-relative `adapter_path`. Resolution only validates selection and the adapter
path; it does not generate, upload, check credentials, or establish paid-provider
availability. Unknown, ambiguous, unavailable, malformed, or unsafe resolution fails
closed without fallback.

Resolve **skill root** as the directory containing the loaded `godot-game-production`
`SKILL.md`. The commands below run with that directory as cwd; `scripts/` is directly
inside it. From another cwd, use the equivalent absolute script path beneath that
resolved skill root and quote it. `<project-root>` is the separate existing absolute
Godot project directory; quote it when it contains spaces. Read `adapter_path` relative
to skill root, never project root. Repository checkout examples in README.md explicitly
use the repository root, one directory above this installed-package layout.

## Request and authorization boundary

The conceptual request is adapter data, not a new evidence schema or required JSON
file. It has these fields:

| Field | Required meaning |
| --- | --- |
| `work_kind` | Always `production_asset`; generated GLB is not a reference-image result. |
| `asset_id` | Stable production asset identifier. |
| `approved_target_id` | Existing approved visual target or approved asset-family linkage. |
| `task_budget_id` | Existing production task/budget authorizing this operation. |
| `operation` | Exactly `generate`, `texture`, `segment`, `complete`, or `decimate`; no generic `process` alias. |
| `provider_model` | Actual native algorithm/model, not the provider ID. |
| `description` | Text prompt only when the selected native operation supports it. |
| `input_images` | Only authorized local/public references belonging to this approved work. |
| `source_model` | Compatible public model URL or source artifact when supported. |
| `source_task_id` | Compatible upstream task identity when supported or required. |
| `constraints` | Native texture, topology, segmentation, completion, and related flags. |
| `output_path` | A distinct project-local `.glb` destination that cannot overwrite a source or another operation output. |

Model generation does not create reference-image authorization and does not consume a
reference-image slot. Routine production refinements remain autonomous within the
approved direction/task budget. New visual direction returns to the existing visual
reference gates.

Before submission, the adapter verifies the resolved provider, native tool and
prerequisites, supported operation and model, exactly one permitted input mode,
authorized inputs, source compatibility and size, flag ranges, and a non-overwriting
output. A preflight failure submits no job and consumes no operation.

## Submit once and observe the same job

Use the selected adapter's native launcher and watcher. For the prepared provider these
are `model3d_generation_launch.py` and `model3d_generation_watch.py`; do not invent a
common model-generation CLI. Launch each authorized operation once, retain its unique
log and PID paths, and watch it in a separate foreground call. A launch success does not mean operation success.

If monitoring is interrupted, inspect the original reports and resume only the watcher
with the same log/PID pair. There is no duplicate submission and no provider switch
because monitoring is interrupted or the outcome is uncertain. A definite failure or a
new attempt requires a distinct authorized operation within the existing task/budget;
retain every consumed task and log record.

## Processing, provenance, and parallel work

For `generate`, raw and accepted paths may identify the same newly created GLB after inspection. For processing, `raw_path` is the preserved input and `accepted_glb_path` is the distinct processed output. Preserve source model and source/task linkage for every operation. No operation may overwrite its input. Both are retained and hashed in project asset notes.

Before any processing submission, require either an existing project-local raw source with a verified contained path, readable expected format, and SHA-256, or explicitly acquire the authorized source to a distinct project-local raw path and complete those checks before preflight can pass. Acquisition is source preservation, not a processing submission. If neither route produces the verified local raw artifact, fail preflight without submission. A public URL or task ID remains source linkage and is never `raw_path` or a substitute for its hash.

When a native operation supports a non-GLB source (for example GLTF, FBX, OBJ or
STL), retain its original bytes, actual format, path and SHA-256. Preserve required
sidecars under the same authorized acquisition boundary. Use an appropriate local
format reader to verify readability; this skill's GLB inspector accepts only GLB.
If conversion is needed, write a separate GLB and record source/converter/output
paths and hashes; never relabel or overwrite the original. Conversion is not a
provider retry or automatic permission for another generation call. The accepted
output remains a separately inspected GLB. Native support and limits are determined
by the selected adapter's installed operation, not by this example format list.

### Processing source admission

| Native source case | Admission as presented | Required artifact set / next step |
| --- | --- | --- |
| Public model URL without project-local raw source | Block preflight without submission | No processing artifact; URL is not raw_path; optional explicit acquisition to a distinct project-local raw path with verified path/hash must finish before a new preflight |
| Externally owned successful task ID without workflow-retained raw source | Block preflight without submission | No processing artifact; task ID is not raw_path; optional explicit acquisition to a distinct project-local raw path with verified path/hash must finish before a new preflight |
| Workflow-owned successful task ID with project-local raw GLB and verified SHA-256 | Allow after raw path/hash verification | raw_path=<project-local raw GLB>; raw_sha256=<verified>; accepted_glb_path=<distinct processed GLB>; accepted_sha256=<computed after save>; retain source task/log |

`texture`, `segment`, and `decimate` consume a compatible successful upstream task ID or supported public model URL within provider limits. `complete` requires the task ID returned by a successful `segment`, never the original generation task or a local GLB as its native task argument. The preserved raw source for completion is that successful segment output. Each step retains its native model, task, log, and output so dependent operations receive compatible sources.

For independent parallel operations, launch every worker before watching any worker. Monitor each job separately with its own distinct output and log. A dependent operation waits for its actual successful source result.

Face and decimation values are targets, not proof. Inspect the delivered GLB before making a strict budget claim. Report `triangle_count_status=verified` only when complete triangle accounting is verified. When that accounting cannot be verified, report `triangle_count_status=unavailable` with `triangle_count=null`; never report an unverified count as compliant.

## Result normalization

Record the actual native outcome with these fields:

| Field | Required meaning |
| --- | --- |
| `status` | `succeeded`, `failed`, or `unknown`. |
| `provider_id` | Actual resolved provider, initially `tripo`. |
| `operation` | Actual native operation, never inferred from a filename. |
| `provider_model` | Actual algorithm/model used for this operation. |
| `task_id` | Upstream task identity when returned, otherwise a truthful unavailable explanation. |
| `raw_path` | Actual raw/source model in its original supported format; generation preserves its newly created raw output. |
| `accepted_glb_path` | Project-local GLB that passed local inspection. |
| `preview_status` | Independently `available`, `unavailable`, or `failed`. |
| `preview_path` | Actual preview only when its download is confirmed and the file exists. |
| `log_path` | Original native operation log retained for resume and provenance. |
| `error` | Concrete error, blocking `unavailable`/`malformed` class, or unresolved outcome. |

Only `succeeded` with a readable project-local GLB that passes
`python scripts/model_artifact.py inspect --project-root "<project-root>" --model "<portable-relative.glb>"`
enters Godot import. `failed`, `unknown`, `unavailable`, and `malformed` cannot enter acceptance. Inspection supplies bounded container/storage checks. A `verified` triangle count requires supported byte-backed geometry; external, compressed, sparse or otherwise unsupported geometry remains `unavailable`. This is not a full glTF validity certificate or proof of visual quality, scale,
pivot, materials, rigging, animation, Godot import success, or gameplay behavior.

A saved valid model remains successful when its optional preview is unavailable or its
preview download fails. Report model and preview outcomes separately and never resubmit
to obtain a preview. Display preview only when its download is confirmed and the file exists. Generated GLB and provider preview are source/design artifacts;
they cannot replace Godot import inspection, consuming-scene capture, independent
review, or gameplay/release evidence.

Project asset notes retain the request linkage, prompts/references, provider, native
model and operation, source and upstream task IDs, raw and accepted paths, log, preview
outcome, inspection hash and triangle-count status, consuming scene, and Godot evidence.
Existing `visual-decision/v2`, `visual-generation-authorization/v1`, `evidence-run/v2`,
`imagegen_target`, and behavioral-trace schemas remain unchanged.

## Add a custom model provider

Adding a custom model provider requires exactly two integration artifacts:

1. One `model-providers/registry.json` entry for the new provider ID. Keep the registry
   top level to exactly `schema_version` and `providers`, with `schema_version` set to
   `model-provider-registry/v1`. Provider and runtime IDs must match
   `[a-z][a-z0-9-]*`. Each provider entry has exactly `adapter_path` and `default_for_runtimes`.
2. Add one neutral adapter document at the registered path. Its first line must be
   `<!-- provider-kind: model -->`; the resolver rejects missing, malformed, repeated
   or image-kind metadata. This is part of the same document, not another artifact.
   It must implement this
   contract's preflight, one-submission observation, result normalization,
   raw/processed preservation, independent preview outcome, local GLB inspection,
   provenance, and fail-closed recovery semantics for every operation it supports.

Set `adapter_path` to an existing portable skill-relative Markdown path beneath the
installed skill root. Reject absolute paths, backslashes, NUL, trailing slashes, and `.`/`..` segments;
every existing component must be ordinary, without a symlink, junction, or other reparse-point component,
and the resolved file must remain inside the skill root. The required
`default_for_runtimes` may be empty for an explicit/project-only custom provider.
Otherwise it contains unique runtime IDs, and at most one provider may claim a runtime default
across the complete registry.

Custom selection uses only `docs/visual-contract/model-provider.json` with
`model-provider-selection/v1`, exactly `schema_version` and `provider_id`, and the
precedence documented above. Image `providers/registry.json`,
`docs/visual-contract/image-provider.json`, and `image_provider.py` remain separate with their existing image selection precedence.
A model provider ID never selects an image generator, and an image provider ID never
selects a model generator.

No edit to the portable visual-approval sequence is needed or permitted. There is no common model-generation CLI:
each adapter owns its native invocation while the resolver only selects and validates
that adapter. Do not add a third prepared production provider merely to test this extension;
use hypothetical local registry and selection fixtures outside the prepared production
registry.
