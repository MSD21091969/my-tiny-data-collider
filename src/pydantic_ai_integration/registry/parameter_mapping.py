"""
Parameter mapping validator for tool-to-method compatibility.

This module validates that tool parameters correctly map to method parameters,
including type compatibility, constraint alignment, and required parameter coverage.

Part of Phase 1: Validation Foundation (6 hours)
"""

import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set

from ..method_definition import MethodParameterDef
from ..method_registry import MANAGED_METHODS, extract_parameters_from_request_model
from ..tool_definition import ManagedToolDefinition, ParameterType, ToolParameterDef
from ..tool_decorator import MANAGED_TOOLS

logger = logging.getLogger(__name__)


@dataclass
class ParameterMismatch:
    """Represents a parameter mismatch between tool and method."""
    tool_name: str
    method_name: str
    parameter_name: str
    issue_type: str  # 'missing', 'type_mismatch', 'constraint_mismatch', 'required_mismatch'
    tool_value: Optional[str] = None
    method_value: Optional[str] = None
    severity: str = "error"  # 'error', 'warning', 'info'
    message: str = ""


@dataclass
class ParameterMappingReport:
    """Complete report of parameter mapping validation."""
    total_tools: int = 0
    tools_checked: int = 0
    tools_with_mismatches: int = 0
    total_mismatches: int = 0
    mismatches: List[ParameterMismatch] = field(default_factory=list)
    tools_without_methods: List[str] = field(default_factory=list)
    skipped_tools: List[str] = field(default_factory=list)
    
    @property
    def has_errors(self) -> bool:
        """Check if report contains any errors."""
        return any(m.severity == "error" for m in self.mismatches)
    
    @property
    def error_count(self) -> int:
        """Count of error-level mismatches."""
        return sum(1 for m in self.mismatches if m.severity == "error")
    
    @property
    def warning_count(self) -> int:
        """Count of warning-level mismatches."""
        return sum(1 for m in self.mismatches if m.severity == "warning")
    
    def __str__(self) -> str:
        """Human-readable report summary."""
        lines = [
            "Parameter Mapping Validation Report",
            "=" * 50,
            f"Tools Checked: {self.tools_checked}/{self.total_tools}",
            f"Tools with Mismatches: {self.tools_with_mismatches}",
            f"Total Issues: {self.total_mismatches} ({self.error_count} errors, {self.warning_count} warnings)",
        ]
        
        if self.tools_without_methods:
            lines.append(f"\nTools without method reference: {len(self.tools_without_methods)}")
        
        if self.skipped_tools:
            lines.append(f"Skipped tools: {len(self.skipped_tools)}")
        
        if self.mismatches:
            lines.append("\nMismatches by Tool:")
            current_tool = None
            for mismatch in sorted(self.mismatches, key=lambda m: (m.tool_name, m.parameter_name)):
                if mismatch.tool_name != current_tool:
                    current_tool = mismatch.tool_name
                    lines.append(f"\n  {current_tool} → {mismatch.method_name}:")
                
                severity_icon = "❌" if mismatch.severity == "error" else "⚠️" if mismatch.severity == "warning" else "ℹ️"
                lines.append(f"    {severity_icon} {mismatch.parameter_name}: {mismatch.message}")
        
        return "\n".join(lines)


class ParameterMappingValidator:
    """
    Validates tool-to-method parameter mappings.
    
    Checks:
    1. Tool parameters exist in method
    2. Type compatibility
    3. Constraint compatibility (min/max, length, pattern)
    4. Required parameter coverage
    
    Tool-specific parameters (execution control) are automatically filtered:
    - dry_run, timeout_seconds, method_name, execution_type
    - parameter_mapping, implementation_config
    """
    
    # Tool-specific parameters that don't map to methods
    TOOL_PARAMS = {
        "dry_run",
        "timeout_seconds",
        "method_name",
        "execution_type",
        "parameter_mapping",
        "implementation_config",
    }
    
    def __init__(self):
        """Initialize validator with registry references."""
        self.tools = MANAGED_TOOLS
        self.methods = MANAGED_METHODS
    
    def validate_all_mappings(
        self,
        skip_tools_without_methods: bool = True,
    ) -> ParameterMappingReport:
        """
        Validate all tool-to-method mappings in the registry.
        
        Args:
            skip_tools_without_methods: Skip tools that don't reference a method
            
        Returns:
            Complete validation report
        """
        report = ParameterMappingReport(total_tools=len(self.tools))
        
        for tool_name, tool_def in self.tools.items():
            # Skip tools without method reference
            if not tool_def.method_name:
                report.tools_without_methods.append(tool_name)
                if skip_tools_without_methods:
                    report.skipped_tools.append(tool_name)
                    continue
            
            # Validate this tool's mapping
            tool_mismatches = self.validate_tool_mapping(tool_def)
            
            if tool_mismatches:
                report.tools_with_mismatches += 1
                report.total_mismatches += len(tool_mismatches)
                report.mismatches.extend(tool_mismatches)
            
            report.tools_checked += 1
        
        return report
    
    def validate_tool_mapping(
        self,
        tool_def: ManagedToolDefinition,
    ) -> List[ParameterMismatch]:
        """
        Validate a single tool's parameter mapping to its method.
        
        Args:
            tool_def: Tool definition to validate
            
        Returns:
            List of parameter mismatches found
        """
        mismatches: List[ParameterMismatch] = []
        
        if not tool_def.method_name:
            return mismatches
        
        # Get method definition
        method_def = self._find_method(tool_def.method_name)
        if not method_def:
            mismatches.append(ParameterMismatch(
                tool_name=tool_def.name,
                method_name=tool_def.method_name,
                parameter_name="<method>",
                issue_type="missing",
                severity="error",
                message=f"Method '{tool_def.method_name}' not found in MANAGED_METHODS"
            ))
            return mismatches
        
        # Extract method parameters
        method_params = self._get_method_parameters(method_def)
        if not method_params:
            # Method has no parameters - tool shouldn't either
            if tool_def.parameters:
                mismatches.append(ParameterMismatch(
                    tool_name=tool_def.name,
                    method_name=tool_def.method_name,
                    parameter_name="<all>",
                    issue_type="extra_parameters",
                    severity="warning",
                    message="Tool has parameters but method has none"
                ))
            return mismatches
        
        # Create lookup dict for method parameters
        method_params_dict: Dict[str, MethodParameterDef] = {
            p.name: p for p in method_params
        }
        
        # Get tool parameters (explicit or inherited)
        tool_params = tool_def.parameters if tool_def.parameters else []
        
        # Filter out tool-specific parameters (execution control)
        filtered_tool_params = [
            p for p in tool_params
            if p.name not in self.TOOL_PARAMS
        ]
        
        # Check each tool parameter
        for tool_param in filtered_tool_params:
            method_param = method_params_dict.get(tool_param.name)
            
            if not method_param:
                mismatches.append(ParameterMismatch(
                    tool_name=tool_def.name,
                    method_name=tool_def.method_name,
                    parameter_name=tool_param.name,
                    issue_type="missing",
                    severity="error",
                    message=f"Parameter not found in method"
                ))
                continue
            
            # Validate type compatibility
            type_mismatches = self._validate_type_compatibility(
                tool_def.name,
                tool_def.method_name,
                tool_param,
                method_param
            )
            mismatches.extend(type_mismatches)
            
            # Validate constraints
            constraint_mismatches = self._validate_constraints(
                tool_def.name,
                tool_def.method_name,
                tool_param,
                method_param
            )
            mismatches.extend(constraint_mismatches)
            
            # Validate required flag
            if tool_param.required != method_param.required:
                mismatches.append(ParameterMismatch(
                    tool_name=tool_def.name,
                    method_name=tool_def.method_name,
                    parameter_name=tool_param.name,
                    issue_type="required_mismatch",
                    tool_value=str(tool_param.required),
                    method_value=str(method_param.required),
                    severity="warning",
                    message=f"Required flag mismatch: tool={tool_param.required}, method={method_param.required}"
                ))
        
        # Check for missing required parameters
        tool_param_names: Set[str] = {p.name for p in filtered_tool_params}
        for method_param in method_params:
            if method_param.required and method_param.name not in tool_param_names:
                mismatches.append(ParameterMismatch(
                    tool_name=tool_def.name,
                    method_name=tool_def.method_name,
                    parameter_name=method_param.name,
                    issue_type="missing",
                    severity="error",
                    message=f"Required method parameter missing from tool"
                ))
        
        return mismatches
    
    def _find_method(self, method_name: str):
        """Find method by name (supports compound keys and simple names)."""
        # Try direct lookup first
        method_def = self.methods.get(method_name)
        if method_def:
            return method_def
        
        # Try finding by method name only (without service prefix)
        for key, method in self.methods.items():
            if key.endswith(f".{method_name}") or key == method_name:
                return method
        
        return None
    
    def _get_method_parameters(self, method_def) -> List[MethodParameterDef]:
        """Extract parameters from method's request model."""
        if not method_def.request_model_class:
            return []
        
        return extract_parameters_from_request_model(method_def.request_model_class)
    
    def _validate_type_compatibility(
        self,
        tool_name: str,
        method_name: str,
        tool_param: ToolParameterDef,
        method_param: MethodParameterDef,
    ) -> List[ParameterMismatch]:
        """Check if parameter types are compatible."""
        mismatches: List[ParameterMismatch] = []
        
        # Normalize types for comparison
        tool_type = tool_param.param_type.value if isinstance(tool_param.param_type, ParameterType) else tool_param.param_type
        method_type = method_param.param_type
        
        # Direct match
        if tool_type == method_type:
            return mismatches
        
        # Check for compatible types (e.g., integer vs number)
        compatible_types = {
            ("integer", "number"),
            ("number", "integer"),
            ("string", "str"),
            ("str", "string"),
            ("boolean", "bool"),
            ("bool", "boolean"),
        }
        
        if (tool_type, method_type) not in compatible_types:
            mismatches.append(ParameterMismatch(
                tool_name=tool_name,
                method_name=method_name,
                parameter_name=tool_param.name,
                issue_type="type_mismatch",
                tool_value=tool_type,
                method_value=method_type,
                severity="error",
                message=f"Type mismatch: tool={tool_type}, method={method_type}"
            ))
        
        return mismatches
    
    def _validate_constraints(
        self,
        tool_name: str,
        method_name: str,
        tool_param: ToolParameterDef,
        method_param: MethodParameterDef,
    ) -> List[ParameterMismatch]:
        """Check if parameter constraints are compatible."""
        mismatches: List[ParameterMismatch] = []
        
        # Numeric constraints
        if tool_param.min_value is not None and method_param.min_value is not None:
            if tool_param.min_value != method_param.min_value:
                mismatches.append(ParameterMismatch(
                    tool_name=tool_name,
                    method_name=method_name,
                    parameter_name=tool_param.name,
                    issue_type="constraint_mismatch",
                    tool_value=str(tool_param.min_value),
                    method_value=str(method_param.min_value),
                    severity="warning",
                    message=f"min_value mismatch: tool={tool_param.min_value}, method={method_param.min_value}"
                ))
        
        if tool_param.max_value is not None and method_param.max_value is not None:
            if tool_param.max_value != method_param.max_value:
                mismatches.append(ParameterMismatch(
                    tool_name=tool_name,
                    method_name=method_name,
                    parameter_name=tool_param.name,
                    issue_type="constraint_mismatch",
                    tool_value=str(tool_param.max_value),
                    method_value=str(method_param.max_value),
                    severity="warning",
                    message=f"max_value mismatch: tool={tool_param.max_value}, method={method_param.max_value}"
                ))
        
        # String constraints
        if tool_param.min_length is not None and method_param.min_length is not None:
            if tool_param.min_length != method_param.min_length:
                mismatches.append(ParameterMismatch(
                    tool_name=tool_name,
                    method_name=method_name,
                    parameter_name=tool_param.name,
                    issue_type="constraint_mismatch",
                    tool_value=str(tool_param.min_length),
                    method_value=str(method_param.min_length),
                    severity="warning",
                    message=f"min_length mismatch: tool={tool_param.min_length}, method={method_param.min_length}"
                ))
        
        if tool_param.max_length is not None and method_param.max_length is not None:
            if tool_param.max_length != method_param.max_length:
                mismatches.append(ParameterMismatch(
                    tool_name=tool_name,
                    method_name=method_name,
                    parameter_name=tool_param.name,
                    issue_type="constraint_mismatch",
                    tool_value=str(tool_param.max_length),
                    method_value=str(method_param.max_length),
                    severity="warning",
                    message=f"max_length mismatch: tool={tool_param.max_length}, method={method_param.max_length}"
                ))
        
        # Pattern constraint
        if tool_param.pattern is not None and method_param.pattern is not None:
            if tool_param.pattern != method_param.pattern:
                mismatches.append(ParameterMismatch(
                    tool_name=tool_name,
                    method_name=method_name,
                    parameter_name=tool_param.name,
                    issue_type="constraint_mismatch",
                    tool_value=tool_param.pattern,
                    method_value=method_param.pattern,
                    severity="info",
                    message=f"pattern mismatch: tool={tool_param.pattern}, method={method_param.pattern}"
                ))
        
        return mismatches


# Convenience function
def validate_parameter_mappings(
    skip_tools_without_methods: bool = True,
) -> ParameterMappingReport:
    """
    Validate all tool-to-method parameter mappings.
    
    Args:
        skip_tools_without_methods: Skip tools without method references
        
    Returns:
        Complete validation report
        
    Example:
        >>> report = validate_parameter_mappings()
        >>> print(report)
        >>> if report.has_errors:
        >>>     print(f"Found {report.error_count} errors!")
    """
    validator = ParameterMappingValidator()
    return validator.validate_all_mappings(skip_tools_without_methods=skip_tools_without_methods)
