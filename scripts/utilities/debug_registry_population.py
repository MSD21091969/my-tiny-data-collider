#!/usr/bin/env python3
"""
Minimal registry debug script: import all service modules and print MANAGED_METHODS.
Usage:
    python scripts/utilities/debug_registry_population.py
"""
import os
os.environ["SKIP_AUTO_INIT"] = "true"  # Disable auto-init to avoid YAML loading

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Import all service modules FIRST (triggers decorators)
print("[DEBUG] Importing casefileservice...")
import src.casefileservice.service
print(f"[DEBUG] After casefileservice import")

print("[DEBUG] Importing communicationservice...")
import src.communicationservice.service
print(f"[DEBUG] After communicationservice import")

print("[DEBUG] Importing tool_sessionservice...")
import src.tool_sessionservice.service
print(f"[DEBUG] After tool_sessionservice import")

# Import MANAGED_METHODS directly from method_registry module (bypass __init__.py)
import importlib
method_registry_module = importlib.import_module('src.pydantic_ai_integration.method_registry')
MANAGED_METHODS = method_registry_module.MANAGED_METHODS

# Also check if there's a global tracking variable
print(f"[DEBUG] Checking for global registry tracking...")
try:
    # Check if decorators created any global tracking
    import src.pydantic_ai_integration.method_decorator as decorator_module
    print(f"[DEBUG] Decorator module globals: {[k for k in decorator_module.__dict__.keys() if 'registry' in k.lower() or 'managed' in k.lower()]}")
    
    # Check the decorator's MANAGED_METHODS
    decorator_managed_methods = getattr(decorator_module, 'MANAGED_METHODS', None)
    if decorator_managed_methods is not None:
        print(f"[DEBUG] Decorator MANAGED_METHODS id: {id(decorator_managed_methods)}")
        print(f"[DEBUG] Decorator MANAGED_METHODS count: {len(decorator_managed_methods)}")
        print(f"[DEBUG] Decorator MANAGED_METHODS contents: {list(decorator_managed_methods.keys())[:5]}...")
    else:
        print(f"[DEBUG] No MANAGED_METHODS in decorator module")
        
except Exception as e:
    print(f"[DEBUG] Error checking decorator module: {e}")

print(f"[DEBUG] My MANAGED_METHODS id after all imports: {id(MANAGED_METHODS)}")
print(f"[DEBUG] My MANAGED_METHODS module: {MANAGED_METHODS.__class__.__module__}")

def main():
    print("[DEBUG] MANAGED_METHODS registry contents:")
    for k, v in MANAGED_METHODS.items():
        print(f"- {k}: {v}")
    print(f"Total methods registered: {len(MANAGED_METHODS)}")

if __name__ == "__main__":
    main()
