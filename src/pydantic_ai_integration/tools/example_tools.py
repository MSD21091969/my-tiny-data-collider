"""
Example tool implementation.
"""

from typing import Dict, Any
import asyncio

from ..agents.base import default_agent

@default_agent.tool
async def hello_world(ctx: Any, name: str) -> Dict[str, Any]:
    """
    A simple hello world tool for demonstration purposes.
    
    Args:
        name: The name to greet
        
    Returns:
        A greeting message
    """
    # Access context
    mds_context = ctx.deps if hasattr(ctx, 'deps') else ctx
    
    # Register the event
    mds_context.register_event(
        "hello_world",
        {"name": name}
    )
    
    # Process (simulate some work)
    await asyncio.sleep(0.5)
    
    return {
        "greeting": f"Hello, {name}!",
        "timestamp": mds_context.tool_events[-1].timestamp if mds_context.tool_events else None
    }

@default_agent.tool
async def echo_data(ctx: Any, data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Echo back the provided data with additional metadata.
    
    Args:
        data: The data to echo back
        
    Returns:
        The data with additional metadata
    """
    # Access context
    mds_context = ctx.deps if hasattr(ctx, 'deps') else ctx
    
    # Register the event
    mds_context.register_event(
        "echo_data",
        {"data": data}
    )
    
    return {
        "original_data": data,
        "data_size": len(str(data)),
        "timestamp": mds_context.tool_events[-1].timestamp if mds_context.tool_events else None
    }