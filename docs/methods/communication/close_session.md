# close_session

Close chat session

## Classification

| Field | Value |
|-------|-------|
| **Domain** | communication |
| **Subdomain** | chat_session |
| **Capability** | update |
| **Complexity** | atomic |
| **Maturity** | stable |
| **Integration Tier** | internal |

## Service

**Service:** `CommunicationService`  
**Module:** `src.communicationservice.service`  
**Implementation:** `CommunicationService.close_session`

## Signature

```python
async def close_session(
    self,
    request: CloseChatSessionRequest
) -> CloseChatSessionResponse
```

## Request Model

**Type:** `CloseChatSessionRequest`  
**Module:** `src.pydantic_models.operations.chat_session_ops`

### Parameters

*No parameters documented.*


## Response Model

**Type:** `CloseChatSessionResponse`  
**Module:** `src.pydantic_models.operations.chat_session_ops`

## Business Rules

| Rule | Value |
|------|-------|
| **Enabled** | ✓ |
| **Requires Auth** | ✓ |
| **Requires Casefile** | ✗ |
| **Timeout** | 30s |

### Required Permissions

- `chat:write`


## Usage Example

```python
from src.communicationservice.service import CommunicationService
from src.pydantic_models.operations.chat_session_ops import (
    CloseChatSessionRequest,
    CloseChatSessionPayload
)

# Create request
# No parameters required
payload = CloseChatSessionPayload()
request = CloseChatSessionRequest(payload=payload)

# Call method
service = CommunicationService()
response = await service.close_session(request)

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
