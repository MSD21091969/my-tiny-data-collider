"""
Session management request/response models for tool sessions.

These models handle session lifecycle operations (create, get, list, close).
Tool execution uses ToolRequest/ToolResponse from models.py.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Literal
from datetime import datetime

from ..shared.base_models import BaseRequest, BaseResponse
from .models import ToolSession


# ============================================================================
# CREATE SESSION
# ============================================================================

class CreateSessionPayload(BaseModel):
    """Payload for creating a new tool session."""
    casefile_id: str = Field(..., description="Casefile ID to associate with session")
    title: Optional[str] = Field(None, description="Optional session title")


class CreateSessionRequest(BaseRequest[CreateSessionPayload]):
    """Request to create a new tool session."""
    operation: Literal["create_session"] = "create_session"


class SessionCreatedPayload(BaseModel):
    """Response payload for session creation."""
    session_id: str = Field(..., description="Created session ID (ts_yymmdd_xxx)")
    casefile_id: str = Field(..., description="Associated casefile ID")
    created_at: str = Field(..., description="Session creation timestamp (ISO 8601)")


class CreateSessionResponse(BaseResponse[SessionCreatedPayload]):
    """Response for session creation."""
    pass


# ============================================================================
# GET SESSION
# ============================================================================

class GetSessionPayload(BaseModel):
    """Payload for retrieving a session."""
    session_id: str = Field(..., description="Session ID to retrieve")


class GetSessionRequest(BaseRequest[GetSessionPayload]):
    """Request to get session details."""
    operation: Literal["get_session"] = "get_session"


class SessionDataPayload(BaseModel):
    """Response payload with full session data."""
    session_id: str = Field(..., description="Session ID")
    user_id: str = Field(..., description="User who owns the session")
    casefile_id: str = Field(..., description="Associated casefile ID")
    created_at: str = Field(..., description="Creation timestamp")
    updated_at: str = Field(..., description="Last update timestamp")
    active: bool = Field(..., description="Whether session is active")
    title: Optional[str] = Field(None, description="Session title")
    request_count: int = Field(default=0, description="Number of tool requests in session")
    event_count: int = Field(default=0, description="Total events across all requests")
    metadata: dict = Field(default_factory=dict, description="Additional session metadata")


class GetSessionResponse(BaseResponse[SessionDataPayload]):
    """Response with session details."""
    pass


# ============================================================================
# LIST SESSIONS
# ============================================================================

class ListSessionsPayload(BaseModel):
    """Payload for listing sessions with filters."""
    user_id: Optional[str] = Field(None, description="Filter by user ID")
    casefile_id: Optional[str] = Field(None, description="Filter by casefile ID")
    active_only: bool = Field(default=True, description="Only return active sessions")
    limit: int = Field(default=50, ge=1, le=100, description="Maximum results to return")
    offset: int = Field(default=0, ge=0, description="Offset for pagination")


class ListSessionsRequest(BaseRequest[ListSessionsPayload]):
    """Request to list sessions."""
    operation: Literal["list_sessions"] = "list_sessions"


class SessionSummary(BaseModel):
    """Summary of a tool session."""
    session_id: str = Field(..., description="Session ID")
    user_id: str = Field(..., description="User ID")
    casefile_id: str = Field(..., description="Casefile ID")
    title: Optional[str] = Field(None, description="Session title")
    created_at: str = Field(..., description="Creation timestamp")
    updated_at: str = Field(..., description="Last update timestamp")
    active: bool = Field(..., description="Active status")
    request_count: int = Field(default=0, description="Number of requests")


class SessionListPayload(BaseModel):
    """Response payload with list of sessions."""
    sessions: List[SessionSummary] = Field(default_factory=list, description="List of sessions")
    total_count: int = Field(..., description="Total matching sessions")
    offset: int = Field(..., description="Current offset")
    limit: int = Field(..., description="Current limit")


class ListSessionsResponse(BaseResponse[SessionListPayload]):
    """Response with list of sessions."""
    pass


# ============================================================================
# CLOSE SESSION
# ============================================================================

class CloseSessionPayload(BaseModel):
    """Payload for closing a session."""
    session_id: str = Field(..., description="Session ID to close")


class CloseSessionRequest(BaseRequest[CloseSessionPayload]):
    """Request to close a session."""
    operation: Literal["close_session"] = "close_session"


class SessionClosedPayload(BaseModel):
    """Response payload for closed session."""
    session_id: str = Field(..., description="Closed session ID")
    closed_at: str = Field(..., description="Session close timestamp")
    total_requests: int = Field(..., description="Total tool executions in session")
    total_events: int = Field(..., description="Total events generated")
    duration_seconds: Optional[int] = Field(None, description="Session duration in seconds")


class CloseSessionResponse(BaseResponse[SessionClosedPayload]):
    """Response for session closure."""
    pass
