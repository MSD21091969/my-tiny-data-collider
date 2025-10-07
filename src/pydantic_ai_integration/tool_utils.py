"""
Tool utilities for session management and chaining.
"""

from typing import Dict, Any, Optional, Callable, Awaitable
from functools import wraps
import logging

from pydantic_ai_integration.dependencies import MDSContext
from pydantic_ai_integration.session_manager import ensure_session_for_tool, chain_tool_execution

logger = logging.getLogger(__name__)


def with_session_resumption(
    auto_create_session: bool = True,
    require_casefile: bool = False
):
    """
    Decorator that enables automatic session resumption for tools.
    
    This decorator allows tools to be called with minimal session management:
    - Automatically creates sessions if none exist
    - Resumes existing sessions based on tokens
    - Handles session validation
    
    Args:
        auto_create_session: Whether to create a session if none provided
        require_casefile: Whether a casefile context is required
        
    Returns:
        Decorated function that handles session management automatically
        
    Example:
        @with_session_resumption(auto_create_session=True)
        async def my_tool(user_id: str, param: str, session_token: str = None) -> Dict[str, Any]:
            # Session context is automatically available in the function
            # No need to manually create or validate sessions
            return {"result": f"processed {param}"}
    """
    def decorator(func: Callable[..., Awaitable[Dict[str, Any]]]) -> Callable[..., Awaitable[Dict[str, Any]]]:
        @wraps(func)
        async def wrapper(
            user_id: str,
            session_token: Optional[str] = None,
            casefile_id: Optional[str] = None,
            client_request_id: Optional[str] = None,
            **kwargs
        ) -> Dict[str, Any]:
            # Get tool name from function
            tool_name = func.__name__
            
            # Ensure session context
            context, session_created = await ensure_session_for_tool(
                user_id=user_id,
                tool_name=tool_name,
                casefile_id=casefile_id,
                session_token=session_token,
                client_request_id=client_request_id,
                auto_create=auto_create_session
            )
            
            # Check casefile requirement
            if require_casefile and not context.casefile_id:
                raise ValueError(f"Tool {tool_name} requires a casefile context")
            
            # Call the original function with context
            try:
                result = await func(context, **kwargs)
                
                # Add session metadata to result
                if isinstance(result, dict):
                    result["_session_info"] = {
                        "session_id": context.session_id,
                        "session_request_id": context.session_request_id,
                        "session_created": session_created,
                        "casefile_id": context.casefile_id
                    }
                
                return result
                
            except Exception as e:
                logger.error(f"Tool {tool_name} execution failed: {e}")
                # Re-raise with session context
                raise e
        
        return wrapper
    
    return decorator


async def execute_tool_with_session(
    tool_func: Callable[..., Awaitable[Dict[str, Any]]],
    user_id: str,
    tool_name: str,
    parameters: Dict[str, Any],
    session_token: Optional[str] = None,
    casefile_id: Optional[str] = None,
    client_request_id: Optional[str] = None,
    auto_create_session: bool = True
) -> Dict[str, Any]:
    """
    Execute a tool function with automatic session management.
    
    This is an alternative to the decorator approach for tools that need
    more control over session management.
    
    Args:
        tool_func: The tool function to execute (should accept MDSContext as first param)
        user_id: User executing the tool
        tool_name: Name of the tool for logging
        parameters: Parameters to pass to the tool
        session_token: Optional existing session token
        casefile_id: Optional casefile context
        client_request_id: Optional client request ID
        auto_create_session: Whether to create session if needed
        
    Returns:
        Tool execution result with session metadata
    """
    # Ensure session context
    context, session_created = await ensure_session_for_tool(
        user_id=user_id,
        tool_name=tool_name,
        casefile_id=casefile_id,
        session_token=session_token,
        client_request_id=client_request_id,
        auto_create=auto_create_session
    )
    
    # Execute tool with context
    result = await tool_func(context, **parameters)
    
    # Add session metadata
    if isinstance(result, dict):
        result["_session_info"] = {
            "session_id": context.session_id,
            "session_request_id": context.session_request_id,
            "session_created": session_created,
            "casefile_id": context.casefile_id
        }
    
    return result


def chain_tools(*tool_funcs: Callable[..., Awaitable[Dict[str, Any]]]):
    """
    Create a tool chain that automatically passes session context between tools.
    
    Args:
        *tool_funcs: Tool functions to chain (each should accept MDSContext as first param)
        
    Returns:
        A chained execution function
        
    Example:
        @chain_tools
        async def tool1(ctx, param1):
            return {"step1": param1}
            
        async def tool2(ctx, param2):
            # ctx will have session info from tool1
            return {"step2": param2}
            
        # Usage:
        result = await chained_tools(user_id, param1="value1", param2="value2")
    """
    async def chained_execution(
        user_id: str,
        session_token: Optional[str] = None,
        casefile_id: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        results = []
        current_context = None
        
        for i, tool_func in enumerate(tool_funcs):
            tool_name = f"{tool_func.__name__}_step{i+1}"
            
            if current_context is None:
                # First tool - create or resume session
                current_context, _ = await ensure_session_for_tool(
                    user_id=user_id,
                    tool_name=tool_name,
                    casefile_id=casefile_id,
                    session_token=session_token
                )
            else:
                # Subsequent tools - chain from previous context
                current_context = await chain_tool_execution(
                    current_context, tool_name, "chained_execution"
                )
            
            # Extract parameters for this tool from kwargs
            # Assume parameters are prefixed with tool name or use generic approach
            tool_params = {}
            for key, value in kwargs.items():
                if key.startswith(f"{tool_func.__name__}_") or key not in [f"{other.__name__}_" for other in tool_funcs]:
                    tool_params[key.replace(f"{tool_func.__name__}_", "")] = value
            
            # Execute tool
            result = await tool_func(current_context, **tool_params)
            results.append(result)
        
        return {
            "chain_results": results,
            "final_session_id": current_context.session_id if current_context else None,
            "steps_executed": len(results)
        }
    
    return chained_execution