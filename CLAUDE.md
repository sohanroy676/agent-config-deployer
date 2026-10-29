# Agent Config Deployer

Windows desktop app (Python 3.11+, CustomTkinter) that deploys coding-agent config templates (Cline today) into a project folder, either an existing local folder or a freshly cloned public GitHub repo. See `README.md` for features and usage.

This repo is developed with the same rules it deploys. The Cline setup (`.clinerules/`, `memory-bank/`) is the single source of truth and is imported below, so Cline and Claude Code share one set of rules. Edit the originals, not this file.

## Commands

- Run: `python main.py`
- Test: `pytest` (always run the full suite)
- Lint: `ruff check .`
- Format: `black .`

## Layout

- `core/`: pure logic, no UI. `file_deployer.py` is the ONLY module allowed to write into a target project.
- `ui/`: CustomTkinter wizard (`main_window.py` controller, `wizard_steps.py`, `theme.py`, `components.py`).
- `agents/*.json`: one config per coding agent. A new agent is a new JSON plus a template folder, with no core/UI changes.
- `templates/<agent>/`: the files that get deployed. This is product content, not rules for working on this repo. Do not confuse `templates/cline/.clinerules-base/` with the live `.clinerules/`.
- `config/settings.json` holds machine-local last-used values. Do not commit changes to it.

## Hard rules

- Never auto-decide file conflicts; always ask (Overwrite / Skip / Merge).
- No `shell=True` in subprocess calls; use argument lists.
- No secrets in source; use `.env` (gitignored).
- Tk tests can flake with `_tkinter.TclError` on this machine (Python 3.14 Tk install). Re-run before assuming a regression.

## Session start

Read `memory-bank/` first (imported below) to rebuild context. At the end of a session, update `memory-bank/progress.md` and `activeContext.md`.

## Workflows

Slash commands `/commit`, `/debug` and `/new-feature` in `.claude/commands/` run the matching files in `.clinerules/workflows/`.

## Rules (imported from `.clinerules/`)

@.clinerules/01-security.md
@.clinerules/02-commit-style.md
@.clinerules/03-testing.md
@.clinerules/04-code-quality-review.md
@.clinerules/05-git-workflow.md
@.clinerules/06-session-efficiency.md

## Project memory (imported from `memory-bank/`)

@memory-bank/projectBrief.md
@memory-bank/architecture.md
@memory-bank/systemPatterns.md
@memory-bank/tech-stack.md
@memory-bank/activeContext.md
@memory-bank/progress.md
@ROADMAP.md
