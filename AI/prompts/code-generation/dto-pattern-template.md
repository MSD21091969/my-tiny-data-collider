# DTO Pattern Template (R-A-R)

*Last updated: October 8, 2025*  
*Sync status: ✅ UP TO DATE (October 8, 2025 - Foundation Sync)*

Template for creating Request-Action-Response (R-A-R) pattern DTOs with Pydantic.

## Context

**Repository**: my-tiny-data-collider  
**Architecture**: 6-Layer Model System  
**Pattern**: Request-Action-Response (R-A-R)  
**Compliance**: 100% (23/23 operations)  
**Location**: `src/pydantic_models/`

## Task Definition

Create a complete DTO set following R-A-R pattern:
1. Payload model (L1) - Business data
2. Request DTO (L2) - Execution envelope
3. Response DTO (L2) - Result envelope

All DTOs must use proper type hints, validation, and documentation.

## Template Structure

### Layer 1: Payload Models

```python
"""
Payload models for {domain}.{subdomain}.{action} operation.
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class {Action}Payload(BaseModel):
    """
    Payload for {action} operation.
    
    This represents the business data required for the operation.
    """
    
    # Required fields with validation
    field_name: str = Field(
        ...,
        description="Description of the field",
        min_length=1,
        max_length=255
    )
    
    # Optional fields with defaults
    optional_field: Optional[str] = Field(
        None,
        description="Optional field description"
    )
    
    # Validated fields with constraints
    count: int = Field(
        default=0,
        ge=0,
        description="Non-negative count value"
    )
    
    class Config:
        """Pydantic model configuration."""
        json_schema_extra = {
            "example": {
                "field_name": "example value",
                "optional_field": "optional example",
                "count": 10
            }
        }

class {Action}ResultPayload(BaseModel):
    """
    Result payload for {action} operation.
    
    This represents the business data returned from the operation.
    """
    
    # Result fields
    entity_id: str = Field(
        ...,
        description="Unique identifier of created/updated entity"
    )
    
    status: str = Field(
        ...,
        description="Operation status"
    )
    
    created_at: datetime = Field(
        ...,
        description="Timestamp of creation"
    )
    
    class Config:
        """Pydantic model configuration."""
        json_schema_extra = {
            "example": {
                "entity_id": "entity_12345",
                "status": "active",
                "created_at": "2025-10-08T12:00:00Z"
            }
        }
```

### Layer 2: Request DTO

```python
"""
Request DTO for {domain}.{subdomain}.{action} operation.
"""
from src.pydantic_models.base.request_response import BaseRequest
from typing import Literal

class {Action}Request(BaseRequest[{Action}Payload]):
    """
    Request for {action} operation.
    
    Follows R-A-R pattern: {Action}Request(BaseRequest[{Action}Payload])
    
    Attributes:
        operation: Literal operation identifier
        payload: {Action}Payload containing business data
        
    Example:
        >>> request = {Action}Request(
        ...     operation="{domain}.{subdomain}.{action}",
        ...     payload={Action}Payload(
        ...         field_name="value",
        ...         count=5
        ...     )
        ... )
    """
    
    operation: Literal["{domain}.{subdomain}.{action}"] = "{domain}.{subdomain}.{action}"
```

### Layer 2: Response DTO

```python
"""
Response DTO for {domain}.{subdomain}.{action} operation.
"""
from src.pydantic_models.base.request_response import BaseResponse
from src.pydantic_models.base.enums import RequestStatus

class {Action}Response(BaseResponse[{Action}ResultPayload]):
    """
    Response for {action} operation.
    
    Follows R-A-R pattern: {Action}Response(BaseResponse[{Action}ResultPayload])
    
    Attributes:
        status: RequestStatus enum
        payload: {Action}ResultPayload containing result data
        
    Example:
        >>> response = {Action}Response(
        ...     request_id="req_12345",
        ...     status=RequestStatus.COMPLETED,
        ...     payload={Action}ResultPayload(
        ...         entity_id="entity_12345",
        ...         status="active",
        ...         created_at=datetime.now()
        ...     )
        ... )
    """
    pass
```

## Complete Example: CreateCasefileRequest

```python
# src/pydantic_models/workspace/casefile_payloads.py
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class CreateCasefilePayload(BaseModel):
    """Payload for creating a new casefile."""
    
    title: str = Field(
        ...,
        description="Casefile title",
        min_length=1,
        max_length=255
    )
    
    description: Optional[str] = Field(
        None,
        description="Optional casefile description",
        max_length=1000
    )
    
    tags: list[str] = Field(
        default_factory=list,
        description="Optional tags for categorization"
    )

class CreateCasefileResultPayload(BaseModel):
    """Result payload for casefile creation."""
    
    casefile_id: str = Field(..., description="Unique casefile identifier")
    status: str = Field(..., description="Casefile status")
    created_at: datetime = Field(..., description="Creation timestamp")


# src/pydantic_models/operations/casefile_operations.py
from src.pydantic_models.base.request_response import BaseRequest, BaseResponse
from src.pydantic_models.workspace.casefile_payloads import (
    CreateCasefilePayload,
    CreateCasefileResultPayload
)
from typing import Literal

class CreateCasefileRequest(BaseRequest[CreateCasefilePayload]):
    """Request to create a new casefile."""
    operation: Literal["workspace.casefile.create_casefile"] = "workspace.casefile.create_casefile"

class CreateCasefileResponse(BaseResponse[CreateCasefileResultPayload]):
    """Response from casefile creation."""
    pass
```

## Guidelines

### Naming Conventions
- **Payload**: `{Action}Payload` (business data)
- **Result**: `{Action}ResultPayload` (operation result)
- **Request**: `{Action}Request` (inherits BaseRequest[{Action}Payload])
- **Response**: `{Action}Response` (inherits BaseResponse[{Action}ResultPayload])

### Operation Naming
- Format: `{domain}.{subdomain}.{action}`
- Example: `workspace.casefile.create_casefile`
- Must match method name in MANAGED_METHODS

### Field Validation
- Use Pydantic `Field()` for all fields
- Include descriptions for all fields
- Add validation constraints (min_length, max_length, ge, le, etc.)
- Provide default values for optional fields

### Type Hints
- Use proper type annotations (str, int, Optional[str], list[str])
- Import types from `typing` module
- Use `datetime` from `datetime` module
- Avoid `Any` type unless absolutely necessary

## Validation Checklist

- [ ] Payload model inherits from BaseModel
- [ ] Request DTO inherits from BaseRequest[{Action}Payload]
- [ ] Response DTO inherits from BaseResponse[{Action}ResultPayload]
- [ ] Operation field is Literal type with correct value
- [ ] All fields have descriptions
- [ ] Validation constraints are appropriate
- [ ] Examples provided in Config
- [ ] Type hints are complete and correct
- [ ] Docstrings follow format with Args/Returns

## Service Integration

```python
# src/{domain}service/service.py
from src.pydantic_models.operations.{domain}_operations import (
    {Action}Request,
    {Action}Response,
    {Action}ResultPayload
)
from src.pydantic_models.base.enums import RequestStatus
from datetime import datetime

class {Domain}Service:
    """Service for {domain} operations."""
    
    async def {action}(
        self,
        request: {Action}Request
    ) -> {Action}Response:
        """
        Execute {action} operation.
        
        Args:
            request: {Action}Request with operation details
            
        Returns:
            {Action}Response with operation results
            
        Raises:
            ValidationError: If request data is invalid
            ServiceError: If operation fails
        """
        start_time = datetime.now()
        
        try:
            # Extract payload
            payload = request.payload
            
            # Execute business logic
            result = await self.repository.{action}(
                title=payload.title,
                description=payload.description,
                user_id=request.user_id
            )
            
            # Build result payload
            result_payload = {Action}ResultPayload(
                entity_id=result.id,
                status=result.status,
                created_at=result.created_at
            )
            
            # Build response
            return {Action}Response(
                request_id=request.request_id,
                status=RequestStatus.COMPLETED,
                payload=result_payload,
                metadata={
                    'execution_time_ms': (datetime.now() - start_time).total_seconds() * 1000
                }
            )
            
        except Exception as e:
            # Error handling
            return {Action}Response(
                request_id=request.request_id,
                status=RequestStatus.FAILED,
                error_message=str(e)
            )
```

## Related Resources

- [Base Request/Response Models](../../../src/pydantic_models/base/request_response.py)
- [Model Registry](../../../config/models_inventory_v1.yaml)
- [Method Registry](../../../config/methods_inventory_v1.yaml)
- [HANDOVER Document](../../../HANDOVER.md)

---

**Note**: All DTOs in this repository follow the R-A-R pattern (100% compliance). Parameters defined in payload models are automatically extracted by the method registry and inherited by tools.
