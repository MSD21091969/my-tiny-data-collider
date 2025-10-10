# System Architecture

**Status:** Phase 8 Complete | 24/28 tests passing | 80%+ coverage
**Version:** 1.1
**Date:** October 10, 2025

---

## System State

- **Tests:** 24/28 passing (4 integration test failures - RequestHub hooks)
- **Methods:** 26 registered in MANAGED_METHODS
- **Models:** 124 total (52 operational)
- **Tools:** 3 generated
- **Coverage:** 80%+ across core services
- **Phase 8:** Router migration complete (tool_session, chat → RequestHub orchestration)

---

## 6-Layer Contract Stack

```
L0: BaseRequest/BaseResponse              # src/pydantic_models/base/
L1: Business payloads                     # src/pydantic_models/workspace/
L2: Request/Response DTOs                 # src/pydantic_models/operations/
L3: MANAGED_METHODS                       # config/methods_inventory_v1.yaml
L4: MANAGED_TOOLS (generated)             # src/pydantic_ai_integration/tools/generated/
L5: YAML source of truth                  # config/toolsets/
```

**DRY Principle:** Define once in DTO → Auto-extract to Method → Auto-inherit to Tool

---

## Request Flow

```
HTTP Request
  ↓
FastAPI Route
  ↓
BaseRequest[PayloadT] (hooks, context_requirements, policy_hints)
  ↓
RequestHub.dispatch()
  ├─ _prepare_context() [load session, casefile, policy]
  ├─ _run_hooks("pre")
  ├─ Service execution
  ├─ _run_hooks("post")
  └─ _attach_hook_metadata()
  ↓
BaseResponse[PayloadT] (with hook_events metadata)
  ↓
FastAPI Response
```

---

## Core Services

### 1. RequestHub (Central Orchestrator)
**Location:** `src/coreservice/request_hub.py`
**Purpose:** Orchestrate all R-A-R workflows with hooks

**Methods:**
- `dispatch(request)` - Main entry point
- `_prepare_context()` - Load session, casefile, policy
- `_run_hooks()` - Execute pre/post hooks
- `_execute_casefile_create()` - Handler for create_casefile
- `_execute_casefile_with_session()` - Composite workflow

**Hooks:**
- `metrics` - Track execution time, status
- `audit` - Log user actions, changes
- `session_lifecycle` - Manage session expiration (planned Phase 8)

### 2. CasefileService
**Location:** `src/casefileservice/service.py`
**Methods:** 13 operations (CRUD, ACL, workspace sync)
**Repository:** Dual-mode (Firestore/memory)

### 3. ToolSessionService
**Location:** `src/tool_sessionservice/service.py`
**Methods:** 5 operations (create, get, list, close, process_tool_request)
**Purpose:** Manage tool execution lifecycle

### 4. CommunicationService
**Location:** `src/communicationservice/service.py`
**Methods:** 6 operations (chat sessions + LLM processing)
**Purpose:** Handle chat sessions with tool execution

### 5. AuthService
**Location:** `src/authservice/`
**Components:** `routes.py` (endpoints), `token.py` (JWT)
**Dev Mode:** Hardcoded Sam user (`sam123/Sam`)

---

## R-A-R Pattern

```python
# L1: Payload (business data only)
class CreateCasefilePayload(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(default="")

# L2: Request (execution envelope)
class CreateCasefileRequest(BaseRequest[CreateCasefilePayload]):
    operation: Literal["create_casefile"] = "create_casefile"
    payload: CreateCasefilePayload

# L2: Response (result envelope)
class CreateCasefileResponse(BaseResponse[CasefileCreatedPayload]):
    pass
```

---

## Tool Generation Pipeline

```
YAML Tool Definition (config/toolsets/**/*.yaml)
  ↓ (scripts/generate_tools.py)
  ├─ Load YAML
  ├─ Resolve method_name → MANAGED_METHODS
  ├─ Extract parameters from method's request payload
  ├─ Generate Pydantic params model
  ├─ Generate tool function with @register_mds_tool
  └─ Write to src/pydantic_ai_integration/tools/generated/
  ↓
Generated Tool (*.py)
  ↓ (scripts/import_generated_tools.py)
MANAGED_TOOLS Registry
```

---

## Registries

### MANAGED_METHODS (26 methods)
**Location:** `src/pydantic_ai_integration/method_registry.py`
**Source:** Auto-loaded from `config/methods_inventory_v1.yaml`

**Discovery APIs:**
- `get_registered_methods()` - All methods
- `get_method_definition(name)` - Get metadata
- `get_method_parameters(name)` - Extract parameters from request payload
- `get_methods_by_domain(domain)` - Filter by domain

### MANAGED_TOOLS (generated tools)
**Location:** `src/pydantic_ai_integration/tool_decorator.py`
**Source:** Generated from YAML + method definitions

### MANAGED_MODELS (124 models)
**Location:** `src/pydantic_ai_integration/model_registry.py`
**Source:** Auto-discovered from `config/models_inventory_v1.yaml`

---

## Classification Taxonomy

**Domain:** `workspace` (15 methods), `communication` (11), `automation` (4)
**Subdomain:** `casefile`, `casefile_acl`, `google_workspace`, `chat_session`, etc.
**Capability:** `create`, `read`, `update`, `delete`, `search`, `process`
**Complexity:** `atomic` (24), `composite` (5), `pipeline` (2)
**Maturity:** `stable` (23), `beta` (7), `experimental` (Phase 8)
**Integration Tier:** `internal` (18), `external` (6), `hybrid` (6)

---

## Persistence

### Dual-Mode Repository Pattern
```python
class CasefileRepository:
    def __init__(self):
        self.mode = os.environ.get("CASEFILE_REPOSITORY_MODE", "firestore")
        # "firestore" - Production (Google Cloud Firestore)
        # "memory" - Development/testing (in-memory dict)
```

**Environment Variables:**
- `FIRESTORE_DATABASE=mds-objects`
- `GOOGLE_APPLICATION_CREDENTIALS=/path/to/key.json`
- `CASEFILE_REPOSITORY_MODE=firestore` (override default)

---

## API Structure

### FastAPI Application
**Location:** `src/pydantic_api/app.py`

**Routers:**
- `/auth` - JWT authentication
- `/casefiles` - Casefile operations
- `/tool-sessions` - Tool session management
- `/chat` - Chat sessions
- `/health` - Health check

**Dependency Injection:**
```python
# Standard route (direct service call)
@router.post("/", response_model=CreateCasefileResponse)
async def create_casefile(
    service: CasefileService = Depends(get_casefile_service),
    current_user: Dict = Depends(get_current_user)
):
    return await service.create_casefile(request)

# RequestHub route (orchestrated with hooks)
@router.post("/hub", response_model=CreateCasefileResponse)
async def create_casefile_via_hub(
    hub: RequestHub = Depends(get_request_hub),
    current_user: Dict = Depends(get_current_user)
):
    request.hooks = ["metrics", "audit"]
    return await hub.dispatch(request)
```

---

## Development Workflow

### Daily Commands
```bash
# Clean and regenerate tools
.\scripts\cleanup_generated_files.ps1
python scripts/generate_tools.py
python scripts/import_generated_tools.py

# Validate alignment
python scripts/validate_dto_alignment.py

# Run tests
pytest tests/ -v --cov=src
```

### Add New Feature
1. Create models in `src/pydantic_models/{layer}/`
2. Update `config/models_inventory_v1.yaml`
3. Add method to `config/methods_inventory_v1.yaml`
4. Implement service logic in `src/{service}/service.py`
5. Create tool YAML in `config/toolsets/`
6. Generate: `python scripts/generate_tools.py`
7. Test: `pytest tests/ -v`

---

## Pending Work (Phases 8-10)

### Phase 8: Service Integration ✅ COMPLETE
**Status**: Router migration complete - tool_session and chat routers migrated to RequestHub orchestration
**Special Cases**: `send_message` and `execute_tool` endpoints remain direct service calls (performance optimization)
**Next**: Extend RequestHub dispatch to handle all 26 methods, migrate casefile routes

### Phase 9: Middleware
- API versioning (`/v1/` prefix)
- Authentication middleware (JWT validation)
- Request logging (trace IDs)
- Rate limiting (60 req/min per user)
- Error handling (standardized responses)

### Phase 10: Production Readiness
- Firestore connection pooling
- Redis caching layer
- Prometheus metrics
- Security audit
- Load testing

---

## API Contract Patterns

### Multi-Pattern Architecture
**Strategic Diversity**: Different contract patterns based on operation complexity and performance requirements

#### 1. CRUD Operations (RequestHub Orchestration)
```python
# Full R-A-R pattern with orchestration
@router.post("/", response_model=CreateCasefileResponse)
async def create_casefile(
    request: CreateCasefileRequest,
    hub: RequestHub = Depends(get_request_hub)
):
    return await hub.dispatch(request)  # Orchestrated with hooks
```

#### 2. Execution Operations (Direct Service Calls)
```python
# Direct domain request bypassing HTTP envelope
@router.post("/execute", response_model=ToolResponse)
async def execute_tool(
    request: ToolRequest,  # Domain layer, not RequestEnvelope
    service: ToolSessionService = Depends(get_tool_session_service)
):
    return await service.process_tool_request(request)  # Direct call for performance
```

#### 3. Composite Operations (Aggregated Workflows)
```python
# Multi-step orchestration with context enrichment
@router.post("/with-session", response_model=CompositeResponse)
async def create_casefile_with_session(
    request: CompositeRequest,
    hub: RequestHub = Depends(get_request_hub)
):
    return await hub.dispatch(request)  # Complex workflow orchestration
```

### ToolRequest vs RequestEnvelope
- **RequestEnvelope**: HTTP transport layer (auth, tracing, client_info)
- **ToolRequest**: Domain execution layer (direct service calls for performance)
- **Architectural Trade-off**: Consistency vs performance optimization

**See:** `AI/recommendations/FASTAPI-REFACTORING-PLAN.md` for detailed implementation guide

---

## Key Files

**Core:**
- `src/coreservice/request_hub.py` - Central orchestrator
- `src/pydantic_models/base/envelopes.py` - BaseRequest/BaseResponse

**Configuration:**
- `config/methods_inventory_v1.yaml` - 26 methods
- `config/models_inventory_v1.yaml` - 124 models
- `config/tool_schema_v2.yaml` - Tool schema

**Scripts:**
- `scripts/generate_tools.py` - Tool generation
- `scripts/validate_dto_alignment.py` - Parameter validation
- `scripts/show_tools.py` - List registered tools

**Tests:**
- `tests/integration/test_request_hub_integration.py` - RequestHub tests (14 tests)
- `tests/integration/test_request_hub_fastapi.py` - FastAPI integration (8 tests)

---

## Quick Reference

**Test:** `pytest tests/ -v`
**Coverage:** `pytest tests/ --cov=src --cov-report=html`
**Type Check:** `mypy src/`
**Lint:** `pylint src/ --rcfile=.pylintrc`
**Generate Tools:** `python scripts/generate_tools.py`
**Validate:** `python scripts/validate_dto_alignment.py`
**Show Tools:** `python scripts/show_tools.py`
**Start API:** `uvicorn src.pydantic_api.app:app --reload --port 8000`

---

**For Refactoring:** See `AI/recommendations/FASTAPI-REFACTORING-PLAN.md`
**For Contributing:** See `CONTRIBUTING.md`
