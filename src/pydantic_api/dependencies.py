"""
FastAPI dependency injection module.
"""

from typing import Any, Dict

from fastapi import Depends, Request

from authservice import get_current_user
from coreservice.request_hub import RequestHub
from coreservice.service_container import get_service_manager
from tool_sessionservice import ToolSessionService


def get_tool_session_service() -> ToolSessionService:
    """Get an instance of the ToolSessionService."""
    return ToolSessionService()


async def get_request_hub(request: Request) -> RequestHub:
    """Get an instance of RequestHub for orchestrated workflows with injected dependencies.
    
    This is an async dependency that retrieves the firestore_pool and redis_cache
    from the FastAPI app state and injects them into the service manager.
    
    Args:
        request: FastAPI Request object for accessing app state
        
    Returns:
        RequestHub instance with injected service manager
    """
    # Get firestore_pool and redis_cache from app state
    firestore_pool = getattr(request.app.state, 'firestore_pool', None)
    redis_cache = getattr(request.app.state, 'redis_cache', None)

    # Get service manager with injected dependencies
    service_manager = get_service_manager(
        firestore_pool=firestore_pool,
        redis_cache=redis_cache
    )

    return RequestHub(service_manager=service_manager)

def get_current_user_id(current_user: Dict[str, Any] = Depends(get_current_user)) -> str:
    """Get the current authenticated user ID.
    
    Args:
        current_user: Current user information from token
        
    Returns:
        User ID string
    """
    return current_user["user_id"]

def get_auth_context(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    """Extract authentication context from token for routing and validation.
    
    Args:
        current_user: Current user information from token
        
    Returns:
        Auth context dict with user_id, session_request_id, casefile_id, session_id
    """
    return {
        "user_id": current_user["user_id"],
        "session_request_id": current_user.get("session_request_id"),
        "casefile_id": current_user.get("casefile_id"),
        "session_id": current_user.get("session_id"),
    }
    
def verify_casefile_access(
    casefile_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> bool:
    """Verify that the user has access to the casefile.
    
    Args:
        casefile_id: ID of the casefile
        current_user: Current user information from token
        
    Returns:
        True if the user has access
        
    Raises:
        HTTPException: If the user doesn't have access to the casefile
    """
    # In development mode, mock always allows access
    # For production, implement real access control here
    return True