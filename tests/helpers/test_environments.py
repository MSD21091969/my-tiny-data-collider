"""
Test environment fixtures for YAML-driven scenario testing.

Provides standardized test environments that can be referenced in tool YAML configurations.
"""

from typing import Dict, Any, List


# Standard test environments for tool validation
TEST_ENVIRONMENTS = {
    "valid_user_session": {
        "user_id": "test_user_123",
        "session_id": "test_session_456",
        "permissions": ["casefiles:write", "casefiles:read", "casefiles:delete"],
        "session_valid": True,
        "token_valid": True,
        "description": "Valid user with full permissions"
    },

    "read_only_user": {
        "user_id": "readonly_user_789",
        "session_id": "readonly_session_999",
        "permissions": ["casefiles:read"],  # Missing write permission
        "session_valid": True,
        "token_valid": True,
        "description": "User with only read permissions"
    },

    "expired_session_user": {
        "user_id": "test_user_123",
        "session_id": "expired_session_000",
        "permissions": ["casefiles:write"],
        "session_valid": False,  # Session expired
        "token_valid": False,
        "description": "User with expired session/token"
    },

    "invalid_session_user": {
        "user_id": "test_user_123",
        "session_id": "nonexistent_session_xxx",
        "permissions": ["casefiles:write"],
        "session_valid": False,  # Session doesn't exist
        "token_valid": True,
        "description": "User with non-existent session"
    },

    "admin_user": {
        "user_id": "admin_user_999",
        "session_id": "admin_session_111",
        "permissions": ["*"],  # All permissions
        "session_valid": True,
        "token_valid": True,
        "description": "Administrator with all permissions"
    },

    "unauthenticated_user": {
        "user_id": "anon_user_000",
        "session_id": None,
        "permissions": [],
        "session_valid": False,
        "token_valid": False,
        "description": "Unauthenticated user"
    }
}


def get_test_environment(env_name: str) -> Dict[str, Any]:
    """Get a test environment configuration by name.

    Args:
        env_name: Name of the test environment

    Returns:
        Environment configuration dictionary

    Raises:
        ValueError: If environment name is not found
    """
    if env_name not in TEST_ENVIRONMENTS:
        available = list(TEST_ENVIRONMENTS.keys())
        raise ValueError(f"Test environment '{env_name}' not found. Available: {available}")

    return TEST_ENVIRONMENTS[env_name].copy()


def list_test_environments() -> List[str]:
    """List all available test environment names.

    Returns:
        List of environment names
    """
    return list(TEST_ENVIRONMENTS.keys())


def get_environment_description(env_name: str) -> str:
    """Get the description of a test environment.

    Args:
        env_name: Name of the test environment

    Returns:
        Description string
    """
    env = get_test_environment(env_name)
    return env.get("description", "")


def create_custom_environment(
    name: str,
    user_id: str,
    session_id: str = None,
    permissions: List[str] = None,
    session_valid: bool = True,
    token_valid: bool = True,
    description: str = ""
) -> Dict[str, Any]:
    """Create a custom test environment.

    Args:
        name: Environment name (for reference)
        user_id: User ID for the environment
        session_id: Session ID (optional)
        permissions: List of permissions
        session_valid: Whether session is valid
        token_valid: Whether token is valid
        description: Environment description

    Returns:
        Custom environment configuration
    """
    if permissions is None:
        permissions = []

    return {
        "name": name,
        "user_id": user_id,
        "session_id": session_id,
        "permissions": permissions,
        "session_valid": session_valid,
        "token_valid": token_valid,
        "description": description or f"Custom environment: {name}"
    }


# Environment validation helpers
def validate_environment_config(env_config: Dict[str, Any]) -> List[str]:
    """Validate a test environment configuration.

    Args:
        env_config: Environment configuration to validate

    Returns:
        List of validation error messages (empty if valid)
    """
    errors = []

    required_fields = ["user_id", "permissions", "session_valid", "token_valid"]
    for field in required_fields:
        if field not in env_config:
            errors.append(f"Missing required field: {field}")

    if "permissions" in env_config and not isinstance(env_config["permissions"], list):
        errors.append("permissions must be a list")

    return errors


def validate_all_environments() -> List[str]:
    """Validate all predefined test environments.

    Returns:
        List of validation errors (empty if all valid)
    """
    errors = []
    for env_name, env_config in TEST_ENVIRONMENTS.items():
        env_errors = validate_environment_config(env_config)
        for error in env_errors:
            errors.append(f"{env_name}: {error}")

    return errors