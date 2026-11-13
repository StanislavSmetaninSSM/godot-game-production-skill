<!-- provider-kind: model -->
# Tripo model provider

Prepared provider ID `tripo` for the Tripo API-backed model capability. Provider
resolution validates this adapter path and model-kind metadata only; it performs no generation, upload,
credential check, availability preflight, or network call.

## Native capability and installation boundary

On Kimi Work, invoke the exact native skill `model3d_generation:model3d_generation`
through native `Skill`. Use it only for detailed 3D modeling of people and animals unless the user explicitly requests this plugin for another subject. Resolve the installed plugin root from the loaded file's actual
location, `<plugin-root>/skills/model3d_generation/SKILL.md`. The plugin root is two directory levels above the skill directory and contains `kimi.plugin.json` and `scripts/`.
Do not hard-code a user profile or infer the root from the workspace cwd. Native downloaded operation results are GLB; Rigging, animation, and format conversion need other suitable tools when requested.

The native wrapper uses the agent-gw SDK and resolves credentials from `KIMI_API_KEY`
or `~/.kimi/agent-gw.json`. These are external prerequisites, not vendored secrets.
Gateway contract `version=v1` is distinct from the algorithm selected by `--model`.
Check the installed subcommand `--help` for supported flags and values. Missing or
outdated `agent_gw` (0.3.0 or newer) follows the native `ensure-deps` recovery only
after checking whether a worker was already created; do not set `PYTHONPATH` or run
import probes.

## Preflight and authorized inputs

Without submitting a job, validate the selected `tripo` resolution, native
prerequisites, operation, model, flags and ranges, exactly one input mode, source
compatibility, and a distinct absolute project-local `.glb` output that cannot overwrite
its input or another operation output. An invalid request fails before submission and
consumes no operation.

Before any processing operation, require an existing project-local raw source with a verified path and SHA-256, or explicitly acquire the authorized source to a distinct project-local raw path and verify its containment, readability, expected native format, and SHA-256 before submission. Neither a public URL nor a task ID is `raw_path`; they remain native input/provenance linkage only. If neither path is possible, fail preflight without submission.

Native processing downloads its own processed result and optional preview, not the input model. Therefore a URL or externally owned task ID without a retained local raw source is blocked as presented. Explicit source acquisition is a separate authorized preservation step before a new preflight, never a hidden processing request. For `complete`, the preserved raw source is the successful segment output and the segment task ID remains mandatory.

All image URLs must be public and reachable by the service. Upload only authorized local reference images belonging to this work, never unrelated inputs. Run native
`image-to-url` in the foreground before starting the model job, including texture or
segmentation references, and pass its printed `signed_url` to the corresponding image
flag:

```sh
python3 "<resolved absolute plugin root>/scripts/model3d_generation_tool.py" image-to-url --image-path "<authorized local image>"
```

On Windows use the documented interpreter rules below. Reference conversion is not
model generation and must not be used to upload unrelated files.

Preserve an authorized non-GLB source in its actual supported native format, including
required sidecars, with path/format/hash provenance. A conversion, when necessary,
produces a separate GLB and records both source and output; it never overwrites or
renames the original. The local GLB inspector cannot validate FBX/OBJ/STL/GLTF input:
use a suitable local reader before preflight. The accepted processed result is GLB.

## Generate

Choose exactly one input mode:

- Text: `--description` with a literal prompt describing the subject, shape, material, and style.
- Single image: `--image-url` with one public URL reachable by the service.
- Multiview: `--multiview` with `--front-url` and at least one of `--left-url`, `--back-url`, or `--right-url` (2–4 views of the same object), with consistent viewpoint labels and lighting.

Choose `--model v3.1`, `v3.0`, `v2.5`, `p1`, or `p2` explicitly. Use `v3.1` as the
default when no specific version is needed. Part generation requires v3.1. Use a
processing operation for an existing model instead of silently regenerating it.

P-series targets low-poly output: `p1` supports 50–20,000 faces; `p2` supports
48–50,000 faces, or 48–25,000 with quad output. `--quad` requires an explicit P2 model;
when `--face-limit` is supplied with P2 quad output it must be 48–25,000. P-series does
not support generate_parts, smart_low_poly, or geometry_quality. Add a positive
`--face-limit N` for the requested target and `--no-texture` only for bare geometry.
Every face limit is a target, not a hard ceiling; inspect the delivered mesh before
claiming compliance with a strict budget.

For textured generation, `--texture-quality fast|standard|detailed|extreme` is generate
only. Its default `standard`; `detailed` is 4K and `extreme` is 8K. The native wrapper
selects the required v3.5 texture route for `fast` without changing the geometry model.
Omit texture-quality controls with `--no-texture`. `--generate-parts` is supported only on v3.1; it forces untextured, non-PBR editable parts and does not replace the segment task required by completion.

## Model tools

For `texture`, `segment`, and `decimate`, supply exactly one source: `--task-id` from a successful upstream model task, or `--model-url` with a public GLB/GLTF/FBX/OBJ/STL URL, at most 150 MB. Check the size before submission. Retain which operation produced each ID so the next operation receives a compatible result. `complete` instead uses a successful segment task ID as specified below. All four commands require `--output` with a distinct local `.glb` path that cannot overwrite the source or another operation output.

For independent outputs, texture, decimate, and segment may use the same successful generate task ID in parallel, each with its own output and log. Launch all workers before any watcher. When one operation needs another's result, wait for that result; completion consumes the successful segment task ID.

### Texture

Select v3.0 with `--model v3.0`, or v3.5 with `--model v3.5`; the script also accepts legacy `v2.5` when that version is required. Texture changes appearance while preserving source geometry.

Guidance is optional. When supplied, choose exactly one of these mutually exclusive modes:

- Text: `--prompt` with a style description; optional `--style-image-url` requires the prompt.
- Single image: `--image-url` as an alternative to text/style guidance.
- Four images: `--front-url`, `--left-url`, `--back-url`, and `--right-url`; all four are required. Four-view texture guidance differs from multiview generation, which accepts two to four views.

`--model-url` identifies the source mesh, while `--image-url` is texture guidance. `--no-delight` preserves reference-image lighting; pair it with `--model v3.5`. Delight control is v3.5-only and defaults to true there; the script does not select a model automatically when this flag is set.

Texture seed, per-part texturing, and texture-quality controls are not exposed by this subcommand. `--texture-quality` belongs to generate and `--part-names` belongs to complete. Report this limitation rather than implying an unsupported control was applied.

### Segment and complete

For geometric segmentation, use `--model v1.0`. For semantic segmentation and any of its controls, explicitly pass `--model v2.0` (Beta); flags alone do not select v2.0.

- `--granularity simple|balanced|detailed` selects segmentation granularity, with default `balanced`.
- `--no-split-by-connectivity` sets split_by_connectivity=false; its default is true.
- `--ref-image-url` supplies a public reference image. It overrides granularity and connectivity, so omit those two flags with it and explain the precedence if both approaches were requested.

To split and complete a model:

1. Run `segment` and watch it to success; a successful `segment` result is mandatory.
2. Read `upstream task_id:` from that operation's log and use the returned segment ID, not the source generation ID and not a model URL or local GLB.
3. Run `complete --task-id` with that segment ID and `--completion-mode ai_completion`, plus a distinct output and log, then watch it to completion.
4. Preserve both the segmented and completed files and their task/log provenance.

Reuse a suitable successful segment task when available; otherwise segment first. Neither command takes a text prompt. Use `--part-names` only with actual names from the segmentation and omit it for all parts. `ai_completion` is the default and generates missing regions; `quick_cap` closes holes. Completion's model override is `v1.0`.

### Decimate

Choose the algorithm before the target; a larger target does not auto-switch the model.

| Model | `--face-limit` for triangles | Behavior |
| --- | --- | --- |
| v2.0 (`--model v2.0`) | Optional; 500–20,000 when supplied | Smart low-poly/retopology; omit for adaptive reduction. |
| v1.0 (`--model v1.0`) | Required, positive integer up to 2,000,000 | Basic decimation; no v2.0 bake or part_names support. |

For example, a 50,000-triangle target uses `decimate --model v1.0 --face-limit 50000` with verified source and distinct output arguments. If v2.0 behavior is required above 20,000, report the tradeoff rather than silently switching algorithms.

Upstream v2.0 supports bake and part_names, but this wrapper does not expose them. `--part-names` belongs to complete only. There is no quad selector for decimate; `--quad` belongs to generate with explicit P2. Use triangle budgets for decimation.

A decimation face count is a target, not a hard ceiling. Inspect the delivered mesh's actual triangle count before claiming a strict budget; if it cannot be measured, report it as unverified. Generation and decimation ranges are distinct and must be validated before submission.

## Submit once and watch

Validate first, then invoke
`scripts/model3d_generation_launch.py <operation> ... --output <distinct-output.glb>`
once. Save the printed `Job log` and `Job PID file`; launch success is not generation
success. In a separate foreground tool call, invoke
`scripts/model3d_generation_watch.py --log-file <exact-log> --pid-file <exact-pid> --interval-seconds 60`.
Never combine launcher and watcher in one shell call.

The native generation-stage inactivity limit is 900 seconds since the last log update. Once the worker logs `download started: fetching generated media`, that inactivity limit no longer applies; process and terminal-result checks continue. There is no overall watcher timeout. The gateway generation request also has a fixed 900-second timeout, and neither limit is configurable through CLI arguments. Download I/O retains its separate tool-level limit.

For independent parallel operations, launch every worker before starting any watcher,
with a distinct output and log for each. If monitoring is interrupted, inspect the
original reports and resume only the watcher with the same interpreter, log, and PID.
Never submit a duplicate operation or switch provider because monitoring was
interrupted. If the worker exits without a terminal result, establish the original
request's outcome from its log before any separately authorized new operation.

On Windows, launch both scripts directly with native `pythonw.exe`, not through a
wrapper. Do not invoke them through `python.exe`, `python3`, `py.exe`, or a wrapper that
later starts pythonw; the launcher uses `sys.executable`, keeping its worker windowless.
Prefer a valid runtime-provided `model3d_pythonw`. Otherwise run
`scripts/resolve_model3d_pythonw.ps1` once with the plugin root, optional candidate, and
a unique absolute resolver report. Use only its reported `Resolved pythonw:` path.
`MODEL3D_PYTHONW_NOT_FOUND` blocks worker start; never fall back to console Python.
Reuse the validated path for parallel jobs and resumed watchers.

Redirect launcher and watcher streams to a unique report for each call because pythonw
may not have usable standard streams. The runner must wait for pythonw and preserve its
exit status. Keep launch and watch as separate foreground calls and restore the absolute
plugin root and interpreter in each independent shell call.

## Delivery and provenance

The native scripts print `upstream task_id:` before downloading files. Recover and
retain that ID from the original log even if a later download fails; the script does not
create `model.task.json`. Confirm the actual saved `.glb` path. For generation, retain it
as `raw_path`; after successful local structural inspection, the same newly created GLB
may be `accepted_glb_path`. Record provider `tripo`, Tripo API attribution, actual
operation and model, task ID, output, and log in project asset notes.

Preview status is independent: `available` only after the log confirms download and the
file exists, `unavailable` when none is returned, and `failed` when its download fails.
Display an available preview with the host's media reader only after those checks. A
saved valid model remains successful without a preview or after preview failure; never
resubmit for one. The watcher can detect the saved-model marker before preview download
finishes. Provider preview and GLB remain source/design artifacts, not Godot evidence.

Classify failures from the response body and submitted parameters, not HTTP status
alone. Pending jobs resume through the same log/PID. Correct invalid parameters before
any separately authorized new request. A 429 rejection waits for capacity and requires
user consent for its native retry; no automatic retry or provider switch is permitted.
Final delivery must name Tripo API and the actual generated model or processed
operation, without claiming output from a failed attempt.
