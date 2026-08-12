# Active Context

<!-- Update this at the end of every session. This is the first thing to read when resuming. -->

## Current focus

Session complete. Cline template improvements are done on `feature/cline-template-improvements`: renamed `templates/cline-templates/` → `templates/cline/` (`a30d6d6`), wired the `CHANGELOG.md` skeleton into `agents/cline.json` `base_files` so every project gets a Keep-a-Changelog file (`8d4b907`), clarified the prompt-step copy, added agent-config integrity tests, and regenerated `CHANGELOG.md` from commit history (`d7d133e`). The branch is ready for review/merge.

## Recent decisions

- Renamed the Cline template folder from `cline-templates/` to `cline/` so it matches the agent name in `agents/cline.json` and stays consistent with the future `claude-code-templates/` pattern.
- `CHANGELOG.md` is a **base file** (copied verbatim from `project-specific-template/CHANGELOG.md`), not a project-specific file — the `/commit` workflow regenerates it from conventional-commit history; users never hand-edit it.
- The prompt step now tells users which files are deployed automatically (base rules, workflows, memory-bank skeletons, CHANGELOG, `.gitignore`/`.clineignore`) so they only paste the four project-specific files.
- Added agent-config integrity tests in `tests/test_agent_loader.py` that load the real `agents/*.json` files and fail if a `base_files` source doesn't resolve or a `project_specific_files` key lacks a `file_descriptions` entry. These would have caught the missing CHANGELOG wiring.
- Earlier design-system decisions (theme.py, components.py, shared footer, live conflict decisions, theme-toggle persistence) remain unchanged and in effect.

## Blockers / open questions

- **Flaky Tk test on this machine:** `tests/test_main_window.py::test_content_persists_when_navigating_back_to_prompt` intermittently fails with `_tkinter.TclError` (e.g. "Can't find a usable tk.tcl", "invalid command name tcl_findLibrary"). This is a Python 3.14 Tk installation issue, not a code regression — it passed in a full run and no Tk/init code changed. Not committed as a failing test knowingly; left as-is per 03-testing.md.

## Next step

Wire `config/settings.py` into the UI so the app remembers last-used folder/repo/agent and per-agent base template paths. After that, consider adding a Claude Code agent config as a second agent.
