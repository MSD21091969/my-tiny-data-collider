#!/usr/bin/env python3
"""
Test script to check if decorators are working.
"""

import sys
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

print("Importing service modules...")
try:
    import casefileservice.service
    print("✓ casefileservice imported")
except ImportError as e:
    print(f"❌ Failed to import casefileservice: {e}")

try:
    import communicationservice.service
    print("✓ communicationservice imported")
except ImportError as e:
    print(f"❌ Failed to import communicationservice: {e}")

try:
    import tool_sessionservice.service
    print("✓ tool_sessionservice imported")
except ImportError as e:
    print(f"❌ Failed to import tool_sessionservice: {e}")

print("\nChecking MANAGED_METHODS...")
from pydantic_ai_integration.method_registry import MANAGED_METHODS
print(f"MANAGED_METHODS has {len(MANAGED_METHODS)} methods")
if MANAGED_METHODS:
    print("All methods:", sorted(MANAGED_METHODS.keys()))
else:
    print("No methods found")

print("\nChecking registry instance...")
print(f"MANAGED_METHODS id: {id(MANAGED_METHODS)}")
print(f"MANAGED_METHODS type: {type(MANAGED_METHODS)}")