"""
Test script to verify the unified tool registration foundation.

Tests:
1. Tool registration works
2. Can retrieve tool definitions
3. Can access metadata and business rules
4. Parameter validation works
"""
import sys
import os
from pathlib import Path

# Add project root to path (not just src)
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Change to project root so relative imports work
os.chdir(str(project_root))

def test_tool_registration():
    """Test that tools are registered in MANAGED_TOOLS."""
    print("\n" + "="*60)
    print("TEST 1: Tool Registration")
    print("="*60)
    
    from src.pydantic_ai_integration.tool_decorator import get_tool_names
    
    tools = get_tool_names()
    print(f"✅ Registered tools: {tools}")
    print(f"✅ Tool count: {len(tools)}")
    
    expected = ["example_tool", "another_example_tool", "advanced_tool"]
    for tool_name in expected:
        if tool_name in tools:
            print(f"   ✓ {tool_name} found")
        else:
            print(f"   ✗ {tool_name} MISSING")
            return False
    
    return True


def test_tool_retrieval():
    """Test that we can get tool definitions."""
    print("\n" + "="*60)
    print("TEST 2: Tool Definition Retrieval")
    print("="*60)
    
    from src.pydantic_ai_integration.tool_decorator import get_tool_definition
    
    tool = get_tool_definition("example_tool")
    if not tool:
        print("✗ Failed to retrieve example_tool")
        return False
    
    print(f"✅ Tool name: {tool.metadata.name}")
    print(f"✅ Description: {tool.metadata.description}")
    print(f"✅ Category: {tool.metadata.category}")
    print(f"✅ Version: {tool.metadata.version}")
    print(f"✅ Timeout: {tool.business_rules.timeout_seconds}s")
    print(f"✅ Requires auth: {tool.business_rules.requires_auth}")
    print(f"✅ Enabled: {tool.business_rules.enabled}")
    
    return True


def test_parameter_validation():
    """Test parameter validation via Pydantic models."""
    print("\n" + "="*60)
    print("TEST 3: Parameter Validation")
    print("="*60)
    
    from src.pydantic_ai_integration.tools.tool_params import ExampleToolParams
    from pydantic import ValidationError
    
    # Test valid parameters
    try:
        params = ExampleToolParams(value=42)
        print(f"✅ Valid params accepted: value={params.value}")
    except ValidationError as e:
        print(f"✗ Valid params rejected: {e}")
        return False
    
    # Test boundary (should work)
    try:
        params = ExampleToolParams(value=0)
        print(f"✅ Lower boundary accepted: value={params.value}")
    except ValidationError as e:
        print(f"✗ Lower boundary rejected: {e}")
        return False
    
    # Test invalid (should fail)
    try:
        params = ExampleToolParams(value=-1)
        print(f"✗ Invalid params accepted (should have failed): value=-1")
        return False
    except ValidationError as e:
        print(f"✅ Invalid params rejected correctly: value=-1")
        print(f"   Error: {str(e.errors()[0]['msg'])}")
    
    # Test upper boundary (should work)
    try:
        params = ExampleToolParams(value=10000)
        print(f"✅ Upper boundary accepted: value={params.value}")
    except ValidationError as e:
        print(f"✗ Upper boundary rejected: {e}")
        return False
    
    # Test over limit (should fail)
    try:
        params = ExampleToolParams(value=10001)
        print(f"✗ Over-limit params accepted (should have failed): value=10001")
        return False
    except ValidationError as e:
        print(f"✅ Over-limit params rejected correctly: value=10001")
        print(f"   Error: {str(e.errors()[0]['msg'])}")
    
    return True


def test_tool_definition_methods():
    """Test helper methods on ManagedToolDefinition."""
    print("\n" + "="*60)
    print("TEST 4: Tool Definition Helper Methods")
    print("="*60)
    
    from src.pydantic_ai_integration.tool_decorator import get_tool_definition
    
    tool = get_tool_definition("example_tool")
    
    # Test validate_params
    try:
        validated = tool.validate_params({"value": 100})
        print(f"✅ validate_params works: {validated}")
    except Exception as e:
        print(f"✗ validate_params failed: {e}")
        return False
    
    # Test get_openapi_schema
    try:
        schema = tool.get_openapi_schema()
        print(f"✅ get_openapi_schema works")
        print(f"   Properties: {list(schema.get('properties', {}).keys())}")
    except Exception as e:
        print(f"✗ get_openapi_schema failed: {e}")
        return False
    
    # Test check_permission
    try:
        has_permission = tool.check_permission([])
        print(f"✅ check_permission works: {has_permission}")
    except Exception as e:
        print(f"✗ check_permission failed: {e}")
        return False
    
    return True


def main():
    """Run all tests."""
    print("\n" + "="*70)
    print("UNIFIED TOOL REGISTRATION FOUNDATION TEST")
    print("="*70)
    
    tests = [
        test_tool_registration,
        test_tool_retrieval,
        test_parameter_validation,
        test_tool_definition_methods
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"\n✗ Test failed with exception: {e}")
            import traceback
            traceback.print_exc()
            results.append(False)
    
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    passed = sum(results)
    total = len(results)
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! Foundation is solid.")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
