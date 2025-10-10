#!/usr/bin/env python3
"""
Method Tools Generator v1.0
Generates versioned tool YAMLs from methods_inventory_v1.yaml

This script creates standardized tool definitions with:
- R-A-R pattern documentation
- Parameter separation (method_params vs tool_params)
- Data contract references
- Classification inheritance
- Comprehensive examples

Usage:
    python scripts/generate_method_tools.py

Output:
    Creates /config/methodtools_v1/ directory with tool YAMLs
"""

import os
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml

class MethodToolsGenerator:
    """Generates tool YAMLs from methods inventory"""

    def __init__(self, workspace_root: str):
        self.workspace_root = Path(workspace_root)
        self.config_dir = self.workspace_root / "config"
        self.methods_file = self.config_dir / "methods_inventory_v1.yaml"
        self.models_file = self.config_dir / "models_inventory_v1.yaml"
        self.output_dir = self.config_dir / "methodtools_v1"

        # Load source data
        self.methods_data = self._load_yaml(self.methods_file)
        self.models_data = self._load_yaml(self.models_file)

        # Create output directory
        self.output_dir.mkdir(exist_ok=True)

    def _load_yaml(self, file_path: Path) -> dict[str, Any]:
        """Load YAML file with error handling"""
        try:
            with open(file_path, encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            raise RuntimeError(f"Failed to load {file_path}: {e}") from e

    def _get_model_info(self, model_name: str) -> dict[str, Any] | None:
        """Get model information from models inventory"""
        # This would need to be implemented based on models_inventory structure
        # For now, return basic info
        return {
            "name": model_name,
            "classification": f"operations/{model_name.lower()}"
        }

    def _extract_method_params(self, method: dict[str, Any]) -> list[dict[str, Any]]:
        """Extract method parameters from signature or models"""
        # This is a simplified extraction - in practice would parse the signature
        # or look up model fields from models_inventory
        method_name = method['name']

        # Basic parameter extraction based on common patterns
        param_patterns = {
            'create_casefile': [
                {'name': 'title', 'type': 'string', 'required': True, 'description': 'Title of the casefile'},
                {'name': 'description', 'type': 'string', 'required': False, 'description': 'Optional description'},
                {'name': 'tags', 'type': 'array', 'required': False, 'description': 'Tags for categorization'}
            ],
            'get_casefile': [
                {'name': 'casefile_id', 'type': 'string', 'required': True, 'description': 'Casefile identifier'}
            ],
            # Add more patterns as needed
        }

        return param_patterns.get(method_name, [
            {'name': 'request', 'type': 'object', 'required': True, 'description': 'Request object'}
        ])

    def _generate_tool_yaml(self, method: dict[str, Any], service: dict[str, Any], compound_key: str) -> dict[str, Any]:
        """Generate complete tool YAML structure"""
        method_name = method['name']
        service_name = service['name']

        tool_name = f"{method_name}_tool"
        category = f"{method.get('classification', {}).get('domain', 'general')}_management"

        return {
            'name': tool_name,
            'description': f"Tool wrapper for {service_name}.{method_name} with validation and execution control",
            'category': category,
            'version': '1.0.0',
            'tags': [
                method.get('classification', {}).get('domain', 'general'),
                method.get('classification', {}).get('capability', 'process'),
                method_name.split('_')[0]  # First part of method name
            ],

            # Removed: rar_pattern - now in separate documentation index

            'method_reference': {
                'service': service_name,
                'method': method_name,
                'classification': method.get('classification', {})
            },

            'method_params': self._extract_method_params(method),

            'tool_params': [
                {
                    'name': 'timeout_seconds',
                    'type': 'integer',
                    'required': False,
                    'description': 'Maximum execution time in seconds',
                    'default': method.get('business_rules', {}).get('timeout_seconds', 30),
                    'min_value': 5,
                    'max_value': 300
                },
                {
                    'name': 'dry_run',
                    'type': 'boolean',
                    'required': False,
                    'description': 'Preview mode without actual execution',
                    'default': False
                }
            ],

            'implementation': {
                'type': 'method_wrapper',
                'method_wrapper': {
                    'method_name': compound_key,  # Use compound key for unique identification
                    'parameter_mapping': {
                        'method_params': [p['name'] for p in self._extract_method_params(method)],
                        'tool_params': ['timeout_seconds', 'dry_run']
                    }
                }
            },

            'business_rules': method.get('business_rules', {}),

            'examples': [
                {
                    'description': f'Basic {method_name} operation',
                    'input': {p['name']: f'sample_{p["name"]}' for p in self._extract_method_params(method)[:2]},
                    'expected_output': {'result': 'success', 'data': {}}
                }
            ],

            'data_contracts': {
                'request_model': method.get('models', {}).get('request', f'{method_name.title()}Request'),
                'response_model': method.get('models', {}).get('response', f'{method_name.title()}Response'),
                'canonical_models': [],  # Would be populated from models_inventory
                'module': method.get('models', {}).get('module', 'src.pydantic_models.operations')
            },

            'dependencies': {
                'methods': [method_name],
                'models': [
                    method.get('models', {}).get('request', f'{method_name.title()}Request'),
                    method.get('models', {}).get('response', f'{method_name.title()}Response')
                ],
                'services': [service_name]
            },

            'compatibility': {
                'method_version': '1.0.0',
                'schema_version': '1.0',
                'requires_auth': method.get('business_rules', {}).get('requires_auth', True)
            }
        }

    def generate_tools(self):
        """Generate tool YAMLs for all methods"""
        print(f"Generating method tools in {self.output_dir}")

        total_methods = 0

        for service in self.methods_data.get('services', []):
            service_name = service['name']
            print(f"Processing {service_name}...")

            for method in service.get('methods', []):
                method_name = method['name']
                service_name = service['name']
                
                # Use compound key to avoid duplicates
                compound_key = f"{service_name}.{method_name}"
                tool_name = f"{compound_key}_tool".replace(".", "_")

                # Generate tool YAML
                tool_data = self._generate_tool_yaml(method, service, compound_key)

                # Write to file
                output_file = self.output_dir / f"{tool_name}.yaml"
                with open(output_file, 'w', encoding='utf-8') as f:
                    yaml.dump(tool_data, f, default_flow_style=False, sort_keys=False)

                print(f"  ✓ Generated {tool_name}.yaml ({compound_key})")
                total_methods += 1

        print(f"\nGenerated {total_methods} method tools")

        # Update README with actual file list
        self._update_readme(total_methods)

    def _update_readme(self, total_methods: int):
        """Update README with generated file list"""
        readme_file = self.output_dir / "README.md"

        if readme_file.exists():
            with open(readme_file, encoding='utf-8') as f:
                content = f.read()

            # Update the generated count
            content = content.replace(
                "# Generated: October 10, 2025",
                f"# Generated: {datetime.now().strftime('%B %d, %Y')}\n# Total Tools: {total_methods}"
            )

            with open(readme_file, 'w', encoding='utf-8') as f:
                f.write(content)

def main():
    """Main entry point"""
    workspace_root = os.getenv('WORKSPACE_ROOT', str(Path(__file__).parent.parent))

    generator = MethodToolsGenerator(workspace_root)
    generator.generate_tools()

    print("\nMethod tools generation complete!")
    print(f"Output directory: {generator.output_dir}")

if __name__ == '__main__':
    main()
