"""
Tools package initialization.

Imports unified_example_tools to register tools in MANAGED_TOOLS.
"""

# Import to trigger tool registration via @register_mds_tool decorator
from . import unified_example_tools

# Re-export for convenience
__all__ = ['unified_example_tools']