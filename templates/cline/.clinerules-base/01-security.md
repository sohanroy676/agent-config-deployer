# Security Rules (Non-negotiable)

- NEVER hardcode API keys, tokens, passwords, connection strings, or secrets directly in source files.
- Always use environment variables loaded via `.env` (or the project's config system).
- Before every commit, scan the diff for anything that looks like a secret (long random strings, "key=", "token=", "password="). If found, stop and move it to `.env` first.
- Ensure `.env`, `.env.local`, and any credentials file are listed in `.gitignore` BEFORE the first commit of a new project.
- Never log sensitive data (passwords, tokens, full credit card numbers, etc.) to console or files.
- When adding a new third-party dependency, briefly check it's a real, maintained package (not a typo-squat) before installing.
- Validate and sanitize all external/user input on any code path that touches a database query, shell command, or file path (basic injection prevention).
