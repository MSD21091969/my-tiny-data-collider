"""
Test suite for autonomous execution verification.

Tests the autonomous_test function to verify:
1. Proper R-A-R pattern implementation
2. Type hints and Pydantic validation
3. Business logic execution
4. Error handling
"""

import pytest
from pydantic import ValidationError

from coreservice.test_autonomous import (
    AutonomousTestPayload,
    AutonomousTestRequest,
    AutonomousTestResponse,
    AutonomousTestResultPayload,
    execute_autonomous_test,
)
from src.pydantic_models.base.types import RequestStatus


class TestAutonomousExecution:
    """Test suite for autonomous execution verification."""

    @pytest.mark.asyncio
    async def test_execute_autonomous_test_success(self):
        """Test successful execution of autonomous test operation."""
        # Arrange
        test_message = "Hello from AI autonomous execution!"
        request = AutonomousTestRequest(
            user_id="test_user_123",
            operation="autonomous_test",
            payload=AutonomousTestPayload(message=test_message),
        )

        # Act
        response = await execute_autonomous_test(request)

        # Assert
        assert isinstance(response, AutonomousTestResponse)
        assert response.status == RequestStatus.COMPLETED
        assert response.request_id == request.request_id
        assert response.payload.message == f"Echo: {test_message}"
        assert response.payload.execution_mode == "autonomous"
        assert response.payload.processed_at is not None

    @pytest.mark.asyncio
    async def test_execute_autonomous_test_with_custom_timestamp(self):
        """Test execution with custom timestamp."""
        # Arrange
        custom_timestamp = "2025-10-10T12:00:00"
        request = AutonomousTestRequest(
            user_id="test_user_123",
            operation="autonomous_test",
            payload=AutonomousTestPayload(
                message="Test with timestamp", timestamp=custom_timestamp
            ),
        )

        # Act
        response = await execute_autonomous_test(request)

        # Assert
        assert response.status == RequestStatus.COMPLETED
        assert response.payload.processed_at == custom_timestamp

    @pytest.mark.asyncio
    async def test_execute_autonomous_test_empty_message_fails(self):
        """Test that empty message raises ValueError."""
        # Arrange
        request = AutonomousTestRequest(
            user_id="test_user_123",
            operation="autonomous_test",
            payload=AutonomousTestPayload(message="   "),  # Empty/whitespace
        )

        # Act & Assert
        with pytest.raises(ValueError, match="Message cannot be empty"):
            await execute_autonomous_test(request)

    def test_payload_validation_fails_for_invalid_message(self):
        """Test that Pydantic validation fails for invalid message."""
        # Act & Assert - message too long
        with pytest.raises(ValidationError) as exc_info:
            AutonomousTestPayload(message="a" * 201)  # Exceeds max_length=200

        assert "String should have at most 200 characters" in str(exc_info.value)

        # Act & Assert - message empty
        with pytest.raises(ValidationError) as exc_info:
            AutonomousTestPayload(message="")  # Below min_length=1

        assert "String should have at least 1 character" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_response_payload_structure(self):
        """Test that response payload has correct structure."""
        # Arrange
        request = AutonomousTestRequest(
            user_id="test_user_123",
            operation="autonomous_test",
            payload=AutonomousTestPayload(message="Structure test"),
        )

        # Act
        response = await execute_autonomous_test(request)

        # Assert
        payload = response.payload
        assert hasattr(payload, "message")
        assert hasattr(payload, "processed_at")
        assert hasattr(payload, "execution_mode")
        assert isinstance(payload, AutonomousTestResultPayload)

    @pytest.mark.asyncio
    async def test_request_id_propagation(self):
        """Test that request_id is properly propagated to response."""
        # Arrange
        request = AutonomousTestRequest(
            user_id="test_user_123",
            operation="autonomous_test",
            payload=AutonomousTestPayload(message="Request ID test"),
        )
        original_request_id = request.request_id

        # Act
        response = await execute_autonomous_test(request)

        # Assert
        assert response.request_id == original_request_id

    @pytest.mark.asyncio
    async def test_multiple_executions_independent(self):
        """Test that multiple executions are independent."""
        # Arrange
        request1 = AutonomousTestRequest(
            user_id="user_1",
            operation="autonomous_test",
            payload=AutonomousTestPayload(message="First message"),
        )
        request2 = AutonomousTestRequest(
            user_id="user_2",
            operation="autonomous_test",
            payload=AutonomousTestPayload(message="Second message"),
        )

        # Act
        response1 = await execute_autonomous_test(request1)
        response2 = await execute_autonomous_test(request2)

        # Assert
        assert response1.request_id != response2.request_id
        assert response1.payload.message != response2.payload.message
        assert "First message" in response1.payload.message
        assert "Second message" in response2.payload.message
