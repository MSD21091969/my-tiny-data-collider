# search_messages

Search Gmail messages by query

## Classification

| Field | Value |
|-------|-------|
| **Domain** | communication |
| **Subdomain** | gmail |
| **Capability** | search |
| **Complexity** | atomic |
| **Maturity** | beta |
| **Integration Tier** | external |

## Service

**Service:** `GmailClient`  
**Module:** `src.pydantic_ai_integration.integrations.google_workspace.clients`  
**Implementation:** `GmailClient.search_messages`

## Signature

```python
async def search_messages(
    self,
    request: GmailSearchMessagesRequest
) -> GmailSearchMessagesResponse
```

## Request Model

**Type:** `GmailSearchMessagesRequest`  
**Module:** `src.pydantic_ai_integration.integrations.google_workspace.models`

### Parameters

*No parameters documented.*


## Response Model

**Type:** `GmailSearchMessagesResponse`  
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
    GmailSearchMessagesRequest,
    GmailSearchMessagesPayload
)

# Create request
# No parameters required
payload = GmailSearchMessagesPayload()
request = GmailSearchMessagesRequest(payload=payload)

# Call method
service = GmailClient()
response = await service.search_messages(request)

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
**Last Updated:** 2025-10-06
