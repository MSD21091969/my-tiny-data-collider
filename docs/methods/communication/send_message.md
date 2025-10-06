# send_message

Send Gmail message

## Classification

| Field | Value |
|-------|-------|
| **Domain** | communication |
| **Subdomain** | gmail |
| **Capability** | create |
| **Complexity** | atomic |
| **Maturity** | beta |
| **Integration Tier** | external |

## Service

**Service:** `GmailClient`  
**Module:** `src.pydantic_ai_integration.integrations.google_workspace.clients`  
**Implementation:** `GmailClient.send_message`

## Signature

```python
async def send_message(
    self,
    request: GmailSendMessageRequest
) -> GmailSendMessageResponse
```

## Request Model

**Type:** `GmailSendMessageRequest`  
**Module:** `src.pydantic_ai_integration.integrations.google_workspace.models`

### Parameters

*No parameters documented.*


## Response Model

**Type:** `GmailSendMessageResponse`  
**Module:** `src.pydantic_ai_integration.integrations.google_workspace.models`

## Business Rules

| Rule | Value |
|------|-------|
| **Enabled** | ✓ |
| **Requires Auth** | ✓ |
| **Requires Casefile** | ✗ |
| **Timeout** | 30s |

### Required Permissions

- `workspace:gmail:write`


## Usage Example

```python
from src.pydantic_ai_integration.integrations.google_workspace.clients import GmailClient
from src.pydantic_ai_integration.integrations.google_workspace.models import (
    GmailSendMessageRequest,
    GmailSendMessagePayload
)

# Create request
# No parameters required
payload = GmailSendMessagePayload()
request = GmailSendMessageRequest(payload=payload)

# Call method
service = GmailClient()
response = await service.send_message(request)

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
