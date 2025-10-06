"""
Generate markdown documentation from MANAGED_METHODS registry.

Creates comprehensive API reference organized by:
- Classification hierarchy (domain/subdomain/capability)
- Service
- Request/Response schemas
- Business rules
- Usage examples

Output: docs/methods/
"""

import sys
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Any

# Add src to path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from pydantic_ai_integration.method_decorator import load_methods_from_yaml
from pydantic_ai_integration.method_registry import (
    get_registered_methods,
    get_methods_by_domain,
    get_methods_by_service,
    get_classification_summary
)


def generate_index_page(methods_dict: Dict[str, Any], output_dir: Path):
    """Generate index page with overview and statistics from local methods dictionary."""
    
    # Calculate statistics from local methods_dict
    by_domain = defaultdict(int)
    by_capability = defaultdict(int)
    by_maturity = defaultdict(int)
    by_integration_tier = defaultdict(int)
    by_service = defaultdict(int)
    
    for method_name, method_def in methods_dict.items():
        by_domain[method_def.metadata.domain] += 1
        by_capability[method_def.metadata.capability] += 1
        by_maturity[method_def.metadata.maturity] += 1
        by_integration_tier[method_def.metadata.integration_tier] += 1
        by_service[method_def.metadata.service_name] += 1
    
    total_methods = len(methods_dict)
    
    content = f"""# Service Methods API Reference

**Version:** 1.0.0  
**Generated:** 2025-10-06  
**Total Methods:** {total_methods}

## Overview

This API reference documents all service-level methods in the system, organized by classification hierarchy.

All methods follow the **BaseRequest→BaseResponse** pattern with:
- ✅ Pydantic validation
- ✅ Type safety
- ✅ Execution tracking (execution_time_ms)
- ✅ Standardized error handling
- ✅ Permission-based access control

## Statistics

### By Domain
"""
    
    for domain, count in sorted(by_domain.items()):
        content += f"- **{domain.title()}**: {count} methods\n"
    
    content += "\n### By Capability\n"
    for capability, count in sorted(by_capability.items()):
        content += f"- **{capability.title()}**: {count} methods\n"
    
    content += "\n### By Maturity\n"
    for maturity, count in sorted(by_maturity.items()):
        content += f"- **{maturity.title()}**: {count} methods\n"
    
    content += "\n### By Integration Tier\n"
    for tier, count in sorted(by_integration_tier.items()):
        content += f"- **{tier.title()}**: {count} methods\n"
    
    content += """

## Navigation

### By Domain
"""
    
    domains = ['workspace', 'communication', 'automation']
    for domain in domains:
        if domain in by_domain:
            content += f"- [{domain.title()}](./{domain}/README.md)\n"
    
    content += """

### By Service
"""
    
    for service, count in sorted(by_service.items()):
        if count > 0:
            content += f"- [{service}](./services/{service}.md) ({count} methods)\n"
    
    content += """

## Quick Links

- [Methods Registry Documentation](../registry/README.md) - System documentation
- [Classification Schema](../registry/classification-schema.md) - Taxonomy definitions
- [Methods Inventory YAML](../../config/methods_inventory_v1.yaml) - Source configuration
- [Model Mapping](../registry/model-mapping.md) - Request/Response coverage
- [Versioning Guide](../registry/versioning-guide.md) - Semver rules
- [CHANGELOG](../registry/CHANGELOG.md) - Version history

## Usage Pattern

All methods follow this pattern:

```python
from src.casefileservice.service import CasefileService
from src.pydantic_models.operations.casefile_ops import (
    CreateCasefileRequest,
    CreateCasefilePayload
)

# Create request
payload = CreateCasefilePayload(
    title="My Casefile",
    description="Investigation notes"
)
request = CreateCasefileRequest(payload=payload)

# Call service method
service = CasefileService()
response = await service.create_casefile(request)

# Handle response
if response.status == RequestStatus.COMPLETED:
    casefile_id = response.payload.casefile_id
    print(f"Created casefile: {casefile_id}")
    print(f"Execution time: {response.metadata['execution_time_ms']}ms")
else:
    print(f"Error: {response.error}")
```

## Response Envelope

All methods return `BaseResponse[T]`:

```python
class BaseResponse(BaseModel, Generic[T]):
    request_id: UUID
    status: RequestStatus  # COMPLETED | FAILED | PENDING
    payload: T  # Business payload
    error: Optional[str]
    metadata: Dict[str, Any]  # execution_time_ms, etc.
```
"""
    
    index_file = output_dir / "README.md"
    index_file.write_text(content, encoding='utf-8')
    print(f"[OK] Generated: {index_file}")


def generate_domain_page(domain: str, methods: List[Any], output_dir: Path):
    """Generate domain overview page."""
    
    domain_dir = output_dir / domain
    domain_dir.mkdir(parents=True, exist_ok=True)
    
    # Group by subdomain
    by_subdomain = defaultdict(list)
    for method in methods:
        by_subdomain[method.metadata.subdomain].append(method)
    
    content = f"""# {domain.title()} Domain

**Methods:** {len(methods)}  
**Subdomains:** {len(by_subdomain)}

## Subdomains

"""
    
    for subdomain in sorted(by_subdomain.keys()):
        subdomain_methods = by_subdomain[subdomain]
        content += f"### {subdomain.replace('_', ' ').title()}\n\n"
        content += f"**Methods:** {len(subdomain_methods)}\n\n"
        
        for method in sorted(subdomain_methods, key=lambda m: m.metadata.name):
            content += f"- [`{method.metadata.name}`](./{method.metadata.name}.md) - {method.metadata.description}\n"
        
        content += "\n"
    
    readme_file = domain_dir / "README.md"
    readme_file.write_text(content, encoding='utf-8')
    print(f"[OK] Generated: {readme_file}")


def generate_method_page(method_def: Any, output_dir: Path):
    """Generate detailed method documentation page."""
    
    # Create domain directory
    domain = method_def.metadata.domain
    domain_dir = output_dir / domain
    domain_dir.mkdir(parents=True, exist_ok=True)
    
    # Build content
    content = f"""# {method_def.metadata.name}

{method_def.metadata.description}

## Classification

| Field | Value |
|-------|-------|
| **Domain** | {method_def.metadata.domain} |
| **Subdomain** | {method_def.metadata.subdomain} |
| **Capability** | {method_def.metadata.capability} |
| **Complexity** | {method_def.metadata.complexity} |
| **Maturity** | {method_def.metadata.maturity} |
| **Integration Tier** | {method_def.metadata.integration_tier} |

## Service

**Service:** `{method_def.metadata.service_name}`  
**Module:** `{method_def.metadata.module_path}`  
**Implementation:** `{method_def.implementation_class}.{method_def.implementation_method}`

## Signature

```python
async def {method_def.metadata.name}(
    self,
    request: {method_def.models.request_model_name}
) -> {method_def.models.response_model_name}
```

## Request Model

**Type:** `{method_def.models.request_model_name}`  
**Module:** `{method_def.models.request_model_path}`

### Parameters

"""
    
    if method_def.parameters:
        content += "| Name | Type | Required | Description |\n"
        content += "|------|------|----------|-------------|\n"
        for param in method_def.parameters:
            required = "✓" if param.required else "✗"
            content += f"| `{param.name}` | `{param.param_type}` | {required} | {param.description} |\n"
    else:
        content += "*No parameters documented.*\n"
    
    content += f"""

## Response Model

**Type:** `{method_def.models.response_model_name}`  
**Module:** `{method_def.models.response_model_path}`

## Business Rules

| Rule | Value |
|------|-------|
| **Enabled** | {"✓" if method_def.business_rules.enabled else "✗"} |
| **Requires Auth** | {"✓" if method_def.business_rules.requires_auth else "✗"} |
| **Requires Casefile** | {"✓" if method_def.business_rules.requires_casefile else "✗"} |
"""
    
    if method_def.business_rules.casefile_permission_level:
        content += f"| **Casefile Permission Level** | {method_def.business_rules.casefile_permission_level} |\n"
    
    content += f"| **Timeout** | {method_def.business_rules.timeout_seconds}s |\n"
    
    if method_def.business_rules.required_permissions:
        content += "\n### Required Permissions\n\n"
        for perm in method_def.business_rules.required_permissions:
            content += f"- `{perm}`\n"
    
    if method_def.business_rules.dependencies:
        content += "\n### Dependencies\n\n"
        for dep in method_def.business_rules.dependencies:
            content += f"- `{dep}`\n"
    
    content += f"""

## Usage Example

```python
from {method_def.metadata.module_path} import {method_def.metadata.service_name}
from {method_def.models.request_model_path} import (
    {method_def.models.request_model_name},
"""
    
    # Infer payload type from request model name
    if method_def.models.request_model_name.endswith('Request'):
        payload_name = method_def.models.request_model_name[:-7] + 'Payload'
        content += f"    {payload_name}\n"
    
    content += ")\n\n# Create request\n"
    
    # Infer payload name
    payload_name = "Payload"
    if method_def.models.request_model_name.endswith('Request'):
        payload_name = method_def.models.request_model_name[:-7] + 'Payload'
    
    if method_def.parameters:
        content += "payload = " + payload_name + "(\n"
        for param in method_def.parameters[:3]:  # Show first 3 params
            if param.param_type == 'str':
                content += f'    {param.name}="example_value",\n'
            elif param.param_type == 'int':
                content += f'    {param.name}=42,\n'
            elif param.param_type == 'bool':
                content += f'    {param.name}=True,\n'
            else:
                content += f'    {param.name}=...,  # {param.param_type}\n'
        if len(method_def.parameters) > 3:
            content += "    # ... more parameters\n"
        content += ")\n"
    else:
        content += "# No parameters required\npayload = " + payload_name + "()\n"
    
    content += f"""request = {method_def.models.request_model_name}(payload=payload)

# Call method
service = {method_def.metadata.service_name}()
response = await service.{method_def.metadata.name}(request)

# Handle response
if response.status == RequestStatus.COMPLETED:
    result = response.payload
    print(f"Success: {{result}}")
    print(f"Execution time: {{response.metadata['execution_time_ms']}}ms")
else:
    print(f"Error: {{response.error}}")
```

## Related

"""
    
    # Find related methods in same subdomain
    from pydantic_ai_integration.method_registry import get_methods_by_subdomain
    related = get_methods_by_subdomain(
        method_def.metadata.domain,
        method_def.metadata.subdomain
    )
    related = [m for m in related if m.metadata.name != method_def.metadata.name]
    
    if related:
        for rel_method in related[:5]:  # Show up to 5 related
            content += f"- [`{rel_method.metadata.name}`](./{rel_method.metadata.name}.md)\n"
    else:
        content += "*No related methods in this subdomain.*\n"
    
    content += f"""

---

**Version:** {method_def.metadata.version}  
**Last Updated:** {method_def.registered_at.strftime('%Y-%m-%d')}
"""
    
    method_file = domain_dir / f"{method_def.metadata.name}.md"
    method_file.write_text(content, encoding='utf-8')
    print(f"[OK] Generated: {method_file}")


def generate_service_pages(methods_dict: Dict[str, Any], output_dir: Path):
    """Generate service-specific pages from local methods dictionary."""
    
    services_dir = output_dir / "services"
    services_dir.mkdir(parents=True, exist_ok=True)
    
    # Group methods by service
    by_service = defaultdict(list)
    for method_name, method_def in methods_dict.items():
        service_name = method_def.metadata.service_name
        by_service[service_name].append(method_def)
    
    for service_name in sorted(by_service.keys()):
        methods = by_service[service_name]
        if not methods:
            continue
        
        content = f"""# {service_name}

**Module:** `{methods[0].metadata.module_path if methods else 'unknown'}`  
**Methods:** {len(methods)}

## Methods

"""
        
        # Group by capability
        by_capability = defaultdict(list)
        for method in methods:
            by_capability[method.metadata.capability].append(method)
        
        for capability in sorted(by_capability.keys()):
            cap_methods = by_capability[capability]
            content += f"### {capability.title()} Operations\n\n"
            
            for method in sorted(cap_methods, key=lambda m: m.metadata.name):
                content += f"#### [`{method.metadata.name}`](../{method.metadata.domain}/{method.metadata.name}.md)\n\n"
                content += f"{method.metadata.description}\n\n"
                content += f"**Request:** `{method.models.request_model_name}`  \n"
                content += f"**Response:** `{method.models.response_model_name}`  \n"
                
                if method.business_rules.requires_casefile:
                    content += f"**Requires Casefile:** ✓  \n"
                
                if method.business_rules.required_permissions:
                    content += f"**Permissions:** {', '.join(f'`{p}`' for p in method.business_rules.required_permissions)}  \n"
                
                content += "\n"
        
        service_file = services_dir / f"{service_name}.md"
        service_file.write_text(content, encoding='utf-8')
        print(f"[OK] Generated: {service_file}")


def main():
    """Main documentation generation."""
    print("\n" + "="*60)
    print("METHOD DOCUMENTATION GENERATOR")
    print("="*60 + "\n")
    
    # Load methods from YAML
    print("[1/5] Loading methods from YAML...")
    yaml_path = Path("config/methods_inventory_v1.yaml")
    if not yaml_path.exists():
        print(f"[ERROR] YAML file not found: {yaml_path}")
        sys.exit(1)
    
    methods_dict = load_methods_from_yaml(str(yaml_path))
    print(f"      Loaded {len(methods_dict)} methods")
    
    # Setup output directory
    print("\n[2/5] Setting up output directory...")
    output_dir = Path("docs/methods")
    output_dir.mkdir(parents=True, exist_ok=True)
    print(f"      Output: {output_dir}")
    
    # Generate index
    print("\n[3/5] Generating index page...")
    generate_index_page(methods_dict, output_dir)
    
    # Generate domain pages
    print("\n[4/5] Generating domain pages...")
    domains = ['workspace', 'communication', 'automation']
    for domain in domains:
        domain_methods = get_methods_by_domain(domain, enabled_only=False)
        if domain_methods:
            generate_domain_page(domain, domain_methods, output_dir)
    
    # Generate method pages
    print("\n[5/5] Generating method pages...")
    for method_name, method_def in methods_dict.items():
        generate_method_page(method_def, output_dir)
    
    # Generate service pages
    print("\n[BONUS] Generating service pages...")
    generate_service_pages(methods_dict, output_dir)
    
    print("\n" + "="*60)
    print("[SUCCESS] Documentation generated successfully!")
    print("="*60)
    print(f"\nView documentation: {output_dir / 'README.md'}")
    print()


if __name__ == "__main__":
    main()
