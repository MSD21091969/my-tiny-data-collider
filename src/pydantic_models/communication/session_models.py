"""
Session management request/response models for chat sessions.

These models handle chat session lifecycle operations (create, get, close).
Chat messages use ChatRequest/ChatResponse from models.py.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Literal

from ..shared.base_models import BaseRequest, BaseResponse


# ============================================================================
# CREATE CHAT SESSION
# ============================================================================

class CreateChatSessionPayload(BaseModel):
    """Payload for creating a new chat session."""
    casefile_id: Optional[str] = Field(None, description="Optional casefile ID to associate")
    title: Optional[str] = Field(None, description="Optional session title")


class CreateChatSessionRequest(BaseRequest[CreateChatSessionPayload]):
    """Request to create a new chat session."""
    operation: Literal["create_chat_session"] = "create_chat_session"


class ChatSessionCreatedPayload(BaseModel):
    """Response payload for chat session creation."""
    session_id: str = Field(..., description="Created session ID (cs_yymmdd_xxx)")
    casefile_id: Optional[str] = Field(None, description="Associated casefile ID if any")
    created_at: str = Field(..., description="Session creation timestamp (ISO 8601)")


class CreateChatSessionResponse(BaseResponse[ChatSessionCreatedPayload]):
    """Response for chat session creation."""
    pass


# ============================================================================
# GET CHAT SESSION
# ============================================================================

class GetChatSessionPayload(BaseModel):
    """Payload for retrieving a chat session."""
    session_id: str = Field(..., description="Session ID to retrieve")
    include_messages: bool = Field(default=False, description="Include full message history")


class GetChatSessionRequest(BaseRequest[GetChatSessionPayload]):
    """Request to get chat session details."""
    operation: Literal["get_chat_session"] = "get_chat_session"


class ChatSessionDataPayload(BaseModel):
    """Response payload with full chat session data."""
    session_id: str = Field(..., description="Session ID")
    user_id: str = Field(..., description="User who owns the session")
    casefile_id: Optional[str] = Field(None, description="Associated casefile ID")
    created_at: str = Field(..., description="Creation timestamp")
    updated_at: str = Field(..., description="Last update timestamp")
    active: bool = Field(..., description="Whether session is active")
    message_count: int = Field(default=0, description="Number of messages in session")
    event_count: int = Field(default=0, description="Total events in session")
    messages: List[dict] = Field(default_factory=list, description="Message history if requested")
    metadata: dict = Field(default_factory=dict, description="Additional session metadata")


class GetChatSessionResponse(BaseResponse[ChatSessionDataPayload]):
    """Response with chat session details."""
    pass


# ============================================================================
# LIST CHAT SESSIONS
# ============================================================================

class ListChatSessionsPayload(BaseModel):
    """Payload for listing chat sessions with filters."""
    user_id: Optional[str] = Field(None, description="Filter by user ID")
    casefile_id: Optional[str] = Field(None, description="Filter by casefile ID")
    active_only: bool = Field(default=True, description="Only return active sessions")
    limit: int = Field(default=50, ge=1, le=100, description="Maximum results to return")
    offset: int = Field(default=0, ge=0, description="Offset for pagination")


class ListChatSessionsRequest(BaseRequest[ListChatSessionsPayload]):
    """Request to list chat sessions."""
    operation: Literal["list_chat_sessions"] = "list_chat_sessions"


class ChatSessionSummary(BaseModel):
    """Summary of a chat session."""
    session_id: str = Field(..., description="Session ID")
    user_id: str = Field(..., description="User ID")
    casefile_id: Optional[str] = Field(None, description="Casefile ID if any")
    created_at: str = Field(..., description="Creation timestamp")
    updated_at: str = Field(..., description="Last update timestamp")
    active: bool = Field(..., description="Active status")
    message_count: int = Field(default=0, description="Number of messages")


class ChatSessionListPayload(BaseModel):
    """Response payload with list of chat sessions."""
    sessions: List[ChatSessionSummary] = Field(default_factory=list, description="List of sessions")
    total_count: int = Field(..., description="Total matching sessions")
    offset: int = Field(..., description="Current offset")
    limit: int = Field(..., description="Current limit")


class ListChatSessionsResponse(BaseResponse[ChatSessionListPayload]):
    """Response with list of chat sessions."""
    pass


# ============================================================================
# CLOSE CHAT SESSION
# ============================================================================

class CloseChatSessionPayload(BaseModel):
    """Payload for closing a chat session."""
    session_id: str = Field(..., description="Session ID to close")


class CloseChatSessionRequest(BaseRequest[CloseChatSessionPayload]):
    """Request to close a chat session."""
    operation: Literal["close_chat_session"] = "close_chat_session"


class ChatSessionClosedPayload(BaseModel):
    """Response payload for closed chat session."""
    session_id: str = Field(..., description="Closed session ID")
    closed_at: str = Field(..., description="Session close timestamp")
    total_messages: int = Field(..., description="Total messages in session")
    total_events: int = Field(..., description="Total events generated")
    duration_seconds: Optional[int] = Field(None, description="Session duration in seconds")


class CloseChatSessionResponse(BaseResponse[ChatSessionClosedPayload]):
    """Response for chat session closure."""
    pass
