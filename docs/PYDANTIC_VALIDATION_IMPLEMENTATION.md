# Pydantic Validation - Implementation Guide

**Date**: 2025-10-03  
**Status**: Phase 2 - Creating Models

---

## Summary

**Finding**: 85% of service methods and 86% of API endpoints return `Dict[str, Any]` instead of typed Pydantic models.

**Solution**: Create 26 missing Request/Response models and refactor service/API layers.

---

## Phase 2: Create 26 Request/Response Models

### Template Pattern

```python
from pydantic import BaseModel, Field
from typing import Optional, List, Literal
from ..shared.base_models import BaseRequest, BaseResponse

# 1. Define Payload (pure data)
class CreateSessionPayload(BaseModel):
    casefile_id: str = Field(..., description="Casefile ID")
    session_id: Optional[str] = Field(None, description="Optional session ID to resume")
    title: Optional[str] = Field(None, description="Session title")

# 2. Define Request (wraps payload)
class CreateSessionRequest(BaseRequest[CreateSessionPayload]):
    operation: Literal["create_session"] = "create_session"

# 3. Define Response Payload (result data)
class SessionCreatedPayload(BaseModel):
    session_id: str
    casefile_id: str
    created_at: str

# 4. Define Response (wraps result)
class CreateSessionResponse(BaseResponse[SessionCreatedPayload]):
    pass  # Inherits request_id, status, error, metadata
```

---

## Models to Create

### File 1: `src/pydantic_models/tool_session/session_models.py`

**8 Models** (4 Request + 4 Response):

1. **CreateSession**
   - Request: `casefile_id`, `session_id?`, `title?`
   - Response: `session_id`, `casefile_id`, `created_at`

2. **GetSession**
   - Request: `session_id`
   - Response: Full `ToolSession` object

3. **ListSessions**
   - Request: `user_id?`, `casefile_id?`
   - Response: `sessions: List[ToolSessionSummary]`, `total_count`

4. **CloseSession**
   - Request: `session_id`
   - Response: Updated `ToolSession` object

### File 2: `src/pydantic_models/communication/session_models.py`

**6 Models** (3 Request + 3 Response):

1. **CreateChatSession**
   - Request: `user_id`, `casefile_id?`, `title?`
   - Response: `session_id`, `created_at`

2. **GetChatSession**
   - Request: `session_id`
   - Response: Full `ChatSession` object

3. **CloseChatSession**
   - Request: `session_id`
   - Response: Updated `ChatSession` object

### File 3: `src/pydantic_models/casefile/crud_models.py`

**12 Models** (6 Request + 6 Response):

1. **CreateCasefile**
   - Request: `title`, `description`, `tags`
   - Response: `casefile_id`, `created_at`

2. **GetCasefile**
   - Request: `casefile_id`
   - Response: Full `CasefileModel` object

3. **UpdateCasefile** ⚠️ SECURITY CRITICAL
   - Request: `casefile_id`, `title?`, `description?`, `tags?` (explicit fields, NOT Dict)
   - Response: Updated `CasefileModel` object

4. **ListCasefiles**
   - Request: `user_id?`
   - Response: `casefiles: List[CasefileSummary]`, `total_count`

5. **DeleteCasefile**
   - Request: `casefile_id`
   - Response: `casefile_id`, `deleted_at`

6. **AddSessionToCasefile**
   - Request: `casefile_id`, `session_id`
   - Response: Updated `CasefileModel` object

---

## Current Non-Compliant Methods

### ToolSessionService (4 methods)
```python
create_session(user_id, casefile_id) → Dict[str, str]  ❌
get_session(session_id) → Dict[str, Any]  ❌
list_sessions(user_id, casefile_id) → List[Dict[str, Any]]  ❌
close_session(session_id) → Dict[str, Any]  ❌
```

### CommunicationService (3 methods)
```python
create_session(user_id, casefile_id) → Dict[str, str]  ❌
get_session(session_id) → Dict[str, Any]  ❌
close_session(session_id) → Dict[str, Any]  ❌
```

### CasefileService (6 methods)
```python
create_casefile(...) → Dict[str, str]  ❌
get_casefile(casefile_id) → Dict[str, Any]  ❌
update_casefile(casefile_id, updates: Dict[str, Any]) → Dict[str, Any]  ❌ SECURITY RISK
list_casefiles(user_id) → List[Dict[str, Any]]  ❌
delete_casefile(casefile_id) → Dict[str, Any]  ❌
add_session_to_casefile(...) → Dict[str, Any]  ❌
```

---

## Next Steps

1. ✅ Create `session_models.py` files with all Request/Response models
2. Refactor service methods to use new models
3. Refactor API endpoints to use new models
4. Test end-to-end validation
5. Remove all `Dict[str, Any]` returns

---

## Success Criteria

- ✅ 26 new models created and exported
- ✅ All models inherit from BaseRequest/BaseResponse
- ✅ All fields explicitly typed (no Dict[str, Any])
- ✅ Models pass Pydantic validation
- ✅ Ready for service layer refactoring
