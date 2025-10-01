# Tool Registration Gap Analysis

## The Problem You Identified

**Q: "is it validating against available (registered?) tool(sets)?"**

**A: No, there's a disconnect between validation and registration!**

## Two Separate Systems

### 1. Agent Registration (`@default_agent.tool`)
```python
# src/pydantic_ai_integration/tools/enhanced_example_tools.py
@default_agent.tool
async def example_tool(ctx: Any, value: int) -> Dict[str, Any]:
    """An example tool..."""
    pass
```

**What it does:**
- Registers tools for **execution** with the agent runtime
- Stores in `default_agent.tools` dict
- Makes tools callable by the agent

**What it doesn't do:**
- ❌ Not used for API request validation
- ❌ Not introspectable for schema generation
- ❌ Doesn't define parameter schemas

### 2. Tool Registry (`tool_registry.py`)
```python
# src/pydantic_ai_integration/tool_registry.py
registry.register_tool(ToolDefinition(
    tool_name="example_tool",
    parameters=[...]
))
```

**What it does:**
- Validates API requests
- Defines parameter schemas
- Provides tool discovery API

**What it doesn't do:**
- ❌ Not connected to actual agent tools
- ❌ Manual registration required (duplication)
- ❌ Can get out of sync with `@default_agent.tool`

### 3. Pydantic Models (`tool_schemas.py` with `Literal`)
```python
# src/pydantic_models/tool_session/tool_schemas.py
ToolName = Literal["example_tool", "another_example_tool"]
```

**What it does:**
- Type-safe validation in Pydantic
- FastAPI generates Swagger dropdown

**What it doesn't do:**
- ❌ Hardcoded - not dynamic
- ❌ Must manually update when tools change
- ❌ Not connected to agent registration

## The Proper Solution

### Option 1: Introspect Agent Registry (Runtime)
```python
# Generate Literal dynamically from agent
def get_registered_tool_names() -> tuple:
    """Get tool names from agent registry."""
    from .agents.base import default_agent
    return tuple(default_agent.get_available_tools())

# Use in model
ToolName = Literal[get_registered_tool_names()]  # Won't work - Literal needs compile-time values
```

**Problem:** `Literal` requires compile-time constants, can't use runtime values.

### Option 2: Decorator Pattern (Build-Time Registration)
```python
# Single registration point
@register_tool(
    name="example_tool",
    params=ExampleToolParams,
    description="Doubles a number"
)
async def example_tool(ctx: Any, value: int) -> Dict[str, Any]:
    pass
```

**This decorator would:**
1. Register with agent (`@default_agent.tool`)
2. Register in tool_registry (for validation)
3. Update type hints / generate Literal dynamically

### Option 3: Validation at Service Layer (Current Best Option)
```python
# src/tool_sessionservice/service.py
async def process_tool_request(...):
    # Check if tool actually exists in agent
    from ..pydantic_ai_integration.agents.base import default_agent
    
    if tool_name not in default_agent.tools:
        available = ', '.join(default_agent.get_available_tools())
        raise HTTPException(
            status_code=400,
            detail=f"Tool '{tool_name}' not registered. Available: {available}"
        )
    
    # Execute
    result = await default_agent.run(...)
```

**Pros:**
- Validates against actual runtime registration
- Single source of truth (agent.tools)
- No duplication

**Cons:**
- Validation happens at service layer, not Pydantic layer
- FastAPI can't auto-generate dropdown (no Literal)
- Less type safety

## Recommended Approach

### Short Term (Pragmatic)
1. **Remove `tool_registry.py`** - it's duplicating agent registration
2. **Service layer validation** - check `default_agent.tools.keys()`
3. **Keep tool_schemas.py** - but use for parameter validation only
4. **Document tool names** - maintain list in docstring/comment

```python
# src/pydantic_models/tool_session/models.py
class ToolRequestPayload(BaseModel):
    tool_name: str = Field(..., description="Tool name (must be registered with agent)")
    parameters: Dict[str, Any] = Field(default_factory=dict)
    
    @field_validator('tool_name')
    @classmethod
    def validate_tool_registered(cls, v: str) -> str:
        """Validate tool is registered with agent."""
        from ...pydantic_ai_integration.agents.base import default_agent
        
        if v not in default_agent.tools:
            available = ', '.join(default_agent.get_available_tools())
            raise ValueError(
                f"Tool '{v}' is not registered. Available tools: {available}"
            )
        return v
```

### Long Term (Ideal)
Build a unified registration system:

```python
# src/pydantic_ai_integration/tool_decorator.py
from typing import Type
from pydantic import BaseModel

class ToolMetadata:
    def __init__(self, name: str, params_model: Type[BaseModel], description: str):
        self.name = name
        self.params_model = params_model
        self.description = description

TOOL_REGISTRY: Dict[str, ToolMetadata] = {}

def register_mds_tool(
    name: str,
    params: Type[BaseModel],
    description: str
):
    """Unified tool registration decorator."""
    def decorator(func):
        # Register metadata
        TOOL_REGISTRY[name] = ToolMetadata(name, params, description)
        
        # Register with agent
        registered_func = default_agent.tool(func)
        
        return registered_func
    
    return decorator

# Usage
@register_mds_tool(
    name="example_tool",
    params=ExampleToolParams,
    description="Doubles a number"
)
async def example_tool(ctx: Any, value: int) -> Dict[str, Any]:
    pass
```

Then generate OpenAPI schema dynamically from `TOOL_REGISTRY`.

## What Needs to Happen

1. **Decide**: Service-layer validation vs unified decorator
2. **Remove**: `tool_registry.py` (redundant)
3. **Simplify**: `tool_schemas.py` to just parameter models
4. **Validate**: Against `default_agent.tools.keys()` in service layer
5. **Document**: Available tools endpoint that introspects agent registry

## Current State vs Ideal

| Feature | Current | Should Be |
|---------|---------|-----------|
| Tool execution | `@default_agent.tool` | Same |
| Parameter schemas | `tool_schemas.py` | Same (but simpler) |
| Validation | `tool_registry.py` | Agent introspection |
| Tool discovery | GET /tool-sessions/tools | GET /tools (from agent) |
| Type safety | `Literal[...]` (static) | Validator (dynamic) |
| Single source of truth | ❌ Three places | ✅ Agent decorator |

## The Core Issue

**We're maintaining three separate lists of tools:**
1. Agent registration (`@default_agent.tool`)
2. Tool registry (`tool_registry.py`)
3. Type hints (`Literal["tool1", "tool2"]`)

**These WILL get out of sync.**

The solution is to **introspect the agent registry at runtime** in validators, not try to maintain parallel static definitions.
