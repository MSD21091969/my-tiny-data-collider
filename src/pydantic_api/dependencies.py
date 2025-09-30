"""
FastAPI dependency injection module.
"""

from typing import Callable, Dict, Any
from functools import lru_cache

from fastapi import Depends, HTTPException, status

from ..tool_sessionservice import ToolSessionService
from ..coreservice.config import get_use_mocks
from ..authservice import get_current_user

@lru_cache()
def get_tool_session_service(use_mocks: bool = Depends(get_use_mocks)) -> ToolSessionService:
    """Get an instance of the ToolSessionService."""
    return ToolSessionService(use_mocks=use_mocks)

def get_current_user_id(current_user: Dict[str, Any] = Depends(get_current_user)) -> str:
    """Get the current authenticated user ID.
    
    Args:
        current_user: Current user information from token
        
    Returns:
        User ID string
    """
    return current_user["user_id"]
    
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