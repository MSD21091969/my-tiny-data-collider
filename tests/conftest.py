"""
Pytest configuration and shared fixtures for my-tiny-data-collider tests.
"""
import pytest
import sys
from pathlib import Path


def pytest_configure(config):
    """
    Pytest hook that runs BEFORE test collection.
    This ensures src/ is in sys.path before any test imports happen.
    """
    project_root = Path(__file__).parent.parent
    src_path = project_root / "src"
    src_str = str(src_path)
    
    # Add to sys.path if not already present
    if src_str not in sys.path:
        sys.path.insert(0, src_str)
        print(f"✓ Added {src_str} to sys.path")


# Also set at module level for backwards compatibility
project_root = Path(__file__).parent.parent
src_path = project_root / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))


@pytest.fixture(scope="session")
def project_root():
    """Provide the project root directory."""
    return Path(__file__).parent.parent


@pytest.fixture(scope="session")
def src_path(project_root):
    """Provide the src directory path."""
    return project_root / "src"


@pytest.fixture(scope="session")
def config_path(project_root):
    """Provide the config directory path."""
    return project_root / "config"


@pytest.fixture(scope="session")
def tools_config_path(config_path):
    """Provide the tools config directory path."""
    return config_path / "toolsets"


@pytest.fixture(scope="session")
def methods_yaml_path(config_path):
    """Provide the methods inventory YAML path."""
    return config_path / "methods_inventory_v1.yaml"





# Test environment fixtures for YAML scenario testing
@pytest.fixture
def valid_user_session():
    """Valid user session environment."""
    return {
        "user_id": "test_user_123",
        "session_id": "test_session_456",
        "permissions": ["casefiles:write", "casefiles:read", "casefiles:delete"],
        "session_valid": True,
        "token_valid": True
    }


@pytest.fixture
def read_only_user():
    """Read-only user environment (missing write permission)."""
    return {
        "user_id": "readonly_user_789",
        "session_id": "readonly_session_999",
        "permissions": ["casefiles:read"],  # Missing write permission
        "session_valid": True,
        "token_valid": True
    }


@pytest.fixture
def expired_session_user():
    """Expired session environment."""
    return {
        "user_id": "test_user_123",
        "session_id": "expired_session_000",
        "permissions": ["casefiles:write"],
        "session_valid": False,  # Session expired
        "token_valid": False
    }


@pytest.fixture
def invalid_session_user():
    """Invalid/non-existent session environment."""
    return {
        "user_id": "test_user_123",
        "session_id": "nonexistent_session_xxx",
        "permissions": ["casefiles:write"],
        "session_valid": False,  # Session doesn't exist
        "token_valid": True
    }