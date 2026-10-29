# Active Context

<!-- Update this at the end of every session. This is the first thing to read when resuming. -->

## Current focus

Session complete. Settings persistence is done on `feature/settings-persistence`: `config/settings.py` is wired into the UI — the app remembers the last-used folder/repo/agent and per-agent base template paths. The Source step prefills from saved values and persists on navigation; the Agent step prefills the last-used agent and gained a "Base template path" override field (with Browse); prompt loading and deployment resolve the effective base template path (user-configured override → agent default). `load_prompt()` accepts an optional override. All 72 tests pass; ruff + black clean. Branch `feature/settings-persistence` (commit `8291f1e`) is ready for review/merge.

## Recent decisions

- `config/settings.py` is now fully wired into the UI. `update_last_used()` persists folder/repo on Source-next and agent on Agent-next; `set_base_template_path()`/`clear_base_template_path()` manage per-agent template overrides; `MainWindow._effective_base_template_path()` resolves the path used for prompt loading and deployment (configured → agent default). The Agent step's "Base template path" field defaults to the agent config's path and is editable with a Browse button; saving an empty value clears the override.
- The CI workflow (`ci-template/.github/workflows/ci.yml`) is a **configurable base file**: users edit a single CONFIG section (matrix for `os`/`python-version`, `env` vars for `INSTALL_CMD`/`LINT_CMD`/`FORMAT_CMD`/`TEST_CMD`, `RUN_SECRET_SCAN` toggle) rather than hunting through `# --- CUSTOMIZE ---` comments. It's extensible by adding steps/jobs.
- `ci-template/.github/` (workflow + dependabot), `docs-adr-template/*.md` (→ `docs/adr/`), and `PRE-DEPLOY-CHECKLIST.md` (project root) are all **base files** — deployed automatically, with conflicts still prompted per file.
- The PromptStep description now lists CI workflows, ADR templates, and the pre-deploy checklist among the automatically-deployed files.
- Earlier decisions (ROADMAP optional deploy, memory-bank deployment targets, design system, CHANGELOG as base file, agent integrity tests) remain in effect.

## Blockers / open questions

- None blocking. (Known environmental flake: the Tk regression test can intermittently fail on this machine with `_tkinter.TclError` — Python 3.14 Tk install issue, not a code regression.)

## Next step

Claude Code agent is built on `feature/claude-code-agent` (79 tests pass, awaiting review/merge). After that: PyInstaller packaging, CI for this repo, and template variable substitution + final preview.

## Roadmap expansion

The ROADMAP was expanded with a full feature backlog across agent/template expansion, git/repo features, settings/UX polish, deployment/content, CI/CD templates, security/quality, integration/extensibility, and project self-improvement. Near-term priorities (Next): Claude Code agent, PyInstaller packaging, CI for this repo, and template variable substitution + final preview.

## Claude Code support (2026-10-29)

This repo's own dev setup now works with Claude Code too: `CLAUDE.md` imports the Cline rules/memory-bank, `.claude/commands/` wraps the workflows, `.claude/settings.json` holds permissions. The deployable side is still Cline-only: next is `agents/claude_code.json` + `templates/claude-code/` (CLAUDE.md template with @-imports, `.claude/commands`, `.claude/settings.json`), then verify the outer setup in a live Claude Code session.

## CI (2026-10-29)

CI for this repo is on `feature/repo-ci`; the roadmap is now a single root `ROADMAP.md`. Next: PyInstaller packaging, then template variables + file-tree preview.
