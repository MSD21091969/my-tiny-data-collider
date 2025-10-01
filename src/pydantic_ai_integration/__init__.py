"""
Basic initialization for the Pydantic AI integration module.

Imports tools subpackage to trigger @register_mds_tool decorator execution,
which populates the MANAGED_TOOLS registry.
"""

__version__ = "0.1.0"

# Import tools to trigger registration
# This ensures all @register_mds_tool decorated functions get registered
from . import tools  # noqa: F401