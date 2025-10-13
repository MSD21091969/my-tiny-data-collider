# Tiny Data Collider

A comprehensive data integration and API orchestration platform built with FastAPI and Pydantic.

## Quick Start

After cloning the repository, AI assistant will check field notes for context.

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
- **Complete Toolset Setup**: Full analysis and tooling setup
- **Quick Analysis**: Fast codebase analysis
- **Pre-commit Checks**: Validation and testing before PRs
- **Full PR Workflow**: End-to-end pull request process

### Analysis Tools
- **code_analyzer**: Python code analysis (models, functions, APIs)
- **version_tracker**: Change history and version analysis
- **excel_exporter**: Analysis results in Excel format
- **mapping_analyzer**: Model relationships (needs CLI interface)

## Pydantic Validation Enhancements

### Custom Types Library
The project includes 20+ reusable Annotated types for consistent validation:

```python
from src.pydantic_models.base.custom_types import (
    CasefileId, ToolSessionId, ChatSessionId,
    ShortString, MediumString, LongString,
    PositiveInt, NonNegativeInt,
    IsoTimestamp, EmailAddress, TagList
)

class MyModel(BaseModel):
    id: CasefileId              # Auto-validates UUID, converts to lowercase
    title: ShortString          # 1-200 characters
    count: PositiveInt          # Must be > 0
    created_at: IsoTimestamp    # ISO 8601 format validation
    tags: TagList               # List of non-empty strings
```

**Available Custom Types:**
- **IDs**: `CasefileId`, `ToolSessionId`, `ChatSessionId`, `SessionId`
- **Strings**: `NonEmptyString`, `ShortString` (1-200), `MediumString` (1-1000), `LongString` (1-10000)
- **Numbers**: `PositiveInt`, `NonNegativeInt`, `PositiveFloat`, `NonNegativeFloat`, `Percentage`, `FileSizeBytes`
- **Email/URL**: `EmailAddress`, `UrlString`
- **Timestamps**: `IsoTimestamp` (ISO 8601 format)
- **Collections**: `TagList`, `EmailList`

### Reusable Validators
Extract common validation patterns with reusable validators:

```python
from src.pydantic_models.base.validators import (
    validate_timestamp_order,
    validate_at_least_one,
    validate_mutually_exclusive,
    validate_conditional_required
)

@model_validator(mode='after')
def validate_model(self) -> 'MyModel':
    # Ensure created_at <= updated_at
    validate_timestamp_order(self, 'created_at', 'updated_at')
    
    # At least one contact method required
    validate_at_least_one(self, ['email', 'phone', 'address'])
    
    # Only one payment method allowed
    validate_mutually_exclusive(self, ['credit_card', 'paypal', 'bank_transfer'])
    
    return self
```

**Available Validators:**
- `validate_timestamp_order` - Ensure timestamp ordering
- `validate_at_least_one` - At least one field required
- `validate_mutually_exclusive` - Only one field allowed
- `validate_conditional_required` - Conditional field requirements
- `validate_list_not_empty` - Non-empty list validation
- `validate_list_unique` - Unique list items
- `validate_range` - Numeric range validation
- `validate_string_length` - String length constraints
- `validate_depends_on` - Field dependency validation

See `docs/VALIDATION_PATTERNS.md` for detailed usage examples and migration guide.

## Documentation

### Core Documentation
- **[Documentation Index](docs/README.md)** - Complete documentation guide and navigation ⭐
- **[Validation Patterns](docs/VALIDATION_PATTERNS.md)** - Custom types and validators guide
- **[Development Progress](docs/DEVELOPMENT_PROGRESS.md)** - Phase 1 completion tracking (27/32 hours)
- **[Phase 1 Summary](docs/PHASE1_COMPLETION_SUMMARY.md)** - Comprehensive achievements overview

### Technical References
- **[Parameter Mapping Results](docs/PARAMETER_MAPPING_RESULTS.md)** - 40 tool-method mismatches discovered
- **[Pytest Import Issue](docs/PYTEST_IMPORT_ISSUE.md)** - Test collection issue and workarounds
- **[Parameter Mapping Test Issues](docs/PARAMETER_MAPPING_TEST_ISSUES.md)** - Test creation challenges

### Planning Documents
- **[Pydantic Enhancement Longlist](docs/PYDANTIC_ENHANCEMENT_LONGLIST.md)** - Original planning (historical reference)

**See [docs/README.md](docs/README.md) for complete documentation index and quick navigation.**

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
# Full validation (coverage, consistency, drift, parameter mapping)
python scripts/validate_registries.py --strict --verbose

# Skip specific validations
python scripts/validate_registries.py --no-drift --no-param-mapping

# Detailed parameter mapping validation
python scripts/validate_parameter_mappings.py --verbose
```

**Validation Features:**
- **Coverage Validation**: Ensures all tools reference valid methods
- **Consistency Validation**: Checks method/tool configuration consistency
- **Drift Detection**: Compares YAML definitions with code implementation
- **Parameter Mapping**: Validates tool-to-method parameter compatibility

### Test Suites
```bash
# Run all tests
python -m pytest tests/ -v --tb=short

# Run specific test suites
python -m pytest tests/pydantic_models/ -v  # Model validation tests
python -m pytest tests/registry/ -v          # Registry tests
python -m pytest tests/integration/ -v       # Integration tests
```

**Test Coverage:**
- **Pydantic Models**: 116 tests (custom types, canonical models, validators)
- **Registry System**: 43 tests (method/tool registration, validation)
- **Integration**: Service initialization and cross-service patterns

### Integration Tests
- Service initialization and configuration
- Registry validation and drift detection
- Cross-service communication patterns
- Parameter mapping and validation

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