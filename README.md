# Tiny Data Collider

A comprehensive data integration and API orchestration platform built with FastAPI and Pydantic.

## Quick Start

After cloning the repository, run the **Session Startup** task in VS Code for immediate context and session planning:

```
Tasks: Run Task → "Session Startup"
```

This will:
- Check field notes for previous session context
- Display knowledge base status
- Show current branch and recent changes
- Present context menu for focused development

## Architecture Overview

### Core Services
- **AuthService**: Authentication and authorization
- **CasefileService**: Document and case management
- **CommunicationService**: Chat and messaging integration
- **CoreService**: Central business logic and orchestration
- **ToolSessionService**: Tool execution and session management

### Analysis & Tooling
- **Code Analysis**: 294 models, 825 functions, 122 request/response mappings
- **Persistence Layer**: Database abstractions and data management
- **Pydantic Integration**: Model validation and API integration
- **Testing**: Comprehensive integration and unit tests

## Development Workflow

### Branch Strategy
- `main`: Production-ready code (protected, requires PR + approval)
- `feature/develop`: Development branch (protected, requires PR)
- `feature/*`: Feature branches (CI required)

### Available Tasks
- **Session Startup**: Initialize development session with context
- **Complete Toolset Setup**: Full analysis and tooling setup
- **Quick Analysis**: Fast codebase analysis
- **Pre-commit Checks**: Validation and testing before PRs
- **Full PR Workflow**: End-to-end pull request process

### Analysis Tools
- **code_analyzer**: Python code analysis (models, functions, APIs)
- **version_tracker**: Change history and version analysis
- **excel_exporter**: Analysis results in Excel format
- **mapping_analyzer**: Model relationships (needs CLI interface)

## Knowledge Base

### Documentation
- **Field Notes**: `tool-outputs/docs/personal/MY_FIELD_NOTES.md` - Persistent development context
- **Field References**: `tool-outputs/docs/FIELD_REFERENCES.md` - Domain references
- **Branch Protection**: `.github/BRANCH_PROTECTION.md` - Workflow requirements
- **Copilot Instructions**: `.github/copilot-instructions.md` - AI assistant guidelines

### Generated Analysis
- **Analysis Output**: `tool-outputs/analysis/` - Code analysis results
- **Excel Reports**: `tool-outputs/excel/` - Formatted analysis reports
- **Mappings**: `tool-outputs/mappings/` - Model relationship analysis

## Configuration

### Inventories
- **Models**: `config/models_inventory_v1.yaml` - Model registry
- **Methods**: `config/methods_inventory_v1.yaml` - Method registry
- **Tools**: `config/methodtools_v1/` - Tool configurations

### Tool Schema
- **Schema**: `config/tool_schema_v2.yaml` - Tool definition schema

## Testing

### Registry Validation
```bash
python scripts/validate_registries.py --strict --verbose
```

### Test Suites
```bash
python -m pytest tests/ -v --tb=short
```

### Integration Tests
- Service initialization and configuration
- Registry validation and drift detection
- Cross-service communication patterns

## Getting Started

1. **Clone** the repository
2. **Install** dependencies: `pip install -r requirements.txt`
3. **Configure** your environment
4. **Run** tests to verify setup: `python -m pytest tests/`

### Development Workflow

- Create feature branches from `feature/develop`
- All changes require pull requests with approval
- CI/CD validates registries and runs comprehensive tests
- Use VS Code tasks for analysis and validation

### Working with AI Assistant

You can interact naturally with the AI assistant to streamline your development workflow:

**Getting Started:**
- `"start the session and run the tasks"` - Initialize complete development environment
- `"check field notes"` - Review previous session context and decisions
- `"what's the current project status?"` - Git status, branch info, recent changes
- `"show me the context menu"` - Display available session focus areas

**Code Analysis:**
- `"analyze the codebase"` - Run comprehensive code analysis
- `"show me the models"` - Display Pydantic models and data structures
- `"what tools are available?"` - List analysis and development tools

**Development Tasks:**
- `"check for issues or errors"` - Validate registries and run tests
- `"review my current branch work"` - Show branch changes and progress
- `"help me plan this feature"` - Architecture discussion and planning
- `"validate everything"` - Run pre-commit checks

**Project Management:**
- `"explain the architecture"` - Service overview and relationships
- `"check branch protection rules"` - PR requirements and workflow
- `"create a PR"` - Start pull request process

The AI will automatically detect your environment and run appropriate development tasks.

## Contributing

All contributions require:
- Passing CI/CD checks (registry validation, tests)
- Pull request review and approval
- Documentation updates for significant changes
- Field notes updates for architectural decisions

See `.github/BRANCH_PROTECTION.md` for detailed workflow requirements.