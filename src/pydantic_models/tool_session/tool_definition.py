"""
Unified tool definition model - the foundation of tool engineering.

This module defines the core data structures that bridge:
- API layer (schema, validation)
- Service layer (execution orchestration)
- Agent layer (runtime tool registration)

METADATA vs BUSINESS LOGIC SEPARATION:
- Metadata fields: WHAT the tool is (name, description, category, parameters)
- Business logic fields: WHEN/WHERE to use it (enabled, permissions, rate_limits)
- Execution fields: HOW it runs (implementation, params_model, validation)
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Type, Callable, Dict, Any, Optional, List, Awaitable
from enum import Enum
from datetime import datetime


class ParameterType(str, Enum):
    """
    Parameter types that map to both Pydantic and OpenAPI.
    
    METADATA: These describe WHAT type of data is expected.
    """
    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    OBJECT = "object"
    ARRAY = "array"


class ToolParameterDef(BaseModel):
    """
    Definition of a single tool parameter.
    
    FIELD PURPOSES:
    - name, param_type, description: METADATA (describes the parameter)
    - required, default_value: BUSINESS LOGIC (validation rules)
    - pydantic_field: EXECUTION (actual validator instance)
    """
    name: str = Field(..., description="Parameter name")
    param_type: ParameterType = Field(..., description="Parameter type")
    required: bool = Field(True, description="Whether parameter is required")
    description: Optional[str] = Field(None, description="Human-readable description")
    default_value: Optional[Any] = Field(None, description="Default value if not provided")
    
    # Constraints (business logic - guardrails)
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


class ToolMetadata(BaseModel):
    """
    Pure metadata about a tool - the WHAT.
    
    These fields describe the tool but don't affect execution.
    They're used for:
    - Discovery (listing tools)
    - Documentation (OpenAPI schema)
    - Categorization (filtering, organization)
    - Audit trail (tracking what was executed)
    """
    name: str = Field(..., description="Unique tool name (used as identifier)")
    display_name: Optional[str] = Field(None, description="Human-friendly display name")
    description: str = Field(..., description="What this tool does")
    category: str = Field("general", description="Tool category for organization")
    version: str = Field("1.0.0", description="Tool version for compatibility tracking")
    author: Optional[str] = Field(None, description="Tool author/maintainer")
    tags: List[str] = Field(default_factory=list, description="Tags for discovery/filtering")
    
    # Documentation URLs
    docs_url: Optional[str] = Field(None, description="Link to detailed documentation")
    example_url: Optional[str] = Field(None, description="Link to usage examples")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "example_tool",
                "display_name": "Example Tool",
                "description": "Processes numeric values",
                "category": "examples",
                "version": "1.0.0",
                "tags": ["demo", "numeric"]
            }
        }
    )


class ToolBusinessRules(BaseModel):
    """
    Business logic configuration - the WHEN/WHERE.
    
    These fields control:
    - Availability (enabled, deprecated)
    - Access control (permissions, rate limits)
    - Execution constraints (timeout, retries)
    - Cost management (resource limits)
    """
    enabled: bool = Field(True, description="Whether tool is available for use")
    deprecated: bool = Field(False, description="Whether tool is deprecated")
    deprecation_message: Optional[str] = Field(None, description="Message if deprecated")
    
    # Access control (business logic)
    requires_auth: bool = Field(True, description="Whether authentication is required")
    required_permissions: List[str] = Field(
        default_factory=list,
        description="Permissions required to execute (e.g., ['casefiles:write'])"
    )
    allowed_roles: List[str] = Field(
        default_factory=list,
        description="Roles allowed to execute (empty = all authenticated users)"
    )
    
    # Rate limiting (business logic)
    rate_limit_per_minute: Optional[int] = Field(None, description="Max executions per minute per user")
    rate_limit_per_hour: Optional[int] = Field(None, description="Max executions per hour per user")
    
    # Execution constraints (business logic)
    timeout_seconds: int = Field(30, description="Max execution time before timeout")
    max_retries: int = Field(0, description="Number of retries on failure")
    requires_casefile: bool = Field(False, description="Whether casefile context is required")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "enabled": True,
                "requires_auth": True,
                "required_permissions": ["tools:execute"],
                "timeout_seconds": 30,
                "requires_casefile": False
            }
        }
    )


class ManagedToolDefinition(BaseModel):
    """
    Complete tool definition that serves as the single source of truth.
    
    ARCHITECTURE:
    This model bridges three layers:
    1. API Layer: Provides schema for validation and discovery
    2. Service Layer: Provides execution orchestration
    3. Agent Layer: Provides runtime registration
    
    FIELD CATEGORIZATION:
    - metadata: Pure information (WHAT is this tool?)
    - business_rules: Execution policy (WHEN/WHERE can it run?)
    - parameters: Input specification (WHAT data does it need?)
    - implementation: Execution function (HOW does it work?)
    - params_model: Validation model (HOW to validate inputs?)
    
    USAGE:
    This is created by the @register_mds_tool decorator and stored in
    MANAGED_TOOLS global registry. Services query this registry for:
    - Validation (params_model.validate())
    - Execution (implementation())
    - Discovery (metadata, parameters)
    - Authorization (business_rules.required_permissions)
    """
    
    # Core metadata (WHAT)
    metadata: ToolMetadata = Field(..., description="Tool metadata and documentation")
    
    # Business rules (WHEN/WHERE)
    business_rules: ToolBusinessRules = Field(
        default_factory=ToolBusinessRules,
        description="Business logic and execution policies"
    )
    
    # Parameters (WHAT inputs)
    parameters: List[ToolParameterDef] = Field(
        default_factory=list,
        description="Tool parameter definitions"
    )
    
    # Execution components (HOW)
    implementation: Optional[Callable[..., Awaitable[Dict[str, Any]]]] = Field(
        None,
        description="The actual async function implementation",
        exclude=True  # Don't serialize the function
    )
    
    params_model: Optional[Type[BaseModel]] = Field(
        None,
        description="Pydantic model for parameter validation",
        exclude=True  # Don't serialize the type
    )
    
    # Registration tracking (WHEN - audit)
    registered_at: str = Field(
        default_factory=lambda: datetime.now().isoformat(),
        description="When this tool was registered (ISO 8601)"
    )
    
    model_config = ConfigDict(
        arbitrary_types_allowed=True,  # Allow Callable and Type
        json_schema_extra={
            "example": {
                "metadata": {
                    "name": "example_tool",
                    "description": "Processes numeric values",
                    "category": "examples",
                    "version": "1.0.0"
                },
                "business_rules": {
                    "enabled": True,
                    "requires_auth": True,
                    "timeout_seconds": 30
                },
                "parameters": [
                    {
                        "name": "value",
                        "param_type": "integer",
                        "required": True,
                        "description": "Value to process"
                    }
                ]
            }
        }
    )
    
    def validate_params(self, params: Dict[str, Any]) -> BaseModel:
        """
        Validate parameters using the Pydantic model.
        
        This is WHERE validation happens - at the boundary between
        API input and service execution.
        
        Args:
            params: Raw parameter dictionary from API request
            
        Returns:
            Validated Pydantic model instance
            
        Raises:
            ValidationError: If parameters don't match schema
        """
        if self.params_model:
            return self.params_model(**params)
        
        # If no model, return params as-is (validation happened elsewhere)
        return params
    
    def get_openapi_schema(self) -> Dict[str, Any]:
        """
        Generate OpenAPI parameter schema from Pydantic model.
        
        This is HOW we generate API documentation automatically.
        The schema comes from the params_model, which has all the
        Field() constraints (ge=, le=, min_length=, etc.)
        
        Returns:
            OpenAPI-compatible parameter schema
        """
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
    
    def check_permission(self, user_permissions: List[str]) -> bool:
        """
        Check if user has required permissions.
        
        This is WHERE authorization happens - service layer checks
        this before execution.
        
        Args:
            user_permissions: List of permissions the user has
            
        Returns:
            True if user has all required permissions
        """
        if not self.business_rules.required_permissions:
            return True  # No permissions required
        
        return all(
            perm in user_permissions
            for perm in self.business_rules.required_permissions
        )
    
    def check_enabled(self) -> tuple[bool, Optional[str]]:
        """
        Check if tool is enabled and available.
        
        Returns:
            Tuple of (is_enabled, error_message)
        """
        if not self.business_rules.enabled:
            return False, f"Tool '{self.metadata.name}' is currently disabled"
        
        if self.business_rules.deprecated:
            msg = self.business_rules.deprecation_message or "This tool is deprecated"
            return False, f"Tool '{self.metadata.name}' is deprecated: {msg}"
        
        return True, None
    
    def to_discovery_format(self) -> Dict[str, Any]:
        """
        Convert to format suitable for tool discovery API.
        
        This is WHAT gets returned by GET /tools endpoint.
        Includes metadata, parameters, and business rules relevant to clients.
        """
        return {
            "name": self.metadata.name,
            "display_name": self.metadata.display_name or self.metadata.name,
            "description": self.metadata.description,
            "category": self.metadata.category,
            "version": self.metadata.version,
            "tags": self.metadata.tags,
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
            ],
            "enabled": self.business_rules.enabled,
            "deprecated": self.business_rules.deprecated,
            "requires_auth": self.business_rules.requires_auth,
            "requires_casefile": self.business_rules.requires_casefile,
            "docs_url": self.metadata.docs_url
        }


# Notes on Field Purposes (for documentation and future development):
#
# METADATA FIELDS (immutable, descriptive):
# - Used for: Discovery, documentation, categorization, audit logs
# - Examples: name, description, category, version, author, tags
# - Stored in: ManagedToolDefinition.metadata
# - When to add: When you need to describe WHAT the tool is
#
# BUSINESS LOGIC FIELDS (mutable, policy-driven):
# - Used for: Authorization, rate limiting, execution control, cost management
# - Examples: enabled, required_permissions, rate_limit, timeout, retries
# - Stored in: ManagedToolDefinition.business_rules
# - When to add: When you need to control WHEN/WHERE tool can execute
#
# EXECUTION FIELDS (runtime, functional):
# - Used for: Validation, execution, type safety
# - Examples: implementation, params_model, validate_params()
# - Stored in: ManagedToolDefinition (top level)
# - When to add: When you need to define HOW tool executes
#
# AUDIT FIELDS (temporal, tracking):
# - Used for: Compliance, debugging, monitoring, analytics
# - Examples: registered_at, execution timestamps in ToolEvent
# - Stored in: Multiple places (definition, events, context)
# - When to add: When you need to track WHEN something happened
