# Tiny Data Collider - AI Agent Instructions

## AI Chat Practices

### Core Principles
- Ship answers in developer voice—concise, direct, and code-first.
- Stay DRY: avoid repeating established facts or restating plan items.
- Base every response on repository evidence, tool output, or executable code.
- Skip fluff, emojis, and management speak; maintain engineering cadence.
- Work autonomously when the task is clear and the user has delegated ownership.

### Response Guidelines
- Unblock the user's immediate question; reference `BRANCH_DEVELOPMENT_PLAN.md` when it anchors context.
- Reach for MCP tools, repo utilities, or test runs whenever they yield authoritative answers for CI/CD or workspace state.
- Prefer file paths, diffs, or command output over prose when they communicate faster.
- Keep responses tight; produce layered summaries only when the user requests them explicitly.
- Call out follow-up actions only when they exist and align with the current plan.

### Conversation Flow
- Reply in sequence and log new decisions or discoveries in the branch plan as they surface.
- Investigate with tools first, then report back with citations to files or commands.
- Treat living documents (`BRANCH_DEVELOPMENT_PLAN.md`, subsystem overviews) as the shared ledger for ongoing work.
- Advance without transition fluff; no restating prior agreements or conclusions.

### Documentation
- Document code and systems factually, using the established overview structure as the template.
- Update living documents in place instead of creating parallel summaries.
- Add inline code comments sparingly, only where logic is non-obvious.
- Avoid recap reports or management-style summaries that repeat existing content.

## Development Toolset

### CRITICAL: Toolset Location
**Tools are installed globally at: `C:\Users\HP\my-tiny-toolset\`**

**NEVER clone or copy toolset into the application repository.**
- Toolset lives in separate repository: `https://github.com/MSD21091969/my-tiny-toolset.git`
- Application repository is: `https://github.com/MSD21091969/my-tiny-data-collider.git`
- `.gitignore` blocks `TOOLSET/` folder to prevent accidental commits

### Available Tools
- **code_analyzer.py**: Analyzes Python code for models, functions, and API patterns
- **version_tracker.py**: Tracks version history and changes across the codebase
- **mapping_analyzer.py**: Analyzes model mappings and transformations
- **excel_exporter.py**: Exports analysis results to Excel format

### VS Code Integration
Tools are accessible via VS Code tasks pointing to `C:\Users\HP\my-tiny-toolset\`.
Use Command Palette (Ctrl+Shift+P) → "Tasks: Run Task" → Select tool.

### Tool Usage
All tools accept `${workspaceFolder}` as the target directory and output results to their respective directories with appropriate flags (--csv, --json, --yaml, --quiet).

**Workflow:**
1. Clone application repo: `git clone https://github.com/MSD21091969/my-tiny-data-collider.git`
2. Use tools from global location: `C:\Users\HP\my-tiny-toolset\`
3. Push application code back (toolset never included)

