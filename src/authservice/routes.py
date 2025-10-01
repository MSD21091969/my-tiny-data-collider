"""
Authentication service routes and logic.
"""

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Dict, Any

from .token import validate_credentials, create_token, get_current_user

# Models for API requests/responses
class LoginRequest(BaseModel):
    """Login request with username and password."""
    username: str
    password: str

class TokenResponse(BaseModel):
    """Token response after successful login."""
    access_token: str
    token_type: str
    user: Dict[str, Any]

class UserResponse(BaseModel):
    """User information response."""
    user_id: str
    username: str
    email: str
    roles: list

# Create router
router = APIRouter(
    prefix="/auth",
    tags=["auth"],
    responses={401: {"description": "Unauthorized"}},
)

@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest) -> Dict[str, Any]:
    """Log in with username and password.
    
    Args:
        request: Login request with username and password
        
    Returns:
        Token response with access token
    """
    # Validate credentials (using mock in development)
    user = validate_credentials(request.username, request.password)
    
    # Generate token
    token = create_token(user["user_id"], user["username"])
    
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": user
    }

@router.get("/me", response_model=UserResponse)
async def get_me(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    """Get information about the current user.
    
    Args:
        current_user: Current user information from token
        
    Returns:
        User information
    """
    return {
        "user_id": current_user["user_id"],
        "username": current_user["username"],
        "email": current_user["email"],
        "roles": current_user["roles"]
    }

@router.post("/validate")
async def validate_token(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    """Validate a token and return user information.
    
    Args:
        current_user: Current user information from token
        
    Returns:
        Basic response with validity status
    """
    return {"valid": True, "user_id": current_user["user_id"]}

@router.get("/test-token")
async def test_token() -> Dict[str, Any]:
    """Generate a test token for Sam user.
    
    This is a convenience endpoint for testing without going through login.
    
    Returns:
        Token response
    """
    # Generate token for Sam
    token = create_token("sam123", "Sam")
    
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "user_id": "sam123",
            "username": "Sam",
            "email": "sam@example.com",
            "roles": ["user", "admin"]
        }
    }

@router.post("/quick-login")
async def quick_login() -> Dict[str, Any]:
    """Quick login for Sam - no credentials needed for development.
    
    Returns:
        Token response
    """
    # Generate token for Sam
    token = create_token("sam123", "Sam")
    
    return {
        "access_token": token,
        "token_type": "bearer",
        "message": "Logged in as Sam",
        "token_for_headers": f"Bearer {token}"
    }
    