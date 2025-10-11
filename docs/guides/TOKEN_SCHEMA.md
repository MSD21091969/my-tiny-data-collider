# Token Schema Documentation

**Last Updated:** October 11, 2025

## Overview

JWT tokens in the MDS system carry authentication and routing metadata to enable secure, context-aware request processing. Tokens support both user authentication and service-to-service automation.

## Token Payload Structure

### Standard User Token

```json
{
  "sub": "sam123",
  "username": "Sam",
  "exp": 1728691200,
  "iat": 1728687600,
  "session_request_id": "sr_251011_abc123",
  "casefile_id": "cf_251011_xyz",
  "session_id": "ts_251011_sam123_001"
}
```

### Service Token

```json
{
  "sub": "svc_batch_processor",
  "username": "Service:batch_processor",
  "exp": 1728777600,
  "iat": 1728687600,
  "service": true,
  "service_name": "batch_processor",
  "casefile_id": "cf_251011_xyz",
  "session_id": "ts_251011_svc_001"
}
```

## Field Definitions

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `sub` | string | Yes | Subject: user ID or service ID (format: `svc_<name>` for services) |
| `username` | string | Yes | Display name for user or service |
| `exp` | integer | Yes | Expiration timestamp (Unix epoch) |
| `iat` | integer | Yes | Issued at timestamp (Unix epoch) |
| `session_request_id` | string | No | Session request ID for audit trail routing to correct Firestore subcollection |
| `casefile_id` | string | No | Casefile ID for authorization context and validation |
| `session_id` | string | No | Tool session ID for direct session context |
| `service` | boolean | No | Flag indicating service token (not user token) |
| `service_name` | string | No | Service identifier for audit and access control |

## Token Usage Patterns

### User Authentication Flow

1. User logs in via `/auth/login` or `/auth/quick-login`
2. Token generated with user credentials
3. Client includes token in `Authorization: Bearer <token>` header
4. FastAPI dependency `get_current_user` extracts and validates token
5. Routing metadata passed to services via `auth_context`

### Service Token Flow

1. Service calls `create_service_token(service_name, casefile_id?, session_id?)`
2. Token generated with service identity and optional routing context
3. Service includes token in API requests
4. Audit logs capture service actor for compliance
5. Service tokens have extended expiration (24h default)

### Tool Execution Validation

Token/session alignment enforced in `ToolSessionService.process_tool_request`:

```python
if auth_context:
    # Verify user owns the session
    if session.user_id != auth_context.get("user_id"):
        raise ValueError("Access denied: Session does not belong to authenticated user")
    
    # If token contains session_id, verify it matches
    token_session_id = auth_context.get("session_id")
    if token_session_id and token_session_id != session_id:
        raise ValueError(f"Token session mismatch: expected {token_session_id}, got {session_id}")
    
    # If token contains casefile_id, verify session belongs to that casefile
    token_casefile_id = auth_context.get("casefile_id")
    if token_casefile_id and session.casefile_id != token_casefile_id:
        raise ValueError("Access denied: Session not authorized for casefile")
```

## Context Hydration

`RequestHub._prepare_context` uses routing metadata from tokens:

- `session_request_id`: Routes audit entries to correct Firestore subcollection
- `casefile_id`: Pre-loads casefile context when required
- `session_id`: Pre-loads session context when required

## Token Generation Functions

### `create_token`

```python
def create_token(
    user_id: str,
    username: str,
    expires_delta: Optional[timedelta] = None,
    session_request_id: Optional[str] = None,
    casefile_id: Optional[str] = None,
    session_id: Optional[str] = None,
) -> str
```

Creates user authentication token with optional routing metadata.

### `create_service_token`

```python
def create_service_token(
    service_name: str,
    casefile_id: Optional[str] = None,
    session_id: Optional[str] = None,
    expires_delta: Optional[timedelta] = None,
) -> str
```

Creates service token for automated operations.

### `create_dev_token`

```python
def create_dev_token() -> str
```

Development-only convenience function for Sam user token.

## Security Considerations

### Token Validation

- Expiration enforced in production (development mode skips for clock sync issues)
- Signature verification using `SECRET_KEY` and `HS256` algorithm
- Malformed tokens rejected with HTTP 401

### Authorization Context

- Token carrying `casefile_id` grants context, not automatic permission
- ACL checks still required via `CasefileService.check_permission`
- Session ownership verified before tool execution
- Service tokens auditable via `service_name` field

### Development Mode

- Mock user always available without credentials when `ENVIRONMENT=development`
- Test endpoints provide quick token generation
- Production deployment must disable development shortcuts

## Integration Points

### FastAPI Dependencies

- `get_current_user`: Extracts full token payload including routing metadata
- `get_auth_context`: Returns routing context dict for service methods
- `get_current_user_id`: Extracts just the user ID

### Service Integration

- `ToolSessionService.process_tool_request(request, auth_context)`
- `RequestHub._execute_tool_request` passes `auth_context` from metadata
- Routers attach `auth_context` to request metadata via dependency injection

### Audit Trail

- Token metadata logged at service boundaries
- Service tokens capture non-interactive actor for compliance
- `session_request_id` routes events to correct Firestore path

## Migration Notes

**Breaking Changes from Legacy Schema:**

- Added `session_request_id` field for audit routing
- Added `casefile_id` field for authorization context
- Added `session_id` field for session context
- Service tokens use `svc_` prefix in `sub` field
- Old tokens without routing metadata still validate but lack context

**Compatibility:**

- Existing tokens work but lack routing metadata
- Services gracefully handle missing optional fields
- Re-login required to obtain tokens with full routing context

## Examples

### Generate User Token with Full Context

```python
from authservice.token import create_token

token = create_token(
    user_id="sam123",
    username="Sam",
    session_request_id="sr_251011_abc",
    casefile_id="cf_251011_proj01",
    session_id="ts_251011_sam123_001"
)
```

### Generate Service Token for Batch Job

```python
from authservice.token import create_service_token
from datetime import timedelta

token = create_service_token(
    service_name="nightly_report_generator",
    casefile_id="cf_251011_reports",
    expires_delta=timedelta(hours=6)
)
```

### Extract Auth Context in Router

```python
from fastapi import Depends
from pydantic_api.dependencies import get_auth_context

@router.post("/tools/execute")
async def execute_tool(
    request: ToolRequest,
    auth_context: dict = Depends(get_auth_context)
):
    # Attach auth_context to request metadata
    request.metadata = request.metadata or {}
    request.metadata["auth_context"] = auth_context
    
    # Pass to RequestHub
    return await request_hub.dispatch(request)
```

## Testing

### Development Quick Login

```bash
curl -X POST http://localhost:8000/auth/quick-login
```

Returns token for Sam user with default routing.

### Service Token Test

```python
from authservice.token import create_service_token

# Generate service token
svc_token = create_service_token(
    service_name="test_automation",
    casefile_id="cf_251011_test"
)

# Use in request
headers = {"Authorization": f"Bearer {svc_token}"}
```

## References

- Implementation: `src/authservice/token.py`
- Dependencies: `src/pydantic_api/dependencies.py`
- Validation: `src/tool_sessionservice/service.py`
- Context Flow: `src/coreservice/request_hub.py`
- Auth Overview: `docs/AUTHSERVICE_OVERVIEW.md`
