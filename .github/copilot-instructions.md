# Tiny Data Collider – Copilot Guide

## Core Expectations
- `MY_TINY_TOOLSET_DIR` must point at **`C:\Users\HP\my-tiny-toolset`** (local toolset repository with knowledge base). Abort fast if it is unset.
- Use the toolset's direct tasks first (`Quick Analysis`, `Version Tracking`, `Excel Export`). Report the exact task name and error output when something fails.
- Open each session by checking for updates in `MY_FIELD_NOTES.md` at **`C:\Users\HP\Desktop\krabbel\tool-outputs\docs\personal\MY_FIELD_NOTES.md`** and confirming any outstanding issues the user flags.
- Reference system architecture and classification documents at **`C:\Users\HP\Desktop\krabbel\classification\`** for planning, registry analysis, and development context.
- Stay concise, code-forward, and evidence-based—cite files, diffs, or tool output instead of prose summaries.
- Default to acting autonomously once the user hands off a task; ask only when a decision is blocking progress.

## Response Style
- Developer voice only: no fluff, emojis, or recaps of agreed plans.
- Reference documentation or tool outputs already in the repo (README, service docs, `.github/BRANCH_PROTECTION.md`, analysis exports).
- Reference toolset knowledge base at **`C:\Users\HP\my-tiny-toolset\`** (EXAMPLES/, CONFIGS/, PROMPTS/, TEMPLATES/, SCHEMAS/).
- Reference classification documents at **`C:\Users\HP\Desktop\krabbel\classification\`** for system architecture, registry analysis, development plans.
- Prefer direct artefacts (paths, commands, diffs) over narration. Offer follow-up actions only when they are concrete next steps.

## Session Flow
1. Verify `MY_TINY_TOOLSET_DIR`; if unset, set it to **`C:\Users\HP\my-tiny-toolset`** and run `Health Check Toolset`.
2. Review field notes at **`C:\Users\HP\Desktop\krabbel\tool-outputs\docs\personal\MY_FIELD_NOTES.md`** for user context (read-only, personal reference).
3. Check classification documents at **`C:\Users\HP\Desktop\krabbel\classification\`** for system architecture context:
   - `GRAND_CLASSIFICATION_PLAN.md` - Registry system overview (36 tools, 34 methods, 80 models)
   - `SYSTEM/BRANCH_DEVELOPMENT_PLAN.md` - Development milestones and progress
   - `SYSTEM/registry/REGISTRY_CONSOLIDATION_SUMMARY.md` - Registry consolidation status
   - `FIELD_REFERENCES.md` - External references and patterns
   - `exports/` - Model exports and analysis tools
4. Detect environment:
   - Local toolset at **`C:\Users\HP\my-tiny-toolset`** → use direct tasks.
   - `TINYTOOLSET/` clone present → fall back to legacy setup tasks.
   - Working inside the toolset repo → use that repo's tasks.
5. Investigate with repo evidence or MCP tools before responding.
6. Answer the user's question, then point at immediate next steps only if they exist.

## Quick Command Map
- `check` → set `MY_TINY_TOOLSET_DIR=C:\Users\HP\my-tiny-toolset`, run `Health Check Toolset`, check field notes.
- `start the session and run the tasks` → run `Complete Toolset Setup`.
- `check field notes` → read **`C:\Users\HP\Desktop\krabbel\tool-outputs\docs\personal\MY_FIELD_NOTES.md`**, summarize changes.
- `check classification` → review **`C:\Users\HP\Desktop\krabbel\classification\`** for system architecture and registry status.
- `what's the current project status?` → `git status`, branch info, recent commits, check classification docs for milestones.
- `analyze the codebase` → run `Quick Analysis (Direct)`.
- `check for issues or errors` → `Validate Before PR` + `Run All Tests`.
- `create a PR` → guided PR workflow tasks.
- `fix the mapping analyzer` → note that `mapping_analyzer` lacks a CLI entry point; highlight replacement work.

## Key Resource Locations
- **Toolset Repository:** `C:\Users\HP\my-tiny-toolset` (knowledge base: EXAMPLES/, CONFIGS/, PROMPTS/, TEMPLATES/, SCHEMAS/, TOOLSET/)
- **Field Notes:** `C:\Users\HP\Desktop\krabbel\tool-outputs\docs\personal\MY_FIELD_NOTES.md` (personal reference, read-only)
- **Classification Project:** `C:\Users\HP\Desktop\krabbel\classification\` (system architecture, registry analysis, development plans)
- **Tool Outputs:** `C:\Users\HP\Desktop\krabbel\tool-outputs\` (analysis/, mappings/, excel/, docs/)
- **Model Exports:** `C:\Users\HP\Desktop\krabbel\classification\exports\` (77 CSV files with model field structure)

## Tooling Reminders
- Assume outputs land under the configured toolset output directory (default installation uses `C:\Users\HP\Desktop\krabbel\tool-outputs\`).
- Known gaps: `mapping_analyzer` has no main; `excel_exporter` needs `openpyxl`; `code_analyzer` BAT wrapper is unreliable—call the Python module directly.
- When remote: clone `my-tiny-toolset` into `TINYTOOLSET`, run submodule init, then use legacy tasks.
- When developing the toolset itself: switch to that repo’s `.vscode/tasks.json` and follow its workflow.

