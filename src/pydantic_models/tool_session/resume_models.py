"""
Pydantic models for session resumption.
"""

from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional, Union
from uuid import UUID
from datetime import datetime

class SessionResumeRequest(BaseModel):
    """Request to resume a previous session."""
    session_id: str = Field(..., description="ID of the session to resume")
    
class SessionResumeResponse(BaseModel):
    """Response when resuming a session."""
    session_id: str = Field(..., description="ID of the resumed session")
    last_request_id: Optional[str] = Field(None, description="ID of the last request in the session")
    last_response_id: Optional[str] = Field(None, description="ID of the last response in the session") 
    updated_at: str = Field(..., description="Timestamp when the session was last updated")
    request_count: int = Field(..., description="Number of requests in the session")
    context_summary: Dict[str, Any] = Field(default_factory=dict, description="Summary of the session context")