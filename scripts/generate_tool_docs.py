#!/usr/bin/env python3
"""
Auto-generate tool catalog documentation from YAML specifications.
"""
import yaml
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any


def load_tool_specs() -> List[Dict[str, Any]]:
    """Load all tool YAML specifications."""
    tools = []
    tools_dir = Path('config/tools')
    
    for yaml_file in sorted(tools_dir.glob('*.yaml')):
        with open(yaml_file) as f:
            tool_spec = yaml.safe_load(f)
            tool_spec['_filename'] = yaml_file.name
            tools.append(tool_spec)
    
    return tools


def categorize_tools(tools: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    """Group tools by category."""
    categorized = {}
    
    for tool in tools:
        category = tool.get('category', 'uncategorized')
        if category not in categorized:
            categorized[category] = []
        categorized[category].append(tool)
    
    return categorized


def generate_parameter_table(params: List[Dict[str, Any]]) -> str:
    """Generate markdown table for parameters."""
    if not params:
        return "No parameters"
    
    table = "| Parameter | Type | Required | Description |\n"
    table += "|-----------|------|----------|-------------|\n"
    
    for param in params:
        name = param.get('name', 'unknown')
        param_type = param.get('type', 'any')
        required = '✅' if param.get('required', False) else '❌'
        description = param.get('description', 'No description')
        
        # Add constraints
        constraints = []
        if 'min_length' in param:
            constraints.append(f"min: {param['min_length']}")
        if 'max_length' in param:
            constraints.append(f"max: {param['max_length']}")
        if 'min_value' in param:
            constraints.append(f"≥{param['min_value']}")
        if 'max_value' in param:
            constraints.append(f"≤{param['max_value']}")
        if 'default' in param:
            constraints.append(f"default: {param['default']}")
        
        if constraints:
            param_type += f" ({', '.join(constraints)})"
        
        table += f"| `{name}` | {param_type} | {required} | {description} |\n"
    
    return table


def generate_catalog_md(tools: List[Dict[str, Any]]) -> str:
    """Generate complete tool catalog markdown."""
    categorized = categorize_tools(tools)
    
    md = f"""# Tool Catalog

**Auto-generated from YAML specifications**  
**Last Updated:** {datetime.now().strftime('%B %d, %Y at %H:%M UTC')}

---

## 📊 Overview

**Total Tools:** {len(tools)}  
**Categories:** {len(categorized)}

| Category | Tool Count |
|----------|-----------|
"""
    
    for category, category_tools in sorted(categorized.items()):
        md += f"| {category.title()} | {len(category_tools)} |\n"
    
    md += "\n---\n\n"
    
    # Generate detailed documentation per category
    for category, category_tools in sorted(categorized.items()):
        md += f"## 📦 {category.title()}\n\n"
        
        for tool in sorted(category_tools, key=lambda t: t.get('name', '')):
            name = tool.get('name', 'unknown')
            display_name = tool.get('display_name', name)
            description = tool.get('description', 'No description')
            version = tool.get('version', '1.0.0')
            
            md += f"### `{name}`\n\n"
            md += f"**Display Name:** {display_name}  \n"
            md += f"**Version:** {version}  \n"
            md += f"**Description:** {description}\n\n"
            
            # Parameters
            md += "**Parameters:**\n\n"
            params = tool.get('parameters', [])
            md += generate_parameter_table(params) + "\n\n"
            
            # Policies
            business_rules = tool.get('business_rules', {})
            session_policies = tool.get('session_policies', {})
            
            md += "**Policies:**\n\n"
            md += f"- **Authentication:** {'Required' if business_rules.get('requires_auth') else 'Optional'}\n"
            
            perms = business_rules.get('required_permissions', [])
            if perms:
                md += f"- **Permissions:** {', '.join(f'`{p}`' for p in perms)}\n"
            
            md += f"- **Session Required:** {'Yes' if session_policies.get('requires_active_session') else 'No'}\n"
            md += f"- **Timeout:** {business_rules.get('timeout_seconds', 30)}s\n\n"
            
            # Implementation
            impl = tool.get('implementation', {})
            impl_type = impl.get('type', 'unknown')
            md += f"**Implementation Type:** `{impl_type}`\n\n"
            
            # Examples
            examples = tool.get('examples', [])
            if examples:
                md += "**Examples:**\n\n"
                for i, example in enumerate(examples, 1):
                    ex_desc = example.get('description', 'Example')
                    md += f"{i}. **{ex_desc}**\n"
                    md += "   ```python\n"
                    md += f"   # Input: {example.get('input', {})}\n"
                    md += f"   # Output: {example.get('expected_output', {})}\n"
                    md += "   ```\n\n"
            
            # YAML Source
            md += f"**YAML Spec:** `{tool.get('_filename', 'unknown')}`\n\n"
            md += "---\n\n"
    
    # Footer
    md += """
## 🔧 Usage

### Basic Tool Call (Unit Test)

```python
from src.pydantic_ai_integration.dependencies import MDSContext
from src.pydantic_ai_integration.tools.generated.<tool_name> import <tool_name>

ctx = MDSContext(user_id="user_123", session_id="session_123")
result = await <tool_name>(ctx, param1="value1", param2="value2")
```

### Via Service Layer (Integration)

```python
from src.tool_sessionservice.service import ToolSessionService
from src.pydantic_models.tool_session.models import ToolRequest, ToolRequestPayload

service = ToolSessionService()
request = ToolRequest(
    user_id="user_123",
    session_id="session_123",
    operation="tool_execution",
    payload=ToolRequestPayload(
        tool_name="<tool_name>",
        parameters={"param1": "value1", "param2": "value2"}
    )
)
response = await service.execute_tool(request)
```

---

**Generated by:** `scripts/generate_tool_docs.py`  
**See Also:** [README.md](../README.md), [QUICK_REFERENCE.md](../QUICK_REFERENCE.md)
"""
    
    return md


def main():
    """Main execution."""
    print("🔍 Loading tool specifications...")
    tools = load_tool_specs()
    print(f"✅ Found {len(tools)} tools")
    
    print("📝 Generating catalog documentation...")
    catalog_md = generate_catalog_md(tools)
    
    output_file = Path('docs/TOOL_CATALOG.md')
    output_file.write_text(catalog_md, encoding='utf-8')
    print(f"✅ Catalog written to {output_file}")
    
    print("\n📊 Summary:")
    categorized = categorize_tools(tools)
    for category, category_tools in sorted(categorized.items()):
        print(f"  - {category.title()}: {len(category_tools)} tools")


if __name__ == '__main__':
    main()
