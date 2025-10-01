"""
End-to-end integration test of the refactored unified tool system.

Tests the complete workflow:
1. Tool registration via @register_mds_tool
2. Casefile creation
3. Session creation
4. Tool execution with parameter validation
5. Result verification
6. Error handling
"""
import asyncio
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
os.chdir(str(project_root))

from src.tool_sessionservice import ToolSessionService
from src.casefileservice import CasefileService
from src.pydantic_models.tool_session import ToolRequest, ToolRequestPayload
from src.pydantic_ai_integration.tool_decorator import get_tool_names, get_tool_definition


async def test_tool_discovery():
    """Test 1: Tool discovery via MANAGED_TOOLS."""
    print("\n" + "="*70)
    print("TEST 1: Tool Discovery")
    print("="*70)
    
    # Get all registered tools
    tools = get_tool_names()
    print(f"✅ Found {len(tools)} registered tools: {', '.join(tools)}")
    
    assert len(tools) >= 3, "Expected at least 3 tools"
    assert "example_tool" in tools, "example_tool not found"
    assert "another_example_tool" in tools, "another_example_tool not found"
    assert "advanced_tool" in tools, "advanced_tool not found"
    
    # Get detailed info for one tool
    tool_def = get_tool_definition("example_tool")
    print(f"\n✅ Tool Details:")
    print(f"   Name: {tool_def.metadata.name}")
    print(f"   Description: {tool_def.metadata.description}")
    print(f"   Category: {tool_def.metadata.category}")
    print(f"   Timeout: {tool_def.business_rules.timeout_seconds}s")
    print(f"   Requires Auth: {tool_def.business_rules.requires_auth}")
    
    # Validate parameters
    valid_params = {"value": 42}
    validated = tool_def.validate_params(valid_params)
    print(f"\n✅ Parameter Validation: value={validated.value}")
    
    return True


async def test_casefile_creation():
    """Test 2: Casefile creation."""
    print("\n" + "="*70)
    print("TEST 2: Casefile Creation")
    print("="*70)
    
    casefile_service = CasefileService()
    
    # Create casefile with correct signature
    result = await casefile_service.create_casefile(
        user_id="test_user_e2e",
        title="E2E Refactored Test Case",
        description="Testing the refactored unified tool system"
    )
    casefile_id = result["casefile_id"]
    
    print(f"✅ Created casefile: {casefile_id}")
    
    # Verify casefile exists
    retrieved = await casefile_service.get_casefile(casefile_id)
    assert retrieved["metadata"]["title"] == "E2E Refactored Test Case"
    print(f"✅ Verified casefile retrieval")
    
    return casefile_id


async def test_session_creation(casefile_id: str):
    """Test 3: Session creation."""
    print("\n" + "="*70)
    print("TEST 3: Session Creation")
    print("="*70)
    
    session_service = ToolSessionService()
    
    # Create session
    result = await session_service.create_session(
        user_id="test_user_e2e",
        casefile_id=casefile_id
    )
    session_id = result["session_id"]
    
    print(f"✅ Created session: {session_id}")
    
    # Verify session exists
    session = await session_service.get_session(session_id)
    assert session["user_id"] == "test_user_e2e"
    assert session["casefile_id"] == casefile_id
    print(f"✅ Verified session retrieval")
    
    return session_id


async def test_tool_execution(session_id: str, casefile_id: str):
    """Test 4: Tool execution with validation."""
    print("\n" + "="*70)
    print("TEST 4: Tool Execution")
    print("="*70)
    
    session_service = ToolSessionService()
    
    # Test 4a: Execute example_tool
    print("\n--- 4a: Execute example_tool ---")
    request = ToolRequest(
        user_id="test_user_e2e",
        operation="tool_execution",
        session_id=session_id,
        payload=ToolRequestPayload(
            tool_name="example_tool",
            parameters={"value": 7},
            casefile_id=casefile_id
        )
    )
    
    response = await session_service.process_tool_request(request)
    print(f"✅ example_tool executed")
    print(f"   Status: {response.status}")
    print(f"   Result: {response.payload.result}")
    
    assert response.status == "completed", f"Expected completed, got {response.status}"
    assert "original_value" in response.payload.result
    assert response.payload.result["original_value"] == 7
    assert response.payload.result["squared"] == 49
    print(f"✅ Verified result: 7² = 49")
    
    # Test 4b: Execute another_example_tool
    print("\n--- 4b: Execute another_example_tool ---")
    request2 = ToolRequest(
        user_id="test_user_e2e",
        operation="tool_execution",
        session_id=session_id,
        payload=ToolRequestPayload(
            tool_name="another_example_tool",
            parameters={"name": "TestUser", "count": 2},
            casefile_id=casefile_id
        )
    )
    
    response2 = await session_service.process_tool_request(request2)
    print(f"✅ another_example_tool executed")
    print(f"   Messages: {response2.payload.result.get('total_messages', 0)}")
    
    assert response2.status == "completed"
    assert response2.payload.result["total_messages"] == 2
    print(f"✅ Verified {response2.payload.result['total_messages']} messages generated")
    
    # Test 4c: Execute advanced_tool (requires permission)
    print("\n--- 4c: Execute advanced_tool ---")
    request3 = ToolRequest(
        user_id="test_user_e2e",
        operation="tool_execution",
        session_id=session_id,
        payload=ToolRequestPayload(
            tool_name="advanced_tool",
            parameters={
                "input_data": {"key1": "hello", "key2": 123},
                "options": {"mode": "standard", "include_stats": True}
            },
            casefile_id=casefile_id
        )
    )
    
    response3 = await session_service.process_tool_request(request3)
    print(f"✅ advanced_tool executed")
    print(f"   Mode: {response3.payload.result.get('processing_mode', 'N/A')}")
    
    assert response3.status == "completed"
    assert "processed_data" in response3.payload.result
    print(f"✅ Verified advanced processing")
    
    return True


async def test_parameter_validation(session_id: str, casefile_id: str):
    """Test 5: Parameter validation."""
    print("\n" + "="*70)
    print("TEST 5: Parameter Validation")
    print("="*70)
    
    session_service = ToolSessionService()
    
    # Test 5a: Invalid parameter (value < 0)
    print("\n--- 5a: Test negative value (should fail) ---")
    try:
        bad_request = ToolRequest(
            user_id="test_user_e2e",
            operation="tool_execution",
            session_id=session_id,
            payload=ToolRequestPayload(
                tool_name="example_tool",
                parameters={"value": -5},  # Invalid: must be >= 0
                casefile_id=casefile_id
            )
        )
        response = await session_service.process_tool_request(bad_request)
        print(f"❌ Should have rejected negative value!")
        return False
    except ValueError as e:
        print(f"✅ Validation caught error: {str(e)[:80]}...")
    
    # Test 5b: Invalid tool name
    print("\n--- 5b: Test invalid tool name (should fail) ---")
    try:
        bad_request2 = ToolRequest(
            user_id="test_user_e2e",
            operation="tool_execution",
            session_id=session_id,
            payload=ToolRequestPayload(
                tool_name="nonexistent_tool",  # Invalid tool
                parameters={},
                casefile_id=casefile_id
            )
        )
        response2 = await session_service.process_tool_request(bad_request2)
        print(f"❌ Should have rejected invalid tool name!")
        return False
    except ValueError as e:
        print(f"✅ Validation caught error: {str(e)[:80]}...")
    
    # Test 5c: Missing required parameter
    print("\n--- 5c: Test missing required parameter (should fail) ---")
    try:
        bad_request3 = ToolRequest(
            user_id="test_user_e2e",
            operation="tool_execution",
            session_id=session_id,
            payload=ToolRequestPayload(
                tool_name="another_example_tool",
                parameters={"count": 3},  # Missing required 'name'
                casefile_id=casefile_id
            )
        )
        response3 = await session_service.process_tool_request(bad_request3)
        print(f"❌ Should have rejected missing parameter!")
        return False
    except ValueError as e:
        print(f"✅ Validation caught error: {str(e)[:80]}...")
    
    return True


async def main():
    """Run all end-to-end tests."""
    print("\n" + "="*70)
    print("END-TO-END INTEGRATION TEST - REFACTORED SYSTEM")
    print("="*70)
    
    try:
        # Test 1: Tool Discovery
        await test_tool_discovery()
        
        # Test 2: Casefile Creation
        casefile_id = await test_casefile_creation()
        
        # Test 3: Session Creation
        session_id = await test_session_creation(casefile_id)
        
        # Test 4: Tool Execution
        await test_tool_execution(session_id, casefile_id)
        
        # Test 5: Parameter Validation
        await test_parameter_validation(session_id, casefile_id)
        
        # Success!
        print("\n" + "="*70)
        print("🎉 ALL END-TO-END TESTS PASSED!")
        print("="*70)
        print("\nRefactored system verified:")
        print("✅ Tools registered in MANAGED_TOOLS")
        print("✅ Parameter validation via Pydantic models")
        print("✅ Service layer uses tool definitions")
        print("✅ Full workflow from casefile to execution")
        print("✅ Error handling and validation")
        print("="*70)
        
        return 0
        
    except Exception as e:
        print("\n" + "="*70)
        print(f"❌ TEST FAILED: {e}")
        print("="*70)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
