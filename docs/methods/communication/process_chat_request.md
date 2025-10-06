# process_chat_request

Parse message, call LLM, handle tool calls

## Classification

| Field | Value |
|-------|-------|
| **Domain** | communication |
| **Subdomain** | chat_processing |
| **Capability** | process |
| **Complexity** | pipeline |
| **Maturity** | stable |
| **Integration Tier** | hybrid |

## Service

**Service:** `CommunicationService`  
**Module:** `src.communicationservice.service`  
**Implementation:** `CommunicationService.process_chat_request`

## Signature

```python
async def process_chat_request(
    self,
    request: ChatRequest
) -> ChatResponse
```

## Request Model

**Type:** `ChatRequest`  
**Module:** `src.pydantic_models.operations.tool_execution_ops`

### Parameters

*No parameters documented.*


## Response Model

**Type:** `ChatResponse`  
**Module:** `src.pydantic_models.operations.tool_execution_ops`

## Business Rules

| Rule | Value |
|------|-------|
| **Enabled** | ✓ |
| **Requires Auth** | ✓ |
| **Requires Casefile** | ✗ |
| **Timeout** | 120s |

### Required Permissions

- `chat:write`

### Dependencies

- `ToolSessionService.process_tool_request`
- `LLM provider`


## Usage Example

```python
from src.communicationservice.service import CommunicationService
from src.pydantic_models.operations.tool_execution_ops import (
    ChatRequest,
    ChatPayload
)

# Create request
# No parameters required
payload = ChatPayload()
request = ChatRequest(payload=payload)

# Call method
service = CommunicationService()
response = await service.process_chat_request(request)

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
