# store_drive_files

Store Google Drive files in casefile

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
**Implementation:** `CasefileService.store_drive_files`

## Signature

```python
async def store_drive_files(
    self,
    request: StoreDriveFilesRequest
) -> StoreDriveFilesResponse
```

## Request Model

**Type:** `StoreDriveFilesRequest`  
**Module:** `src.pydantic_models.operations.casefile_ops`

### Parameters

*No parameters documented.*


## Response Model

**Type:** `StoreDriveFilesResponse`  
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
- `workspace:drive:read`

### Dependencies

- `DriveClient`


## Usage Example

```python
from src.casefileservice.service import CasefileService
from src.pydantic_models.operations.casefile_ops import (
    StoreDriveFilesRequest,
    StoreDriveFilesPayload
)

# Create request
# No parameters required
payload = StoreDriveFilesPayload()
request = StoreDriveFilesRequest(payload=payload)

# Call method
service = CasefileService()
response = await service.store_drive_files(request)

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
