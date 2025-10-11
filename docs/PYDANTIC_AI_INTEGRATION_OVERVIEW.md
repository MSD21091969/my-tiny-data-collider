# pydantic_ai_integration Overview

**Tags:** `tool-engineering` `method-registry` `context` `yaml-inventory`

## Directory Snapshot

```text
src/pydantic_ai_integration/
  __init__.py           # Bootstraps registries from YAML + decorators
  dependencies.py       # MDSContext definition, persistence helpers
  method_decorator.py   # @register_service_method implementation
  method_definition.py  # ManagedMethodDefinition + parameter metadata
  method_registry.py    # MANAGED_METHODS store, lookup utilities
  model_registry.py     # Model registration/lookup helpers for DTO mapping
  session_manager.py    # Tool session lifecycle helpers (ctx + persistence)
  tool_decorator.py     # @register_mds_tool decorator, execution wrapper
  tool_definition.py    # ManagedToolDefinition schema
  tool_utils.py         # Shared helpers for tool execution
  execution/            # Tool execution engine integrations
  integrations/         # External system adapters (LLMs, data sources)
  tools/                # YAML-backed tool implementations auto-registered
```

## Key Abstractions

| Concept | Definition | Related Modules |
| --- | --- | --- |
| `MDSContext` | Canonical runtime context shared across tool executions | `dependencies.py` |
| `ManagedMethodDefinition` | Slim metadata record describing service methods | `method_definition.py` |
| `ManagedToolDefinition` | Tool metadata + execution hints | `tool_definition.py` |
| `MANAGED_METHODS` / `MANAGED_TOOLS` | Global registries populated via decorators & YAML | `method_registry.py`, `tool_decorator.py` |
| YAML inventories | Source-of-truth for method & tool templates (`methods_inventory_v1.yaml`, `methodtools_v1/*`) | `config/` |
| Session helpers | Manage context persistence and audit trails | `dependencies.py`, `session_manager.py` |

### Registration & Bootstrapping Pattern

1. `__init__.py` imports `tools`, then calls `register_methods_from_yaml()` and `register_tools_from_yaml()`.
2. YAML inventories hydrate registries before any decorator-based registrations run.
3. Decorators (`@register_service_method`, `@register_mds_tool`) add code-defined overrides or new definitions.
4. Registries expose discovery APIs for RequestHub, tool factories, and documentation.

> Critical: failures during YAML load are logged but do not stop imports. Monitor logs to catch missing definitions.

### Context & Session Infrastructure

| Element | Description | Notes |
| --- | --- | --- |
| `MDSContext` | Rich context object (user/session/casefile IDs, tool chains, conversation history) with persistence hooks | Ensures tool executions share a consistent state; serializable for Firestore/storage |
| Persistence handlers | Optional callbacks invoked via `set_persistence_handler`; decorator `with_persistence` auto-persists | Integrate with tool session repository or custom stores |
| Tool events & chains | `register_event`, `plan_tool_chain`, `complete_chain` capture audit trails and reasoning paths | Aligns with RequestHub hook outputs |
| Session utilities | `create_session_request`, `add_conversation_message`, `link_related_document` standardize metadata updates | Used by tool execution engine and chat integrations |

### Method & Tool Engineering Interfaces

| Interface | Purpose | Notes |
| --- | --- | --- |
| `register_service_method` | Records method metadata (classification, permissions, DTOs) without wrapping execution | Service methods stay clean; metadata fuels docs/UI |
| `register_mds_tool` | Wraps callable with validation, context injection, and execution policies | Tools become first-class citizens in the inventory |
| Definition models | Capture DTO classes, payload parameter metadata, versioning info | Guarantees alignment with YAML and Pydantic models |
| Utilities | Helpers for argument normalization, error handling, instrumentation | Shared across generated/manual tools |

### Open Questions / Next Actions

1. **Startup robustness:** consider surfacing YAML load failures to health checks so CI/CD blocks when inventories diverge.
2. **Context/token alignment:** ensure `MDSContext.session_request_id` stays in sync with auth token enhancements planned in coreservice docs.
3. **Inventory drift detection:** add tests/scripts that diff YAML inventories against registries to prevent stale tool definitions.

## Navigation

- [[CORE_SERVICE_OVERVIEW.md|coreservice overview]]
- [[CASEFILE_SERVICE_OVERVIEW.md|casefileservice overview]]
- [[TOOL_SESSION_SERVICE_OVERVIEW.md|tool_sessionservice overview]]
- [[BRANCH_DEVELOPMENT_PLAN.md|branch development plan]]
