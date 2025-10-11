# tool_sessionservice Overview

**Tags:** `tool-session` `context` `execution` `audit`

## Directory Snapshot

```text
src/tool_sessionservice/
  repository.py        # Firestore persistence for tool sessions and events
  service.py           # ContextAwareService subclass handling lifecycle + execution
  models/
    session.py         # Canonical tool session entity
    tool_event.py      # Event records tied to sessions
  mappers/
    tool_session_mapper.py  # DTO ↔ domain transformations
  tools/
    ToolSessionService_*    # YAML tool specs for session operations
```

## Key Abstractions

| Concept | Definition | Related Modules |
| --- | --- | --- |
| `ToolSessionRepository` | Firestore gateway for sessions, events, request IDs | `repository.py` |
| `ToolSessionService` | Business logic orchestrating session lifecycle + tool execution | `service.py` |
| `ToolSessionModel` | Canonical session document with metadata | `models/session.py` |
| `ToolEventModel` | Captures individual tool executions within a session | `models/tool_event.py` |
| Tool templates | YAML method/tool definitions driving execution | `config/methodtools_v1/ToolSessionService_*` |

### Service Execution Details (service.py)

| Aspect | Description | Notes |
| --- | --- | --- |
| Base class | Extends `ContextAwareService` for hooks + context propagation | Aligns with RequestHub and audit flow |
| Dependencies | Injected `ToolSessionRepository`, `id_service`, optional metrics cache | Configured via `ServiceContainer` |
| Lifecycle ops | `create_session`, `get_session`, `list_sessions`, `close_session` | Mirrors YAML tool operations |
| Tool execution | `process_tool_request` validates session, records events, dispatches tools | Gateway between RAR and execution engine |
| Context usage | Enforces session/address metadata, updates activity timestamps | Works with `_session_lifecycle_hook` |
| Metrics hooks | Emits counters for session creation/closure, tool success/failure | Integrates with `ServiceMetrics` and profiling |

### Auth & Routing Considerations

- Token/session alignment must be verified before processing tool requests; invalid tokens should short-circuit with audit entry.
- Repository updates should include `session_request_id` so Firestore hierarchy remains in sync with user/address.
- Service should expose helpers for RequestHub hooks to update session activity and event logs.

### Open Questions / Next Actions

1. Implement the token/session validation gate referenced in casefile and coreservice overviews.
2. Review `process_tool_request` for audit completeness (tool events, request IDs, context snapshots).
3. Ensure repository methods return data compatible with classification templates (fields used in YAML tool payloads).

## Navigation

- [[CORE_SERVICE_OVERVIEW.md|coreservice overview]]
- [[CASEFILE_SERVICE_OVERVIEW|casefileservice overview]]
- [[BRANCH_DEVELOPMENT_PLAN.md|branch development plan]]
