# Tiny Data Collider - AI Agent Instructions

## AI Chat Practices

### Core Principles
- Ship answers in developer voice—concise, direct, and code-first.
- Stay DRY: avoid repeating established facts or restating plan items.
- Base every response on repository evidence, tool output, or **conceptual context** from toolset resources.
- Skip fluff, emojis, and management speak; maintain engineering cadence.
- Work autonomously when the task is clear and the user has delegated ownership.
- **Leverage conceptual laboratory**: Use FIELD_REFERENCES.md and toolset collections for rich context when concrete data is absent.

### Response Guidelines
- Unblock the user's immediate question; reference `BRANCH_DEVELOPMENT_PLAN.md` when it anchors context.
- **Auto-detect development context** and suggest appropriate tasks without asking:
  - Test `code_analyzer` command → suggest Direct tasks
  - Check for `TINYTOOLSET/` → suggest Legacy setup tasks  
  - Working in toolset repo → reference toolset development tasks
- **Access conceptual resources** from `C:\Users\HP\Desktop\krabbel\tool-outputs\docs\` for AI-assisted design
- Reach for MCP tools, repo utilities, or test runs whenever they yield authoritative answers for CI/CD or workspace state.
- **Run appropriate VS Code tasks** based on detected environment without mentioning task type
- Prefer file paths, diffs, or command output over prose when they communicate faster.
- Keep responses tight; produce layered summaries only when the user requests them explicitly.
- Call out follow-up actions only when they exist and align with the current plan.

### Conceptual Laboratory Integration
- **When concrete data is absent**: Reference `C:\Users\HP\Desktop\krabbel\tool-outputs\docs\ai-context\conceptual-patterns.md` for domain patterns and architectural guidance
- **For AI collaboration**: Access dedicated context at `tool-outputs\docs\ai-context\` (separate from task outputs)
- **For design decisions**: Use FastAPI configs, Pydantic examples, and schema patterns as reference
- **For learning/exploration**: Leverage prompt collections and educational resources
- **Human-relevant context hints**: Always check `ai-context\README.md` for current guidance approach

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

### CRITICAL: Location-Aware Toolset Strategy

**Three Development Contexts:**

1. **HQ Station (Primary Development)**
   - Location: `C:\Users\HP\my-tiny-toolset\TOOLSET\` (permanent installation)
   - PATH configured: Direct tool execution (`code_analyzer`, `mapping_analyzer`, etc.)
   - Tasks: Use "Direct" tasks in VS Code (fastest execution)
   - Outputs: `C:\Users\HP\Desktop\krabbel\tool-outputs\`

2. **Remote/Other Locations (Away from HQ)**
   - Clone: `git clone https://github.com/MSD21091969/my-tiny-toolset.git TINYTOOLSET`
   - Initialize: `git submodule update --init --recursive`
   - Tasks: Use "Legacy" tasks in VS Code (full setup workflow)
   - Outputs: `C:\Users\HP\Desktop\krabbel\tool-outputs\` (or local equivalent)

3. **Toolset Development (Working on toolset itself)**
   - Location: Inside `my-tiny-toolset` repository
   - Tasks: Use toolset's own `.vscode/tasks.json` for tool development
   - Testing: Local tool modifications and template work

**Auto-Detection Strategy:**
- Check if `code_analyzer` command works → HQ Station
- Check if `TINYTOOLSET/` exists → Remote with workspace clone
- Check if `TOOLSET/` exists in current directory → Toolset development

### Repository Tasks Integration

**Multiple tasks.json Files:**
- **Application repo**: `.vscode/tasks.json` (data collider development tasks)
  - Direct tasks: For HQ with permanent toolset
  - Legacy tasks: For remote locations requiring setup
  - Git workflow tasks: Branch management, PR workflow
- **Toolset repo**: `my-tiny-toolset/.vscode/tasks.json` (tool development tasks)
  - Tool testing and development
  - Template and config management
  - Submodule maintenance

**VS Code Command Palette Integration:**
- Tasks automatically available via "Tasks: Run Task"
- Context-aware task selection based on environment detection
- Direct tasks preferred when PATH toolset available
- Legacy tasks for remote/setup scenarios
- **Never mention task type** - just run appropriate tasks for context

### Available Tools
- **code_analyzer**: Analyzes Python code for models, functions, and API patterns
- **version_tracker**: Tracks version history and changes across the codebase
- **mapping_analyzer**: Analyzes model mappings and transformations
- **excel_exporter**: Exports analysis results to Excel format

### Tool Usage Patterns
**HQ Quick Analysis:**
```
code_analyzer . --csv --json --output-dir C:\Users\HP\Desktop\krabbel\tool-outputs\analysis
```

**Remote Setup:**
```
Tasks: Run Task → "Complete Toolset Setup"
```

**Toolset Development:**
```
Tasks: Run Task → "Test Tool" (from toolset's tasks.json)
```

