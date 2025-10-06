# Service Methods API Reference

**Version:** 1.0.0  
**Generated:** 2025-10-06  
**Total Methods:** 26

## Overview

This API reference documents all service-level methods in the system, organized by classification hierarchy.

All methods follow the **BaseRequest→BaseResponse** pattern with:
- ✅ Pydantic validation
- ✅ Type safety
- ✅ Execution tracking (execution_time_ms)
- ✅ Standardized error handling
- ✅ Permission-based access control

## Statistics

### By Domain
- **Automation**: 1 methods
- **Communication**: 10 methods
- **Workspace**: 15 methods

### By Capability
- **Create**: 3 methods
- **Delete**: 2 methods
- **Process**: 3 methods
- **Read**: 8 methods
- **Search**: 3 methods
- **Update**: 7 methods

### By Maturity
- **Beta**: 9 methods
- **Stable**: 17 methods

### By Integration Tier
- **External**: 6 methods
- **Hybrid**: 5 methods
- **Internal**: 15 methods


## Navigation

### By Domain
- [Workspace](./workspace/README.md)
- [Communication](./communication/README.md)
- [Automation](./automation/README.md)


### By Service
- [CasefileService](./services/CasefileService.md) (13 methods)
- [CommunicationService](./services/CommunicationService.md) (6 methods)
- [DriveClient](./services/DriveClient.md) (1 methods)
- [GmailClient](./services/GmailClient.md) (4 methods)
- [SheetsClient](./services/SheetsClient.md) (1 methods)
- [ToolSessionService](./services/ToolSessionService.md) (1 methods)


## Quick Links

- [Methods Registry Documentation](../registry/README.md) - System documentation
- [Reference Guide](../registry/reference.md) - Classification schema, stats, model coverage
- [Methods Inventory YAML](../../config/methods_inventory_v1.yaml) - Source configuration
- [Versioning Guide](../registry/versioning-guide.md) - Semver rules
- [CHANGELOG](../registry/CHANGELOG.md) - Version history

## Usage Pattern

All methods follow this pattern:

```python
from src.casefileservice.service import CasefileService
from src.pydantic_models.operations.casefile_ops import (
    CreateCasefileRequest,
    CreateCasefilePayload
)

# Create request
payload = CreateCasefilePayload(
    title="My Casefile",
    description="Investigation notes"
)
request = CreateCasefileRequest(payload=payload)

# Call service method
service = CasefileService()
response = await service.create_casefile(request)

# Handle response
if response.status == RequestStatus.COMPLETED:
    casefile_id = response.payload.casefile_id
    print(f"Created casefile: {casefile_id}")
    print(f"Execution time: {response.metadata['execution_time_ms']}ms")
else:
    print(f"Error: {response.error}")
```

## Response Envelope

All methods return `BaseResponse[T]`:

```python
class BaseResponse(BaseModel, Generic[T]):
    request_id: UUID
    status: RequestStatus  # COMPLETED | FAILED | PENDING
    payload: T  # Business payload
    error: Optional[str]
    metadata: Dict[str, Any]  # execution_time_ms, etc.
```
