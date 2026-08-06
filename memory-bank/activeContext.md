# Active Context

<!-- Update this at the end of every session. This is the first thing to read when resuming. -->

## Current focus

The full UI/UX redesign is complete on `feature/ui-redesign` (16b2f39): a cohesive design system (`ui/theme.py`), reusable components (`ui/components.py`), a rebuilt app shell with header/footer/theme toggle, and redesigned 6-step wizard screens with loading/error/empty states. All 56 tests pass.

## Recent decisions

- Introduced a design-system layer (`ui/theme.py`) with dark/light palettes, standardized typography, spacing, radii, and widget factories — every screen draws from it; no isolated cosmetic hacks.
- Added shared components (`ui/components.py`): cards, badges, inline notices, form fields with inline validation (replaces `messagebox` popups), step-indicator rail, segmented conflict choices (replaces dropdowns), and loading/error/empty full-area states.
- Moved "Back"/"Next" into a shared footer with per-step metadata (`back_enabled`/`next_enabled`/`footer_*_label`); footer labels refresh after content-page navigation.
- Conflict decisions are recorded live via the segmented control's callback (same `report.decisions` contract) — the old collect-on-Next loop is gone.
- Theme toggle rebuilds the current step; wizard state persists across rebuilds (`folder_path`, `repo_url`, `agent`, `_content_state`, `report`, `written`/`skipped`), so toggling on the content/conflicts steps does not lose data.
- Default window is now 980x680 (min 820x600) and follows the system appearance with a dark/light toggle in the header; `main.py` sets the appearance mode and a pure-Tk app icon.
- Kept `file_deployer.py` as the ONLY module writing into the target project and conflict resolution in `conflict_resolver.py` unchanged.

## Blockers / open questions

- None blocking. Note: `config/settings.py` still exists but is not yet wired into the UI (last-used paths / per-agent base template paths are not yet remembered between runs).

## Next step

Wire `config/settings.py` into the UI so the app remembers last-used folder/repo/agent and per-agent base template paths. After that, consider adding a Claude Code agent config as a second agent.
