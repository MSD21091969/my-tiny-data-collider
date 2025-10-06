# delete_casefile

Delete casefile permanently

## Classification

| Field | Value |
|-------|-------|
| **Domain** | workspace |
| **Subdomain** | casefile |
| **Capability** | delete |
| **Complexity** | atomic |
| **Maturity** | stable |
| **Integration Tier** | internal |

## Service

**Service:** `CasefileService`  
**Module:** `src.casefileservice.service`  
**Implementation:** `CasefileService.delete_casefile`

## Signature

```python
async def delete_casefile(
    self,
    request: DeleteCasefileRequest
) -> DeleteCasefileResponse
```

## Request Model

**Type:** `DeleteCasefileRequest`  
**Module:** `src.pydantic_models.operations.casefile_ops`

### Parameters

*No parameters documented.*


## Response Model

**Type:** `DeleteCasefileResponse`  
**Module:** `src.pydantic_models.operations.casefile_ops`

## Business Rules

| Rule | Value |
|------|-------|
| **Enabled** | ✓ |
| **Requires Auth** | ✓ |
| **Requires Casefile** | ✓ |
| **Casefile Permission Level** | owner |
| **Timeout** | 30s |

### Required Permissions

- `casefiles:delete`


## Usage Example

```python
from src.casefileservice.service import CasefileService
from src.pydantic_models.operations.casefile_ops import (
    DeleteCasefileRequest,
    DeleteCasefilePayload
)

# Create request
# No parameters required
payload = DeleteCasefilePayload()
request = DeleteCasefileRequest(payload=payload)

# Call method
service = CasefileService()
response = await service.delete_casefile(request)

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
