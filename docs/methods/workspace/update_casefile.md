# update_casefile

Update casefile metadata

## Classification

| Field | Value |
|-------|-------|
| **Domain** | workspace |
| **Subdomain** | casefile |
| **Capability** | update |
| **Complexity** | atomic |
| **Maturity** | stable |
| **Integration Tier** | internal |

## Service

**Service:** `CasefileService`  
**Module:** `src.casefileservice.service`  
**Implementation:** `CasefileService.update_casefile`

## Signature

```python
async def update_casefile(
    self,
    request: UpdateCasefileRequest
) -> UpdateCasefileResponse
```

## Request Model

**Type:** `UpdateCasefileRequest`  
**Module:** `src.pydantic_models.operations.casefile_ops`

### Parameters

*No parameters documented.*


## Response Model

**Type:** `UpdateCasefileResponse`  
**Module:** `src.pydantic_models.operations.casefile_ops`

## Business Rules

| Rule | Value |
|------|-------|
| **Enabled** | ✓ |
| **Requires Auth** | ✓ |
| **Requires Casefile** | ✓ |
| **Casefile Permission Level** | write |
| **Timeout** | 30s |

### Required Permissions

- `casefiles:write`


## Usage Example

```python
from src.casefileservice.service import CasefileService
from src.pydantic_models.operations.casefile_ops import (
    UpdateCasefileRequest,
    UpdateCasefilePayload
)

# Create request
# No parameters required
payload = UpdateCasefilePayload()
request = UpdateCasefileRequest(payload=payload)

# Call method
service = CasefileService()
response = await service.update_casefile(request)

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
