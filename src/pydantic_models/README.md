# Pydantic Models

Purpose-based organisation for every data shape used across the application stack. The layout mirrors the high-level architecture described in the root `README.md` and the contribution guidelines in `CONTRIBUTING.md`.

> Starting from scratch? Run the clean-slate bootstrap flow first (clone → create venv → `pip install -e ".[dev]"` → `python scripts/generate_tools.py` → `python scripts/import_generated_tools.py`) so the generated tooling that relies on these models is available.

## Directory Layout

```

├── base/          # Cross-cutting envelopes, enums, shared primitives
├── canonical/     # Authoritative domain entities + behaviour
├── operations/    # Request/response DTOs (API & service edges)
├── views/         # Lightweight read models for list endpoints
└── workspace/     # External data caches (Gmail, Drive, Sheets)
```

### Base layer (`base/`)
- `envelopes.py`: generic `BaseRequest[T]`, `BaseResponse[T]`, and `RequestEnvelope` used by every service and router. These wrap payloads with metadata (`user_id`, `session_id`, timestamps) and power the envelope pattern highlighted in `INSTALL.md`.
- `types.py`: shared enums such as `RequestStatus` so responses carry a consistent lifecycle (`pending → processing → completed/failed`).

### Canonical layer (`canonical/`)
- **Casefiles** (`casefile.py`): source of truth entity with metadata, session links, ACL, and typed workspace caches (`CasefileGmailData`, `CasefileDriveData`, `CasefileSheetsData`). Uses the central ID service for IDs.
- **ACL** (`acl.py`): permission hierarchy plus helpers (`can_read`, `can_share`, etc.) consumed by `casefileservice` and FastAPI routers.
- **Tool sessions** (`tool_session.py`): tracks requests/events, generates audit-friendly `ToolEvent` records, and delegates ID generation to `coreservice.id_service`.
- **Chat sessions** (`chat_session.py`): chat history, message indexing, and metadata required by `communicationservice`.

### Operations layer (`operations/`)
Request/response DTOs that cross service and API boundaries. Each module mirrors a service:
- `casefile_ops.py`: CRUD envelopes, ACL commands, session linking payloads.
- `tool_session_ops.py`: create/get/list/close session contracts.
- `tool_execution_ops.py`: tool execution + chat message envelopes (`ToolRequest`, `ToolResponse`, `ChatRequest`, `ChatResponse`) with runtime validation against the tool registry (`MANAGED_TOOLS`).
- `chat_session_ops.py`: chat lifecycle management requests.

All operation models inherit from `BaseRequest` / `BaseResponse` to guarantee consistent metadata and typed payloads.

### Views layer (`views/`)
Projection models tailored for listing endpoints (`CasefileSummary`, `SessionSummary`). These intentionally omit heavy nested structures for performance; routers return them inside `BaseResponse` wrappers.

### Workspace layer (`workspace/`)
Typed caches that persist external data pulled by tools or integrations. Examples:
- `gmail.py`: messages, threads, labels; includes helper methods for upserts.
- `drive.py`: Drive file metadata and owners.
- `sheets.py`: spreadsheets with range snapshots.

These models are hydrated by Google Workspace clients (`src/pydantic_ai_integration/integrations/google_workspace/clients.py`) and stored on `CasefileModel`.

## Usage Patterns

```python
from src.pydantic_models.base.envelopes import BaseRequest, BaseResponse
from src.pydantic_models.operations.tool_execution_ops import ToolRequest
from src.pydantic_models.canonical.tool_session import ToolSession

# Construct a tool execution request
request = ToolRequest(
    user_id="user_123",
    session_id="ts_20241004_abcd",
    payload={
        "tool_name": "gmail_send_message",
        "parameters": {"to": "recipient@example.com", "subject": "Hello", "body": "Hi"},
    },
)

# Services return BaseResponse envelopes with canonical payloads
response: BaseResponse = await tool_session_service.process_tool_request(request)
```

## Extending the Model Layer

1. **Decide the purpose**: canonical entity, DTO, view, or workspace cache. Keep business logic inside canonical models; keep DTOs minimal.
2. **Follow the envelope pattern**: new operations should extend `BaseRequest` / `BaseResponse` so routers and services stay uniform.
3. **Update documentation/tests**: describe new models in the relevant README and add fixtures/tests under `tests/` as outlined in `CONTRIBUTING.md`.

By keeping the purpose-driven layout, services (`casefileservice`, `tool_sessionservice`, `communicationservice`) and the FastAPI routers can reference shared, validated contracts without circular imports or duplicated schemas.

## Compatibility Shims

- `src/pydantic_models/tool_session.py` re-exports `ToolRequest`, `ToolRequestPayload`, and `ToolResponse` for older code paths that have not migrated to `operations.tool_execution_ops`.
- `src/pydantic_models/shared/base_models.py` bridges the legacy `RequestStatus` import to the new `base.types` enum.
- These modules are light wrappers—prefer importing directly from the `operations` or `base` packages when writing new code.
