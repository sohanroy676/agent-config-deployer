# Cline Project Template — Setup Guide

## One-time setup

1. Keep this whole `cline-templates/` folder somewhere permanent on your machine (e.g. `~/cline-templates/`).
2. Optional: copy the contents of `.clinerules-base/` into Cline's **global custom instructions** (Settings) if you want them applied automatically to every project without copying files.

## For every new project

1. Copy these into your new project root:
    - `.clinerules-base/*.md` → into a `.clinerules/` folder in the project
    - `workflows/*.md` → into `.clinerules/workflows/` in the project
    - `.clineignore` → project root
    - `.gitignore` → project root (merge with any existing one)
    - `memory-bank-template/*.md` → into a new `memory-bank/` folder, then fill in `projectBrief.md`
2. Copy `project-specific-template/*.md` into `.clinerules/` too, except the `AGENTS.md`, and fill in `tech-stack.md` and `architecture.md` for this specific project BEFORE starting to build features.
3. Copy the `AGENTS.md` file into the project root, and fill in with project-specific content.
4. Tell Cline: "Read all files in .clinerules and memory-bank, then confirm you understand the project setup" as your first message in a new project.

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
│   ├── tech-stack.md          (filled in per project)
│   ├── architecture.md        (filled in per project)
│   └── workflows/
│       ├── new-feature.md
│       ├── debug.md
│       └── commit.md
├── memory-bank/
│   ├── projectBrief.md
│   ├── activeContext.md
│   ├── progress.md
│   └── systemPatterns.md
├── .clineignore
├── .gitignore
└── (your actual code)
```

## Daily usage

- Start a session: "Read memory-bank and .clinerules, then let's continue."
- Build a feature: "/new-feature — [describe the feature]"
- Fix a bug: "/debug — [describe the bug]"
- Commit manually anytime: "/commit"
- End a session: "Update memory bank" before closing.
