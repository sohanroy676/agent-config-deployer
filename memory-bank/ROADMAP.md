# Roadmap

<!-- Unversioned, priority-grouped planning. NOT a version map — version numbers
     are assigned at release time (see CHANGELOG.md), not here. This is just
     "what's the plan," so architecture decisions can account for what's coming
     without pre-committing to exact scope/order. -->

## Now

- (nothing active — UI redesign, Cline template improvements, ROADMAP/memory-bank deployment, and CI/ADR/checklist deployment are complete)

## Next

- Wire `config/settings.py` into the UI so the app remembers last-used folder/repo/agent and per-agent base template paths
- Add Claude Code agent config (`agents/claude_code.json`) as a second agent
- PyInstaller packaging to produce a standalone `.exe`
- Add CI for this repo (dogfood the CI template — run pytest/ruff/black on GitHub Actions)
- Template variable substitution (e.g. `{{PROJECT_NAME}}`, `{{YEAR}}`) + final file-tree preview before deploy

## Later / ideas

### Agent & template expansion
- Add more agents: Codex, Gemini CLI, Aider, Cursor, Windsurf, etc. (same JSON + template pattern)
- Per-agent template folder configuration in the wizard (leveraging `settings.py` base template paths)
- Template preview before deploy (show resulting file tree / contents)
- Template versioning / update mechanism (track versions, offer to pull updated base files into existing projects)
- Template import/export (share/backup agent templates as a single archive)
- Template editor UI (visual editor for `agents/*.json` and template folder structure)

### Git & repo features
- GitLab / Bitbucket / Azure DevOps cloning (extend `git_handler.py` beyond GitHub)
- Branch selection when cloning (pick branch/tag instead of default)
- Shallow clone option (faster for large repos)
- Post-deploy initial commit (create first commit automatically, with confirmation)
- Detect existing git repo (adapt flow if target folder is already a repo)
- Create a new GitHub repo from the app (scaffold repo and push deployed template)

### Settings & UX polish
- Settings dialog (manage base template paths, default agent, theme preference)
- Recent projects list / quick resume
- Drag-and-drop folder support on the Source step
- Command-line / batch mode (headless deploy via CLI flags)
- Multi-language UI (i18n)
- Keyboard shortcuts (e.g. Ctrl+Enter Next, Ctrl+B Back)
- Undo/redo on content pages
- Auto-save drafts (persist in-progress content across app restarts)

### Deployment & content
- Direct content generation (call Claude/other API from inside the app instead of copy-paste)
- Dry-run mode (simulate deployment without writing)
- Deploy to multiple projects at once (batch same template to several folders)
- Backup / rollback of overwritten files (keep a `.backup` of anything overwritten)
- Diff view for merge conflicts (side-by-side diff + pick instead of append-only merge)

### CI/CD & DevOps templates
- More CI template variants: Node.js, Go, Rust, Docker (current `ci.yml` is Python-focused but CONFIG-adaptable)
- Other CI platforms: GitLab CI, CircleCI, Azure Pipelines templates
- Dockerfile / docker-compose templates
- Pre-commit hooks template (`.pre-commit-config.yaml` with ruff/black/etc.)
- Release/publish workflow templates (PyPI/npm/GitHub Releases automation)

### Security & quality
- Local pre-deploy secret scan in the app (gitleaks already in CI template)
- Template integrity checks (checksums/validation so corrupted templates fail fast)
- Dependency vulnerability scan (surface known-vulnerable deps during setup)
- Auto-update for the app (check for new versions and self-update)

### Integration & extensibility
- Plugin system (allow third-party deployers/agents without touching core)
- API / webhook (programmatic deployment from scripts or other tools)
- VS Code extension companion (trigger a deploy from within VS Code)
- Cloud sync (sync settings/templates across machines)

### Project self-improvement
- E2E UI tests (automated wizard walkthroughs)
- Broader test coverage (more edge cases across modules)

## Explicitly not planned

- Private GitHub repo support (auth/tokens) — public repos only for now (see projectBrief.md)
- Non-Windows OS support (see projectBrief.md)
- Deploying to multiple agents in a single run — one agent per run (see projectBrief.md)