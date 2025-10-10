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

import logging
from functools import wraps
from typing import Any, Awaitable, Callable, Dict, List, Optional, Type

from pydantic import BaseModel, ValidationError

# Import from local module (tool infrastructure belongs together)
from .tool_definition import (
    ManagedToolDefinition,
    ParameterType,
    ToolParameterDef,
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
    tags: Optional[List[str]] = None,
    method_name: Optional[str] = None,
) -> Callable:
    """
    Unified tool registration decorator - SLIM VERSION.
    
    After R-A-R refactor:
    - Policies moved to Request DTOs
    - Parameters inherited from methods
    - Tool = execution metadata only
    
    Args:
        name: Unique tool identifier
        params_model: Pydantic model class for parameter validation
        description: What the tool does
        category: Tool category for organization
        version: Tool version
        tags: List of tags for discovery
        method_name: Optional reference to method in MANAGED_METHODS (for parameter inheritance)
        
    Returns:
        Decorated function with validation and registration
    """
    def decorator(func: Callable[..., Awaitable[Dict[str, Any]]]) -> Callable:
        """Inner decorator that processes the function."""
        
        # Extract parameter definitions from Pydantic model
        parameters = _extract_parameter_definitions(params_model)
        
        # Create slim tool definition
        tool_def = ManagedToolDefinition(
            name=name,
            description=description,
            version=version,
            category=category,
            tags=tags or [],
            method_name=method_name,
            parameters=parameters,
            implementation=func,
            params_model=params_model,
        )
        
        # Store in global registry
        MANAGED_TOOLS[name] = tool_def
        logger.info(
            f"Registered tool '{name}' (category: {category}, "
            f"method_name: {method_name or 'N/A'})"
        )
        
        # Create validated wrapper
        @wraps(func)
        async def validated_wrapper(ctx, **kwargs):
            """
            Wrapper that validates parameters and wraps response in ToolResponse.
            
            This is WHERE validation and response wrapping happens - at the boundary
            between service layer and tool execution.
            
            The wrapper:
            1. Validates params using Pydantic model (guardrails!)
            2. Tracks execution time
            3. Calls original function with validated params
            4. Wraps result in ToolResponse envelope (standard structure!)
            5. Handles errors with proper status and error fields
            """
            from datetime import datetime
            from uuid import uuid4

            from src.pydantic_models.base.types import RequestStatus
            from src.pydantic_models.operations.tool_execution_ops import (
                ToolResponse,
                ToolResponsePayload,
            )
            
            # Track execution time
            start_time = datetime.now()
            
            # Get request_id from context if available, otherwise generate new one
            request_id = getattr(ctx, 'request_id', None) or uuid4()
            
            try:
                # Validate using Pydantic model
                validated = params_model(**kwargs)
                
                # Call original function with validated params
                # The .model_dump() ensures we pass plain dict/primitives
                raw_result = await func(ctx, **validated.model_dump())
                
                # Calculate execution time
                execution_time_ms = int((datetime.now() - start_time).total_seconds() * 1000)
                
                # Serialize tool events to dicts if they exist
                tool_events = getattr(ctx, 'tool_events', [])
                serialized_events = []
                for event in tool_events:
                    if hasattr(event, 'model_dump'):
                        serialized_events.append(event.model_dump())
                    elif isinstance(event, dict):
                        serialized_events.append(event)
                    else:
                        # Fallback: convert to dict if possible
                        serialized_events.append(dict(event) if hasattr(event, '__dict__') else {})
                
                # Wrap raw Dict result in ToolResponsePayload
                response_payload = ToolResponsePayload(
                    result=raw_result if isinstance(raw_result, dict) else {"value": raw_result},
                    events=serialized_events,
                    session_request_id=getattr(ctx, 'session_request_id', None)
                )
                
                # Wrap in standard ToolResponse envelope
                tool_response = ToolResponse(
                    request_id=request_id,
                    status=RequestStatus.COMPLETED,
                    payload=response_payload,
                    metadata={
                        "tool_name": name,
                        "execution_time_ms": execution_time_ms,
                        "user_id": getattr(ctx, 'user_id', None),
                        "session_id": getattr(ctx, 'session_id', None),
                        "casefile_id": getattr(ctx, 'casefile_id', None)
                    }
                )
                
                logger.info(
                    f"Tool '{name}' completed successfully in {execution_time_ms}ms "
                    f"(request_id: {request_id})"
                )
                
                return tool_response.model_dump()
                
            except ValidationError as e:
                # Pydantic validation failed - return error details wrapped in ToolResponse
                logger.error(f"Validation failed for tool '{name}': {e}")
                
                execution_time_ms = int((datetime.now() - start_time).total_seconds() * 1000)
                
                error_response = ToolResponse(
                    request_id=request_id,
                    status=RequestStatus.FAILED,
                    payload=ToolResponsePayload(
                        result={},
                        events=[],
                        session_request_id=getattr(ctx, 'session_request_id', None)
                    ),
                    error=f"Parameter validation failed: {str(e)}",
                    metadata={
                        "tool_name": name,
                        "execution_time_ms": execution_time_ms,
                        "validation_errors": e.errors(),
                        "user_id": getattr(ctx, 'user_id', None),
                        "session_id": getattr(ctx, 'session_id', None)
                    }
                )
                
                return error_response.model_dump()
                
            except Exception as e:
                # Tool execution failed - return error wrapped in ToolResponse
                logger.error(f"Tool '{name}' execution failed: {e}", exc_info=True)
                
                execution_time_ms = int((datetime.now() - start_time).total_seconds() * 1000)
                
                error_response = ToolResponse(
                    request_id=request_id,
                    status=RequestStatus.FAILED,
                    payload=ToolResponsePayload(
                        result={},
                        events=[],
                        session_request_id=getattr(ctx, 'session_request_id', None)
                    ),
                    error=f"Tool execution failed: {str(e)}",
                    metadata={
                        "tool_name": name,
                        "execution_time_ms": execution_time_ms,
                        "error_type": type(e).__name__,
                        "user_id": getattr(ctx, 'user_id', None),
                        "session_id": getattr(ctx, 'session_id', None)
                    }
                )
                
                return error_response.model_dump()
        
        # Register with agent runtime
        # This makes the tool callable by the agent
        from .tools.agents.base import default_agent
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
        if tool.category == category
    ]
    
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


# Hierarchical Discovery API (Classification System)
# These methods enable filtering and discovery based on the new classification metadata


def get_tools_by_domain(domain: str, enabled_only: bool = True) -> List[ManagedToolDefinition]:
    """
    List tools filtered by classification domain.
    
    Supports hierarchical tool organization with domains:
    - communication: Email, chat, notifications
    - workspace: Documents, files, spreadsheets
    - automation: Workflows, pipelines, orchestration
    - utilities: Debugging, testing, monitoring
    
    Args:
        domain: Domain to filter by (communication, workspace, automation, utilities)
        enabled_only: Whether to only return enabled tools
        
    Returns:
        List of matching tool definitions
        
    Example:
        >>> email_tools = get_tools_by_domain("communication")
        >>> for tool in email_tools:
        ...     print(tool.metadata.name)
    """
    tools = []
    for tool in MANAGED_TOOLS.values():
        # Check if tool has classification metadata
        if hasattr(tool, 'classification') and tool.classification:
            if tool.classification.get('domain') == domain:
                tools.append(tool)
    
    if enabled_only:
        tools = [t for t in tools if t.business_rules.enabled]
    
    return tools


def get_tools_by_subdomain(domain: str, subdomain: str, enabled_only: bool = True) -> List[ManagedToolDefinition]:
    """
    List tools filtered by domain and subdomain.
    
    Provides more granular filtering within a domain:
    - communication/email: Gmail, SMTP tools
    - communication/chat: Slack, Teams tools
    - workspace/google: Drive, Sheets, Docs
    - automation/pipelines: Multi-step workflows
    
    Args:
        domain: Parent domain
        subdomain: Specific area within domain
        enabled_only: Whether to only return enabled tools
        
    Returns:
        List of matching tool definitions
        
    Example:
        >>> gmail_tools = get_tools_by_subdomain("communication", "email")
    """
    tools = []
    for tool in MANAGED_TOOLS.values():
        if hasattr(tool, 'classification') and tool.classification:
            if (tool.classification.get('domain') == domain and 
                tool.classification.get('subdomain') == subdomain):
                tools.append(tool)
    
    if enabled_only:
        tools = [t for t in tools if t.business_rules.enabled]
    
    return tools


def get_tools_by_capability(capability: str, enabled_only: bool = True) -> List[ManagedToolDefinition]:
    """
    List tools filtered by capability (operation type).
    
    Enables filtering by what the tool does:
    - create: Creates new resources (send email, create file)
    - read: Retrieves data (list messages, get document)
    - update: Modifies existing resources (edit file, update record)
    - delete: Removes resources (delete message, remove file)
    - process: Transforms or analyzes data (pipeline, batch)
    - search: Queries and filters data (search messages, find files)
    
    Args:
        capability: Capability to filter by
        enabled_only: Whether to only return enabled tools
        
    Returns:
        List of matching tool definitions
        
    Example:
        >>> read_tools = get_tools_by_capability("read")
        >>> search_tools = get_tools_by_capability("search")
    """
    tools = []
    for tool in MANAGED_TOOLS.values():
        if hasattr(tool, 'classification') and tool.classification:
            if tool.classification.get('capability') == capability:
                tools.append(tool)
    
    if enabled_only:
        tools = [t for t in tools if t.business_rules.enabled]
    
    return tools


def get_tools_by_complexity(complexity: str, enabled_only: bool = True) -> List[ManagedToolDefinition]:
    """
    List tools filtered by complexity level.
    
    Enables filtering by composition:
    - atomic: Single operation, no sub-tools
    - composite: Combines multiple operations
    - pipeline: Multi-step workflow with orchestration
    
    Args:
        complexity: Complexity level to filter by
        enabled_only: Whether to only return enabled tools
        
    Returns:
        List of matching tool definitions
        
    Example:
        >>> simple_tools = get_tools_by_complexity("atomic")
        >>> workflows = get_tools_by_complexity("pipeline")
    """
    tools = []
    for tool in MANAGED_TOOLS.values():
        if hasattr(tool, 'classification') and tool.classification:
            if tool.classification.get('complexity') == complexity:
                tools.append(tool)
    
    if enabled_only:
        tools = [t for t in tools if t.business_rules.enabled]
    
    return tools


def get_tools_by_maturity(maturity: str, enabled_only: bool = True) -> List[ManagedToolDefinition]:
    """
    List tools filtered by maturity stage.
    
    Enables filtering by lifecycle stage:
    - experimental: Early development, API may change
    - beta: Feature complete, testing in progress
    - stable: Production ready, versioned, documented
    - deprecated: Being phased out, migration path available
    
    Args:
        maturity: Maturity stage to filter by
        enabled_only: Whether to only return enabled tools
        
    Returns:
        List of matching tool definitions
        
    Example:
        >>> prod_tools = get_tools_by_maturity("stable")
        >>> beta_tools = get_tools_by_maturity("beta")
    """
    tools = []
    for tool in MANAGED_TOOLS.values():
        if hasattr(tool, 'classification') and tool.classification:
            if tool.classification.get('maturity') == maturity:
                tools.append(tool)
    
    if enabled_only:
        tools = [t for t in tools if t.business_rules.enabled]
    
    return tools


def get_tools_by_integration_tier(integration_tier: str, enabled_only: bool = True) -> List[ManagedToolDefinition]:
    """
    List tools filtered by integration tier.
    
    Enables filtering by external dependency scope:
    - internal: Uses only internal services (casefile, session)
    - external: Requires external APIs (Gmail, Drive, Sheets)
    - hybrid: Combines internal and external services
    
    Args:
        integration_tier: Integration tier to filter by
        enabled_only: Whether to only return enabled tools
        
    Returns:
        List of matching tool definitions
        
    Example:
        >>> internal_tools = get_tools_by_integration_tier("internal")
        >>> api_tools = get_tools_by_integration_tier("external")
    """
    tools = []
    for tool in MANAGED_TOOLS.values():
        if hasattr(tool, 'classification') and tool.classification:
            if tool.classification.get('integration_tier') == integration_tier:
                tools.append(tool)
    
    if enabled_only:
        tools = [t for t in tools if t.business_rules.enabled]
    
    return tools


def get_hierarchical_tool_path(tool_name: str) -> Optional[str]:
    """
    Get hierarchical path for a tool based on classification.
    
    Constructs a path like "communication.email.gmail_send_message"
    from the tool's classification metadata.
    
    Args:
        tool_name: Name of the tool
        
    Returns:
        Hierarchical path string or None if tool not found or no classification
        
    Example:
        >>> path = get_hierarchical_tool_path("gmail_send_message")
        >>> print(path)  # "communication.email.gmail_send_message"
    """
    tool = MANAGED_TOOLS.get(tool_name)
    if not tool or not hasattr(tool, 'classification') or not tool.classification:
        return None
    
    domain = tool.classification.get('domain', '')
    subdomain = tool.classification.get('subdomain', '')
    
    if domain and subdomain:
        return f"{domain}.{subdomain}.{tool_name}"
    elif domain:
        return f"{domain}.{tool_name}"
    else:
        return tool_name


def get_classification_summary() -> Dict[str, Any]:
    """
    Get summary statistics of tool classification.
    
    Provides overview of:
    - Tools by domain
    - Tools by capability
    - Tools by maturity
    - Tools by integration tier
    
    Returns:
        Dictionary with classification counts
        
    Example:
        >>> summary = get_classification_summary()
        >>> print(f"Communication tools: {summary['by_domain']['communication']}")
    """
    summary = {
        'total_tools': len(MANAGED_TOOLS),
        'by_domain': {},
        'by_capability': {},
        'by_complexity': {},
        'by_maturity': {},
        'by_integration_tier': {},
        'unclassified': 0
    }
    
    for tool in MANAGED_TOOLS.values():
        if hasattr(tool, 'classification') and tool.classification:
            # Count by domain
            domain = tool.classification.get('domain')
            if domain:
                summary['by_domain'][domain] = summary['by_domain'].get(domain, 0) + 1
            
            # Count by capability
            capability = tool.classification.get('capability')
            if capability:
                summary['by_capability'][capability] = summary['by_capability'].get(capability, 0) + 1
            
            # Count by complexity
            complexity = tool.classification.get('complexity')
            if complexity:
                summary['by_complexity'][complexity] = summary['by_complexity'].get(complexity, 0) + 1
            
            # Count by maturity
            maturity = tool.classification.get('maturity')
            if maturity:
                summary['by_maturity'][maturity] = summary['by_maturity'].get(maturity, 0) + 1
            
            # Count by integration tier
            integration_tier = tool.classification.get('integration_tier')
            if integration_tier:
                summary['by_integration_tier'][integration_tier] = summary['by_integration_tier'].get(integration_tier, 0) + 1
        else:
            summary['unclassified'] += 1
    
    return summary


def get_tool_parameters(tool_name: str) -> List[ToolParameterDef]:
    """
    Get parameters for a tool (inherited from method or explicit).
    
    Parameter Inheritance Flow:
    1. If tool has explicit parameters → use them
    2. If tool has method_name → inherit from method
    3. Otherwise → empty list
    
    Args:
        tool_name: Name of the tool
        
    Returns:
        List of parameter definitions
        
    Raises:
        KeyError: If tool not found
    """
    tool_def = MANAGED_TOOLS.get(tool_name)
    if not tool_def:
        raise KeyError(f"Tool '{tool_name}' not found in MANAGED_TOOLS registry")
    
    # If tool has explicit parameters, use them
    if tool_def.parameters:
        return tool_def.parameters
    
    # Otherwise, inherit from method
    if tool_def.method_name:
        from . import method_registry
        try:
            # Try compound key first (for tools that specify service.method_name)
            if '.' in tool_def.method_name:
                method_params = method_registry.get_method_parameters(tool_def.method_name)
            else:
                # For simple method names, find all matching methods and use the first one
                # This handles the case where multiple services have the same method name
                matching_methods = method_registry.find_methods_by_method_name(tool_def.method_name)
                if matching_methods:
                    # Use the first match (could be enhanced to be more specific later)
                    method_def = matching_methods[0]
                    method_params = method_registry.extract_parameters_from_request_model(method_def.request_model_class)
                else:
                    method_params = []
            
            # Convert MethodParameterDef → ToolParameterDef
            tool_params = []
            for mp in method_params:
                tool_params.append(ToolParameterDef(
                    name=mp.name,
                    param_type=ParameterType(mp.param_type),  # Convert string to enum
                    required=mp.required,
                    description=mp.description,
                    default_value=mp.default_value,
                    min_value=mp.min_value,
                    max_value=mp.max_value,
                    min_length=mp.min_length,
                    max_length=mp.max_length,
                    pattern=mp.pattern,
                ))
            return tool_params
        except Exception as e:
            logger.warning(
                f"Failed to inherit parameters from method '{tool_def.method_name}' "
                f"for tool '{tool_name}': {e}"
            )
            return []
    
    return []


def _instantiate_service(service_name: str, method_name: str):
    """
    Instantiate a service by name with future-proof DI design.
    
    Current: Simple instantiation (no DI)
    Future: Accept service_registry parameter for full DI support
    
    Args:
        service_name: Service class name (e.g., "CasefileService")
        method_name: Method name for logging context
        
    Returns:
        Instantiated service object
        
    Raises:
        ValueError: If service cannot be instantiated
    """
    import importlib
    
    logger.info(f"Instantiating service '{service_name}' for method '{method_name}'")
    
    try:
        # Map service name to module path
        # Convention: CasefileService → src.casefileservice.service
        service_module_map = {
            "CasefileService": "casefileservice.service",
            "ToolSessionService": "tool_sessionservice.service",
            "CommunicationService": "communicationservice.service",
            "DriveClient": "pydantic_ai_integration.integrations.google_workspace.drive_client",
            "GmailClient": "pydantic_ai_integration.integrations.google_workspace.gmail_client",
            "SheetsClient": "pydantic_ai_integration.integrations.google_workspace.sheets_client",
            "RequestHubService": "coreservice.request_hub_service",
        }
        
        module_path = service_module_map.get(service_name)
        if not module_path:
            raise ValueError(f"Unknown service: {service_name}. Add to service_module_map.")
        
        # Import module
        logger.debug(f"Importing module: {module_path}")
        module = importlib.import_module(module_path)
        
        # Get service class
        service_class = getattr(module, service_name)
        logger.debug(f"Found service class: {service_class}")
        
        # Instantiate (simple - no DI for now)
        service_instance = service_class()
        logger.info(f"✓ Successfully instantiated {service_name}")
        
        return service_instance
        
    except ImportError as e:
        logger.error(f"Failed to import service module '{service_name}': {e}", exc_info=True)
        raise ValueError(f"Service '{service_name}' module not found: {e}")
    except AttributeError as e:
        logger.error(f"Service class '{service_name}' not found in module: {e}", exc_info=True)
        raise ValueError(f"Service class '{service_name}' not found: {e}")
    except Exception as e:
        logger.error(f"Failed to instantiate service '{service_name}': {e}", exc_info=True)
        raise ValueError(f"Failed to instantiate '{service_name}': {e}")


def _build_request_dto(service_name: str, method_name: str, method_params: Dict[str, Any], ctx):
    """
    Build Request DTO from method parameters.
    
    Services expect Request objects (BaseRequest[PayloadT]), not raw params.
    This function wraps params in the appropriate Request DTO.
    
    Args:
        service_name: Service name for model lookup
        method_name: Method name for model lookup
        method_params: Raw parameters from tool invocation
        ctx: MDSContext for user_id, session_id, casefile_id
        
    Returns:
        Instantiated Request DTO object
        
    Raises:
        ValueError: If Request model cannot be found or instantiated
    """
    from . import method_registry
    import importlib
    import json
    
    logger.info(f"┌─ BUILDING REQUEST DTO ──────────────────")
    logger.info(f"│ Service: {service_name}")
    logger.info(f"│ Method: {method_name}")
    logger.info(f"│ Method params count: {len(method_params)}")
    logger.info(f"└────────────────────────────────────────")
    
    try:
        # Get method definition
        compound_key = f"{service_name}.{method_name}"
        method_def = method_registry.get_method_definition(compound_key)
        
        if not method_def:
            raise ValueError(f"Method '{compound_key}' not found in MANAGED_METHODS registry")
        
        # Get Request model class
        request_model_class = method_def.request_model_class
        if not request_model_class:
            raise ValueError(f"Method '{compound_key}' has no request_model_class")
        
        logger.info(f"✓ Request DTO class found: {request_model_class.__name__}")
        
        # Build Request DTO with context + payload
        # Request DTOs follow pattern: BaseRequest[PayloadT]
        # They expect: user_id, session_id, casefile_id, payload
        
        logger.info(f"┌─ INJECTING CONTEXT ─────────────────────")
        logger.info(f"│ user_id: {ctx.user_id}")
        logger.info(f"│ session_id: {ctx.session_id}")
        logger.info(f"│ casefile_id: {ctx.casefile_id}")
        logger.info(f"│ payload: {json.dumps(method_params, default=str)}")
        logger.info(f"└────────────────────────────────────────")
        
        request_dto = request_model_class(
            user_id=ctx.user_id,
            session_id=ctx.session_id,
            casefile_id=ctx.casefile_id,
            payload=method_params  # Pydantic will validate and build PayloadT
        )
        
        logger.info(f"✓ Successfully built {request_model_class.__name__}")
        
        return request_dto
        
    except Exception as e:
        logger.error(f"Failed to build Request DTO for {compound_key}: {e}", exc_info=True)
        raise ValueError(f"Failed to build Request DTO: {e}")


def register_tools_from_yaml(yaml_path: Optional[str] = None) -> None:
    """
    Load and register tools from YAML method tool definitions.

    This function reads YAML files from config/methodtools_v1/ and creates
    actual tool registrations using @register_mds_tool decorator.

    Args:
        yaml_path: Optional path to YAML directory. Defaults to config/methodtools_v1/

    Example:
        >>> # In main.py or service initialization
        >>> from src.pydantic_ai_integration.tool_decorator import register_tools_from_yaml
        >>> register_tools_from_yaml()
    """
    from pathlib import Path
    import yaml
    from typing import Literal

    from pydantic import BaseModel, Field

    if yaml_path is None:
        # Auto-detect from module location
        module_dir = Path(__file__).parent.parent.parent
        yaml_path = module_dir / "config" / "methodtools_v1"

    yaml_dir = Path(yaml_path)
    if not yaml_dir.exists():
        logger.warning(f"Method tools directory not found: {yaml_dir}")
        return

    registered_count = 0

    # Load all YAML files in the directory
    for yaml_file in yaml_dir.glob("*.yaml"):
        try:
            with open(yaml_file, encoding='utf-8') as f:
                tool_config = yaml.safe_load(f)

            # Extract tool configuration
            tool_name = tool_config['name']
            description = tool_config['description']
            category = tool_config.get('category', 'general')
            version = tool_config.get('version', '1.0.0')
            tags = tool_config.get('tags', [])

            # Get method reference for routing
            method_ref = tool_config.get('method_reference', {})
            service_name = method_ref.get('service', '')
            method_name_part = method_ref.get('method', '')
            method_name = f"{service_name}.{method_name_part}".strip('.')
            if not method_name or method_name == '.':
                method_name = None

            # Ensure tool name is unique by including service name if there are duplicates
            # Check if this tool name already exists
            if tool_name in MANAGED_TOOLS:
                # Make it unique by prefixing with service name
                unique_tool_name = f"{service_name.lower()}_{tool_name}"
                logger.warning(f"Tool name '{tool_name}' already exists, using '{unique_tool_name}' instead")
                tool_name = unique_tool_name

            # Create enhanced parameter model with execution metadata
            # This allows tools to actually execute instead of returning placeholders

            # Build the class attributes
            class_attrs = {
                '__module__': __name__,
                'model_config': {'extra': 'allow'}
            }

            # Build annotations dict
            annotations = {}

            # Add tool parameters from YAML
            for param in tool_config.get('tool_params', []):
                param_type = _yaml_type_to_python_type(param['type'])
                field_kwargs = {'description': param.get('description', '')}

                # Add constraints
                if 'default' in param:
                    field_kwargs['default'] = param['default']
                elif param.get('required', False):
                    pass  # No default for required fields
                else:
                    field_kwargs['default'] = None

                if 'min_value' in param:
                    field_kwargs['ge'] = param['min_value']
                if 'max_value' in param:
                    field_kwargs['le'] = param['max_value']
                if 'min_length' in param:
                    field_kwargs['min_length'] = param['min_length']
                if 'max_length' in param:
                    field_kwargs['max_length'] = param['max_length']

                # Add to annotations and class attrs
                annotations[param['name']] = param_type
                class_attrs[param['name']] = Field(**field_kwargs)

            # Add special execution fields
            annotations.update({
                'execution_type': str,
                'method_name': str,
                'parameter_mapping': dict,
                'implementation_config': dict,
                'dry_run': bool,
                'timeout_seconds': int,
            })

            class_attrs.update({
                'execution_type': Field(default="method_wrapper", description="How the tool should execute"),
                'method_name': Field(default=method_name or "", description="Method to execute"),
                'parameter_mapping': Field(default_factory=dict, description="How to map parameters to method calls"),
                'implementation_config': Field(default_factory=dict, description="Additional implementation configuration"),
                'dry_run': Field(default=False, description="Preview mode without actual execution"),
                'timeout_seconds': Field(default=30, description="Maximum execution time in seconds"),
            })

            # Set default values for execution fields based on YAML
            implementation = tool_config.get('implementation', {})
            class_attrs['execution_type'] = Field(default=implementation.get('type', 'method_wrapper'), description="How the tool should execute")
            class_attrs['method_name'] = Field(default=method_name, description="Method to execute")
            class_attrs['parameter_mapping'] = Field(default=implementation.get('method_wrapper', {}).get('parameter_mapping', {}), description="How to map parameters to method calls")
            class_attrs['implementation_config'] = Field(default=implementation, description="Additional implementation configuration")

            # Create the class
            class_attrs['__annotations__'] = annotations
            EnhancedToolParams = type(
                f"{tool_name.title().replace('_', '')}Params",
                (BaseModel,),
                class_attrs
            )

            # Create the tool function that actually executes based on execution metadata
            async def tool_function(ctx, tool_name=tool_name, method_name=method_name, method_ref_copy=method_ref, **kwargs):
                """
                Enhanced tool function that executes based on YAML configuration.

                This function now ACTUALLY CALLS SERVICE METHODS instead of returning placeholders.

                Flow:
                1. Extract execution metadata and parameters
                2. Separate method_params from tool_params (orchestration)
                3. Instantiate service
                4. Build Request DTO
                5. Call service method
                6. Return result
                """

                logger.info(f"═══ Tool Execution Start: {tool_name} ═══")
                logger.info(f"┌─ EXECUTION CONTEXT ─────────────────────")
                logger.info(f"│ User ID: {ctx.user_id}")
                logger.info(f"│ Session ID: {ctx.session_id}")
                logger.info(f"│ Casefile ID: {ctx.casefile_id}")
                logger.info(f"└────────────────────────────────────────")
                logger.info(f"┌─ RAW INPUT PARAMETERS ──────────────────")
                import json
                for key, value in kwargs.items():
                    logger.info(f"│ {key}: {json.dumps(value) if not isinstance(value, str) else value}")
                logger.info(f"└────────────────────────────────────────")

                # Extract execution metadata from parameters
                execution_type = kwargs.get('execution_type', 'method_wrapper')
                method_name_param = kwargs.get('method_name', method_name)
                parameter_mapping = kwargs.get('parameter_mapping', {})
                dry_run = kwargs.get('dry_run', False)
                timeout_seconds = kwargs.get('timeout_seconds', 30)

                # DRY RUN: Preview execution without calling services
                if dry_run:
                    logger.info(f"[DRY RUN] Would execute {tool_name} via {execution_type}")
                    logger.debug(f"[DRY RUN] method_name: {method_name_param}")
                    logger.debug(f"[DRY RUN] parameters: {kwargs}")
                    return {
                        "tool_name": tool_name,
                        "method_name": method_name_param,
                        "execution_type": execution_type,
                        "status": "dry_run",
                        "parameters": kwargs,
                        "message": f"Dry run: would execute {tool_name} via {execution_type}"
                    }

                # Execute based on type
                if execution_type == 'method_wrapper':
                    logger.info(f"Execution type: method_wrapper for {method_name_param}")
                    
                    try:
                        # STEP 1: Map parameters according to YAML configuration
                        method_params = {}
                        tool_params = {}

                        # Separate parameters based on mapping
                        method_param_names = parameter_mapping.get('method_params', [])
                        tool_param_names = parameter_mapping.get('tool_params', [])

                        logger.debug(f"Parameter mapping config:")
                        logger.debug(f"  - method_params expected: {method_param_names}")
                        logger.debug(f"  - tool_params expected: {tool_param_names}")

                        for param_name, param_value in kwargs.items():
                            # Skip execution metadata params
                            if param_name in ('execution_type', 'method_name', 'parameter_mapping', 
                                            'implementation_config', 'dry_run', 'timeout_seconds'):
                                tool_params[param_name] = param_value
                                continue
                            
                            if param_name in method_param_names:
                                method_params[param_name] = param_value
                                logger.debug(f"  → method_param: {param_name} = {param_value}")
                            elif param_name in tool_param_names:
                                tool_params[param_name] = param_value
                                logger.debug(f"  → tool_param: {param_name} = {param_value}")
                            else:
                                # Default: assume it's a method parameter if not in tool_params list
                                method_params[param_name] = param_value
                                logger.debug(f"  → method_param (default): {param_name} = {param_value}")

                        logger.info(f"┌─ PARAMETER SEPARATION COMPLETE ─────────")
                        logger.info(f"│ METHOD PARAMETERS (for service method):")
                        for key, value in method_params.items():
                            logger.info(f"│   {key}: {json.dumps(value) if not isinstance(value, str) else value}")
                        logger.info(f"│")
                        logger.info(f"│ TOOL PARAMETERS (orchestration metadata):")
                        for key, value in tool_params.items():
                            logger.info(f"│   {key}: {json.dumps(value) if not isinstance(value, str) else value}")
                        logger.info(f"└────────────────────────────────────────")

                        # STEP 2: Parse service and method name
                        if '.' in method_name_param:
                            service_name, method_part = method_name_param.split('.', 1)
                        else:
                            # Fallback: try to infer from YAML method_reference
                            service_name = method_ref_copy.get('service', '')
                            method_part = method_name_param
                        
                        logger.info(f"Service: {service_name}, Method: {method_part}")

                        # STEP 3: Instantiate service
                        try:
                            service_instance = _instantiate_service(service_name, method_part)
                        except ValueError as e:
                            logger.error(f"Service instantiation failed: {e}")
                            return {
                                "tool_name": tool_name,
                                "status": "error",
                                "error_type": "ServiceInstantiationError",
                                "error_message": str(e),
                                "method_name": method_name_param
                            }

                        # STEP 4: Build Request DTO
                        try:
                            request_dto = _build_request_dto(
                                service_name=service_name,
                                method_name=method_part,
                                method_params=method_params,
                                ctx=ctx
                            )
                            
                            # Log Request DTO structure
                            logger.info(f"┌─ REQUEST DTO STRUCTURE ─────────────────")
                            if hasattr(request_dto, 'model_dump'):
                                dto_dict = request_dto.model_dump()
                                logger.info(f"│ DTO Type: {type(request_dto).__name__}")
                                for key, value in dto_dict.items():
                                    if key == 'payload' and isinstance(value, dict):
                                        logger.info(f"│ {key}:")
                                        for pk, pv in value.items():
                                            logger.info(f"│   {pk}: {json.dumps(pv) if not isinstance(pv, str) else pv}")
                                    else:
                                        logger.info(f"│ {key}: {json.dumps(value) if not isinstance(value, str) else value}")
                            logger.info(f"└────────────────────────────────────────")
                        except ValueError as e:
                            logger.error(f"Request DTO build failed: {e}")
                            return {
                                "tool_name": tool_name,
                                "status": "error",
                                "error_type": "RequestDTOBuildError",
                                "error_message": str(e),
                                "method_name": method_name_param,
                                "method_params": method_params
                            }

                        # STEP 5: Call service method
                        try:
                            method_callable = getattr(service_instance, method_part)
                            logger.info(f"Calling {service_name}.{method_part}...")
                            
                            import asyncio
                            from datetime import datetime
                            start_time = datetime.now()
                            
                            # Execute with timeout
                            result = await asyncio.wait_for(
                                method_callable(request_dto),
                                timeout=timeout_seconds
                            )
                            
                            duration_ms = int((datetime.now() - start_time).total_seconds() * 1000)
                            logger.info(f"✓ Method executed successfully in {duration_ms}ms")

                            # STEP 6: Extract result payload
                            # Services return BaseResponse[PayloadT] objects
                            if hasattr(result, 'model_dump'):
                                result_dict = result.model_dump()
                            elif isinstance(result, dict):
                                result_dict = result
                            else:
                                result_dict = {"value": str(result)}
                            
                            # Log service response structure
                            logger.info(f"┌─ SERVICE RESPONSE ──────────────────────")
                            logger.info(f"│ Response Type: {type(result).__name__}")
                            for key, value in result_dict.items():
                                if key == 'payload' and isinstance(value, dict):
                                    logger.info(f"│ {key}:")
                                    for pk, pv in value.items():
                                        val_str = json.dumps(pv) if not isinstance(pv, (str, int, float, bool, type(None))) else str(pv)
                                        logger.info(f"│   {pk}: {val_str}")
                                elif key == 'audit' and isinstance(value, dict):
                                    logger.info(f"│ {key}: [audit data - {len(value)} fields]")
                                else:
                                    val_str = json.dumps(value) if not isinstance(value, (str, int, float, bool, type(None))) else str(value)
                                    logger.info(f"│ {key}: {val_str}")
                            logger.info(f"└────────────────────────────────────────")
                            
                            logger.info(f"═══ Tool Execution Complete: {tool_name} ═══")
                            
                            return {
                                "tool_name": tool_name,
                                "method_name": method_name_param,
                                "execution_type": execution_type,
                                "status": "success",
                                "result": result_dict,
                                "duration_ms": duration_ms,
                                "tool_params": tool_params,
                                "message": f"Successfully executed {tool_name}"
                            }

                        except asyncio.TimeoutError:
                            logger.error(f"Method execution timed out after {timeout_seconds}s")
                            return {
                                "tool_name": tool_name,
                                "status": "error",
                                "error_type": "TimeoutError",
                                "error_message": f"Method execution exceeded timeout of {timeout_seconds}s",
                                "method_name": method_name_param
                            }
                        except AttributeError as e:
                            logger.error(f"Method '{method_part}' not found on {service_name}: {e}")
                            return {
                                "tool_name": tool_name,
                                "status": "error",
                                "error_type": "MethodNotFoundError",
                                "error_message": f"Method '{method_part}' not found on service '{service_name}'",
                                "method_name": method_name_param
                            }
                        except Exception as e:
                            logger.error(f"Method execution failed: {e}", exc_info=True)
                            return {
                                "tool_name": tool_name,
                                "status": "error",
                                "error_type": type(e).__name__,
                                "error_message": str(e),
                                "method_name": method_name_param
                            }

                    except Exception as e:
                        logger.error(f"Tool execution failed: {e}", exc_info=True)
                        return {
                            "tool_name": tool_name,
                            "status": "error",
                            "error_type": "ToolExecutionError",
                            "error_message": str(e),
                            "method_name": method_name_param
                        }

                else:
                    # Placeholder for other execution types
                    logger.warning(f"Execution type '{execution_type}' not implemented")
                    return {
                        "tool_name": tool_name,
                        "execution_type": execution_type,
                        "status": "not_implemented",
                        "message": f"Execution type '{execution_type}' not yet implemented"
                    }

            # Register the tool with enhanced parameter model
            register_mds_tool(
                name=tool_name,
                params_model=EnhancedToolParams,
                description=description,
                category=category,
                version=version,
                tags=tags,
                method_name=method_name
            )(tool_function)

            registered_count += 1
            logger.info(f"Registered YAML tool: {tool_name} -> {method_name}")

        except Exception as e:
            logger.error(f"Failed to register tool from {yaml_file.name}: {e}")
            continue

    logger.info(f"Registered {registered_count} tools from YAML method tool definitions")


def _yaml_type_to_python_type(yaml_type: str) -> type:
    """Convert YAML type string to Python type."""
    type_map = {
        'string': str,
        'integer': int,
        'float': float,
        'boolean': bool,
        'array': list,
        'object': dict
    }
    return type_map.get(yaml_type, str)

