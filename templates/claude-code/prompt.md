I'm setting up project-specific configuration files for Claude Code (Anthropic's coding agent)
for a new project. I need you to generate tech-stack.md, architecture.md, and projectBrief.md —
and optionally ROADMAP.md.

Here is my project explanation:

[PROJECT EXPLANATION — describe what you're building, the stack you want to use if you already
have a preference, key features, and anything else relevant. The more detail you give here, the
fewer questions you'll get back.]

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

STEP ORDER — follow exactly:

1. First, read my project explanation above.
2. Ask me: "Do you want me to generate ROADMAP.md content as well, or leave it as a blank
   template for you to fill in later?" Ask this as its own standalone question, before any
   other clarifying questions, and wait for my answer.
3. THEN ask any clarifying questions needed for tech-stack.md, architecture.md, and projectBrief.md
   (and ROADMAP.md too, if I said yes in step 2) — batched together in one message.
4. Only after I've answered, generate the files.
5. If I said no to ROADMAP.md in step 2, do not output any content for it, and only give the content for the 3 other files.

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

ROADMAP.md (ONLY if I said yes in step 2):

- Now: what should be actively built first — do NOT guess priority, ask me explicitly
- Next: planned but not started — again, ask, don't infer from the project explanation alone
- Later / ideas: loosely planned items
- Explicitly not planned: things intentionally excluded
- Do not populate any of these sections from assumptions about what a project like this
  "typically" needs — every item must come from something I actually said.
