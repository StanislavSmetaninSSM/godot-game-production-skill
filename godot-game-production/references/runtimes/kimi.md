# Kimi runtime adapter

Use this adapter when the portable Godot production workflow runs in Kimi Work. The
portable approval, authorization, evidence, and review gates remain authoritative;
this document only maps host capabilities.

Resolve **skill root** as the directory containing the loaded `godot-game-production`
`SKILL.md`. The commands below run with that directory as cwd; `scripts/` is directly
inside it. From another cwd, use the equivalent absolute script path beneath that
resolved skill root and quote it. `<project-root>` is the separate existing absolute
Godot project directory; quote it when it contains spaces. Read `adapter_path` relative
to skill root, never project root. Repository checkout examples in README.md explicitly
use the repository root, one directory above this installed-package layout.

## Native workflow capabilities

Invoke capabilities through Kimi's native `Skill` mechanism using these exact names:

| Portable capability | Kimi skill |
| --- | --- |
| Creative definition and behavior changes | `superpowers:brainstorming` |
| Spec Kit and Superpowers coordination | `spec-kit-superpowers-bridge` |
| Behavior implementation | `superpowers:test-driven-development` |
| Defect investigation | `superpowers:systematic-debugging` |
| Independent review | `superpowers:requesting-code-review` |
| Completion checks | `superpowers:verification-before-completion` |
| Prepared Kimi image generation | `image_generation:image_generation` |

Load the applicable skill for the current phase rather than substituting a similarly
named host command. A missing required capability is a blocker to report, not
permission to bypass the corresponding production gate.

## Select and read the image provider

Before any image generation, read `references/image-generation.md`, then resolve the
provider from the skill root and current Godot project root:

```sh
python scripts/image_provider.py resolve --runtime kimi --project-root "<project-root>"
```

Resolution selects an adapter only; it does not generate an image. A nonzero exit or
invalid resolution blocks generation. Read the returned skill-relative `adapter_path`
and follow that adapter. With the prepared Kimi default, the adapter is
`references/providers/kimi.md`, which invokes `image_generation:image_generation`.
Do not silently substitute another provider when resolution or adapter preflight
fails.

For reference work, invoke the selected provider only after the existing immutable
authorization says `AUTHORIZED`, and preserve its exact slot and result budget.
Production assets retain the portable autonomous-authoring boundary.

## Display actual accepted results

Use `ReadMediaFile` on every actual accepted bitmap path returned by the adapter.
For references, display the complete authorized candidate batch before the existing
target-approval question. A launch message, job ID, URL, prose description, or raw
unverified download is not display of an accepted bitmap. If the adapter created a
separate project-local PNG, display and hash that accepted PNG while retaining the
raw file and conversion record.

The runtime guide intentionally relies only on public Kimi capabilities and the
current installation's own skill discovery. It does not require a particular local
user directory, plugin installation path, credential value, or machine-wide workflow
configuration.

## Select and invoke the model provider

Before any 3D model generation or processing, read `references/model-generation.md`,
then resolve the model provider separately from the image provider:

```sh
python scripts/model_provider.py resolve --runtime kimi --project-root "<project-root>"
```

Kimi host default is `tripo`; explicit current-user or persisted project selection still
takes precedence according to the neutral contract. A nonzero exit or invalid resolution
blocks native invocation without fallback. Read the returned skill-relative
`adapter_path` and follow that adapter.

For the prepared provider, invoke `model3d_generation:model3d_generation` through
Kimi's native `Skill` mechanism. Resolve the actual plugin root from that loaded skill's
actual location as the adapter specifies; never hard-code a user directory or substitute
another capability. Provider prerequisites and credentials remain
external. Resolver success is not a credential, availability, generation, or upload
check.

Use `ReadMediaFile` for a model preview only when the adapter confirms its download and
the file exists. A provider preview, GLB path, or upstream task ID is not Godot import,
runtime, independent-review, or gameplay evidence.
