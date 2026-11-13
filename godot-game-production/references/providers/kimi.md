<!-- provider-kind: image -->
# Kimi image provider

Prepared provider adapter for the Kimi runtime. It implements the neutral contract in
`references/image-generation.md`; it never weakens the portable authorization and
evidence gates.

## Native capability and preflight

Invoke the native skill `image_generation:image_generation`. Read its installed
`SKILL.md` to resolve the plugin root: it is two directories above the directory containing that skill file and
contains `kimi.plugin.json`. Use the resolved absolute path for every bundled script
invocation, including checks, uploads, launch, and monitoring.

Preflight dependencies and credentials **without generating**. The provider requires
the agent-gw Python SDK, version 0.2.6 or newer. Its documented dependency command is
`image_generation_tool.py ensure-deps`; follow the user's installation permissions
because that command can install or upgrade the SDK. Confirm an API key through the
provider-supported `api_key=...`, `KIMI_API_KEY`, or `~/.kimi/agent-gw.json` source.
Do not expose or vendor the credential. Use one Python interpreter for setup, launch,
and monitoring. On Windows, launch both `image_generation_launch.py` and
`image_generation_watch.py` directly with a validated native `pythonw.exe`, never an
outer console Python wrapper. Prefer the runtime-provided `image_pythonw`; if absent
or invalid, follow the loaded native skill's bundled interpreter resolver (currently
`scripts/resolve_image_powershell.sh`), using its absolute plugin-root path. Reuse that
validated interpreter for the job and resumed watchers. Do not guess interpreter paths.
Redirect both streams to unique launcher/watcher report files, explicitly wait for
pythonw to exit and retain its exit status. In PowerShell, use a waiting process
invocation with `-WindowStyle Hidden` and both streams redirected; a GUI executable
invocation alone does not guarantee waiting. These Windows rules supplement, rather
than replace, the installed native skill's current launch examples.

Before invocation, validate the neutral request, destination, provider availability,
and these constraints:

- width and height are positive multiples of 16, each at most 3840;
- aspect ratio is at most 3:1 and total pixels are 655,360–8,294,400;
- `background` is `opaque` or `transparent`, and transparent output requires PNG;
- the output destination is project-local and uses the provider-supported `.png`,
  `.jpg`, or `.jpeg` extension, with `.png` for transparency.

A preflight provider-unavailability failure returns neutral `status: failed` with a
concrete unavailable-provider `error`. Other preflight failures also return
`status: failed` with a concrete `error`. These outcomes occur before generator
invocation, consume no reference result budget, and produce no image request.
`unknown` is reserved for an unresolved invoked job, never for preflight
unavailability. Resolve the concrete blocker rather than switching providers.

## Authorized reference inputs

The gateway accepts reference images only as a public URL. For each relevant local
reference, use the provider's separate `image-to-url` conversion through
`image_generation_tool.py`, then pass the returned public URL with
`--reference-image`; repeat the flag for multiple references. The adapter uploads
only files belonging to the authorized work, never unrelated inputs. For an ordinary
production asset, the corresponding authorization is the already approved direction
and task scope; do not invent a reference `authorization_id`.

## Launch and monitor the same job

Translate one authorized neutral request into one native generation job. Generation
launcher `image_generation_launch.py` and watcher `image_generation_watch.py` are
separate operations. Run the launcher in its own quick-return call with a unique
output path, retain the printed job log and native PID-file paths, then run the
watcher in a separate foreground call with those exact paths. Do not combine worker
and watcher in one shell call or replace the printed native PID with shell `$!`.

**launch success is not generation success**. Only the watcher and actual saved,
verified output establish the material outcome. If monitoring is interrupted or times
out, resume only the watcher with the exact **same log and PID** paths. If the launch
itself is interrupted before paths return, inspect that launch's existing job files
and processes before any decision. Never infer upstream failure from watcher timeout;
an unresolved result is `unknown`, and recovery resumes observation of the same job.

Use bounded concurrency within the authorized batch and the provider's current limit
(the installed capability states at most 20 concurrent generations per user). Launch
concurrent jobs separately before watching them, with distinct output/log/PID paths.
When the bound is uncertain or the batch policy cannot be preserved, serial execution
is the safe fallback. Provider generic retry guidance is subordinate to this skill's
authorization gate: after generator invocation there is **no automatic retry** and
**no provider switch**. A definite technical failure follows the neutral contract's
new-decision, complete-batch approval, and fresh-authorization procedure.

## Normalize the result truthfully

Record the actual provider and available job identity and return the neutral result
fields `status`, `provider_id`, `job_id`, `raw_path`, `accepted_png_path`,
`media_type`, and `error`.

- `succeeded` requires an actual readable returned file and a readable project-local
  accepted PNG.
- `failed` records the concrete terminal provider/worker failure.
- `unknown` records why the existing job's outcome remains unresolved and retains its
  observation paths.
- An `unavailable` provider and a `malformed`, missing, or unreadable result fail
  closed. Failed, unknown, unavailable, and malformed outcomes cannot enter subsequent evidence steps and cannot receive target approval.

Preserve each returned **raw file** and its observed media type; never infer media
type solely from the filename extension. If the raw file is not PNG, create a
separate **project-local PNG**, verify its readability and media type, and record the
conversion in generation work notes. Hash and display the accepted PNG rather than
renaming or disguising the raw file. Keep the raw path and accepted PNG path distinct
in the neutral result and provenance notes.

After failure or an unknown outcome, make **no fabricated file/path** claim. Only `succeeded`
with a readable project-local accepted PNG may continue to the existing
authorization, exact-slot, batch-display, SHA-256, target-approval, and Godot evidence
steps. Provider and conversion details remain generation audit metadata; they do not
change the stored evidence schemas or the provider-neutral `imagegen_target` value.
