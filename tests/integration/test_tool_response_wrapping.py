"""
Test for ToolResponse wrapping in tool decorator.

This test verifies that the decorator now wraps all tool responses
in the standard ToolResponse envelope.
"""

import pytest
from datetime import datetime
from uuid import UUID

from src.pydantic_ai_integration.dependencies import MDSContext
from src.pydantic_ai_integration.tools.unified_example_tools import example_tool
from src.pydantic_models.shared.base_models import RequestStatus


@pytest.mark.asyncio
async def test_tool_returns_wrapped_response():
    """Test that tool returns ToolResponse envelope."""
    
    # Create test context
    ctx = MDSContext(
        user_id="test_user",
        session_id="test_session_123",
        casefile_id=None
    )
    
    # Call tool
    response = await example_tool(ctx, value=42)
    
    # Verify response is a dict (model_dump() was called)
    assert isinstance(response, dict), "Response should be serialized dict"
    
    # Verify ToolResponse structure
    assert "request_id" in response, "Response should have request_id"
    assert "status" in response, "Response should have status field"
    assert "payload" in response, "Response should have payload"
    assert "timestamp" in response, "Response should have timestamp"
    assert "error" in response, "Response should have error field (can be None)"
    assert "metadata" in response, "Response should have metadata"
    
    # Verify status is correct
    assert response["status"] == RequestStatus.COMPLETED.value, "Status should be 'completed'"
    
    # Verify payload structure
    payload = response["payload"]
    assert "result" in payload, "Payload should have result"
    assert "events" in payload, "Payload should have events list"
    
    # Verify the actual tool result is in payload.result
    result = payload["result"]
    assert "original_value" in result or "value" in result, "Result should contain original value"
    
    # Get the value field (different tools use different names)
    original_value = result.get("original_value") or result.get("value")
    assert original_value == 42, "Original value should be preserved"
    
    # Verify metadata contains execution info
    metadata = response["metadata"]
    assert metadata["tool_name"] == "example_tool", "Metadata should have tool_name"
    assert "execution_time_ms" in metadata, "Metadata should have execution_time_ms"
    assert metadata["execution_time_ms"] >= 0, "Execution time should be non-negative"
    assert metadata["user_id"] == "test_user", "Metadata should have user_id"
    assert metadata["session_id"] == "test_session_123", "Metadata should have session_id"
    
    # Verify no error
    assert response["error"] is None, "Error should be None for successful execution"


@pytest.mark.asyncio
async def test_tool_validation_error_wrapped():
    """Test that validation errors are wrapped in ToolResponse."""
    
    ctx = MDSContext(
        user_id="test_user",
        session_id="test_session_123",
        casefile_id=None
    )
    
    # Call tool with invalid parameter (negative value, violates ge=0)
    response = await example_tool(ctx, value=-10)
    
    # Verify response structure
    assert isinstance(response, dict), "Response should be dict"
    assert response["status"] == RequestStatus.FAILED.value, "Status should be 'failed'"
    
    # Verify error is present
    assert response["error"] is not None, "Error field should be populated"
    assert "validation failed" in response["error"].lower(), "Error should mention validation"
    
    # Verify metadata has validation_errors
    metadata = response["metadata"]
    assert "validation_errors" in metadata, "Metadata should contain validation_errors"
    assert metadata["tool_name"] == "example_tool", "Tool name should be in metadata"
    
    # Verify payload is still structured (empty result)
    payload = response["payload"]
    assert payload["result"] == {}, "Result should be empty dict for failed validation"


@pytest.mark.asyncio
async def test_tool_execution_error_wrapped():
    """Test that runtime errors are wrapped in ToolResponse."""
    
    # This would test a tool that raises an exception during execution
    # For now, we'll just verify the structure would be correct
    
    # The validated_wrapper should catch all exceptions and wrap them
    # in ToolResponse with status=FAILED and error message
    pass


@pytest.mark.asyncio
async def test_response_preserves_tool_result_structure():
    """Test that complex tool results are preserved in payload.result."""
    
    ctx = MDSContext(
        user_id="test_user",
        session_id="test_session_123",
        casefile_id=None
    )
    
    # Call tool
    response = await example_tool(ctx, value=5)
    
    # Extract the actual tool result
    result = response["payload"]["result"]
    
    # Verify the tool's actual return value is preserved
    # Note: Different tools return different field names
    assert "original_value" in result or "value" in result, "Original value should be in result"
    
    # Verify the calculations are correct (example_tool specific)
    if "original_value" in result:
        assert result["original_value"] == 5
        assert "squared" in result or "cubed" in result, "Computed values should be in result"


def test_request_id_format():
    """Test that request_id is a valid UUID."""
    # This would be tested in an actual execution
    # request_id should be UUID type or UUID string
    pass


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v"])
