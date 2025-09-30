"""
Base request and response models for all service operations.
"""

from pydantic import BaseModel, Field, computed_field
from typing import Dict, Any, Generic, TypeVar, Optional
from uuid import UUID, uuid4
from datetime import datetime
from enum import Enum

# Generic type variables for payloads
RequestPayloadT = TypeVar('RequestPayloadT')
ResponsePayloadT = TypeVar('ResponsePayloadT')

class RequestStatus(str, Enum):
    """Status of a request."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class BaseRequest(BaseModel, Generic[RequestPayloadT]):
    """Base model for all requests in the system."""
    request_id: UUID = Field(default_factory=uuid4, description="Unique request identifier")
    session_id: Optional[str] = Field(None, description="Optional session identifier")
    user_id: str = Field(..., description="User making the request")
    operation: str = Field(..., description="Operation being requested")
    payload: RequestPayloadT = Field(..., description="Request payload")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat(), description="Request timestamp")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata for the request")
    
    @computed_field
    def operation_key(self) -> str:
        """Generate a unique operation key."""
        return f"{self.user_id}:{self.operation}:{self.request_id}"

class BaseResponse(BaseModel, Generic[ResponsePayloadT]):
    """Base model for all responses in the system."""
    request_id: UUID = Field(..., description="ID of the originating request")
    status: RequestStatus = Field(..., description="Request processing status")
    payload: ResponsePayloadT = Field(..., description="Response payload")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat(), description="Response timestamp")
    error: Optional[str] = Field(None, description="Error message if status is FAILED")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata for the response")
    
class RequestEnvelope(BaseModel):
    """Envelope for all requests including authentication and context information."""
    request: Dict[str, Any] = Field(..., description="The actual request")
    auth_token: Optional[str] = Field(None, description="Authentication token")
    trace_id: UUID = Field(default_factory=uuid4, description="Unique trace identifier for request tracking")
    client_info: Dict[str, Any] = Field(default_factory=dict, description="Information about the client")