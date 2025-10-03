"""
Tools package initialization.

Imports tools to register them in MANAGED_TOOLS via @register_mds_tool decorator.
"""

# Import example tools (moved to examples subfolder)
from .examples import unified_example_tools

# Import generated tools (YAML-based tools)
from . import generated

# Re-export for convenience
__all__ = ['unified_example_tools', 'generated']
