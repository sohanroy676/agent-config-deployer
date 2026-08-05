I'm setting up project-specific configuration files for Cline (an AI coding agent in VS Code)
for a new project. I need you to generate four files: tech-stack.md, architecture.md,
projectBrief.md, and AGENTS.md.

IMPORTANT RULES FOR YOU:

- Do NOT assume anything about the project that I haven't explicitly stated.
- If any detail needed for these files is missing, unclear, or ambiguous, ASK ME first instead
  of guessing or filling it in with a "reasonable default."
- Ask all your clarifying questions together in one batch before generating anything, not one
  at a time.
- Only generate the files after I've answered your questions (or confirmed there's nothing more
  to add).
- Give me the full content of each file directly in the chat as plain text in a code block,
  labeled clearly with the filename above each block. Do NOT create a downloadable artifact or
  file — I need to copy-paste the text directly.

WHAT EACH FILE NEEDS TO COVER:

tech-stack.md:

- Languages/frameworks (with versions if known)
- Test framework, test file location/naming convention, run command
- Lint/format tools and their run commands
- Build/run/dev commands
- Database or external services used

architecture.md:

- Intended folder structure (as a sketch/tree)
- Data flow (how a request/action moves through the system)
- Key modules/folders and their responsibility
- Third-party services/APIs used, and confirmation that any keys go in .env (never hardcoded)

projectBrief.md:

- What the project is and who it's for (1-2 sentences)
- Core goal / success criteria (what "done" looks like for v1)
- Explicitly out of scope (to prevent scope creep later)

AGENTS.md:

- This is a SHORT, cross-tool-compatible summary file (the agents.md standard), not a full rule
  set — keep it under ~15 lines of actual content.
- Project overview (1-2 sentences)
- Tech stack (one line)
- Setup/run/test/lint commands (just the commands, no explanation)
- 2-4 bullet points max of the most critical conventions any agent should know
- End with a line pointing to .clinerules/ for detailed rules

Here is my project explanation:

[PROJECT EXPLANATION — describe what you're building, the stack you want to use if you already
have a preference, key features, and anything else relevant. The more detail you give here, the
fewer questions you'll get back.]
