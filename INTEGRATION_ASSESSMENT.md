# Integration Assessment: Cross-Branch Dependencies

**Date:** October 10, 2025  
**Current Branch:** develop (feature/ai-method-integration merged)  
**Waiting For:** feature/tool-execution-engine  
**Future:** feature/src-services

## Current State

**BaseRequest Structure (src/pydantic_models/base/envelopes.py:23):**
```python
class BaseRequest(BaseModel, Generic[RequestPayloadT]):
    request_id: UUID
    session_id: Optional[str]  # ✓ Present
    user_id: str
    operation: str
    payload: RequestPayloadT
```

**Session Handling:**
- JWT auth middleware: `src/pydantic_api/middleware.py:123` (JWTAuthMiddleware)
- Token validation: `src/authservice/token.py` (jwt library)
- Session creation hooks in routers (chat.py lines 44, 50, 79, 123, 152, 183, 212)

## Integration Points

### 1. feature/tool-execution-engine → develop

**Conflict Analysis:**
```
develop has:                          tool-execution-engine removes:
+ IMPLEMENTATION.md                   - IMPLEMENTATION.md
+ VERIFICATION.md                     - VERIFICATION.md
+ docs/ANALYTICAL_TOOLSET_*           - docs/* (3 files)
+ tests/integration/* (541 lines)     - tests/integration/* (all)
+ Enhanced tool_decorator.py          - Reverts tool_decorator.py
```

**Concern:** tool-execution-engine removes implementation and tests from ai-method-integration.

**Status:** Session_id field exists in BaseRequest - no blocker mentioned by tool-execution-engine.

### 2. Session-Auth Integration (Phase 2)

**Current Flow:**
1. JWT middleware validates token → extracts user_id
2. Router creates BaseRequest with user_id + session_id
3. Tool decorator builds Request DTO with context (lines 890-940)
4. Service receives validated Request DTO

**Tool Decorator Context Injection (line 920):**
```python
request_dto = request_model_class(
    user_id=ctx.user_id,        # From MDSContext
    session_id=ctx.session_id,  # From MDSContext
    casefile_id=ctx.casefile_id,
    payload=method_params
)
```

**Gap:** Tool execution doesn't validate session ownership or JWT freshness.

### 3. feature/src-services (Future Refactor)

**Impact on ai-method-integration:**
- Service instantiation: `_instantiate_service` (line 809) uses hardcoded module map
- 7 services: CasefileService, ToolSessionService, CommunicationService, 3x Google clients, RequestHubService
- DI-ready design but not activated

**Refactor Prep:**
- Service registry pattern needed
- Constructor injection for repositories
- Lifecycle management (connection pools)

## Recommendations

### Immediate (Before tool-execution-engine Merge)

**1. Conflict Resolution Strategy:**
- Determine which branch is authoritative
- If tool-execution-engine wins: lose 541 lines of integration tests
- If develop wins: merge conflicts in tool_decorator.py

**2. Session Validation Hook:**
Add pre-execution hook in tool_decorator.py tool_function (before line 1138):
```python
# Validate session ownership
if ctx.session_id and not await _validate_session(ctx.user_id, ctx.session_id):
    return {
        "tool_name": tool_name,
        "status": "error",
        "error_type": "AuthorizationError",
        "error_message": "Session does not belong to user or expired"
    }
```

**3. Document Merge Strategy:**
Create merge plan showing:
- Which files from each branch to keep
- Test preservation strategy
- Documentation consolidation approach

### Phase 2 (After tool-execution-engine)

**4. JWT Validation in Tools:**
- Add `jwt_token` to MDSContext
- Validate token freshness before service calls
- Handle token refresh flow

**5. Session-Auth Integration:**
- Link tool_session creation to JWT issuance
- Add session_id to JWT claims
- Validate session_id matches JWT

**6. Test Coverage:**
- Auth failure scenarios (expired JWT, mismatched session)
- Session ownership validation
- Token refresh during long-running tools

### Phase 3 (feature/src-services)

**7. DI Container:**
Replace `_instantiate_service` with:
```python
async def _instantiate_service(service_name: str, container: DIContainer):
    return await container.resolve(service_name)
```

**8. Service Lifecycle:**
- Singleton services with connection pooling
- Scoped services per request
- Transient services per call

**9. Repository Injection:**
Services receive repositories via constructor instead of creating them.

## Questions for Resolution

1. **Merge Priority:** Does tool-execution-engine supersede ai-method-integration or merge both?
2. **Test Preservation:** Keep integration tests from ai-method-integration?
3. **Session Validation:** Add now or defer to Phase 2?
4. **JWT Integration:** Required before production or incremental?

## Files Requiring Coordination

**Shared:**
- `src/pydantic_ai_integration/tool_decorator.py` (both branches modify)
- `BRANCH_DEVELOPMENT_PLAN.md` (both branches have versions)

**Unique to develop:**
- `IMPLEMENTATION.md`, `VERIFICATION.md`
- `tests/integration/*` (19 files)
- `docs/ANALYTICAL_TOOLSET_ENGINEERING.md`
- `docs/METHOD_PARAMETER_INTEGRATION.md`
- `docs/PARAMETER_MAPPING_ANALYSIS.md`

**Unique to tool-execution-engine:**
- `SERVICE_ARCHITECTURE_INTEGRATION.md`
- `IMPLEMENTATION_GUIDE.md` (different from develop)

## Risk Assessment

**High:** Merge conflict in tool_decorator.py (391 lines changed both branches)  
**Medium:** Lost test coverage if tool-execution-engine merge discards tests  
**Low:** Session_id field compatibility (already present in BaseRequest)

## Agreed Merge Strategy

**Order:**
1. Wait for feature/tool-execution-engine completion
2. Merge tool-execution-engine → develop (accept their version)
3. Merge src-services → develop (get DI container)
4. Re-implement ai-method-integration with DI-enabled service instantiation

**Rationale:**
- Both engine & src-services revert ai-method-integration changes
- src-services provides DI infrastructure needed for Phase 2
- Re-implementation will use proper DI instead of hardcoded service map
- Tests preserved in git history, can be restored after DI integration

**Status:** Holding on develop, ready for incoming merges.
