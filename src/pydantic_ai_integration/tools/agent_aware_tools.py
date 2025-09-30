"""
Agent-aware tools that demonstrate enhanced MDSContext usage.
"""

from typing import Dict, Any, List, Optional
import asyncio

from ..agents.base import default_agent
from ..dependencies import MDSContext

@default_agent.tool
async def chain_aware_tool(ctx: Any, input_value: str, chain_position: int = None) -> Dict[str, Any]:
    """
    A tool that is aware of its position in a tool chain.
    
    Args:
        input_value: The input value to process
        chain_position: Optional position in a tool chain
        
    Returns:
        The processed results with chain awareness
    """
    # Access context
    mds_context = ctx.deps if hasattr(ctx, 'deps') else ctx
    
    # Get session request ID for correlation
    session_request_id = (mds_context.transaction_context.get("client_request_id") 
                         if isinstance(mds_context, MDSContext) else None)
    
    # Check for history and chain context
    has_history = hasattr(mds_context, 'conversation_history') and mds_context.conversation_history
    has_previous_tools = hasattr(mds_context, 'previous_tools') and mds_context.previous_tools
    
    # Prepare chain context
    chain_context = {
        "position": chain_position,
        "reasoning": "Processing input in tool chain",
        "purpose": "Demonstrate chain-aware tool execution"
    }
    
    # Register the event with chain context
    event_id = mds_context.register_event(
        "chain_aware_tool",
        {"input_value": input_value, "chain_position": chain_position},
        chain_context=chain_context
    )
    
    # Process (simulate some work)
    await asyncio.sleep(0.5)
    
    # Build the result with chain awareness
    result = {
        "processed_value": input_value.upper(),
        "chain_aware": True,
        "timestamp": mds_context.tool_events[-1].timestamp if mds_context.tool_events else None
    }
    
    # Add history information if available
    if has_history:
        result["has_conversation_history"] = True
        result["history_length"] = len(mds_context.conversation_history)
    
    # Add chain information if available
    if has_previous_tools:
        result["previous_tools_count"] = len(mds_context.previous_tools)
        result["is_part_of_chain"] = True
    
    # Add correlation information
    if session_request_id:
        result["correlation_id"] = session_request_id
        result["event_id"] = event_id
    
    return result

@default_agent.tool
async def context_enrichment_tool(ctx: Any, casefile_id: str = None) -> Dict[str, Any]:
    """
    A tool that enriches the context with additional information.
    
    Args:
        casefile_id: Optional casefile ID to link
        
    Returns:
        Summary of context enrichment
    """
    # Access context
    mds_context = ctx.deps if hasattr(ctx, 'deps') else ctx
    
    # Register the event
    event_id = mds_context.register_event(
        "context_enrichment_tool",
        {"casefile_id": casefile_id}
    )
    
    # Add a sample document to related documents if that field exists
    if hasattr(mds_context, 'related_documents'):
        mds_context.link_related_document({
            "id": f"doc-{event_id[:8]}",
            "type": "casefile_document",
            "title": "Sample Related Document",
            "relevance_score": 0.95
        })
    
    # Add a sample conversation message if that field exists
    if hasattr(mds_context, 'conversation_history'):
        mds_context.add_conversation_message({
            "role": "system",
            "content": "Context has been enriched with additional information."
        })
    
    # Plan a sample tool chain if that field exists
    if hasattr(mds_context, 'next_planned_tools'):
        mds_context.plan_tool_chain([
            {"tool_name": "chain_aware_tool", "parameters": {"input_value": "follow-up action 1"}},
            {"tool_name": "chain_aware_tool", "parameters": {"input_value": "follow-up action 2"}}
        ], reasoning="Demonstrating planned tool chain")
    
    # Build result
    result = {
        "context_enriched": True,
        "added_document": hasattr(mds_context, 'related_documents'),
        "added_message": hasattr(mds_context, 'conversation_history'),
        "planned_chain": hasattr(mds_context, 'next_planned_tools'),
        "event_id": event_id
    }
    
    return result