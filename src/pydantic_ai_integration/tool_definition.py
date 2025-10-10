"""
Tool definition model - SLIM VERSION for MANAGED_TOOLS registry.

After R-A-R pattern implementation:
- Policies (auth, permissions, session, casefile) live in Request DTOs
- Parameters inherited from methods via method_name reference
- Tool = execution metadata only (WHAT to call, not WHEN/WHERE)

DELETED (44+ fields → 12 fields):
- ToolMetadata: Flattened into parent
- ToolBusinessRules: Policies moved to Request DTOs
- ToolSessionPolicies: DELETED (belongs in ToolRequest DTO)
- ToolCasefilePolicies: DELETED (belongs in ToolRequest DTO)  
- ToolAuditConfig: DELETED (handled by Response DTOs)
"""

from datetime import datetime
from enum import Enum
from typing import Any, Awaitable, Callable, Dict, List, Optional, Type

from pydantic import BaseModel, ConfigDict, Field


class ParameterType(str, Enum):
    """Parameter types that map to both Pydantic and OpenAPI."""
    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    OBJECT = "object"
    ARRAY = "array"


class ToolParameterDef(BaseModel):
    """
    Definition of a single tool parameter.
    Kept for Tool inheritance from Method parameters.
    """
    name: str = Field(..., description="Parameter name")
    param_type: ParameterType = Field(..., description="Parameter type")
    required: bool = Field(True, description="Whether parameter is required")
    description: Optional[str] = Field(None, description="Human-readable description")
    default_value: Optional[Any] = Field(None, description="Default value if not provided")
    
    # Constraints for validation
    min_value: Optional[float] = Field(None, description="Minimum value for numeric types")
    max_value: Optional[float] = Field(None, description="Maximum value for numeric types")
    min_length: Optional[int] = Field(None, description="Minimum length for string types")
    max_length: Optional[int] = Field(None, description="Maximum length for string types")
    pattern: Optional[str] = Field(None, description="Regex pattern for string validation")
    enum_values: Optional[List[Any]] = Field(None, description="Allowed values (enum)")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "value",
                "param_type": "integer",
                "required": True,
                "description": "The numeric value to process",
                "min_value": 0,
                "max_value": 1000
            }
        }
    )


class ManagedToolDefinition(BaseModel):
    """
    SLIM tool definition for MANAGED_TOOLS registry.
    12 fields - pure essentials only.
    
    Policies (auth, permissions, session, casefile) belong in Request DTOs (R-A-R pattern).
    Parameters inherited from methods via method_name reference.
    """
    # Identity
    name: str = Field(..., description="Unique tool name (used as identifier)")
    description: str = Field(..., description="What this tool does")
    version: str = Field("1.0.0", description="Tool version for compatibility tracking")
    
    # Classification (optional if method_name specified)
    category: str = Field("general", description="Tool category for organization")
    tags: List[str] = Field(default_factory=list, description="Tags for discovery/filtering")
    
    # Method Reference (for parameter inheritance)
    method_name: Optional[str] = Field(None, description="Reference to method in MANAGED_METHODS")
    
    # Parameters (inherited from method or explicit)
    parameters: List[ToolParameterDef] = Field(
        default_factory=list,
        description="Tool parameter definitions (empty = inherit from method)"
    )
    
    # Execution components
    implementation: Optional[Callable[..., Awaitable[Dict[str, Any]]]] = Field(
        None,
        description="The actual async function implementation",
        exclude=True
    )
    
    params_model: Optional[Type[BaseModel]] = Field(
        None,
        description="Pydantic model for parameter validation",
        exclude=True
    )
    
    # Registration tracking
    registered_at: datetime = Field(
        default_factory=datetime.now,
        description="When this tool was registered"
    )
    
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        json_schema_extra={
            "example": {
                "name": "create_casefile_tool",
                "description": "Creates new casefile with metadata",
                "version": "1.0.0",
                "category": "workspace",
                "tags": ["casefile", "create"],
                "method_name": "create_casefile",
                "parameters": []
            }
        }
    )
    
    def validate_params(self, params: Dict[str, Any]) -> BaseModel:
        """Validate parameters using the Pydantic model."""
        if self.params_model:
            return self.params_model(**params)
        return params
    
    def get_openapi_schema(self) -> Dict[str, Any]:
        """Generate OpenAPI parameter schema from Pydantic model."""
        if self.params_model:
            return self.params_model.model_json_schema()
        
        # Fallback: generate from parameter definitions
        return {
            "type": "object",
            "properties": {
                p.name: {
                    "type": p.param_type.value,
                    "description": p.description,
                    "default": p.default_value
                }
                for p in self.parameters
            },
            "required": [p.name for p in self.parameters if p.required]
        }
    
    def to_discovery_format(self) -> Dict[str, Any]:
        """Convert to format suitable for tool discovery API."""
        return {
            "name": self.name,
            "description": self.description,
            "category": self.category,
            "version": self.version,
            "tags": self.tags,
            "method_name": self.method_name,
            "parameters": [
                {
                    "name": p.name,
                    "type": p.param_type.value,
                    "required": p.required,
                    "description": p.description,
                    "default": p.default_value,
                    "constraints": {
                        k: v for k, v in {
                            "min_value": p.min_value,
                            "max_value": p.max_value,
                            "min_length": p.min_length,
                            "max_length": p.max_length,
                            "pattern": p.pattern,
                            "enum": p.enum_values
                        }.items() if v is not None
                    }
                }
                for p in self.parameters
            ]
        }
