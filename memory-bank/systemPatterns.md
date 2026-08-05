# System Patterns

<!-- Fill in as patterns emerge, so every session follows the same conventions instead of inventing new ones. -->

## Naming conventions

- Python modules: `snake_case.py` (e.g. `git_handler.py`, `file_deployer.py`)
- Classes: `PascalCase` (e.g. `MainWindow`, `SourceStep`, `ConflictReport`)
- Functions/methods: `snake_case` (e.g. `deploy_base_files`, `detect_conflicts`)
- Test files: `tests/test_<module>.py` (e.g. `test_git_handler.py`), functions `test_*`
- Agent configs: `agents/<agent_name>.json` (e.g. `cline.json`)

## Folder structure logic

- `core/` — pure logic, no UI. `file_deployer.py` is the ONLY module that writes into the target project.
- `ui/` — CustomTkinter wizard screens; one class per step (`SourceStep`, `AgentStep`, `ContentStep`, `ConflictStep`, `SummaryStep`), wired together by `MainWindow` (the controller).
- `agents/*.json` — one config per coding agent; defines `base_files` and `project_specific_files` mappings (template-relative source → project-relative destination).
- `config/` — user settings persistence (`settings.json` + `settings.py` loader/saver).
- `tests/` — pytest, one file per core module.

## Common patterns used in this project

- Wizard flow: each step is a `ctk.CTkFrame` that receives an `on_next` callback; `MainWindow` holds shared `self.state` dict and swaps steps via `_clear()` + `_show_*_step()`.
- Conflict resolution: `conflict_resolver.py` is pure decision logic (dataclasses + functions), never writes files; the UI prompts the user and records choices via `record_decision()`.
- Error handling: custom exception classes per module (`GitCloneError`, `DeployError`, `AgentConfigError`) wrapping lower-level errors with `raise ... from exc`.
- Agent extensibility: adding a new agent = adding a new JSON in `agents/`; no core/UI changes required.

## Things to avoid

- Do NOT write files into the target project from anywhere except `core/file_deployer.py`.
- Do NOT auto-decide conflict outcomes — always ask the user (overwrite/skip/merge).
- Do NOT hardcode secrets; use `.env` (already in `.gitignore`).
- Do NOT use `shell=True` in subprocess calls (injection risk) — use argument lists.
