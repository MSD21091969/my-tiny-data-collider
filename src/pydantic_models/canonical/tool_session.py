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

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import uuid4

from pydantic import BaseModel, Field, model_validator

from ..base.custom_types import ToolSessionId, CasefileId, IsoTimestamp, PositiveInt, NonNegativeInt


class AuthToken(BaseModel):
    """JWT authentication token structure."""
    user_id: str = Field(
        ...,
        description="User ID from JWT",
        json_schema_extra={"example": "user@example.com"}
    )
    exp: PositiveInt = Field(
        ...,
        description="Expiration timestamp (Unix epoch)",
        json_schema_extra={"example": 1728835200}
    )
    iat: PositiveInt = Field(
        ...,
        description="Issued at timestamp (Unix epoch)",
        json_schema_extra={"example": 1728748800}
    )
    # Add other fields as needed for your JWT structure


class ToolEvent(BaseModel):
    """Record of a tool execution within a session."""
    event_id: str = Field(
        default_factory=lambda: ToolEvent._get_id_service_static().new_tool_event_id(),
        json_schema_extra={"example": "evt_abc123"}
    )
    event_type: str = Field(
        ...,
        description="Type of event: tool_request_received, tool_execution_started, tool_execution_completed, tool_execution_failed, tool_response_sent",
        json_schema_extra={"example": "tool_execution_completed"}
    )
    tool_name: str = Field(
        ...,
        description="Name of the tool executed",
        json_schema_extra={"example": "create_casefile_tool"}
    )
    timestamp: IsoTimestamp = Field(
        default_factory=lambda: datetime.now().isoformat(),
        description="Event timestamp (ISO 8601)",
        json_schema_extra={"example": "2025-10-13T12:00:00"}
    )
    parameters: Dict[str, Any] = Field(
        default_factory=dict,
        description="Tool execution parameters",
        json_schema_extra={"example": {"title": "Test Casefile"}}
    )
    result_summary: Optional[Dict[str, Any]] = Field(
        None,
        description="Summary of execution result",
        json_schema_extra={"example": {"casefile_id": "cf_251013_abc123"}}
    )
    duration_ms: Optional[NonNegativeInt] = Field(
        None,
        description="Execution duration in milliseconds",
        json_schema_extra={"example": 250}
    )
    status: Optional[str] = Field(
        None,
        description="Event status: success, error, pending",
        json_schema_extra={"example": "success"}
    )
    error_message: Optional[str] = Field(
        None,
        description="Error message if status is error",
        max_length=2000
    )
    
    # Enhanced tracking for agent integration
    initiator: str = Field(
        default="user",
        description="Who/what initiated this tool execution",
        json_schema_extra={"example": "user"}
    )
    chain_position: Optional[NonNegativeInt] = Field(
        None,
        description="Position in execution chain",
        json_schema_extra={"example": 1}
    )
    chain_id: Optional[str] = Field(
        default_factory=lambda: str(uuid4()),
        description="Unique identifier for a chain of tool executions",
        json_schema_extra={"example": "chain_abc123"}
    )
    reasoning: Optional[str] = Field(
        None,
        description="Agent reasoning for this execution",
        max_length=2000
    )
    source_message_id: Optional[str] = Field(
        None,
        description="Source message ID if applicable"
    )
    related_events: List[str] = Field(
        default_factory=list,
        description="Related event IDs"
    )
    
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
    session_id: ToolSessionId = Field(
        ...,
        description="Unique session ID (ts_ prefix)",
        json_schema_extra={"example": "ts_abc123xyz"}
    )
    user_id: str = Field(
        ...,
        description="User who created the session",
        json_schema_extra={"example": "user@example.com"}
    )
    casefile_id: Optional[CasefileId] = Field(
        None,
        description="Associated casefile ID",
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
    request_ids: List[str] = Field(
        default_factory=list,
        description="List of request IDs (UUIDs) in this session"
    )
    active: bool = Field(
        default=True,
        description="Whether this session is active"
    )
    
    @model_validator(mode='after')
    def validate_timestamp_order(self) -> 'ToolSession':
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
