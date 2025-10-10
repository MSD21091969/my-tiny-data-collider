"""
Core configuration functions and settings.
"""

import os
from typing import Any, Dict


def get_environment() -> str:
    """Get the current environment name."""
    return os.environ.get("ENVIRONMENT", "development")

def get_config() -> Dict[str, Any]:
    """Get the full configuration."""
    return {
        "environment": get_environment(),
        "project_id": os.environ.get("GOOGLE_CLOUD_PROJECT", ""),
        "enable_mock_gmail": os.environ.get("ENABLE_MOCK_GMAIL", "true").lower() == "true",
        "enable_mock_drive": os.environ.get("ENABLE_MOCK_DRIVE", "true").lower() == "true",
    }