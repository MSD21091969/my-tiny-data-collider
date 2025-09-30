"""
Core configuration functions and settings.
"""

import os
from typing import Dict, Any

def get_environment() -> str:
    """Get the current environment name."""
    return os.environ.get("ENVIRONMENT", "development")

def get_use_mocks() -> bool:
    """Get whether to use mock implementations."""
    env_value = os.environ.get("USE_MOCKS", "").lower()
    if env_value == "true":
        return True
    elif env_value == "false":
        return False
    else:
        # Default based on environment
        return get_environment() != "production"

def get_config() -> Dict[str, Any]:
    """Get the full configuration."""
    return {
        "environment": get_environment(),
        "use_mocks": get_use_mocks(),
        "project_id": os.environ.get("GOOGLE_CLOUD_PROJECT", ""),
        "enable_mock_gmail": os.environ.get("ENABLE_MOCK_GMAIL", "true").lower() == "true",
        "enable_mock_drive": os.environ.get("ENABLE_MOCK_DRIVE", "true").lower() == "true",
    }