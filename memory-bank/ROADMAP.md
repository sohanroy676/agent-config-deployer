# Roadmap

<!-- Unversioned, priority-grouped planning. NOT a version map — version numbers
     are assigned at release time (see CHANGELOG.md), not here. This is just
     "what's the plan," so architecture decisions can account for what's coming
     without pre-committing to exact scope/order. -->

## Now

- (nothing active — UI redesign, Cline template improvements, and ROADMAP/memory-bank deployment changes are complete)

## Next

- Wire `config/settings.py` into the UI so the app remembers last-used folder/repo/agent and per-agent base template paths
- Add Claude Code agent config (`agents/claude_code.json`) as a second agent
- PyInstaller packaging to produce a standalone `.exe`

## Later / ideas

- Per-agent template folder configuration in the wizard (leveraging `settings.py` base template paths)

## Explicitly not planned

- Private GitHub repo support (auth/tokens) — public repos only for now (see projectBrief.md)
- Non-Windows OS support (see projectBrief.md)
- Deploying to multiple agents in a single run — one agent per run (see projectBrief.md)