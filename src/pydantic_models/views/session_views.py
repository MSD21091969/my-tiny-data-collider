"""
Session view and projection models.

This module contains lightweight projections and summaries of session entities:
- SessionSummary: Summary of tool sessions
- ChatSessionSummary: Summary of chat sessions

These are used in API responses where full session data is not needed.
"""

from pydantic import BaseModel, Field
from typing import Optional


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


class ChatSessionSummary(BaseModel):
    """Summary of a chat session."""
    session_id: str = Field(..., description="Session ID")
    user_id: str = Field(..., description="User ID")
    casefile_id: Optional[str] = Field(None, description="Casefile ID if any")
    created_at: str = Field(..., description="Creation timestamp")
    updated_at: str = Field(..., description="Last update timestamp")
    active: bool = Field(..., description="Active status")
    message_count: int = Field(default=0, description="Number of messages")
