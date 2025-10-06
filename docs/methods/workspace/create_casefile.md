# create_casefile

Create new casefile with metadata

## Classification

| Field | Value |
|-------|-------|
| **Domain** | workspace |
| **Subdomain** | casefile |
| **Capability** | create |
| **Complexity** | atomic |
| **Maturity** | stable |
| **Integration Tier** | internal |

## Service

**Service:** `CasefileService`  
**Module:** `src.casefileservice.service`  
**Implementation:** `CasefileService.create_casefile`

## Signature

```python
async def create_casefile(
    self,
    request: CreateCasefileRequest
) -> CreateCasefileResponse
```

## Request Model

**Type:** `CreateCasefileRequest`  
**Module:** `src.pydantic_models.operations.casefile_ops`

### Parameters

*No parameters documented.*


## Response Model

**Type:** `CreateCasefileResponse`  
**Module:** `src.pydantic_models.operations.casefile_ops`

## Business Rules

| Rule | Value |
|------|-------|
| **Enabled** | ✓ |
| **Requires Auth** | ✓ |
| **Requires Casefile** | ✗ |
| **Timeout** | 30s |

### Required Permissions

- `casefiles:write`


## Usage Example

```python
from src.casefileservice.service import CasefileService
from src.pydantic_models.operations.casefile_ops import (
    CreateCasefileRequest,
    CreateCasefilePayload
)

# Create request
# No parameters required
payload = CreateCasefilePayload()
request = CreateCasefileRequest(payload=payload)

# Call method
service = CasefileService()
response = await service.create_casefile(request)

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
