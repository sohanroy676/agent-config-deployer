# Cline Project Template — Setup Guide

## One-time setup

1. Keep this whole `cline/` folder somewhere permanent on your machine (e.g. `~/cline/`).
2. Optional: copy the contents of `.clinerules-base/` into Cline's **global custom instructions** (Settings) if you want them applied automatically to every project without copying files.

## For every new project

1. Copy these into your new project root:
    - `.clinerules-base/*.md` → into a `.clinerules/` folder in the project
    - `workflows/*.md` → into `.clinerules/workflows/` in the project
    - `.clineignore` → project root
    - `.gitignore` → project root (merge with any existing one)
    - `memory-bank-template/*.md` → into a new `memory-bank/` folder, then fill in `projectBrief.md`
2. Copy `project-specific-template/tech-stack.md` and `architecture.md` into `.clinerules/`, and fill them in for this specific project BEFORE starting to build features.
3. Copy `project-specific-template/AGENTS.md`, `CHANGELOG.md`, and `ROADMAP.md` into the **project root** (not `.clinerules/`) and fill them in. `AGENTS.md` is a short, cross-tool file Cline reads automatically alongside `.clinerules/`. `CHANGELOG.md` starts with just an `[Unreleased]` header — it gets filled in via the `/commit` workflow, not by hand. `ROADMAP.md` is your unversioned, priority-grouped feature plan.
4. Tell Cline: "Read all files in .clinerules, AGENTS.md, and memory-bank, then confirm you understand the project setup" as your first message in a new project.
5. Copy `ci-template/.github/` (both `workflows/ci.yml` and `dependabot.yml`) into your project's `.github/` folder, then customize the install/lint/test commands in `ci.yml` to match `tech-stack.md`. Also enable GitHub's secret scanning manually in repo Settings → Code security and analysis (free, no file needed for that part).
6. Copy `docs-adr-template/*.md` into a `docs/adr/` folder in your project — `0001-record-architecture-decisions.md` as your first real ADR, `adr-template.md` stays as the copyable template for future decisions.
7. Copy `PRE-DEPLOY-CHECKLIST.md` into the project root — run through it before deploying anywhere real users can reach it.

## Resulting folder structure in each project

```
your-project/
├── .clinerules/
│   ├── 01-security.md
│   ├── 02-commit-style.md
│   ├── 03-testing.md
│   ├── 04-code-quality-review.md
│   ├── 05-git-workflow.md
│   ├── 06-session-efficiency.md
│   └── workflows/
│       ├── new-feature.md
│       ├── debug.md
│       └── commit.md
├── memory-bank/
│   ├── projectBrief.md        (filled in per project)
│   ├── activeContext.md
│   ├── progress.md
│   ├── systemPatterns.md
│   ├── tech-stack.md          (filled in per project)
│   └── architecture.md        (filled in per project)
├── .github/
│   ├── workflows/
│   │   └── ci.yml           (customize commands in the CONFIG section)
│   └── dependabot.yml       (weekly dependency update PRs)
├── docs/
│   └── adr/
│       ├── adr-template.md  (copy for each new architecture decision)
│       └── 0001-record-architecture-decisions.md
├── .clineignore
├── .gitignore
├── CHANGELOG.md             (regenerate via /commit, don't hand-edit)
├── ROADMAP.md               (optional — blank template deployed, fill in the plan)
├── PRE-DEPLOY-CHECKLIST.md  (run through before deploying anywhere real)
└── (your actual code)
```

## Daily usage

- Start a session: "Read memory-bank, .clinerules, and AGENTS.md, then let's continue."
- Build a feature: "/new-feature — [describe the feature]"
- Fix a bug: "/debug — [describe the bug]"
- Commit manually anytime: "/commit"
- End a session: "Update memory bank" before closing.
