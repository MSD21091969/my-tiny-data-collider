"""
Canonical tool session domain models.

This module contains the core tool session entity and related models:
- AuthToken: JWT authentication token structure
- ToolEvent: Record of a tool execution within a session
- ToolSession: The tool session entity (single source of truth)

For tool session operations (create, get, list, close), see pydantic_models.operations.tool_session_ops
For tool execution operations (ToolRequest, ToolResponse), see pydantic_models.operations.tool_execution_ops

NOTE: ToolDefinition, ToolsetDefinition, and ToolParameter have been DEPRECATED.
Use ManagedToolDefinition from pydantic_ai_integration.tool_definition instead.
"""

from pydantic import BaseModel, Field, model_validator
from typing import Dict, Any, List, Optional
from datetime import datetime
from uuid import uuid4


class AuthToken(BaseModel):
    """JWT authentication token structure."""
    user_id: str
    exp: int
    iat: int
    # Add other fields as needed for your JWT structure


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
        from coreservice.id_service import get_id_service
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


class ToolSession(BaseModel):
    """Complete record of a tool session with requests and responses."""
    session_id: str = Field(..., description="Unique session ID (ts_ prefix)")
    user_id: str = Field(..., description="User who created the session")
    casefile_id: Optional[str] = Field(None, description="Associated casefile ID (string format: yymmdd_code)")
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat(), description="Session creation timestamp")
    updated_at: str = Field(default_factory=lambda: datetime.now().isoformat(), description="Last update timestamp")
    request_ids: List[str] = Field(default_factory=list, description="List of request IDs (UUIDs) in this session")
    active: bool = Field(default=True, description="Whether this session is active")
