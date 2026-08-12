# Active Context

<!-- Update this at the end of every session. This is the first thing to read when resuming. -->

## Current focus

Session complete. ROADMAP + memory-bank deployment work is done on `feature/roadmap-memory-bank`: optional `ROADMAP.md` deploys at project root (project-specific page; blank content falls back to the blank template), `tech-stack.md`/`architecture.md` now deploy to `memory-bank/` instead of `.clinerules/`, the Cline template README + new-feature workflow are synced, and a real-`prompt.md` resolution guard was added. All 64 tests pass; ruff + black clean. Branch is ready for review/merge.

## Recent decisions

- `ROADMAP.md` is an **optional project-specific file deployed at the project root**. It's also a `base_files` entry so the blank template is always deployed; if the user leaves the ROADMAP content page blank (or whitespace-only), `deploy_project_specific_files` now skips non-blank writes, preserving the blank template.
- `tech-stack.md` and `architecture.md` now deploy to `memory-bank/` (alongside `projectBrief.md`) instead of `.clinerules/` — the root project already moved its own copies (`R .clinerules/architecture.md -> memory-bank/`).
- The prompt (`templates/cline/prompt.md`) asks the user whether to generate ROADMAP.md content before any other clarifying questions, honoring the optional nature.
- Template docs (`templates/cline/README.md`, `workflows/new-feature.md`) and the root `.clinerules/workflows/new-feature.md` all now reference `memory-bank/architecture.md` and `ROADMAP.md`.
- Added `memory-bank/ROADMAP.md` to this repo per the new-feature workflow (Now/Next/Later/Explicitly-not-planned); existing memory-bank docs were moved here from `.clinerules/`.
- Earlier decisions (design system, CHANGELOG as base file, agent integrity tests) remain in effect.

## Blockers / open questions

- None blocking. (Known environmental flake: the Tk regression test can intermittently fail on this machine with `_tkinter.TclError` — Python 3.14 Tk install issue, not a code regression.)

## Next step

Wire `config/settings.py` into the UI so the app remembers last-used folder/repo/agent and per-agent base template paths. After that, consider adding a Claude Code agent config as a second agent.
