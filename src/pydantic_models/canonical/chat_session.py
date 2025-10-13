"""
Canonical chat session domain models.

This module contains the core chat session entity and related types:
- MessageType: Enumeration of message types
- ChatSession: The chat session entity (single source of truth)

For chat session operations (create, get, list, close), see pydantic_models.operations.chat_session_ops
For chat message operations (ChatRequest, ChatResponse), see pydantic_models.operations.tool_execution_ops
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, model_validator

from ..base.custom_types import ChatSessionId, CasefileId, IsoTimestamp


class MessageType(str, Enum):
    """Types of chat messages."""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
    TOOL = "tool"
    ERROR = "error"


class ChatSession(BaseModel):
    """Complete record of a chat session with messages."""
    session_id: ChatSessionId = Field(
        ...,
        description="Unique session ID (cs_ prefix)",
        json_schema_extra={"example": "cs_abc123xyz"}
    )
    user_id: str = Field(
        ...,
        description="User who created the session",
        json_schema_extra={"example": "user@example.com"}
    )
    casefile_id: Optional[CasefileId] = Field(
        None,
        description="Associated casefile if any",
        json_schema_extra={"example": "cf_251013_abc123"}
    )
    created_at: IsoTimestamp = Field(
        default_factory=lambda: datetime.now().isoformat(),
        description="Session creation timestamp (ISO 8601)",
        json_schema_extra={"example": "2025-10-13T12:00:00"}
    )
    updated_at: IsoTimestamp = Field(
        default_factory=lambda: datetime.now().isoformat(),
        description="Last update timestamp (ISO 8601)",
        json_schema_extra={"example": "2025-10-13T12:30:00"}
    )
    messages: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Messages in chronological order"
    )
    message_index: Dict[str, int] = Field(
        default_factory=dict,
        description="Index to map message IDs to positions"
    )
    request_index: Dict[str, List[str]] = Field(
        default_factory=dict,
        description="Index to map session request IDs to message IDs"
    )
    events: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Chronological list of all events in the session"
    )
    active: bool = Field(
        default=True,
        description="Whether this session is active"
    )
    metadata: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Additional metadata for this session"
    )
    
    @model_validator(mode='after')
    def validate_timestamp_order(self) -> 'ChatSession':
        """Ensure created_at <= updated_at."""
        try:
            created = datetime.fromisoformat(self.created_at.replace('Z', '+00:00'))
            updated = datetime.fromisoformat(self.updated_at.replace('Z', '+00:00'))
            if created > updated:
                raise ValueError("created_at must be <= updated_at")
        except (ValueError, AttributeError) as e:
            if "created_at must be <=" not in str(e):
                pass  # Let custom type validators handle format errors
            else:
                raise
        return self
