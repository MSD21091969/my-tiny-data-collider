# AI Collaboration Framework# AI Collaboration Framework



**Updated:** October 8, 2025 at 20:50Last updated: October 8, 2025 at 19:30



## Structure## Structure



``````

AI/AI/

├── practices/        # Conversation standards, VS Code setup├── practices/        # Conversation standards, collaboration guidelines

└── prompts/          # Reusable prompt templates├── workflows/        # Development processes, quality assurance

```├── prompts/          # Reusable prompt templates

└── examples/         # Real repository examples

## Repository Context```



**Name:** my-tiny-data-collider  ## Quick Start

**Stack:** Python 3.11+, FastAPI, Pydantic, Firebase  

**Architecture:** Tool Engineering + R-A-R Management (intertwined)  **Contributors:** Read practices/conversation-practices.md, prompts/README.md  

**Status:** Foundation synchronized, RequestHub design complete**AI Assistants:** Check ../.github/copilot-instructions.md, workflows/quality-assurance.md



### Core Systems## Principles



**Tool Engineering:** Model→Method→Tool chain via YAML code generation  **Communication:** Precise, unambiguous, factual. No emojis, DRY prose.  

**R-A-R Management:** RequestHub orchestrates all routes with DTO-driven validation**Documentation:** Update README.md and HANDOVER.md only. Report progress in chat.  

**Code Quality:** Type hints required, async/await patterns, 85% test coverage.  

**Intertwined:** Tools create Request DTOs → RequestHub validates/enriches → Services execute**Review:** All AI-generated code requires human validation.



### Key Directories## Repository Context

- `src/pydantic_models/` - 124 models, 23 Request/Response pairs

- `src/coreservice/` - RequestHub (not implemented yet)**Name:** my-tiny-data-collider  

- `src/casefileservice/` - Business logic services**Stack:** Python 3.11+, FastAPI, Pydantic, Firebase  

- `config/methods_inventory_v1.yaml` - 26 method definitions**Architecture:** Service-Repository pattern, tool-based AI integration  

- `config/models_inventory_v1.yaml` - 124 model definitions**Primary Branch:** develop  

- `config/toolsets/` - Tool YAML definitions**Current Feature:** feature/dto-inheritance (READY FOR MERGE)  

- `scripts/` - generate_tools.py, validate_dto_alignment.py, show_tools.py**Status:** 100% DTO compliance (23/23 operations), 52 models across 6 layers

- `HANDOVER.md` - Current state, architecture, roadmap

### Core Directories

## Development Standards- `src/pydantic_models/` - Data models (100% DTO coverage, 23/23 operations)

- `src/casefileservice/` - Casefile CRUD operations

### Code Pattern- `src/communicationservice/` - Chat session management

```python- `src/tool_sessionservice/` - Tool execution lifecycle

async def method_name(- `src/pydantic_ai_integration/` - AI tool system and registries

    self,  - `method_registry.py` - MANAGED_METHODS global registry (26 methods)

    request: RequestModel,  - `model_registry.py` - Model discovery APIs (52 models)

    context: MDSContext,  - `tool_decorator.py` - MANAGED_TOOLS registry with @register_mds_tool

    session: ToolSession- `config/` - YAML configurations

) -> ResponseModel:  - `methods_inventory_v1.yaml` - 26 method definitions

    """Docstring with Args, Returns, Raises."""  - `models_inventory_v1.yaml` - 52 model definitions across 6 layers

    result = await self.repository.operation(request.payload)  - `tool_schema_v2.yaml` - Tool schema with method inheritance

    return ResponseModel(payload=result)  - `toolsets/` - Tool YAML definitions (core, helpers, prototypes, workflows)

```  - `policies/` - Audit, security, and session policies

- `scripts/` - Automation tools

### Architecture  - `generate_tools.py` - Tool generation from YAML

- **Models** (L0-L2): Pydantic DTOs  - `validate_dto_alignment.py` - Parameter drift detection

- **Methods** (L3): MANAGED_METHODS registry  - `show_tools.py` - Display registered tools

- **Tools** (L4): Generated wrappers- `AI/` - AI collaboration framework (this directory)

- **YAML** (L5): Declarative configs

### Key Files

**Flow:** Tool creates DTO → RequestHub validates → Service executes- `HANDOVER.md` - Current development state and session notes

- `.github/copilot-instructions.md` - GitHub Copilot configuration

### Tool Generation- `config/methods_inventory_v1.yaml` - Method registry (26 methods)

```bash- `config/models_inventory_v1.yaml` - Model registry (52 models)

python scripts/generate_tools.py            # Generate all

python scripts/validate_dto_alignment.py    # Check drift## Development Standards

python scripts/show_tools.py                # List tools

```### Code Pattern

```python

## Communication Standardsasync def method_name(self, request: RequestModel) -> ResponseModel:

    """Docstring with Args, Returns, Raises."""

- Update README.md and HANDOVER.md only    result = await self.repository.operation(request.payload)

- No intermediate docs    return ResponseModel(

- DRY, factual, systematic        request_id=request.request_id,

- Code examples over prose        status=RequestStatus.COMPLETED,

- No emojis        payload=result

    )

## Commit Format```



```### Architecture

type(scope): Short description- **6-Layer Model System:** L0 (Base) → L1 (Payloads) → L2 (DTOs) → L3 (Methods) → L4 (Tools) → L5 (YAML)

- **Parameter Flow:** Define once in DTO (L1), auto-extract to Method (L3), auto-inherit to Tool (L4)

- Factual changes- **R-A-R Pattern:** Request-Action-Response for all operations (23/23 compliant)

```- **Tool Registration:** `@register_mds_tool` decorator for AI integration

- **Single Source of Truth:** Parameters defined in DTOs, inherited everywhere

Types: feat, fix, refactor, test, docs, chore

### Tool Engineering

## References```bash

# Generate tools from YAML

| Topic | Location |python scripts/generate_tools.py

|-------|----------|

| Copilot Instructions | ../.github/copilot-instructions.md |# Validate DTO alignment (detect parameter drift)

| Current State | ../HANDOVER.md |python scripts/validate_dto_alignment.py

| Conversation Standards | practices/conversation-practices.md |

| VS Code Setup | practices/vscode-setup.md |# Display registered tools

| Prompt Templates | prompts/README.md |python scripts/show_tools.py

| Method Registry | ../config/methods_inventory_v1.yaml |```

| Model Registry | ../config/models_inventory_v1.yaml |

Tool YAML structure (parameters auto-inherited from method):
```yaml
name: tool_name
implementation:
  type: api_call
  method_name: workspace.casefile.create_casefile
# Parameters auto-inherited from method DTO
# Override only for transformations or additional UI fields
```

## Testing

```bash
pytest                              # All tests
pytest --cov=src --cov-report=html # With coverage
pytest tests/integration/          # Integration only
pytest -m unit                      # Unit tests only
```

**Requirements:** 85% coverage minimum for AI-generated code, comprehensive assertions, proper mocking.  
**Standards:** All service methods require tests, edge cases covered, async patterns validated.

## Quality Gates

**Prohibited AI Uses:** Security-sensitive authentication, production configs, legal docs, financial logic  
**Required:** Type hints everywhere, async/await, error handling, docstrings  
**Standards:** Pylint >8.0, API response <200ms, input validation

## Commit Format

```
type(scope): Short description

- Factual bullet points
- No emojis, code over prose
```

Types: feat, fix, refactor, test, docs, chore

## Documentation References

| Topic | Location |
|-------|----------|
| Copilot Instructions | ../.github/copilot-instructions.md |
| Current Development State | ../HANDOVER.md |
| Conversation Standards | practices/conversation-practices.md |
| Quality Assurance | workflows/quality-assurance.md |
| Develop Branch Guide | workflows/develop-branch-guide.md |
| Prompt Templates | prompts/README.md |
| VS Code Setup | practices/vscode-setup.md |
| Method Registry | ../config/methods_inventory_v1.yaml |
| Model Registry | ../config/models_inventory_v1.yaml |
| Tool Schema | ../config/tool_schema_v2.yaml |