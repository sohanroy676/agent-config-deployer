# Tech Stack

## Languages / frameworks

- Python 3.11+
- OS target: Windows only (for now)
- GUI framework: CustomTkinter (modern-looking, free, lightweight — good fit for a simple wizard-style UI)

## Test framework

- Framework: pytest
- Test file location/naming: `tests/`, files named `test_*.py`
- Run command: `pytest`

## Lint/format tools

- Linter: ruff
- Formatter: black
- Run commands: `ruff check .` and `black .`

## Build/run commands

- Dev run: `python main.py`
- Packaging (later, optional): PyInstaller to produce a standalone `.exe`

## Database / external services

- None. Local filesystem operations only.
- Git integration: uses the system-installed `git` CLI (via subprocess or GitPython) to clone public GitHub repos — no API key required for public repos.
