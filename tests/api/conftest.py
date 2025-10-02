"""Configuration and fixtures for API tests.

API tests validate the HTTP layer, JWT authentication, and end-to-end flow.
This conftest ensures generated tools are imported and registered.
"""
import pytest

# Import generated tools to ensure they're registered in MANAGED_TOOLS
from src.pydantic_ai_integration.tools.generated import echo_tool  # noqa: F401


# Make all common fixtures available
from tests.fixtures.common import *  # noqa: F401, F403
