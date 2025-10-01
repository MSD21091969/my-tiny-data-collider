"""
Models for chat sessions and messages.
"""

from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional, Literal
from datetime import datetime
from enum import Enum

from ..shared.base_models import BaseRequest, BaseResponse

# Chat message payload types
class MessageType(str, Enum):
    """Types of chat messages."""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
    TOOL = "tool"
    ERROR = "error"

class ChatMessagePayload(BaseModel):
    """Payload for a chat message."""
    content: str = Field(..., description="Message content")
    message_type: MessageType = Field(..., description="Type of message")
    tool_calls: List[Dict[str, Any]] = Field(default_factory=list, description="Tool calls in this message")
    session_request_id: Optional[str] = Field(None, description="Client-provided session request ID")
    casefile_id: Optional[str] = Field(None, description="Associated casefile ID")

class ChatResponsePayload(BaseModel):
    """Payload for a chat response."""
    message: ChatMessagePayload
    related_messages: List[ChatMessagePayload] = Field(default_factory=list, description="Related messages")
    events: List[Dict[str, Any]] = Field(default_factory=list, description="Events generated during processing")

# Concrete chat request and response models
class ChatRequest(BaseRequest[ChatMessagePayload]):
    """Request to send a chat message."""
    operation: Literal["chat_message"] = "chat_message"

class ChatResponse(BaseResponse[ChatResponsePayload]):
    """Response to a chat message."""
    session_request_id: Optional[str] = Field(None, description="Session request ID")

class ChatSession(BaseModel):
    """Complete record of a chat session with messages."""
    session_id: str = Field(..., description="Unique session ID (cs_yymmdd_*)")
    user_id: str = Field(..., description="User who created the session")
    casefile_id: Optional[str] = Field(None, description="Associated casefile if any (cf_yymmdd_code)")
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat(), description="Session creation timestamp")
    updated_at: str = Field(default_factory=lambda: datetime.now().isoformat(), description="Last update timestamp")
    messages: List[Dict[str, Any]] = Field(default_factory=list, description="Messages in chronological order")
    message_index: Dict[str, int] = Field(default_factory=dict, description="Index to map message IDs to positions")
    request_index: Dict[str, List[str]] = Field(default_factory=dict, description="Index to map session request IDs to message IDs")
    events: List[Dict[str, Any]] = Field(default_factory=list, description="Chronological list of all events in the session")
    active: bool = Field(default=True, description="Whether this session is active")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional metadata for this session")