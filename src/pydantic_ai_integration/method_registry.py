"""
Method registry - parallel to tool_decorator.py for service methods.

Global MANAGED_METHODS registry with discovery APIs.
Used by ToolFactory to validate api_call.method_name exists.

ARCHITECTURE:
- MANAGED_METHODS: Global Dict[str, ManagedMethodDefinition]
- Discovery APIs: 11 methods matching tool_decorator.py
- Classification-based queries: domain, subdomain, capability, etc.
- Future: @register_service_method decorator (Phase 10)
"""

from typing import Dict, List, Optional, Any
from collections import defaultdict
import logging

from .method_definition import ManagedMethodDefinition

logger = logging.getLogger(__name__)

# Global registry - SINGLE SOURCE OF TRUTH for methods
# Parallel to MANAGED_TOOLS in tool_decorator.py
# Format: {method_name: ManagedMethodDefinition}
MANAGED_METHODS: Dict[str, ManagedMethodDefinition] = {}


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
# CLASSIFICATION DISCOVERY (6 methods)
# ==============================================================================

def get_methods_by_domain(domain: str, enabled_only: bool = True) -> List[ManagedMethodDefinition]:
    """
    Get all methods in a domain.
    Parallel to tool_decorator.get_tools_by_domain().
    
    Args:
        domain: workspace, communication, automation
        enabled_only: Only return enabled methods
    """
    results = []
    for method_def in MANAGED_METHODS.values():
        if method_def.metadata.domain == domain:
            if not enabled_only or method_def.business_rules.enabled:
                results.append(method_def)
    return results


def get_methods_by_subdomain(domain: str, subdomain: str, enabled_only: bool = True) -> List[ManagedMethodDefinition]:
    """
    Get methods by domain + subdomain.
    Parallel to tool_decorator.get_tools_by_subdomain().
    
    Args:
        domain: workspace, communication, automation
        subdomain: casefile, gmail, tool_session, etc.
        enabled_only: Only return enabled methods
    """
    results = []
    for method_def in MANAGED_METHODS.values():
        if method_def.metadata.domain == domain and method_def.metadata.subdomain == subdomain:
            if not enabled_only or method_def.business_rules.enabled:
                results.append(method_def)
    return results


def get_methods_by_capability(capability: str, enabled_only: bool = True) -> List[ManagedMethodDefinition]:
    """
    Get methods by capability.
    Parallel to tool_decorator.get_tools_by_capability().
    
    Args:
        capability: create, read, update, delete, process, search
        enabled_only: Only return enabled methods
    """
    results = []
    for method_def in MANAGED_METHODS.values():
        if method_def.metadata.capability == capability:
            if not enabled_only or method_def.business_rules.enabled:
                results.append(method_def)
    return results


def get_methods_by_complexity(complexity: str, enabled_only: bool = True) -> List[ManagedMethodDefinition]:
    """
    Get methods by complexity.
    Parallel to tool_decorator.get_tools_by_complexity().
    
    Args:
        complexity: atomic, composite, pipeline
        enabled_only: Only return enabled methods
    """
    results = []
    for method_def in MANAGED_METHODS.values():
        if method_def.metadata.complexity == complexity:
            if not enabled_only or method_def.business_rules.enabled:
                results.append(method_def)
    return results


def get_methods_by_maturity(maturity: str, enabled_only: bool = True) -> List[ManagedMethodDefinition]:
    """
    Get methods by maturity level.
    Parallel to tool_decorator.get_tools_by_maturity().
    
    Args:
        maturity: stable, beta, alpha, experimental
        enabled_only: Only return enabled methods
    """
    results = []
    for method_def in MANAGED_METHODS.values():
        if method_def.metadata.maturity == maturity:
            if not enabled_only or method_def.business_rules.enabled:
                results.append(method_def)
    return results


def get_methods_by_integration_tier(tier: str, enabled_only: bool = True) -> List[ManagedMethodDefinition]:
    """
    Get methods by integration tier.
    Parallel to tool_decorator.get_tools_by_integration_tier().
    
    Args:
        tier: internal, external, hybrid
        enabled_only: Only return enabled methods
    """
    results = []
    for method_def in MANAGED_METHODS.values():
        if method_def.metadata.integration_tier == tier:
            if not enabled_only or method_def.business_rules.enabled:
                results.append(method_def)
    return results


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
        "enabled_methods": sum(1 for m in MANAGED_METHODS.values() if m.business_rules.enabled),
        "by_domain": defaultdict(int),
        "by_subdomain": defaultdict(int),
        "by_capability": defaultdict(int),
        "by_complexity": defaultdict(int),
        "by_maturity": defaultdict(int),
        "by_integration_tier": defaultdict(int),
        "by_service": defaultdict(int)
    }
    
    for method_def in MANAGED_METHODS.values():
        summary["by_domain"][method_def.metadata.domain] += 1
        summary["by_subdomain"][method_def.metadata.subdomain] += 1
        summary["by_capability"][method_def.metadata.capability] += 1
        summary["by_complexity"][method_def.metadata.complexity] += 1
        summary["by_maturity"][method_def.metadata.maturity] += 1
        summary["by_integration_tier"][method_def.metadata.integration_tier] += 1
        summary["by_service"][method_def.metadata.service_name] += 1
    
    # Convert defaultdict to regular dict for JSON serialization
    return {
        "total_methods": summary["total_methods"],
        "enabled_methods": summary["enabled_methods"],
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

def get_methods_by_service(service_name: str, enabled_only: bool = True) -> List[ManagedMethodDefinition]:
    """
    Get all methods from a specific service.
    Useful for service-level documentation.
    
    Args:
        service_name: CasefileService, ToolSessionService, etc.
        enabled_only: Only return enabled methods
    """
    results = []
    for method_def in MANAGED_METHODS.values():
        if method_def.metadata.service_name == service_name:
            if not enabled_only or method_def.business_rules.enabled:
                results.append(method_def)
    return results


def get_methods_requiring_casefile(enabled_only: bool = True) -> List[ManagedMethodDefinition]:
    """
    Get all methods that require casefile context.
    Useful for casefile-related tooling.
    """
    results = []
    for method_def in MANAGED_METHODS.values():
        if method_def.business_rules.requires_casefile:
            if not enabled_only or method_def.business_rules.enabled:
                results.append(method_def)
    return results


# ==============================================================================
# MANUAL REGISTRATION (Phase 10 will add decorator)
# ==============================================================================

def register_method(method_name: str, method_def: ManagedMethodDefinition) -> None:
    """
    Manually register a method definition.
    Used for initial population and by @register_service_method decorator.
    
    Args:
        method_name: Unique method identifier
        method_def: Complete ManagedMethodDefinition instance
    """
    if method_name in MANAGED_METHODS:
        logger.warning(f"Method '{method_name}' already registered, overwriting")
    
    MANAGED_METHODS[method_name] = method_def
    logger.info(
        f"Registered method: {method_name} "
        f"({method_def.metadata.service_name})"
    )


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
        service = method_def.metadata.service_name
        by_service[service].append(method_def.to_yaml_compatible())
    return dict(by_service)


def get_deprecated_methods(include_disabled: bool = False) -> List[Dict[str, Any]]:
    """
    Get all deprecated methods with deprecation metadata.
    
    Used for:
    - Generating deprecation reports
    - Warning users about upcoming removals
    - Planning migration strategies
    
    Args:
        include_disabled: Whether to include disabled methods
        
    Returns:
        List of dicts with deprecation info:
        {
            "name": "method_name",
            "service": "ServiceName",
            "deprecated_since": "1.5.0",
            "removal_version": "2.0.0",
            "replacement": "new_method_name",
            "message": "Use new_method_name for better performance"
        }
    """
    deprecated = []
    
    for method_name, method_def in MANAGED_METHODS.items():
        rules = method_def.business_rules
        
        if not rules.deprecated:
            continue
            
        if not include_disabled and not rules.enabled:
            continue
        
        deprecated.append({
            "name": method_name,
            "service": method_def.metadata.service_name,
            "domain": method_def.metadata.domain,
            "deprecated_since": rules.deprecated_since,
            "removal_version": rules.removal_version,
            "replacement": rules.replacement_method,
            "message": rules.deprecation_message
        })
    
    return deprecated


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
    import yaml
    from pathlib import Path
    
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
