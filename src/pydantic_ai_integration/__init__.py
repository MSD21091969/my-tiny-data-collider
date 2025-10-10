"""
Basic initialization for the Pydantic AI integration module.

Imports tools subpackage to trigger @register_mds_tool decorator execution,
which populates the MANAGED_TOOLS registry.
"""

__version__ = "0.1.0"

# Import tools to trigger registration
# This ensures all @register_mds_tool decorated functions get registered
from . import tools  # noqa: F401

# Load methods from YAML inventory to populate MANAGED_METHODS registry
# This enables ToolFactory to inherit method DTOs for tool generation
from .method_decorator import register_methods_from_yaml  # noqa: F401

try:
    register_methods_from_yaml()
except Exception as e:
    # Log but don't fail - methods can still be registered via decorators
    import logging
    logger = logging.getLogger(__name__)
    logger.warning(f"Failed to load methods from YAML: {e}")