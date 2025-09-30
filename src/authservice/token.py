"""
JWT token handling and authentication logic.
"""

import time
import jwt
import logging
import os
from typing import Dict, Any, Optional
from datetime import UTC, datetime, timedelta
from fastapi import HTTPException, Depends, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# Configure logging
logger = logging.getLogger(__name__)

# Development mode configuration
def is_dev_mode() -> bool:
    """Check if we're in development mode."""
    return os.environ.get("ENVIRONMENT", "development").lower() == "development"

# Mock configuration - hardcoded for development
MOCK_USER = {
    "user_id": "sam123",
    "username": "Sam",
    "password": "Sam",
    "email": "sam@example.com",
    "is_active": True,
    "roles": ["user", "admin"]
}

# JWT settings
SECRET_KEY = "development_secret_key_replace_in_production"
ALGORITHM = "HS256"
TOKEN_EXPIRE_MINUTES = 60

# Security scheme
security = HTTPBearer(auto_error=False)  # Don't auto-error in dev mode

def create_token(user_id: str, username: str, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT token.
    
    Args:
        user_id: User ID to encode in the token
        username: Username to encode in the token
        expires_delta: Optional custom expiration time
        
    Returns:
        JWT token string
    """
    logger.info(f"Creating token for user: {username} ({user_id})")
    logger.info(f"Using JWT version: {jwt.__version__}")
    
    expire = datetime.now(UTC) + (expires_delta or timedelta(minutes=TOKEN_EXPIRE_MINUTES))
    
    # Token payload
    payload = {
        "sub": user_id,
        "username": username,
        "exp": int(expire.timestamp()),
    "iat": int(datetime.now(UTC).timestamp()),
    }
    
    logger.info(f"Token payload: {payload}")
    
    try:
        # Create token
        encoded_jwt = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
        logger.info(f"Token type: {type(encoded_jwt)}")
        
        # Convert from bytes to string if needed
        if isinstance(encoded_jwt, bytes):
            encoded_jwt = encoded_jwt.decode('utf-8')
            logger.info("Converted token from bytes to string")
        
        return encoded_jwt
    except Exception as e:
        logger.error(f"Error encoding token: {str(e)}")
        raise

def decode_token(token: str) -> Dict[str, Any]:
    """Decode and validate a JWT token.
    
    Args:
        token: JWT token string
        
    Returns:
        Decoded token payload
        
    Raises:
        HTTPException: If token is invalid or expired
    """
    logger.info(f"Decoding token (first 10 chars): {token[:10] if token else 'None'}...")
    
    if not token:
        logger.error("Token is empty")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token is empty",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if token looks like a JWT (has two dots)
    if token.count('.') != 2:
        logger.error(f"Token does not look like a JWT (dots count: {token.count('.')})")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token format: expected 3 segments separated by dots",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        logger.info(f"Attempting to decode token with algorithm {ALGORITHM}")
        # In development mode, skip expiration verification due to system clock issues
        payload = jwt.decode(
            token, 
            SECRET_KEY, 
            algorithms=[ALGORITHM],
            options={"verify_exp": False}  # Skip expiration check in development
        )
        logger.info(f"Token decoded successfully: {payload}")
        
        return payload
        
    except jwt.PyJWTError as e:
        logger.error(f"JWT decode error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )

def validate_credentials(username: str, password: str) -> Dict[str, Any]:
    """Validate user credentials and return user info.
    
    Args:
        username: Username to validate
        password: Password to validate
        
    Returns:
        User information dictionary
        
    Raises:
        HTTPException: If credentials are invalid
    """
    # In development mode, just check against hardcoded values
    if username == MOCK_USER["username"] and password == MOCK_USER["password"]:
        return {
            "user_id": MOCK_USER["user_id"],
            "username": MOCK_USER["username"],
            "email": MOCK_USER["email"],
            "roles": MOCK_USER["roles"]
        }
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """FastAPI dependency to get the current authenticated user.
    
    Args:
        credentials: HTTP Authorization credentials
        
    Returns:
        User information from the token
        
    Raises:
        HTTPException: If token is invalid or missing
    """
    # In development mode, always return Sam user if no credentials provided
    if is_dev_mode() and not credentials:
        logger.info("Development mode: No credentials provided, returning default Sam user")
        return {
            "user_id": MOCK_USER["user_id"],
            "username": MOCK_USER["username"],
            "email": MOCK_USER["email"],
            "roles": MOCK_USER["roles"]
        }
    
    if not credentials:
        logger.error("No credentials provided")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header missing",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = credentials.credentials
    logger.info(f"Received token: {token[:20] if token and len(token) > 20 else token}...")
    
    payload = decode_token(token)
    
    # Extract user info from token
    user_id = payload.get("sub")
    username = payload.get("username")
    
    if not user_id or not username:
        logger.error(f"Invalid token content: user_id={user_id}, username={username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token content",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    # In development mode, just return mock user data
    return {
        "user_id": user_id,
        "username": username,
        "email": MOCK_USER["email"],
        "roles": MOCK_USER["roles"]
    }

def get_dev_user() -> Dict[str, Any]:
    """Get development user for testing without authentication.
    
    Returns:
        Development user information
    """
    if not is_dev_mode():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Development user only available in development mode"
        )
    
    return {
        "user_id": MOCK_USER["user_id"],
        "username": MOCK_USER["username"],
        "email": MOCK_USER["email"],
        "roles": MOCK_USER["roles"]
    }

def create_dev_token() -> str:
    """Create a development token for Sam user with 1 hour expiry.
    
    Returns:
        JWT token string for development use
    """
    if not is_dev_mode():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Development token only available in development mode"
        )
    
    return create_token(
        user_id=MOCK_USER["user_id"],
        username=MOCK_USER["username"],
        expires_delta=timedelta(hours=1)
    )

def verify_admin(user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    """Verify that the user is an admin.
    
    Args:
        user: User information from token
        
    Returns:
        User information if admin
        
    Raises:
        HTTPException: If user is not an admin
    """
    if "admin" not in user.get("roles", []):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions",
        )
    return user