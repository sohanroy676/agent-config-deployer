# Agent Config Deployer

A Windows desktop app that deploys coding-agent configuration templates (**Cline** and **Claude Code**) into a project folder — either an existing local folder or a freshly cloned public GitHub repo. It places base rule/workflow files and your project-specific files (`tech-stack.md`, `architecture.md`, `projectBrief.md`, plus `AGENTS.md` for Cline) into the correct structure automatically, so every project starts with a consistent, agent-ready setup.

Built with Python + CustomTkinter.

## Features

- **6-step wizard** — Source → Agent → Prompt → Content → Conflicts → Deploy, with a visual progress rail and a shared Back/Next footer.
- **Local folder or GitHub repo** — pick an existing folder, or provide a public repo URL and the app clones it into the folder for you.
- **Prompt step** — shows the agent's `prompt.md` template with a one-click copy, so you can generate project-specific content in Claude (or any AI chat).
- **Per-file content pages** — one page per project-specific file with a description, auto-saved as you navigate (no Save button).
- **Conflict resolution** — if target files/folders already exist, the app always asks you how to proceed (Overwrite / Skip / Merge) — it never decides for you.
- **CI + ADR + checklist deployment** — deploys a configurable GitHub Actions CI workflow (`.github/`), Architecture Decision Record templates (`docs/adr/`), and a pre-deploy checklist (`PRE-DEPLOY-CHECKLIST.md`) alongside the base rules.
- **Dark & light themes** — follows your system appearance, with a toggle in the header.
- **Extensible agents** — adding a new coding agent is just a new JSON config file; no app code changes needed.

## Requirements

- Windows 10/11
- Python 3.11+
- `git` CLI available on `PATH` (for cloning public repos)

## Installation

```bash
# 1. Create and activate a virtual environment
python -m venv venv
venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the app
python main.py
```

## Usage

1. **Project Source** — enter the folder path (the project folder, or the parent folder if cloning) and optionally a public GitHub repo URL.
2. **Select Agent** — choose the coding agent whose configuration you want to deploy (Cline for now).
3. **Generate Content** — copy the prompt, add your project details as instructed, paste it into Claude, and generate the project-specific files.
4. **Project-Specific Content** — paste the generated content into each file page. Content is saved automatically as you navigate.
5. **Resolve Conflicts** — review any existing files/folders that would be overwritten and choose Overwrite / Skip / Merge for each.
6. **Deploy** — the app copies the base template files and writes your project-specific content, then shows a summary of what was written and skipped.

## Project structure

```
agent-config-deployer/
├── main.py                  # entry point
├── ui/
│   ├── theme.py             # design system (colors, typography, widget factories)
│   ├── components.py        # reusable UI components (cards, badges, step rail, …)
│   ├── main_window.py       # app shell / wizard controller
│   └── wizard_steps.py      # the 6 step screens
├── core/
│   ├── git_handler.py       # clones public repos (only git operation in the app)
│   ├── agent_loader.py      # reads agents/*.json, exposes agents + prompt loading
│   ├── conflict_resolver.py # pure conflict decision logic (never writes files)
│   └── file_deployer.py     # the ONLY module that writes into the target project
├── agents/
│   ├── cline.json           # one config per coding agent
│   └── claude_code.json
├── config/
│   └── settings.py          # user settings persistence (last-used values, per-agent template paths)
├── templates/
│   ├── cline/               # base template files deployed into projects
│   └── claude-code/
├── tests/                   # pytest suite
└── requirements.txt
```

## Adding a new agent

1. Create `agents/<agent_name>.json` following the shape of `agents/cline.json`:

   ```json
   {
     "name": "My Agent",
     "version": "1.0.0",
     "base_template_path": "templates/my-agent",
     "structure": {
       "base_files": { "template-relative-source": "project-relative-destination" },
       "project_specific_files": { "filename": "project-relative-destination" },
       "file_descriptions": { "filename": "one-line description shown in the UI" }
     }
   }
   ```

2. Create the base template folder it points to (including a `prompt.md`).
3. Restart the app — the new agent appears in the Select Agent step. No core or UI code changes required.

## Development

```bash
# Run tests
pytest

# Lint
ruff check .

# Format
black .
```

## Roadmap

- [x] Remember last-used folder/repo/agent and per-agent base template paths (`config/settings.py`)
- [x] Claude Code agent config as a second agent
- [ ] PyInstaller packaging for a standalone `.exe`