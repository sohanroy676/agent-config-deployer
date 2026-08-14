# ADR-0001: Record architecture decisions

## Status
Accepted

## Date
(fill in when you start using this)

## Context
Decisions made early in a project (tech choices, tradeoffs accepted for cost/time reasons) get forgotten or re-litigated later, especially across sessions with an AI coding agent that doesn't retain memory between chats.

## Decision
Use lightweight Architecture Decision Records (ADRs) for any significant, hard-to-reverse decision — e.g. choice of database, framework, hosting, or a tradeoff accepted for the free tier. One file per decision in `docs/adr/`, using `adr-template.md` as the starting point. Skip ADRs for small, easily reversible choices — don't over-document.

## Alternatives considered
- No formal record, rely on memory/git history — rejected, too easy to lose the "why" behind a decision.
- Full design docs per decision — rejected as too heavyweight for a solo/small project.

## Consequences
Slightly more upfront writing per major decision, but decisions stay traceable across sessions and Claude chats, and future-you (or Cline) doesn't have to guess why something was done a certain way.
