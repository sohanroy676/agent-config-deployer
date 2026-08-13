# Active Context

<!-- Update this at the end of every session. This is the first thing to read when resuming. -->

## Current focus

Session complete. CI + ADR + pre-deploy checklist deployment is done on `feature/ci-adr-deploy-templates`: the new `ci-template/` (`.github/workflows/ci.yml` + `dependabot.yml`), `docs-adr-template/` (`docs/adr/`), and `PRE-DEPLOY-CHECKLIST.md` are wired into the Cline agent's `base_files` so they deploy automatically. The Python CI workflow was rewritten to be configurable (matrix for OS/Python version, env vars for install/lint/format/test commands, secret-scan toggle) and extensible. All 66 tests pass; ruff + black clean. Branch is ready for review/merge.

## Recent decisions

- The CI workflow (`ci-template/.github/workflows/ci.yml`) is a **configurable base file**: users edit a single CONFIG section (matrix for `os`/`python-version`, `env` vars for `INSTALL_CMD`/`LINT_CMD`/`FORMAT_CMD`/`TEST_CMD`, `RUN_SECRET_SCAN` toggle) rather than hunting through `# --- CUSTOMIZE ---` comments. It's extensible by adding steps/jobs.
- `ci-template/.github/` (workflow + dependabot), `docs-adr-template/*.md` (→ `docs/adr/`), and `PRE-DEPLOY-CHECKLIST.md` (project root) are all **base files** — deployed automatically, with conflicts still prompted per file.
- The PromptStep description now lists CI workflows, ADR templates, and the pre-deploy checklist among the automatically-deployed files.
- Earlier decisions (ROADMAP optional deploy, memory-bank deployment targets, design system, CHANGELOG as base file, agent integrity tests) remain in effect.

## Blockers / open questions

- None blocking. (Known environmental flake: the Tk regression test can intermittently fail on this machine with `_tkinter.TclError` — Python 3.14 Tk install issue, not a code regression.)

## Next step

Wire `config/settings.py` into the UI so the app remembers last-used folder/repo/agent and per-agent base template paths. After that, consider adding a Claude Code agent config as a second agent.

## Roadmap expansion

The ROADMAP was expanded with a full feature backlog across agent/template expansion, git/repo features, settings/UX polish, deployment/content, CI/CD templates, security/quality, integration/extensibility, and project self-improvement. Near-term priorities (Next): settings wiring, Claude Code agent, PyInstaller packaging, CI for this repo, and template variable substitution + final preview.
