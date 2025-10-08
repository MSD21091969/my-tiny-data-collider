# Copilot Instructions for my-tiny-data-collider# Copilot Instructions for my-tiny-data-collider



**Updated:** October 8, 2025 at 20:50**Updated:** October 8, 2025 at 20:50



## Project Overview## Project Overview



**Stack:** Python 3.11+, FastAPI, Pydantic, Firebase  **Stack:** Python 3.11+, FastAPI, Pydantic, Firebase  

**Architecture:** Tool Engineering + R-A-R Management (intertwined systems)  **Architecture:** Tool Engineering + R-A-R Management (intertwined systems)  

**Status:** Foundation synchronized, RequestHub design complete, tool generation pending**Status:** Foundation synchronized, RequestHub design complete, tool generation pending



## Two Intertwined Systems## Two Intertwined Systems



### System 1: Tool Engineering (Model→Method→Tool Chain)### System 1: Tool Engineering (Model→Method→Tool Chain)

- **Models** (L0-L2): Pydantic DTOs (124 models)- **Models** (L0-L2): Pydantic DTOs (124 models)

- **Methods** (L3): 26 operations in MANAGED_METHODS- **Methods** (L3): 26 operations in MANAGED_METHODS

- **Tools** (L4): Generated from YAML, wraps methods- **Tools** (L4): Generated from YAML, wraps methods

- **YAML** (L5): Declarative configs in `config/toolsets/`- **YAML** (L5): Declarative configs in `config/toolsets/`



**Key:** Parameters defined once in DTO, inherited via code generation.**Key:** Parameters defined once in DTO, inherited via code generation.



### System 2: R-A-R Management (RequestHub Orchestration)### System 2: R-A-R Management (RequestHub Orchestration)

- **RequestHub**: Validates, enriches context, orchestrates routes- **RequestHub**: Validates, enriches context, orchestrates routes

- **Request DTOs**: Fields declare requirements (user_id, auth_token, session_id, etc.)- **Request DTOs**: Fields declare requirements (user_id, auth_token, session_id, etc.)

- **Services**: Business logic, no validation- **Services**: Business logic, no validation

- **Hooks**: Optional downstream operations (metrics, audit, notification)- **Hooks**: Optional downstream operations (metrics, audit, notification)



**Key:** Tool creates Request DTO → RequestHub orchestrates → Service executes.**Key:** Tool creates Request DTO → RequestHub orchestrates → Service executes.



## Code Patterns## Code Patterns



### Request DTO (declares requirements)### Request DTO (declares requirements)

```python```python

class UpdateCasefileRequest(BaseRequest):class UpdateCasefileRequest(BaseRequest):

    # Required    # Required

    user_id: str    user_id: str

    auth_token: str    auth_token: str

    casefile_id: str    casefile_id: str

    payload: UpdateCasefilePayload    payload: UpdateCasefilePayload

        

    # Optional (RequestHub honors if present)    # Optional (RequestHub honors if present)

    session_id: str | None = None    session_id: str | None = None

    context_requirements: List[str] = []    context_requirements: List[str] = []

    hooks: List[str] = []    hooks: List[str] = []

``````



### Generated Tool (creates DTO)### Generated Tool (creates DTO)

```python```python

async def update_casefile_tool(user_id, auth_token, casefile_id, payload, **kwargs):async def update_casefile_tool(user_id, auth_token, casefile_id, payload, **kwargs):

    request = UpdateCasefileRequest(    request = UpdateCasefileRequest(

        user_id=user_id,        user_id=user_id,

        auth_token=auth_token,        auth_token=auth_token,

        casefile_id=casefile_id,        casefile_id=casefile_id,

        payload=payload,        payload=payload,

        hooks=kwargs.get('hooks', [])        hooks=kwargs.get('hooks', [])

    )    )

    return await request_hub.process(request, "update_casefile")    return await request_hub.process(request, "update_casefile")

``````



### RequestHub (orchestrates)### RequestHub (orchestrates)

```python```python

class RequestHub:class RequestHub:

    async def process(self, request: BaseRequest, operation: str):    async def process(self, request: BaseRequest, operation: str):

        # Validate what request declares        # Validate what request declares

        if hasattr(request, 'auth_token'):        if hasattr(request, 'auth_token'):

            await self._validate_auth(request.auth_token)            await self._validate_auth(request.auth_token)

        if hasattr(request, 'session_id'):        if hasattr(request, 'session_id'):

            session = await self._validate_session(request.session_id)            session = await self._validate_session(request.session_id)

                

        # Execute with enriched context        # Execute with enriched context

        service = self._get_service(operation)        service = self._get_service(operation)

        result = await service.method(request, context, session)        result = await service.method(request, context, session)

                

        # Trigger hooks if requested        # Trigger hooks if requested

        if hasattr(request, 'hooks'):        if hasattr(request, 'hooks'):

            for hook in request.hooks:            for hook in request.hooks:

                await self._trigger_hook(hook, request, result)                await self._trigger_hook(hook, request, result)

                

        return result        return result

``````



### Service Method (pure business logic)### Service Method (pure business logic)

```python```python

async def update_casefile(async def update_casefile(

    self,    self,

    request: UpdateCasefileRequest,    request: UpdateCasefileRequest,

    context: MDSContext,    context: MDSContext,

    session: ToolSession    session: ToolSession

) -> UpdateCasefileResponse:) -> UpdateCasefileResponse:

    # No validation - RequestHub did that    # No validation - RequestHub did that

    casefile = await self.repository.update(request.casefile_id, request.payload)    casefile = await self.repository.update(request.casefile_id, request.payload)

    return UpdateCasefileResponse(payload=casefile)    return UpdateCasefileResponse(payload=casefile)

``````



## Tool Generation## Tool Generation



### YAML Structure### YAML Structure

```yaml```yaml

name: update_casefilename: update_casefile

implementation:implementation:

  type: api_call  type: api_call

  method_name: workspace.casefile.update_casefile  method_name: workspace.casefile.update_casefile



# Optional# Optional

default_hooks:default_hooks:

  - metrics  - metrics

  - notification  - notification

``````



### Commands### Commands

```bash```bash

python scripts/generate_tools.py                    # Generate allpython scripts/generate_tools.py                    # Generate all

python scripts/validate_dto_alignment.py            # Check driftpython scripts/validate_dto_alignment.py            # Check drift

python scripts/show_tools.py                        # List toolspython scripts/show_tools.py                        # List tools

``````



## File Locations## File Locations



### Core### Core

- `src/pydantic_models/` - 124 models, 23 Request/Response pairs- `src/pydantic_models/` - 124 models, 23 Request/Response pairs

- `src/coreservice/` - RequestHub (not implemented yet)- `src/coreservice/` - RequestHub (not implemented yet)

- `src/casefileservice/` - Business logic services- `src/casefileservice/` - Business logic services

- `config/methods_inventory_v1.yaml` - 26 methods- `config/methods_inventory_v1.yaml` - 26 methods

- `config/models_inventory_v1.yaml` - 124 models- `config/models_inventory_v1.yaml` - 124 models

- `config/toolsets/` - Tool YAML definitions- `config/toolsets/` - Tool YAML definitions



### Documentation### Documentation

- `HANDOVER.md` - Current state, architecture, roadmap- `HANDOVER.md` - Current state, architecture, roadmap

- `AI/practices/` - Conversation standards, VS Code setup- `AI/practices/` - Conversation standards, VS Code setup

- `AI/prompts/` - Reusable templates- `AI/prompts/` - Reusable templates



## Standards## Standards



### Code Quality### Code Quality

- Type hints required- Type hints required

- Async/await patterns- Async/await patterns

- 85% test coverage minimum- 85% test coverage minimum

- Docstrings with Args, Returns, Raises- Docstrings with Args, Returns, Raises



### Documentation### Documentation

- Update README.md and HANDOVER.md only- Update README.md and HANDOVER.md only

- No intermediate docs- No intermediate docs

- DRY, factual, systematic- DRY, factual, systematic

- Code examples over prose- Code examples over prose



### Commits### Commits

``````

type(scope): Short descriptiontype(scope): Short description



- Factual changes- Factual changes

- No emojis- No emojis

``````



## Current Focus## Current Focus



**Phase 1-2 (This Week):****Phase 1-2 (This Week):**

- Implement RequestHub with field-based validation- Implement RequestHub with field-based validation

- Add optional fields to BaseRequest- Add optional fields to BaseRequest

- Test with one service- Test with one service



**Phase 3-4 (Next Week):****Phase 3-4 (Next Week):**

- Generate tools that create Request DTOs- Generate tools that create Request DTOs

- Build hooks framework- Build hooks framework



**Phase 5-8 (Following Weeks):****Phase 5-8 (Following Weeks):**

- Migrate all services- Migrate all services

- Update routes- Update routes

- Documentation- Documentation



## Prohibited## Prohibited

- Generic policy templates (deleted)- Generic policy templates (deleted)

- Scattered validation in services- Scattered validation in services

- Tools calling methods directly- Tools calling methods directly

- Manual parameter duplication- Manual parameter duplication



## See Also## See Also

- `HANDOVER.md` - Architecture details- `HANDOVER.md` - Architecture details

- `AI/practices/conversation-practices.md` - Communication standards- `AI/practices/conversation-practices.md` - Communication standards


## See Also
- `HANDOVER.md` - Architecture details
- `AI/practices/conversation-practices.md` - Communication standards

### Core Patterns
1. **Service-Repository Pattern**: Clean separation of business logic and data access
2. **Tool Decorator Pattern**: `@register_mds_tool` for AI tool registration
3. **Request-Response DTOs**: `BaseRequest[T]` → `BaseResponse[T]` pattern
4. **Factory Pattern**: YAML → Python tool generation
5. **R-A-R Pattern**: Request-Action-Response model alignment
6. **Parameter Inheritance**: Define once in DTO, auto-extract to Method, auto-inherit to Tool

### 6-Layer Model System
```
L0: Base Infrastructure (BaseRequest/BaseResponse)
  ↓
L1: Payload Models (business data - CreateCasefilePayload)
  ↓
L2: Request/Response DTOs (execution envelopes)
  ↓
L3: Method Definitions (metadata - MANAGED_METHODS)
  ↓
L4: Tool Definitions (metadata - MANAGED_TOOLS)
  ↓
L5: YAML Configuration (source of truth)
```

### Parameter Flow (Single Source of Truth)
```
L1 Payload.title: str
    ↓ AUTO-EXTRACT
L3 MethodParameterDef(name="title", type="str")
    ↓ AUTO-INHERIT
L4 ToolParameterDef(name="title", type="string")
```

### API Layer Structure
```
API Layer (FastAPI) 
  ↓
Tool Request/Response Layer (ToolRequest[ToolRequestPayload])
  ↓
Method DTO Layer (BaseRequest[Payload] → BaseResponse[Payload])
  ↓
Service Layer (Business Logic)
  ↓
Repository Layer (Data Access)
```

## 💻 Code Standards

### Python Code Style
- **Async/Await**: Use for all service methods
- **Type Hints**: Required everywhere
- **Docstrings**: Comprehensive with Args, Returns, Raises
- **Error Handling**: Try-except blocks with specific exceptions
- **Validation**: Pydantic models for all data structures

### Example Service Method
```python
async def method_name(self, request: RequestModel) -> ResponseModel:
    """
    Brief description of what this method does.
    
    Args:
        request: RequestModel containing operation details
        
    Returns:
        ResponseModel with operation results
        
    Raises:
        ValidationError: If request data is invalid
        ServiceError: If operation fails
    """
    start_time = datetime.now()
    try:
        result = await self.repository.operation(request.payload)
        return ResponseModel(
            request_id=request.request_id,
            status=RequestStatus.COMPLETED,
            payload=result,
            metadata={'execution_time_ms': calculate_time(start_time)}
        )
    except Exception as e:
        # Handle error appropriately
        raise ServiceError(f"Operation failed: {str(e)}")
```

### DTO Pattern Requirements
- Follow Request-Action-Response (R-A-R) pattern
- Use `BaseRequest[PayloadT]` for all request DTOs
- Use `BaseResponse[PayloadT]` for all response DTOs
- Payload classes inherit from `BaseModel`
- Include operation field: `operation: Literal["operation_name"]`

## 🛠️ Tool Engineering

### YAML Tool Definition
Tools are defined in `config/toolsets/` following this structure:
```yaml
name: tool_name
description: "Clear, concise description"
category: "domain"
classification:
  domain: workspace
  subdomain: casefile
  capability: create
  complexity: atomic
  maturity: stable
  integration_tier: internal
implementation:
  type: api_call
  api_call:
    method_name: workspace.casefile.create_casefile
# Parameters auto-inherited from method - no manual definition needed
# For composite tools with multiple methods, parameters are merged
```

**Key Rules:**
- 1:1 tools inherit parameters from referenced method automatically
- Composite tools merge parameters from multiple methods
- Override parameters only for transformations or additional UI fields
- Use `method_name` reference for type-safe parameter inheritance

### Tool Generation Commands
```bash
# Generate all tools
python scripts/generate_tools.py

# Generate specific tool
python scripts/generate_tools.py tool_name

# Validate YAML only
python scripts/generate_tools.py --validate-only

# Validate DTO alignment (detect parameter drift)
python scripts/validate_dto_alignment.py

# Display registered tools
python scripts/show_tools.py
```

### Tool Decorator Usage
```python
from src.pydantic_ai_integration.tool_decorator import register_mds_tool

@register_mds_tool(
    name="tool_name",
    description="Tool description",
    enabled=True,
    requires_auth=True
)
async def tool_function(ctx: MDSContext, **kwargs):
    """Tool implementation"""
    # Business logic here
    return result
```

## 📚 Key File Locations

### Documentation
- `AI/` - AI collaboration framework (practices, workflows, prompts, examples)
- `AI/README.md` - Quick start and repository context
- `AI/practices/conversation-practices.md` - Communication standards
- `AI/workflows/` - Development processes and quality assurance
- `HANDOVER.md` - Current development state and session notes
- `config/methods_inventory_v1.yaml` - Method registry (26 methods)
- `config/models_inventory_v1.yaml` - Model registry (52 models)

### Source Code
- `src/pydantic_models/` - Data models (100% DTO coverage, 23/23 operations)
- `src/casefileservice/` - Casefile CRUD operations
- `src/communicationservice/` - Chat session management
- `src/tool_sessionservice/` - Tool execution lifecycle
- `src/pydantic_ai_integration/` - AI tool system and registries
  - `method_registry.py` - MANAGED_METHODS global registry with parameter extraction
  - `model_registry.py` - Model discovery APIs
  - `tool_decorator.py` - MANAGED_TOOLS registry with @register_mds_tool

### Configuration
- `config/toolsets/` - Tool YAML definitions (core, helpers, prototypes, workflows)
- `config/methods_inventory_v1.yaml` - Method registry (26 methods)
- `config/models_inventory_v1.yaml` - Model registry (52 models across 6 layers)
- `config/tool_schema_v2.yaml` - Tool schema with method inheritance support
- `config/policies/` - Audit, security, and session policies
- `pyproject.toml` - Project configuration
- `pytest.ini` - Test configuration

### Scripts
- `scripts/generate_tools.py` - Tool generation from YAML
- `scripts/show_tools.py` - Display registered tools
- `scripts/validate_dto_alignment.py` - Detect parameter drift between models/methods/tools
- `scripts/import_generated_tools.py` - Import tools into MANAGED_TOOLS registry
- `scripts/yaml_test_executor.py` - Execute YAML-based test scenarios

## 🧪 Testing Standards

### Test Coverage Requirements
- **Minimum Coverage**: 80% overall, 85% for new AI-generated code
- **Test Types**: Unit, integration, and end-to-end tests
- **Performance**: API response time <200ms

### Test Structure
```python
def test_function_name():
    """Test description following AAA pattern."""
    # Arrange
    mock_repo = Mock()
    service = ServiceClass(mock_repo, mock_id_service)
    request = RequestModel(valid_test_data)
    
    # Act
    result = await service.method(request)
    
    # Assert
    assert result.status == RequestStatus.COMPLETED
    assert result.payload is not None
    mock_repo.method.assert_called_once()
```

### Running Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific tests
pytest tests/test_specific.py -v

# Run by marker
pytest -m unit
```

## 🔒 Security Requirements

### Authentication & Authorization
- All service methods require user authentication
- Use `user_id` from request context
- Validate permissions before operations
- Include audit trail in metadata

### Input Validation
- Validate all inputs with Pydantic models
- Sanitize user-provided data
- Check for SQL injection, XSS risks
- Rate limit API endpoints

### Prohibited AI Uses
- Do not generate authentication/authorization code
- Do not create production deployment configs
- Do not write financial calculation logic
- Do not generate legal/compliance documentation

## 📊 Quality Standards

### Code Quality
- **Pylint Score**: >8.0
- **Type Coverage**: 100% type hints
- **Documentation**: All public methods documented
- **Error Handling**: Comprehensive exception handling

### Review Process
- All AI-generated code requires human review
- Senior developer approval for significant changes
- PR must include tests and documentation updates
- CI/CD pipeline must pass all checks

## 🔄 Development Workflow

### Daily Development Cycle
1. **Planning**: Use AI for task breakdown and design
2. **Implementation**: Leverage Copilot with established patterns
3. **Generation**: Use ToolFactory for YAML → Python conversion
4. **Testing**: Apply comprehensive test helpers and validation
5. **Review**: Human review following quality guidelines
6. **Integration**: Automated quality gates and deployment

### Commit Standards
```
type(scope): Short description

- Bullet point with factual changes
- Another bullet point
- No emojis, code examples over prose
```

**Types**: feat, fix, refactor, test, docs, chore

## 🎯 Current Status & Next Steps

### Completed (feature/dto-inheritance branch)
✅ **DTO Compliance**: 100% (23/23 operations following R-A-R pattern)  
✅ **Parameter Inheritance**: Auto-extract from DTOs, auto-inherit to tools  
✅ **Model Registry**: 52 models documented across 6 layers  
✅ **Method Registry**: 26 methods with parameter extraction  
✅ **Validation**: `validate_dto_alignment.py` script for drift detection  
✅ **Documentation**: Complete architecture and workflow documentation

### Ready for Merge
- All artifacts complete (configs, registries, validation scripts)
- HANDOVER.md documents current state
- AI collaboration framework in place (AI/ directory)

### Post-Merge Priorities

**Priority 1: Tool Migration**
- Update existing tool YAMLs to use `method_name` references
- Remove redundant parameter definitions from tools
- Re-generate tools with parameter inheritance

**Priority 2: Composite Tool Patterns**
- Implement multi-step workflow orchestration
- Create example composite tools
- Document composition patterns

**Priority 3: R-A-R Route Hooks**
- Add process monitoring and metrics
- Implement validation hooks
- Create observability patterns

## 📖 Documentation Standards

### README Updates
- Update all affected README files with current dates
- Include clear examples and usage instructions
- Cross-reference related documentation
- Keep table of contents current

### API Documentation
- Document all public methods with examples
- Include request/response models
- Show error cases and handling
- Provide integration examples

### Inline Comments
- Use comments sparingly, prefer self-documenting code
- Explain complex algorithms or business logic
- Document workarounds or technical debt
- Reference related issues or decisions

## 🆘 Troubleshooting

### Common Issues
- **Tool Generation Fails**: Check YAML syntax and method references
- **Import Errors**: Verify MANAGED_METHODS registry is loaded
- **Test Failures**: Check DTO compatibility and mocking setup
- **Performance Issues**: Review async/await patterns and queries

### Getting Help
- Review `AI_ASSISTANT_KNOWLEDGE_BASE.md` for comprehensive guidance
- Check `docs/ai-collaboration/` for AI practices
- Consult `TOOL_GENERATION_WORKFLOW.md` for tool engineering
- See `docs/methods/` for API reference

## � Maintenance & Synchronization

### When Models Change (src/pydantic_models/)
1. Update `config/models_inventory_v1.yaml` - Add/remove model entries
2. Update method definitions in `config/methods_inventory_v1.yaml` - Update model references
3. Re-run `python scripts/generate_tools.py` - Regenerate affected tools
4. Validate with `python scripts/validate_dto_alignment.py`

### When Methods Change (config/methods_inventory_v1.yaml)
1. Update tool YAML configs - Fix `method_name` references if method names change
2. Re-run `python scripts/generate_tools.py` - Regenerate affected tools
3. Run `python scripts/import_generated_tools.py` - Refresh MANAGED_TOOLS registry
4. Update tests referencing old method names/signatures
5. Validate with `python scripts/validate_dto_alignment.py`

### When Tools Change (config/toolsets/)
1. Re-run `python scripts/generate_tools.py` - Generate tool code
2. Run `python scripts/import_generated_tools.py` - Update MANAGED_TOOLS registry
3. Update tests if tool signatures change
4. Verify with `python scripts/show_tools.py`

### Critical Rules
- **Parameter drift**: Never manually duplicate parameters between layers
- **Single source of truth**: DTOs define fields, methods extract, tools inherit
- **Validation**: Run validation scripts before committing changes
- **Documentation**: Update HANDOVER.md with session notes, not intermediate docs

## 🔗 Related Resources

- [AI Collaboration Framework](../AI/README.md)
- [Conversation Practices](../AI/practices/conversation-practices.md)
- [Development Workflows](../AI/workflows/)
- [Current Development State](../HANDOVER.md)
- [Method Registry](../config/methods_inventory_v1.yaml)
- [Model Registry](../config/models_inventory_v1.yaml)

---

**Note**: This file is version-controlled and should be updated when major architecture or process changes occur. Keep it synchronized with HANDOVER.md and AI/README.md.
