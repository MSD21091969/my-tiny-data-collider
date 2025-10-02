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

logger = logging.getLogger(__name__)


# Type mapping from YAML types to Python types
TYPE_MAPPING = {
    "string": "str",
    "integer": "int",
    "float": "float",
    "boolean": "bool",
    "array": "List",
    "object": "Dict",
}


class ToolFactory:
    """Factory for generating tools from YAML configurations."""
    
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
        """Load and validate tool configuration from YAML.
        
        Args:
            yaml_file: Path to YAML configuration file
            
        Returns:
            Parsed and validated configuration dictionary
            
        Raises:
            ValueError: If required fields are missing
        """
        logger.info(f"Loading {yaml_file.name}...")
        
        with open(yaml_file, 'r') as f:
            config = yaml.safe_load(f)
        
        # Validate required fields
        required_fields = ['name', 'description', 'category', 'parameters']
        for field in required_fields:
            if field not in config:
                raise ValueError(f"Missing required field: {field}")
        
        # Set defaults
        config.setdefault('display_name', config['name'].replace('_', ' ').title())
        config.setdefault('version', '1.0.0')
        config.setdefault('tags', [])
        config.setdefault('business_rules', {})
        config.setdefault('implementation', {})
        
        # Set business rule defaults
        br = config['business_rules']
        br.setdefault('enabled', True)
        br.setdefault('requires_auth', True)
        br.setdefault('required_permissions', [])
        br.setdefault('requires_casefile', False)
        br.setdefault('timeout_seconds', 30)
        
        # Process parameters
        for param in config['parameters']:
            param['python_type'] = TYPE_MAPPING.get(param['type'], 'str')
            
            # Generate example values for tests
            if param['type'] == 'string':
                param['example_value'] = f'"{param.get("default", "example")}"'
            elif param['type'] == 'integer':
                param['example_value'] = str(param.get('default', 1))
            elif param['type'] == 'float':
                param['example_value'] = str(param.get('default', 1.0))
            elif param['type'] == 'boolean':
                param['example_value'] = str(param.get('default', True)).lower()
            else:
                param['example_value'] = 'None'
            
            # Format default value for Python code
            if param.get('default') is None:
                param['default_value'] = 'None'
            elif param['type'] == 'string':
                param['default_value'] = f'"{param["default"]}"'
            else:
                param['default_value'] = str(param['default'])
        
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
        
        # Write to file
        output_file = self.output_dir / f"{config['name']}.py"
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w') as f:
            f.write(output)
        
        logger.info(f"Generated tool: {output_file.relative_to(self.project_root)}")
        return output_file
    
    def generate_tests(self, config: Dict[str, Any]) -> Path:
        """Generate test suite from config.
        
        Args:
            config: Tool configuration dictionary
            
        Returns:
            Path to generated test file
        """
        template = self.jinja_env.get_template('test_template.py.jinja2')
        output = template.render(tool=config)
        
        # Write to tests directory (at project root level)
        test_output_dir = self.project_root / "tests" / "generated"
        test_output_dir.mkdir(parents=True, exist_ok=True)
        
        output_file = test_output_dir / f"test_{config['name']}.py"
        
        with open(output_file, 'w') as f:
            f.write(output)
        
        logger.info(f"Generated tests: {output_file.relative_to(self.project_root)}")
        return output_file
    
    def generate_init_files(self):
        """Generate __init__.py files for generated packages."""
        # src/pydantic_ai_integration/tools/generated/__init__.py
        init_file = self.output_dir / "__init__.py"
        if not init_file.exists():
            init_content = '''"""Auto-generated tools from YAML configurations.

This package contains tools generated by the Tool Factory.
DO NOT manually edit files in this package - they will be overwritten.

All tools are automatically registered with MANAGED_TOOLS when imported.
"""
'''
            init_file.write_text(init_content)
            logger.info(f"Created {init_file.relative_to(self.project_root)}")
        
        # tests/generated/__init__.py
        test_init = self.project_root / "tests" / "generated" / "__init__.py"
        if not test_init.exists():
            test_init.write_text('"""Auto-generated test suites."""\n')
            logger.info(f"Created {test_init.relative_to(self.project_root)}")
    
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
            self.generate_tests(config)
            
            return True
            
        except Exception as e:
            logger.error(f"Error processing {yaml_file.name}: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def generate_all_tools(self, validate_only: bool = False) -> Dict[str, bool]:
        """Process all YAML files in config/tools/.
        
        Args:
            validate_only: If True, only validate without generating code
            
        Returns:
            Dictionary mapping tool names to success status
        """
        if not self.config_dir.exists():
            logger.error(f"Config directory not found: {self.config_dir}")
            return {}
        
        yaml_files = list(self.config_dir.glob("*.yaml")) + list(self.config_dir.glob("*.yml"))
        
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
        # Process specific tool
        yaml_file = factory.config_dir / f"{args.tool_name}.yaml"
        if not yaml_file.exists():
            print(f"❌ Tool configuration not found: {yaml_file}")
            sys.exit(1)
        
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
