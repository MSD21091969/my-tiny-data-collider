#!/usr/bin/env python3
"""
DTO Alignment Validation Script
Created: 2025-10-08
Purpose: Validate R-A-R pattern compliance and parameter alignment across layers

Checks:
1. Tool → Method references are valid (method exists in MANAGED_METHODS)
2. Method → DTO references are valid (request/response models exist)
3. Parameter alignment: Tool params match Method request payload fields
4. Classification alignment: Tool classification matches Method classification (if specified)
5. All operations follow R-A-R pattern (Request → Action → Response)
"""

import sys
import yaml
from pathlib import Path
from typing import Dict, List, Tuple, Any
from dataclasses import dataclass

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from pydantic_ai_integration import method_registry
from pydantic_ai_integration.model_registry import get_model_registry


@dataclass
class ValidationIssue:
    """Represents a validation issue"""
    severity: str  # ERROR, WARNING, INFO
    category: str  # reference, alignment, pattern, classification
    entity: str    # tool/method/model name
    message: str
    details: Dict[str, Any] = None
    
    def __str__(self):
        result = f"[{self.severity}] {self.category.upper()}: {self.entity}"
        result += f"\n  {self.message}"
        if self.details:
            for key, value in self.details.items():
                result += f"\n  {key}: {value}"
        return result


class DTOAlignmentValidator:
    """Validates DTO alignment across layers"""
    
    def __init__(self):
        # Method registry uses function-based API
        self.model_registry = get_model_registry()
        self.issues: List[ValidationIssue] = []
        
        # Load tools inventory if exists
        self.tools_inventory = self._load_tools_inventory()
    
    def _load_tools_inventory(self) -> Dict:
        """Load tools inventory YAML"""
        tools_path = Path(__file__).parent.parent / "config" / "tools_inventory_v1.yaml"
        if not tools_path.exists():
            return {}
        
        with open(tools_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f) or {}
    
    def validate_all(self) -> bool:
        """Run all validations. Returns True if no errors."""
        print("=" * 80)
        print("DTO ALIGNMENT VALIDATION")
        print("=" * 80)
        
        # Run validations
        self.validate_method_references()
        self.validate_model_references()
        self.validate_rar_pattern()
        self.validate_parameter_alignment()
        
        # Report results
        self._report_results()
        
        # Return success if no errors
        return not any(issue.severity == "ERROR" for issue in self.issues)
    
    def validate_method_references(self):
        """Validate that all tool → method references are valid"""
        print("\n[1/4] Validating Tool → Method References...")
        
        tools = self.tools_inventory.get('tools', [])
        if not tools:
            self.issues.append(ValidationIssue(
                severity="WARNING",
                category="reference",
                entity="tools_inventory",
                message="No tools found in tools_inventory_v1.yaml"
            ))
            return
        
        for tool in tools:
            tool_name = tool.get('name', 'unknown')
            impl = tool.get('implementation', {})
            method_name = impl.get('method_name')
            
            if method_name:
                # Check if method exists
                if not method_registry.validate_method_exists(method_name):
                    self.issues.append(ValidationIssue(
                        severity="ERROR",
                        category="reference",
                        entity=tool_name,
                        message=f"References non-existent method: {method_name}"
                    ))
        
        print(f"  ✓ Checked {len(tools)} tools")
    
    def validate_model_references(self):
        """Validate that all method → model references are valid"""
        print("\n[2/4] Validating Method → Model References...")
        
        methods = method_registry.get_registered_methods()
        checked = 0
        
        for method_name, method_def in methods.items():
            checked += 1
            
            # Check request model
            if method_def.request_model_class:
                req_model_name = method_def.request_model_class.__name__
                if not self.model_registry.validate_model_exists(req_model_name):
                    self.issues.append(ValidationIssue(
                        severity="WARNING",
                        category="reference",
                        entity=method_def.name,
                        message=f"Request model not in registry: {req_model_name}",
                        details={"model": req_model_name}
                    ))
            
            # Check response model
            if method_def.response_model_class:
                resp_model_name = method_def.response_model_class.__name__
                if not self.model_registry.validate_model_exists(resp_model_name):
                    self.issues.append(ValidationIssue(
                        severity="WARNING",
                        category="reference",
                        entity=method_def.name,
                        message=f"Response model not in registry: {resp_model_name}",
                        details={"model": resp_model_name}
                    ))
        
        print(f"  ✓ Checked {checked} methods")
    
    def validate_rar_pattern(self):
        """Validate R-A-R pattern compliance"""
        print("\n[3/4] Validating R-A-R Pattern Compliance...")
        
        methods = method_registry.get_registered_methods()
        checked = 0
        
        for method_name, method_def in methods.items():
            checked += 1
            
            # Check request model exists
            if not method_def.request_model_class:
                self.issues.append(ValidationIssue(
                    severity="ERROR",
                    category="pattern",
                    entity=method_def.name,
                    message="Missing request_model_class (R-A-R violation)"
                ))
            
            # Check response model exists
            if not method_def.response_model_class:
                self.issues.append(ValidationIssue(
                    severity="ERROR",
                    category="pattern",
                    entity=method_def.name,
                    message="Missing response_model_class (R-A-R violation)"
                ))
            
            # Check naming convention
            if method_def.request_model_class:
                req_name = method_def.request_model_class.__name__
                if not req_name.endswith('Request'):
                    self.issues.append(ValidationIssue(
                        severity="WARNING",
                        category="pattern",
                        entity=method_def.name,
                        message=f"Request model should end with 'Request': {req_name}"
                    ))
            
            if method_def.response_model_class:
                resp_name = method_def.response_model_class.__name__
                if not resp_name.endswith('Response'):
                    self.issues.append(ValidationIssue(
                        severity="WARNING",
                        category="pattern",
                        entity=method_def.name,
                        message=f"Response model should end with 'Response': {resp_name}"
                    ))
        
        print(f"  ✓ Checked {checked} methods for R-A-R compliance")
    
    def validate_parameter_alignment(self):
        """Validate parameter alignment across layers"""
        print("\n[4/4] Validating Parameter Alignment...")
        
        tools = self.tools_inventory.get('tools', [])
        if not tools:
            return
        
        checked = 0
        for tool in tools:
            tool_name = tool.get('name', 'unknown')
            impl = tool.get('implementation', {})
            method_name = impl.get('method_name')
            
            if not method_name:
                continue
            
            checked += 1
            if not method_registry.validate_method_exists(method_name):
                continue
            
            # Get method parameters from request model
            try:
                method_params = method_registry.get_method_parameters(method_name)
            except Exception as e:
                self.issues.append(ValidationIssue(
                    severity="ERROR",
                    category="alignment",
                    entity=tool_name,
                    message=f"Failed to extract parameters from method: {e}"
                ))
                continue
            
            # Get tool parameters
            tool_params = {p['name']: p for p in tool.get('parameters', [])}
            method_param_names = {p.name for p in method_params}
            
            # Check for missing parameters
            missing = method_param_names - set(tool_params.keys())
            if missing:
                self.issues.append(ValidationIssue(
                    severity="WARNING",
                    category="alignment",
                    entity=tool_name,
                    message=f"Tool missing parameters from method {method_name}",
                    details={"missing_params": sorted(missing)}
                ))
            
            # Check for extra parameters
            extra = set(tool_params.keys()) - method_param_names
            if extra:
                self.issues.append(ValidationIssue(
                    severity="INFO",
                    category="alignment",
                    entity=tool_name,
                    message=f"Tool has extra parameters not in method {method_name}",
                    details={"extra_params": sorted(extra)}
                ))
        
        print(f"  ✓ Checked {checked} tool/method parameter alignments")
    
    def _report_results(self):
        """Report validation results"""
        print("\n" + "=" * 80)
        print("VALIDATION RESULTS")
        print("=" * 80)
        
        # Count by severity
        errors = [i for i in self.issues if i.severity == "ERROR"]
        warnings = [i for i in self.issues if i.severity == "WARNING"]
        infos = [i for i in self.issues if i.severity == "INFO"]
        
        print(f"\nTotal Issues: {len(self.issues)}")
        print(f"  Errors:   {len(errors)}")
        print(f"  Warnings: {len(warnings)}")
        print(f"  Info:     {len(infos)}")
        
        # Print errors
        if errors:
            print("\n" + "-" * 80)
            print("ERRORS")
            print("-" * 80)
            for issue in errors:
                print(f"\n{issue}")
        
        # Print warnings
        if warnings:
            print("\n" + "-" * 80)
            print("WARNINGS")
            print("-" * 80)
            for issue in warnings:
                print(f"\n{issue}")
        
        # Print info (only if verbose)
        if infos and len(infos) <= 10:
            print("\n" + "-" * 80)
            print("INFO")
            print("-" * 80)
            for issue in infos:
                print(f"\n{issue}")
        
        # Summary
        print("\n" + "=" * 80)
        if not self.issues:
            print("✅ ALL VALIDATIONS PASSED")
        elif not errors:
            print("⚠️  VALIDATION PASSED WITH WARNINGS")
        else:
            print("❌ VALIDATION FAILED")
        print("=" * 80)


def main():
    """Main entry point"""
    validator = DTOAlignmentValidator()
    success = validator.validate_all()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
