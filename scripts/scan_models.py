"""
Scan all Pydantic models and regenerate models_inventory_v1.yaml
"""
import ast
from pathlib import Path
from collections import defaultdict
from datetime import datetime

# Project root
ROOT = Path(__file__).parent.parent

# Model directories to scan
MODEL_PATHS = [
    ROOT / "src" / "pydantic_models" / "base",
    ROOT / "src" / "pydantic_models" / "operations",
    ROOT / "src" / "pydantic_models" / "canonical",
    ROOT / "src" / "pydantic_models" / "workspace",
    ROOT / "src" / "pydantic_models" / "views",
]

class ModelScanner(ast.NodeVisitor):
    """AST visitor to extract Pydantic model definitions."""
    
    def __init__(self, filepath):
        self.filepath = filepath
        self.models = []
        
    def visit_ClassDef(self, node):
        """Visit class definitions."""
        # Check if class inherits from BaseModel, BaseRequest, BaseResponse, or Enum
        bases = [self._get_base_name(base) for base in node.bases]
        
        if any(b in bases for b in ['BaseModel', 'BaseRequest', 'BaseResponse', 'Enum', 'str']):
            # Get docstring
            docstring = ast.get_docstring(node) or ""
            
            # Get fields
            fields = []
            for item in node.body:
                if isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
                    fields.append(item.target.id)
            
            self.models.append({
                'name': node.name,
                'bases': bases,
                'fields': fields,
                'docstring': docstring.split('\n')[0] if docstring else ""
            })
        
        self.generic_visit(node)
    
    def _get_base_name(self, base):
        """Extract base class name from AST node."""
        if isinstance(base, ast.Name):
            return base.id
        elif isinstance(base, ast.Subscript):
            if isinstance(base.value, ast.Name):
                return base.value.id
        elif isinstance(base, ast.Attribute):
            return base.attr
        return ""

def scan_models():
    """Scan all Python files for Pydantic models."""
    all_models = defaultdict(list)
    
    for model_dir in MODEL_PATHS:
        if not model_dir.exists():
            continue
            
        layer = model_dir.name
        
        for py_file in model_dir.glob("*.py"):
            if py_file.name.startswith("_"):
                continue
                
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    tree = ast.parse(f.read(), filename=str(py_file))
                
                scanner = ModelScanner(py_file)
                scanner.visit(tree)
                
                if scanner.models:
                    rel_path = py_file.relative_to(ROOT / "src" / "pydantic_models")
                    all_models[layer].extend([
                        {**model, 'file': str(rel_path), 'filepath': py_file}
                        for model in scanner.models
                    ])
            except Exception as e:
                print(f"Warning: Could not parse {py_file}: {e}")
    
    return all_models

def categorize_models(all_models):
    """Categorize models by type and layer."""
    categorized = {
        'layer_0_base': [],
        'layer_1_payloads': defaultdict(list),
        'layer_2_dtos': defaultdict(list),
        'layer_3_canonical': [],
        'layer_4_external': [],
        'layer_5_views': [],
    }
    
    # Layer 0 - Base infrastructure
    if 'base' in all_models:
        categorized['layer_0_base'] = all_models['base']
    
    # Layer 2 (DTOs) and Layer 1 (Payloads) from operations/
    if 'operations' in all_models:
        for model in all_models['operations']:
            name = model['name']
            bases = model['bases']
            
            if 'BaseRequest' in bases:
                # This is a Request DTO (Layer 2)
                # Infer domain from filename
                file = Path(model['file'])
                domain = file.stem.replace('_ops', '')
                categorized['layer_2_dtos'][domain].append(model)
            elif 'BaseResponse' in bases:
                # This is a Response DTO (Layer 2)
                file = Path(model['file'])
                domain = file.stem.replace('_ops', '')
                categorized['layer_2_dtos'][domain].append(model)
            elif 'BaseModel' in bases and ('Payload' in name or 'Result' in name):
                # This is a Payload model (Layer 1)
                file = Path(model['file'])
                domain = file.stem.replace('_ops', '')
                categorized['layer_1_payloads'][domain].append(model)
    
    # Layer 3 - Canonical entities
    if 'canonical' in all_models:
        categorized['layer_3_canonical'] = all_models['canonical']
    
    # Layer 4 - External API models
    if 'workspace' in all_models:
        categorized['layer_4_external'] = all_models['workspace']
    
    # Layer 5 - View models
    if 'views' in all_models:
        categorized['layer_5_views'] = all_models['views']
    
    return categorized

def generate_yaml(categorized):
    """Generate YAML content from categorized models."""
    timestamp = datetime.now().strftime("%Y-%m-%d")
    
    # Calculate statistics
    stats = {
        'layer_0': len(categorized['layer_0_base']),
        'layer_1': sum(len(models) for models in categorized['layer_1_payloads'].values()),
        'layer_2': sum(len(models) for models in categorized['layer_2_dtos'].values()),
        'layer_3': len(categorized['layer_3_canonical']),
        'layer_4': len(categorized['layer_4_external']),
        'layer_5': len(categorized['layer_5_views']),
    }
    stats['total'] = sum(stats.values())
    
    lines = [
        "# ============================================================",
        "# MODELS INVENTORY v1.0.1 - AUTO-REGENERATED",
        "# ============================================================",
        f"# Last synchronized: {timestamp}",
        "# Synchronization reference: October 8, 2025 Foundation Sync",
        "# Generated from actual codebase using scripts/scan_models.py",
        "#",
        "# This inventory reflects the actual state of Pydantic models",
        "# in the codebase at the time of generation.",
        "#",
        "# VERSIONING:",
        "# - v1.0.0: Initial baseline (manual)",
        f"# - v1.0.1: First auto-regenerated version ({timestamp})",
        "# ============================================================",
        "",
        'version: "1.0.1"',
        f'generated_at: "{timestamp}"',
        'description: "Complete registry of all Pydantic models organized by layer and domain"',
        "",
        "layers:",
        "  # Layer 0: Base Infrastructure",
        "  layer_0_base:",
        '    description: "Foundation models - envelopes, types, base classes"',
        "    models:",
    ]
    
    # Layer 0
    for model in categorized['layer_0_base']:
        lines.append(f"      - name: {model['name']}")
        lines.append(f"        file: {model['file']}")
        if model['docstring']:
            lines.append(f"        description: \"{model['docstring']}\"")
    
    lines.extend([
        "",
        "  # Layer 1: Payload Models (Business Data)",
        "  layer_1_payloads:",
        '    description: "Business data models - operation parameters and results"',
        "",
    ])
    
    # Layer 1 - by domain
    for domain, models in sorted(categorized['layer_1_payloads'].items()):
        lines.append(f"    {domain}_domain:")
        lines.append("      models:")
        for model in models:
            lines.append(f"        - name: {model['name']}")
            lines.append(f"          file: {model['file']}")
            if model['fields']:
                fields_str = ', '.join(model['fields'])
                lines.append(f"          fields: [{fields_str}]")
        lines.append("")
    
    lines.extend([
        "  # Layer 2: Request/Response DTOs (Execution Envelopes)",
        "  layer_2_dtos:",
        '    description: "Request/Response DTOs wrapping payloads"',
        "",
    ])
    
    # Layer 2 - by domain
    for domain, models in sorted(categorized['layer_2_dtos'].items()):
        lines.append(f"    {domain}_operations:")
        for model in models:
            lines.append(f"      - {model['name']}")
        lines.append("")
    
    lines.extend([
        "  # Layer 3: Canonical Models (Entities)",
        "  layer_3_canonical:",
        '    description: "Domain entities - single source of truth"',
        "    models:",
    ])
    
    # Layer 3
    for model in categorized['layer_3_canonical']:
        lines.append(f"      - name: {model['name']}")
        lines.append(f"        file: {model['file']}")
        if model['docstring']:
            lines.append(f"        description: \"{model['docstring']}\"")
    
    lines.extend([
        "",
        "  # Layer 4: External API Models",
        "  layer_4_external:",
        '    description: "Google Workspace API data structures"',
        "    models:",
    ])
    
    # Layer 4
    for model in categorized['layer_4_external']:
        lines.append(f"      - name: {model['name']}")
        lines.append(f"        file: {model['file']}")
        if model['docstring']:
            lines.append(f"        description: \"{model['docstring']}\"")
    
    lines.extend([
        "",
        "  # Layer 5: View Models (API Responses)",
        "  layer_5_views:",
        '    description: "Denormalized views for API responses"',
        "    models:",
    ])
    
    # Layer 5
    for model in categorized['layer_5_views']:
        lines.append(f"      - name: {model['name']}")
        lines.append(f"        file: {model['file']}")
        if model['docstring']:
            lines.append(f"        description: \"{model['docstring']}\"")
    
    lines.extend([
        "",
        "statistics:",
        f"  total_models: {stats['total']}",
        "  by_layer:",
        f"    layer_0: {stats['layer_0']}",
        f"    layer_1: {stats['layer_1']}",
        f"    layer_2: {stats['layer_2']}",
        f"    layer_3: {stats['layer_3']}",
        f"    layer_4: {stats['layer_4']}",
        f"    layer_5: {stats['layer_5']}",
        "",
        "notes:",
        "  - All operations follow R-A-R pattern (Request-Action-Response)",
        "  - Parameters extracted on-demand from Layer 1 payloads",
        "  - Tools inherit parameters from methods which extract from Layer 2 DTOs",
        "  - Canonical models (Layer 3) are single source of truth for entities",
        "  - External API models (Layer 4) map to Google Workspace APIs",
        "  - Views (Layer 5) denormalize data for efficient API responses",
        "",
    ])
    
    return '\n'.join(lines)

if __name__ == '__main__':
    print("Scanning Pydantic models...")
    all_models = scan_models()
    
    print("\nModels found by directory:")
    for layer, models in all_models.items():
        print(f"  {layer}: {len(models)} models")
    
    print("\nCategorizing models...")
    categorized = categorize_models(all_models)
    
    print("\nStatistics:")
    print(f"  Layer 0 (Base): {len(categorized['layer_0_base'])}")
    print(f"  Layer 1 (Payloads): {sum(len(m) for m in categorized['layer_1_payloads'].values())}")
    print(f"  Layer 2 (DTOs): {sum(len(m) for m in categorized['layer_2_dtos'].values())}")
    print(f"  Layer 3 (Canonical): {len(categorized['layer_3_canonical'])}")
    print(f"  Layer 4 (External): {len(categorized['layer_4_external'])}")
    print(f"  Layer 5 (Views): {len(categorized['layer_5_views'])}")
    
    print("\nGenerating YAML...")
    yaml_content = generate_yaml(categorized)
    
    output_path = ROOT / "config" / "models_inventory_v1.yaml"
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(yaml_content)
    
    print(f"\n✅ Generated: {output_path}")
    print(f"   Total models: {sum(len(m) if isinstance(m, list) else sum(len(v) for v in m.values()) for m in categorized.values())}")
