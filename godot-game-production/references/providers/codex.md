<!-- provider-kind: image -->
# Codex image provider

Prepared provider adapter for the Codex runtime. It implements the neutral contract
in `references/image-generation.md` through the built-in `imagegen` capability and
never weakens the portable authorization and evidence gates. It does not require
Kimi skills, scripts, credentials, or launcher processes.

## Native capability and preflight

Before generation, confirm native Codex `imagegen` availability and validate the
neutral request, provider-supported prompt/size/background constraints, relevant
reference inputs, and project-local output destination without generating. An
`unavailable` capability or invalid request returns neutral `status: failed` with a
concrete `error`; preflight failure consumes no reference result budget and makes no
generation request. Do not fall back to another provider.

For reference work, verify that the immutable authorization is `AUTHORIZED` and that
the request carries its exact `authorization_id`, decision, and slot binding. Convert
one authorized reference slot into exactly one generation request and no more than
one authorized result. Production assets remain within the approved direction and
task budget without invented reference authorization.

## Invoke and monitor the same request

Use native Codex `imagegen` invocation for the authorized request and retain the
available provider/job identity. Monitor that same operation through interruption or
an uncertain monitoring result. Never infer terminal provider failure merely from a
monitoring interruption, and never launch a duplicate while the outcome is
unresolved. After generator invocation there is **no automatic retry** and **no
provider switch**. A definite technical failure follows the neutral contract's new
decision ID, complete affected-batch approval, and fresh authorization procedure.

## Normalize and bind the result

Return `status`, `provider_id`, `job_id`, `raw_path`, `accepted_png_path`,
`media_type`, and `error` truthfully:

- `succeeded` requires an actual readable returned file and a readable project-local
  accepted PNG;
- `failed` records a concrete terminal provider failure;
- `unknown` records why the invoked operation remains unresolved;
- an `unavailable` provider or a `malformed`, missing, unreadable, or unverified
  result fails closed.

Failed, unknown, unavailable, and malformed outcomes cannot enter subsequent visual
evidence or receive target approval. Only `succeeded` with a readable project-local
accepted PNG and the existing authorization, exact-slot, complete-batch, and SHA-256
bindings may enter subsequent visual evidence and Godot evidence steps.

Preserve the raw file and its observed media type; never infer the type solely from
an extension. When conversion is needed, create a separate project-local PNG, verify
readability and media type, record both paths and the conversion, and display and
hash the accepted PNG rather than disguising the raw output. Do not fabricate a path
or bitmap after failure or an unknown outcome. Partial batches cannot receive target
approval, and provider details never redefine `visual-decision/v2`,
`visual-generation-authorization/v1`, `evidence-run/v2`, or stored `imagegen_target`.
