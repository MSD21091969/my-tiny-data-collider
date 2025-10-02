# My Tiny Data Collider - Copilot Instructions

## Project Overview

**My Tiny Data Collider** is a Pydantic-based tool engineering framework for AI agents and users. The project is organized as an N-tier layered architecture with YAML-driven tool generation.

## Architecture

### Layered Structure
1. **API Layer** (`src/pydantic_api/routers/`): FastAPI HTTP endpoints, JWT auth, RequestEnvelope models
2. **Service Layer** (`src/communicationservice/`, `src/tool_sessionservice/`): Business logic, policy enforcement, orchestration
3. **Tool Layer** (`src/pydantic_ai_integration/tools/`): Tool implementations, MDSContext, execution logic
4. **Persistence Layer** (`src/casefileservice/`, repositories): Firestore storage for sessions, casefiles, events

### Key Components
- **Tool Factory** (`src/pydantic_ai_integration/tools/factory/`): Generates Python tools from YAML definitions
- **MDSContext** (`src/pydantic_ai_integration/dependencies.py`): Unified context carrying user_id, session_id, casefile_id
- **Policy System**: Declarative policies (business_rules, session_policies, casefile_policies, audit_config) defined in YAML, enforced at service layer
- **SOLID Integration** (`src/solidservice/`): Experimental Solid Pod storage (side project)

## Development Guidelines

### Adding New Tools
1. Create YAML definition in `config/tools/`
2. Run tool factory: `python -m scripts.main config/tools/your_tool.yaml`
3. Generated files: `src/pydantic_ai_integration/tools/generated/your_tool.py`, `tests/generated/test_your_tool.py`
4. Run tests: `python -m pytest tests/generated/test_your_tool.py -v`

### Testing Strategy
- **Unit Tests** (`tests/generated/`): Tool layer only, test business logic, use MDSContext directly
- **Integration Tests** (`tests/integration/`): Service layer, test policy enforcement, use ToolRequest/ToolResponse
- **API Tests** (`tests/api/`): HTTP layer, test end-to-end with JWT auth, use RequestEnvelope

### Request/Response Models by Layer
- **API Layer**: `RequestEnvelope` → JSON response
- **Service Layer**: `ToolRequest`/`ChatRequest` → `ToolResponse`/`ChatResponse`
- **Tool Layer**: `MDSContext` + params → `Dict[str, Any]`
- **Persistence Layer**: Pydantic models → Firestore dicts

### Policy Enforcement Flow
1. Policies defined in YAML (business_rules, session_policies, casefile_policies)
2. Tool factory generates code with `@register_mds_tool` decorator
3. Policies stored in `MANAGED_TOOLS` registry
4. Service layer enforces policies before tool execution
5. Tool executes if all policies pass
6. Audit trail created per audit_config

### Code Generation
- **Templates**: `templates/tool_template.py.jinja2`, `templates/test_template.py.jinja2`
- **Factory**: Uses Jinja2 to render Python code from YAML specifications
- **Validation**: Pydantic v2 models for parameters, automatic constraint checking

## Important Patterns

### Context Propagation
```
JWT → user_id → MDSContext(user_id, session_id, casefile_id) → Tool → Audit Trail
```

### Separation of Concerns
- API layer: HTTP handling, authentication extraction
- Service layer: Policy enforcement, orchestration (PRIMARY ENFORCEMENT POINT)
- Tool layer: Business logic execution only (NO policy checks)
- Persistence layer: Data storage only

### When to Use What
- **Direct tool call**: Unit tests, agent integration
- **Service layer call**: When policies need enforcement
- **API endpoint**: When HTTP auth/routing needed

## Tech Stack
- Python 3.12+, Pydantic v2, FastAPI
- Firestore (firebase-admin SDK)
- PyYAML, Jinja2, pytest, pytest-asyncio

## Documentation
- `README.md`: Project overview, quick start, testing philosophy
- `docs/POLICY_AND_USER_ID_FLOW.md`: Policy and user_id propagation
- `docs/LAYERED_ARCHITECTURE_FLOW.md`: N-tier architecture, request/response patterns
- `docs/TOOLENGINEERING_FOUNDATION.md`: Core design principles

## Current Status
- ✅ Week 1 Complete: Tool Factory MVP with echo_tool (9/9 tests passing)
- 🚧 Week 2: Google Workspace toolset, integration test templates
- 📋 Planned: Tool composition, agent-driven selection, document analysis

## Development Commands
```bash
# Generate tool from YAML
python -m scripts.main config/tools/tool_name.yaml

# Run tests by layer
python -m pytest tests/generated/ -v        # Unit tests
python -m pytest tests/integration/ -v      # Integration tests
python -m pytest tests/api/ -v              # API tests

# Run all tests
python -m pytest tests/ -v --tb=short

# Coverage
python -m pytest tests/ --cov=src --cov-report=html
```

## Copilot Assistance Guidelines
- When modifying tools, always regenerate from YAML (don't edit generated files directly)
- When adding features, identify correct layer first
- For policy questions, refer to `docs/POLICY_AND_USER_ID_FLOW.md`
- For architecture questions, refer to `docs/LAYERED_ARCHITECTURE_FLOW.md`
- Test at appropriate layer: unit for logic, integration for policies, API for HTTP
- Follow existing patterns in `src/pydantic_ai_integration/tools/unified_example_tools.py`
