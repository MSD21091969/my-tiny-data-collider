# store_gmail_messages

Store Gmail messages in casefile

## Classification

| Field | Value |
|-------|-------|
| **Domain** | workspace |
| **Subdomain** | google_workspace |
| **Capability** | update |
| **Complexity** | composite |
| **Maturity** | beta |
| **Integration Tier** | hybrid |

## Service

**Service:** `CasefileService`  
**Module:** `src.casefileservice.service`  
**Implementation:** `CasefileService.store_gmail_messages`

## Signature

```python
async def store_gmail_messages(
    self,
    request: StoreGmailMessagesRequest
) -> StoreGmailMessagesResponse
```

## Request Model

**Type:** `StoreGmailMessagesRequest`  
**Module:** `src.pydantic_models.operations.casefile_ops`

### Parameters

*No parameters documented.*


## Response Model

**Type:** `StoreGmailMessagesResponse`  
**Module:** `src.pydantic_models.operations.casefile_ops`

## Business Rules

| Rule | Value |
|------|-------|
| **Enabled** | ✓ |
| **Requires Auth** | ✓ |
| **Requires Casefile** | ✓ |
| **Casefile Permission Level** | write |
| **Timeout** | 60s |

### Required Permissions

- `casefiles:write`
- `workspace:gmail:read`

### Dependencies

- `GmailClient`


## Usage Example

```python
from src.casefileservice.service import CasefileService
from src.pydantic_models.operations.casefile_ops import (
    StoreGmailMessagesRequest,
    StoreGmailMessagesPayload
)

# Create request
# No parameters required
payload = StoreGmailMessagesPayload()
request = StoreGmailMessagesRequest(payload=payload)

# Call method
service = CasefileService()
response = await service.store_gmail_messages(request)

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
