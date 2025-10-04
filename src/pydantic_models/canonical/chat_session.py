"""
Canonical chat session domain models.

This module contains the core chat session entity and related types:
- MessageType: Enumeration of message types
- ChatSession: The chat session entity (single source of truth)

For chat session operations (create, get, list, close), see pydantic_models.operations.chat_session_ops
For chat message operations (ChatRequest, ChatResponse), see pydantic_models.operations.tool_execution_ops
"""

from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum


class MessageType(str, Enum):
    """Types of chat messages."""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
    TOOL = "tool"
    ERROR = "error"


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
