# HANDOVER - feature/dto-inheritance

**Branch:** feature/dto-inheritance  
**Date:** October 8, 2025 at 19:05  
**Status:** READY FOR MERGE

**Latest Session:** Tool Engineering Architecture Documentation
- Parameter inheritance system fully documented
- Composite tool orchestration patterns explained
- R-A-R route hooks implementation guide added
- HTTP API usage examples with complete request/response flows
- Validation and synchronization workflows documented

---

## Summary

**DTO Compliance:** 100% (23/23 operations - R-A-R pattern)  
**Parameter Flow:** DTO → Method → Tool (single source of truth)  
**Model Registry:** 52 models across 6 layers  
**Artifacts:** All configs, registries, validation scripts complete

---

## Architecture

### 6-Layer System
```
L0: Base Infrastructure (BaseRequest/BaseResponse)
L1: Payload Models (business data - CreateCasefilePayload)
L2: Request/Response DTOs (execution envelopes)
L3: Method Definitions (metadata - MANAGED_METHODS)
L4: Tool Definitions (metadata - MANAGED_TOOLS)
L5: YAML Configuration (source of truth)
```

### Parameter Flow
```
L1 Payload.title: str
    ↓ AUTO-EXTRACT
L3 MethodParameterDef(name="title", type="str")
    ↓ AUTO-INHERIT
L4 ToolParameterDef(name="title", type="string")
```

**Rule:** Define once in DTO, inherit everywhere

---

## R-A-R Pattern

```python
class {Action}Payload(BaseModel):      # L1: Business data
    field: str

class {Action}Request(BaseRequest[{Action}Payload]):  # L2: Envelope
    operation: Literal["action_name"]

class {Action}Response(BaseResponse[{Result}Payload]):
    pass
```

---

## Completed Tasks (14/14)

### Foundation
- DTO Audit (100% compliance, ChatRequest fixed)
- Parameter extraction (get_method_parameters())
- Parameter alignment audit (no drift)

### Model System  
- Google Workspace models decision (external APIs = plain Pydantic)
- Models inventory (models_inventory_v1.yaml - 52 models)
- Model registry (model_registry.py)

### Tool Inheritance
- Tool schema v2 (method_name references, optional params)
- Validation script (validate_dto_alignment.py)

### Documentation
- Model classification docs (6-layer taxonomy)
- Architecture diagram (parameter flow)

### Release
- Model-method alignment (100% coverage)
- Version documentation

### Tool Engineering Architecture (Session Oct 8, 19:05)
- Parameter inheritance system documentation
- Composite vs 1:1 tool patterns
- HTTP API usage guide with examples
- R-A-R route hooks implementation options
- Complete validation workflow documentation
- Tool definition models reference (MethodParameterDef, ManagedMethodDefinition, ManagedToolDefinition)

---

## Artifacts Created

**Config:**
- config/models_inventory_v1.yaml - 52 models by layer/domain
- config/tool_schema_v2.yaml - Method inheritance support

**Code:**
- src/pydantic_ai_integration/model_registry.py - Discovery APIs
- src/pydantic_ai_integration/method_registry.py - Parameter extraction
- scripts/validate_dto_alignment.py - Drift detection

**Docs:**
- docs/models/README.md - Layer taxonomy
- docs/architecture/model_flow_diagram.md - Parameter flow
- docs/decisions/google_workspace_model_classification.md - External API decision

---

## Key Implementation

### Parameter Extraction
```python
def extract_parameters_from_model(payload_class: Type[BaseModel]):
    params = []
    for field_name, field_info in payload_class.model_fields.items():
        params.append(MethodParameterDef(
            name=field_name,
            param_type=str(field_info.annotation),
            required=field_info.is_required(),
            description=field_info.description or ""
        ))
    return params
```

### Tool Inheritance
```python
# Tool YAML references method
implementation:
  type: api_call
  method_name: workspace.casefile.create_casefile

# Parameters auto-inherited from method's request payload
```

---

## Session Communication Policy

**Documentation Updates:** README.md and HANDOVER.md only - no intermediate docs  
**Progress Reporting:** In-chat updates, not separate markdown files  
**Style:** No emojis, DRY factual prose, systematic structure  
**Code Quality:** Type hints required, async/await, 85% test coverage minimum

---

## Next Steps

**Priority: Full R-A-R Implementation with RequestHub**

See "Full R-A-R Implementation Roadmap" section for complete 8-phase plan.

**Immediate Actions (October 8-9, 2025):**
1. Create `src/coreservice/policy_patterns.py` - Load policy templates into Python patterns
2. Create `src/coreservice/request_hub.py` - Core orchestration class
3. Update `BaseRequest` with metadata field for policy hints
4. Write unit tests for RequestHub validation patterns

**This Week (October 8-12, 2025):**
1. Complete Phase 1-2: RequestHub core + pattern loader
2. Update `generate_tools.py` to apply policy templates
3. Test RequestHub integration with one service (casefileservice)
4. Regenerate tools with policy metadata

**Next Week (October 15-19, 2025):**
1. Complete Phase 3-4: DTO enhancement + tool generation
2. Implement Phase 5: Downstream hooks framework
3. Begin Phase 6: Service integration (remove scattered checks)

**Legacy Next Steps (Preserved for Reference):**
1. Merge to develop
2. Deploy validation script to CI/CD
3. Update tool YAMLs to use method_name references
4. Remove redundant parameter definitions from existing tools
5. Implement composite tool orchestration for multi-step workflows
6. Add R-A-R route hooks for process monitoring and metrics
7. Create example composite tools demonstrating workflow patterns

---

## Maintenance: Synchronization Requirements

### Foundation Status (October 8, 2025)

**✅ SYNCHRONIZED**
- methods_inventory_v1.yaml: 26 methods loaded into MANAGED_METHODS at startup
- models_inventory_v1.yaml: 124 models inventoried (regenerated from code)
- tool_schema_v2.yaml: Aligned with R-A-R pattern
- Templates: Jinja2 and markdown templates marked with sync status

**Implementation:**
- Method loader: `register_methods_from_yaml()` called in `src/__init__.py`
- Model scanner: `scripts/scan_models.py` for inventory regeneration
- All config files marked: "October 8, 2025 - Foundation Sync"

### System Synchronization Workflow

**Complete Workflow (Quick Reference):**
```powershell
# Navigate to project
cd C:\Users\HP\Documents\Python\my-tiny-data-collider

# 1. Clean slate
.\scripts\cleanup_generated_files.ps1

# 2. Generate tools
python scripts/generate_tools.py

# 3. Import tools
python scripts/import_generated_tools.py

# 4. Verify registration
python scripts/show_tools.py

# 5. Validate alignment
python scripts/validate_dto_alignment.py

# 6. Run tests
pytest tests/test_imports.py -v
```

**Troubleshooting:**
- "Method not found in MANAGED_METHODS": Check `config/methods_inventory_v1.yaml` has the method
- "Model class not found": Check method's request_model_class/response_model_class points to existing DTO
- "Parameter mismatch": Remove manual parameters from tool YAML to use auto-inheritance
- Import errors: Check generated Python files for syntax errors, re-run `generate_tools.py`

**Synchronization Checklist:**
- [ ] No generated tool import errors
- [ ] All tests passing (3/3 in test_imports.py)
- [ ] `validate_dto_alignment.py` reports 0 errors
- [ ] `show_tools.py` lists all expected tools
- [ ] Tool parameter counts match DTO field counts
- [ ] 100% R-A-R pattern compliance maintained
- [ ] 26 methods in MANAGED_METHODS
- [ ] 124 models in inventory

### When Models Change (src/pydantic_models/)

**Update Required:**
1. `config/models_inventory_v1.yaml` - Add/remove model entries, update field lists
2. Method definitions - Update `models.request`/`models.response` references in `config/methods_inventory_v1.yaml`
3. Tool generation - Re-run `python scripts/generate_tools.py` for tools inheriting from affected methods
4. API schemas - Regenerate OpenAPI specs if models affect external APIs

**Validation:**
```bash
python scripts/validate_dto_alignment.py  # Check model references
```

### When Methods Change (config/methods_inventory_v1.yaml)

**Update Required:**
1. Tool YAML configs - Update `method_name` references if method names change
2. Tool generation - Re-run `python scripts/generate_tools.py` for affected tools
3. MANAGED_TOOLS registry - Refresh via `python scripts/import_generated_tools.py`
4. Tests - Update test cases referencing old method names/signatures

**Validation:**
```bash
python scripts/validate_dto_alignment.py  # Check method references
python scripts/show_tools.py             # Verify tool registration
```

### When Tool Generation Changes (YAML configs, templates)

**Update Required:**
1. Generated tool code - Re-run `python scripts/generate_tools.py`
2. MANAGED_TOOLS registry - Run `python scripts/import_generated_tools.py`
3. Test files - Update if tool signatures change
4. API discovery - Refresh tool discovery endpoints

**Validation:**
```bash
python scripts/generate_tools.py --validate-only  # Validate configs
python scripts/run_continuous_integration_tests.py  # Run full test suite
```

### Change Impact Matrix

| Change Type | Affects Methods | Affects Tools | Affects Models | Requires Regen |
|-------------|----------------|---------------|----------------|---------------|
| Model field | Update YAML refs | Re-inherit params | Update inventory | Tools |
| Method signature | Update YAML | Update YAML refs | - | Tools |
| Tool config | - | Update YAML | - | Tools + Registry |
| Classification | Update YAML | Optional override | - | - |

### Recommended Sync Check

```bash
# After any change to models, methods, or tools:
python scripts/validate_dto_alignment.py
python scripts/generate_tools.py --validate-only
python scripts/run_continuous_integration_tests.py
```

---

## Tool Engineering Architecture: Complete Implementation Guide

### Parameter Inheritance System

**Core Concept:** Parameters defined once in DTOs, inherited throughout the system.

**Flow:**
```
L1 DTO Field → L3 Method Parameter → L4 Tool Parameter → Runtime Validation
```

**Method Parameter Extraction:**
```python
def extract_parameters_from_payload(payload_class: Type[BaseModel]) -> List[MethodParameterDef]:
    """Extract parameters from Pydantic payload model."""
    params = []
    for field_name, field_info in payload_class.model_fields.items():
        # Extract type, required status, description, constraints
        params.append(MethodParameterDef(
            name=field_name,
            param_type=str(field_info.annotation),
            required=field_info.is_required(),
            description=field_info.description or "",
            min_value=getattr(field_info, 'ge', None),
            max_value=getattr(field_info, 'le', None),
            # ... other constraints
        ))
    return params
```

**Tool Inheritance:**
```yaml
# Simple method wrapper
name: create_casefile_tool
implementation:
  type: api_call
  method_name: create_casefile
# Parameters auto-inherited from method

# Composite orchestration tool
name: process_casefile_workflow
parameters:
  - name: casefile_title      # Orchestration parameter
  - name: document_urls       # Orchestration parameter
implementation:
  type: composite
  composite:
    steps:
      - tool: create_casefile_inherited
      - tool: upload_documents
      - tool: analyze_documents
```

### Tool Types and Classification

**1:1 Method Tools:**
- Direct wrappers around single methods
- Inherit all parameters from method's request DTO
- Classification matches method classification
- Example: `create_casefile_tool` → `create_casefile` method

**Composite Tools:**
- Orchestrate multiple sub-tools/methods
- Define orchestration-level parameters
- Independent classification for workflow complexity
- Example: Multi-step casefile processing workflow

**Classification Taxonomy:**
```yaml
domain: workspace | communication | automation | utilities
subdomain: casefile | gmail | tool_session | etc.
capability: create | read | update | delete | process | search
complexity: atomic | composite | pipeline
maturity: experimental | beta | stable | deprecated
integration_tier: internal | external | hybrid
```

### HTTP API Usage

**Tool Execution Endpoint:** `POST /tool-sessions/execute`

**Request Structure:**
```json
{
  "user_id": "user123",
  "operation": "tool_execution",
  "payload": {
    "tool_name": "process_casefile_workflow",
    "parameters": {
      "casefile_title": "Legal Case #2025-001",
      "document_urls": ["https://...", "https://..."],
      "analysis_type": "full"
    },
    "casefile_id": "cf_123",
    "session_request_id": "req_456"
  },
  "session_id": "session_789"
}
```

**Response with Events:**
```json
{
  "status": "COMPLETED",
  "payload": {
    "result": {
      "casefile_id": "cf_new_001",
      "document_ids": ["doc_1", "doc_2"],
      "analysis_result": {...}
    },
    "events": [
      {"type": "tool_start", "timestamp": "..."},
      {"type": "subtool_complete", "subtool": "create_casefile"},
      {"type": "tool_complete", "duration_ms": 2500}
    ]
  }
}
```

### Parameter Alignment Validation

**Purpose:** Ensure tools stay synchronized with referenced methods.

**Validation Checks:**
```python
# Extract method parameters
method_params = method_registry.get_method_parameters(method_name)

# Compare with tool parameters
tool_params = tool.get('parameters', [])
method_param_names = {p.name for p in method_params}

missing = method_param_names - set(tool_params.keys())  # ERROR if missing required
extra = set(tool_params.keys()) - method_param_names    # INFO for extensions
```

**Command:**
```bash
python scripts/validate_dto_alignment.py
```

### R-A-R Route Hooks

**Available Injection Points:**

**1. Service Method Hooks (Recommended):**
```python
class ToolSessionService:
    async def process_tool_request(self, request: ToolRequest) -> ToolResponse:
        await self.on_tool_request_start(request)  # PRE hook
        
        try:
            result = await self._execute_tool(request)
            await self.on_tool_request_success(request, result)  # SUCCESS hook
            return result
        except Exception as e:
            await self.on_tool_request_failure(request, e)  # FAILURE hook
            raise
    
    async def on_tool_request_start(self, request: ToolRequest):
        # Hook: Log session start, emit events, update metrics
        pass
        
    async def on_tool_request_success(self, request: ToolRequest, response: ToolResponse):
        # Hook: Log completion, emit tool events, update duration metrics
        pass
        
    async def on_tool_request_failure(self, request: ToolRequest, error: Exception):
        # Hook: Log failure, emit error events, update error metrics
        pass
```

**2. FastAPI Middleware (Global):**
```python
class RARHooksMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # PRE-REQUEST HOOK
        await self.log_request_start(request)
        
        response = await call_next(request)
        
        # POST-RESPONSE HOOK
        await self.log_request_complete(request, response)
        
        return response
    
    async def log_request_start(self, request: Request):
        # Hook: Tool execution started
        pass
        
    async def log_request_complete(self, request: Request, response: Response):
        # Hook: Tool execution completed with duration
        pass
```

**3. Dependency Injection:**
```python
async def tool_execution_hooks(
    request: ToolRequest,
    service: ToolSessionService = Depends(get_tool_session_service)
) -> ToolResponse:
    # PRE-EXECUTION HOOK
    start_time = datetime.now()
    await service.emit_event("tool_execution_start", {
        "tool_name": request.payload.tool_name,
        "session_id": request.session_id,
        "start_time": start_time.isoformat()
    })
    
    # EXECUTE
    response = await service.process_tool_request(request)
    
    # POST-EXECUTION HOOK
    duration_ms = (datetime.now() - start_time).total_seconds() * 1000
    await service.emit_event("tool_execution_complete", {
        "tool_name": request.payload.tool_name,
        "session_id": request.session_id,
        "duration_ms": duration_ms,
        "status": response.status.value
    })
    
    return response
```

**4. Event-Driven Hooks:**
```python
class ToolExecutionEvents:
    @staticmethod
    async def on_tool_start(request: ToolRequest):
        # Emit: tool.session.request.start
        # Log: Tool execution initiated
        pass
        
    @staticmethod  
    async def on_tool_complete(request: ToolRequest, response: ToolResponse, duration_ms: float):
        # Emit: tool.session.request.complete
        # Log: Tool execution finished with duration
        pass
        
    @staticmethod
    async def on_tool_error(request: ToolRequest, error: Exception):
        # Emit: tool.session.request.error
        # Log: Tool execution failed
        pass
```

### Tool Definition Models

**MethodParameterDef:**
```python
class MethodParameterDef(BaseModel):
    """Extracted on-demand from request_model_class."""
    name: str
    param_type: str
    required: bool
    description: str | None = None
    default_value: Any = None
    min_value: float | None = None
    max_value: float | None = None
    min_length: int | None = None
    max_length: int | None = None
    pattern: str | None = None
```

**ManagedMethodDefinition (16 fields):**
```python
class ManagedMethodDefinition(BaseModel):
    # Identity
    name: str
    description: str
    version: str
    
    # Classification
    domain: str  # workspace, communication, automation
    subdomain: str  # casefile, gmail, tool_session
    capability: str  # create, read, update, delete, process, search
    complexity: str  # atomic, composite, pipeline
    maturity: str  # stable, beta, experimental
    integration_tier: str  # internal, external, hybrid
    
    # Execution
    request_model_class: Type[BaseModel] | None
    response_model_class: Type[BaseModel] | None
    implementation_class: str
    implementation_method: str
    
    # Tracking
    registered_at: datetime
```

**ManagedToolDefinition (12 fields):**
```python
class ManagedToolDefinition(BaseModel):
    # Identity
    name: str
    description: str
    version: str
    
    # Classification
    category: str
    tags: List[str]
    
    # Method Reference
    method_name: Optional[str]  # For inheritance
    
    # Parameters (inherited or explicit)
    parameters: List[ToolParameterDef]
    
    # Execution
    implementation: Optional[Callable[..., Awaitable[Dict[str, Any]]]]
    params_model: Optional[Type[BaseModel]]
    
    # Tracking
    registered_at: datetime
```

### Architecture Separation

**WHAT/HOW (Definitions):**
- Tool definitions, parameters, orchestration logic
- Method signatures, business rules, validation
- YAML configurations, inheritance mechanisms

**WHEN/WHERE (Process):**
- R-A-R hooks for timing, events, performance
- Session management, request tracking
- Audit trails, monitoring, metrics

**Benefits:**
- Clean separation of concerns
- Testable business logic vs monitoring
- Flexible instrumentation without coupling
- Scalable from atomic to composite operations

### Tool Generation Workflow

**Generate Tools:**
```bash
python scripts/generate_tools.py                    # All tools
python scripts/generate_tools.py tool_name         # Specific tool
python scripts/generate_tools.py --validate-only   # Validate only
```

**Import to Registry:**
```bash
python scripts/import_generated_tools.py
```

**Validate Alignment:**
```bash
python scripts/validate_dto_alignment.py
python scripts/show_tools.py
```

### Key Design Decisions

**1. Parameter Inheritance vs Explicit Definition:**
- Simple tools: Inherit from methods (DRY)
- Composite tools: Define orchestration parameters (abstraction)

**2. Classification Independence:**
- Methods: Business logic classification
- Tools: Operational classification (may differ for composites)

**3. Hook Architecture:**
- Service methods: Business logic monitoring
- Events: Loose coupling for extensibility
- Middleware: Global concerns (logging, metrics)

**4. Registry Design:**
- Methods: 16 fields, slim execution metadata
- Tools: 12 fields, pure execution metadata
- Parameters: Extracted on-demand, not stored

This architecture supports the full spectrum from simple method wrappers to complex orchestration workflows while maintaining clean separation between business logic and execution monitoring.

---

## System Architecture: Two Intertwined Systems

**Updated:** October 8, 2025 at 20:45  
**Status:** Design Complete - Implementation Pending

### System 1: Tool Engineering (Model→Method→Tool Chain)

**Purpose:** Generate executable tools from declarative YAML configs via method inheritance.

**Components:**
- **Models** (L0-L2): Pydantic DTOs defining request/response structures
- **Methods** (L3): Registry of 26 operations with classification metadata
- **Tools** (L4): Generated Python code wrapping methods
- **YAML Configs** (L5): Declarative tool definitions in `config/toolsets/`

**Current State:**
- 26 methods registered, 124 models inventoried
- Tool generation scripts ready (not yet executed)
- Parameter inheritance via DTO introspection
- No validation hooks at method level (methods are pure business logic)

**Key Principle:** Define parameters once in DTO, inherit everywhere via code generation.

### System 2: R-A-R Management (RequestHub Orchestration)

**Purpose:** Facilitate all R-A-R routes with smart DTO-driven validation, context injection, and hooks.

**Components:**
- **RequestHub**: Central orchestrator for validation, context, hooks
- **Request DTOs**: Declare field requirements per route
- **Services**: CasefileService, ToolSessionService, CommunicationService, Persistence
- **Hooks**: Optional downstream operations (metrics, audit, notification)

**Current State:**
- Architecture designed, not implemented
- Request DTOs exist (23 operations), need optional fields
- Services exist with scattered validation (needs centralization)
- No RequestHub implementation yet

**Key Principle:** Request DTO fields communicate requirements to RequestHub, which orchestrates the entire route.

### How They Intertwine

**Tool Engineering operates WITHIN R-A-R Management:**

```python
# Tool Engineering: Generated tool wrapper
async def update_casefile_tool(user_id, auth_token, casefile_id, payload, **kwargs):
    # Tool creates Request DTO
    request = UpdateCasefileRequest(
        user_id=user_id,
        auth_token=auth_token,
        casefile_id=casefile_id,
        payload=payload,
        hooks=kwargs.get('hooks', [])  # Optional behavioral hints
    )
    
    # R-A-R Management: RequestHub takes over
    return await request_hub.process(request, operation="update_casefile")
    # ↑ RequestHub validates, enriches context, calls service method, triggers hooks

# Inside RequestHub
class RequestHub:
    async def process(self, request: UpdateCasefileRequest, operation: str):
        # Validate what request declares
        await self._validate_auth(request.auth_token)
        session = await self._validate_session(request.session_id)
        
        # Enrich context
        context = await self.persistence.get_context(request.user_id)
        
        # Call service method (Tool Engineering's method)
        service = self._get_service(operation)
        result = await service.update_casefile(request, context, session)
        
        # Trigger hooks if requested
        for hook in request.hooks:
            await self._trigger_hook(hook, request, result)
        
        return result
```

**Dependency Chain:**
```
User Request
    ↓
Tool (L4) - Generated wrapper, creates Request DTO
    ↓
RequestHub - Validates DTO fields, enriches context
    ↓
Method (L3) - Pure business logic, no validation
    ↓
Service - Domain operations on enriched context
    ↓
RequestHub - Triggers hooks, updates persistence
    ↓
Response
```

**Critical Insight:** Tools don't call methods directly. Tools create Request DTOs, RequestHub orchestrates the entire route including method execution. This is why Tool Engineering and R-A-R Management are intertwined.

### Field-Based Communication Pattern

**Request DTOs are the communication interface between systems:**

```python
class UpdateCasefileRequest(BaseRequest):
    # Required fields (Tool Engineering must provide)
    user_id: str
    auth_token: str
    casefile_id: str
    payload: UpdateCasefilePayload
    
    # Optional fields (R-A-R Management honors)
    session_id: str | None = None           # If present, validate session
    context_requirements: List[str] = []     # If present, fetch context
    hooks: List[str] = []                    # If present, trigger hooks
    notify_user: bool = False                # Behavioral hint
    include_in_analysis: bool = False        # Behavioral hint
```

**RequestHub reads these fields to orchestrate:**
- `auth_token` present → validate auth
- `session_id` present → validate/load session
- `casefile_id` present → check permissions
- `context_requirements` populated → fetch MDSContext, ToolSession, etc.
- `hooks` populated → trigger metrics, audit, notification hooks
- `notify_user=True` → trigger communication service
- `include_in_analysis=True` → pass to analytics pipeline

**This is "smart communication" at the DTO level - fields declare intent, RequestHub executes.**

### Why This Timing Matters

**We haven't generated tools yet, so we can design the DTO contract NOW:**

1. **Tool Generation** will create wrappers that instantiate proper Request DTOs
2. **Request DTOs** will declare all required + optional fields upfront
3. **RequestHub** will validate/enrich based on what DTO declares
4. **Services** will receive validated requests + enriched context
5. **Hooks** will trigger based on DTO hints

**This is the RIGHT time to:**
- Define optional fields in BaseRequest (context_requirements, hooks, etc.)
- Document field conventions
- Design RequestHub validation logic
- Plan hook framework
- Generate tools that leverage this contract

### System Boundaries

**Tool Engineering:**
- Generates tool code from YAML
- Tools inherit parameters from method DTOs
- No validation, no hooks, no context management
- Pure wrapper around Request DTO creation

**R-A-R Management:**
- Validates Request DTOs
- Enriches with context (MDSContext, ToolSession, Casefile rules)
- Delegates to services (CasefileService, ToolSessionService, etc.)
- Triggers downstream hooks
- Updates persistence
- Returns Response DTOs

**Services (Existing):**
- Pure business logic
- Receive validated Request + enriched context
- No auth checks, no session management
- Return Response payload

**No Overlap:** Tool Engineering generates wrappers, R-A-R Management orchestrates execution, Services implement logic.

### Implementation Focus

**Phase 1-2 (This Week):**
- Implement RequestHub with field-based validation
- Add optional fields to BaseRequest (hooks, context_requirements)
- Update one service to use RequestHub pattern

**Phase 3-4 (Next Week):**
- Generate tools that create proper Request DTOs
- Tools optionally set hooks/context hints from YAML config
- Validate tool→request→hub→service flow

**Phase 5-8 (Following Weeks):**
- Build hook framework
- Migrate all services
- Update all routes
- Documentation

### Request DTO Field Conventions

**Fields communicate requirements to RequestHub:**

```python
# Identity & Auth
user_id: str                    # Who is making the request
auth_token: str                 # Authentication credential
admin_token: str | None         # Elevated privileges (admin ops)

# Context
session_id: str | None          # Active session (if needed)
casefile_id: str | None         # Casefile being operated on
document_id: str | None         # Document being accessed

# Behavioral Hints (Optional)
notify_user: bool = False       # Trigger user notification
include_in_analysis: bool = False  # Add to analytics
store_results: bool = True      # Persist operation results

# Context Enrichment (Optional)
context_requirements: List[str] = []  # What to fetch: ["mds_context", "recent_docs", "user_prefs"]

# Downstream Hooks (Optional)
hooks: List[str] = []           # Which hooks: ["metrics", "audit", "notification"]
```

**RequestHub behavior:**
- Required field missing → ValidationError
- `auth_token` present → validate with auth service
- `session_id` present → validate/load from ToolSessionService
- `casefile_id` present → check permissions via CasefileService
- `context_requirements` populated → fetch from Persistence/services
- `hooks` populated → trigger after operation completes

### RequestHub Implementation Pattern

```python
class RequestHub:
    async def process(self, request: BaseRequest, operation: str):
        # 1. Validate required fields
        self._check_required_fields(request)
        
        # 2. Validate auth (if token present)
        if hasattr(request, 'auth_token') and request.auth_token:
            await self.auth_service.validate(request.auth_token)
        
        # 3. Validate/load session (if session_id present)
        session = None
        if hasattr(request, 'session_id') and request.session_id:
            session = await self.session_service.get_session(request.session_id)
        
        # 4. Check permissions (if casefile_id present)
        if hasattr(request, 'casefile_id') and request.casefile_id:
            await self.casefile_service.check_access(request.user_id, request.casefile_id)
        
        # 5. Fetch context (if requested)
        context = {}
        if hasattr(request, 'context_requirements') and request.context_requirements:
            for req in request.context_requirements:
                if req == "mds_context":
                    context['mds'] = await self.persistence.get_context(request.user_id)
                elif req == "recent_docs":
                    context['docs'] = await self.casefile_service.get_recent_documents(request.casefile_id)
                # ... other context fetching
        
        # 6. Execute operation
        service = self._get_service(operation)
        method = getattr(service, operation)
        result = await method(request, **context, session=session)
        
        # 7. Trigger hooks (if specified)
        if hasattr(request, 'hooks') and request.hooks:
            for hook_name in request.hooks:
                hook = self.hook_registry[hook_name]
                await hook.on_complete(request, result)
        
        # 8. Update persistence
        if hasattr(request, 'notify_user') and request.notify_user:
            await self.comm_service.notify(request.user_id, result)
        
        return result
```

**Service Integration:**
```python
# FastAPI Route
@router.post("/casefile/update")
async def update_casefile(request: UpdateCasefileRequest):
    return await request_hub.process(request, "update_casefile")

# Service Method (pure business logic)
class CasefileService:
    async def update_casefile(
        self,
        request: UpdateCasefileRequest,
        mds: MDSContext,
        session: ToolSession
    ) -> UpdateCasefileResponse:
        # No validation - RequestHub did that
        # Just implement business logic
        casefile = await self.repository.update(request.casefile_id, request.payload)
        return UpdateCasefileResponse(payload=casefile)
```

---

## Implementation Roadmap

**Updated:** October 8, 2025 at 20:45  
**Status:** Ready for Phase 1

### Phase 1: RequestHub Core (Week 1)
- [ ] Create `src/coreservice/request_hub.py`
- [ ] Implement field-based validation
- [ ] Add context injection (MDSContext, ToolSession)
- [ ] Unit tests

### Phase 2: DTO Enhancement (Week 1)
- [ ] Add optional fields to BaseRequest (context_requirements, hooks)
- [ ] Update existing Request DTOs as needed
- [ ] Document field conventions

### Phase 3: Tool Generation (Week 2)
- [ ] Update `generate_tools.py` to create proper Request DTOs
- [ ] Generate all tools with DTO instantiation
- [ ] Validate tool→request→hub flow

### Phase 4: Hooks Framework (Week 2)
- [ ] Create `src/coreservice/hooks/` module
- [ ] Implement metrics, audit, notification hooks
- [ ] Hook registry pattern

### Phase 5-6: Service Integration (Week 3)
- [ ] Refactor services to use RequestHub
- [ ] Remove scattered validation code
- [ ] Integration tests

### Phase 7-8: Routes & Cleanup (Week 4)
- [ ] Update FastAPI routes
- [ ] Performance benchmarking
- [ ] Documentation

