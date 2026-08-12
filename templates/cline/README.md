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
2. Copy `tech-stack.md` and `architecture.md` from `project-specific-template/` into `memory-bank/` and fill them in for this specific project BEFORE starting to build features.
3. Optional: copy `ROADMAP.md` from `project-specific-template/` into the project root and fill in the plan, or leave the blank template.
4. Copy the `AGENTS.md` file into the project root, and fill in with project-specific content.
5. Tell Cline: "Read all files in .clinerules and memory-bank, then confirm you understand the project setup" as your first message in a new project.

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
├── .clineignore
├── .gitignore
├── CHANGELOG.md             (regenerate via /commit, don't hand-edit)
├── ROADMAP.md               (optional — blank template deployed, fill in the plan)
└── (your actual code)
```

## Daily usage

- Start a session: "Read memory-bank and .clinerules, then let's continue."
- Build a feature: "/new-feature — [describe the feature]"
- Fix a bug: "/debug — [describe the bug]"
- Commit manually anytime: "/commit"
- End a session: "Update memory bank" before closing.
