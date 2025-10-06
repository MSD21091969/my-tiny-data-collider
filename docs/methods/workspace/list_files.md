# list_files

List Google Drive files

## Classification

| Field | Value |
|-------|-------|
| **Domain** | workspace |
| **Subdomain** | google_drive |
| **Capability** | read |
| **Complexity** | atomic |
| **Maturity** | beta |
| **Integration Tier** | external |

## Service

**Service:** `DriveClient`  
**Module:** `src.pydantic_ai_integration.integrations.google_workspace.clients`  
**Implementation:** `DriveClient.list_files`

## Signature

```python
async def list_files(
    self,
    request: DriveListFilesRequest
) -> DriveListFilesResponse
```

## Request Model

**Type:** `DriveListFilesRequest`  
**Module:** `src.pydantic_ai_integration.integrations.google_workspace.models`

### Parameters

*No parameters documented.*


## Response Model

**Type:** `DriveListFilesResponse`  
**Module:** `src.pydantic_ai_integration.integrations.google_workspace.models`

## Business Rules

| Rule | Value |
|------|-------|
| **Enabled** | ✓ |
| **Requires Auth** | ✓ |
| **Requires Casefile** | ✗ |
| **Timeout** | 30s |

### Required Permissions

- `workspace:drive:read`


## Usage Example

```python
from src.pydantic_ai_integration.integrations.google_workspace.clients import DriveClient
from src.pydantic_ai_integration.integrations.google_workspace.models import (
    DriveListFilesRequest,
    DriveListFilesPayload
)

# Create request
# No parameters required
payload = DriveListFilesPayload()
request = DriveListFilesRequest(payload=payload)

# Call method
service = DriveClient()
response = await service.list_files(request)

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
