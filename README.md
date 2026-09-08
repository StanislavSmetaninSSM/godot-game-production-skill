# Godot Game Production

`godot-game-production` is a Codex skill for creating, continuing, repairing, and broadly developing Godot 2D, 2.5D, and 3D games. It coordinates game intent, visual direction, mechanics, production evidence, and release decisions; it is not intended for a single isolated asset or a narrow audit.

## What the skill enforces

The workflow moves through `AUDIT -> SPECIFY -> VISUAL_PENDING -> VISUAL_APPROVED -> GODOT_FEASIBILITY -> CORE_LOOP -> PRODUCTION -> RELEASE`.

Visual references are needs-derived rather than fixed in count. The user approves
the complete slot set before ImageGen; the deterministic command then issues an
exact batch authorization. One condition is that one authorized row budgets one generated result.
A late visual delta repeats the decision and authorization flow, and a correction needs fresh authorization.
The rule is that unauthorized raw output cannot enter verified evidence as an approved reference or a release result as proof.
During approval, machine JSON stays in project files. Chat shows detailed,
numbered image descriptions and approval questions in the user's language.

After visual target approval, the agent independently chooses suitable existing
assets, procedural/native authoring, ImageGen, or a combination for production
art. It explicitly considers ImageGen for textures, sprites, decals, and other
bitmap assets, generates and refines them without per-image approval, and checks
their integration in Godot. A change to the approved visual direction reopens
reference approval; routine asset production does not.

Important: screenshots are design evidence only. They never prove mechanics. Mechanics require evidence from the target Godot build that shows the input, state change, and outcome, with filmstrip or video evidence where the skill calls for it.

No showcase game, sample project, templates, or Godot assets are bundled in this repository.

For concurrent production work, the skill conditionally loads
`references/production-operations.md` to keep one authoritative owner per mutable
game fact, define measurable conflict-aware slices, and verify their integrated
candidate. A single bounded serial slice keeps the normal lighter routing.

## Prerequisites

- Codex with skill loading enabled.
- Git and a Godot project appropriate to the work being requested.
- [GitHub Spec Kit](https://github.com/github/spec-kit) and [Superpowers](https://github.com/obra/superpowers) installed and available to Codex.
- The separately installed [`spec-kit-superpowers-bridge`](https://github.com/StanislavSmetaninSSM/spec-kit-superpowers-bridge) workflow available to Codex. The skill requires that named workflow: Spec Kit owns durable constitution, specification, plan, tasks, and consistency; Superpowers owns execution.
- An available image-generation capability when the visual-contract gate is reached; the skill uses Codex `imagegen` for initial and material visual re-entry.

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

## License

This project is released under the [Unlicense](LICENSE).
