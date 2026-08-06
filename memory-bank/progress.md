# Progress

<!-- Running log. Append, don't rewrite history. Newest at top. -->

## Done

- Full UI/UX redesign — introduced a cohesive design system (`ui/theme.py` with dark/light palettes, type scale, radii, spacing, and widget factories) and reusable components (`ui/components.py`: cards, badges, inline notices, form fields with inline validation, step indicator rail, segmented conflict choices, loading/error/empty states). Rebuilt the app shell (`ui/main_window.py`) with a header (title, tagline, theme toggle, step rail) and a shared footer (context-aware Back/Next labels/state, refreshed after content-page navigation), plus redesigned all 6 wizard steps (`ui/wizard_steps.py`) with scrollable agent/conflict/summary cards and a pure `StepIndicatorState`. Theme toggling rebuilds the current step without losing wizard data. All 56 tests pass; `ruff` and `black` clean. Committed `16b2f39` on `feature/ui-redesign`. 2026-08-06
- Per-file content pages — replaced the single dropdown-based content step with one page per project-specific file. Each page shows the filename as a second heading plus a one-line description (from `agents/*.json` `file_descriptions`), and content auto-saves on navigation (no Save button). Extracted `ContentPageState` for testable navigation/save logic. Committed `174d13d` on `feature/per-file-content-pages`. 2026-08-05
- Prompt step — added a wizard step between agent selection and content input that shows the agent's `prompt.md` template with a Copy button, so users can paste it into Claude to generate project-specific file contents. Added `load_prompt()` to `agent_loader` and renumbered subsequent steps. Committed `943fcc0` on `feature/prompt-step`. 2026-08-05
- Fix: `TypeError: 'dict' object is not callable` on app startup — the wizard data dict was named `state`, shadowing Tk's `state()` method that CustomTkinter calls internally during `mainloop()`. Renamed to `wizard_state` and added a regression test (`tests/test_main_window.py`). Committed `ec366d9`. 2026-08-05
- App skeleton (v1) — built the full wizard-style desktop app: `main.py`, `ui/` (main_window + wizard_steps), `core/` (git_handler, agent_loader, conflict_resolver, file_deployer), `config/` (settings), `agents/cline.json`, and pytest coverage (38 tests). Committed on `feature/app-skeleton` (c0d21d1). 2026-08-05
- Template base rules — created `templates/cline-templates/.clinerules-base/` (01-06 rule files) so the Cline template has the base rules the README references. 2026-08-05

## In progress

- (none)

## Not started / backlog

- Wire `config/settings.py` into the UI (remember last-used folder/repo/agent, per-agent base template paths)
- Add Claude Code agent config (`agents/claude_code.json`) as a second agent
- PyInstaller packaging to produce a standalone `.exe`
- README.md for the app itself
