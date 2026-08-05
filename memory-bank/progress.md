# Progress

<!-- Running log. Append, don't rewrite history. Newest at top. -->

## Done

- App skeleton (v1) — built the full wizard-style desktop app: `main.py`, `ui/` (main_window + wizard_steps), `core/` (git_handler, agent_loader, conflict_resolver, file_deployer), `config/` (settings), `agents/cline.json`, and pytest coverage (38 tests). Committed on `feature/app-skeleton` (c0d21d1). 2026-08-05
- Template base rules — created `templates/cline-templates/.clinerules-base/` (01-06 rule files) so the Cline template has the base rules the README references. 2026-08-05

## In progress

- (none)

## Not started / backlog

- Wire `config/settings.py` into the UI (remember last-used folder/repo/agent, per-agent base template paths)
- Add Claude Code agent config (`agents/claude_code.json`) as a second agent
- PyInstaller packaging to produce a standalone `.exe`
- README.md for the app itself
