# Tool Engineering Foundation v1.0.0

**Date**: 2025-10-06 | **Reference**: YAML classification, MANAGED_TOOLS, ToolFactory

---

## YAML Classification (`tool_schema_v2.yaml`)

```yaml
domain:           [workspace, communication, automation, utilities]
subdomain:        Specific area (casefile, gmail, tool_session, etc.)
capability:       [create, read, update, delete, process, search]
complexity:       [atomic, composite, pipeline]
maturity:         [experimental, beta, stable, deprecated]
integration_tier: [internal, external, hybrid]
```

**Example**:
```yaml
name: casefile_create_v2
classification:
  domain: workspace
  subdomain: casefile
  capability: create
  complexity: atomic
  maturity: stable
  integration_tier: internal
```

---

## MANAGED_TOOLS Registry (`tool_decorator.py`)

```python
MANAGED_TOOLS: Dict[str, ManagedToolDefinition] = {}

class ManagedToolDefinition:
    metadata: ToolMetadata                   # name, description, category
    business_rules: ToolBusinessRules        # auth, permissions, timeout
    parameters: List[ToolParameterDef]       # validation
    params_model: Type[BaseModel]            # Pydantic model
    classification: Dict[str, str]           # 6 YAML fields
    implementation: Callable                 # wrapped function
```

**@register_mds_tool Decorator**:
```python
@register_mds_tool(name="tool", params_model=ParamsModel)
async def tool(ctx: MDSContext, param: int) -> Dict:
    return {"result": param * 2}
```

**Discovery API (11 methods)**:
```python
# Basic
get_registered_tools() -> Dict[str, ManagedToolDefinition]
get_tool_names() -> List[str]
validate_tool_exists(name) -> bool
get_tool_definition(name) -> Optional[ManagedToolDefinition]

# Classification
get_tools_by_domain(domain) -> List[ManagedToolDefinition]
get_tools_by_capability(capability) -> List[ManagedToolDefinition]
get_tools_by_complexity(complexity) -> List[ManagedToolDefinition]
get_tools_by_maturity(maturity) -> List[ManagedToolDefinition]
get_tools_by_integration_tier(tier) -> List[ManagedToolDefinition]
get_hierarchical_tool_path(name) -> str  # "workspace.casefile.create"
get_classification_summary() -> Dict  # stats
```

---

## ToolFactory Pipeline (`factory/__init__.py`)

**Flow**: `YAML → load_tool_config → enrich → validate → Jinja2 → generated tools`

**Pipeline Steps**:
```python
# 1. Load & Enrich
config = load_tool_config(yaml_path)  # Adds defaults, processes examples

# 2. Validate
issues = validate_config(config)  # Name format, constraints, duplicates

# 3. Generate
generate_tool(config)  # Renders tool_template.py.jinja2
generate_tests(config)  # Unit/integration/API tests

# Output: tools/generated/{domain}/{subdomain}/{name}.py
```

**Implementation Types**:
```yaml
# api_call: Calls service method
implementation:
  type: api_call
  api_call:
    client_module: "src.casefileservice.service"
    client_class: "CasefileService"
    method_name: "create_casefile"

# simple: Inline logic
implementation:
  type: simple
  simple:
    logic: "return {'result': param1 + param2}"

# data_transform: Process casefile data
implementation:
  type: data_transform
  data_transform:
    source: "casefile.gmail_data"
    transform_logic: "return [m for m in source if m.unread]"
```

**Template** (`tool_template.py.jinja2`):
```python
class {{ tool.name | title }}Params(BaseModel):
    {% for p in tool.parameters %}{{ p.name }}: {{ p.type }}{% endfor %}

@register_mds_tool(name="{{ tool.name }}", params_model={{ tool.name | title }}Params)
async def {{ tool.name }}(ctx, {{ params }}):
    # Generated based on implementation.type
```

---

## Integration Flow

**1. YAML → Registry**: Generated tools auto-register via `@register_mds_tool` on import

**2. Registry → Execution** (`ToolSessionService.process_tool_request`):
```python
validate_tool_exists(tool_name)
tool_def = get_tool_definition(tool_name)
result = await tool_def.implementation(ctx, **params)
```

**3. Registry → Discovery** (API endpoints):
```python
@app.get("/tools")
def list_tools(domain: str = None):
    return get_tools_by_domain(domain) if domain else get_registered_tools()
```

**4. Factory → Methods** (Phase 11 - future):
- Validate `api_call.method_name` exists in MANAGED_METHODS
- Auto-generate `request_mapping` from method signature
