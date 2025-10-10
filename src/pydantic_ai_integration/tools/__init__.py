"""
Tools package initialization.

Imports tools to register them in MANAGED_TOOLS via @register_mds_tool decorator.
"""

# Export MANAGED_TOOLS registry for test helpers and other consumers
from ..tool_decorator import MANAGED_TOOLS  # noqa: F401

__all__ = ["MANAGED_TOOLS"]
