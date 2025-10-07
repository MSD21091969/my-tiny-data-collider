# list_sessions

List chat sessions with filters

## Classification

| Field | Value |
|-------|-------|
| **Domain** | communication |
| **Subdomain** | chat_session |
| **Capability** | search |
| **Complexity** | atomic |
| **Maturity** | stable |
| **Integration Tier** | internal |

## Service

**Service:** `CommunicationService`  
**Module:** `src.communicationservice.service`  
**Implementation:** `CommunicationService.list_sessions`

## Signature

```python
async def list_sessions(
    self,
    request: ListChatSessionsRequest
) -> ListChatSessionsResponse
```

## Request Model

**Type:** `ListChatSessionsRequest`  
**Module:** `src.pydantic_models.operations.chat_session_ops`

### Parameters

*No parameters documented.*


## Response Model

**Type:** `ListChatSessionsResponse`  
**Module:** `src.pydantic_models.operations.chat_session_ops`

## Business Rules

| Rule | Value |
|------|-------|
| **Enabled** | ✓ |
| **Requires Auth** | ✓ |
| **Requires Casefile** | ✗ |
| **Timeout** | 30s |

### Required Permissions

- `chat:read`


## Usage Example

```python
from src.communicationservice.service import CommunicationService
from src.pydantic_models.operations.chat_session_ops import (
    ListChatSessionsRequest,
    ListChatSessionsPayload
)

# Create request
# No parameters required
payload = ListChatSessionsPayload()
request = ListChatSessionsRequest(payload=payload)

# Call method
service = CommunicationService()
response = await service.list_sessions(request)

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
