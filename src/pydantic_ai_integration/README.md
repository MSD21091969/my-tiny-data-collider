# Pydantic AI Integration

Home to the tool runtime, registry, and code generation pipeline. This layer stitches together the YAML definitions in `config/tools/**`, the canonical models in `src/pydantic_models`, and the service layer described in the root `README.md`.

## Directory Overview

```

├── tool_decorator.py         # @register_mds_tool + MANAGED_TOOLS registry
├── tool_definition.py        # ManagedToolDefinition + metadata/business rules
├── dependencies.py           # MDSContext (execution state + persistence hooks)
├── execution/
│   ├── chain_executor.py         # Experimental composite-chain executor
│   └── firebase_stub.py          # In-memory Firestore substitute for tests
├── integrations/
│   └── google_workspace/
│       ├── clients.py            # Mock-friendly Gmail/Drive/Sheets clients
│       └── models.py             # Typed request/response contracts
└── tools/
    ├── agents/                   # Stub agent runtime for decorator wiring
    │   └── base.py               # `default_agent` used by generated modules
    ├── factory/                  # YAML → code/test generator (ToolFactory)
    │   └── templates/            # Jinja2 templates for code + pytest suites
    ├── generated/                # Auto-generated tool implementations/tests
    ├── legacy/                   # Hand-authored tools kept for compatibility
    ├── unified_example_tools.py  # Import compat shim for legacy imports
    └── examples/                 # (Optional) hand-written examples/demos
```

### Tool Registry (`tool_decorator.py`)
- `register_mds_tool` wraps a coroutine, validates parameters with a Pydantic model, and stores a `ManagedToolDefinition` in the global `MANAGED_TOOLS` map.
- Metadata (what the tool is) and business rules (when it can run) live together so services and APIs can enforce policy consistently.
- The decorator also registers the validated wrapper with the default agent runtime (`tools.agents.base.default_agent`).

```python
from src.pydantic_ai_integration.tool_decorator import register_mds_tool
from src.pydantic_ai_integration.dependencies import MDSContext

class EchoParams(BaseModel):
    text: str = Field(..., min_length=1)

@register_mds_tool(
    name="echo_tool",
    params_model=EchoParams,
    description="Echo the provided text",
    category="utilities",
    required_permissions=["debug:echo"],
)
async def echo_tool(ctx: MDSContext, text: str) -> dict:
    ctx.register_event("echo_tool", {"text": text})
    return {"echo": text}
```

`ManagedToolDefinition` (see `tool_definition.py`) exposes helpers like `validate_params`, `check_permission`, and `get_openapi_schema`, which the service layer and FastAPI routers call when executing `/tool-sessions/execute` or surfacing discovery metadata.

### Execution Context (`dependencies.py`)
`MDSContext` captures everything that happens during a tool session: chain planning, event logging, persistent state, knowledge graph entries, and conversation history. Highlights:
- Auto-persistence hooks: set `ctx.set_persistence_handler(handler, auto_persist=True)` to save state after each mutating call.
- Chain utilities (`plan_tool_chain`, `register_event`, `complete_chain`) allow composite tools to coordinate multi-step workflows.
- Serialization guards ensure anything stored on the context is JSON-safe before persisting or emitting audit events.

### Tool Generation (`tools/factory`)
`ToolFactory` reads each YAML file under `config/tools/**` and produces:
- Tool implementations in `tools/generated/{domain}/{subdomain}/`. Each module defines the params model, registers the tool, and implements the body according to the specified `implementation` type (`api_call`, `data_transform`, `composite`, etc.).
- Unit, integration, and API tests under `tests/{unit|integration|api}/...` using the same domain/subdomain hierarchy.
- Package scaffolding (`__init__.py`) so imports work recursively.

CLI entry points:
- `generate-tools` (installed via `pip install -e ".[dev]"` as described in `INSTALL.md`).
- `python scripts/generate_tools.py` or `python -m src.pydantic_ai_integration.tools.factory` if you want explicit control (see root documentation for workflow).

### Compatibility Shims
- `tools.agents.base.default_agent` provides the decorator hook expected by legacy generated modules; swap this stub out when the real agent runtime is available.
- `tools.legacy` and `tools.unified_example_tools` expose hand-maintained examples (`example_tool`) while still registering with the canonical decorator.
- `execution.firebase_stub` mirrors the Firestore client used by `tool_sessionservice` so tests run without external dependencies.
- Importing from the deprecated `pydantic_ai_integration.google_workspace` namespace raises an informative `ImportError`, guiding consumers to `integrations.google_workspace`.

### Google Workspace Integrations (`integrations/google_workspace`)
- Clients (`GmailClient`, `DriveClient`, `SheetsClient`) read environment toggles via `coreservice.config.get_config()` and default to mock mode so local development works without external credentials.
- Response helpers (`to_casefile_data`) return the typed workspace caches defined in `src/pydantic_models.workspace.*`, enabling the casefile service to persist synced data.

### Chain Executor (`execution/chain_executor.py`)
Prototype support for YAML-defined composite tools. It walks a list of steps, resolves inputs from `MDSContext` state, and calls registered tools sequentially with optional branching/retries. The implementation expects `MANAGED_TOOLS` entries to expose the callable implementation; when wiring new composites ensure you pass along the validated wrapper.

## Putting It Together
1. Write or edit a YAML definition (`config/tools/{domain}/{subdomain}/tool.yaml`) following the schema documented in `config/tools/README.md`.
2. Run `generate-tools` to refresh generated modules and tests.
3. Import the generated module (tests do this automatically), which registers the tool via `register_mds_tool`.
4. Execute the tool through the API (`POST /tool-sessions/execute`) or directly with `ToolSessionService.process_tool_request`. The service builds an `MDSContext`, validates parameters with `ManagedToolDefinition`, and captures audit events.

Refer back to `INSTALL.md` for environment setup, and `CONTRIBUTING.md` for coding standards and commit workflow. The YAML stays the single source of truth; generated artifacts are disposable and should never be edited by hand.
## MDSContext Quick Reference

- `register_event(name, parameters, result_summary=None, duration_ms=None)`: append audit-friendly breadcrumbs for each tool invocation.
- `set_persistence_handler(handler, auto_persist=False)`: configure how context state is flushed to storage after operations.
- `plan_tool_chain(chain_name, steps)`: capture intent before invoking a composite pipeline via `ChainExecutor`.
- `transaction_context`: mutable dictionary for correlating downstream service calls (e.g., request IDs, correlation IDs).
- `ensure_serializable(obj)`: helper used internally before persisting payloads to Firestore or emitting audit events.
