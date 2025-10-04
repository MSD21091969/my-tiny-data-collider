# Contributing Guidelines

General development guidelines for all branches (main, develop, feature/*, hotfix/*).

---

## Branch Strategy

```
main          Production-ready code only
develop       Active development, all features merge here first
feature/*     New features, branch from develop
hotfix/*      Critical fixes, branch from main
```

**Workflow:**
1. Branch from `develop` for features
2. Commit frequently with clear messages
3. Pull request to `develop` when ready
4. After testing, merge `develop` → `main`

---

## Coding Standards

### Python Style

**PEP 8 compliant:**
```python
# Use snake_case for functions/variables
def send_email_message(recipient_email: str):
    pass

# Use PascalCase for classes
class GmailClient:
    pass

# Type hints required
async def execute_tool(ctx: MDSContext, params: dict) -> ToolResponse:
    pass
```

**Import order:**
```python
# 1. Standard library
import os
from typing import List, Dict

# 2. Third-party
from pydantic import BaseModel, Field
from fastapi import APIRouter

# 3. Local
from src.pydantic_models.base import BaseResponse
from src.pydantic_ai_integration.dependencies import MDSContext
```

**Docstrings:**
```python
async def send_message(ctx: MDSContext, to: str, subject: str) -> dict:
    """Send email via Gmail API.
    
    Args:
        ctx: Execution context with user_id, session_id
        to: Recipient email address
        subject: Email subject line
        
    Returns:
        dict: Status and message_id
        
    Raises:
        PermissionError: If user lacks gmail:send permission
    """
```

---

## Project Structure Rules

### Pydantic Models Organization

**By purpose, not domain:**

```python
# ✓ CORRECT
from src.pydantic_models.base import BaseRequest, BaseResponse
from src.pydantic_models.canonical import ToolSession, CasefileModel
from src.pydantic_models.operations.tool_execution_ops import (
    ToolRequest,
    ToolResponse,
)

# ✗ WRONG
from src.pydantic_models.tool_session import ToolSession  # Old structure
from src.pydantic_models.casefile import CasefileModel    # Old structure
```

**Layer separation:**
```python
# Layer 1: Domain models (purpose-based)
src/pydantic_models/
├── base/           # BaseRequest, BaseResponse, enums
├── canonical/      # Core entities (ToolSession, Casefile)
├── operations/     # Request/Response DTOs
├── views/          # Read-only projections
└── workspace/      # External data models (Gmail, Drive)

# Layer 2: Integration models (external APIs)
src/pydantic_ai_integration/integrations/
└── google_workspace/
    ├── clients.py  # GmailClient, DriveClient
    └── models.py   # API-specific models

# Layer 3: Generated tools (YAML-driven)
# (Directories created on demand via `python scripts/generate_tools.py`)
src/pydantic_ai_integration/tools/generated/
├── automation/pipelines/
├── communication/email/
├── utilities/debugging/
└── workspace/google/
```

---

## Pydantic AI Integration

### Service Layer Pattern

**Service classes use Pydantic models:**

```python
# tool_sessionservice/service.py
from src.pydantic_models.canonical import ToolSession
from src.pydantic_models.operations.tool_execution_ops import (
    ToolRequest,
    ToolResponse,
)
from src.pydantic_models.base import BaseResponse, RequestStatus

class ToolSessionService:
    async def execute_tool(
        self, 
        session_id: str, 
        request: ToolRequest  # Pydantic model
    ) -> BaseResponse[ToolResponse]:
        # Get tool from registry
        tool_def = get_tool_definition(request.payload.tool_name)
        
        # Validate policies
        if not tool_def.business_rules.enabled:
            raise ToolDisabledError()
            
        # Create context
        ctx = MDSContext(
            user_id=request.user_id,
            session_id=session_id
        )
        
        # Execute (Pydantic validation happens in decorator)
        result = await tool_def.implementation(ctx, **request.payload.parameters)
        
        # Return wrapped response
        return BaseResponse(
            status=RequestStatus.COMPLETED,
            payload=ToolResponse(
                tool_name=request.payload.tool_name,
                result=result
            )
        )
```

**Key principles:**
- Service methods accept Pydantic models as input
- Service methods return Pydantic models wrapped in BaseResponse
- Validation happens at model instantiation
- No raw dicts crossing service boundaries

---

## API Layer Pattern

**FastAPI routers use Pydantic models:**

```python
# pydantic_api/routers/tool_session.py
from fastapi import APIRouter, Depends
from src.pydantic_models.base import BaseResponse
from src.pydantic_models.operations.tool_session_ops import CreateSessionRequest
from src.pydantic_models.operations.tool_execution_ops import (
    ToolRequest,
    ToolResponse,
)

router = APIRouter(prefix="/tool_sessions")


@router.post("/sessions")
async def create_session(
    request: CreateSessionRequest,
    service: ToolSessionService = Depends(get_service),
) -> BaseResponse:
    """Create a new tool session and return its identifier."""
    return await service.create_session(request)


@router.post("/sessions/{session_id}/execute")
async def execute_tool(
    session_id: str,
    request: ToolRequest,  # FastAPI validates from JSON
    service: ToolSessionService = Depends(get_service),
) -> BaseResponse[ToolResponse]:
    """Execute tool in session context.

    Request body validated by Pydantic.
    Response serialized by Pydantic.
    """
    return await service.execute_tool(session_id, request)
```

**Request/Response flow:**
```
JSON Request → FastAPI → Pydantic Model → Service → Pydantic Model → FastAPI → JSON Response
```

**Validation layers:**
1. **API layer:** FastAPI + Pydantic validates HTTP request
2. **Service layer:** Business rules + policies
3. **Tool layer:** @register_mds_tool decorator validates parameters

---

## Tool Development

### YAML is Single Source of Truth

**Folder structure:**
```
config/tools/domain/subdomain/tool_name.yaml
    ↓
src/.../generated/domain/subdomain/tool_name.py
    ↓
tests/unit/domain/subdomain/test_tool_name.py
```

**Creating new tool:**

1. **Create YAML:**
```yaml
# config/tools/communication/email/gmail_send.yaml
name: gmail_send_message
description: "Send email via Gmail"

classification:
  domain: communication
  subdomain: email
  capability: create

parameters:
  - name: to
    type: string
    required: true
  - name: subject
    type: string
    required: true
```

2. **Generate code:**
```powershell
generate-tools
```

3. **Test:**
```powershell
pytest tests/unit/communication/email/test_gmail_send.py -v
```

4. **Commit YAML + generated files:**
```powershell
git add config/tools/communication/email/gmail_send.yaml
git add src/.../generated/communication/email/gmail_send.py
git add tests/unit/communication/email/test_gmail_send.py
git commit -m "Add gmail_send_message tool"
```

**Modifying existing tool:**
- Edit YAML only
- Run `generate-tools`
- Commit YAML (generated files update automatically)

---

## Testing Requirements

### Three Test Layers

**Unit tests** (test tool logic):
```python
# tests/unit/communication/email/test_gmail_send.py
@pytest.mark.asyncio
async def test_gmail_send_message():
    ctx = mock_context()
    result = await gmail_send_message(ctx, to="test@example.com", subject="Test")
    assert result["status"] == "sent"
```

**Integration tests** (test service layer):
```python
# tests/integration/communication/email/test_gmail_send_integration.py
@pytest.mark.asyncio
async def test_gmail_send_via_service():
    service = ToolSessionService()
    request = ToolRequest(
        user_id="user_123",
        payload=ToolRequestPayload(
            tool_name="gmail_send_message",
            parameters={"to": "test@example.com", "subject": "Test"}
        )
    )
    response = await service.execute_tool("session_123", request)
    assert response.status == RequestStatus.COMPLETED
```

**API tests** (test HTTP endpoints):
```python
# tests/api/communication/email/test_gmail_send_api.py
def test_execute_gmail_send(client, auth_headers):
    response = client.post(
        "/tool_sessions/session_123/execute",
        json={"tool_name": "gmail_send_message", "parameters": {...}},
        headers=auth_headers
    )
    assert response.status_code == 200
```

**Test organization mirrors tool structure:**
```
config/tools/communication/email/gmail_send.yaml
    ↓
tests/unit/communication/email/test_gmail_send.py
tests/integration/communication/email/test_gmail_send_integration.py
tests/api/communication/email/test_gmail_send_api.py
```

---

## Git Commit Messages

**Format:**
```
<type>: <short summary>

<detailed explanation if needed>
```

**Types:**
- `feat:` New feature
- `fix:` Bug fix
- `refactor:` Code restructuring
- `test:` Test changes
- `docs:` Documentation
- `chore:` Tooling, dependencies

**Examples:**
```
feat: Add gmail_send_message tool

Generated from YAML definition with Gmail API integration.
Includes unit, integration, and API tests.

---

fix: Tool session policy enforcement

Service layer now checks requires_active_session before execution.
Added test coverage for policy violations.

---

refactor: Reorganize pydantic_models by purpose

Moved from domain-based (user/, casefile/) to purpose-based
(base/, canonical/, operations/, views/).
```

---

## Code Review Checklist

**Before submitting PR:**

- [ ] All tests pass: `pytest tests/`
- [ ] Type hints on all functions
- [ ] Docstrings on public functions
- [ ] Imports organized (stdlib → third-party → local)
- [ ] No print statements (use logging)
- [ ] Pydantic models for all data structures
- [ ] Service layer returns BaseResponse
- [ ] API layer uses Pydantic models
- [ ] Generated files from YAML (if applicable)
- [ ] Tests mirror tool structure

**PR description includes:**
- What changed
- Why it changed
- How to test
- Breaking changes (if any)

---

## Common Patterns

### Service Method Template

```python
async def service_method(
    self,
    request: RequestModel  # Pydantic input
) -> BaseResponse[ResponseModel]:  # Pydantic output
    """Service method docstring."""
    try:
        # Business logic
        result = await self._do_work(request.payload)
        
        # Return success
        return BaseResponse(
            status=RequestStatus.COMPLETED,
            payload=ResponseModel(**result)
        )
    except ValidationError as e:
        return BaseResponse(
            status=RequestStatus.FAILED,
            error_message=str(e)
        )
```

### API Router Template

```python
@router.post("/resource/{id}/action")
async def action_endpoint(
    id: str,
    request: RequestModel,  # Auto-validated by FastAPI
    service: ServiceClass = Depends(get_service)
) -> BaseResponse[ResponseModel]:
    """Endpoint docstring."""
    return await service.method(id, request)
```

### Tool Implementation Template

```python
@register_mds_tool(
    name="tool_name",
    params_model=ToolParams,
    description="Tool description"
)
async def tool_name(ctx: MDSContext, param1: str, param2: int) -> dict:
    """Tool docstring."""
    # Implementation
    return {"status": "success"}
```

---

## Communication Guidelines

**Code comments:**
- Explain why, not what
- Use for complex logic only
- Keep short and factual

**PR/issue discussions:**
- Be concise and technical
- Use code examples
- Avoid management speak
- No emojis in formal communication
- Provide facts, not opinions

**Example - Good:**
```
The session policy check fails because requires_active_session=true
but session.status=inactive. Added validation in service layer:

if tool_def.session_policies.requires_active_session:
    if not session.is_active():
        raise SessionInactiveError()
```

**Example - Bad:**
```
Great work everyone! 🎉 The session thing wasn't working properly
so I added some checks to make sure everything flows smoothly now.
```

---

## Questions?

- Check `README.md` for architecture overview
- Check `src/pydantic_models/README.md` for model organization
- Check `src/pydantic_api/README.md` for API patterns
- Check `src/pydantic_ai_integration/README.md` for tool development
