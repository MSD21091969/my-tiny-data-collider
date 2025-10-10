"""
Service method registration decorator - parallel to tool_decorator.py.

This module provides the @register_service_method decorator that:
1. Registers service methods with MANAGED_METHODS registry (for execution)
2. Stores Pydantic request/response models (for validation)
3. Makes methods discoverable via API (for documentation)
4. Enables type safety (for compile-time checks)

ARCHITECTURE NOTES:
- MANAGED_METHODS is the global registry (single source of truth)
- Decorator extracts metadata from method signature and Pydantic models
- Service layer continues normal execution (no wrapper needed)
- API layer queries registry for discovery
- All metadata/business logic lives in one place

DIFFERENCE FROM TOOL DECORATOR:
- Tools use @register_mds_tool and wrap execution with validation
- Methods use @register_service_method and only register metadata
- Methods already have BaseRequest/BaseResponse pattern built-in
- No execution wrapper needed - Pydantic handles validation automatically

Example:
    @register_service_method(
        name="create_casefile",
        description="Create new casefile with metadata",
        service_name="CasefileService",
        classification={
            "domain": "workspace",
            "subdomain": "casefile",
            "capability": "create",
            "complexity": "atomic",
            "maturity": "stable",
            "integration_tier": "internal"
        },
        required_permissions=["casefiles:write"]
    )
    async def create_casefile(self, request: CreateCasefileRequest) -> CreateCasefileResponse:
        # Implementation...
"""

import inspect
import logging
from functools import wraps
from typing import Any, Awaitable, Callable, Dict, List, Optional, Type

from pydantic import BaseModel

# Import from method infrastructure
from .method_definition import (
    ManagedMethodDefinition,
    MethodParameterDef,
)

# Import from registry
from .method_registry import register_method

logger = logging.getLogger(__name__)


def register_service_method(
    name: str,
    description: str,
    service_name: str,
    service_module: str,
    classification: Dict[str, str],
    required_permissions: Optional[List[str]] = None,
    requires_casefile: bool = False,
    casefile_permission_level: Optional[str] = None,
    enabled: bool = True,
    requires_auth: bool = True,
    timeout_seconds: int = 30,
    version: str = "1.0.0",
    dependencies: Optional[List[str]] = None,
    visibility: str = "public",
) -> Callable:
    """
    Register a service method in the MANAGED_METHODS registry.

    This decorator is the FOUNDATION of method engineering. It:
    1. Creates a ManagedMethodDefinition with metadata + business rules
    2. Extracts parameter definitions from method signature
    3. Registers in global MANAGED_METHODS registry for discovery
    4. Does NOT wrap execution (methods use BaseRequest/BaseResponse pattern)

    FIELD PURPOSES:
    Metadata fields (WHAT):
    - name: Method identifier (e.g., "create_casefile")
    - description: Human-readable purpose
    - service_name: Service class name (e.g., "CasefileService")
    - service_module: Module path (e.g., "src.casefileservice.service")
    - classification: 6-field taxonomy (domain, subdomain, capability, complexity, maturity, integration_tier)
    - version: Method version for compatibility

    Business logic fields (WHEN/WHERE):
    - enabled: Method availability toggle
    - requires_auth: Whether user must be authenticated
    - required_permissions: Specific permissions needed
    - requires_casefile: Whether casefile context is mandatory
    - casefile_permission_level: Required permission level (read/write/admin/owner)
    - timeout_seconds: Max execution time
    - dependencies: Other services/methods this depends on
    - visibility: "public" or "private" (internal helpers)

    Args:
        name: Unique method identifier
        description: What the method does
        service_name: Name of the service class
        service_module: Full module path to service
        classification: Dict with domain/subdomain/capability/complexity/maturity/integration_tier
        required_permissions: List of required permissions
        requires_casefile: Whether casefile context is required
        casefile_permission_level: Required casefile permission level
        enabled: Whether method is available
        requires_auth: Whether authentication is required
        timeout_seconds: Max execution time
        version: Method version
        dependencies: List of dependencies (other services/methods)
        visibility: "public" or "private"

    Returns:
        Decorated method (unmodified - no execution wrapper)

    Example:
        >>> @register_service_method(
        ...     name="create_casefile",
        ...     description="Create new casefile with metadata",
        ...     service_name="CasefileService",
        ...     service_module="src.casefileservice.service",
        ...     classification={
        ...         "domain": "workspace",
        ...         "subdomain": "casefile",
        ...         "capability": "create",
        ...         "complexity": "atomic",
        ...         "maturity": "stable",
        ...         "integration_tier": "internal"
        ...     },
        ...     required_permissions=["casefiles:write"]
        ... )
        ... async def create_casefile(self, request: CreateCasefileRequest) -> CreateCasefileResponse:
        ...     # Implementation
    """

    def decorator(func: Callable[..., Awaitable[BaseModel]]) -> Callable:
        """Inner decorator that processes the function."""

        # Extract method signature
        sig = inspect.signature(func)

        # Extract request/response model types from annotations
        request_model = None
        response_model = None

        # Get parameters (skip 'self' if present)
        params = list(sig.parameters.values())
        if params and params[0].name == "self":
            params = params[1:]

        # First parameter should be request model
        if params and params[0].annotation != inspect.Parameter.empty:
            request_model = params[0].annotation

        # Return annotation should be response model
        if sig.return_annotation != inspect.Signature.empty:
            response_model = sig.return_annotation

        # Create slim method definition (flat 16 fields)
        method_def = ManagedMethodDefinition(
            name=name,
            description=description,
            version=version,
            domain=classification.get("domain", ""),
            subdomain=classification.get("subdomain", ""),
            capability=classification.get("capability", ""),
            complexity=classification.get("complexity", ""),
            maturity=classification.get("maturity", ""),
            integration_tier=classification.get("integration_tier", ""),
            request_model_class=request_model,
            response_model_class=response_model,
            implementation_class=service_name,
            implementation_method=name,
        )

        # Register in MANAGED_METHODS
        register_method(name, method_def)

        logger.info(
            f"Registered method '{name}' in service '{service_name}' "
            f"(domain: {classification.get('domain')})"
        )

        # Return original function unmodified
        # Methods don't need execution wrapper - BaseRequest/BaseResponse handles validation
        return func

    return decorator


def _extract_parameter_definitions_from_request(
    request_model: Type[BaseModel],
) -> List[MethodParameterDef]:
    """
    Extract parameter definitions from request model's payload.

    This extracts parameters from the BaseRequest[T] payload field,
    which contains the actual business parameters.

    Args:
        request_model: Request model class (e.g., CreateCasefileRequest)

    Returns:
        List of MethodParameterDef instances
    """
    parameters = []

    # Get model fields from Pydantic v2
    if not hasattr(request_model, "model_fields"):
        return parameters

    model_fields = request_model.model_fields

    # Look for 'payload' field which contains the actual parameters
    if "payload" not in model_fields:
        # If no payload field, extract from all fields
        for field_name, field_info in model_fields.items():
            param_def = _create_parameter_def(field_name, field_info)
            parameters.append(param_def)
    else:
        # Extract from payload type
        payload_field = model_fields["payload"]
        payload_type = payload_field.annotation

        # Handle Optional[T] unwrapping
        import typing

        if hasattr(typing, "get_origin") and typing.get_origin(payload_type) is typing.Union:
            args = typing.get_args(payload_type)
            if len(args) == 2 and type(None) in args:
                # This is Optional[T], get T
                payload_type = args[0] if args[1] is type(None) else args[1]

        # Extract fields from payload model
        if hasattr(payload_type, "model_fields"):
            for field_name, field_info in payload_type.model_fields.items():
                param_def = _create_parameter_def(field_name, field_info)
                parameters.append(param_def)

    return parameters


def _create_parameter_def(field_name: str, field_info: Any) -> MethodParameterDef:
    """
    Create MethodParameterDef from Pydantic field info.

    Args:
        field_name: Name of the field
        field_info: Pydantic FieldInfo object

    Returns:
        MethodParameterDef instance
    """
    # Determine parameter type from annotation
    param_type = _python_type_to_string(field_info.annotation)

    # Extract description
    description = field_info.description or f"Parameter: {field_name}"

    # Determine if required
    required = field_info.is_required()

    # Get default value
    default_value = None
    if not required and field_info.default is not None:
        default_value = field_info.default

    # Create parameter definition
    param_def = MethodParameterDef(
        name=field_name,
        param_type=param_type,
        required=required,
        description=description,
        default_value=default_value,
    )

    return param_def


def _create_parameter_def_from_field(field_name: str, field_info: Any) -> MethodParameterDef:
    """
    Create MethodParameterDef from Pydantic FieldInfo.

    Args:
        field_name: Name of the field
        field_info: Pydantic FieldInfo object

    Returns:
        MethodParameterDef instance
    """
    # Determine parameter type from annotation
    param_type = _python_type_to_string(field_info.annotation)

    # Extract description
    description = field_info.description or f"Parameter: {field_name}"

    # Determine if required
    required = field_info.is_required()

    # Get default value
    default_value = None
    if not required and field_info.default is not None:
        default_value = field_info.default

    # Create parameter definition
    param_def = MethodParameterDef(
        name=field_name,
        param_type=param_type,
        required=required,
        description=description,
        default_value=default_value,
    )

    return param_def


def _python_type_to_string(python_type: Any) -> str:
    """
    Convert Python type annotation to string representation.

    Args:
        python_type: Python type annotation

    Returns:
        String representation of type
    """
    import typing

    # Handle None type
    if python_type is type(None):
        return "None"

    # Handle basic types
    if python_type == str:
        return "str"
    elif python_type == int:
        return "int"
    elif python_type == float:
        return "float"
    elif python_type == bool:
        return "bool"
    elif python_type == dict:
        return "dict"
    elif python_type == list:
        return "list"

    # Handle generic types
    origin = typing.get_origin(python_type)
    if origin is not None:
        args = typing.get_args(python_type)

        if origin is list:
            if args:
                return f"List[{_python_type_to_string(args[0])}]"
            return "List"
        elif origin is dict:
            if len(args) >= 2:
                return f"Dict[{_python_type_to_string(args[0])}, {_python_type_to_string(args[1])}]"
            return "Dict"
        elif origin is typing.Union:
            # Handle Optional[T] (Union[T, None])
            if len(args) == 2 and type(None) in args:
                inner_type = args[0] if args[1] is type(None) else args[1]
                return f"Optional[{_python_type_to_string(inner_type)}]"
            # Handle Union[T1, T2, ...]
            type_strs = [_python_type_to_string(arg) for arg in args]
            return f"Union[{', '.join(type_strs)}]"

    # Handle custom classes
    if hasattr(python_type, "__name__"):
        return python_type.__name__

    # Fallback to string representation
    return str(python_type)


# Load methods from YAML configuration file


def load_methods_from_yaml(yaml_path: str) -> Dict[str, ManagedMethodDefinition]:
    """
    Load method definitions from YAML configuration file.

    This reads the methods_inventory_v1.yaml file and creates
    ManagedMethodDefinition instances for each method.

    Used during service initialization to populate MANAGED_METHODS
    registry before decorators are applied.

    Args:
        yaml_path: Path to YAML configuration file

    Returns:
        Dictionary mapping method name to ManagedMethodDefinition

    Example:
        >>> methods = load_methods_from_yaml("config/methods_inventory_v1.yaml")
        >>> for name, method_def in methods.items():
        ...     register_method(name, method_def)
    """
    from pathlib import Path

    import yaml

    yaml_file = Path(yaml_path)
    if not yaml_file.exists():
        logger.warning(f"Methods YAML file not found: {yaml_path}")
        return {}

    with open(yaml_file, "r") as f:
        config = yaml.safe_load(f)

    methods = {}

    # Iterate through services
    for service in config.get("services", []):
        service_name = service["name"]
        service_module = service["module"]

        # Iterate through methods in service
        for method_config in service.get("methods", []):
            method_name = method_config["name"]
            classification = method_config["classification"]

            # Extract model classes for validation
            models_config = method_config.get("models", {})
            module_path = models_config.get("module") or "unknown"
            request_name = models_config.get("request") or "Unknown"
            response_name = models_config.get("response") or "Unknown"

            request_model_class = None
            response_model_class = None

            # Try to import model classes
            if module_path != "unknown":
                try:
                    import importlib

                    # Strip 'src.' prefix since src is already in Python path
                    import_path = module_path
                    if import_path.startswith("src."):
                        import_path = import_path[4:]  # Remove 'src.' prefix
                    models_module = importlib.import_module(import_path)
                    request_model_class = getattr(models_module, request_name, None)
                    response_model_class = getattr(models_module, response_name, None)
                except Exception as e:
                    logger.warning(f"  ⚠ Could not import models from {module_path}: {e}")

            # Create slim method definition
            method_def = ManagedMethodDefinition(
                name=method_name,
                description=method_config["description"],
                version=method_config.get("version", "1.0.0"),
                domain=classification.get("domain", ""),
                subdomain=classification.get("subdomain", ""),
                capability=classification.get("capability", ""),
                complexity=classification.get("complexity", ""),
                maturity=classification.get("maturity", ""),
                integration_tier=classification.get("integration_tier", ""),
                request_model_class=request_model_class,
                response_model_class=response_model_class,
                implementation_class=service_name,
                implementation_method=method_name,
            )

            # FIX: Use compound key to avoid duplicates across services
            # Format: "ServiceName.method_name"
            compound_key = f"{service_name}.{method_name}"
            methods[compound_key] = method_def

            logger.info(
                f"Loaded method '{compound_key}' from YAML "
                f"(service: {service_name}, domain: {classification.get('domain')})"
            )

    logger.info(f"Loaded {len(methods)} methods from {yaml_path}")
    return methods


# Utility function for service initialization


def register_methods_from_yaml(yaml_path: str = "config/methods_inventory_v1.yaml"):
    """
    Load and register all methods from YAML configuration.

    This should be called during application startup to populate
    the MANAGED_METHODS registry before services are instantiated.

    Args:
        yaml_path: Path to YAML configuration file

    Example:
        >>> # In main.py or service initialization
        >>> from src.pydantic_ai_integration.method_decorator import register_methods_from_yaml
        >>> register_methods_from_yaml()
    """
    methods = load_methods_from_yaml(yaml_path)

    for method_name, method_def in methods.items():
        register_method(method_name, method_def)

    logger.info(f"Registered {len(methods)} methods in MANAGED_METHODS registry")


def check_method_deprecation(method_name: str) -> None:
    """
    Check if a method is deprecated and log a warning.

    This should be called at the beginning of service methods to warn
    users about deprecated methods.

    Args:
        method_name: Name of the method being called

    Example:
        >>> async def create_casefile(self, request: CreateCasefileRequest):
        ...     check_method_deprecation("create_casefile")
        ...     # Implementation...
    """
    from .method_registry import get_method

    method_def = get_method(method_name)
    if not method_def:
        return

    business_rules = method_def.business_rules
    if business_rules.deprecated:
        import warnings

        # Build deprecation message
        msg = f"Method '{method_name}' is deprecated"

        if business_rules.deprecated_since:
            msg += f" since v{business_rules.deprecated_since}"

        if business_rules.replacement_method:
            msg += f". Use '{business_rules.replacement_method}' instead"

        if business_rules.removal_version:
            msg += f". Will be removed in v{business_rules.removal_version}"

        if business_rules.deprecation_message:
            msg += f". {business_rules.deprecation_message}"

        warnings.warn(msg, DeprecationWarning, stacklevel=3)
        logger.warning(f"DEPRECATION: {msg}")


def get_registry_version() -> str:
    """
    Get the current version of the methods registry.

    Returns version string from the loaded YAML inventory.

    Returns:
        Version string (e.g., "1.0.0")

    Example:
        >>> version = get_registry_version()
        >>> print(f"Registry version: {version}")
    """
    # This would ideally be loaded from YAML metadata
    # For now, return hardcoded version
    return "1.0.0"
