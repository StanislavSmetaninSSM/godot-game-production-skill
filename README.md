# Godot Game Production

`godot-game-production` is a Codex skill for creating, continuing, repairing, and broadly developing Godot 2D, 2.5D, and 3D games. It coordinates game intent, visual direction, mechanics, production evidence, and release decisions; it is not intended for a single isolated asset or a narrow audit.

## What the skill enforces

The workflow moves through `AUDIT -> SPECIFY -> VISUAL_PENDING -> VISUAL_APPROVED -> GODOT_FEASIBILITY -> CORE_LOOP -> PRODUCTION -> RELEASE`.

Before material production, it freezes a coverage matrix, generates a target-gameplay screenshot pack, records each approved target with a stable ID, SHA-256 hash, and project-relative path, and asks for exact approval. It then requires a buildable Godot implementation and evidence for the causal core loop before multiplying content. It routes into 2D, 3D, procedural-art, evidence-ledger, and release-check references only when they apply.

Important: screenshots are design evidence only. They never prove mechanics. Mechanics require evidence from the target Godot build that shows the input, state change, and outcome, with filmstrip or video evidence where the skill calls for it.

No showcase game, sample project, templates, or Godot assets are bundled in this repository.

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

The commands below leave the working installation untouched until a staged download passes Codex's validator. If moving the current installation to its backup fails, the command stops before changing the target. If replacement or final validation fails, the confirmed backup is restored and the failed candidate is retained alongside it for inspection.

### Windows (PowerShell)

```powershell
$ErrorActionPreference = 'Stop'
$repositoryUrl = 'https://github.com/StanislavSmetaninSSM/godot-game-production-skill.git'
$codexHome = if ($env:CODEX_HOME) { $env:CODEX_HOME } else { Join-Path $HOME '.codex' }
$skillsRoot = Join-Path $codexHome 'skills'
$target = Join-Path $skillsRoot 'godot-game-production'
$stagingRoot = Join-Path ([System.IO.Path]::GetTempPath()) ('godot-game-production-stage-' + [guid]::NewGuid())
$backup = Join-Path $skillsRoot ('godot-game-production.backup-' + [guid]::NewGuid())
$failedCandidate = Join-Path $skillsRoot ('godot-game-production.failed-' + [guid]::NewGuid())
$validator = Join-Path $codexHome 'skills\.system\skill-creator\scripts\quick_validate.py'
$backupCreated = $false

try {
  git clone --depth 1 $repositoryUrl $stagingRoot
  & python $validator (Join-Path $stagingRoot 'godot-game-production')
  if ($LASTEXITCODE -ne 0) { throw 'Staged skill failed Codex validation.' }

  New-Item -ItemType Directory -Force -Path $skillsRoot | Out-Null
  if (Test-Path -LiteralPath $target) {
    Move-Item -LiteralPath $target -Destination $backup
    $backupCreated = $true
  }

  Move-Item -LiteralPath (Join-Path $stagingRoot 'godot-game-production') -Destination $target
  & python $validator $target
  if ($LASTEXITCODE -ne 0) { throw 'Replacement skill failed final Codex validation.' }

  if ($backupCreated) { Remove-Item -Recurse -Force -LiteralPath $backup }
} catch {
  if ($backupCreated -and (Test-Path -LiteralPath $backup)) {
    if (Test-Path -LiteralPath $target) { Move-Item -LiteralPath $target -Destination $failedCandidate }
    Move-Item -LiteralPath $backup -Destination $target
  }
  throw
} finally {
  if (Test-Path -LiteralPath $stagingRoot) { Remove-Item -Recurse -Force -LiteralPath $stagingRoot }
}
```

### macOS and Linux (shell)

```sh
set -eu
repository_url='https://github.com/StanislavSmetaninSSM/godot-game-production-skill.git'
codex_home="${CODEX_HOME:-$HOME/.codex}"
skills_root="$codex_home/skills"
target="$skills_root/godot-game-production"
staging_root="$(mktemp -d)"
backup="$skills_root/godot-game-production.backup-$(date +%s)"
failed_candidate="$skills_root/godot-game-production.failed-$(date +%s)"
validator="$codex_home/skills/.system/skill-creator/scripts/quick_validate.py"
backup_created=false

rollback() {
  if [ "$backup_created" = true ] && [ -d "$backup" ]; then
    if [ -e "$target" ]; then mv "$target" "$failed_candidate"; fi
    mv "$backup" "$target"
  fi
}
cleanup() { rm -rf "$staging_root"; }
trap 'rollback; cleanup' EXIT HUP INT TERM

git clone --depth 1 "$repository_url" "$staging_root/repository"
python3 "$validator" "$staging_root/repository/godot-game-production"
mkdir -p "$skills_root"
if [ -e "$target" ]; then
  mv "$target" "$backup"
  backup_created=true
fi
mv "$staging_root/repository/godot-game-production" "$target"
python3 "$validator" "$target"

if [ "$backup_created" = true ]; then rm -rf "$backup"; fi
trap - EXIT HUP INT TERM
cleanup
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
