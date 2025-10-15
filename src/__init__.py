"""
MDS Objects - Core initialization and package structure
"""

__version__ = "0.1.0"

# Phase 10: Decorator-based auto-registration
# Import service modules to trigger @register_service_method decorators
# This replaces YAML-based registration with decorator-based registration

# Service imports (triggers decorators)
from . import casefileservice  # noqa: F401
from . import tool_sessionservice  # noqa: F401
from . import communicationservice  # noqa: F401
from .coreservice import request_hub  # noqa: F401
from .pydantic_ai_integration.integrations import google_workspace  # noqa: F401

# YAML loading kept optional for documentation/verification
# from .pydantic_ai_integration.method_decorator import register_methods_from_yaml
# register_methods_from_yaml("config/methods_inventory_v1.yaml")  # Optional: verify decorator count matches YAML