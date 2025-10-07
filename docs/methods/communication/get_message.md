# get_message

Get single Gmail message by ID

## Classification

| Field | Value |
|-------|-------|
| **Domain** | communication |
| **Subdomain** | gmail |
| **Capability** | read |
| **Complexity** | atomic |
| **Maturity** | beta |
| **Integration Tier** | external |

## Service

**Service:** `GmailClient`  
**Module:** `src.pydantic_ai_integration.integrations.google_workspace.clients`  
**Implementation:** `GmailClient.get_message`

## Signature

```python
async def get_message(
    self,
    request: GmailGetMessageRequest
) -> GmailGetMessageResponse
```

## Request Model

**Type:** `GmailGetMessageRequest`  
**Module:** `src.pydantic_ai_integration.integrations.google_workspace.models`

### Parameters

*No parameters documented.*


## Response Model

**Type:** `GmailGetMessageResponse`  
**Module:** `src.pydantic_ai_integration.integrations.google_workspace.models`

## Business Rules

| Rule | Value |
|------|-------|
| **Enabled** | ✓ |
| **Requires Auth** | ✓ |
| **Requires Casefile** | ✗ |
| **Timeout** | 30s |

### Required Permissions

- `workspace:gmail:read`


## Usage Example

```python
from src.pydantic_ai_integration.integrations.google_workspace.clients import GmailClient
from src.pydantic_ai_integration.integrations.google_workspace.models import (
    GmailGetMessageRequest,
    GmailGetMessagePayload
)

# Create request
# No parameters required
payload = GmailGetMessagePayload()
request = GmailGetMessageRequest(payload=payload)

# Call method
service = GmailClient()
response = await service.get_message(request)

# Handle response
if response.status == RequestStatus.COMPLETED:
    result = response.payload
    print(f"Success: {result}")
    print(f"Execution time: {response.metadata['execution_time_ms']}ms")
else:
    print(f"Error: {response.error}")
```

## Related

*No related methods in this subdomain.*


---

**Version:** 1.0.0  
**Last Updated:** 2025-10-07
