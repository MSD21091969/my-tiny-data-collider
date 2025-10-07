"""Tool Factory - Generate tools from YAML configurations.

This module is part of the pydantic_ai_integration tool engineering foundation.
It reads YAML tool definitions and generates:
1. Tool implementations with @register_mds_tool decorator
2. Pydantic parameter models with validation constraints
3. Comprehensive test suites

Architecture:
- Reads YAML from config/tools/
- Generates to src/pydantic_ai_integration/tools/generated/
- Uses templates from src/pydantic_ai_integration/tools/factory/templates/
- Integrates with existing tool_decorator.py registry

Usage:
    from src.pydantic_ai_integration.tools.factory import ToolFactory
    
    factory = ToolFactory()
    factory.generate_all_tools()
"""
import yaml
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from typing import Dict, Any, List, Optional
import logging
import re

logger = logging.getLogger(__name__)


# Type mapping from YAML types to Python types
TYPE_MAPPING = {
    "string": "str",
    "integer": "int",
    "float": "float",
    "boolean": "bool",
    "array": "List[Any]",
    "object": "Dict[str, Any]",
}


class ToolFactory:
    """Factory for generating tools from YAML configurations."""
    
    @staticmethod
    def _python_literal(value: Any) -> str:
        """Render a Python literal suitable for generated code."""

        if isinstance(value, str):
            return repr(value)
        if isinstance(value, bool):
            return "True" if value else "False"
        if value is None:
            return "None"
        if isinstance(value, (int, float)):
            return str(value)
        if isinstance(value, (list, dict, tuple, set)):
            return repr(value)
        return repr(value)

    @staticmethod
    def _slugify(text: str, fallback: str = "example") -> str:
        """Convert text into a slug suitable for identifiers."""

        slug = re.sub(r"[^a-z0-9]+", "_", text.lower())
        slug = slug.strip("_")
        return slug or fallback

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize the tool factory.
        
        Args:
            project_root: Optional project root path. If None, auto-detects from module location.
        """
        if project_root is None:
            # Auto-detect: go up from src/pydantic_ai_integration/tools/factory to project root
            project_root = Path(__file__).parent.parent.parent.parent.parent
        
        self.project_root = project_root
        self.config_dir = project_root / "config" / "tools"
        self.templates_dir = Path(__file__).parent / "templates"
        self.output_dir = Path(__file__).parent.parent / "generated"
        
        logger.info(f"Tool Factory initialized:")
        logger.info(f"  Config dir: {self.config_dir}")
        logger.info(f"  Templates dir: {self.templates_dir}")
        logger.info(f"  Output dir: {self.output_dir}")
        
        # Setup Jinja2 environment
        self.jinja_env = Environment(
            loader=FileSystemLoader(str(self.templates_dir)),
            trim_blocks=True,
            lstrip_blocks=True
        )
    
    def load_tool_config(self, yaml_file: Path) -> Dict[str, Any]:
        """Load and enrich tool configuration from YAML."""

        logger.info(f"Loading {yaml_file.name}...")

        with open(yaml_file, "r") as f:
            config = yaml.safe_load(f)

        # Store YAML path for folder structure generation
        config['_yaml_path'] = yaml_file

        # Validate required fields at a high level
        required_fields = ["name", "description", "category", "parameters"]
        for field in required_fields:
            if field not in config:
                raise ValueError(f"Missing required field: {field}")

        # Basic defaults
        config.setdefault("display_name", config["name"].replace("_", " ").title())
        config.setdefault("version", "1.0.0")
        config.setdefault("tags", [])
        config.setdefault("business_rules", {})

        # Business rule defaults
        business_rules = config["business_rules"]
        business_rules.setdefault("enabled", True)
        business_rules.setdefault("requires_auth", True)
        business_rules.setdefault("required_permissions", [])
        business_rules.setdefault("requires_casefile", False)
        business_rules.setdefault("timeout_seconds", 30)

        # Session and casefile policies
        session_defaults = {
            "requires_active_session": True,
            "allow_new_session": False,
            "allow_session_resume": True,
            "session_event_type": "request",
            "log_request_payload": True,
            "log_full_response": True,
        }
        session_policies = config.setdefault("session_policies", {})
        for key, value in session_defaults.items():
            session_policies.setdefault(key, value)

        casefile_defaults = {
            "requires_casefile": business_rules.get("requires_casefile", False),
            "allowed_casefile_states": ["active"],
            "create_if_missing": False,
            "enforce_access_control": True,
            "audit_casefile_changes": True,
        }
        casefile_policies = config.setdefault("casefile_policies", {})
        for key, value in casefile_defaults.items():
            casefile_policies.setdefault(key, value)

        # Implementation defaults
        implementation = config.setdefault("implementation", {})
        impl_type = implementation.get("type") or implementation.get("template") or "simple"
        implementation["type"] = impl_type
        if impl_type == "simple":
            implementation.setdefault("simple", {})
        elif impl_type == "api_call":
            implementation.setdefault("api_call", {})
            # Validate method_name exists in MANAGED_METHODS registry
            api_call = implementation["api_call"]
            method_name = api_call.get("method_name")
            if method_name:
                from ...method_registry import validate_method_exists, get_method_definition
                if validate_method_exists(method_name):
                    # Enrich with method metadata
                    method_def = get_method_definition(method_name)
                    api_call["_method_metadata"] = {
                        "service_name": method_def.metadata.service_name,
                        "module_path": method_def.metadata.module_path,
                        "request_model": method_def.models.request_model_name,
                        "response_model": method_def.models.response_model_name,
                        "required_permissions": method_def.business_rules.required_permissions,
                        "requires_casefile": method_def.business_rules.requires_casefile,
                    }
                    logger.info(f"  ✓ Method '{method_name}' found in MANAGED_METHODS registry")
                else:
                    logger.warning(f"  ⚠ Method '{method_name}' not found in MANAGED_METHODS registry (will validate at generation)")
        elif impl_type == "data_transform":
            implementation.setdefault("data_transform", {})
        elif impl_type == "composite":
            implementation.setdefault("composite", {})
        else:
            raise ValueError(f"Unsupported implementation type: {impl_type}")

        # Return contract defaults
        returns = config.setdefault("returns", {})
        returns.setdefault("type", "object")
        returns.setdefault("description", "Tool result payload")
        returns.setdefault("properties", {})
        returns.setdefault("required", [])

        # Audit event defaults
        audit_defaults = {
            "success_event": "tool_success",
            "failure_event": "tool_failure",
            "log_response_fields": [],
            "redact_fields": [],
            "emit_casefile_event": True,
        }
        audit_events = config.setdefault("audit_events", {})
        for key, value in audit_defaults.items():
            audit_events.setdefault(key, value)

        # Normalise collections
        config["examples"] = config.get("examples", [])
        config["error_scenarios"] = config.get("error_scenarios", [])

        # Prepare helper data for examples and defaults
        example_inputs = [example.get("input", {}) for example in config["examples"]]
        fallback_examples = {
            "string": "example",
            "integer": 1,
            "float": 1.0,
            "boolean": True,
            "array": [],
            "object": {},
        }

        # Process parameters
        for param in config["parameters"]:
            param.setdefault("required", False)
            param.setdefault("description", "")
            param_type = param.get("type", "string")
            param["python_type"] = TYPE_MAPPING.get(param_type, "str")

            # Determine example value (prefer explicit examples)
            example_raw_value = None
            for example_input in example_inputs:
                if param["name"] in example_input:
                    example_raw_value = example_input[param["name"]]
                    break

            if example_raw_value is None:
                if "default" in param:
                    example_raw_value = param.get("default")
            if example_raw_value is None:
                # Fallback by type
                template_value = fallback_examples.get(param_type, None)
                if isinstance(template_value, list):
                    example_raw_value = list(template_value)
                elif isinstance(template_value, dict):
                    example_raw_value = dict(template_value)
                else:
                    example_raw_value = template_value

            param["example_raw_value"] = example_raw_value
            param["example_value"] = self._python_literal(example_raw_value)

            # Determine default for generated code
            default_raw = param.get("default", None)
            if default_raw is None and not param["required"]:
                param["default_value"] = "None"
            elif default_raw is not None:
                param["default_value"] = self._python_literal(default_raw)
            else:
                param["default_value"] = None

        # Process examples for test/template consumption
        processed_examples: List[Dict[str, Any]] = []
        for idx, example in enumerate(config["examples"]):
            description = example.get("description") or f"Example {idx + 1}"
            context_block = example.get("context", {})
            session_block = context_block.get("session", {})
            permissions = context_block.get("permissions", [])
            input_payload = example.get("input", {})
            expected_output = example.get("expected_output", {})

            processed_examples.append(
                {
                    "name": self._slugify(description, f"example_{idx + 1}"),
                    "description": description,
                    "context_user_id": self._python_literal(session_block.get("user_id", "test_user")),
                    "context_session_id": self._python_literal(session_block.get("session_id", "test_session")),
                    "context_casefile_id": self._python_literal(session_block.get("casefile_id")) if session_block.get("casefile_id") else None,
                    "permissions_literal": self._python_literal(permissions) if permissions else None,
                    "input_kwargs_literal": [
                        {
                            "name": param["name"],
                            "value": self._python_literal(input_payload[param["name"]]),
                        }
                        for param in config["parameters"]
                        if param["name"] in input_payload
                    ],
                    "input_raw": {
                        name: input_payload[name] for name in input_payload
                    },
                    "expected_output_literal": self._python_literal(expected_output),
                    "expect_casefile_changes": example.get("expect_casefile_changes", False),
                }
            )

        config["processed_examples"] = processed_examples
        config["primary_example"] = processed_examples[0] if processed_examples else None

        # Prepare error scenarios
        base_inputs: Dict[str, Any] = {}
        if processed_examples:
            base_inputs = dict(processed_examples[0]["input_raw"])
        else:
            for param in config["parameters"]:
                if param["required"]:
                    base_inputs[param["name"]] = param["example_raw_value"]

        processed_errors: List[Dict[str, Any]] = []
        for idx, scenario in enumerate(config["error_scenarios"]):
            description = scenario.get("description") or f"Error {idx + 1}"
            override_inputs = scenario.get("input", {})
            expected_error = scenario.get("expected_error", {})

            scenario_inputs = dict(base_inputs)
            scenario_inputs.update(override_inputs)

            processed_errors.append(
                {
                    "name": self._slugify(description, f"error_{idx + 1}"),
                    "description": description,
                    "input_kwargs_literal": [
                        {
                            "name": param["name"],
                            "value": self._python_literal(scenario_inputs[param["name"]]),
                        }
                        for param in config["parameters"]
                        if param["name"] in scenario_inputs
                    ],
                    "error_type": expected_error.get("type", "Exception"),
                    "error_message": expected_error.get("message"),
                }
            )

        config["processed_error_tests"] = processed_errors
        config["requires_validation_error_import"] = any(
            error["error_type"] == "ValidationError" for error in processed_errors
        )

        config["has_examples"] = bool(processed_examples)
        config["has_error_tests"] = bool(processed_errors)

        # Derive helpful paths for templates
        yaml_relative_path = yaml_file.relative_to(self.config_dir)
        config["yaml_relative_path"] = str(yaml_relative_path).replace("\\", "/")

        module_parts = [part for part in yaml_relative_path.parent.parts if part]
        generated_base = "src.pydantic_ai_integration.tools.generated"
        module_package_suffix = ".".join(module_parts)
        config["generated_module_package"] = (
            f"{generated_base}.{module_package_suffix}" if module_package_suffix else generated_base
        )
        config["generated_module_import"] = f"{config['generated_module_package']}.{config['name']}"

        return config
    
    def validate_config(self, config: Dict[str, Any]) -> List[str]:
        """Validate tool configuration and return list of issues.
        
        Args:
            config: Tool configuration dictionary
            
        Returns:
            List of validation issue strings (empty if valid)
        """
        issues = []
        
        # Check name format (lowercase, underscores only)
        if not config['name'].replace('_', '').islower():
            issues.append(f"Tool name must be lowercase with underscores: {config['name']}")
        
        # Check for duplicate parameter names
        param_names = [p['name'] for p in config['parameters']]
        if len(param_names) != len(set(param_names)):
            issues.append("Duplicate parameter names found")
        
        # Validate parameter constraints
        for param in config['parameters']:
            if param['type'] in ['integer', 'float']:
                if 'min_value' in param and 'max_value' in param:
                    if param['min_value'] > param['max_value']:
                        issues.append(f"Parameter {param['name']}: min_value > max_value")
            
            if param['type'] in ['string', 'array']:
                if 'min_length' in param and 'max_length' in param:
                    if param['min_length'] > param['max_length']:
                        issues.append(f"Parameter {param['name']}: min_length > max_length")
        
        # Validate api_call implementation references valid method
        implementation = config.get('implementation', {})
        if implementation.get('type') == 'api_call':
            api_call = implementation.get('api_call', {})
            method_name = api_call.get('method_name')
            if method_name:
                from ...method_registry import validate_method_exists
                if not validate_method_exists(method_name):
                    issues.append(
                        f"api_call.method_name '{method_name}' not found in MANAGED_METHODS registry. "
                        f"Ensure method is registered with @register_service_method decorator."
                    )
        
        return issues
    
    def generate_tool(self, config: Dict[str, Any]) -> Path:
        """Generate tool implementation from config.
        
        Args:
            config: Tool configuration dictionary
            
        Returns:
            Path to generated tool file
        """
        template = self.jinja_env.get_template('tool_template.py.jinja2')
        output = template.render(tool=config)
        
        # Use YAML path structure (domain/subdomain) from config
        yaml_path = config.get('_yaml_path', Path('general'))
        relative_path = yaml_path.relative_to(self.config_dir).parent
        
        # Create output directory matching YAML structure
        output_subdir = self.output_dir / relative_path
        output_subdir.mkdir(parents=True, exist_ok=True)
        
        # Ensure each level has __init__.py
        current = self.output_dir
        for part in relative_path.parts:
            current = current / part
            init_file = current / "__init__.py"
            if not init_file.exists():
                init_file.write_text(f'"""Generated tools in {part}."""\n')
        
        # Write tool file
        output_file = output_subdir / f"{config['name']}.py"
        
        with open(output_file, 'w') as f:
            f.write(output)
        
        logger.info(f"Generated tool: {output_file.relative_to(self.project_root)}")
        return output_file
    
    def generate_init_files(self):
        """Generate __init__.py files for generated packages."""
        # src/pydantic_ai_integration/tools/generated/__init__.py
        init_file = self.output_dir / "__init__.py"
        if not init_file.exists():
            init_file.parent.mkdir(parents=True, exist_ok=True)
            init_content = '''"""Auto-generated tools from YAML configurations.

This package contains tools generated by the Tool Factory.
DO NOT manually edit files in this package - they will be overwritten.

All tools are automatically registered with MANAGED_TOOLS when imported.
"""
'''
            init_file.write_text(init_content)
            logger.info(f"Created {init_file.relative_to(self.project_root)}")
    
    def process_tool(self, yaml_file: Path, validate_only: bool = False) -> bool:
        """Process a single tool configuration.
        
        Args:
            yaml_file: Path to YAML configuration file
            validate_only: If True, only validate without generating code
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Load configuration
            config = self.load_tool_config(yaml_file)
            
            # Validate
            issues = self.validate_config(config)
            if issues:
                logger.error(f"Validation errors in {yaml_file.name}:")
                for issue in issues:
                    logger.error(f"  - {issue}")
                return False
            
            logger.info(f"Validation passed for {config['name']}")
            
            if validate_only:
                return True
            
            # Generate code
            self.generate_tool(config)
            
            return True
            
        except Exception as e:
            logger.error(f"Error processing {yaml_file.name}: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def generate_all_tools(self, validate_only: bool = False) -> Dict[str, bool]:
        """Process all YAML files in config/tools/ (recursive).
        
        Args:
            validate_only: If True, only validate without generating code
            
        Returns:
            Dictionary mapping tool names to success status
        """
        if not self.config_dir.exists():
            logger.error(f"Config directory not found: {self.config_dir}")
            return {}
        
        # Recursive glob to find YAMLs in subdirectories
        yaml_files = list(self.config_dir.glob("**/*.yaml")) + list(self.config_dir.glob("**/*.yml"))
        
        if not yaml_files:
            logger.warning(f"No YAML files found in {self.config_dir}")
            return {}
        
        logger.info(f"Found {len(yaml_files)} tool definition(s)")
        
        results = {}
        for yaml_file in yaml_files:
            tool_name = yaml_file.stem
            success = self.process_tool(yaml_file, validate_only)
            results[tool_name] = success
        
        if not validate_only:
            self.generate_init_files()
        
        success_count = sum(1 for v in results.values() if v)
        logger.info(f"Successfully processed: {success_count}/{len(yaml_files)} tools")
        
        return results


def generate_tools_cli():
    """Command-line interface for tool generation."""
    import argparse
    import sys
    
    parser = argparse.ArgumentParser(description="Generate tools from YAML configurations")
    parser.add_argument(
        'tool_name',
        nargs='?',
        help='Specific tool to generate (optional, generates all if omitted)'
    )
    parser.add_argument(
        '--validate-only',
        action='store_true',
        help='Only validate YAML, do not generate code'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    
    args = parser.parse_args()
    
    # Configure logging
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format='%(message)s'
    )
    
    factory = ToolFactory()
    
    print(f"\n🏭 Tool Factory Starting...")
    print(f"📁 Config directory: {factory.config_dir}")
    print(f"📁 Output directory: {factory.output_dir}")
    print()
    
    if args.tool_name:
        # Process specific tool - search recursively in subdirectories
        yaml_files = list(factory.config_dir.glob(f"**/{args.tool_name}.yaml")) + list(factory.config_dir.glob(f"**/{args.tool_name}.yml"))
        if not yaml_files:
            print(f"❌ Tool configuration not found: {args.tool_name}.yaml (searched recursively in {factory.config_dir})")
            sys.exit(1)
        elif len(yaml_files) > 1:
            print(f"❌ Multiple tool configurations found for '{args.tool_name}':")
            for yf in yaml_files:
                print(f"  - {yf.relative_to(factory.config_dir)}")
            print("Please specify the full path or ensure unique tool names.")
            sys.exit(1)
        
        yaml_file = yaml_files[0]
        success = factory.process_tool(yaml_file, args.validate_only)
        print()
        print("=" * 60)
        print(f"{'✅' if success else '❌'} {'Validated' if args.validate_only else 'Generated'}: {args.tool_name}")
        print("=" * 60)
        sys.exit(0 if success else 1)
    else:
        # Process all tools
        results = factory.generate_all_tools(args.validate_only)
        print()
        print("=" * 60)
        success_count = sum(1 for v in results.values() if v)
        print(f"✅ Successfully processed: {success_count}/{len(results)} tools")
        if success_count < len(results):
            print(f"❌ Failed: {len(results) - success_count} tools")
        print("=" * 60)
        sys.exit(0 if success_count == len(results) else 1)


if __name__ == "__main__":
    generate_tools_cli()
