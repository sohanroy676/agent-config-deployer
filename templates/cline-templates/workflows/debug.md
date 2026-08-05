# /debug

Use this workflow when fixing a bug or failing behavior.

Steps:
1. Reproduce the issue first — run the app/tests and confirm you can see the failure before changing anything.
2. Isolate the root cause (don't guess-patch symptoms). Trace back through logs/stack traces/relevant code.
3. State the root cause in one or two sentences before writing the fix.
4. Implement the minimal fix — do not refactor unrelated code while fixing a bug.
5. Write a regression test that would have caught this bug, in addition to any other needed test coverage (03-testing.md).
6. Run the full test suite to confirm the fix works and nothing else broke.
7. Self-review per 04-code-quality-review.md.
8. Commit per 02-commit-style.md, using `fix:` type and referencing the root cause in the commit body.
9. Update `memory-bank/progress.md` with what was fixed.
