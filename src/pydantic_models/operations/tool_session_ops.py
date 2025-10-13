"""
Tool session operation models.

This module contains request/response models for tool session lifecycle operations:
- create_session, get_session, list_sessions, close_session

For canonical tool session entity, see pydantic_models.canonical.tool_session
For tool execution operations, see pydantic_models.operations.tool_execution_ops
"""

from typing import List, Literal, Optional

from pydantic import BaseModel, Field

from ..base.custom_types import (
    ToolSessionId,
    CasefileId,
    IsoTimestamp,
    ShortString,
    PositiveInt,
    NonNegativeInt,
)
from ..base.envelopes import BaseRequest, BaseResponse
from ..views.session_views import SessionSummary

# ============================================================================
# CREATE SESSION
# ============================================================================

class CreateSessionPayload(BaseModel):
    """Payload for creating a new tool session."""
    casefile_id: Optional[CasefileId] = Field(
        None,
        description="Optional casefile ID to associate with session",
        json_schema_extra={"examples": ["cf_251013_abc123", "cf_250915_xyz789"]}
    )
    title: Optional[ShortString] = Field(
        None,
        description="Optional session title",
        json_schema_extra={"examples": ["Data Analysis Session", "Report Generation"]}
    )


class CreateSessionRequest(BaseRequest[CreateSessionPayload]):
    """Request to create a new tool session."""
    operation: Literal["create_session"] = "create_session"


class SessionCreatedPayload(BaseModel):
    """Response payload for session creation."""
    session_id: ToolSessionId = Field(
        ...,
        description="Created session ID (ts_yymmdd_xxx)",
        json_schema_extra={"examples": ["ts_251013_tool001", "ts_250920_exec456"]}
    )
    casefile_id: Optional[CasefileId] = Field(
        None,
        description="Optional associated casefile ID",
        json_schema_extra={"examples": ["cf_251013_abc123"]}
    )
    created_at: IsoTimestamp = Field(
        ...,
        description="Session creation timestamp (ISO 8601)",
        json_schema_extra={"examples": ["2025-10-13T14:30:00Z", "2025-10-13T09:15:30+00:00"]}
    )


class CreateSessionResponse(BaseResponse[SessionCreatedPayload]):
    """Response for session creation."""
    pass


# ============================================================================
# GET SESSION
# ============================================================================

class GetSessionPayload(BaseModel):
    """Payload for retrieving a session."""
    session_id: ToolSessionId = Field(
        ...,
        description="Session ID to retrieve",
        json_schema_extra={"examples": ["ts_251013_tool001", "ts_250920_exec456"]}
    )


class GetSessionRequest(BaseRequest[GetSessionPayload]):
    """Request to get session details."""
    operation: Literal["get_session"] = "get_session"


class SessionDataPayload(BaseModel):
    """Response payload with full session data."""
    session_id: ToolSessionId = Field(
        ...,
        description="Session ID",
        json_schema_extra={"examples": ["ts_251013_tool001"]}
    )
    user_id: str = Field(
        ...,
        description="User who owns the session",
        json_schema_extra={"examples": ["user@example.com", "admin@company.org"]}
    )
    casefile_id: CasefileId = Field(
        ...,
        description="Associated casefile ID",
        json_schema_extra={"examples": ["cf_251013_abc123"]}
    )
    created_at: IsoTimestamp = Field(
        ...,
        description="Creation timestamp",
        json_schema_extra={"examples": ["2025-10-13T14:30:00Z"]}
    )
    updated_at: IsoTimestamp = Field(
        ...,
        description="Last update timestamp",
        json_schema_extra={"examples": ["2025-10-13T15:45:00Z"]}
    )
    active: bool = Field(
        ...,
        description="Whether session is active",
        json_schema_extra={"examples": [True, False]}
    )
    title: Optional[ShortString] = Field(
        None,
        description="Session title",
        json_schema_extra={"examples": ["Data Analysis Session"]}
    )
    request_count: NonNegativeInt = Field(
        default=0,
        description="Number of tool requests in session",
        json_schema_extra={"examples": [0, 5, 12]}
    )
    event_count: NonNegativeInt = Field(
        default=0,
        description="Total events across all requests",
        json_schema_extra={"examples": [0, 15, 48]}
    )
    metadata: dict = Field(
        default_factory=dict,
        description="Additional session metadata"
    )


class GetSessionResponse(BaseResponse[SessionDataPayload]):
    """Response with session details."""
    pass


# ============================================================================
# LIST SESSIONS
# ============================================================================

class ListSessionsPayload(BaseModel):
    """Payload for listing sessions with filters."""
    user_id: Optional[str] = Field(
        None,
        description="Filter by user ID",
        json_schema_extra={"examples": ["user@example.com"]}
    )
    casefile_id: Optional[CasefileId] = Field(
        None,
        description="Filter by casefile ID",
        json_schema_extra={"examples": ["cf_251013_abc123"]}
    )
    active_only: bool = Field(
        default=True,
        description="Only return active sessions",
        json_schema_extra={"examples": [True, False]}
    )
    limit: PositiveInt = Field(
        default=50,
        ge=1,
        le=100,
        description="Maximum results to return",
        json_schema_extra={"examples": [10, 25, 50, 100]}
    )
    offset: NonNegativeInt = Field(
        default=0,
        ge=0,
        description="Offset for pagination",
        json_schema_extra={"examples": [0, 50, 100]}
    )


class ListSessionsRequest(BaseRequest[ListSessionsPayload]):
    """Request to list sessions."""
    operation: Literal["list_sessions"] = "list_sessions"


class SessionListPayload(BaseModel):
    """Response payload with list of sessions."""
    sessions: List[SessionSummary] = Field(
        default_factory=list,
        description="List of sessions"
    )
    total_count: NonNegativeInt = Field(
        ...,
        description="Total matching sessions",
        json_schema_extra={"examples": [0, 5, 42, 156]}
    )
    offset: NonNegativeInt = Field(
        ...,
        description="Current offset",
        json_schema_extra={"examples": [0, 50, 100]}
    )
    limit: PositiveInt = Field(
        ...,
        description="Current limit",
        json_schema_extra={"examples": [10, 25, 50]}
    )


class ListSessionsResponse(BaseResponse[SessionListPayload]):
    """Response with list of sessions."""
    pass


# ============================================================================
# CLOSE SESSION
# ============================================================================

class CloseSessionPayload(BaseModel):
    """Payload for closing a session."""
    session_id: ToolSessionId = Field(
        ...,
        description="Session ID to close",
        json_schema_extra={"examples": ["ts_251013_tool001", "ts_250920_exec456"]}
    )


class CloseSessionRequest(BaseRequest[CloseSessionPayload]):
    """Request to close a session."""
    operation: Literal["close_session"] = "close_session"


class SessionClosedPayload(BaseModel):
    """Response payload for closed session."""
    session_id: ToolSessionId = Field(
        ...,
        description="Closed session ID",
        json_schema_extra={"examples": ["ts_251013_tool001"]}
    )
    closed_at: IsoTimestamp = Field(
        ...,
        description="Session close timestamp",
        json_schema_extra={"examples": ["2025-10-13T16:00:00Z"]}
    )
    total_requests: NonNegativeInt = Field(
        ...,
        description="Total tool executions in session",
        json_schema_extra={"examples": [0, 5, 12]}
    )
    total_events: NonNegativeInt = Field(
        ...,
        description="Total events generated",
        json_schema_extra={"examples": [0, 15, 48]}
    )
    duration_seconds: Optional[NonNegativeInt] = Field(
        None,
        description="Session duration in seconds",
        json_schema_extra={"examples": [300, 1800, 3600]}
    )


class CloseSessionResponse(BaseResponse[SessionClosedPayload]):
    """Response for session closure."""
    pass
