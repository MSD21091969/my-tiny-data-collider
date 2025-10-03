"""
Pytest configuration and fixture registration.

This file makes all fixtures from tests/fixtures/common.py and
tests/fixtures/auth_fixtures.py available to all test files in the project.
"""

# Import all fixtures so pytest can discover them
from tests.fixtures.common import *  # noqa: F401, F403
from tests.fixtures.auth_fixtures import *  # noqa: F401, F403
