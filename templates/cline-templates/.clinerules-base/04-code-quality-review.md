# Self-Review Before Committing

Before committing any change, re-read the diff acting as a strict code reviewer and check for:

- Security: hardcoded secrets, unsanitized input, unsafe file/shell operations
- Error handling: missing try/catch, unhandled promise rejections, silent failures
- Complexity: functions doing too much, deeply nested logic, unclear naming
- Duplication: logic that already exists elsewhere in the codebase
- Consistency: does this match existing patterns in the project (see systemPatterns.md)?
- Dead code: unused imports, commented-out blocks, leftover debug logs/print statements

Fix anything flagged before proceeding to commit. If unsure whether something is an issue, err on the side of fixing it.

## General coding style

- Make minimal, targeted edits — do not rewrite entire files unless the task genuinely requires it.
- Do not "helpfully" refactor unrelated code while fixing a specific bug; stay scoped to the task.
- Prefer clear, boring code over clever one-liners.
- Run the project's linter/formatter before committing and fix all warnings (not just errors).
