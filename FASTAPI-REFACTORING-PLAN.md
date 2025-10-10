# FastAPI Refactoring Plan - System Status & Implementation Guide

**Date:** October 10, 2025
**Status:** Phase 8 COMPLETE | Phase 9 COMPLETE | Phase 10 COMPLETE
**Document Version:** 3.0
**Tests:** 15/15 passing

---

## System Status

**Core Infrastructure:**
- RequestHub: 26/26 operation handlers implemented
- Routers: 3 routers migrated (casefile, tool_session, chat)
- Middleware: 7-layer stack operational (Prometheus, Security, Error, Logging, JWT, RateLimit, TraceID, CORS)
- API Versioning: /v1/ prefix on all routers
- DTO Alignment: Validated, 0 errors
- Tools: 3 registered and operational

**Production Hardening (Phase 10):**
- Connection Pooling: FirestoreConnectionPool (10 connections)
- Redis Caching: RedisCacheService with graceful degradation
- Prometheus Metrics: /metrics endpoint with HTTP and operation tracking
- Health Monitoring: /health endpoint with pool and cache status

**Configuration:**
- Ruff linter: Updated to non-deprecated format
- Pytest: 0 collection warnings
- Pydantic: 3 deprecation warnings (framework-level, non-critical)

---

## Architecture Patterns

**Request Flow:**
```
HTTP Request → Middleware Stack → FastAPI Router → RequestHub.dispatch()
  → _prepare_context() → _run_hooks("pre") → Service execution
  → _run_hooks("post") → _attach_hook_metadata() → Response
```

**Multi-Pattern Design:**
- Orchestrated CRUD: All casefile, session, ACL operations via RequestHub with hooks
- Direct Execution: High-frequency operations (execute_tool, send_message) bypass orchestration for performance
- Context Enrichment: Automatic session/casefile/policy loading in _prepare_context()

**Middleware Stack (outer to inner):**
1. PrometheusMiddleware - HTTP metrics collection
2. SecurityHeadersMiddleware - HSTS, X-Frame-Options, CSP
3. ErrorHandlingMiddleware - Global exception handling with trace IDs
4. RequestLoggingMiddleware - Request/response logging with timing
5. JWTAuthMiddleware - JWT validation with dev mode bypass
6. RateLimitMiddleware - 100 req/60s per IP with headers
7. TraceIDMiddleware - X-Trace-ID generation and propagation
8. CORSMiddleware - Cross-origin request handling

---

## Implementation Details

**Phase 8: Service Integration**

All routers migrated to RequestHub orchestration pattern:

```python
# Pattern: Router → RequestHub → Service
@router.post("/", response_model=CreateCasefileResponse)
async def create_casefile(
    title: str,
    hub: RequestHub = Depends(get_request_hub),
    current_user: Dict = Depends(get_current_user)
):
    request = CreateCasefileRequest(
        user_id=current_user["user_id"],
        operation="create_casefile",
        payload=CreateCasefilePayload(title=title),
        hooks=["metrics", "audit"],
        context_requirements=["session"]
    )
    response = await hub.dispatch(request)
    _raise_for_failure(response)
    return response
```

RequestHub handlers map 26 operations to service methods with automatic hook execution and context enrichment.

**Phase 9: Middleware Stack**

Full middleware implementation in `src/pydantic_api/middleware.py` (250 lines) and `src/pydantic_api/app.py`:
- Trace ID propagation via X-Trace-ID header
- JWT authentication with /health and /v1/auth/* bypass
- Dev mode auto-authentication (sam123/Sam)
- Rate limiting: 100 req/60s per IP with X-RateLimit-* headers
- Request/response logging with X-Process-Time header
- Global error handling with trace IDs in responses
- Security headers: HSTS, X-Frame-Options, X-XSS-Protection, X-Content-Type-Options

**Phase 10: Production Hardening**

Connection Pooling (`src/persistence/firestore_pool.py`):
- FirestoreConnectionPool class with 10 async connections
- Pool management: initialize(), acquire(), release(), close_all()
- Health check method for monitoring
- Integrated into app startup/shutdown lifecycle

Redis Caching (`src/persistence/redis_cache.py`):
- RedisCacheService with async Redis client
- Methods: get(), set(), delete(), invalidate_pattern()
- Default TTL: 3600s (configurable)
- Graceful degradation if Redis unavailable
- Health check integration

Prometheus Metrics (`src/pydantic_api/prometheus_metrics.py`):
- PrometheusMiddleware for HTTP request tracking
- Metrics: http_requests_total, http_request_duration_seconds, operation_requests_total, operation_duration_seconds
- /metrics endpoint exposing Prometheus format
- Helper function track_operation() for RequestHub integration

---

## Next Steps: Tool Engineering Foundation

**Current State:**
System is operationally complete with all infrastructure in place. Focus shifts to tool engineering workflow.

**Tool Development Workflow:**

1. Design Request/Response DTOs
   - Define operation-specific payloads in `src/pydantic_models/operations/`
   - Follow parameter inheritance pattern (DTO → Method → Tool)
   - Validate DTO alignment: `python scripts/validate_dto_alignment.py`

2. Register Method
   - Add to `config/methods_inventory_v1.yaml` with DTO mappings
   - Define hooks: metrics, audit, session_lifecycle
   - Specify context_requirements: session, casefile, policy

3. Implement Service Handler
   - Add operation handler to appropriate service (CasefileService, ToolSessionService, etc.)
   - Implement business logic with proper error handling
   - Return typed Response object

4. Add RequestHub Handler
   - Implement `_execute_<operation>()` method in `src/coreservice/request_hub.py`
   - Wire to service method
   - Add to dispatch() handlers map

5. Generate Tool (optional)
   - Create YAML definition in `config/toolsets/`
   - Run: `python scripts/generate_tools.py`
   - Tool auto-registers with parameter inheritance from method

6. Test End-to-End
   - Unit tests for service logic
   - Integration tests for RequestHub dispatch
   - Tool execution tests via API

**Testing Tools:**

Simple tool request:
```python
# Direct service call
from casefileservice.service import CasefileService
service = CasefileService()
request = CreateCasefileRequest(...)
response = await service.create_casefile(request)

# Via RequestHub (with hooks)
from coreservice.request_hub import RequestHub
hub = RequestHub()
response = await hub.dispatch(request)

# Via API endpoint
import httpx
response = await httpx.post(
    "http://localhost:8000/v1/casefiles",
    json={"title": "Test", "description": "..."},
    headers={"Authorization": f"Bearer {token}"}
)
```

Composite tool/script:
```python
# Multi-operation workflow
hub = RequestHub()

# 1. Create casefile
casefile_req = CreateCasefileRequest(...)
casefile_resp = await hub.dispatch(casefile_req)
casefile_id = casefile_resp.payload.casefile_id

# 2. Create session linked to casefile
session_req = CreateSessionRequest(
    payload=CreateSessionPayload(casefile_id=casefile_id)
)
session_resp = await hub.dispatch(session_req)
session_id = session_resp.payload.session_id

# 3. Execute tool in session context
tool_req = ProcessToolRequestRequest(
    session_id=session_id,
    payload=ProcessToolRequestPayload(tool_name="...", args={...})
)
tool_resp = await hub.dispatch(tool_req)
```

**Hook Development:**

Adding custom hooks:
```python
# src/coreservice/request_hub.py
async def _custom_hook(
    self,
    stage: str,
    request: BaseRequest[Any],
    context: Dict[str, Any],
    response: Optional[BaseResponse[Any]],
) -> None:
    """Custom hook implementation."""
    if stage == "pre":
        # Pre-execution logic
        context["custom_data"] = {...}
    elif stage == "post":
        # Post-execution logic
        context["hook_events"].append({
            "hook": "custom",
            "stage": stage,
            "timestamp": datetime.utcnow().isoformat(),
        })

# Register in __init__
self.hook_handlers = {
    "metrics": self._metrics_hook,
    "audit": self._audit_hook,
    "session_lifecycle": self._session_lifecycle_hook,
    "custom": self._custom_hook,  # Add custom hook
}
```

**Metrics Integration:**

Track custom operations:
```python
from pydantic_api.prometheus_metrics import track_operation

# In service method
start_time = time.time()
try:
    result = await some_operation()
    track_operation("custom_op", "COMPLETED", time.time() - start_time)
except Exception:
    track_operation("custom_op", "FAILED", time.time() - start_time)
    raise
```

**Priority Actions:**

1. Identify next tool/operation to implement
2. Design req/resp DTOs following existing patterns
3. Implement service logic with proper error handling
4. Add RequestHub handler and routing
5. Write tests (unit + integration)
6. Generate tool YAML if needed
7. Test via API endpoint with authentication
8. Monitor metrics and logs for issues

---

## File Structure Reference

**Core Services:**
- `src/coreservice/request_hub.py` - Central orchestration hub (26 handlers)
- `src/casefileservice/service.py` - Casefile operations (13 methods)
- `src/tool_sessionservice/service.py` - Tool session management (5 methods)
- `src/communicationservice/service.py` - Chat session management (6 methods)

**API Layer:**
- `src/pydantic_api/app.py` - FastAPI application with middleware stack
- `src/pydantic_api/middleware.py` - 6 middleware implementations
- `src/pydantic_api/prometheus_metrics.py` - Metrics collection
- `src/pydantic_api/routers/` - casefile.py, tool_session.py, chat.py

**Infrastructure:**
- `src/persistence/firestore_pool.py` - Connection pooling
- `src/persistence/redis_cache.py` - Caching service
- `src/authservice/` - JWT authentication

**Models:**
- `src/pydantic_models/base/` - BaseRequest, BaseResponse, envelopes
- `src/pydantic_models/operations/` - Operation-specific req/resp DTOs
- `src/pydantic_models/canonical/` - Domain models (CasefileModel, etc.)
- `src/pydantic_models/workspace/` - Workspace integration models

**Configuration:**
- `config/methods_inventory_v1.yaml` - Method registry (26 operations)
- `config/toolsets/` - Tool YAML definitions
- `pyproject.toml` - Project configuration (ruff, pytest, dependencies)

**Scripts:**
- `scripts/generate_tools.py` - Tool code generation
- `scripts/validate_dto_alignment.py` - DTO validation
- `scripts/show_tools.py` - List registered tools

**Tests:**
- `tests/casefileservice/` - Casefile service tests
- `tests/coreservice/` - RequestHub and autonomous tests
- `tests/integration/` - End-to-end integration tests

---

## Validation Checklist

Before deploying new tools/operations:

**Architecture:**
- [ ] Request/Response DTOs defined with proper typing
- [ ] Method registered in methods_inventory_v1.yaml
- [ ] Service handler implemented with error handling
- [ ] RequestHub handler added to dispatch() map
- [ ] Hooks configured (metrics, audit, session_lifecycle)

**Testing:**
- [ ] Unit tests for service logic
- [ ] Integration tests for RequestHub dispatch
- [ ] API endpoint tests with authentication
- [ ] Error handling tests (validation, not found, permission denied)
- [ ] All existing tests still passing (15/15)

**Observability:**
- [ ] Operation metrics tracked via track_operation()
- [ ] Logging includes trace IDs and context
- [ ] /metrics endpoint shows new operation counters
- [ ] /health endpoint responds correctly

**Documentation:**
- [ ] Operation documented in ARCHITECTURE.md
- [ ] Request/Response models documented
- [ ] Example usage provided
- [ ] Error codes documented

---

## System Ready

Infrastructure complete. Foundation ready for tool engineering. Next operation: identify and implement next tool/method following the workflow above.
