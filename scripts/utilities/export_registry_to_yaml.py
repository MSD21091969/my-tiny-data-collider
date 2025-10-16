#!/usr/bin/env python3
"""
Export the live MANAGED_METHODS registry to YAML.
- Imports all service modules explicitly to trigger decorator registration.
- Prints MANAGED_METHODS contents for debugging.
- Exports to config/methods_inventory_v1.yaml

Usage:
    python scripts/utilities/export_registry_to_yaml.py
"""
import sys
import os
from pathlib import Path
import yaml

# Ensure project root is in sys.path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# CRITICAL: Import MANAGED_METHODS AFTER service imports
# The decorators populate the registry during service module imports
# We need to import MANAGED_METHODS after that happens

# Ensure project root is in sys.path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Explicitly import all service modules to trigger decorator registration
print("Loading service modules to populate registry...")
import src.casefileservice.service
import src.communicationservice.service
import src.tool_sessionservice.service
print("Service modules loaded.")

# NOW import MANAGED_METHODS - this should get the populated instance
# Use the SAME import path as the decorators: from pydantic_ai_integration.method_registry import MANAGED_METHODS
from pydantic_ai_integration.method_registry import MANAGED_METHODS as REGISTRY

def main():
    print(f"[DEBUG] Final registry count: {len(REGISTRY)}")
    print("[DEBUG] MANAGED_METHODS registry contents:")
    for k, v in REGISTRY.items():
        print(f"- {k}: {v}")
    print(f"Total methods registered: {len(REGISTRY)}")

    # Export to YAML, handling None for model classes
    output_path = project_root / "config" / "methods_inventory_v1.yaml"
    yaml_dict = {}
    for k, v in REGISTRY.items():
        try:
            d = v.to_yaml_compatible()
        except AttributeError as e:
            # Patch for NoneType model classes
            d = {
                "name": v.name,
                "description": v.description,
                "version": v.version,
                "classification": v.get_classification(),
                "models": {
                    "request": getattr(v.request_model_class, "__name__", "null"),
                    "response": getattr(v.response_model_class, "__name__", "null")
                },
                "implementation": {
                    "class": v.implementation_class,
                    "method": v.implementation_method
                }
            }
            print(f"[WARN] Method '{k}' has missing model class: {e}")
        yaml_dict[k] = d
    with open(output_path, "w", encoding="utf-8") as f:
        yaml.dump(yaml_dict, f, sort_keys=False, allow_unicode=True)
    print(f"[INFO] Exported registry to {output_path}")

if __name__ == "__main__":
    main()
