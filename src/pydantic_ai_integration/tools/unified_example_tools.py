"""
Example tools using unified @register_mds_tool decorator.

This module demonstrates the new tool engineering foundation:
1. Define Pydantic model for parameters (guardrails)
2. Use @register_mds_tool decorator (single registration)
3. Implement clean function (validation already done)

FIELD PURPOSES IN PARAMETER MODELS:
- Field constraints (ge=, le=, min_length=, etc.) are BUSINESS LOGIC (guardrails)
- Field descriptions are METADATA (documentation)
- Field defaults are BUSINESS LOGIC (fallback behavior)
- Field types are METADATA (schema definition)

METADATA vs BUSINESS LOGIC in @register_mds_tool:
- name, description, category, version = METADATA (what the tool is)
- required_permissions, requires_casefile, timeout = BUSINESS LOGIC (when/where it runs)
- params_model = EXECUTION (how to validate)
"""

from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
import asyncio

from ..tool_decorator import register_mds_tool
from ..dependencies import MDSContext


# ============================================================================
# PARAMETER MODELS (Pydantic = Guardrails)
# ============================================================================

class ExampleToolParams(BaseModel):
    """
    Parameters for example_tool.
    
    FIELD BREAKDOWN:
    - value: int = METADATA (type descriptor)
    - Field(...) = BUSINESS LOGIC (required constraint)
    - ge=0 = BUSINESS LOGIC (guardrail: must be non-negative)
    - description = METADATA (human-readable documentation)
    
    These constraints are enforced at:
    1. Pydantic validation (parse time)
    2. Decorator wrapper (execution boundary)
    3. OpenAPI schema (API documentation)
    """
    value: int = Field(
        ...,
        ge=0,
        description="The numeric value to process (must be non-negative)"
    )


class AnotherExampleToolParams(BaseModel):
    """
    Parameters for another_example_tool.
    
    FIELD BREAKDOWN:
    - name: METADATA (type) + BUSINESS LOGIC (min_length constraint)
    - count: METADATA (type) + BUSINESS LOGIC (default, ge, le constraints)
    
    Note: min_length=1 is a GUARDRAIL preventing empty names.
    """
    name: str = Field(
        ...,
        min_length=1,
        description="Name to greet (cannot be empty)"
    )
    count: int = Field(
        1,
        ge=1,
        le=10,
        description="Number of times to greet (1-10)"
    )


class AdvancedToolParams(BaseModel):
    """
    Parameters for advanced_tool.
    
    FIELD BREAKDOWN:
    - input_data: METADATA (dict type) + BUSINESS LOGIC (required)
    - options: METADATA (dict type) + BUSINESS LOGIC (optional, has default)
    
    The Optional[Dict] = None pattern is BUSINESS LOGIC (makes field optional).
    """
    input_data: Dict[str, Any] = Field(
        ...,
        description="Input data dictionary to process"
    )
    options: Optional[Dict[str, Any]] = Field(
        None,
        description="Optional configuration for processing"
    )


# ============================================================================
# TOOL IMPLEMENTATIONS (Clean, validation done by decorator)
# ============================================================================

@register_mds_tool(
    # METADATA (WHAT the tool is)
    name="example_tool",
    description="Processes a numeric value - demonstrates basic tool patterns",
    category="examples",
    version="1.0.0",
    tags=["demo", "numeric", "example"],
    
    # BUSINESS LOGIC (WHEN/WHERE it can run)
    enabled=True,
    requires_auth=True,
    required_permissions=[],  # No specific permissions needed (all authenticated users)
    requires_casefile=False,
    timeout_seconds=30,
    
    # EXECUTION (HOW to validate)
    params_model=ExampleToolParams,
)
async def example_tool(ctx: MDSContext, value: int) -> Dict[str, Any]:
    """
    An example tool that processes a numeric value.
    
    NOTE: Parameters are already validated by the decorator!
    The decorator wrapper:
    1. Validates 'value' is an int
    2. Validates 'value' >= 0 (ge=0 constraint)
    3. Only then calls this function
    
    AUDIT TRAIL:
    - ctx.register_event() creates ToolEvent with metadata
    - Event type, parameters, timestamp are automatically tracked
    - result_summary is updated before return
    - All events are persisted in Firestore subcollections
    
    Args:
        ctx: MDSContext with user_id, session_id, casefile_id (METADATA + STATE)
        value: Validated integer >= 0 (guardrails enforced)
        
    Returns:
        Dictionary with processing results
    """
    # Register event (AUDIT TRAIL - captures WHAT and WHEN)
    event_id = ctx.register_event(
        "example_tool",
        {"value": value}
    )
    
    # Simulate processing
    await asyncio.sleep(0.5)
    
    # Calculate results
    squared = value * value
    cubed = value * value * value
    
    result = {
        "original_value": value,  # METADATA (input)
        "squared": squared,  # METADATA (output)
        "cubed": cubed,  # METADATA (output)
        "is_even": (value % 2 == 0),  # METADATA (computed property)
        "timestamp": ctx.tool_events[-1].timestamp if ctx.tool_events else None,  # TEMPORAL (when)
        "event_id": event_id,  # AUDIT TRAIL (correlation)
    }
    
    # Update event with result summary (AUDIT TRAIL)
    if ctx.tool_events:
        last_event = ctx.tool_events[-1]
        last_event.result_summary = {"status": "success", "squared": squared}
        last_event.duration_ms = 500
        last_event.status = "success"
    
    # Add correlation if available (AUDIT TRAIL - links to session request)
    session_request_id = ctx.transaction_context.get("client_request_id")
    if session_request_id:
        result["correlation_id"] = session_request_id
    
    return result


@register_mds_tool(
    # METADATA
    name="another_example_tool",
    description="Generates personalized greeting messages",
    category="examples",
    version="1.0.0",
    tags=["demo", "string", "example"],
    
    # BUSINESS LOGIC
    enabled=True,
    requires_auth=True,
    required_permissions=[],
    requires_casefile=False,
    timeout_seconds=30,
    
    # EXECUTION
    params_model=AnotherExampleToolParams,
)
async def another_example_tool(ctx: MDSContext, name: str, count: int = 1) -> Dict[str, Any]:
    """
    Another example tool that generates repeated messages.
    
    NOTE: Parameters already validated!
    - name is non-empty (min_length=1)
    - count is between 1-10 (ge=1, le=10)
    
    Args:
        ctx: MDSContext
        name: Validated non-empty string
        count: Validated integer 1-10
        
    Returns:
        Dictionary with generated messages
    """
    # Register event (AUDIT TRAIL)
    event_id = ctx.register_event(
        "another_example_tool",
        {"name": name, "count": count}
    )
    
    # Simulate processing
    await asyncio.sleep(0.2 * count)
    
    # Generate messages
    messages = [f"Hello {name}, message {i+1} of {count}" for i in range(count)]
    
    result = {
        "messages": messages,  # METADATA (output)
        "total_messages": count,  # METADATA (computed)
        "timestamp": ctx.tool_events[-1].timestamp if ctx.tool_events else None,  # TEMPORAL
        "event_id": event_id,  # AUDIT TRAIL
    }
    
    # Update event (AUDIT TRAIL)
    if ctx.tool_events:
        last_event = ctx.tool_events[-1]
        last_event.result_summary = {"status": "success", "message_count": count}
        last_event.duration_ms = 200 * count
        last_event.status = "success"
    
    # Add correlation (AUDIT TRAIL)
    session_request_id = ctx.transaction_context.get("client_request_id")
    if session_request_id:
        result["correlation_id"] = session_request_id
    
    return result


@register_mds_tool(
    # METADATA
    name="advanced_tool",
    description="Complex tool demonstrating nested data and options handling",
    category="examples",
    version="1.0.0",
    tags=["demo", "advanced", "nested-data"],
    
    # BUSINESS LOGIC
    enabled=True,
    requires_auth=True,
    required_permissions=["tools:advanced"],  # Requires specific permission
    requires_casefile=False,
    timeout_seconds=60,  # Longer timeout for complex processing
    
    # EXECUTION
    params_model=AdvancedToolParams,
)
async def advanced_tool(
    ctx: MDSContext,
    input_data: Dict[str, Any],
    options: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    A more complex tool that demonstrates handling nested data and options.
    
    NOTE: Parameters already validated!
    - input_data is a non-empty dict (required)
    - options is optional (can be None)
    
    BUSINESS LOGIC vs METADATA:
    - process_mode, include_stats are BUSINESS LOGIC (control behavior)
    - input_data_keys, processed_data are METADATA (content)
    - stats are METADATA (computed information)
    
    Args:
        ctx: MDSContext
        input_data: Validated dictionary
        options: Optional configuration dictionary
        
    Returns:
        Dictionary with processed results and stats
    """
    # Register event (AUDIT TRAIL)
    event_id = ctx.register_event(
        "advanced_tool",
        {"input_data_keys": list(input_data.keys()), "options": options}
    )
    
    # Process options with defaults (BUSINESS LOGIC)
    options = options or {}
    process_mode = options.get("mode", "standard")
    include_stats = options.get("include_stats", True)
    
    # Simulate processing
    await asyncio.sleep(0.5)
    
    # Process based on mode (BUSINESS LOGIC determines HOW)
    if process_mode == "standard":
        processed_data = {
            k: str(v).upper() if isinstance(v, str) else v
            for k, v in input_data.items()
        }
    elif process_mode == "numeric":
        processed_data = {
            k: v * 2 if isinstance(v, (int, float)) else v
            for k, v in input_data.items()
        }
    else:
        processed_data = input_data.copy()
    
    # Build result (METADATA)
    result = {
        "processed_data": processed_data,
        "processing_mode": process_mode,
        "timestamp": ctx.tool_events[-1].timestamp if ctx.tool_events else None,  # TEMPORAL
        "event_id": event_id,  # AUDIT TRAIL
    }
    
    # Add stats if requested (BUSINESS LOGIC controls inclusion)
    if include_stats:
        result["stats"] = {  # METADATA (computed information)
            "input_keys_count": len(input_data),
            "string_values_count": sum(1 for v in input_data.values() if isinstance(v, str)),
            "numeric_values_count": sum(1 for v in input_data.values() if isinstance(v, (int, float)))
        }
    
    # Update event (AUDIT TRAIL)
    if ctx.tool_events:
        last_event = ctx.tool_events[-1]
        last_event.result_summary = {
            "status": "success",
            "mode": process_mode,
            "keys_processed": len(processed_data)
        }
        last_event.duration_ms = 500
        last_event.status = "success"
    
    # Add correlation (AUDIT TRAIL)
    session_request_id = ctx.transaction_context.get("client_request_id")
    if session_request_id:
        result["correlation_id"] = session_request_id
    
    return result


# ============================================================================
# NOTES ON FIELD CATEGORIZATION
# ============================================================================

# METADATA FIELDS (descriptive, immutable):
# - Tool name, description, category, version
# - Parameter names, types, descriptions
# - Result data (output values, computed properties)
# - Used for: Documentation, discovery, analytics
# - Examples: "example_tool", "value: int", squared=100

# BUSINESS LOGIC FIELDS (policy, mutable):
# - Permissions, timeouts, rate limits
# - Validation constraints (ge=, le=, min_length=)
# - Processing modes, options, feature flags
# - Used for: Authorization, validation, behavior control
# - Examples: required_permissions=["tools:advanced"], ge=0, process_mode="standard"

# EXECUTION FIELDS (runtime, functional):
# - params_model (the Pydantic validator)
# - implementation (the function)
# - validation wrappers
# - Used for: Running the tool, enforcing guardrails
# - Examples: ExampleToolParams, validated_wrapper

# TEMPORAL FIELDS (audit, tracking):
# - Timestamps, event IDs, correlation IDs
# - registered_at, created_at, updated_at
# - Duration, execution order
# - Used for: Audit trail, debugging, analytics
# - Examples: timestamp="2025-10-01T10:30:00", duration_ms=500

# STATE FIELDS (context, session):
# - user_id, session_id, casefile_id
# - transaction_context, tool_events
# - Used for: Maintaining execution context
# - Examples: ctx.user_id="sam123", ctx.session_id="ts_..."
