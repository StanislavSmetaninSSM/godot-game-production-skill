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
- GitHub Spec Kit and Superpowers installed and available to Codex.
- The `spec-kit-superpowers-bridge` workflow installed and available. The skill requires that named workflow: Spec Kit owns durable constitution, specification, plan, tasks, and consistency; Superpowers owns execution.
- An available image-generation capability when the visual-contract gate is reached; the skill uses Codex `imagegen` for initial and material visual re-entry.

This repository supplies the `godot-game-production` skill only. It does not install or vendor any prerequisite.

## Automated installation

After this repository is publicly available, use the commands below to download the current release and place its installable folder in Codex's skills directory. They replace an existing installation of this skill.

### Windows (PowerShell)

```powershell
$repositoryUrl = 'https://github.com/StanislavSmetaninSSM/godot-game-production-skill.git'
$skillRoot = if ($env:CODEX_HOME) { Join-Path $env:CODEX_HOME 'skills' } else { Join-Path $HOME '.codex\skills' }
$temporaryRoot = Join-Path ([System.IO.Path]::GetTempPath()) ('godot-game-production-skill-' + [guid]::NewGuid())
git clone --depth 1 $repositoryUrl $temporaryRoot
New-Item -ItemType Directory -Force -Path $skillRoot | Out-Null
Remove-Item -Recurse -Force -LiteralPath (Join-Path $skillRoot 'godot-game-production') -ErrorAction SilentlyContinue
Copy-Item -Recurse -LiteralPath (Join-Path $temporaryRoot 'godot-game-production') -Destination (Join-Path $skillRoot 'godot-game-production')
Remove-Item -Recurse -Force -LiteralPath $temporaryRoot
```

### macOS and Linux (shell)

```sh
repository_url='https://github.com/StanislavSmetaninSSM/godot-game-production-skill.git'
skill_root="${CODEX_HOME:-$HOME/.codex}/skills"
temporary_root="$(mktemp -d)"
git clone --depth 1 "$repository_url" "$temporary_root/repository"
mkdir -p "$skill_root"
rm -rf "$skill_root/godot-game-production"
cp -R "$temporary_root/repository/godot-game-production" "$skill_root/godot-game-production"
rm -rf "$temporary_root"
```

Restart or reload Codex after installation if its current session does not discover the skill automatically.

## Manual installation

1. Clone or download this repository.
2. Locate Codex's skills directory: `${CODEX_HOME}/skills` when `CODEX_HOME` is set, otherwise `~/.codex/skills`.
3. Copy this repository's `godot-game-production` directory into that skills directory without renaming it.
4. Restart or reload Codex.

The installed path must be `.../skills/godot-game-production/SKILL.md`.

## Invocation

Ask Codex to use `$godot-game-production` for a broad Godot game task, or describe a qualifying Godot 2D, 2.5D, or 3D production task and let Codex select the skill. The skill must use its required workflows before it changes creative behavior or implementation.

## Update and removal

Run the automated-installation command again to replace the installed copy with the latest repository version.

To remove it, delete only the installed `godot-game-production` directory from Codex's skills directory, then restart or reload Codex. Do not delete the repository clone unless you also intend to remove your local source checkout.

## Validation

From a checkout of this repository, run:

```powershell
python path/to/skill-creator/scripts/quick_validate.py godot-game-production
```

The expected result is `Skill is valid!`. This validates the skill's basic structure and metadata; it does not demonstrate a Godot game's mechanics or release readiness.

## License

This project is released under the [Unlicense](LICENSE).
