# check_permission

Check if user has specific permission

## Classification

| Field | Value |
|-------|-------|
| **Domain** | workspace |
| **Subdomain** | casefile_acl |
| **Capability** | read |
| **Complexity** | atomic |
| **Maturity** | stable |
| **Integration Tier** | internal |

## Service

**Service:** `CasefileService`  
**Module:** `src.casefileservice.service`  
**Implementation:** `CasefileService.check_permission`

## Signature

```python
async def check_permission(
    self,
    request: CheckPermissionRequest
) -> CheckPermissionResponse
```

## Request Model

**Type:** `CheckPermissionRequest`  
**Module:** `src.pydantic_models.operations.casefile_ops`

### Parameters

*No parameters documented.*


## Response Model

**Type:** `CheckPermissionResponse`  
**Module:** `src.pydantic_models.operations.casefile_ops`

## Business Rules

| Rule | Value |
|------|-------|
| **Enabled** | ✓ |
| **Requires Auth** | ✓ |
| **Requires Casefile** | ✓ |
| **Casefile Permission Level** | read |
| **Timeout** | 30s |

### Required Permissions

- `casefiles:read`


## Usage Example

```python
from src.casefileservice.service import CasefileService
from src.pydantic_models.operations.casefile_ops import (
    CheckPermissionRequest,
    CheckPermissionPayload
)

# Create request
# No parameters required
payload = CheckPermissionPayload()
request = CheckPermissionRequest(payload=payload)

# Call method
service = CasefileService()
response = await service.check_permission(request)

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
