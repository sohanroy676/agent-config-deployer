# /new-feature

Use this workflow when implementing a new feature end-to-end.

Steps:

1. Confirm you understand the requirement — restate acceptance criteria (expected inputs/outputs, edge cases, what "done" looks like) before writing code. If the request is vague, ask for the missing specifics first.
2. Check `memory-bank/architecture.md` and `memory-bank/systemPatterns.md` for existing conventions to follow, and check `ROADMAP.md` to confirm this feature's priority/scope matches what's planned.
3. Create a feature branch (see 05-git-workflow.md).
4. Implement the feature with minimal, targeted changes.
5. Write/update tests per 03-testing.md and run the full suite.
6. Run lint/format and fix all warnings.
7. Self-review the diff per 04-code-quality-review.md.
8. Commit per 02-commit-style.md.
9. Update `memory-bank/progress.md` and `activeContext.md` with what was done and what's next, and update ROADMAP.md to move this feature out of "Now"/"Next" (CHANGELOG.md itself gets regenerated via the /commit workflow, step 7).
10. Summarize the change in plain English for the user, and note it's ready for review/merge (do not push or merge without approval).
