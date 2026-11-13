# Godot Game Production

`godot-game-production` is a shared skill for Kimi Work and Codex for creating, continuing, repairing, and broadly developing Godot 2D, 2.5D, and 3D games. It coordinates game intent, visual direction, mechanics, production evidence, and release decisions; it is not intended for a single isolated asset or a narrow audit.

## What the skill enforces

The workflow moves through `AUDIT -> SPECIFY -> VISUAL_PENDING -> VISUAL_APPROVED -> GODOT_FEASIBILITY -> CORE_LOOP -> PRODUCTION -> RELEASE`.

Visual references are needs-derived rather than fixed in count. The user approves
the complete slot set before image generation through the selected image provider;
the deterministic command then issues an exact batch authorization; one authorized row budgets one generated result. Before generation, read
`godot-game-production/references/image-generation.md` and the selected provider's
adapter. A late visual delta repeats the decision and authorization flow, and a
correction needs fresh authorization; unauthorized raw output cannot enter verified evidence
as an approved reference or a release result as proof. During approval,
machine JSON stays in project files. Chat shows detailed, numbered image descriptions and approval questions in the user's language.

Explicit user delegation can authorize a distinct independent reviewer to approve
visual decisions. The evidence ledger preserves the real user instruction and
reviewer role, and binds the grant to the complete visual contract chain. Without
that delegation, the normal user approval flow remains required.

After visual target approval, the agent independently chooses suitable existing
assets, procedural/native authoring, the selected image provider, or a combination
for production art. It explicitly considers image generation for textures, sprites,
decals, and other bitmap assets through the neutral adapter, generates and refines
them without per-image approval, and checks their integration in Godot. A change to
the approved visual direction reopens reference approval; routine asset production
does not.

Important: screenshots are design evidence only. They never prove mechanics. Mechanics require evidence from the target Godot build that shows the input, state change, and outcome, with filmstrip or video evidence where the skill calls for it.

No showcase game, sample project, templates, or Godot assets are bundled in this repository.

For concurrent production work, the skill conditionally loads
`references/production-operations.md` to keep one authoritative owner per mutable
game fact, define measurable conflict-aware slices, and verify their integrated
candidate. A single bounded serial slice keeps the normal lighter routing.

Visual and motion diagnostics support both dimension families: comparable frame
captures, contact/pose/event measurements, and explicit coverage gaps. Production
checks include early exported-build capture, risky mechanic combinations, continuous
audio/performance runs, and bounded cold-player sessions. Agent completion does not
establish human enjoyment, pacing, replay value or native input quality.

## Prerequisites

- A supported host (Kimi Work or Codex) with skill loading enabled.
- Git and a Godot project appropriate to the work being requested.
- [GitHub Spec Kit](https://github.com/github/spec-kit) and [Superpowers](https://github.com/obra/superpowers) installed and available to the current host.
- The separately installed [`spec-kit-superpowers-bridge`](https://github.com/StanislavSmetaninSSM/spec-kit-superpowers-bridge) workflow available to the current host. The skill requires that named workflow: Spec Kit owns durable constitution, specification, plan, tasks, and consistency; Superpowers owns execution.
- An available image-generation capability and selected provider when the visual-contract gate is reached. Use `godot-game-production/references/image-generation.md` and the provider adapter for initial and material visual re-entry.
- Python 3.10+ for bundled diagnostic and validation scripts. Frame comparison
  requires Pillow and NumPy; motion and evidence checks use the standard library.

This repository supplies the `godot-game-production` skill only. It does not install or vendor any prerequisite.

## Installation

For a fresh install, use Codex's official skill installer. It downloads only the installable `godot-game-production` folder and refuses to overwrite an existing installation. Use the update procedure below when the skill is already installed.

### Windows (PowerShell)

```powershell
$codexHome = if ($env:CODEX_HOME) { $env:CODEX_HOME } else { Join-Path $HOME '.codex' }
$installer = Join-Path $codexHome 'skills\.system\skill-installer\scripts\install-skill-from-github.py'
& python $installer --repo StanislavSmetaninSSM/godot-game-production-skill --path godot-game-production
if ($LASTEXITCODE -ne 0) { throw 'Codex skill installation failed.' }
```

### macOS and Linux (shell)

```sh
codex_home="${CODEX_HOME:-$HOME/.codex}"
installer="$codex_home/skills/.system/skill-installer/scripts/install-skill-from-github.py"
python3 "$installer" --repo StanislavSmetaninSSM/godot-game-production-skill --path godot-game-production
```

Restart or reload Codex after installation if its current session does not discover the skill automatically.

## Kimi Work installation and invocation

1. Clone or download this repository and copy the same `godot-game-production/`
   folder into `~/.agents/skills/godot-game-production/` without renaming it. The
   installed entry point must be
   `~/.agents/skills/godot-game-production/SKILL.md` (a
   `godot-game-production/SKILL.md` path beneath the skills root), not a nested
   repository-folder duplicate.
2. Start a new session or reload skills so Kimi Work discovers the installation.
3. Invoke `$godot-game-production` for a broad Godot production task.

Kimi Work also needs the required Spec Kit, Superpowers, and bridge workflows. For
image generation, the installed `image_generation:image_generation` capability and
its credentials are prerequisites, not vendored secrets; this repository supplies
neither the capability nor API keys. The prepared Kimi provider is the host default,
and its adapter performs preflight before any generation.

## 3D model provider installation, selection, and artifacts

The portable 3D workflow is documented in
[`godot-game-production/references/model-generation.md`](godot-game-production/references/model-generation.md).
Its prepared Tripo adapter is
[`godot-game-production/references/model-providers/tripo.md`](godot-game-production/references/model-providers/tripo.md).
Python 3.10+ is sufficient for offline provider resolution and GLB inspection; these
operations need no additional package, API key, or network access.

Actual generation and processing through the prepared `tripo` provider additionally
require the separately installed `model3d_generation:model3d_generation` capability,
its documented native launcher/watcher prerequisites, and Tripo API access with the
required credentials. Those native prerequisites and credentials are external and
**not vendored** by this repository. The adapter preflights their availability before
submission; resolving a provider does not check credentials or paid-service
availability.

### Select a model provider

Model-provider precedence is **explicit current-user choice → persisted project choice → host default**.
The Kimi host default is `tripo`. Codex has no model-provider default and therefore
requires an explicit or persisted project choice. Run these deterministic commands
from the repository checkout; replace the project-root `.` with the actual Godot
project root when it differs:

```sh
python godot-game-production/scripts/model_provider.py resolve --runtime kimi --project-root .
python godot-game-production/scripts/model_provider.py resolve --runtime codex --project-root . --provider tripo
```

To persist a project choice, create `docs/visual-contract/model-provider.json` beneath
the Godot project root with exactly these fields:

```json
{
  "schema_version": "model-provider-selection/v1",
  "provider_id": "tripo"
}
```

An explicit `--provider <provider-id>` overrides and bypasses persisted project
selection. Unknown, ambiguous, unavailable, malformed, or unsafe selections fail
closed with no automatic fallback to another model provider or to an image provider.
Model and image registries, selection files, resolver commands, and adapter documents
remain separate.

### Native operations and retained artifacts

The prepared adapter supports the five separately authorized operations `generate`,
`texture`, `segment`, `complete`, and `decimate`. Follow the prepared adapter for
native models, flags, source/task compatibility, launcher/watcher use, and limits;
this README intentionally does not duplicate all native flags. There is no common model-generation CLI:
the selected adapter owns native invocation.

Retain the raw model from generation and each distinct processed model output without
overwriting its source. Record provider, native model, operation, upstream task and
log identities, raw/processed paths and hashes, input references, and approved target
linkage as model provenance in project asset notes. Preview outcome is independent:
an unavailable or failed preview does not invalidate a saved valid model and never
causes duplicate generation.

Before Godot import, inspect the accepted local GLB from the repository checkout:

```sh
python godot-game-production/scripts/model_artifact.py inspect --project-root "<project-root>" --model "<portable-relative.glb>"
```

The inspector checks safe local containment, GLB 2.0 structure, mesh primitives,
SHA-256, and triangle-count status. It does not prove visual quality, scale, pivot,
materials, rigging, animation, Godot import success, consuming-scene behavior, or
gameplay evidence; the existing Godot and independent-review gates remain mandatory.

A custom generator follows the neutral contract with exactly two integration
artifacts: one model-registry entry and one neutral adapter document. It does not
change image-provider configuration or portable visual approval, and a hypothetical
test provider is not added to the prepared production registry.

**Live provider testing is not part of the default validation.** The deterministic
suites use local fixtures and do not upload references, submit jobs, download
previews, or contact Tripo API. Real generation, processing, upload, watcher, preview
download, or other live/billable provider testing requires separate explicit authorization
and the native prerequisites above. Local resolution and GLB inspection
remain offline and do not establish live-provider success.

## Image provider selection and configuration

Provider precedence is **explicit current-user choice → persisted project choice → host default**.
The Kimi host default is `kimi`; the Codex host default is `codex`.
The resolver only selects and validates the adapter: it performs no generation or provider availability check.
The selected adapter performs its own preflight before generation.

To persist a project choice, create the optional
`docs/visual-contract/image-provider.json` beneath the project root. Its schema is
`image-provider-selection/v1`, with exactly `schema_version` and `provider_id` fields; the prepared provider IDs are `kimi` and `codex`.

```json
{
  "schema_version": "image-provider-selection/v1",
  "provider_id": "kimi"
}
```

Run these commands from the repository checkout to resolve the host defaults without
generating images:

```sh
python godot-game-production/scripts/image_provider.py resolve --runtime kimi --project-root .
python godot-game-production/scripts/image_provider.py resolve --runtime codex --project-root .
```

An explicit current-user choice overrides both lower-precedence sources:

```sh
python godot-game-production/scripts/image_provider.py resolve --runtime kimi --project-root . --provider codex
```

The override bypasses project configuration, including malformed persisted configuration.
For an unknown, ambiguous, or unavailable selection, no fallback occurs.
Selection and extension failures fail closed as specified in
`godot-game-production/references/image-generation.md`; adding a custom provider does
not change the portable visual-approval sequence.

## Safe updates

The commands below leave the working installation untouched until an official-installer download passes Codex's validator in a unique transaction directory under the skills root. If moving the current installation to its backup fails, the command stops before changing the target. If replacement or final validation fails, rollback prioritizes restoring the confirmed backup; the failed replacement may be discarded.

### Windows (PowerShell)

```powershell
$ErrorActionPreference = 'Stop'
$codexHome = if ($env:CODEX_HOME) { $env:CODEX_HOME } else { Join-Path $HOME '.codex' }
$skillsRoot = Join-Path $codexHome 'skills'
$target = Join-Path $skillsRoot 'godot-game-production'
$transactionRoot = Join-Path $skillsRoot ('.godot-game-production-update-' + [guid]::NewGuid())
$stagingRoot = Join-Path $transactionRoot 'staging'
$backup = Join-Path $transactionRoot 'backup'
$installer = Join-Path $codexHome 'skills\.system\skill-installer\scripts\install-skill-from-github.py'
$validator = Join-Path $codexHome 'skills\.system\skill-creator\scripts\quick_validate.py'

New-Item -ItemType Directory -Force -Path $skillsRoot | Out-Null
if (Test-Path -LiteralPath $transactionRoot) { throw "Transaction path already exists: $transactionRoot" }
New-Item -ItemType Directory -Path $transactionRoot | Out-Null

function Write-ManualRecovery {
  Write-Warning "Manual recovery: after inspecting '$target', move '$backup' to '$target'."
}

function Restore-Backup {
  if (-not (Test-Path -LiteralPath $backup)) { return }
  if (Test-Path -LiteralPath $target) {
    try {
      Remove-Item -Recurse -Force -LiteralPath $target
    } catch {
      Write-Warning "Rollback could not remove failed replacement '$target': $($_.Exception.Message)"
      Write-ManualRecovery
      return
    }
  }
  try {
    Move-Item -LiteralPath $backup -Destination $target
  } catch {
    Write-Warning "Rollback could not restore backup '$backup': $($_.Exception.Message)"
    Write-ManualRecovery
  }
}

try {
  & python $installer --repo StanislavSmetaninSSM/godot-game-production-skill --path godot-game-production --dest $stagingRoot
  if ($LASTEXITCODE -ne 0) { throw 'Staged Codex installer download failed.' }
  & python $validator (Join-Path $stagingRoot 'godot-game-production')
  if ($LASTEXITCODE -ne 0) { throw 'Staged skill failed Codex validation.' }

  if (Test-Path -LiteralPath $target) {
    Move-Item -LiteralPath $target -Destination $backup
  }

  Move-Item -LiteralPath (Join-Path $stagingRoot 'godot-game-production') -Destination $target
  & python $validator $target
  if ($LASTEXITCODE -ne 0) { throw 'Replacement skill failed final Codex validation.' }

  if (Test-Path -LiteralPath $backup) {
    Write-Host "Update succeeded. Previous version retained at $backup."
  } else {
    Write-Host "Update succeeded. Transaction directory retained at $transactionRoot."
  }
} catch {
  Restore-Backup
  throw
}
```

### macOS and Linux (shell)

```sh
set -u
codex_home="${CODEX_HOME:-$HOME/.codex}"
skills_root="$codex_home/skills"
target="$skills_root/godot-game-production"
installer="$codex_home/skills/.system/skill-installer/scripts/install-skill-from-github.py"
validator="$codex_home/skills/.system/skill-creator/scripts/quick_validate.py"

mkdir -p "$skills_root"
mkdir_status=$?
if [ "$mkdir_status" -ne 0 ]; then exit "$mkdir_status"; fi
transaction_root="$(mktemp -d "$skills_root/.godot-game-production-update.XXXXXX")"
transaction_status=$?
if [ "$transaction_status" -ne 0 ]; then exit "$transaction_status"; fi
staging_root="$transaction_root/staging"
backup="$transaction_root/backup"

manual_recovery() {
  printf >&2 'Manual recovery: after inspecting "%s", move "%s" to "%s".\n' "$target" "$backup" "$target"
}

restore_backup() {
  if [ -e "$backup" ] || [ -d "$backup" ]; then
    if [ -e "$target" ]; then
      rm -rf "$target"
      removal_status=$?
      if [ "$removal_status" -ne 0 ] || [ -e "$target" ]; then
        printf >&2 'Rollback could not remove failed replacement "%s"; backup remains at "%s".\n' "$target" "$backup"
        manual_recovery
        return
      fi
    fi
    mv "$backup" "$target"
    restore_status=$?
    if [ "$restore_status" -ne 0 ]; then
      printf >&2 'Rollback could not restore backup "%s"; backup remains at "%s".\n' "$backup" "$backup"
      manual_recovery
    fi
  fi
}

on_exit() {
  status=$?
  trap - EXIT HUP INT TERM
  if [ "$status" -ne 0 ]; then restore_backup; fi
  exit "$status"
}

on_signal() {
  trap - HUP INT TERM
  exit "$1"
}

trap 'on_exit' EXIT
trap 'on_signal 129' HUP
trap 'on_signal 130' INT
trap 'on_signal 143' TERM

python3 "$installer" --repo StanislavSmetaninSSM/godot-game-production-skill --path godot-game-production --dest "$staging_root"
installer_status=$?
if [ "$installer_status" -ne 0 ]; then exit "$installer_status"; fi
python3 "$validator" "$staging_root/godot-game-production"
staged_validation_status=$?
if [ "$staged_validation_status" -ne 0 ]; then exit "$staged_validation_status"; fi
if [ -e "$target" ]; then
  mv "$target" "$backup"
  backup_status=$?
  if [ "$backup_status" -ne 0 ]; then exit "$backup_status"; fi
fi
mv "$staging_root/godot-game-production" "$target"
replacement_status=$?
if [ "$replacement_status" -ne 0 ]; then exit "$replacement_status"; fi
python3 "$validator" "$target"
final_validation_status=$?
if [ "$final_validation_status" -ne 0 ]; then exit "$final_validation_status"; fi

if [ -e "$backup" ] || [ -d "$backup" ]; then
  printf 'Update succeeded. Previous version retained at %s.\n' "$backup"
else
  printf 'Update succeeded. Transaction directory retained at %s.\n' "$transaction_root"
fi
trap - EXIT HUP INT TERM
exit 0
```

## Manual installation

1. Clone or download this repository.
2. Locate Codex's skills directory: `${CODEX_HOME}/skills` when `CODEX_HOME` is set, otherwise `~/.codex/skills`.
3. Copy this repository's `godot-game-production` directory into that skills directory without renaming it.
4. Restart or reload Codex.

The installed path must be `.../skills/godot-game-production/SKILL.md`.

## Invocation

Ask Codex to use `$godot-game-production` for a broad Godot game task, or describe a qualifying Godot 2D, 2.5D, or 3D production task and let Codex select the skill. The skill must use its required workflows before it changes creative behavior or implementation.

## Update and removal

Use the safe update procedure above to replace the installed copy with the latest repository version.

To remove it, delete only the installed `godot-game-production` directory from Codex's skills directory, then restart or reload Codex. Do not delete the repository clone unless you also intend to remove your local source checkout.

## Validation

From a checkout of this repository, run:

```powershell
$codexHome = if ($env:CODEX_HOME) { $env:CODEX_HOME } else { Join-Path $HOME '.codex' }
& python (Join-Path $codexHome 'skills\.system\skill-creator\scripts\quick_validate.py') godot-game-production
```

```sh
python3 "${CODEX_HOME:-$HOME/.codex}/skills/.system/skill-creator/scripts/quick_validate.py" godot-game-production
```

The expected result is `Skill is valid!`. This validates the skill's basic structure and metadata; it does not demonstrate a Godot game's mechanics or release readiness.

Run both executable suites from the repository root (Pillow and NumPy are required
for the frame-comparison tests). On Windows, use `python` in place of `python3`:

```sh
python3 -m unittest discover -s tests -v
python3 -m unittest discover -s godot-game-production/tests -v
```

The diagnostic command contracts and limits are documented in
[`quality-tools.md`](godot-game-production/references/quality-tools.md). The optional
delegation extension to `evidence-run/v2` requires the updated validator; existing
ledgers without that extension retain their original behavior.

## License

This project is released under the [Unlicense](LICENSE).

### Adapter kind and installed layout

Runtime guide commands run from the installed skill directory containing `SKILL.md`,
so their scripts are `scripts/image_provider.py`, `scripts/model_provider.py` and
`scripts/model_artifact.py`. The repository-root examples above deliberately include
the `godot-game-production/` prefix. Resolve absolute script paths from the loaded
skill when running from elsewhere, and keep the game project root explicit.

A custom model adapter begins with `<!-- provider-kind: model -->` on its first line.
Prepared image adapters declare `<!-- provider-kind: image -->`; legacy unmarked image
adapters remain supported. Conflicting, malformed or repeated declarations fail
closed. The marker belongs to the existing adapter document: a custom provider still
requires exactly its registry entry and adapter document, at any safe relative path.

The GLB inspector verifies bounded container/storage and supported byte-backed
triangle accounting. Unsupported external, sparse or compressed geometry yields
`triangle_count=null` / `unavailable`, never a fabricated budget claim. It is not a
full glTF validator and does not replace Godot import or runtime evidence. Original
non-GLB processing sources are preserved and hashed separately from converted GLB.
