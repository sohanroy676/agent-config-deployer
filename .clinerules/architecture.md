# Architecture

## Folder structure

agent-config-deployer/
├── main.py
├── ui/
│ ├── main*window.py # app entry window / wizard controller
│ └── wizard_steps.py # step screens: source input, agent select, content input, conflict resolution, summary
├── core/
│ ├── git_handler.py # clones public repo into parent folder path
│ ├── file_deployer.py # copies base template + writes project-specific files into correct structure
│ └── conflict_resolver.py # detects existing files/folders, prompts user (ask each time)
├── agents/
│ ├── agent_loader.py # reads agent config JSONs, exposes available agents to UI
│ ├── cline.json # defines Cline's file/folder structure + base template location
│ └── claude_code.json # (future) same pattern for Claude Code
├── config/
│ └── settings.json # user-configured base template folder path(s), remembers last-used paths
├── tests/
│ └── test*\*.py
├── requirements.txt
└── README.md

## Data flow

1. User fills in: folder path, optional GitHub repo link, selects agent (e.g. Cline), provides project-specific file content (paste or file picker).
2. If repo link is filled → `git_handler.py` clones the repo into the given folder path (parent folder); resulting cloned folder becomes the project folder for the rest of the flow. If repo link is empty → folder path IS the project folder directly.
3. `agent_loader.py` reads the selected agent's JSON config to determine target folder/file structure and where the configured base template files live.
4. `conflict_resolver.py` checks the project folder for any existing files/folders that would be overwritten; if found, asks the user (overwrite/skip/merge) before proceeding — never auto-decides.
5. `file_deployer.py` copies the base template files into the project folder per the agent's structure, and writes the user-provided project-specific content (tech-stack.md, architecture.md, projectBrief.md, etc.) into the correct locations.
6. UI shows a summary of what was copied/skipped.

## Key modules and their responsibility

- `ui/`: wizard-style screens (source → agent → content → conflicts → summary), built with CustomTkinter.
- `core/git_handler.py`: handles cloning only; no other git operations.
- `core/file_deployer.py`: the only module that writes files into the target project — centralizes all file-copy logic.
- `core/conflict_resolver.py`: pure decision logic, always defers to user input, no silent overwrites.
- `agents/*.json`: one config file per coding agent, defining that agent's folder/file naming conventions and base template source path. Adding a new agent (e.g. Claude Code) means adding a new JSON file here — no changes to `core/` or `ui/` required.
- `config/settings.json`: stores user preferences (base template locations per agent, last-used folder paths) so the app remembers setup between runs.

## Third-party services/APIs used

- GitHub (public repo cloning only, via system `git` CLI) — no authentication/keys needed at this stage. Not applicable to `.env`/secrets since this is a local desktop tool with no credentials to store yet. If private-repo support is added later, any token/credential handling must go through Windows Credential Manager or a local `.env`-equivalent — never hardcoded in `agents/*.json` or source.
