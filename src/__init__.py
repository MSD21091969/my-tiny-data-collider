"""
MDS Objects - Core initialization and package structure
"""

__version__ = "0.1.0"

# Activate MANAGED_METHODS registry on import
from .pydantic_ai_integration.method_decorator import register_methods_from_yaml

# Load all 26 methods from YAML into registry
register_methods_from_yaml("config/methods_inventory_v1.yaml")