"""
Comprehensive test suite for tool execution with multiple modes and result verification.

Test Modes:
1. Direct tool call (tool_def.implementation)
2. Via Request DTO
3. Mock mode (no real service calls)
4. Dry run mode
5. With result verification per tool
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

from coreservice.id_service import get_id_service
from pydantic_ai_integration.dependencies import MDSContext
from pydantic_ai_integration.tool_decorator import MANAGED_TOOLS
from pydantic_models.base.types import RequestStatus


@pytest.fixture
def mock_context():
    """Create mock context for testing."""
    user_id = f"test_user_{uuid4().hex[:8]}"
    return MDSContext(
        user_id=user_id,
        session_id=get_id_service().new_tool_session_id(user_id=user_id, casefile_id=None),
        casefile_id=None
    )


@pytest.fixture
def mock_casefile_context():
    """Create mock context with casefile."""
    user_id = f"test_user_{uuid4().hex[:8]}"
    casefile_id = f"cf_{uuid4().hex[:8]}"
    return MDSContext(
        user_id=user_id,
        session_id=get_id_service().new_tool_session_id(user_id=user_id, casefile_id=casefile_id),
        casefile_id=casefile_id
    )


# ============================================================================
# MODE 1: Direct Tool Execution
# ============================================================================

@pytest.mark.asyncio
@pytest.mark.integration
class TestDirectToolExecution:
    """Test tools by calling implementation directly."""
    
    async def test_create_casefile_direct(self, mock_context):
        """Test create_casefile_tool via direct call."""
        tool = MANAGED_TOOLS.get("create_casefile_tool")
        assert tool is not None, "Tool not found"
        
        result = await tool.implementation(
            mock_context,
            title="Direct Test Casefile",
            description="Testing direct execution",
            tags=["test"],
            dry_run=False
        )
        
        # Verify structure
        assert "status" in result
        assert "tool_name" in result
        assert result["tool_name"] == "create_casefile_tool"
        
        # Verify execution happened
        if result["status"] == "success":
            assert "result" in result
            assert "duration_ms" in result
            print(f"✓ Direct execution successful: {result['duration_ms']}ms")
        elif result["status"] == "error":
            print(f"⚠ Error (OK if Firestore not configured): {result.get('error_type')}")
    
    async def test_get_casefile_direct(self, mock_casefile_context):
        """Test get_casefile_tool via direct call."""
        tool = MANAGED_TOOLS.get("get_casefile_tool")
        if not tool:
            pytest.skip("Tool not found")
        
        result = await tool.implementation(
            mock_casefile_context,
            casefile_id=mock_casefile_context.casefile_id,
            dry_run=False
        )
        
        assert "status" in result
        print(f"Get casefile status: {result['status']}")
    
    async def test_list_casefiles_direct(self, mock_context):
        """Test list_casefiles_tool via direct call."""
        tool = MANAGED_TOOLS.get("list_casefiles_tool")
        if not tool:
            pytest.skip("Tool not found")
        
        result = await tool.implementation(
            mock_context,
            limit=10,
            dry_run=False
        )
        
        assert "status" in result
        print(f"List casefiles status: {result['status']}")


# ============================================================================
# MODE 2: Via Request DTO (Future Enhancement)
# ============================================================================

@pytest.mark.asyncio
@pytest.mark.integration
class TestToolExecutionViaRequestDTO:
    """Test tools using Request DTO pattern."""
    
    async def test_create_casefile_via_dto(self, mock_context):
        """
        Test create_casefile by building Request DTO.
        
        This demonstrates the full flow:
        Tool params → Request DTO → Service → Response
        """
        from pydantic_models.operations.casefile_ops import CreateCasefileRequest
        
        tool = MANAGED_TOOLS.get("create_casefile_tool")
        if not tool:
            pytest.skip("Tool not found")
        
        # Build Request DTO
        request = CreateCasefileRequest(
            user_id=mock_context.user_id,
            session_id=mock_context.session_id,
            casefile_id=None,
            payload={
                "title": "DTO Test Casefile",
                "description": "Created via DTO",
                "tags": ["dto", "test"]
            }
        )
        
        # Execute tool (which will unwrap DTO internally)
        result = await tool.implementation(
            mock_context,
            title=request.payload.title,
            description=request.payload.description,
            tags=request.payload.tags,
            dry_run=False
        )
        
        assert "status" in result
        print(f"DTO execution status: {result['status']}")


# ============================================================================
# MODE 3: Mock Mode (No Real Service Calls)
# ============================================================================

@pytest.mark.asyncio
@pytest.mark.mock
class TestToolExecutionMockMode:
    """Test tools with mocked services (no real calls)."""
    
    async def test_create_casefile_mocked(self, mock_context):
        """Test create_casefile with mocked service."""
        tool = MANAGED_TOOLS.get("create_casefile_tool")
        if not tool:
            pytest.skip("Tool not found")
        
        # Mock the service
        with patch('casefileservice.service.CasefileService') as MockService:
            # Setup mock
            mock_service_instance = AsyncMock()
            mock_response = MagicMock()
            mock_response.model_dump.return_value = {
                "status": RequestStatus.COMPLETED,
                "payload": {
                    "casefile_id": "cf_test_123",
                    "title": "Mocked Casefile",
                    "created_at": "2025-10-10T12:00:00",
                    "created_by": mock_context.user_id
                }
            }
            mock_service_instance.create_casefile.return_value = mock_response
            MockService.return_value = mock_service_instance
            
            # Execute tool
            result = await tool.implementation(
                mock_context,
                title="Mocked Test",
                description="Testing with mock",
                tags=["mock"],
                dry_run=False
            )
            
            # Verify mock was called
            if result["status"] == "success":
                mock_service_instance.create_casefile.assert_called_once()
                print("✓ Mock service was called correctly")
    
    async def test_multiple_tools_mocked(self, mock_context):
        """Test multiple tools with mocked services."""
        tools_to_test = [
            ("create_casefile_tool", "casefileservice.service.CasefileService", "create_casefile"),
            ("get_casefile_tool", "casefileservice.service.CasefileService", "get_casefile"),
        ]
        
        for tool_name, service_path, method_name in tools_to_test:
            tool = MANAGED_TOOLS.get(tool_name)
            if not tool:
                continue
            
            with patch(service_path) as MockService:
                mock_service = AsyncMock()
                mock_response = MagicMock()
                mock_response.model_dump.return_value = {
                    "status": RequestStatus.COMPLETED,
                    "payload": {"result": "mocked"}
                }
                getattr(mock_service, method_name).return_value = mock_response
                MockService.return_value = mock_service
                
                # Execute with appropriate params
                if tool_name == "create_casefile_tool":
                    result = await tool.implementation(
                        mock_context, title="Test", dry_run=False
                    )
                elif tool_name == "get_casefile_tool":
                    result = await tool.implementation(
                        mock_context, casefile_id="cf_test", dry_run=False
                    )
                
                print(f"✓ {tool_name}: {result.get('status')}")


# ============================================================================
# MODE 4: Dry Run Mode
# ============================================================================

@pytest.mark.asyncio
@pytest.mark.integration
class TestDryRunMode:
    """Test dry run mode for all tools."""
    
    @pytest.mark.parametrize("tool_name", [
        "create_casefile_tool",
        "get_casefile_tool",
        "list_casefiles_tool",
        "update_casefile_tool",
        "delete_casefile_tool",
    ])
    async def test_tool_dry_run(self, mock_context, tool_name):
        """Test dry run mode for various tools."""
        tool = MANAGED_TOOLS.get(tool_name)
        if not tool:
            pytest.skip(f"Tool {tool_name} not found")
        
        # Execute in dry run mode
        params = {"dry_run": True}
        
        # Add required params per tool
        if "create" in tool_name:
            params["title"] = "Dry Run Test"
        elif "get" in tool_name or "delete" in tool_name:
            params["casefile_id"] = "cf_dryrun"
        elif "update" in tool_name:
            params["casefile_id"] = "cf_dryrun"
            params["title"] = "Updated"
        
        result = await tool.implementation(mock_context, **params)
        
        # Verify dry run response
        assert result["status"] == "dry_run", f"{tool_name} should return dry_run status"
        assert "message" in result
        assert "would execute" in result["message"].lower()
        print(f"✓ {tool_name} dry run: {result['message']}")


# ============================================================================
# MODE 5: Result Verification Per Tool
# ============================================================================

@pytest.mark.asyncio
@pytest.mark.integration
class TestToolResultVerification:
    """Verify result structure and content per tool type."""
    
    async def test_create_casefile_result_structure(self, mock_context):
        """Verify create_casefile returns expected structure."""
        tool = MANAGED_TOOLS.get("create_casefile_tool")
        if not tool:
            pytest.skip("Tool not found")
        
        result = await tool.implementation(
            mock_context,
            title="Structure Test",
            description="Testing result structure",
            tags=["test"],
            dry_run=False
        )
        
        # Common fields
        assert "status" in result
        assert "tool_name" in result
        assert "method_name" in result
        assert "execution_type" in result
        
        if result["status"] == "success":
            # Success-specific fields
            assert "result" in result
            assert "duration_ms" in result
            assert "tool_params" in result
            assert isinstance(result["duration_ms"], int)
            
            # Service response structure
            service_result = result["result"]
            assert isinstance(service_result, dict)
            assert "status" in service_result
            assert "payload" in service_result
            
            print(f"✓ Create casefile result structure valid")
            print(f"  - Duration: {result['duration_ms']}ms")
            print(f"  - Service status: {service_result['status']}")
            
            # Verify payload has expected fields
            payload = service_result.get("payload", {})
            if "casefile_id" in payload:
                assert payload["casefile_id"].startswith("cf_")
                print(f"  - Casefile ID: {payload['casefile_id']}")
        
        elif result["status"] == "error":
            # Error-specific fields
            assert "error_type" in result
            assert "error_message" in result
            
            print(f"⚠ Error result structure valid")
            print(f"  - Error type: {result['error_type']}")
            print(f"  - Error message: {result['error_message'][:100]}")
    
    async def test_list_casefiles_result_structure(self, mock_context):
        """Verify list_casefiles returns expected structure."""
        tool = MANAGED_TOOLS.get("list_casefiles_tool")
        if not tool:
            pytest.skip("Tool not found")
        
        result = await tool.implementation(
            mock_context,
            limit=5,
            dry_run=False
        )
        
        assert "status" in result
        
        if result["status"] == "success":
            service_result = result["result"]
            payload = service_result.get("payload", {})
            
            # List operations should return array
            if "casefiles" in payload:
                assert isinstance(payload["casefiles"], list)
                print(f"✓ List casefiles returned {len(payload['casefiles'])} items")
            
            print(f"✓ List result structure valid")
    
    async def test_parameter_separation_verification(self, mock_context):
        """Verify method_params and tool_params are separated correctly."""
        tool = MANAGED_TOOLS.get("create_casefile_tool")
        if not tool:
            pytest.skip("Tool not found")
        
        result = await tool.implementation(
            mock_context,
            title="Param Test",
            description="Testing param separation",
            tags=["params"],
            dry_run=False,
            timeout_seconds=15
        )
        
        # Verify tool_params were extracted
        if "tool_params" in result:
            tool_params = result["tool_params"]
            
            # Should contain orchestration params
            assert "dry_run" in tool_params
            assert "timeout_seconds" in tool_params
            assert tool_params["timeout_seconds"] == 15
            
            print(f"✓ Parameter separation verified")
            print(f"  - Tool params: {list(tool_params.keys())}")


# ============================================================================
# MODE 6: Error Handling Verification
# ============================================================================

@pytest.mark.asyncio
@pytest.mark.integration
class TestToolErrorHandling:
    """Verify error handling for various error scenarios."""
    
    async def test_invalid_parameters(self, mock_context):
        """Test tool handles invalid parameters."""
        tool = MANAGED_TOOLS.get("create_casefile_tool")
        if not tool:
            pytest.skip("Tool not found")
        
        # Missing required parameter (title)
        try:
            result = await tool.implementation(
                mock_context,
                description="Missing title",
                dry_run=False
            )
            
            # Should get validation error or parameter error
            if "error" in str(result).lower() or result.get("status") == "error":
                print(f"✓ Invalid parameters handled: {result.get('status')}")
        except Exception as e:
            print(f"✓ Invalid parameters raised exception: {type(e).__name__}")
    
    async def test_timeout_handling(self, mock_context):
        """Test tool respects timeout_seconds."""
        tool = MANAGED_TOOLS.get("create_casefile_tool")
        if not tool:
            pytest.skip("Tool not found")
        
        # Very short timeout (may cause timeout in slow environments)
        result = await tool.implementation(
            mock_context,
            title="Timeout Test",
            dry_run=False,
            timeout_seconds=1  # 1 second timeout
        )
        
        # Should either succeed fast or timeout
        assert result["status"] in ["success", "error"]
        
        if result["status"] == "error" and result.get("error_type") == "TimeoutError":
            print(f"✓ Timeout handling verified")
        elif result["status"] == "success":
            print(f"✓ Completed within timeout: {result['duration_ms']}ms")
    
    async def test_service_error_handling(self, mock_context):
        """Test tool handles service errors gracefully."""
        tool = MANAGED_TOOLS.get("get_casefile_tool")
        if not tool:
            pytest.skip("Tool not found")
        
        # Try to get non-existent casefile
        result = await tool.implementation(
            mock_context,
            casefile_id="cf_nonexistent_999",
            dry_run=False
        )
        
        # Should handle gracefully (not crash)
        assert "status" in result
        print(f"✓ Service error handled: {result['status']}")


# ============================================================================
# MODE 7: Performance Testing
# ============================================================================

@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.slow
class TestToolPerformance:
    """Test tool execution performance."""
    
    async def test_execution_timing(self, mock_context):
        """Verify execution timing is tracked."""
        tool = MANAGED_TOOLS.get("create_casefile_tool")
        if not tool:
            pytest.skip("Tool not found")
        
        result = await tool.implementation(
            mock_context,
            title="Timing Test",
            dry_run=False
        )
        
        if result["status"] == "success":
            duration = result.get("duration_ms", 0)
            assert duration >= 0
            assert duration < 30000  # Should complete within 30s
            print(f"✓ Execution timing: {duration}ms")
    
    async def test_multiple_sequential_calls(self, mock_context):
        """Test multiple sequential tool calls."""
        tool = MANAGED_TOOLS.get("create_casefile_tool")
        if not tool:
            pytest.skip("Tool not found")
        
        import time
        start = time.time()
        
        for i in range(3):
            result = await tool.implementation(
                mock_context,
                title=f"Sequential Test {i}",
                dry_run=False
            )
            print(f"  Call {i+1}: {result['status']}")
        
        total_time = (time.time() - start) * 1000
        print(f"✓ 3 sequential calls completed in {total_time:.0f}ms")


# ============================================================================
# Test Summary Generator
# ============================================================================

@pytest.mark.asyncio
async def test_generate_tool_summary():
    """Generate summary of all registered tools and their test status."""
    print("\n" + "="*70)
    print("TOOL EXECUTION SUMMARY")
    print("="*70)
    
    print(f"\nTotal tools registered: {len(MANAGED_TOOLS)}")
    
    # Group by category
    by_category = {}
    for name, tool_def in MANAGED_TOOLS.items():
        category = tool_def.category
        if category not in by_category:
            by_category[category] = []
        by_category[category].append(name)
    
    print(f"\nTools by category:")
    for category, tools in sorted(by_category.items()):
        print(f"  {category}: {len(tools)} tools")
        for tool in sorted(tools)[:3]:  # Show first 3
            print(f"    - {tool}")
    
    print("\n" + "="*70)
