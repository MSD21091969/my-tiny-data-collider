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
- **Start every session:** Check `MY_FIELD_NOTES.md` for persistent context and previous session state
- **Session Startup Protocol:** Run "Session Startup" task for comprehensive status check
- **Context Menu Approach:** After startup, offer focused session options (field notes, knowledge base, branch work, analysis, PR review, web research)
- **Auto-detect development context** and suggest appropriate tasks without asking:
  - Test `code_analyzer` command → suggest Direct tasks
  - Check for `TINYTOOLSET/` → suggest Legacy setup tasks  
  - Working in toolset repo → reference toolset development tasks
- **Access conceptual resources** from `C:\Users\HP\Desktop\krabbel\tool-outputs\docs\personal\` for AI-assisted design
- **Run appropriate VS Code tasks** based on detected environment without mentioning task type
- **Check Git status** and branch protection rules from `.github/BRANCH_PROTECTION.md` for PR workflows
- Reach for MCP tools, repo utilities, or test runs whenever they yield authoritative answers for CI/CD or workspace state.
- Unblock the user's immediate question; reference `BRANCH_DEVELOPMENT_PLAN.md` when it anchors context.
- Prefer file paths, diffs, or command output over prose when they communicate faster.
- Keep responses tight; produce layered summaries only when the user requests them explicitly.
- Call out follow-up actions only when they exist and align with the current plan.

### Common User Prompts & Actions
**Context & Planning:**
- `"start the session and run the tasks"` → Run Complete Toolset Setup
- `"check field notes"` → Read MY_FIELD_NOTES.md and summarize recent context
- `"what's the current project status?"` → Git status, branch info, recent changes
- `"show me the context menu"` → Display session focus options

**Development Focus:**
- `"analyze the codebase"` → Run code analysis and show key metrics
- `"check for issues or errors"` → Validate registries and run tests
- `"review my current branch work"` → Branch changes and development progress
- `"help me plan this feature"` → Architecture discussion using field notes

**Knowledge Base:**
- `"explain the architecture"` → Reference README.md and service documentation
- `"show me the models"` → Use analysis results to show Pydantic models
- `"what tools are available?"` → List analysis toolset capabilities
- `"check branch protection rules"` → Reference .github/BRANCH_PROTECTION.md

**Quick Actions:**
- `"run analysis"` → Execute appropriate analysis tasks
- `"validate everything"` → Pre-commit checks and validation
- `"create a PR"` → Start pull request workflow
- `"fix the mapping analyzer"` → Address known toolset issues

### Conceptual Laboratory Integration
- **Session Startup:** Always check `MY_FIELD_NOTES.md` first for persistent context from previous sessions
- **Documentation Access:** Reference README.md for project overview, .github/ docs for workflows
- **When concrete data is absent**: Reference `C:\Users\HP\Desktop\krabbel\tool-outputs\docs\personal\MY_FIELD_NOTES.md` for domain patterns and architectural guidance
- **For AI collaboration**: Access personal documentation at `tool-outputs\docs\personal\` (persistent across sessions)
- **For design decisions**: Use FastAPI configs, Pydantic examples, and schema patterns as reference
- **For learning/exploration**: Leverage prompt collections and educational resources
- **Human-relevant context hints**: Always check personal field notes for current guidance approach
- **Knowledge Base Access**: Use `C:\Users\HP\Desktop\krabbel\tool-outputs\docs\FIELD_REFERENCES.md` and README.md for systematic reference
- **Branch Context**: Check `.github/BRANCH_PROTECTION.md` for workflow requirements and PR rules
- **Service Documentation**: Reference individual service README files in scripts/, config/, tests/ directories

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
**HQ Quick Analysis (Reliable):**
```
python "C:\Users\HP\my-tiny-toolset\TOOLSET\code_analyzer.py" . --csv --json --output-dir C:\Users\HP\Desktop\krabbel\tool-outputs\analysis
```

**Known Issues & Workarounds:**
- **code_analyzer BAT wrapper:** Has path handling bug for CSV export - use Python directly
- **mapping_analyzer:** Missing main entry point - contains 431 lines of useful mapping classes but no executable main function. **NEEDS REPLACEMENT** with proper CLI interface or integration into code_analyzer
- **excel_exporter:** Requires openpyxl - install via `install_python_packages` tool
- **File locations:** Tools may output to workspace root - manually move to tool-outputs directories

**Remote Setup:**
```
Tasks: Run Task → "Complete Toolset Setup"
```

**Toolset Development:**
```
Tasks: Run Task → "Test Tool" (from toolset's tasks.json)
```

