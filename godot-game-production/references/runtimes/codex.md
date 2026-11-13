# Codex runtime adapter

Use this adapter when the portable Godot production workflow runs in Codex. The
portable approval, authorization, evidence, and review gates remain authoritative;
this document only maps native Codex capabilities.

Resolve **skill root** as the directory containing the loaded `godot-game-production`
`SKILL.md`. The commands below run with that directory as cwd; `scripts/` is directly
inside it. From another cwd, use the equivalent absolute script path beneath that
resolved skill root and quote it. `<project-root>` is the separate existing absolute
Godot project directory; quote it when it contains spaces. Read `adapter_path` relative
to skill root, never project root. Repository checkout examples in README.md explicitly
use the repository root, one directory above this installed-package layout.

## Native workflow capabilities

Invoke the shared workflow as `$godot-game-production`. Use the existing Codex skill
names for the applicable phase rather than renaming or bypassing a production gate:

| Portable capability | Codex skill |
| --- | --- |
| Creative definition and behavior changes | `brainstorming` |
| Spec Kit and Superpowers coordination | `spec-kit-superpowers-bridge` |
| Behavior implementation | `test-driven-development` |
| Defect investigation | `systematic-debugging` |
| Independent review | `requesting-code-review` |
| Completion checks | `verification-before-completion` |

A missing required native Codex capability is a blocker to report, not permission to
skip its corresponding visual or evidence gate.

## Select and read the image provider

Before any image generation, read `references/image-generation.md`, then resolve the
provider from the skill root and current Godot project root:

```sh
python scripts/image_provider.py resolve --runtime codex --project-root "<project-root>"
```

Resolution only selects an adapter; it performs no generation. A nonzero exit or
invalid resolution blocks generation. Read the returned skill-relative `adapter_path`
and follow that adapter. The prepared Codex default is `codex`, implemented by
`references/providers/codex.md` through the built-in `imagegen` capability. Do not
silently substitute another provider when selection or preflight fails.

For reference work, invoke the selected provider only after the immutable
authorization says `AUTHORIZED`, and preserve its exact slot, `authorization_id`, and
result budget. Production assets retain the portable autonomous-authoring boundary.

## Display actual accepted results

Use native Codex image display on every actual bitmap returned and accepted by the
adapter. For references, display the complete authorized candidate batch before the
existing target-approval question. A generation job identity, URL, prose description,
or unverified file is not display of an actual bitmap. If conversion produced a
separate project-local PNG, display and hash that accepted PNG while retaining the
raw file and conversion record.

The prepared Codex path needs no Kimi skill, script, credential, or launcher process.

## Select and invoke the model provider

Before any 3D model generation or processing, read `references/model-generation.md` and
resolve a model provider separately from the image provider:

```sh
python scripts/model_provider.py resolve --runtime codex --project-root "<project-root>"
```

Codex has no model-provider default. It requires explicit or persisted project selection;
without either, resolution fails closed and no fallback occurs. Read the returned
skill-relative `adapter_path` and satisfy that selected adapter's own native invocation
and prerequisites. Resolution performs no generation, upload, credential check, or
availability preflight.

The portable Codex route does not acquire a Kimi credential, native skill, launcher, or
script dependency merely by supporting model providers. If an explicitly selected
adapter itself needs a host-specific capability or credential, report that prerequisite
without silently substituting another provider. Provider previews and GLB files remain
source/design artifacts and never replace Godot evidence.
