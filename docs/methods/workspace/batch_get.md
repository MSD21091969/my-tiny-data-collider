# batch_get

Batch get Google Sheets data

## Classification

| Field | Value |
|-------|-------|
| **Domain** | workspace |
| **Subdomain** | google_sheets |
| **Capability** | read |
| **Complexity** | atomic |
| **Maturity** | beta |
| **Integration Tier** | external |

## Service

**Service:** `SheetsClient`  
**Module:** `src.pydantic_ai_integration.integrations.google_workspace.clients`  
**Implementation:** `SheetsClient.batch_get`

## Signature

```python
async def batch_get(
    self,
    request: SheetsBatchGetRequest
) -> SheetsBatchGetResponse
```

## Request Model

**Type:** `SheetsBatchGetRequest`  
**Module:** `src.pydantic_ai_integration.integrations.google_workspace.models`

### Parameters

*No parameters documented.*


## Response Model

**Type:** `SheetsBatchGetResponse`  
**Module:** `src.pydantic_ai_integration.integrations.google_workspace.models`

## Business Rules

| Rule | Value |
|------|-------|
| **Enabled** | ✓ |
| **Requires Auth** | ✓ |
| **Requires Casefile** | ✗ |
| **Timeout** | 30s |

### Required Permissions

- `workspace:sheets:read`


## Usage Example

```python
from src.pydantic_ai_integration.integrations.google_workspace.clients import SheetsClient
from src.pydantic_ai_integration.integrations.google_workspace.models import (
    SheetsBatchGetRequest,
    SheetsBatchGetPayload
)

# Create request
# No parameters required
payload = SheetsBatchGetPayload()
request = SheetsBatchGetRequest(payload=payload)

# Call method
service = SheetsClient()
response = await service.batch_get(request)

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
