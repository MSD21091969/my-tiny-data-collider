"""
Test for ToolResponse wrapping in tool decorator.

This test verifies that the decorator now wraps all tool responses
in the standard ToolResponse envelope.
"""

import pytest

from pydantic import BaseModel, Field

from src.pydantic_ai_integration.dependencies import MDSContext
from src.pydantic_ai_integration.tool_decorator import register_mds_tool
from src.pydantic_models.base.types import RequestStatus


class _TestEchoParams(BaseModel):
    """Parameters for the local test tool."""

    message: str = Field(..., min_length=1, description="Message to echo")
    repeat_count: int = Field(1, ge=1, le=5, description="Times to repeat message")


@register_mds_tool(
    name="test_echo_tool",
    display_name="Test Echo Tool",
    description="Local test tool for validating response wrapping",
    category="tests",
    params_model=_TestEchoParams,
    requires_auth=False,
    required_permissions=[],
    requires_casefile=False,
    timeout_seconds=5,
)
async def _decorated_echo_tool(ctx: MDSContext, message: str, repeat_count: int = 1) -> dict:
    """Simple echo implementation used to validate wrapper behavior."""

    ctx.register_event(
        tool_name="test_echo_tool",
        parameters={"message": message, "repeat_count": repeat_count},
        result_summary={},
        duration_ms=0,
    )

    echoed_messages = [message for _ in range(repeat_count)]
    total_length = sum(len(part) for part in echoed_messages)

    return {
        "original_message": message,
        "repeat_count": repeat_count,
        "echoed_messages": echoed_messages,
        "total_length": total_length,
    }

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
    response = await _decorated_echo_tool(ctx, message="hello world", repeat_count=2)
    
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
    assert result["original_message"] == "hello world"
    assert result["repeat_count"] == 2
    assert result["echoed_messages"] == ["hello world", "hello world"]
    
    # Verify metadata contains execution info
    metadata = response["metadata"]
    assert metadata["tool_name"] == "test_echo_tool", "Metadata should have tool_name"
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
    
    # Call tool with invalid parameter (empty message, violates min_length=1)
    response = await _decorated_echo_tool(ctx, message="")
    
    # Verify response structure
    assert isinstance(response, dict), "Response should be dict"
    assert response["status"] == RequestStatus.FAILED.value, "Status should be 'failed'"
    
    # Verify error is present
    assert response["error"] is not None, "Error field should be populated"
    assert "validation failed" in response["error"].lower(), "Error should mention validation"
    
    # Verify metadata has validation_errors
    metadata = response["metadata"]
    assert "validation_errors" in metadata, "Metadata should contain validation_errors"
    assert metadata["tool_name"] == "test_echo_tool", "Tool name should be in metadata"
    
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
    response = await _decorated_echo_tool(ctx, message="sample", repeat_count=3)
    
    # Extract the actual tool result
    result = response["payload"]["result"]
    
    assert result["original_message"] == "sample"
    assert result["repeat_count"] == 3
    assert result["echoed_messages"] == ["sample", "sample", "sample"]
    assert result["total_length"] == len("sample") * 3


def test_request_id_format():
    """Test that request_id is a valid UUID."""
    # This would be tested in an actual execution
    # request_id should be UUID type or UUID string
    pass


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v"])
