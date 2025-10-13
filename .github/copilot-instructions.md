# Tiny Data Collider – Copilot Guide

## Core Expectations
- `MY_TINY_TOOLSET_DIR` must point at the local toolset root (example: `C:\Users\HP\my-tiny-toolset`). Abort fast if it is unset.
- Use the toolset’s direct tasks first (`Quick Analysis`, `Version Tracking`, `Excel Export`). Report the exact task name and error output when something fails.
- Open each session by checking for updates in `MY_FIELD_NOTES.md` and confirming any outstanding issues the user flags.
- Stay concise, code-forward, and evidence-based—cite files, diffs, or tool output instead of prose summaries.
- Default to acting autonomously once the user hands off a task; ask only when a decision is blocking progress.

## Response Style
- Developer voice only: no fluff, emojis, or recaps of agreed plans.
- Reference documentation or tool outputs already in the repo (README, service docs, `.github/BRANCH_PROTECTION.md`, analysis exports).
- Prefer direct artefacts (paths, commands, diffs) over narration. Offer follow-up actions only when they are concrete next steps.

## Session Flow
1. Verify `MY_TINY_TOOLSET_DIR`; surface relevant direct tasks without mentioning task categories.
2. Review `MY_FIELD_NOTES.md` for context; log any new decisions in the branch plan as they arise.
3. Detect environment:
   - `code_analyzer` on PATH → use direct tasks.
   - `TINYTOOLSET/` clone present → fall back to legacy setup tasks.
   - Working inside the toolset repo → use that repo’s tasks.
4. Investigate with repo evidence or MCP tools before responding.
5. Answer the user’s question, then point at immediate next steps only if they exist.

## Quick Command Map
- `start the session and run the tasks` → run `Complete Toolset Setup`.
- `check field notes` → read `MY_FIELD_NOTES.md`, summarize changes.
- `what's the current project status?` → `git status`, branch info, recent commits.
- `analyze the codebase` → run `Quick Analysis (Direct)`.
- `check for issues or errors` → `Validate Before PR` + `Run All Tests`.
- `create a PR` → guided PR workflow tasks.
- `fix the mapping analyzer` → note that `mapping_analyzer` lacks a CLI entry point; highlight replacement work.

## Tooling Reminders
- Assume outputs land under the configured toolset output directory (default installation uses `C:\Users\HP\Desktop\krabbel\tool-outputs\`).
- Known gaps: `mapping_analyzer` has no main; `excel_exporter` needs `openpyxl`; `code_analyzer` BAT wrapper is unreliable—call the Python module directly.
- When remote: clone `my-tiny-toolset` into `TINYTOOLSET`, run submodule init, then use legacy tasks.
- When developing the toolset itself: switch to that repo’s `.vscode/tasks.json` and follow its workflow.

