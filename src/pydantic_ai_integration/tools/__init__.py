"""
Tools package initialization.

Imports tools to register them in MANAGED_TOOLS via @register_mds_tool decorator.
"""

# Import generated tools dynamically to avoid import errors during generation
# Tools will be imported when app starts, not during tool generation

__all__ = []
