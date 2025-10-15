"""
Session view and projection models.

This module contains lightweight projections and summaries of session entities:
- SessionSummary: Summary of tool sessions
- ChatSessionSummary: Summary of chat sessions

These are used in API responses where full session data is not needed.
"""

from typing import Optional

from pydantic import BaseModel, Field

from ..base.custom_types import CasefileId, IsoTimestamp, NonNegativeInt, SessionId, ShortString


class SessionSummary(BaseModel):
    """Summary of a tool session."""
    session_id: SessionId = Field(..., description="Session ID")
    user_id: str = Field(..., description="User ID")
    casefile_id: CasefileId = Field(..., description="Casefile ID")
    title: Optional[ShortString] = Field(None, description="Session title")
    created_at: IsoTimestamp = Field(..., description="Creation timestamp")
    updated_at: IsoTimestamp = Field(..., description="Last update timestamp")
    active: bool = Field(..., description="Active status")
    request_count: NonNegativeInt = Field(default=0, description="Number of requests")


class ChatSessionSummary(BaseModel):
    """Summary of a chat session."""
    session_id: SessionId = Field(..., description="Session ID")
    user_id: str = Field(..., description="User ID")
    casefile_id: Optional[CasefileId] = Field(None, description="Casefile ID if any")
    created_at: IsoTimestamp = Field(..., description="Creation timestamp")
    updated_at: IsoTimestamp = Field(..., description="Last update timestamp")
    active: bool = Field(..., description="Active status")
    message_count: NonNegativeInt = Field(default=0, description="Number of messages")
