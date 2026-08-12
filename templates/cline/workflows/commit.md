# /commit

Use this workflow to commit current changes on demand (outside a full feature/debug flow).

Steps:

1. Run `git status` and `git diff` to review changes.
2. Confirm tests pass (run the suite if unsure) — do not commit failing tests.
3. Run lint/format and fix warnings.
4. Self-review the diff per 04-code-quality-review.md.
5. Stage relevant files and write a Conventional Commits message per 02-commit-style.md.
   Ensure the summary line makes sense standalone to someone reading only the changelog later,
   not just someone reading the diff.
6. Commit. Do not push without explicit approval.
7. Regenerate CHANGELOG.md from commit history (e.g. via conventional-changelog or git-cliff) —
   do not hand-write changelog entries.
