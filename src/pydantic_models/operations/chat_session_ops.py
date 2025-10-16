"""
Chat session operation models.

This module contains request/response models for chat session lifecycle operations:
- create_chat_session, get_chat_session, list_chat_sessions, close_chat_session

For canonical chat session entity, see pydantic_models.canonical.chat_session
For chat message operations, see pydantic_models.operations.tool_execution_ops
"""

from typing import List, Literal, Optional

from pydantic import BaseModel, Field

from ..base.custom_types import (
    ChatSessionId,
    CasefileId,
    IsoTimestamp,
    ShortString,
    PositiveInt,
    NonNegativeInt,
    ToolSessionId,
    UserId,
)
from ..base.envelopes import BaseRequest, BaseResponse
from ..views.session_views import ChatSessionSummary

# ============================================================================
# CREATE CHAT SESSION
# ============================================================================

class CreateChatSessionPayload(BaseModel):
    """Payload for creating a new chat session."""
    casefile_id: Optional[CasefileId] = Field(
        None,
        description="Optional casefile ID to associate",
        json_schema_extra={"examples": ["cf_251013_abc123", "cf_250915_xyz789"]}
    )
    title: Optional[ShortString] = Field(
        None,
        description="Optional session title",
        json_schema_extra={"examples": ["Customer Support Chat", "Legal Consultation"]}
    )


class CreateChatSessionRequest(BaseRequest[CreateChatSessionPayload]):
    """Request to create a new chat session."""
    operation: Literal["create_chat_session"] = "create_chat_session"


class ChatSessionCreatedPayload(BaseModel):
    """Response payload for chat session creation."""
    session_id: ChatSessionId = Field(
        ...,
        description="Created session ID (cs_yymmdd_xxx)",
        json_schema_extra={"examples": ["cs_251013_chat001", "cs_250920_conv456"]}
    )
    tool_session_id: Optional[ToolSessionId] = Field(
        None,
        description="Linked tool session ID (created lazily)",
        json_schema_extra={"examples": ["ts_251013_tool001", None]}
    )
    casefile_id: Optional[CasefileId] = Field(
        None,
        description="Associated casefile ID if any",
        json_schema_extra={"examples": ["cf_251013_abc123"]}
    )
    created_at: IsoTimestamp = Field(
        ...,
        description="Session creation timestamp (ISO 8601)",
        json_schema_extra={"examples": ["2025-10-13T14:30:00Z", "2025-10-13T09:15:30+00:00"]}
    )


class CreateChatSessionResponse(BaseResponse[ChatSessionCreatedPayload]):
    """Response for chat session creation."""
    pass


# ============================================================================
# GET CHAT SESSION
# ============================================================================

class GetChatSessionPayload(BaseModel):
    """Payload for retrieving a chat session."""
    session_id: ChatSessionId = Field(
        ...,
        description="Session ID to retrieve",
        json_schema_extra={"examples": ["cs_251013_chat001", "cs_250920_conv456"]}
    )
    include_messages: bool = Field(
        default=False,
        description="Include full message history",
        json_schema_extra={"examples": [True, False]}
    )


class GetChatSessionRequest(BaseRequest[GetChatSessionPayload]):
    """Request to get chat session details."""
    operation: Literal["get_chat_session"] = "get_chat_session"


class ChatSessionDataPayload(BaseModel):
    """Response payload with full chat session data."""
    session_id: ChatSessionId = Field(
        ...,
        description="Session ID",
        json_schema_extra={"examples": ["cs_251013_chat001"]}
    )
    user_id: UserId = Field(
        ...,
        description="User who owns the session",
        json_schema_extra={"examples": ["user@example.com", "admin@company.org"]}
    )
    casefile_id: Optional[CasefileId] = Field(
        None,
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
    message_count: NonNegativeInt = Field(
        default=0,
        description="Number of messages in session",
        json_schema_extra={"examples": [0, 15, 42]}
    )
    event_count: NonNegativeInt = Field(
        default=0,
        description="Total events in session",
        json_schema_extra={"examples": [0, 8, 23]}
    )
    messages: List[dict] = Field(
        default_factory=list,
        description="Message history if requested"
    )
    metadata: dict = Field(
        default_factory=dict,
        description="Additional session metadata"
    )


class GetChatSessionResponse(BaseResponse[ChatSessionDataPayload]):
    """Response with chat session details."""
    pass


# ============================================================================
# LIST CHAT SESSIONS
# ============================================================================

class ListChatSessionsPayload(BaseModel):
    """Payload for listing chat sessions with filters."""
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


class ListChatSessionsRequest(BaseRequest[ListChatSessionsPayload]):
    """Request to list chat sessions."""
    operation: Literal["list_chat_sessions"] = "list_chat_sessions"


class ChatSessionListPayload(BaseModel):
    """Response payload with list of chat sessions."""
    sessions: List[ChatSessionSummary] = Field(
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


class ListChatSessionsResponse(BaseResponse[ChatSessionListPayload]):
    """Response with list of chat sessions."""
    pass


# ============================================================================
# CLOSE CHAT SESSION
# ============================================================================

class CloseChatSessionPayload(BaseModel):
    """Payload for closing a chat session."""
    session_id: ChatSessionId = Field(
        ...,
        description="Session ID to close",
        json_schema_extra={"examples": ["cs_251013_chat001", "cs_250920_conv456"]}
    )


class CloseChatSessionRequest(BaseRequest[CloseChatSessionPayload]):
    """Request to close a chat session."""
    operation: Literal["close_chat_session"] = "close_chat_session"


class ChatSessionClosedPayload(BaseModel):
    """Response payload for closed chat session."""
    session_id: ChatSessionId = Field(
        ...,
        description="Closed session ID",
        json_schema_extra={"examples": ["cs_251013_chat001"]}
    )
    closed_at: IsoTimestamp = Field(
        ...,
        description="Session close timestamp",
        json_schema_extra={"examples": ["2025-10-13T16:00:00Z"]}
    )
    total_messages: NonNegativeInt = Field(
        ...,
        description="Total messages in session",
        json_schema_extra={"examples": [0, 15, 42]}
    )
    total_events: NonNegativeInt = Field(
        ...,
        description="Total events generated",
        json_schema_extra={"examples": [0, 8, 23]}
    )
    duration_seconds: Optional[NonNegativeInt] = Field(
        None,
        description="Session duration in seconds",
        json_schema_extra={"examples": [300, 1800, 3600]}
    )
    tool_session_id: Optional[ToolSessionId] = Field(
        None,
        description="Linked tool session ID if any",
        json_schema_extra={"examples": ["ts_251013_tool001", None]}
    )
    tool_session_closed: bool = Field(
        default=False,
        description="Whether linked tool session was also closed",
        json_schema_extra={"examples": [True, False]}
    )


class CloseChatSessionResponse(BaseResponse[ChatSessionClosedPayload]):
    """Response for chat session closure."""
    pass
