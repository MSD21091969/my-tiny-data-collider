"""Authentication test fixtures for JWT testing.

Provides utilities for:
- Creating valid JWT tokens
- Creating expired JWT tokens  
- Creating malformed JWT tokens
- Testing authentication flows
"""
import pytest
from datetime import datetime, timedelta, UTC
from typing import Dict, Any
from src.authservice.token import create_token, SECRET_KEY, ALGORITHM
import jwt


@pytest.fixture
def valid_jwt_token() -> str:
    """Create a valid JWT token with 1 hour expiry."""
    return create_token(
        user_id="test_user_123",
        username="Test User",
        expires_delta=timedelta(hours=1)
    )


@pytest.fixture
def valid_jwt_headers(valid_jwt_token: str) -> Dict[str, str]:
    """Create valid Authorization headers with JWT token."""
    return {"Authorization": f"Bearer {valid_jwt_token}"}


@pytest.fixture
def expired_jwt_token() -> str:
    """Create an expired JWT token (expired 1 hour ago)."""
    expire = datetime.now(UTC) - timedelta(hours=1)  # Expired 1 hour ago
    
    payload = {
        "sub": "test_user_123",
        "username": "Test User",
        "exp": int(expire.timestamp()),
        "iat": int((datetime.now(UTC) - timedelta(hours=2)).timestamp()),
    }
    
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


@pytest.fixture
def expired_jwt_headers(expired_jwt_token: str) -> Dict[str, str]:
    """Create Authorization headers with expired JWT token."""
    return {"Authorization": f"Bearer {expired_jwt_token}"}


@pytest.fixture
def malformed_jwt_token() -> str:
    """Create a malformed JWT token (invalid signature)."""
    return "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0X3VzZXIiLCJ1c2VybmFtZSI6IlRlc3QifQ.invalid_signature"


@pytest.fixture
def malformed_jwt_headers(malformed_jwt_token: str) -> Dict[str, str]:
    """Create Authorization headers with malformed JWT token."""
    return {"Authorization": f"Bearer {malformed_jwt_token}"}


@pytest.fixture
def missing_auth_headers() -> Dict[str, str]:
    """Return empty headers (no Authorization header)."""
    return {}


@pytest.fixture
def invalid_format_jwt_headers() -> Dict[str, str]:
    """Create Authorization headers with invalid format (not 3 segments)."""
    return {"Authorization": "Bearer not.a.valid.jwt.token"}


@pytest.fixture
def different_user_jwt_token() -> str:
    """Create a valid JWT token for a different user."""
    return create_token(
        user_id="different_user_456",
        username="Different User",
        expires_delta=timedelta(hours=1)
    )


@pytest.fixture
def different_user_jwt_headers(different_user_jwt_token: str) -> Dict[str, str]:
    """Create Authorization headers for a different user."""
    return {"Authorization": f"Bearer {different_user_jwt_token}"}


@pytest.fixture
def admin_jwt_token() -> str:
    """Create a valid JWT token with admin role."""
    # Note: In current implementation, roles are added by get_current_user
    # This is just for testing purposes
    return create_token(
        user_id="admin_user_789",
        username="Admin User",
        expires_delta=timedelta(hours=1)
    )


@pytest.fixture
def admin_jwt_headers(admin_jwt_token: str) -> Dict[str, str]:
    """Create Authorization headers for admin user."""
    return {"Authorization": f"Bearer {admin_jwt_token}"}


@pytest.fixture
def jwt_token_factory():
    """Factory function to create custom JWT tokens for testing.
    
    Usage:
        token = jwt_token_factory(
            user_id="custom_user",
            username="Custom User",
            expires_in_minutes=30
        )
    """
    def _create_token(
        user_id: str = "factory_user",
        username: str = "Factory User",
        expires_in_minutes: int = 60,
        **extra_claims
    ) -> str:
        expire = datetime.now(UTC) + timedelta(minutes=expires_in_minutes)
        
        payload = {
            "sub": user_id,
            "username": username,
            "exp": int(expire.timestamp()),
            "iat": int(datetime.now(UTC).timestamp()),
            **extra_claims
        }
        
        return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    
    return _create_token


@pytest.fixture
def jwt_headers_factory(jwt_token_factory):
    """Factory function to create custom Authorization headers.
    
    Usage:
        headers = jwt_headers_factory(user_id="custom", expires_in_minutes=10)
    """
    def _create_headers(**token_kwargs) -> Dict[str, str]:
        token = jwt_token_factory(**token_kwargs)
        return {"Authorization": f"Bearer {token}"}
    
    return _create_headers


# Helper functions for test assertions
def assert_unauthorized(response, expected_detail: str = None):
    """Assert that response is 401 Unauthorized.
    
    Args:
        response: FastAPI TestClient response
        expected_detail: Optional expected error detail message
    """
    assert response.status_code == 401, f"Expected 401, got {response.status_code}"
    if expected_detail:
        assert expected_detail in response.json().get("detail", "")


def assert_forbidden(response, expected_detail: str = None):
    """Assert that response is 403 Forbidden.
    
    Args:
        response: FastAPI TestClient response
        expected_detail: Optional expected error detail message
    """
    assert response.status_code == 403, f"Expected 403, got {response.status_code}"
    if expected_detail:
        assert expected_detail in response.json().get("detail", "")


def assert_authenticated_success(response):
    """Assert that authenticated request succeeded (200).
    
    Args:
        response: FastAPI TestClient response
    """
    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    assert "request_id" in response.json() or "session_id" in response.json()
