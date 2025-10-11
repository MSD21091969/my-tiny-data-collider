# Request Context Flow Documentation

**Last Updated:** October 11, 2025

## Overview

RequestHub orchestrates all Request-Action-Response (R-A-R) workflows using a standardized context preparation and enrichment pattern. This ensures consistent audit trails, metrics collection, and context propagation across all operations.

## Service Transformation Pattern

Every operation follows this lifecycle:

```
1. Prepare Context → 2. Execute Service → 3. Enrich Response
```

### 1. Prepare Context (`_prepare_context`)

```python
async def _prepare_context(self, request: BaseRequest[Any]) -> dict[str, Any]:
    """Prepare execution context by hydrating session/casefile data and merging policies."""
```

**Context Preparation Steps:**

1. **Load Policy Defaults** - Based on `request.policy_hints.pattern`
2. **Merge Requirements** - Combine policy requirements + request requirements (deduplicated)
3. **Merge Hooks** - Combine policy hooks + request hooks (deduplicated)
4. **Extract Auth Context** - Pull `auth_context` from `request.metadata` for routing
5. **Hydrate Session** - Load session data if `session_id` present and "session" required
6. **Hydrate Casefile** - Load casefile data if `casefile_id` present and "casefile" required

**Context Structure:**

```python
{
    "policy": dict,                    # Loaded policy defaults
    "requirements": list[str],         # Combined context requirements
    "hooks": list[str],                # Combined hook names
    "hook_events": list[dict],         # Hook execution records
    "auth_context": dict,              # Auth routing metadata (if present)
    "session_request_id": str,         # Session request ID for audit routing (if present)
    "session": dict | None,            # Hydrated session data (if required)
    "casefile": dict | None,           # Hydrated casefile data (if required)
}
```

### 2. Execute Service

Service methods receive:

- **Request DTO** with operation-specific payload
- **Context** (implicitly via hooks or explicitly via parameters)

Services return:

- **Response DTO** with operation-specific payload
- **Status** (COMPLETED, FAILED, PENDING)
- **Optional error message**

### 3. Enrich Response

Post-execution enrichment:

- Attach `hook_events` to response metadata
- Include execution timing
- Add context snapshots (session_id, casefile_id, user_id)

## Context Hydration

### Session Hydration

Triggered when:

- `"session" in context["requirements"]`
- `request.session_id` is present

Loads:

```python
session = await service_manager.tool_session_service.repository.get_session(session_id)
context["session"] = session.model_dump() if session else None
```

**Session Context Includes:**

- session_id, user_id, casefile_id
- created_at, updated_at, active
- request_ids (tool requests in session)

### Casefile Hydration

Triggered when:

- `"casefile" in context["requirements"]`
- `casefile_id` found in `request.metadata` or `request.payload.casefile_id`

Loads:

```python
casefile = await service_manager.casefile_service.repository.get_casefile(casefile_id)
context["casefile"] = casefile.model_dump() if casefile else None
```

**Casefile Context Includes:**

- id, title, description, tags
- owner_id, session_ids, permissions
- created_at, updated_at, workspace_data

### Auth Context Extraction

Auth routing metadata flows from token through dependencies into context:

```python
# In router (via dependency injection)
auth_context = Depends(get_auth_context)
request.metadata["auth_context"] = auth_context

# In RequestHub._prepare_context
if request.metadata and "auth_context" in request.metadata:
    auth_context = request.metadata["auth_context"]
    context["auth_context"] = auth_context
    
    session_request_id = auth_context.get("session_request_id")
    if session_request_id:
        context["session_request_id"] = session_request_id
```

**Auth Context Structure:**

```python
{
    "user_id": str,
    "session_request_id": str | None,
    "casefile_id": str | None,
    "session_id": str | None,
}
```

## Hook Execution Flow

### Pre-Execution Hooks

Run before service execution:

- **Metrics Hook** - Record operation start, attach request metadata
- **Audit Hook** - Log operation attempt with user_id, casefile_id, session_id
- **Session Lifecycle Hook** - Update session activity timestamps

```python
await self._run_hooks("pre", request, context)
```

### Post-Execution Hooks

Run after service execution:

- **Metrics Hook** - Record operation completion, duration, status
- **Audit Hook** - Log operation result, errors, metadata changes
- **Session Lifecycle Hook** - Update session state, close if needed

```python
await self._run_hooks("post", request, context, response)
```

### Hook Events

Each hook records events in context:

```python
context["hook_events"].append({
    "hook": "audit",
    "stage": "pre",
    "operation": "create_casefile",
    "user_id": "sam123",
    "timestamp": "2025-10-11T10:30:00",
})
```

Events attached to response metadata for observability.

## Operation Handler Pattern

All operation handlers follow this structure:

```python
async def _execute_<operation>(self, request: OperationRequest) -> OperationResponse:
    """Handler for <operation> operation."""
    
    # Step 1: Prepare context
    context = await self._prepare_context(request)
    
    # Step 2: Run pre-execution hooks
    await self._run_hooks("pre", request, context)
    
    # Step 3: Execute service method
    response = await self.service_manager.<service>.<method>(request)
    
    # Step 4: Enrich context with response data
    context["status"] = response.status.value
    context["<resource_id>"] = response.payload.<resource_id>
    
    # Step 5: Run post-execution hooks
    await self._run_hooks("post", request, context, response)
    
    # Step 6: Attach hook metadata to response
    self._attach_hook_metadata(response, context)
    
    return response
```

## Policy Pattern Integration

Policy patterns define default requirements and hooks per operation type:

```python
# From policy_patterns.py
{
    "standard": {
        "context_requirements": ["session"],
        "hooks": ["metrics", "audit"],
    },
    "casefile_operation": {
        "context_requirements": ["casefile", "session"],
        "hooks": ["metrics", "audit", "session_lifecycle"],
    },
}
```

Merged with request-specific overrides in `_prepare_context`.

## Context Propagation Examples

### Tool Execution with Full Context

```python
# Router
@router.post("/tools/execute")
async def execute_tool(
    request: ToolRequest,
    auth_context: dict = Depends(get_auth_context)
):
    request.metadata = request.metadata or {}
    request.metadata["auth_context"] = auth_context
    return await request_hub.dispatch(request)

# RequestHub._prepare_context
context = {
    "auth_context": {"user_id": "sam123", "session_request_id": "sr_251011_abc"},
    "session": {"session_id": "ts_251011_001", "casefile_id": "cf_251011_proj"},
    "requirements": ["session"],
    "hooks": ["metrics", "audit", "session_lifecycle"],
}

# ToolSessionService.process_tool_request
# Receives auth_context for validation
# Uses session_request_id for audit routing
```

### Casefile Creation with Session Linking

```python
# Composite operation: create_casefile_with_session
context = await self._prepare_context(request)

# Create casefile
casefile_response = await service_manager.casefile_service.create_casefile(...)
context["casefile_id"] = casefile_response.payload.casefile_id

# Create session linked to casefile
session_response = await service_manager.tool_session_service.create_session(...)
context["session_id"] = session_response.payload.session_id

# Hooks receive enriched context with both IDs
await self._run_hooks("post", request, context, composite_response)
```

## Standardized Hook Handlers

### Metrics Hook

```python
async def _metrics_hook(self, stage, request, context, response):
    event = {
        "hook": "metrics",
        "stage": stage,
        "operation": request.operation,
        "timestamp": datetime.now().isoformat(),
    }
    if response:
        event["response_status"] = response.status.value
    context.setdefault("hook_events", []).append(event)
```

### Audit Hook

```python
async def _audit_hook(self, stage, request, context, response):
    entry = {
        "hook": "audit",
        "stage": stage,
        "operation": request.operation,
        "user_id": request.user_id,
        "timestamp": datetime.now().isoformat(),
    }
    if context.get("session_request_id"):
        entry["session_request_id"] = context["session_request_id"]
    if response:
        entry["status"] = response.status.value
    context.setdefault("hook_events", []).append(entry)
```

### Session Lifecycle Hook

```python
async def _session_lifecycle_hook(self, stage, request, context, response):
    if stage == "pre" and context.get("session"):
        # Update session activity timestamp
        pass
    elif stage == "post" and response:
        # Record session state changes
        pass
```

## Debugging Context Flow

### Enable Debug Logging

```python
import logging
logging.getLogger("coreservice.request_hub").setLevel(logging.DEBUG)
```

**Debug Output:**

```
DEBUG:coreservice.request_hub:Context prepared with session_request_id: sr_251011_abc
DEBUG:coreservice.request_hub:Context hydrated with session: ts_251011_001
DEBUG:coreservice.request_hub:Context hydrated with casefile: cf_251011_proj
```

### Inspect Hook Events

```python
response = await request_hub.dispatch(request)
hook_events = response.metadata.get("hook_events", [])

for event in hook_events:
    print(f"{event['hook']} - {event['stage']}: {event['operation']}")
```

## Best Practices

1. **Always call `_prepare_context` first** - Ensures consistent setup
2. **Run pre-hooks before service execution** - Captures intent
3. **Enrich context with response data** - Makes post-hooks meaningful
4. **Run post-hooks after service execution** - Records outcomes
5. **Attach hook metadata to response** - Enables observability
6. **Use auth_context for validation** - Enforces security
7. **Log context hydration at DEBUG level** - Aids debugging
8. **Keep hook handlers idempotent** - Safe for retries

## Migration Guide

### Existing Operation Without Context Flow

```python
# Before
async def _execute_operation(self, request):
    response = await service.method(request)
    return response
```

### Standardized with Context Flow

```python
# After
async def _execute_operation(self, request):
    context = await self._prepare_context(request)
    await self._run_hooks("pre", request, context)
    
    response = await service.method(request)
    
    context["status"] = response.status.value
    await self._run_hooks("post", request, context, response)
    self._attach_hook_metadata(response, context)
    
    return response
```

## References

- Implementation: `src/coreservice/request_hub.py`
- Policy Patterns: `src/coreservice/policy_patterns.py`
- Auth Context: `docs/TOKEN_SCHEMA.md`
- Service Integration: `docs/CORE_SERVICE_OVERVIEW.md`
