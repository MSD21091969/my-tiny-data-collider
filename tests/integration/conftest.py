"""Configuration and fixtures for integration tests.

Integration tests validate the service layer and policy enforcement.
This conftest ensures generated tools are imported and registered.
"""
import pytest
from pathlib import Path
import importlib

# Auto-discover and import all generated tools to register them in MANAGED_TOOLS
# Tools are organized by domain/subdomain matching config/tools/ structure
tools_generated_dir = Path(__file__).parent.parent.parent / "src" / "pydantic_ai_integration" / "tools" / "generated"

def import_tools_recursively(directory: Path, base_module: str = "src.pydantic_ai_integration.tools.generated"):
    """Recursively import all Python tool files."""
    if not directory.exists():
        return
    
    for item in directory.iterdir():
        if item.is_dir() and not item.name.startswith("_"):
            # Recurse into subdirectory
            import_tools_recursively(item, f"{base_module}.{item.name}")
        elif item.is_file() and item.suffix == ".py" and item.stem != "__init__":
            try:
                module_path = f"{base_module}.{item.stem}"
                importlib.import_module(module_path)
            except Exception as e:
                print(f"Warning: Could not import {module_path}: {e}")

import_tools_recursively(tools_generated_dir)

# Make all common fixtures available
from tests.fixtures.common import *  # noqa: F401, F403

