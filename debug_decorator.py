"""Debug script to test decorator registration."""

print("=== Decorator Registration Debug ===\n")

# Step 1: Import decorator module
print("1. Importing tool_decorator...")
from src.pydantic_ai_integration.tool_decorator import MANAGED_TOOLS, register_mds_tool, get_tool_names
print(f"   ✓ Imported successfully")
print(f"   Tools before import: {get_tool_names()}")
print()

# Step 2: Import tool parameters
print("2. Importing tool_params...")
from src.pydantic_ai_integration.tools.tool_params import ExampleToolParams
print(f"   ✓ ExampleToolParams imported")
print()

# Step 3: Import enhanced_example_tools (should trigger decorator)
print("3. Importing enhanced_example_tools...")
try:
    from src.pydantic_ai_integration.tools import enhanced_example_tools
    print(f"   ✓ Module imported successfully")
except Exception as e:
    print(f"   ✗ Import failed: {e}")
    import traceback
    traceback.print_exc()
print()

# Step 4: Check registration
print("4. Checking registration...")
print(f"   Tools after import: {get_tool_names()}")
print(f"   Total tools: {len(MANAGED_TOOLS)}")
print()

# Step 5: Inspect module
print("5. Inspecting module contents...")
if hasattr(enhanced_example_tools, 'example_tool'):
    print(f"   ✓ example_tool exists in module")
    print(f"   Function: {enhanced_example_tools.example_tool}")
else:
    print(f"   ✗ example_tool NOT found in module")
print()

# Step 6: Check MANAGED_TOOLS directly
print("6. Checking MANAGED_TOOLS contents...")
for name, tool_def in MANAGED_TOOLS.items():
    print(f"   - {name}: {tool_def.metadata.description}")
print()

if len(MANAGED_TOOLS) == 0:
    print("❌ PROBLEM: No tools registered!")
    print("\nPossible causes:")
    print("  1. Decorator not executing")
    print("  2. Import order issue")
    print("  3. Module not loaded")
else:
    print(f"✅ SUCCESS: {len(MANAGED_TOOLS)} tools registered!")
