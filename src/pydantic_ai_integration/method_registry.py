"""
Method registry - parallel to tool_decorator.py for service methods.

Global MANAGED_METHODS registry with discovery APIs.
Used by ToolFactory to validate api_call.method_name exists.

ARCHITECTURE:
- MANAGED_METHODS: Global Dict[str, ManagedMethodDefinition]
- Discovery APIs: 11 methods matching tool_decorator.py
- Classification-based queries: domain, subdomain, capability, etc.
- Parameter extraction: Auto-extract from Pydantic payload models
- Future: @register_service_method decorator (Phase 10)
"""

import logging
from collections import defaultdict
from typing import Any, Dict, List, Optional, Type, get_args, get_origin, get_type_hints

from pydantic import BaseModel
from pydantic.fields import FieldInfo

from .method_definition import ManagedMethodDefinition, MethodParameterDef

logger = logging.getLogger(__name__)

# Global registry - SINGLE SOURCE OF TRUTH for methods
# Parallel to MANAGED_TOOLS in tool_decorator.py
# Format: {method_name: ManagedMethodDefinition}
MANAGED_METHODS: Dict[str, ManagedMethodDefinition] = {}


# ==============================================================================
# PARAMETER EXTRACTION (DTO → MethodParameterDef)
# ==============================================================================

def _format_type_annotation(annotation: Any) -> str:
    """
    Format type annotation as string for MethodParameterDef.
    
    Handles:
    - Simple types: str, int, bool
    - Generic types: List[str], Dict[str, Any], Optional[str]
    - Union types: Union[str, int]
    
    Args:
        annotation: Type annotation from Pydantic field
        
    Returns:
        String representation like "str", "List[str]", "Optional[int]"
    """
    origin = get_origin(annotation)
    
    # Simple type (no generic)
    if origin is None:
        return annotation.__name__ if hasattr(annotation, '__name__') else str(annotation)
    
    # Generic type (List, Dict, Optional, Union)
    args = get_args(annotation)
    if args:
        args_str = ', '.join(_format_type_annotation(arg) for arg in args)
        origin_name = origin.__name__ if hasattr(origin, '__name__') else str(origin)
        return f"{origin_name}[{args_str}]"
    
    return origin.__name__ if hasattr(origin, '__name__') else str(origin)


def extract_parameters_from_payload(payload_class: Type[BaseModel]) -> List[MethodParameterDef]:
    """
    Extract parameter definitions from Pydantic payload model.
    
    This is the FOUNDATION of DTO inheritance - parameters are defined once
    in the Pydantic model and automatically extracted to method/tool definitions.
    
    Extracts:
    - Field name, type, required status
    - Description from Field(description=...)
    - Default value from Field(default=...)
    - Validation constraints: min_length, max_length, ge, le, pattern
    
    Args:
        payload_class: Pydantic model class (e.g., CreateCasefilePayload)
        
    Returns:
        List of MethodParameterDef with all metadata
        
    Example:
        >>> class CreateCasefilePayload(BaseModel):
        ...     title: str = Field(..., min_length=1, max_length=200)
        ...     tags: List[str] = Field(default_factory=list)
        >>> params = extract_parameters_from_payload(CreateCasefilePayload)
        >>> params[0].name  # "title"
        >>> params[0].required  # True
        >>> params[0].max_length  # 200
    """
    params = []
    
    # Use Pydantic v2 API
    for field_name, field_info in payload_class.model_fields.items():
        # Get type annotation
        annotation = field_info.annotation
        type_str = _format_type_annotation(annotation)
        
        # Determine if required
        required = field_info.is_required()
        
        # Get description
        description = field_info.description or ""
        
        # Get default value
        default_value = None if required else (
            field_info.default if field_info.default is not None 
            else field_info.default_factory() if field_info.default_factory else None
        )
        
        # Extract validation constraints from field metadata
        min_value = None
        max_value = None
        min_length = None
        max_length = None
        pattern = None
        
        # Check field metadata for constraints
        if hasattr(field_info, 'metadata'):
            for constraint in field_info.metadata:
                constraint_type = type(constraint).__name__
                if constraint_type == 'Ge':  # Greater than or equal
                    min_value = constraint.ge if hasattr(constraint, 'ge') else None
                elif constraint_type == 'Le':  # Less than or equal
                    max_value = constraint.le if hasattr(constraint, 'le') else None
                elif constraint_type == 'MinLen':
                    min_length = constraint.min_length if hasattr(constraint, 'min_length') else None
                elif constraint_type == 'MaxLen':
                    max_length = constraint.max_length if hasattr(constraint, 'max_length') else None
                elif constraint_type == 'Pattern':
                    pattern = constraint.pattern if hasattr(constraint, 'pattern') else None
        
        # Also check json_schema_extra for constraints (Pydantic v2)
        if hasattr(field_info, 'json_schema_extra'):
            extra = field_info.json_schema_extra or {}
            if isinstance(extra, dict):
                min_value = min_value or extra.get('ge') or extra.get('min_value')
                max_value = max_value or extra.get('le') or extra.get('max_value')
                min_length = min_length or extra.get('min_length')
                max_length = max_length or extra.get('max_length')
                pattern = pattern or extra.get('pattern')
        
        param = MethodParameterDef(
            name=field_name,
            param_type=type_str,
            required=required,
            description=description,
            default_value=default_value,
            min_value=min_value,
            max_value=max_value,
            min_length=min_length,
            max_length=max_length,
            pattern=pattern
        )
        params.append(param)
    
    return params


def extract_parameters_from_request_model(request_model_class: Type[BaseModel]) -> List[MethodParameterDef]:
    """
    Extract parameters from Request DTO by inspecting its payload type or fields.
    
    Handles two patterns:
    1. R-A-R pattern: BaseRequest[PayloadT] with 'payload' field (CasefileService, ToolSessionService)
    2. Direct parameters: All fields are parameters (Google Workspace clients)
    
    Args:
        request_model_class: Request DTO class (e.g., CreateCasefileRequest, GmailListMessagesRequest)
        
    Returns:
        List of MethodParameterDef extracted from payload or model fields
        
    Example:
        >>> # R-A-R pattern
        >>> params = extract_parameters_from_request_model(CreateCasefileRequest)
        >>> # Extracts from CreateCasefilePayload automatically
        >>> 
        >>> # Direct parameters
        >>> params = extract_parameters_from_request_model(GmailListMessagesRequest)
        >>> # Extracts from GmailListMessagesRequest fields directly
    """
    # Check for R-A-R pattern (has 'payload' field)
    if 'payload' in request_model_class.model_fields:
        payload_field = request_model_class.model_fields['payload']
        payload_type = payload_field.annotation
        
        # Handle Optional/Union types
        origin = get_origin(payload_type)
        if origin:
            args = get_args(payload_type)
            # For Optional[X] or Union[X, None], get first non-None type
            if args:
                payload_class = None
                for arg in args:
                    if arg is not type(None) and hasattr(arg, 'model_fields'):
                        payload_class = arg
                        break
                if not payload_class:
                    payload_class = args[0]
            else:
                payload_class = payload_type
        else:
            payload_class = payload_type
        
        # Validate it's a Pydantic model
        if not hasattr(payload_class, 'model_fields'):
            logger.warning(
                f"Could not determine payload class for {request_model_class.__name__}, "
                f"got {payload_class}"
            )
            return []
        
        # Extract from payload class
        return extract_parameters_from_payload(payload_class)
    
    # Direct parameter model (no payload field) - extract from model itself
    logger.debug(
        f"Request model {request_model_class.__name__} has no 'payload' field, "
        "extracting parameters directly from model fields"
    )
    return extract_parameters_from_payload(request_model_class)


# ==============================================================================
# BASIC DISCOVERY (4 methods)
# ==============================================================================

def get_registered_methods() -> Dict[str, ManagedMethodDefinition]:
    """
    Returns all registered methods.
    Parallel to tool_decorator.get_registered_tools().
    """
    return MANAGED_METHODS.copy()


def get_method_names() -> List[str]:
    """
    Returns list of all method names.
    Parallel to tool_decorator.get_tool_names().
    """
    return list(MANAGED_METHODS.keys())


def validate_method_exists(method_name: str) -> bool:
    """
    Check if method is registered.
    Used by ToolFactory to validate api_call.method_name.
    Parallel to tool_decorator.validate_tool_exists().
    """
    return method_name in MANAGED_METHODS


def get_method_definition(method_name: str) -> Optional[ManagedMethodDefinition]:
    """
    Get method definition by name.
    Returns None if not found.
    Parallel to tool_decorator.get_tool_definition().
    """
    return MANAGED_METHODS.get(method_name)


# ==============================================================================
# COMPOUND KEY HELPERS (for ServiceName.method_name format)
# ==============================================================================

def get_compound_key(service_name: str, method_name: str) -> str:
    """
    Generate compound key from service and method names.
    
    Args:
        service_name: Service class name (e.g., "ToolSessionService")
        method_name: Method name (e.g., "create_session")
        
    Returns:
        Compound key (e.g., "ToolSessionService.create_session")
    """
    return f"{service_name}.{method_name}"


def validate_method_exists_by_compound_key(service_name: str, method_name: str) -> bool:
    """
    Check if method exists using compound key format.
    
    Args:
        service_name: Service class name
        method_name: Method name
        
    Returns:
        True if method exists with compound key
    """
    compound_key = get_compound_key(service_name, method_name)
    return compound_key in MANAGED_METHODS


def get_method_definition_by_compound_key(service_name: str, method_name: str) -> Optional[ManagedMethodDefinition]:
    """
    Get method definition using compound key format.
    
    Args:
        service_name: Service class name
        method_name: Method name
        
    Returns:
        Method definition or None if not found
    """
    compound_key = get_compound_key(service_name, method_name)
    return MANAGED_METHODS.get(compound_key)


def find_methods_by_method_name(method_name: str) -> List[ManagedMethodDefinition]:
    """
    Find all methods with a given method name across all services.
    Useful when method names are duplicated across services.
    
    Args:
        method_name: Method name to search for
        
    Returns:
        List of method definitions with matching method names
    """
    return [
        method_def for key, method_def in MANAGED_METHODS.items()
        if key.endswith(f".{method_name}")
    ]


def get_method_definition_by_method_name(method_name: str) -> Optional[ManagedMethodDefinition]:
    """
    Get method definition by method name only.
    Returns the first match if multiple services have the same method name.
    Use find_methods_by_method_name() if you need all matches.
    
    Args:
        method_name: Method name (without service prefix)
        
    Returns:
        First matching method definition or None
    """
    matches = find_methods_by_method_name(method_name)
    return matches[0] if matches else None


def get_method_parameters(method_name: str) -> List[MethodParameterDef]:
    """
    Get parameters for a method by extracting them on-demand from request model.
    
    Args:
        method_name: Method name to look up (can be compound key or simple name)
        
    Returns:
        List of MethodParameterDef extracted from the request model payload
        
    Example:
        >>> params = get_method_parameters("ToolSessionService.create_session")
        >>> # Returns parameters extracted fresh from CreateSessionRequest
    """
    # Try compound key first, then fall back to method name lookup
    method_def = MANAGED_METHODS.get(method_name)
    if not method_def:
        method_def = get_method_definition_by_method_name(method_name)
    
    if not method_def or not method_def.request_model_class:
        return []
    
    return extract_parameters_from_request_model(method_def.request_model_class)


# ==============================================================================
# CLASSIFICATION DISCOVERY (6 methods)
# ==============================================================================

def get_methods_by_domain(domain: str) -> List[ManagedMethodDefinition]:
    """
    Get all methods in a domain.
    Parallel to tool_decorator.get_tools_by_domain().
    
    Args:
        domain: workspace, communication, automation
    """
    return [m for m in MANAGED_METHODS.values() if m.domain == domain]


def get_methods_by_subdomain(domain: str, subdomain: str) -> List[ManagedMethodDefinition]:
    """
    Get methods by domain + subdomain.
    Parallel to tool_decorator.get_tools_by_subdomain().
    
    Args:
        domain: workspace, communication, automation
        subdomain: casefile, gmail, tool_session, etc.
    """
    return [
        m for m in MANAGED_METHODS.values()
        if m.domain == domain and m.subdomain == subdomain
    ]


def get_methods_by_capability(capability: str) -> List[ManagedMethodDefinition]:
    """
    Get methods by capability.
    Parallel to tool_decorator.get_tools_by_capability().
    
    Args:
        capability: create, read, update, delete, process, search
    """
    return [m for m in MANAGED_METHODS.values() if m.capability == capability]


def get_methods_by_complexity(complexity: str) -> List[ManagedMethodDefinition]:
    """
    Get methods by complexity.
    Parallel to tool_decorator.get_tools_by_complexity().
    
    Args:
        complexity: atomic, composite, pipeline
    """
    return [m for m in MANAGED_METHODS.values() if m.complexity == complexity]


def get_methods_by_maturity(maturity: str) -> List[ManagedMethodDefinition]:
    """
    Get methods by maturity level.
    Parallel to tool_decorator.get_tools_by_maturity().
    
    Args:
        maturity: stable, beta, alpha, experimental
    """
    return [m for m in MANAGED_METHODS.values() if m.maturity == maturity]


def get_methods_by_integration_tier(tier: str) -> List[ManagedMethodDefinition]:
    """
    Get methods by integration tier.
    Parallel to tool_decorator.get_tools_by_integration_tier().
    
    Args:
        tier: internal, external, hybrid
    """
    return [m for m in MANAGED_METHODS.values() if m.integration_tier == tier]


# ==============================================================================
# UTILITY METHODS (2 methods)
# ==============================================================================

def get_hierarchical_method_path(method_name: str) -> Optional[str]:
    """
    Get hierarchical path for method.
    Parallel to tool_decorator.get_hierarchical_tool_path().
    
    Returns: {domain}.{subdomain}.{method_name}
    Example: workspace.casefile.create_casefile
    """
    method_def = get_method_definition(method_name)
    if method_def:
        return method_def.get_hierarchical_path()
    return None


def get_classification_summary() -> Dict[str, Any]:
    """
    Get statistics on method classification.
    Parallel to tool_decorator.get_classification_summary().
    
    Returns:
        Dict with counts by domain, capability, complexity, maturity, integration_tier
    """
    summary = {
        "total_methods": len(MANAGED_METHODS),
        "by_domain": defaultdict(int),
        "by_subdomain": defaultdict(int),
        "by_capability": defaultdict(int),
        "by_complexity": defaultdict(int),
        "by_maturity": defaultdict(int),
        "by_integration_tier": defaultdict(int),
        "by_service": defaultdict(int)
    }
    
    for method_def in MANAGED_METHODS.values():
        summary["by_domain"][method_def.domain] += 1
        summary["by_subdomain"][method_def.subdomain] += 1
        summary["by_capability"][method_def.capability] += 1
        summary["by_complexity"][method_def.complexity] += 1
        summary["by_maturity"][method_def.maturity] += 1
        summary["by_integration_tier"][method_def.integration_tier] += 1
        summary["by_service"][method_def.implementation_class] += 1
    
    # Convert defaultdict to regular dict for JSON serialization
    return {
        "total_methods": summary["total_methods"],
        "by_domain": dict(summary["by_domain"]),
        "by_subdomain": dict(summary["by_subdomain"]),
        "by_capability": dict(summary["by_capability"]),
        "by_complexity": dict(summary["by_complexity"]),
        "by_maturity": dict(summary["by_maturity"]),
        "by_integration_tier": dict(summary["by_integration_tier"]),
        "by_service": dict(summary["by_service"])
    }


# ==============================================================================
# SERVICE-SPECIFIC QUERIES (bonus)
# ==============================================================================

def get_methods_by_service(service_name: str) -> List[ManagedMethodDefinition]:
    """
    Get all methods from a specific service.
    Useful for service-level documentation.
    
    Args:
        service_name: CasefileService, ToolSessionService, etc.
    """
    return [m for m in MANAGED_METHODS.values() if m.implementation_class == service_name]


# ==============================================================================
# MANUAL REGISTRATION (Phase 10 will add decorator)
# ==============================================================================

def register_method(method_name: str, method_def: ManagedMethodDefinition) -> None:
    """
    Register a method definition.
    
    Args:
        method_name: Unique method identifier
        method_def: Complete ManagedMethodDefinition instance
    """
    if method_name in MANAGED_METHODS:
        logger.warning(f"Method '{method_name}' already registered, overwriting")
    
    MANAGED_METHODS[method_name] = method_def
    logger.info(f"Registered method: {method_name} ({method_def.implementation_class})")


def unregister_method(method_name: str) -> bool:
    """
    Remove method from registry.
    Returns True if method was found and removed.
    """
    if method_name in MANAGED_METHODS:
        del MANAGED_METHODS[method_name]
        logger.info(f"Unregistered method: {method_name}")
        return True
    return False


# ==============================================================================
# EXPORT METHODS (for YAML generation)
# ==============================================================================

def export_methods_to_yaml() -> List[Dict[str, Any]]:
    """
    Export all methods in YAML-compatible format.
    Used for methods_inventory_v1.yaml generation (Phase 9).
    
    Returns:
        List of method definitions as dicts
    """
    return [
        method_def.to_yaml_compatible()
        for method_def in MANAGED_METHODS.values()
    ]


def export_methods_by_service() -> Dict[str, List[Dict[str, Any]]]:
    """
    Export methods grouped by service.
    Useful for service-specific documentation.
    """
    by_service = defaultdict(list)
    for method_def in MANAGED_METHODS.values():
        service = method_def.implementation_class
        by_service[service].append(method_def.to_yaml_compatible())
    return dict(by_service)


def get_deprecated_methods() -> List[Dict[str, Any]]:
    """
    DEPRECATED FUNCTION - No longer supported.
    Deprecation metadata removed in slim refactor.
    Returns empty list for backwards compatibility.
    """
    logger.warning("get_deprecated_methods() called but deprecation tracking removed")
    return []


def validate_yaml_compatibility(yaml_path: str) -> Dict[str, Any]:
    """
    Validate compatibility between YAML inventory and current registry code.
    
    Checks:
    - YAML version format (semver)
    - Required fields present
    - Minimum version requirements met
    
    Args:
        yaml_path: Path to methods_inventory_vX.yaml
        
    Returns:
        Dict with validation results:
        {
            "compatible": bool,
            "issues": List[str],
            "yaml_version": str,
            "registry_version": str
        }
        
    Example:
        >>> result = validate_yaml_compatibility("config/methods_inventory_v2.yaml")
        >>> if not result["compatible"]:
        ...     print(f"Compatibility issues: {result['issues']}")
    """
    from pathlib import Path

    import yaml
    
    issues = []
    
    # Load YAML
    try:
        yaml_file = Path(yaml_path)
        if not yaml_file.exists():
            return {
                "compatible": False,
                "issues": [f"YAML file not found: {yaml_path}"],
                "yaml_version": "unknown",
                "registry_version": "1.0.0"
            }
        
        with open(yaml_file, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        yaml_version = data.get('version', 'unknown')
        
        # Check required fields
        required_fields = ['version', 'schema_version', 'services']
        for field in required_fields:
            if field not in data:
                issues.append(f"Missing required field: {field}")
        
        # Check version format (semver)
        if yaml_version != 'unknown':
            import re
            if not re.match(r'^\d+\.\d+\.\d+$', yaml_version):
                issues.append(f"Invalid version format: {yaml_version} (expected semver)")
        
        # Check compatibility metadata
        if 'compatibility' in data:
            compat = data['compatibility']
            min_registry = compat.get('minimum_registry_version', '1.0.0')
            
            # Simple version comparison (assumes 1.x.x format)
            # In production, use packaging.version
            current_version = "1.0.0"
            if min_registry > current_version:
                issues.append(
                    f"YAML requires registry v{min_registry}, "
                    f"but current version is v{current_version}"
                )
        
        compatible = len(issues) == 0
        
        return {
            "compatible": compatible,
            "issues": issues,
            "yaml_version": yaml_version,
            "registry_version": "1.0.0"
        }
        
    except Exception as e:
        return {
            "compatible": False,
            "issues": [f"Error loading YAML: {str(e)}"],
            "yaml_version": "unknown",
            "registry_version": "1.0.0"
        }
