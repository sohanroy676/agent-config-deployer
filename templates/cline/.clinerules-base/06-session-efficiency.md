# Session & Token Efficiency

- Do not re-read entire files that are already visible in context unless they've changed.
- When exploring a codebase, read only the files relevant to the current task, not the whole directory tree.
- Prefer targeted `grep`/search over opening large files fully when just locating something.
- At the end of a work session (or after completing 1-2 features), update the memory bank files (`progress.md`, `activeContext.md`) with current state, then recommend starting a fresh session for the next feature rather than continuing indefinitely in one thread.
- At the start of a new session, read the memory-bank folder fully before doing anything else, to rebuild context efficiently instead of asking the user to re-explain.
