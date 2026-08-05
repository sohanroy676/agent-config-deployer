# Project Brief

## What is this project?

A Windows desktop app that deploys coding-agent configuration templates (starting with Cline) into a project folder — either an existing local folder or a freshly cloned public GitHub repo — placing base rule/workflow files and user-supplied project-specific files (tech-stack.md, architecture.md, projectBrief.md) into the correct structure automatically.

## Core goal / success criteria

- User can, in under a minute: pick a source (local folder path, or a folder path + GitHub repo link to clone), select a coding agent (Cline for v1), paste or select project-specific file content, and get all base + project-specific files correctly placed in the target project folder.
- For cline, the project-specific files are AGENTS.md, memory-bank/projectBrief.md, .clinerules/architecture.md, .clinerules/tech-stack.md
- If target files/folders already exist, the app always asks the user how to proceed (overwrite/skip/merge) rather than deciding automatically.
- Adding support for a new coding agent (e.g. Claude Code) requires only adding a new agent config file — no changes to core app logic.

## Out of scope (v1)

- Private GitHub repo support (auth/tokens) — public repos only for now.
- Non-Windows OS support.
- Deploying to multiple agents in a single run (one agent per run).
- Generating the project-specific file content itself — that stays a separate step done via a Claude chat prompt, this app only deploys already-written content.
