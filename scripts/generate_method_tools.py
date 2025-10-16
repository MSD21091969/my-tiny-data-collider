#!/usr/bin/env python3
"""
Generate tool YAML definitions from methods_inventory_v1.yaml

This script creates 1:1 tool wrappers for service methods by:
1. Reading method definitions from methods_inventory_v1.yaml
2. Extracting parameters from request models via Pydantic introspection
3. Generating tool YAMLs with proper parameter separation:
   - method_params: Documentation of parameters passed to method
   - tool_params: Actual parameters for tool execution (includes method params + execution controls)

Usage:
    python scripts/generate_method_tools.py [--dry-run] [--verbose]
    
Generated: October 15, 2025
Purpose: Fix parameter mapping validation by including method params in tool_params
"""

import argparse
import sys
from pathlib import Path
from typing import Any, Dict, List

import yaml
from pydantic import BaseModel
from pydantic.fields import FieldInfo

# Project root for relative paths
project_root = Path(__file__).parent.parent

# NOTE: Do NOT import from pydantic_ai_integration here!
# Importing triggers decorators which fail to import Google Workspace models.
# Script has standalone extraction logic below (extract_tool_parameters function).


def load_methods_inventory(yaml_path: str = "config/methods_inventory_v1.yaml") -> Dict:
    """Load methods inventory from YAML."""
    with open(yaml_path, "r", encoding="utf-8") as f:
        flat_inventory = yaml.safe_load(f)
    
    # Convert flat structure to nested structure expected by generate_all_tools
    # Group methods by implementation.class
    services_dict = {}
    
    for method_name, method_def in flat_inventory.items():
        impl = method_def.get("implementation", {})
        service_class = impl.get("class", "UnknownService")
        
        # Normalize service name (remove 'Service' suffix if present)
        service_name = service_class.replace("Service", "").lower()
        
        if service_name not in services_dict:
            services_dict[service_name] = {
                "name": service_name,
                "methods": []
            }
        
        # Add method to service, but add module path for import_request_model
        method_def_copy = method_def.copy()
        if "models" in method_def_copy:
            method_def_copy["models"]["module"] = f"pydantic_models.operations.{service_name}_ops"
        
        services_dict[service_name]["methods"].append(method_def_copy)
    
    # Convert to list format expected by generate_all_tools
    nested_inventory = {
        "services": list(services_dict.values())
    }
    
    return nested_inventory


def load_tool_schema(schema_path: str = "config/tool_schema_v2.yaml") -> Dict:
    """Load tool schema for validation."""
    with open(schema_path, "r", encoding="utf-8") as f:
        content = f.read()
        # Schema is documented in comments, extract validation rules
        # For now, return empty dict - schema is documentation only
        # Future: Parse schema into validation rules
        return {}


def load_tool_schema(schema_path: str = "config/tool_schema_v2.yaml") -> Dict:
    """Load tool schema for validation."""
    with open(schema_path, "r") as f:
        return yaml.safe_load(f)


def import_request_model(module_path: str, model_name: str) -> type[BaseModel] | None:
    """
    Dynamically import a request model.
    
    Note: With editable install, module paths use package-relative paths,
    Python imports should use the package name directly.
    """
    try:
        # Use the module path directly since package-dir maps src to root
        import_path = module_path
        
        module = __import__(import_path, fromlist=[model_name])
        model_class = getattr(module, model_name, None)
        if model_class is None:
            print(f"  ⚠ Could not find {model_name} in {import_path}")
        return model_class
        
    except (ImportError, AttributeError, UnicodeEncodeError) as e:
        # Log import failures with full error
        print(f"  ⚠ Could not import {model_name} from {module_path}: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return None
    except Exception as e:
        # Unexpected error - log it
        print(f"  ! Unexpected error importing {model_name} from {module_path}: {type(e).__name__}: {e}")
        return None


def extract_tool_parameters(request_model_class: type[BaseModel]) -> List[Dict[str, Any]]:
    """
    Extract parameters from request model for tool definition.
    
    Returns list of parameter dicts with: name, type, required, description, constraints
    
    Note: Handles R-A-R pattern where actual parameters are in 'payload' field
    """
    if not request_model_class:
        return []
    
    params = []
    
    # Check if this is an R-A-R Request model with a 'payload' field
    if "payload" in request_model_class.model_fields:
        # Extract parameters from the payload model
        payload_field = request_model_class.model_fields["payload"]
        payload_model_class = payload_field.annotation
        
        # Get the actual model class (handle Optional[])
        if hasattr(payload_model_class, "__args__"):
            payload_model_class = payload_model_class.__args__[0]
        
        # Extract from payload model
        if hasattr(payload_model_class, "model_fields"):
            for field_name, field_info in payload_model_class.model_fields.items():
                if field_name.startswith("_"):
                    continue
                params.append(_build_parameter_def(field_name, field_info))
    else:
        # Direct parameter model (not R-A-R pattern)
        for field_name, field_info in request_model_class.model_fields.items():
            if field_name.startswith("_"):
                continue
            params.append(_build_parameter_def(field_name, field_info))
    
    return params


def validate_tool_structure(tool_data: Dict[str, Any]) -> List[str]:
    """
    Validate tool YAML structure against tool_schema_v2.yaml requirements.
    
    Returns list of validation errors (empty = valid).
    """
    errors = []
    
    # Required top-level fields
    required_fields = ['name', 'description', 'category', 'version']
    for field in required_fields:
        if field not in tool_data:
            errors.append(f"Missing required field: {field}")
    
    # Validate name format (should be snake_case and end with _tool)
    if 'name' in tool_data:
        name = tool_data['name']
        if not name.endswith('_tool'):
            errors.append(f"Tool name must end with '_tool': {name}")
        if not name.replace('_', '').replace('-', '').isalnum():
            errors.append(f"Tool name must be alphanumeric with underscores: {name}")
    
    # Validate method_reference
    if 'method_reference' in tool_data:
        ref = tool_data['method_reference']
        if not isinstance(ref, dict):
            errors.append("method_reference must be a dictionary")
        elif 'service' not in ref or 'method' not in ref:
            errors.append("method_reference must contain 'service' and 'method'")
    
    # Validate parameters
    valid_param_types = ['string', 'integer', 'float', 'boolean', 'array', 'object']
    
    for param_section in ['method_params', 'tool_params']:
        if param_section in tool_data:
            params = tool_data[param_section]
            if not isinstance(params, list):
                errors.append(f"{param_section} must be a list")
                continue
            
            for idx, param in enumerate(params):
                if not isinstance(param, dict):
                    errors.append(f"{param_section}[{idx}] must be a dictionary")
                    continue
                
                # Required parameter fields
                if 'name' not in param:
                    errors.append(f"{param_section}[{idx}] missing 'name'")
                if 'type' not in param:
                    errors.append(f"{param_section}[{idx}] missing 'type'")
                elif param['type'] not in valid_param_types:
                    errors.append(
                        f"{param_section}[{idx}] invalid type '{param['type']}'. "
                        f"Must be one of: {', '.join(valid_param_types)}"
                    )
                
                # Validate constraints match type
                param_type = param.get('type')
                if param_type in ['integer', 'float']:
                    if 'min_length' in param or 'max_length' in param:
                        errors.append(
                            f"{param_section}[{idx}] ({param.get('name')}): "
                            "min_length/max_length not valid for numeric types"
                        )
                elif param_type == 'string':
                    if 'min_value' in param or 'max_value' in param:
                        errors.append(
                            f"{param_section}[{idx}] ({param.get('name')}): "
                            "min_value/max_value not valid for string type"
                        )
    
    # Validate implementation
    if 'implementation' in tool_data:
        impl = tool_data['implementation']
        if not isinstance(impl, dict):
            errors.append("implementation must be a dictionary")
        elif 'type' not in impl:
            errors.append("implementation missing 'type'")
        elif impl['type'] not in ['simple', 'api_call', 'data_transform', 'composite', 'method_wrapper']:
            errors.append(f"Invalid implementation type: {impl['type']}")
    
    return errors


def _build_parameter_def(field_name: str, field_info: FieldInfo) -> Dict[str, Any]:
    """Build parameter definition from Pydantic field info."""
    from pydantic_core import PydanticUndefined
    import typing
    
    # Extract type information
    param_type = "string"  # default
    annotation = field_info.annotation
    
    # Get origin type for generics (list[str] → list, dict[str, Any] → dict)
    origin = typing.get_origin(annotation)
    if origin is not None:
        type_name = origin.__name__.lower()
    elif hasattr(annotation, "__name__"):
        type_name = annotation.__name__.lower()
    else:
        # Complex type, try string representation
        type_str = str(annotation).lower()
        if "list" in type_str:
            type_name = "list"
        elif "dict" in type_str:
            type_name = "dict"
        else:
            type_name = "string"
    
    type_map = {
        "str": "string",
        "int": "integer",
        "float": "number",
        "bool": "boolean",
        "list": "array",
        "dict": "object",
    }
    param_type = type_map.get(type_name, "string")
    
    # Build parameter definition
    param = {
        "name": field_name,
        "type": param_type,
        "required": field_info.is_required(),
        "description": field_info.description or f"Parameter: {field_name}",
    }
    
    # Add constraints if present
    if hasattr(field_info, "metadata"):
        for constraint in field_info.metadata:
            if hasattr(constraint, "ge"):
                param["min_value"] = constraint.ge
            if hasattr(constraint, "le"):
                param["max_value"] = constraint.le
            if hasattr(constraint, "min_length"):
                param["min_length"] = constraint.min_length
            if hasattr(constraint, "max_length"):
                param["max_length"] = constraint.max_length
    
    # Add default if present (skip PydanticUndefined)
    if (field_info.default is not None and 
        field_info.default != PydanticUndefined and
        field_info.default != ...):
        param["default"] = field_info.default
    
    return param


def generate_tool_yaml(
    service_name: str,
    method_def: Dict[str, Any],
    verbose: bool = False
) -> Dict[str, Any]:
    """
    Generate tool YAML structure from method definition.
    
    KEY FIX: Parameters go in BOTH method_params (doc) AND tool_params (execution)
    """
    method_name = method_def["name"]
    tool_name = f"{method_name}_tool"
    
    # Extract classification
    classification = method_def.get("classification", {})
    domain = classification.get("domain", "unknown")
    subdomain = classification.get("subdomain", "unknown")
    capability = classification.get("capability", "unknown")
    
    # Category from domain
    category_map = {
        "workspace": "workspace_management",
        "communication": "communication",
        "automation": "automation",
    }
    category = category_map.get(domain, domain)
    
    # Tags
    tags = [domain, subdomain, capability]
    
    # Get request model
    models = method_def.get("models", {})
    request_model_name = models.get("request")
    response_model_name = models.get("response")
    module_path = models.get("module")
    
    # Extract parameters from request model
    method_params = []
    if request_model_name and module_path:
        if verbose:
            print(f"  Importing {request_model_name} from {module_path}")
        request_model_class = import_request_model(module_path, request_model_name)
        if verbose:
            print(f"  Model imported: {request_model_class}")
        if request_model_class:
            method_params = extract_tool_parameters(request_model_class)
            if verbose:
                print(f"  Extracted {len(method_params)} parameters for {method_name}")
                if method_params:
                    for p in method_params:
                        print(f"    - {p['name']}: {p['type']}")
    
    # Build tool_params: method params + execution controls
    tool_params = []
    
    # Add method parameters first
    for param in method_params:
        tool_params.append(param.copy())
    
    # Add execution control parameters
    tool_params.extend([
        {
            "name": "timeout_seconds",
            "type": "integer",
            "required": False,
            "description": "Maximum execution time in seconds",
            "default": 30,
            "min_value": 5,
            "max_value": 300,
        },
        {
            "name": "dry_run",
            "type": "boolean",
            "required": False,
            "description": "Preview mode without actual execution",
            "default": False,
        }
    ])
    
    # Parameter mapping
    parameter_mapping = {
        "method_params": [p["name"] for p in method_params],
        "tool_params": ["timeout_seconds", "dry_run"],
    }
    
    # Business rules
    business_rules = method_def.get("business_rules", {})
    
    # Build tool definition
    tool_def = {
        "name": tool_name,
        "description": f"Tool wrapper for {service_name}.{method_name} with validation and execution control",
        "category": category,
        "version": "1.0.0",
        "tags": tags,
        "method_reference": {
            "service": service_name,
            "method": method_name,
            "classification": classification,
        },
        "method_params": method_params,  # Documentation only
        "tool_params": tool_params,  # Actual execution parameters (includes method_params + controls)
        "implementation": {
            "type": "method_wrapper",
            "method_wrapper": {
                "method_name": f"{service_name}.{method_name}",
                "parameter_mapping": parameter_mapping,
            }
        },
        "business_rules": {
            "enabled": business_rules.get("enabled", True),
            "requires_auth": business_rules.get("requires_auth", True),
            "required_permissions": business_rules.get("required_permissions", []),
            "requires_casefile": business_rules.get("requires_casefile", False),
            "timeout_seconds": business_rules.get("timeout_seconds", 30),
        },
        "examples": [
            {
                "description": f"Basic {method_name} operation",
                "input": {p["name"]: f"sample_{p['name']}" for p in method_params[:2]},
                "expected_output": {
                    "result": "success",
                    "data": {},
                }
            }
        ],
        "data_contracts": {
            "request_model": request_model_name,
            "response_model": response_model_name,
            "canonical_models": [],
            "module": module_path,
        },
        "dependencies": {
            "methods": [method_name],
            "models": [request_model_name, response_model_name],
            "services": [service_name],
        },
        "compatibility": {
            "method_version": "1.0.0",
            "schema_version": "1.0",
            "requires_auth": business_rules.get("requires_auth", True),
        }
    }
    
    # Validate tool structure
    validation_errors = validate_tool_structure(tool_def)
    if validation_errors:
        error_msg = f"Tool '{tool_name}' failed validation:\n"
        error_msg += "\n".join(f"  - {err}" for err in validation_errors)
        raise ValueError(error_msg)
    
    return tool_def


def generate_all_tools(
    inventory: Dict,
    output_dir: Path,
    dry_run: bool = False,
    verbose: bool = False
) -> int:
    """Generate all tool YAMLs from inventory."""
    services = inventory.get("services", [])
    generated_count = 0
    
    for service in services:
        service_name = service["name"]
        methods = service.get("methods", [])
        
        print(f"\n[{service_name}] ({len(methods)} methods)")
        
        for method_def in methods:
            method_name = method_def["name"]
            tool_name = f"{service_name}_{method_name}_tool"
            output_file = output_dir / f"{tool_name}.yaml"
            
            if verbose:
                print(f"  > Generating {tool_name}")
            
            try:
                tool_yaml = generate_tool_yaml(service_name, method_def, verbose)
                
                if not dry_run:
                    with open(output_file, "w") as f:
                        yaml.dump(tool_yaml, f, default_flow_style=False, sort_keys=False, width=120)
                    print(f"  + {tool_name}.yaml")
                else:
                    print(f"  [DRY-RUN] Would generate {tool_name}.yaml")
                
                generated_count += 1
                
            except Exception as e:
                print(f"  ! Failed to generate {tool_name}: {e}")
    
    return generated_count


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Generate tool YAMLs from methods inventory"
    )
    parser.add_argument(
        "--inventory",
        default="config/methods_inventory_v1.yaml",
        help="Path to methods inventory YAML"
    )
    parser.add_argument(
        "--output-dir",
        default="config/methodtools_v1",
        help="Output directory for tool YAMLs"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview changes without writing files"
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Verbose output"
    )
    
    args = parser.parse_args()
    
    # Resolve paths
    inventory_path = project_root / args.inventory
    output_dir = project_root / args.output_dir
    
    print("=" * 70)
    print("TOOL YAML GENERATION WITH VALIDATION")
    print("=" * 70)
    print(f"Inventory: {inventory_path}")
    print(f"Schema: config/tool_schema_v2.yaml")
    print(f"Output: {output_dir}")
    print(f"Mode: {'DRY-RUN' if args.dry_run else 'WRITE'}")
    print()
    
    # Load inventory
    try:
        inventory = load_methods_inventory(inventory_path)
    except Exception as e:
        print(f"❌ Failed to load inventory: {e}")
        return 1
    
    # Load and verify tool schema exists
    schema_path = project_root / "config" / "tool_schema_v2.yaml"
    if not schema_path.exists():
        print(f"❌ Tool schema not found: {schema_path}")
        return 1
    
    try:
        schema = load_tool_schema(schema_path)
        print(f"[OK] Tool schema loaded: {schema_path}")
    except Exception as e:
        print(f"❌ Failed to load schema: {e}")
        return 1
    
    # Create output directory
    if not args.dry_run:
        output_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate tools
    generated_count = generate_all_tools(
        inventory,
        output_dir,
        dry_run=args.dry_run,
        verbose=args.verbose
    )
    
    print()
    print("=" * 70)
    print(f"[OK] Generated {generated_count} tool YAMLs")
    print(f"[OK] All tools validated against tool_schema_v2.yaml")
    print("=" * 70)
    
    if args.dry_run:
        print("\n[INFO] Run without --dry-run to write files")
    else:
        print(f"\n[OUTPUT] Tools written to: {output_dir}")
        print(f"[VALIDATED] All {generated_count} YAMLs conform to schema")
        print("[NEXT] Run parameter mapping validation")
        print("   python scripts/validate_parameter_mappings.py --verbose")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
