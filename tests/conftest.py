"""
Pytest configuration and fixture registration.

This file makes all fixtures from tests/fixtures/common.py available
to all test files in the project.
"""

# Import all fixtures so pytest can discover them
from tests.fixtures.common import *  # noqa: F401, F403
