# Active Context

<!-- Update this at the end of every session. This is the first thing to read when resuming. -->

## Current focus

The wizard flow is now: source → agent → prompt (new) → content → conflicts → summary. The prompt step shows the agent's `prompt.md` template with a Copy button so users can generate project-specific file contents in Claude. Implemented on `feature/prompt-step` (943fcc0).

## Recent decisions

- Chose to keep `file_deployer.py` as the ONLY module that writes into the target project, per architecture.md.
- Conflict resolution is pure decision logic in `conflict_resolver.py`; the UI layer prompts the user and records choices (overwrite/skip/merge) — never auto-decides.
- `agents/*.json` defines the file mapping (base_files + project_specific_files) so adding a new agent requires no core/UI changes.
- Created `templates/cline-templates/.clinerules-base/` (01-06 rule files) because the template README referenced it but it didn't exist yet.
- Added a prompt step between agent selection and content input; the prompt is loaded from `<base_template_path>/prompt.md` via `agent_loader.load_prompt()`.

## Blockers / open questions

- None blocking. Note: `config/settings.py` exists but is not yet wired into the UI (last-used paths / per-agent base template paths are not yet remembered between runs).

## Next step

Wire `config/settings.py` into the UI so the app remembers last-used folder/repo/agent and per-agent base template paths. After that, consider adding a Claude Code agent config as a second agent.
