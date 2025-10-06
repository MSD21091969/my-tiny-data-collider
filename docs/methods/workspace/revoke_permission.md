# revoke_permission

Revoke user permission on casefile

## Classification

| Field | Value |
|-------|-------|
| **Domain** | workspace |
| **Subdomain** | casefile_acl |
| **Capability** | delete |
| **Complexity** | atomic |
| **Maturity** | stable |
| **Integration Tier** | internal |

## Service

**Service:** `CasefileService`  
**Module:** `src.casefileservice.service`  
**Implementation:** `CasefileService.revoke_permission`

## Signature

```python
async def revoke_permission(
    self,
    request: RevokePermissionRequest
) -> RevokePermissionResponse
```

## Request Model

**Type:** `RevokePermissionRequest`  
**Module:** `src.pydantic_models.operations.casefile_ops`

### Parameters

*No parameters documented.*


## Response Model

**Type:** `RevokePermissionResponse`  
**Module:** `src.pydantic_models.operations.casefile_ops`

## Business Rules

| Rule | Value |
|------|-------|
| **Enabled** | ✓ |
| **Requires Auth** | ✓ |
| **Requires Casefile** | ✓ |
| **Casefile Permission Level** | admin |
| **Timeout** | 30s |

### Required Permissions

- `casefiles:share`


## Usage Example

```python
from src.casefileservice.service import CasefileService
from src.pydantic_models.operations.casefile_ops import (
    RevokePermissionRequest,
    RevokePermissionPayload
)

# Create request
# No parameters required
payload = RevokePermissionPayload()
request = RevokePermissionRequest(payload=payload)

# Call method
service = CasefileService()
response = await service.revoke_permission(request)

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
