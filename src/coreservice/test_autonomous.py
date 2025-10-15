"""
Autonomous Execution Test Module

This module demonstrates understanding of the R-A-R (Request-Action-Response) pattern
and serves as a verification that the AI assistant can execute autonomously.

Pattern: Request → RequestHub → Service → Response
"""

from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field

from src.pydantic_models.base.envelopes import BaseRequest, BaseResponse
from src.pydantic_models.base.types import RequestStatus


# L1: Payload (business data)
class AutonomousTestPayload(BaseModel):
    """Payload for autonomous execution test."""

    message: str = Field(..., min_length=1, max_length=200, description="Test message")
    timestamp: Optional[str] = Field(default=None, description="Optional timestamp")


# L2: Request (execution envelope)
class AutonomousTestRequest(BaseRequest[AutonomousTestPayload]):
    """Request envelope for autonomous test operation."""

    operation: Literal["autonomous_test"] = "autonomous_test"
    payload: AutonomousTestPayload


# L2: Response payload
class AutonomousTestResultPayload(BaseModel):
    """Result payload for autonomous test response."""

    message: str = Field(..., description="Echo of the input message")
    processed_at: str = Field(..., description="Processing timestamp")
    execution_mode: str = Field(..., description="Execution mode indicator")


# L2: Response (result envelope)
class AutonomousTestResponse(BaseResponse[AutonomousTestResultPayload]):
    """Response envelope for autonomous test operation."""

    pass


async def execute_autonomous_test(
    request: AutonomousTestRequest,
) -> AutonomousTestResponse:
    """
    Execute autonomous test operation.

    This function demonstrates the R-A-R pattern:
    - Receives a BaseRequest with typed payload
    - Processes business logic (echoes message with timestamp)
    - Returns a BaseResponse with typed payload

    Args:
        request: AutonomousTestRequest containing the test message

    Returns:
        AutonomousTestResponse with processed result

    Raises:
        ValueError: If the message is empty
    """
    # Validate input
    if not request.payload.message.strip():
        raise ValueError("Message cannot be empty")

    # Process request (business logic)
    processed_timestamp = request.payload.timestamp or datetime.now().isoformat()

    # Create response payload
    result_payload = AutonomousTestResultPayload(
        message=f"Echo: {request.payload.message}",
        processed_at=processed_timestamp,
        execution_mode="autonomous",
    )

    # Create and return response envelope
    return AutonomousTestResponse(
        request_id=request.request_id,
        status=RequestStatus.COMPLETED,
        payload=result_payload,
    )
