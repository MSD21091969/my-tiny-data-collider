"""
Unified tool decorator and registry - single source of truth for tool engineering.

This module provides the @register_mds_tool decorator that:
1. Registers tools with the agent runtime (for execution)
2. Stores Pydantic validation models (for guardrails)
3. Makes tools discoverable via API (for documentation)
4. Enables type safety (for compile-time checks)

ARCHITECTURE NOTES:
- MANAGED_TOOLS is the global registry (single source of truth)
- Decorator wraps implementation with validation
- Service layer queries registry for execution
- API layer queries registry for discovery
- All metadata/business logic lives in one place

METADATA vs BUSINESS LOGIC:
The decorator accepts both metadata (WHAT) and business rules (WHEN/WHERE).
This allows tools to be self-contained with their own policies.

Example:
    @register_mds_tool(
        name="example_tool",
        description="Processes values",
        params_model=ExampleToolParams,
        category="examples",
        required_permissions=["tools:execute"]
    )
    async def example_tool(ctx: MDSContext, value: int) -> Dict[str, Any]:
        return {"result": value * 2}
"""

from typing import Callable, Type, Dict, Any, List, Optional, Awaitable
from pydantic import BaseModel, ValidationError
from functools import wraps
import logging

# Use absolute imports for better compatibility
from src.pydantic_models.tool_session.tool_definition import (
    ManagedToolDefinition,
    ToolMetadata,
    ToolBusinessRules,
    ToolParameterDef,
    ParameterType,
    ToolSessionPolicies,
    ToolCasefilePolicies,
    ToolAuditConfig,
)

logger = logging.getLogger(__name__)

# Global registry - SINGLE SOURCE OF TRUTH
# All tools registered via @register_mds_tool go here
# Services, API routes, and validators query this registry
MANAGED_TOOLS: Dict[str, ManagedToolDefinition] = {}


def register_mds_tool(
    name: str,
    params_model: Type[BaseModel],
    description: str,
    category: str = "general",
    version: str = "1.0.0",
    display_name: Optional[str] = None,
    enabled: bool = True,
    requires_auth: bool = True,
    required_permissions: Optional[List[str]] = None,
    requires_casefile: bool = False,
    timeout_seconds: int = 30,
    tags: Optional[List[str]] = None,
    docs_url: Optional[str] = None,
    session_policies: Optional[ToolSessionPolicies | Dict[str, Any]] = None,
    casefile_policies: Optional[ToolCasefilePolicies | Dict[str, Any]] = None,
    audit_config: Optional[ToolAuditConfig | Dict[str, Any]] = None,
) -> Callable:
    """
    Unified tool registration decorator.
    
    This decorator is the FOUNDATION of tool engineering. It:
    1. Creates a ManagedToolDefinition with metadata + business rules
    2. Wraps the implementation with Pydantic validation
    3. Registers with agent runtime for execution
    4. Stores in global MANAGED_TOOLS registry for discovery
    
    FIELD PURPOSES:
    Metadata fields (WHAT):
    - name: Tool identifier (used in API, validation, execution)
    - description: Human-readable purpose
    - category: Organization/filtering
    - version: Compatibility tracking
    - display_name: Pretty name for UI
    - tags: Discovery keywords
    - docs_url: Link to documentation
    
    Business logic fields (WHEN/WHERE):
    - enabled: Tool availability toggle
    - requires_auth: Whether user must be authenticated
    - required_permissions: Specific permissions needed
    - requires_casefile: Whether casefile context is mandatory
    - timeout_seconds: Max execution time
    
    Execution fields (HOW):
    - params_model: Pydantic model for validation (the guardrails!)
    
    Args:
        name: Unique tool identifier
        params_model: Pydantic model class for parameter validation
        description: What the tool does
        category: Tool category for organization
        version: Tool version for compatibility
        display_name: Optional human-friendly name
        enabled: Whether tool is available
        requires_auth: Whether authentication is required
        required_permissions: List of required permissions
        requires_casefile: Whether casefile context is required
        timeout_seconds: Max execution time
        tags: List of tags for discovery
        docs_url: Link to documentation
        
    Returns:
        Decorated function with validation and registration
        
    Example:
        >>> class MyToolParams(BaseModel):
        ...     value: int = Field(..., ge=0, le=100)
        ...
        >>> @register_mds_tool(
        ...     name="my_tool",
        ...     params_model=MyToolParams,
        ...     description="Does something",
        ...     required_permissions=["tools:execute"]
        ... )
        ... async def my_tool(ctx: MDSContext, value: int) -> Dict[str, Any]:
        ...     return {"result": value * 2}
    """
    def decorator(func: Callable[..., Awaitable[Dict[str, Any]]]) -> Callable:
        """Inner decorator that processes the function."""
        
        # Extract parameter definitions from Pydantic model
        # This bridges Pydantic's Field() constraints to our ToolParameterDef
        parameters = _extract_parameter_definitions(params_model)
        
        # Create metadata (WHAT the tool is)
        metadata = ToolMetadata(
            name=name,
            display_name=display_name or name,
            description=description,
            category=category,
            version=version,
            tags=tags or [],
            docs_url=docs_url
        )
        
        # Create business rules (WHEN/WHERE it can run)
        business_rules = ToolBusinessRules(
            enabled=enabled,
            requires_auth=requires_auth,
            required_permissions=required_permissions or [],
            requires_casefile=requires_casefile,
            timeout_seconds=timeout_seconds
        )
        
        # Normalize optional policy inputs (allow dicts from templates)
        session_policy_obj: Optional[ToolSessionPolicies]
        if isinstance(session_policies, dict):
            session_policy_obj = ToolSessionPolicies(**session_policies)
        else:
            session_policy_obj = session_policies

        casefile_policy_obj: Optional[ToolCasefilePolicies]
        if isinstance(casefile_policies, dict):
            casefile_policy_obj = ToolCasefilePolicies(**casefile_policies)
        else:
            casefile_policy_obj = casefile_policies

        audit_config_obj: Optional[ToolAuditConfig]
        if isinstance(audit_config, dict):
            audit_config_obj = ToolAuditConfig(**audit_config)
        else:
            audit_config_obj = audit_config

        # Create complete tool definition (single source of truth)
        tool_def = ManagedToolDefinition(
            metadata=metadata,
            business_rules=business_rules,
            parameters=parameters,
            implementation=func,
            params_model=params_model,
            session_policies=session_policy_obj,
            casefile_policies=casefile_policy_obj,
            audit_config=audit_config_obj,
        )
        
        # Store in global registry
        MANAGED_TOOLS[name] = tool_def
        logger.info(
            f"Registered tool '{name}' (category: {category}, "
            f"requires_auth: {requires_auth}, enabled: {enabled})"
        )
        
        # Create validated wrapper
        @wraps(func)
        async def validated_wrapper(ctx, **kwargs):
            """
            Wrapper that validates parameters before execution.
            
            This is WHERE validation happens - at the boundary between
            service layer and tool execution.
            
            The wrapper:
            1. Validates params using Pydantic model (guardrails!)
            2. Calls original function with validated params
            3. Preserves function signature for type checking
            """
            try:
                # Validate using Pydantic model
                validated = params_model(**kwargs)
                
                # Call original function with validated params
                # The .model_dump() ensures we pass plain dict/primitives
                return await func(ctx, **validated.model_dump())
                
            except ValidationError as e:
                # Pydantic validation failed - return error details
                logger.error(f"Validation failed for tool '{name}': {e}")
                return {
                    "error": "Parameter validation failed",
                    "details": e.errors(),
                    "tool_name": name
                }
        
        # Register with agent runtime
        # This makes the tool callable by the agent
        from .agents.base import default_agent
        default_agent.tool(validated_wrapper)
        
        logger.info(f"Tool '{name}' registered with agent runtime")
        
        # Return the validated wrapper
        # This allows direct calls: await example_tool(ctx, value=42)
        return validated_wrapper
    
    return decorator


def _extract_parameter_definitions(params_model: Type[BaseModel]) -> List[ToolParameterDef]:
    """
    Extract parameter definitions from Pydantic model.
    
    This bridges Pydantic's Field() constraints to our ToolParameterDef schema.
    It extracts metadata (name, type, description) and business logic
    (required, min/max values, patterns).
    
    FIELD MAPPING:
    - Pydantic Field(...) → ToolParameterDef.required = True
    - Field(default=X) → ToolParameterDef.default_value = X
    - Field(ge=0, le=100) → min_value=0, max_value=100
    - Field(min_length=1) → min_length=1
    - Literal["a", "b"] → enum_values=["a", "b"]
    
    Args:
        params_model: Pydantic model class
        
    Returns:
        List of ToolParameterDef instances
    """
    parameters = []
    
    # Get model fields from Pydantic v2
    model_fields = params_model.model_fields
    
    for field_name, field_info in model_fields.items():
        # Determine parameter type from annotation
        param_type = _python_type_to_parameter_type(field_info.annotation)
        
        # Extract constraints from Field()
        constraints = {}
        if hasattr(field_info, 'metadata'):
            for metadata_item in field_info.metadata:
                if hasattr(metadata_item, 'ge'):
                    constraints['min_value'] = metadata_item.ge
                if hasattr(metadata_item, 'le'):
                    constraints['max_value'] = metadata_item.le
                if hasattr(metadata_item, 'min_length'):
                    constraints['min_length'] = metadata_item.min_length
                if hasattr(metadata_item, 'max_length'):
                    constraints['max_length'] = metadata_item.max_length
                if hasattr(metadata_item, 'pattern'):
                    constraints['pattern'] = metadata_item.pattern
        
        # Create parameter definition
        param_def = ToolParameterDef(
            name=field_name,
            param_type=param_type,
            required=field_info.is_required(),
            description=field_info.description or f"Parameter: {field_name}",
            default_value=field_info.default if not field_info.is_required() else None,
            **constraints
        )
        
        parameters.append(param_def)
    
    return parameters


def _python_type_to_parameter_type(python_type: Any) -> ParameterType:
    """
    Map Python/Pydantic type hints to ParameterType enum.
    
    This is metadata mapping - describes WHAT type the parameter is.
    
    Args:
        python_type: Python type annotation
        
    Returns:
        ParameterType enum value
    """
    # Handle string representations
    type_str = str(python_type).lower()
    
    if 'int' in type_str:
        return ParameterType.INTEGER
    elif 'float' in type_str or 'decimal' in type_str:
        return ParameterType.FLOAT
    elif 'bool' in type_str:
        return ParameterType.BOOLEAN
    elif 'dict' in type_str or 'mapping' in type_str:
        return ParameterType.OBJECT
    elif 'list' in type_str or 'sequence' in type_str:
        return ParameterType.ARRAY
    else:
        return ParameterType.STRING


# Public API functions for querying the registry

def get_registered_tools() -> Dict[str, ManagedToolDefinition]:
    """
    Get all registered tools.
    
    Returns:
        Dictionary mapping tool name to ManagedToolDefinition
    """
    return MANAGED_TOOLS


def get_tool_names() -> List[str]:
    """
    Get list of all registered tool names.
    
    Used by validators to check if a tool_name is valid.
    
    Returns:
        List of tool names
    """
    return list(MANAGED_TOOLS.keys())


def validate_tool_exists(tool_name: str) -> bool:
    """
    Check if a tool is registered.
    
    Used by Pydantic validators in ToolRequestPayload.
    
    Args:
        tool_name: Name to check
        
    Returns:
        True if tool is registered
    """
    return tool_name in MANAGED_TOOLS


def get_tool_definition(tool_name: str) -> Optional[ManagedToolDefinition]:
    """
    Get tool definition by name.
    
    Used by service layer to:
    - Validate parameters (tool_def.validate_params())
    - Check permissions (tool_def.check_permission())
    - Execute tool (tool_def.implementation())
    
    Args:
        tool_name: Name of the tool
        
    Returns:
        ManagedToolDefinition or None if not found
    """
    return MANAGED_TOOLS.get(tool_name)


def list_tools_by_category(category: str, enabled_only: bool = True) -> List[ManagedToolDefinition]:
    """
    List tools filtered by category.
    
    Used by API discovery endpoints.
    
    Args:
        category: Category to filter by
        enabled_only: Whether to only return enabled tools
        
    Returns:
        List of matching tool definitions
    """
    tools = [
        tool for tool in MANAGED_TOOLS.values()
        if tool.metadata.category == category
    ]
    
    if enabled_only:
        tools = [t for t in tools if t.business_rules.enabled]
    
    return tools


def get_tool_schema(tool_name: str) -> Optional[Dict[str, Any]]:
    """
    Get OpenAPI schema for a tool.
    
    Used by API documentation endpoints.
    
    Args:
        tool_name: Name of the tool
        
    Returns:
        OpenAPI schema dictionary or None if tool not found
    """
    tool = MANAGED_TOOLS.get(tool_name)
    if not tool:
        return None
    
    return tool.get_openapi_schema()


# Notes for future development:
#
# RATE LIMITING:
# Add rate_limiter field to ManagedToolDefinition that stores a RateLimiter instance.
# Service layer checks rate_limiter.check(user_id) before execution.
#
# PERMISSIONS:
# Add permission_checker field that's a Callable[[List[str]], bool].
# Service layer calls tool_def.permission_checker(user.permissions) before execution.
#
# COST TRACKING:
# Add cost_per_execution field (float) to business_rules.
# Service layer logs cost in ToolEvent.metadata for billing/analytics.
#
# VERSIONING:
# Multiple versions can coexist: MANAGED_TOOLS["tool_name:v1"], ["tool_name:v2"]
# API accepts version in request, defaults to latest.
#
# TOOLSETS:
# Group tools via category or create ToolsetDefinition model.
# API can list/filter by toolset for easier discovery.
