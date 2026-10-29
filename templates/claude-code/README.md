# Claude Code Project Template

Template files deployed by Agent Config Deployer for the **Claude Code** agent. Paths are defined in `agents/claude_code.json`.

## What gets deployed

```
your-project/
├── CLAUDE.md                  (fill in commands + hard rules; @-imports memory-bank/)
├── .claude/
│   ├── rules/01-06-*.md       (auto-loaded by Claude Code at launch)
│   ├── commands/              (/commit, /debug, /new-feature)
│   └── settings.json          (deny reads of secrets, ask before destructive git)
├── memory-bank/               (projectBrief, tech-stack, architecture filled in per project)
├── .github/                   (ci.yml + dependabot.yml)
├── docs/adr/
├── CHANGELOG.md, ROADMAP.md, PRE-DEPLOY-CHECKLIST.md, .gitignore
```

## Notes

- Rules live in `.claude/rules/` and are not `@`-imported by `CLAUDE.md`, to avoid loading them twice.
- `prompt.md` is shown in the wizard's Prompt step; paste it into Claude to generate the project-specific files.
- Files shared with `templates/cline/` are kept identical by a drift test in `tests/test_agent_loader.py`.
