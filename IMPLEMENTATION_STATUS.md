# Implementation Status: feature/src-services-integration

**Branch:** feature/src-services-integration  
**Date:** October 10, 2025  
**Status:** Phase 1 Planning → Implementation Ready

## What We Have

### 1. Architecture Plans (Comprehensive)

**SERVICE_REFACTORING_PLAN.md (808 lines):**
- SmartDependencyContainer design (line 200)
- ContextAwareService base class pattern
- Service discovery/registry architecture
- 5-phase implementation plan (Phase 1-5)
- Migration strategy (adapters, gradual migration)

**SESSION_MANAGEMENT_ARCHITECTURE.md (1397 lines):**
- Enhanced Session model with rich metadata
- SessionManager for lifecycle
- Multiple storage backend support
- AI-ready session context
- Performance and scalability patterns

### 2. Existing Code

**Chain Executor (src/pydantic_ai_integration/execution/chain_executor.py):**
- Sequential tool execution
- Conditional branching (on_success, on_failure)
- State passing between steps
- Error recovery strategies

**ai-method-integration (merged from develop):**
- Enhanced tool_decorator.py (line 809: _instantiate_service)
- Parameter mapping (method_params vs tool_params)
- Request DTO building (line 890)
- 541 lines of integration tests
- 5 error types, dry run, timeout handling

### 3. Current Gaps

**Not Implemented:**
- SmartDependencyContainer (only design exists)
- ServiceRegistry (no code)
- ContextAwareService base class (no code)
- SessionManager (no code)
- Enhanced ExecutionContext (basic MDSContext only)

## Integration Plan: ai-method-integration + DI

### Step 1: Implement SmartDependencyContainer

Replace hardcoded service_module_map with DI container:

**Current (tool_decorator.py line 809):**
```python
service_module_map = {
    "CasefileService": "casefileservice.service",
    "ToolSessionService": "tool_sessionservice.service",
    # ... 7 services hardcoded
}
```

**Target:**
```python
# New file: src/pydantic_ai_integration/services/container.py
class ServiceContainer:
    def __init__(self):
        self._services = {}
        self._factories = {}
    
    def register_service(self, name: str, instance: Any):
        self._services[name] = instance
    
    def register_factory(self, name: str, factory: Callable):
        self._factories[name] = factory
    
    async def resolve(self, name: str, ctx: MDSContext = None) -> Any:
        if name in self._services:
            return self._services[name]
        if name in self._factories:
            return self._factories[name](ctx)
        raise ValueError(f"Service not registered: {name}")

# Global container
_container = ServiceContainer()

# tool_decorator.py updated:
async def _instantiate_service(service_name: str, ctx: MDSContext):
    return await _container.resolve(service_name, ctx)
```

### Step 2: Service Registration at Startup

**New file: src/pydantic_ai_integration/services/registry.py:**
```python
from .container import _container

def register_core_services():
    """Register core services at application startup."""
    from casefileservice.service import CasefileService
    from tool_sessionservice.service import ToolSessionService
    # ... import others
    
    _container.register_factory("CasefileService", lambda ctx: CasefileService())
    _container.register_factory("ToolSessionService", lambda ctx: ToolSessionService())
    # ... register others

# In pydantic_api/app.py startup:
from pydantic_ai_integration.services.registry import register_core_services

@app.on_event("startup")
async def startup():
    register_core_services()
```

### Step 3: Enhanced ExecutionContext

**Current:** MDSContext (user_id, session_id, casefile_id)

**Target (from SERVICE_REFACTORING_PLAN.md line 95):**
```python
class ExecutionContext(BaseModel):
    context_id: str
    parent_context_id: Optional[str]
    request_id: Optional[str]
    user_id: Optional[str]
    session_id: Optional[str]
    tool_name: Optional[str]
    start_time: float
    end_time: Optional[float]
    metadata: Dict[str, Any]
    # AI context, feature flags, etc.
```

### Step 4: Session Integration

Connect ToolSession with JWT and tool execution:

**In tool_decorator.py tool_function (before line 1138):**
```python
# Validate session ownership
if ctx.session_id:
    session_manager = await _container.resolve("SessionManager", ctx)
    session = await session_manager.get_session(ctx.session_id)
    if session.user_id != ctx.user_id:
        return {"status": "error", "error_type": "AuthorizationError"}
```

## Implementation Priority

**Phase 1 (This Branch):**
1. ServiceContainer + registry (replace hardcoded map)
2. Register 7 existing services
3. Update _instantiate_service to use container
4. Tests pass with DI

**Phase 2 (After tool-execution-engine merge):**
5. Enhanced ExecutionContext
6. SessionManager implementation
7. Session ownership validation
8. JWT integration in tools

**Phase 3 (Full Refactor):**
9. ContextAwareService base class
10. Service discovery
11. Context providers
12. All services inherit from base

## Files to Create

```
src/pydantic_ai_integration/services/
├── __init__.py
├── container.py          # ServiceContainer implementation
├── registry.py           # Service registration
└── base.py               # ContextAwareService base (Phase 3)
```

## Current Working State

- All tests passing (5 dry_run tests verified)
- tool_decorator.py functional with hardcoded services
- Chain executor available for composite tools
- Architecture plans comprehensive and detailed

## Next Actions

1. Implement ServiceContainer (container.py)
2. Implement service registration (registry.py)
3. Update tool_decorator.py to use container
4. Run integration tests to verify DI works
5. Monitor feature/tool-execution-engine progress

**Ready to implement Phase 1.**
