# Pydantic AI Integration

**Purpose:** Service method and tool registration infrastructure for R-A-R pattern.

---

## Core Files

### Definitions (Data Models)
- **`method_definition.py`** - `ManagedMethodDefinition` model (16 fields)
  - What: Service method metadata
  - Stores: name, description, version, classification (6 fields), execution refs (4 fields)
  - Deleted: MethodMetadata, MethodBusinessRules, MethodModels (moved to Request DTOs)

- **`tool_definition.py`** - `ManagedToolDefinition` model (12 fields)
  - What: Tool metadata
  - Stores: name, description, version, category, tags, method_name, parameters, implementation
  - Deleted: ToolMetadata, ToolBusinessRules, ToolSessionPolicies, ToolCasefilePolicies, ToolAuditConfig (moved to Request DTOs)

### Registries (Storage)
- **`method_registry.py`** - `MANAGED_METHODS` global dict
  - What: Runtime storage for methods
  - APIs: `get_method_definition()`, `get_method_parameters()`, `get_methods_by_domain()`, etc.
  - Relation: Loaded from `config/methods_inventory_v1.yaml` at startup

- **`tool_decorator.py`** - `MANAGED_TOOLS` global dict
  - What: Runtime storage for tools
  - APIs: `@register_mds_tool()`, `get_tool_definition()`, `get_tool_parameters()`, etc.
  - Relation: Tools reference methods via `method_name` field

### Decorators (Registration)
- **`method_decorator.py`** - `@register_service_method()` + YAML loader
  - What: Registers methods into `MANAGED_METHODS`
  - Use: Loads from YAML at startup via `register_methods_from_yaml()`
  - Future: Phase 10 - code-first registration

- **`tool_decorator.py`** - `@register_mds_tool()`
  - What: Registers tools into `MANAGED_TOOLS`
  - Use: Decorates tool functions, inherits params from methods
  - Relation: References `MANAGED_METHODS` for parameter inheritance

### Model Registry
- **`model_registry.py`** - Model discovery and validation
  - What: Loads `config/models_inventory_v1.yaml` for model lookup
  - APIs: `get_model()`, `list_by_layer()`, `list_by_domain()`, `get_payload_models()`
  - Use: Validation scripts, documentation generation

---

## Architecture

```
YAML Config
  ↓ loaded by
Method Decorator → MANAGED_METHODS registry
  ↓ referenced by
Tool Decorator → MANAGED_TOOLS registry
  ↓ accessed by
Service Layer (execution)
```

**Parameter Flow:**
```
DTO Payload fields
  → extract on-demand
Method Parameters (get_method_parameters)
  → inherit
Tool Parameters (get_tool_parameters)
```

**Policies (R-A-R Pattern):**
- ❌ NOT in definitions (deleted business_rules, session_policies, etc.)
- ✅ IN Request DTOs (validation layer enforces auth, permissions, session)

---

## Recent Changes (2025-10-08)

### Method Definition Refactor
- `method_definition.py`: 292 → 120 lines (40+ → 16 fields)
- `method_registry.py`: Added `get_method_parameters()` for extraction
- Deleted: MethodMetadata, MethodBusinessRules, MethodModels

### Tool Definition Refactor  
- `tool_definition.py`: 470 → 130 lines (44+ → 12 fields)
- `tool_decorator.py`: Updated to 7-param decorator, added `get_tool_parameters()`
- Deleted: ToolMetadata, ToolBusinessRules, ToolSessionPolicies, ToolCasefilePolicies, ToolAuditConfig

### Model Registry Added
- `model_registry.py`: Discovery APIs for all Pydantic models
- `config/models_inventory_v1.yaml`: 52 models across 5 layers

**Status:** All refactors complete, no errors ✅

