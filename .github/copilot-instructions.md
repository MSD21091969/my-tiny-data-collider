>md# Copilot Instructions

**Updated:** October 9, 2025
**Status:** 8/8 tests | 26 methods | 124 models | 3 tools



## Architecture

**Stack:** Python 3.13+, FastAPI, Pydantic, Firebase
**Pattern:** R-A-R (Request-Action-Response)
**Flow:** HTTP → Tool → RequestHub → Service → Repository

### 6-Layer Stack
```
L5: YAML config/toolsets/ (source of truth)
L4: Generated tools/ (Python code)
L3: MANAGED_METHODS (26 methods)
L2: DTOs operations/ (Request/Response)
L1: Payloads workspace/ (business data)
L0: BaseRequest/BaseResponse (base classes)
```

**Rule:** DTO defines → Method extracts → Tool inherits (zero duplication)



## R-A-R Pattern

```python
# L1: Payload (business data)
class CreateCasefilePayload(BaseModel):
    title: str
    description: str

# L2: Request (execution envelope)
class CreateCasefileRequest(BaseRequest):
    operation: Literal["create_casefile"]
    payload: CreateCasefilePayload
    user_id: str

# L2: Response
class CreateCasefileResponse(BaseResponse):
    payload: Casefile

# Service (business logic only)
async def create_casefile(
    self,
    request: CreateCasefileRequest
) -> CreateCasefileResponse:
    casefile = await self.repository.create(request.payload)
    return CreateCasefileResponse(payload=casefile)
```



## Tool Generation

```yaml
# config/toolsets/core/create_casefile.yaml
name: create_casefile
implementation:
  type: api_call
  method_name: workspace.casefile.create_casefile
# Parameters auto-inherited from CreateCasefileRequest
```

```bash
python scripts/generate_tools.py          # YAML → Python
python scripts/validate_dto_alignment.py  # Check drift
python scripts/show_tools.py              # List tools
```



## Key Files

**Core:**
- `src/coreservice/request_hub.py` - Central orchestrator
- `src/casefileservice/` - Casefile CRUD
- `src/pydantic_models/` - 124 models (6 layers)

**Config:**
- `config/methods_inventory_v1.yaml` - 26 methods
- `config/models_inventory_v1.yaml` - 124 models
- `config/toolsets/` - YAML tool definitions

**Scripts:**
- `scripts/generate_tools.py` - YAML → Python
- `scripts/validate_dto_alignment.py` - Check drift

**Docs:**
- `HANDOVER.md` - Current state
- `README.md` - Quick start
- `AI/prompts/` - Templates (DTO, tool, bug, refactor)



## Standards

**Code:**
- Type hints required
- Async/await for I/O
- Google-style docstrings
- 80% test coverage minimum

**Models:**
- Follow R-A-R pattern
- No parameter duplication
- DTOs define once, inherit everywhere

**Commits:**
```
type(scope): description
- Factual changes
```
Types: feat, fix, refactor, test, docs, chore

**Docs:**
- Update HANDOVER.md only
- DRY, factual, code over prose



## Prohibited

❌ Parameter duplication between layers
❌ Validation in services (RequestHub only)
❌ Tools calling methods directly
❌ Intermediate documentation
❌ Breaking R-A-R pattern



## See Also

- `ARCHITECTURE.md` - System architecture, services, workflows
- `AI/recommendations/FASTAPI-REFACTORING-PLAN.md` - Phase 8-10 implementation guide
- `AI/decisions/` - Architecture decision records
