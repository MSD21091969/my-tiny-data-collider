# Pydantic API

FastAPI application with routers for casefiles, tool sessions, and chat sessions.

## Structure

```
pydantic_api/
├── app.py           # FastAPI application setup
├── dependencies.py  # Shared dependencies (auth, service injection)
└── routers/         # API route handlers
    ├── casefile.py       # Casefile CRUD + ACL endpoints
    ├── tool_session.py   # Tool session lifecycle + execution
    └── chat.py           # Chat session lifecycle + messaging
```

## Router Responsibilities

**casefile.py**
- CRUD: create, get, update, delete, list casefiles
- ACL: grant/revoke permissions, list permissions, check access
- Session linking: add tool/chat sessions to casefiles

**tool_session.py**
- Lifecycle: create, get, list, close tool sessions
- Execution: execute tools within sessions
- Discovery: list available tools by category

**chat.py**
- Lifecycle: create, get, list, close chat sessions
- Messaging: send chat messages, get message history

## Request/Response Pattern

All endpoints use operation models from `pydantic_models.operations.*`:

```python
from pydantic_models.operations.casefile_ops import (
    CreateCasefileRequest,
    CreateCasefileResponse,
)

@router.post("/", response_model=CreateCasefileResponse)
async def create_casefile(request: CreateCasefileRequest):
    return await service.create_casefile(request)
```

## Dependencies

- `get_current_user()` - JWT authentication
- `get_*_service()` - Service layer injection
- `verify_casefile_access()` - ACL enforcement
