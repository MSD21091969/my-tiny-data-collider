# Architectural Consolidation Plan: From Definition to Execution

## Current Reality: The Fragmentation

### The Flow Today (Disconnected)

```
1. DEFINITION (Multiple places)
   ├─ @default_agent.tool decorator (runtime registration)
   ├─ tool_registry.py (manual schema definition)
   ├─ tool_schemas.py (Pydantic parameter models)
   └─ models.py (ToolDefinition, ToolParameter)

2. VALIDATION (Multiple layers, duplicate logic)
   ├─ Pydantic field validators (models.py)
   ├─ Service layer validation (service.py)
   └─ Tool registry validation (tool_registry.py)

3. EXECUTION (Disconnected from definition)
   ├─ Agent.run() (base.py)
   ├─ Direct function calls (service.py lines 154-165)
   └─ Tool function implementation (@default_agent.tool)

4. AUDIT TRAIL (Proper! But...)
   ├─ ToolEvent creation (5 event types) ✓
   ├─ Subcollections in Firestore ✓
   └─ MDSContext.register_event() ✓
   
   Problem: No guardrails connecting definition → execution
```

## The Architectural Truth You Identified

**Quote:** "Its back to models, probably giving blocks of code the sunset in terms of models, but not necessarily, and reaffirming pydantic."

You're right. The solution is:
1. **Models are the source of truth** (Pydantic)
2. **Services orchestrate** (no validation logic, just business rules)
3. **Decorators bridge** (connect definition to execution)
4. **Audit trail persists** (already good)

## The Simplified Architecture

### Single Source of Truth: Tool Definition Model

```python
# src/pydantic_models/tool_session/tool_definition.py

from pydantic import BaseModel, Field
from typing import Type, Callable, Dict, Any, Optional, List
from enum import Enum

class ParameterType(str, Enum):
    """Parameter types (Pydantic compatible)."""
    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    OBJECT = "object"
    ARRAY = "array"

class ToolParameterDef(BaseModel):
    """Parameter definition WITH Pydantic model reference."""
    name: str
    param_type: ParameterType
    required: bool = True
    description: Optional[str] = None
    pydantic_model: Optional[Type[BaseModel]] = None  # The actual validator
    
    class Config:
        arbitrary_types_allowed = True  # Allow Type[BaseModel]

class ManagedToolDefinition(BaseModel):
    """
    Complete tool definition that bridges:
    - API layer (schema, validation)
    - Service layer (execution)
    - Agent layer (tool registration)
    """
    name: str
    description: str
    parameters: List[ToolParameterDef]
    category: str = "general"
    enabled: bool = True
    
    # The actual implementation
    implementation: Optional[Callable] = None
    
    # Parameter validation model (generated from parameters)
    params_model: Optional[Type[BaseModel]] = None
    
    class Config:
        arbitrary_types_allowed = True
    
    def validate_params(self, params: Dict[str, Any]) -> BaseModel:
        """Validate parameters using the Pydantic model."""
        if self.params_model:
            return self.params_model(**params)
        return params
    
    def get_openapi_schema(self) -> Dict[str, Any]:
        """Generate OpenAPI schema from Pydantic model."""
        if self.params_model:
            return self.params_model.model_json_schema()
        return {}
```

### Unified Registration Decorator

```python
# src/pydantic_ai_integration/tool_decorator.py

from typing import Callable, Type, Optional
from pydantic import BaseModel
from functools import wraps

# Global registry (single source of truth)
MANAGED_TOOLS: Dict[str, ManagedToolDefinition] = {}

def register_mds_tool(
    name: str,
    params_model: Type[BaseModel],
    description: str,
    category: str = "general"
):
    """
    Single decorator that:
    1. Registers with agent runtime
    2. Stores Pydantic validation model
    3. Makes available to API discovery
    4. Provides OpenAPI schema
    """
    def decorator(func: Callable) -> Callable:
        # Create managed definition
        tool_def = ManagedToolDefinition(
            name=name,
            description=description,
            parameters=[],  # Extract from params_model
            category=category,
            implementation=func,
            params_model=params_model
        )
        
        # Register in global registry
        MANAGED_TOOLS[name] = tool_def
        
        # Register with agent runtime
        from .agents.base import default_agent
        
        @wraps(func)
        async def validated_wrapper(ctx, **kwargs):
            """Wrapper that validates params before execution."""
            # Validate using Pydantic model
            validated = params_model(**kwargs)
            
            # Call original function with validated params
            return await func(ctx, **validated.model_dump())
        
        # Register the wrapped version
        default_agent.tool(validated_wrapper)
        
        # Return original for direct calls
        return func
    
    return decorator

def get_registered_tools() -> Dict[str, ManagedToolDefinition]:
    """Get all registered tools."""
    return MANAGED_TOOLS

def get_tool_names() -> List[str]:
    """Get list of registered tool names (for validation)."""
    return list(MANAGED_TOOLS.keys())

def validate_tool_exists(tool_name: str) -> bool:
    """Check if tool is registered."""
    return tool_name in MANAGED_TOOLS

def get_tool_definition(tool_name: str) -> Optional[ManagedToolDefinition]:
    """Get tool definition."""
    return MANAGED_TOOLS.get(tool_name)
```

### Tool Implementation (Simplified)

```python
# src/pydantic_ai_integration/tools/example_tools.py

from pydantic import BaseModel, Field
from ..tool_decorator import register_mds_tool
from ..dependencies import MDSContext

# Define parameter schema (Pydantic)
class ExampleToolParams(BaseModel):
    value: int = Field(..., ge=0, description="Value to process")

# Register tool (single decorator)
@register_mds_tool(
    name="example_tool",
    params_model=ExampleToolParams,
    description="Processes a numeric value",
    category="example"
)
async def example_tool(ctx: MDSContext, value: int) -> Dict[str, Any]:
    """Implementation is clean - validation already done."""
    ctx.register_event("example_tool", {"value": value})
    
    result = {
        "original": value,
        "squared": value * value,
        "cubed": value * value * value
    }
    
    if ctx.tool_events:
        ctx.tool_events[-1].result_summary = result
    
    return result
```

### Models (Simplified)

```python
# src/pydantic_models/tool_session/models.py

from pydantic import field_validator

class ToolRequestPayload(BaseModel):
    """Payload for tool execution - ONLY validates structure."""
    tool_name: str = Field(..., description="Tool name")
    parameters: Dict[str, Any] = Field(default_factory=dict)
    
    @field_validator('tool_name')
    @classmethod
    def validate_tool_exists(cls, v: str) -> str:
        """Validate tool is registered."""
        from ...pydantic_ai_integration.tool_decorator import validate_tool_exists, get_tool_names
        
        if not validate_tool_exists(v):
            available = ', '.join(get_tool_names())
            raise ValueError(f"Tool '{v}' not registered. Available: {available}")
        
        return v
    
    # NO parameter validation here - that's in the tool's params_model
```

### Service Layer (Drastically Simplified)

```python
# src/tool_sessionservice/service.py

async def process_tool_request(self, request: ToolRequest) -> ToolResponse:
    """Process tool request - ONLY business logic, NO validation."""
    
    # Business rule: Session must exist
    session = await self.repository.get_session(request.session_id)
    if not session:
        raise HTTPException(404, "Session not found")
    
    # Business rule: User must own session (handled in router)
    
    # Get tool definition
    from ..pydantic_ai_integration.tool_decorator import get_tool_definition
    tool_def = get_tool_definition(request.payload.tool_name)
    
    # Validate parameters using tool's Pydantic model
    try:
        validated_params = tool_def.validate_params(request.payload.parameters)
    except ValidationError as e:
        raise HTTPException(422, f"Invalid parameters: {e}")
    
    # Create context
    context = MDSContext(...)
    
    # Execute (validation already done by decorator)
    result = await tool_def.implementation(context, **validated_params.model_dump())
    
    # Audit trail (already good)
    await self._create_events_and_persist(...)
    
    return ToolResponse(...)
```

### API Router (Minimal)

```python
# src/pydantic_api/routers/tool_session.py

@router.get("/tools")
async def list_tools() -> Dict[str, Any]:
    """List available tools - reads from unified registry."""
    from ...pydantic_ai_integration.tool_decorator import get_registered_tools
    
    tools = get_registered_tools()
    
    return {
        "tools": [
            {
                "name": name,
                "description": tool.description,
                "category": tool.category,
                "schema": tool.get_openapi_schema()  # Generated from Pydantic
            }
            for name, tool in tools.items()
            if tool.enabled
        ]
    }

@router.get("/tools/{tool_name}/schema")
async def get_tool_schema(tool_name: str) -> Dict[str, Any]:
    """Get OpenAPI schema for tool parameters."""
    from ...pydantic_ai_integration.tool_decorator import get_tool_definition
    
    tool = get_tool_definition(tool_name)
    if not tool:
        raise HTTPException(404, f"Tool '{tool_name}' not found")
    
    return tool.get_openapi_schema()
```

## What Gets Sunset

### ❌ Delete These Files
- `src/pydantic_ai_integration/tool_registry.py` (replaced by tool_decorator.py)
- `src/pydantic_models/tool_session/tool_schemas.py` (schemas live with tool implementations)

### ❌ Remove These Patterns
- Manual tool registration in `tool_registry._register_builtin_tools()`
- Duplicate validation in service layer
- Hardcoded `Literal["tool1", "tool2"]` type hints

### ✅ Keep These (They're Good)
- `ToolEvent` model and audit trail
- Subcollection persistence pattern
- `MDSContext.register_event()`
- Repository layer
- Base models (BaseRequest, BaseResponse)

## What Gets Simplified

### Before (3 steps)
```python
# 1. Register in tool_registry.py
registry.register_tool(ToolDefinition(...))

# 2. Create Pydantic model
class ExampleToolParams(BaseModel): ...

# 3. Implement function
@default_agent.tool
async def example_tool(...): ...
```

### After (1 step)
```python
# Single decorator does everything
@register_mds_tool(name="example_tool", params_model=ExampleToolParams, ...)
async def example_tool(ctx, value: int): ...
```

## The Guardrails You Mentioned

**Your Quote:** "We've introduced quite the audittrail but might have forgotten about guardrails."

The guardrails ARE the Pydantic models:

```python
class ExampleToolParams(BaseModel):
    value: int = Field(..., ge=0, le=1000)  # Guardrail: 0 ≤ value ≤ 1000
    mode: Literal["fast", "accurate"] = "fast"  # Guardrail: only these values
    
# These guardrails are enforced:
# 1. At Pydantic parse time (422 error)
# 2. At decorator validation (before execution)
# 3. In OpenAPI schema (Swagger UI shows constraints)
```

## Migration Path

### Phase 1: Create Unified Decorator
1. Create `tool_decorator.py` with `@register_mds_tool`
2. Create `ManagedToolDefinition` model
3. Test with one tool (example_tool)

### Phase 2: Migrate Tools
1. Convert each `@default_agent.tool` to `@register_mds_tool`
2. Define `*ToolParams` models
3. Remove from `tool_registry.py`

### Phase 3: Simplify Service Layer
1. Remove validation logic (trust Pydantic)
2. Use `tool_def.validate_params()` and `tool_def.implementation()`
3. Keep only business rules (session exists, permissions, etc.)

### Phase 4: Update API
1. Simplify routers (read from MANAGED_TOOLS)
2. Update `ToolRequestPayload` validator
3. Remove tool_registry imports

### Phase 5: Sunset Old Code
1. Delete `tool_registry.py`
2. Delete `tool_schemas.py`
3. Update tests
4. Update documentation

## Expected Outcome

**Your Quote:** "My intuition says its even going to be simpler too"

**Confirmed. You'll reduce:**
- ~300 lines of code in tool_registry.py → 0
- ~100 lines of validation in service.py → ~20
- Duplicate definitions → Single decorator per tool
- 3 places to update per tool → 1 place

**And gain:**
- ✅ Single source of truth (decorator + Pydantic model)
- ✅ Type safety (MyPy/Pylance understand the models)
- ✅ Auto-generated OpenAPI (from Pydantic)
- ✅ Compile-time validation (can't call with wrong params)
- ✅ Runtime validation (Pydantic enforces constraints)
- ✅ Audit trail intact (events still work)

## The Real Win: Service-to-Service

**Your Quote:** "There's API endpoint to model to logic, and service to service, for us to examine"

With this consolidation:

```python
# Any service can call tools with full type safety
from pydantic_ai_integration.tool_decorator import get_tool_definition

# In CasefileService
async def analyze_casefile(self, casefile_id: str):
    tool = get_tool_definition("document_analyzer")
    params = DocumentAnalyzerParams(casefile_id=casefile_id, depth="full")
    result = await tool.implementation(context, **params.model_dump())
    # Pydantic ensures params are valid, audit trail captures everything
```

No need to go through HTTP endpoints - direct service-to-service calls with full validation and audit trail.

## Conclusion

You identified the core problem: **scattered definition, registration, validation, and execution**.

The solution: **Decorator pattern + Pydantic models = single source of truth**.

This aligns perfectly with your copilot-instructions.md:
> "Data contracts are defined in `src/pydantic_models/**`... prefer reusing them"

Should we start with Phase 1 (create the unified decorator)?
