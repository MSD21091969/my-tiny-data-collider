"""
YAML Tool Definition Validator

Validates tool definitions against:
1. Tool schema v2 structure
2. Method inventory references
3. Pydantic request model parameter alignment
4. Version metadata consistency

Usage:
    python scripts/validate_tool_definitions.py
    python scripts/validate_tool_definitions.py --tool <tool_name>
    python scripts/validate_tool_definitions.py --verbose
"""

import argparse
import importlib
import logging
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml
from pydantic import BaseModel

# Setup paths
REPO_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(REPO_ROOT / "src"))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s"
)
logger = logging.getLogger(__name__)


class ValidationError:
    """Validation error record."""
    def __init__(self, tool_name: str, severity: str, message: str, field: Optional[str] = None):
        self.tool_name = tool_name
        self.severity = severity  # ERROR, WARNING, INFO
        self.message = message
        self.field = field
    
    def __str__(self) -> str:
        field_info = f" [field: {self.field}]" if self.field else ""
        return f"{self.severity}: {self.tool_name}{field_info} - {self.message}"


class ToolDefinitionValidator:
    """Validates YAML tool definitions against schema and models."""
    
    def __init__(self):
        self.errors: List[ValidationError] = []
        self.warnings: List[ValidationError] = []
        self.methods_inventory: Dict[str, Any] = {}
        self.tool_schema: Dict[str, Any] = {}
        
    def load_inventories(self):
        """Load methods inventory and tool schema."""
        # Load methods inventory
        methods_path = REPO_ROOT / "config" / "methods_inventory_v1.yaml"
        if methods_path.exists():
            with open(methods_path) as f:
                data = yaml.safe_load(f)
                # Parse nested services -> methods structure
                for service_def in data.get("services", []):
                    service_name = service_def.get("name")
                    for method_def in service_def.get("methods", []):
                        method_name = method_def.get("name")
                        if method_name:
                            # Store with fully qualified name for easy lookup
                            self.methods_inventory[method_name] = method_def
                            # Also store service context
                            method_def["_service"] = service_name
            logger.info(f"Loaded {len(self.methods_inventory)} methods from inventory")
        else:
            logger.warning(f"Methods inventory not found: {methods_path}")
        
        # Load tool schema
        schema_path = REPO_ROOT / "config" / "tool_schema_v2.yaml"
        if schema_path.exists():
            with open(schema_path) as f:
                self.tool_schema = yaml.safe_load(f) or {}
            logger.info(f"Loaded tool schema v2")
        else:
            logger.warning(f"Tool schema not found: {schema_path}")
    
    def validate_tool_file(self, tool_path: Path) -> bool:
        """Validate single tool definition file.
        
        Returns:
            True if validation passes (no errors), False otherwise
        """
        logger.info(f"\nValidating: {tool_path.name}")
        
        # Load tool definition
        try:
            with open(tool_path) as f:
                tool_def = yaml.safe_load(f)
        except yaml.YAMLError as e:
            self.errors.append(
                ValidationError(tool_path.stem, "ERROR", f"YAML parse error: {e}")
            )
            return False
        
        if not tool_def:
            self.errors.append(
                ValidationError(tool_path.stem, "ERROR", "Empty tool definition")
            )
            return False
        
        tool_name = tool_def.get("name", tool_path.stem)
        
        # Validate required fields
        self._validate_required_fields(tool_name, tool_def)
        
        # Validate method reference
        method_ref = tool_def.get("method_reference", {})
        method_name = method_ref.get("method")
        if method_name:
            self._validate_method_reference(tool_name, method_name)
        
        # Validate parameters against request model
        data_contracts = tool_def.get("data_contracts", {})
        request_model_name = data_contracts.get("request_model")
        if request_model_name:
            self._validate_request_model_alignment(
                tool_name, 
                tool_def,
                request_model_name,
                data_contracts.get("module")
            )
        
        # Validate version metadata
        self._validate_version_metadata(tool_name, tool_def)
        
        # Count errors/warnings for this tool
        tool_errors = [e for e in self.errors if e.tool_name == tool_name]
        tool_warnings = [w for w in self.warnings if w.tool_name == tool_name]
        
        if tool_errors:
            logger.error(f"  ✗ {len(tool_errors)} error(s)")
            for error in tool_errors:
                logger.error(f"    {error}")
        
        if tool_warnings:
            logger.warning(f"  ⚠ {len(tool_warnings)} warning(s)")
            for warning in tool_warnings:
                logger.warning(f"    {warning}")
        
        if not tool_errors and not tool_warnings:
            logger.info(f"  ✓ Validation passed")
        
        return len(tool_errors) == 0
    
    def _validate_required_fields(self, tool_name: str, tool_def: Dict[str, Any]):
        """Validate required fields per tool schema v2."""
        required = ["name", "description", "category", "implementation"]
        
        for field in required:
            if field not in tool_def:
                self.errors.append(
                    ValidationError(tool_name, "ERROR", f"Missing required field", field=field)
                )
        
        # Validate implementation structure
        impl = tool_def.get("implementation", {})
        if impl:
            impl_type = impl.get("type")
            if not impl_type:
                self.errors.append(
                    ValidationError(tool_name, "ERROR", "Missing implementation.type", field="implementation.type")
                )
            elif impl_type not in ["simple", "api_call", "data_transform", "composite", "method_wrapper"]:
                self.errors.append(
                    ValidationError(tool_name, "ERROR", f"Invalid implementation.type: {impl_type}", field="implementation.type")
                )
    
    def _validate_method_reference(self, tool_name: str, method_name: str):
        """Validate method exists in inventory."""
        if method_name not in self.methods_inventory:
            self.errors.append(
                ValidationError(
                    tool_name,
                    "ERROR",
                    f"Method '{method_name}' not found in methods_inventory_v1.yaml",
                    field="method_reference.method"
                )
            )
            return
        
        logger.debug(f"  Method reference validated: {method_name}")
    
    def _validate_request_model_alignment(
        self,
        tool_name: str,
        tool_def: Dict[str, Any],
        request_model_name: str,
        module_path: Optional[str]
    ):
        """Validate tool parameters match request model payload fields."""
        if not module_path:
            self.warnings.append(
                ValidationError(
                    tool_name,
                    "WARNING",
                    f"No module specified for request model {request_model_name}",
                    field="data_contracts.module"
                )
            )
            return
        
        # Try to import and inspect request model
        try:
            # Convert module path to import path
            import_path = module_path.replace("/", ".").replace("src.", "")
            module = importlib.import_module(import_path)
            
            # Get request model class
            request_class = getattr(module, request_model_name, None)
            if not request_class:
                self.warnings.append(
                    ValidationError(
                        tool_name,
                        "WARNING",
                        f"Request model {request_model_name} not found in {import_path}",
                        field="data_contracts.request_model"
                    )
                )
                return
            
            # Get payload model from request
            if hasattr(request_class, "model_fields"):
                request_fields = request_class.model_fields
                payload_field = request_fields.get("payload")
                
                if payload_field and hasattr(payload_field.annotation, "model_fields"):
                    payload_model = payload_field.annotation
                    payload_fields = payload_model.model_fields
                    
                    # Get tool method_params
                    method_params = tool_def.get("method_params", [])
                    method_param_names = {p["name"] for p in method_params}
                    
                    # Get payload field names
                    payload_field_names = set(payload_fields.keys())
                    
                    # Check for missing parameters
                    missing = payload_field_names - method_param_names
                    if missing:
                        self.warnings.append(
                            ValidationError(
                                tool_name,
                                "WARNING",
                                f"Tool method_params missing fields from {payload_model.__name__}: {missing}",
                                field="method_params"
                            )
                        )
                    
                    # Check for extra parameters
                    extra = method_param_names - payload_field_names
                    if extra:
                        self.warnings.append(
                            ValidationError(
                                tool_name,
                                "WARNING",
                                f"Tool method_params has extra fields not in {payload_model.__name__}: {extra}",
                                field="method_params"
                            )
                        )
                    
                    # Validate required fields
                    for field_name, field_info in payload_fields.items():
                        if field_info.is_required():
                            matching_param = next((p for p in method_params if p["name"] == field_name), None)
                            if matching_param and not matching_param.get("required", False):
                                self.warnings.append(
                                    ValidationError(
                                        tool_name,
                                        "WARNING",
                                        f"Field '{field_name}' required in {payload_model.__name__} but not marked required in tool",
                                        field=f"method_params.{field_name}.required"
                                    )
                                )
                    
                    if not missing and not extra:
                        logger.debug(f"  Request model alignment validated: {request_model_name}")
                        
        except ImportError as e:
            self.warnings.append(
                ValidationError(
                    tool_name,
                    "WARNING",
                    f"Could not import module {module_path}: {e}",
                    field="data_contracts.module"
                )
            )
        except Exception as e:
            self.warnings.append(
                ValidationError(
                    tool_name,
                    "WARNING",
                    f"Error validating request model alignment: {e}",
                    field="data_contracts.request_model"
                )
            )
    
    def _validate_version_metadata(self, tool_name: str, tool_def: Dict[str, Any]):
        """Validate version metadata consistency."""
        tool_version = tool_def.get("version")
        if not tool_version:
            self.warnings.append(
                ValidationError(tool_name, "WARNING", "Missing version field", field="version")
            )
        
        # Validate semver format
        if tool_version and not self._is_valid_semver(tool_version):
            self.warnings.append(
                ValidationError(
                    tool_name,
                    "WARNING",
                    f"Invalid semver format: {tool_version}",
                    field="version"
                )
            )
        
        # Check compatibility section
        compat = tool_def.get("compatibility", {})
        method_version = compat.get("method_version")
        schema_version = compat.get("schema_version")
        
        if not method_version:
            self.warnings.append(
                ValidationError(tool_name, "WARNING", "Missing compatibility.method_version", field="compatibility.method_version")
            )
        
        if not schema_version:
            self.warnings.append(
                ValidationError(tool_name, "WARNING", "Missing compatibility.schema_version", field="compatibility.schema_version")
            )
    
    def _is_valid_semver(self, version: str) -> bool:
        """Check if version string is valid semver."""
        parts = version.split(".")
        if len(parts) != 3:
            return False
        return all(part.isdigit() for part in parts)
    
    def validate_all_tools(self, tools_dir: Path) -> Dict[str, bool]:
        """Validate all tool definitions in directory.
        
        Returns:
            Dict mapping tool names to validation results (True = passed)
        """
        if not tools_dir.exists():
            logger.error(f"Tools directory not found: {tools_dir}")
            return {}
        
        tool_files = list(tools_dir.glob("*_tool.yaml"))
        logger.info(f"Found {len(tool_files)} tool definition(s)")
        
        results = {}
        for tool_file in sorted(tool_files):
            passed = self.validate_tool_file(tool_file)
            results[tool_file.stem] = passed
        
        return results
    
    def print_summary(self, results: Dict[str, bool]):
        """Print validation summary."""
        print("\n" + "=" * 70)
        print("VALIDATION SUMMARY")
        print("=" * 70)
        
        passed = sum(1 for v in results.values() if v)
        failed = len(results) - passed
        
        print(f"Total tools: {len(results)}")
        print(f"Passed: {passed}")
        print(f"Failed: {failed}")
        print(f"Errors: {len(self.errors)}")
        print(f"Warnings: {len(self.warnings)}")
        
        if failed > 0:
            print(f"\nFailed tools:")
            for tool_name, result in results.items():
                if not result:
                    print(f"  ✗ {tool_name}")
        
        print("=" * 70)


def main():
    parser = argparse.ArgumentParser(description="Validate YAML tool definitions")
    parser.add_argument("--tool", help="Validate specific tool by name")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose logging")
    args = parser.parse_args()
    
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    
    validator = ToolDefinitionValidator()
    validator.load_inventories()
    
    tools_dir = REPO_ROOT / "config" / "methodtools_v1"
    
    if args.tool:
        # Validate specific tool
        tool_path = tools_dir / f"{args.tool}_tool.yaml"
        if not tool_path.exists():
            tool_path = tools_dir / f"{args.tool}.yaml"
        
        if not tool_path.exists():
            logger.error(f"Tool definition not found: {args.tool}")
            sys.exit(1)
        
        passed = validator.validate_tool_file(tool_path)
        sys.exit(0 if passed else 1)
    else:
        # Validate all tools
        results = validator.validate_all_tools(tools_dir)
        validator.print_summary(results)
        
        # Exit with error if any validations failed
        sys.exit(0 if all(results.values()) else 1)


if __name__ == "__main__":
    main()
