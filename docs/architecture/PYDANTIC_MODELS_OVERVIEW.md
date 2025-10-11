# pydantic_models Overview

**Tags:** `dto` `request-response` `domain-models` `mapping`

## Directory Snapshot

```text
src/pydantic_models/
  base/             # Infrastructure envelopes, enums, transformation helpers
  canonical/        # Source-of-truth domain entities
  operations/       # Request/response DTOs (aligned with services + tools)
  views/            # Projection / summary models for APIs
  mappers/          # Auto-generated DTO ↔ domain mappers
  workspace/        # External workspace payload models (Gmail, Drive, Sheets)
  tool_session.py   # Shared tool session canonical + events
```

## Layered Model Strategy

| Layer | Purpose | Modules |
| --- | --- | --- |
| Base infrastructure | Shared envelopes (`BaseRequest`, `BaseResponse`, `RequestStatus`), transformation utilities | `base/` |
| Canonical models | Domain entities persisted in Firestore or used for business logic | `canonical/` (casefile, tool session, chat, ACL) |
| Operations | Request/response DTOs driving R-A-R flows and tool templates | `operations/` (casefile_ops, tool_session_ops, chat_session_ops, etc.) |
| Views | Read models tailored for API responses | `views/` |
| Workspace integrations | Adapters for external sources (Gmail, Drive, Sheets) | `workspace/` |
| Mapping utilities | Generated `BaseMapper` implementations bridging canonical ↔ DTO | `mappers/` |

> Canonical models remain stable; operations and mappers evolve as services/tools add capabilities. Keep canonical schema changes versioned and reflected in inventories.

## Interactions with Tool Engineering

- Operations DTOs feed `methods_inventory_v1.yaml` and `methodtools_v1/*` to ensure tool payloads match service expectations.
- `mappers/` generation scripts (see `scripts/generate_mapper.py`) rely on canonical + operations models to produce transformation logic.
- `tool_session.py` provides shared event structures used by `MDSContext` and tool execution audit logging.

## Open Questions / Next Actions

1. Establish schema versioning per canonical model to coordinate with Firestore migrations and YAML inventories.
2. Add automated drift checks ensuring operations DTOs and generated mappers stay synchronized (run generator in CI and fail on diffs).
3. Document external workspace payload contracts to ensure Gmail/Drive/Sheets models stay aligned with upstream APIs.

## Navigation

- [[PYDANTIC_AI_INTEGRATION_OVERVIEW.md|pydantic_ai_integration overview]]
- [[CORE_SERVICE_OVERVIEW.md|coreservice overview]]
- [[BRANCH_DEVELOPMENT_PLAN.md|branch development plan]]
