# Codex runtime adapter

Use this adapter when the portable Godot production workflow runs in Codex. The
portable approval, authorization, evidence, and review gates remain authoritative;
this document only maps native Codex capabilities.

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
python godot-game-production/scripts/image_provider.py resolve --runtime codex --project-root <project-root>
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
