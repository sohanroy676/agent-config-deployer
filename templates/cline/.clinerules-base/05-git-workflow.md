# Git Workflow

- Create a new feature branch for each feature/fix: `git checkout -b feature/short-name` or `fix/short-name`.
- Never commit directly to `main`/`master`.
- Before merging a branch to main, produce a short plain-English summary of what changed and why, for the user to review.
- Never force-push (`git push -f`) without explicit user confirmation.
- Never delete branches or tags without explicit user confirmation.
- If a git operation would rewrite history (rebase, reset --hard, force-push), stop and ask first — these are not auto-approved regardless of settings.
