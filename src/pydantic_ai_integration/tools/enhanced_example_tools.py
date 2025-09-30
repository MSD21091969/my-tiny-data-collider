"""
Enhanced example tools that work with the updated model structure.
"""

from typing import Dict, Any, List, Optional
import asyncio

from ..agents.base import default_agent
from ..dependencies import MDSContext

@default_agent.tool
async def example_tool(ctx: Any, value: int) -> Dict[str, Any]:
    """
    An example tool that processes a numeric value.
    
    Args:
        value: The numeric value to process
        
    Returns:
        The processed results
    """
    # Access context
    mds_context = ctx.deps if hasattr(ctx, 'deps') else ctx
    
    # Get session request ID for correlation
    session_request_id = (mds_context.transaction_context.get("client_request_id") 
                         if isinstance(mds_context, MDSContext) else None)
    
    # Register the event
    event_id = mds_context.register_event(
        "example_tool",
        {"value": value}
    )
    
    # Process (simulate some work)
    await asyncio.sleep(0.5)
    squared = value * value
    cubed = value * value * value
    
    result = {
        "original_value": value,
        "squared": squared,
        "cubed": cubed,
        "is_even": (value % 2 == 0),
        "timestamp": mds_context.tool_events[-1].timestamp if mds_context.tool_events else None
    }
    
    # Update the event with result summary
    if mds_context.tool_events:
        last_event = mds_context.tool_events[-1]
        last_event.result_summary = {"status": "success", "squared": squared}
        last_event.duration_ms = 500  # Simulated duration
    
    # Add correlation information
    if session_request_id:
        result["correlation_id"] = session_request_id
        result["event_id"] = event_id
    
    return result

@default_agent.tool
async def another_example_tool(ctx: Any, name: str, count: int = 1) -> Dict[str, Any]:
    """
    Another example tool that generates repeated messages.
    
    Args:
        name: The name to use in messages
        count: How many messages to generate
        
    Returns:
        The generated messages
    """
    # Access context
    mds_context = ctx.deps if hasattr(ctx, 'deps') else ctx
    
    # Get session request ID for correlation
    session_request_id = (mds_context.transaction_context.get("client_request_id") 
                         if isinstance(mds_context, MDSContext) else None)
    
    # Register the event
    event_id = mds_context.register_event(
        "another_example_tool",
        {"name": name, "count": count}
    )
    
    # Process (simulate some work)
    await asyncio.sleep(0.2 * count)
    
    messages = [f"Hello {name}, message {i+1} of {count}" for i in range(count)]
    
    result = {
        "messages": messages,
        "total_messages": count,
        "timestamp": mds_context.tool_events[-1].timestamp if mds_context.tool_events else None
    }
    
    # Update the event with result summary
    if mds_context.tool_events:
        last_event = mds_context.tool_events[-1]
        last_event.result_summary = {"status": "success", "message_count": count}
        last_event.duration_ms = 200 * count  # Simulated duration
    
    # Add correlation information
    if session_request_id:
        result["correlation_id"] = session_request_id
        result["event_id"] = event_id
    
    return result

@default_agent.tool
async def advanced_tool(
    ctx: Any, 
    input_data: Dict[str, Any],
    options: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    A more complex tool that demonstrates handling nested data and options.
    
    Args:
        input_data: The input data dictionary to process
        options: Optional configuration for processing
        
    Returns:
        The processed results
    """
    # Access context
    mds_context = ctx.deps if hasattr(ctx, 'deps') else ctx
    
    # Get session request ID for correlation
    session_request_id = (mds_context.transaction_context.get("client_request_id") 
                         if isinstance(mds_context, MDSContext) else None)
    
    # Prepare options with defaults
    options = options or {}
    process_mode = options.get("mode", "standard")
    include_stats = options.get("include_stats", True)
    
    # Register the event
    event_id = mds_context.register_event(
        "advanced_tool",
        {"input_data_keys": list(input_data.keys()), "options": options}
    )
    
    # Process based on mode (simulate different processing)
    await asyncio.sleep(0.5)
    
    # Create result based on processing mode
    if process_mode == "standard":
        processed_data = {k: str(v).upper() if isinstance(v, str) else v 
                         for k, v in input_data.items()}
    elif process_mode == "numeric":
        processed_data = {k: v * 2 if isinstance(v, (int, float)) else v 
                         for k, v in input_data.items()}
    else:
        processed_data = input_data.copy()
    
    # Build result
    result = {
        "processed_data": processed_data,
        "processing_mode": process_mode,
        "timestamp": mds_context.tool_events[-1].timestamp if mds_context.tool_events else None
    }
    
    # Add stats if requested
    if include_stats:
        result["stats"] = {
            "input_keys_count": len(input_data),
            "string_values_count": sum(1 for v in input_data.values() if isinstance(v, str)),
            "numeric_values_count": sum(1 for v in input_data.values() if isinstance(v, (int, float)))
        }
    
    # Update the event with result summary
    if mds_context.tool_events:
        last_event = mds_context.tool_events[-1]
        last_event.result_summary = {
            "status": "success", 
            "mode": process_mode,
            "keys_processed": len(processed_data)
        }
        last_event.duration_ms = 500  # Simulated duration
    
    # Add correlation information
    if session_request_id:
        result["correlation_id"] = session_request_id
        result["event_id"] = event_id
    
    return result