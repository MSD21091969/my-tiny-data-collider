"""
Registry validation functions.

Provides coverage, consistency, and drift detection for method and tool registries.
Includes parameter mapping validation for tool-to-method compatibility.
"""

import logging

from .parameter_mapping import validate_parameter_mappings, ParameterMappingReport
from .types import ConsistencyReport, CoverageReport, DriftReport

logger = logging.getLogger(__name__)


def validate_method_tool_coverage() -> CoverageReport:
    """
    Validate that every method has a corresponding tool.

    Checks:
    - Every method in MANAGED_METHODS has a tool
    - Every tool references a valid method
    - Parameter alignment (TODO: signature validation)

    Returns:
        CoverageReport with validation results
    """
    from ..method_registry import MANAGED_METHODS
    from ..tool_decorator import MANAGED_TOOLS

    missing_tools = []
    orphaned_tools = []
    mismatched_signatures = []

    # Build method name → tool mapping
    tool_to_method: dict[str, str | None] = {}
    for tool_name, tool_def in MANAGED_TOOLS.items():
        # Extract method reference from tool definition
        # Tools store method_name in different ways, try common patterns
        method_ref = None

        # Try method_reference attribute (check it's a string, not a mock)
        if hasattr(tool_def, "method_reference"):
            ref = tool_def.method_reference
            if isinstance(ref, str):
                method_ref = ref

        # Try method_name attribute if method_reference didn't work
        if method_ref is None and hasattr(tool_def, "method_name"):
            ref = tool_def.method_name
            if isinstance(ref, str):
                method_ref = ref

        # Try metadata dict as fallback
        if (
            method_ref is None
            and hasattr(tool_def, "metadata")
            and isinstance(tool_def.metadata, dict)
        ):
            method_ref = tool_def.metadata.get("method_reference")

        tool_to_method[tool_name] = method_ref

    # Check every method has at least one tool
    method_to_tools: dict[str, list[str]] = {}
    for tool_name, method_ref in tool_to_method.items():
        if method_ref:
            if method_ref not in method_to_tools:
                method_to_tools[method_ref] = []
            method_to_tools[method_ref].append(tool_name)

    for method_name in MANAGED_METHODS.keys():
        if method_name not in method_to_tools:
            missing_tools.append(method_name)

    # Check every tool references a valid method
    for tool_name, method_ref in tool_to_method.items():
        if method_ref and method_ref not in MANAGED_METHODS:
            orphaned_tools.append(tool_name)

    # TODO: Validate parameter alignment
    # This requires comparing tool params with method params
    # Deferred to Phase 2 enhancement

    report = CoverageReport(
        missing_tools=missing_tools,
        orphaned_tools=orphaned_tools,
        mismatched_signatures=mismatched_signatures,
    )

    logger.debug(f"Coverage validation: {report.error_count} errors found")
    return report


def validate_registry_consistency() -> ConsistencyReport:
    """
    Validate internal registry consistency.

    Checks:
    - No duplicate method names
    - No duplicate tool names
    - All required fields present
    - Version consistency

    Returns:
        ConsistencyReport with validation results
    """
    from ..method_registry import MANAGED_METHODS
    from ..tool_decorator import MANAGED_TOOLS

    issues = []

    # Check for duplicate method names
    method_names = list(MANAGED_METHODS.keys())
    if len(method_names) != len(set(method_names)):
        duplicates = [name for name in method_names if method_names.count(name) > 1]
        issues.append(f"Duplicate method names: {set(duplicates)}")

    # Check for duplicate tool names
    tool_names = list(MANAGED_TOOLS.keys())
    if len(tool_names) != len(set(tool_names)):
        duplicates = [name for name in tool_names if tool_names.count(name) > 1]
        issues.append(f"Duplicate tool names: {set(duplicates)}")

    # Validate required fields in methods
    for method_name, method_def in MANAGED_METHODS.items():
        if hasattr(method_def, "description") and not method_def.description:
            issues.append(f"Method '{method_name}' missing description")

        if hasattr(method_def, "service") and not method_def.service:
            issues.append(f"Method '{method_name}' missing service")

    # Validate required fields in tools
    for tool_name, tool_def in MANAGED_TOOLS.items():
        if hasattr(tool_def, "description") and not tool_def.description:
            issues.append(f"Tool '{tool_name}' missing description")

    # Check version consistency (if methods have versions)
    if MANAGED_METHODS:
        versions = set()
        for method_def in MANAGED_METHODS.values():
            if hasattr(method_def, "version"):
                ver = method_def.version
                # Only count string versions, not MagicMock objects in tests
                if isinstance(ver, str) and ver:
                    versions.add(ver)

        if len(versions) > 1:
            issues.append(f"Multiple method versions found: {versions}")

    report = ConsistencyReport(issues=issues)
    logger.debug(f"Consistency validation: {report.error_count} errors found")
    return report


def detect_yaml_code_drift() -> DriftReport:
    """
    Detect drift between YAML inventories and actual service code.

    Scans all service modules for public async methods and compares with
    MANAGED_METHODS registry to identify:
    - Methods in code but not registered (missing_in_yaml)
    - Methods registered but not in code (missing_in_code)
    - Signature mismatches (future enhancement)

    Returns:
        DriftReport with detection results
    """
    import ast
    from pathlib import Path

    from ..method_registry import MANAGED_METHODS

    # Service modules to scan
    service_modules = [
        "casefileservice",
        "tool_sessionservice",
        "communicationservice",
        "authservice",
    ]

    # Build set of methods from code
    code_methods: set[str] = set()
    src_path = Path(__file__).parent.parent.parent

    for service_name in service_modules:
        service_path = src_path / service_name / "service.py"
        if not service_path.exists():
            logger.debug(f"Service file not found: {service_path}")
            continue

        try:
            # Parse the service file
            with open(service_path, encoding="utf-8") as f:
                tree = ast.parse(f.read(), filename=str(service_path))

            # Find service class and extract public async methods
            service_class_name = _to_pascal_case(service_name)
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef) and node.name == service_class_name:
                    for item in node.body:
                        if isinstance(item, ast.AsyncFunctionDef):
                            method_name = item.name
                            # Include public methods (not starting with _)
                            if not method_name.startswith("_"):
                                full_name = f"{service_class_name}.{method_name}"
                                code_methods.add(full_name)
                                logger.debug(f"Found method in code: {full_name}")

        except Exception as e:
            logger.warning(f"Failed to scan {service_path}: {e}")

    # Build set of methods from YAML (via MANAGED_METHODS registry)
    yaml_methods = set(MANAGED_METHODS.keys())

    # Find drift
    missing_in_yaml = code_methods - yaml_methods
    missing_in_code = yaml_methods - code_methods

    # TODO: Implement signature comparison for methods in both sets
    signature_mismatches = []

    report = DriftReport(
        missing_in_yaml=missing_in_yaml,
        missing_in_code=missing_in_code,
        signature_mismatches=signature_mismatches,
    )

    logger.debug(
        f"Drift detection: {len(missing_in_yaml)} missing in YAML, "
        f"{len(missing_in_code)} missing in code"
    )
    return report


def _to_pascal_case(snake_str: str) -> str:
    """Convert snake_case to PascalCase."""
    components = snake_str.split("_")
    return "".join(x.title() for x in components)
