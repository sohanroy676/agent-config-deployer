# Project Instructions

<!-- Fill in the sections below. Claude Code loads this file and the @-imported memory-bank files
     at the start of every session. The rules in .claude/rules/ (01-06) load automatically, so
     they are NOT imported here (importing them too would load them twice). -->

## Commands

- Run:
- Test:
- Lint:
- Format:

## Hard rules

- (Project-specific must-not-break rules, 3-5 bullets max. General rules live in `.claude/rules/`.)

## Session start

Read `memory-bank/` first (imported below) to rebuild context. At the end of a session, update `memory-bank/progress.md` and `activeContext.md`.

## Workflows

Slash commands `/commit`, `/debug` and `/new-feature` live in `.claude/commands/`.

## Project memory (imported from `memory-bank/`)

@memory-bank/projectBrief.md
@memory-bank/architecture.md
@memory-bank/systemPatterns.md
@memory-bank/tech-stack.md
@memory-bank/activeContext.md
@memory-bank/progress.md
@ROADMAP.md
