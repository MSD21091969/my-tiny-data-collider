"""
Models for tool sessions, requests and responses.
"""

from pydantic import BaseModel, Field, computed_field, model_validator
from typing import Dict, Any, List, Optional, Union, Literal
from datetime import datetime
from uuid import uuid4

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

class ToolEvent(BaseModel):
    """Record of a tool execution within a session."""
    event_id: str = Field(default_factory=lambda: ToolEvent._get_id_service_static().new_tool_event_id())
    event_type: str = Field(..., description="Type of event: tool_request_received, tool_execution_started, tool_execution_completed, tool_execution_failed, tool_response_sent")
    tool_name: str
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    parameters: Dict[str, Any] = Field(default_factory=dict)
    result_summary: Optional[Dict[str, Any]] = None
    duration_ms: Optional[int] = None
    status: Optional[str] = Field(None, description="Event status: success, error, pending")
    error_message: Optional[str] = Field(None, description="Error message if status is error")
    
    # Enhanced tracking for agent integration
    initiator: str = Field(default="user", description="Who/what initiated this tool execution")
    chain_position: Optional[int] = None
    chain_id: Optional[str] = Field(default_factory=lambda: str(uuid4()), description="Unique identifier for a chain of tool executions")
    reasoning: Optional[str] = None
    source_message_id: Optional[str] = None
    related_events: List[str] = Field(default_factory=list)
    
    @model_validator(mode='after')
    def ensure_serializable(self) -> 'ToolEvent':
        """Ensure all fields are JSON serializable for storage."""
        # Convert any non-serializable values in parameters
        self.parameters = self._ensure_serializable_dict(self.parameters)
        
        # Convert any non-serializable values in result_summary
        if self.result_summary:
            self.result_summary = self._ensure_serializable_dict(self.result_summary)
            
        return self
    
    @staticmethod
    def _get_id_service_static():
        """Get ID service (avoid circular import)."""
        from ...coreservice.id_service import get_id_service
        return get_id_service()
    
    def _ensure_serializable_dict(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Recursively ensure dictionary is JSON serializable."""
        if not isinstance(data, dict):
            return data
            
        result = {}
        for k, v in data.items():
            if isinstance(v, dict):
                result[k] = self._ensure_serializable_dict(v)
            elif isinstance(v, list):
                result[k] = [self._ensure_serializable_dict(item) if isinstance(item, dict) else item for item in v]
            elif hasattr(v, 'model_dump'):
                # Handle Pydantic models
                result[k] = v.model_dump()
            elif isinstance(v, (str, int, float, bool, type(None))):
                # Basic types are fine
                result[k] = v
            else:
                # Convert anything else to string
                try:
                    result[k] = str(v)
                except:
                    result[k] = f"<non-serializable-{type(v).__name__}>"
        
        return result
        
    def to_storage_format(self) -> Dict[str, Any]:
        """Convert to a format suitable for database storage."""
        return self.model_dump(mode='json')

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
    event_ids: List[str] = Field(default_factory=list, description="List of event IDs generated by this request")
    
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
    request_ids: List[str] = Field(default_factory=list, description="List of request IDs (UUIDs) in this session")
    active: bool = Field(default=True, description="Whether this session is active")