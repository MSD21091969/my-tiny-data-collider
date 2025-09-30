"""
Models for tool sessions, requests and responses.
"""

from pydantic import BaseModel, Field, computed_field
from typing import Dict, Any, List, Optional, Union, Literal
from datetime import datetime

from ..shared.base_models import BaseRequest, BaseResponse, RequestStatus

class ToolParameter(BaseModel):
    """Represents a parameter for a tool with validation rules."""
    name: str = Field(..., description="Parameter name")
    type: str = Field(..., description="Parameter type (string, int, etc.)")
    description: str = Field(..., description="Parameter description")
    required: bool = Field(default=True, description="Whether this parameter is required")
    default: Optional[Any] = Field(None, description="Default value if not specified")
    enum_values: Optional[List[str]] = Field(None, description="Enum values if applicable")

class ToolDefinition(BaseModel):
    """Definition of a tool with its parameters and documentation."""
    name: str = Field(..., description="Tool name")
    description: str = Field(..., description="Tool description")
    parameters: List[ToolParameter] = Field(default_factory=list, description="Tool parameters")
    returns: str = Field(..., description="Description of what the tool returns")
    example: Optional[str] = Field(None, description="Example usage")
    category: str = Field(default="general", description="Tool category")

class ToolsetDefinition(BaseModel):
    """A collection of tools forming a toolset."""
    name: str = Field(..., description="Toolset name")
    description: str = Field(..., description="Toolset description")
    tools: List[ToolDefinition] = Field(..., description="Tools in this toolset")
    category: str = Field(default="general", description="Toolset category")

# Tool request specific payload
class ToolRequestPayload(BaseModel):
    """Payload for a tool execution request."""
    tool_name: str = Field(..., description="Name of the tool to execute")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Parameters for the tool")
    prompt: Optional[str] = Field(None, description="Optional prompt for AI-assisted tool execution")
    casefile_id: Optional[str] = Field(None, description="Optional casefile context")
    session_request_id: Optional[str] = Field(None, description="Client-provided session request ID for tracking")

# Tool response specific payload
class ToolResponsePayload(BaseModel):
    """Payload for a tool execution response."""
    result: Dict[str, Any] = Field(..., description="Result of the tool execution")
    events: List[Dict[str, Any]] = Field(default_factory=list, description="Events generated during execution")
    session_request_id: Optional[str] = Field(None, description="Client-provided session request ID for tracking")
    
# Concrete tool request and response models
class ToolRequest(BaseRequest[ToolRequestPayload]):
    """Request to execute a tool."""
    operation: Literal["tool_execution"] = "tool_execution"
    
    @computed_field
    def has_casefile_context(self) -> bool:
        """Whether this request has casefile context."""
        return self.payload.casefile_id is not None

class ToolResponse(BaseResponse[ToolResponsePayload]):
    """Response from a tool execution."""
    

# Authentication models for JWT handling
class AuthToken(BaseModel):
    """JWT authentication token structure."""
    user_id: str
    exp: int
    iat: int
    # Add other fields as needed for your JWT structure


class ToolSession(BaseModel):
    """Complete record of a tool session with requests and responses."""
    session_id: str = Field(..., description="Unique session ID (ts_ prefix)")
    user_id: str = Field(..., description="User who created the session")
    casefile_id: Optional[str] = Field(None, description="Associated casefile ID (string format: yymmdd_code)")
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat(), description="Session creation timestamp")
    updated_at: str = Field(default_factory=lambda: datetime.now().isoformat(), description="Last update timestamp")
    requests: Dict[str, ToolRequest] = Field(default_factory=dict, description="Map of request IDs to requests")
    responses: Dict[str, ToolResponse] = Field(default_factory=dict, description="Map of request IDs to responses")
    request_index: Dict[str, List[str]] = Field(default_factory=dict, description="Index to map session request IDs to request IDs")
    events: List[Dict[str, Any]] = Field(default_factory=list, description="Chronological list of all events in the session")
    active: bool = Field(default=True, description="Whether this session is active")