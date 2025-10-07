"""
Tools package initialization.

Imports tools to register them in MANAGED_TOOLS via @register_mds_tool decorator.
"""

# Import generated tools dynamically to avoid import errors during generation
# Tools will be imported when app starts, not during tool generation
from .generated import *  # noqa: F401, F403

# Export MANAGED_TOOLS registry for test helpers and other consumers
from ..tool_decorator import MANAGED_TOOLS  # noqa: F401

__all__ = ["MANAGED_TOOLS"]
