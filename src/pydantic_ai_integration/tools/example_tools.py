"""Legacy example tool implementations.

⚠️ This module exists solely for historical context while the new
tool factory rolls out. Prefer the @register_mds_tool pattern in
``unified_example_tools`` or generated tools moving forward.
"""

import asyncio
import logging
import warnings
from typing import Any, Dict

from ..agents.base import default_agent

logger = logging.getLogger(__name__)

warnings.warn(
    "src.pydantic_ai_integration.tools.example_tools is deprecated; "
    "use unified_example_tools or generated tools instead.",
    DeprecationWarning,
    stacklevel=2,
)
logger.warning(
    "Importing legacy module 'example_tools'. This module will be removed once "
    "all tooling is migrated to the declarative factory."
)

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