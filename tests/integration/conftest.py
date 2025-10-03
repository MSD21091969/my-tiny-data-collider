"""Configuration and fixtures for integration tests.

Integration tests validate the service layer and policy enforcement.
This conftest ensures generated tools are imported and registered.
"""
import pytest

# Import generated tools to ensure they're registered in MANAGED_TOOLS
from src.pydantic_ai_integration.tools.generated import echo_tool  # noqa: F401


# Make all common fixtures available
from tests.fixtures.common import *  # noqa: F401, F403
