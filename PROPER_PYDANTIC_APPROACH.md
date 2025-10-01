# The Proper Pydantic + FastAPI Approach

## What You Called Out (Correctly)

We built a separate `tool_registry.py` system when **Pydantic + FastAPI already give us everything we need** through:
- **Centralized models** (`src/pydantic_models/`)
- **Type validation** (Pydantic's core feature)
- **Auto-documentation** (FastAPI reads Pydantic schemas)

## The Right Pattern

### 1. Define Tool Schemas as Pydantic Models

```python
# src/pydantic_models/tool_session/tool_schemas.py

from pydantic import BaseModel, Field
from typing import Literal

class ExampleToolParams(BaseModel):
    """Parameters for example_tool."""
    value: int = Field(..., description="The number to double", ge=0)

class AnotherExampleToolParams(BaseModel):
    """Parameters for another_example_tool."""
    name: str = Field(..., description="Name to greet", min_length=1)
    count: int = Field(1, description="Number of times to greet", ge=1, le=10)

# Literal for tool names - FastAPI generates dropdown
ToolName = Literal["example_tool", "another_example_tool"]
```

### 2. Use Discriminated Unions (Advanced)

```python
from typing import Union, Annotated
from pydantic import Field, BaseModel

class ExampleToolRequest(BaseModel):
    tool_name: Literal["example_tool"] = "example_tool"
    parameters: ExampleToolParams

class AnotherExampleToolRequest(BaseModel):
    tool_name: Literal["another_example_tool"] = "another_example_tool"
    parameters: AnotherExampleToolParams

# Discriminated union - Pydantic validates based on tool_name
ToolRequestPayload = Annotated[
    Union[ExampleToolRequest, AnotherExampleToolRequest],
    Field(discriminator='tool_name')
]
```

### 3. What FastAPI Auto-Generates

- **Swagger dropdown** for tool_name (from Literal)
- **Dynamic parameter form** based on tool_name selection
- **422 validation errors** with field-level details
- **OpenAPI schema** showing all tool options

## What We Actually Need

### Keep from models.py:
- ✅ `ToolParameter` - schema metadata
- ✅ `ToolDefinition` - tool documentation
- ✅ `ToolsetDefinition` - tool grouping

### Replace tool_registry.py with:
- ✅ Typed parameter models (one per tool)
- ✅ `Literal` for tool_name enum
- ✅ Optional: Discriminated union for ultimate type safety

### Service Layer:
- ✅ Keep business logic validation (session exists, permissions, etc.)
- ❌ Remove schema validation (Pydantic already did it)

## Benefits of the Proper Approach

1. **Single Source of Truth**: Tool schemas ARE the Pydantic models
2. **Type Safety**: MyPy/Pylance validate tool parameter access
3. **Zero Duplication**: Don't maintain registry + models
4. **Better Errors**: Pydantic gives field-level validation out of box
5. **Auto-Documentation**: FastAPI reads models directly

## Migration Path

1. Create `tool_schemas.py` with typed parameter models
2. Update `ToolRequestPayload` to use `Literal` for tool_name
3. Optional: Implement discriminated unions for advanced type safety
4. Remove validation logic from service layer that Pydantic handles
5. Keep only business logic validation (session exists, permissions)

## Example: What Validation Stays Where

### ❌ Don't Do This in Service Layer:
```python
# Pydantic already validates this!
if not isinstance(parameters['value'], int):
    raise ValueError("value must be int")
```

### ✅ Do This in Service Layer:
```python
# Business logic that Pydantic can't know
session = await repo.get_session(session_id)
if not session:
    raise HTTPException(404, "Session not found")

if not user_has_permission(user_id, tool_name):
    raise HTTPException(403, "Not authorized for this tool")
```

## The Copilot Instructions Are Right

From `.github/copilot-instructions.md`:
> Data contracts are defined in `src/pydantic_models/**` and carry computed fields used across services, so prefer reusing them over ad-hoc dicts.

We should have:
1. Used existing `ToolDefinition` model
2. Created typed parameter classes
3. Trusted Pydantic + FastAPI to handle validation

**The framework already gives us a "clear modular foundation with centralized models."**
