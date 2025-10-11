# casefileservice Overview

**Tags:** `casefile` `context` `audit` `tool-mapping`

## Directory Snapshot

```text
src/casefileservice/
  repository.py      # Firestore persistence adapters
  service.py         # ContextAwareService subclass implementing casefile R-A-R ops
  models/
    casefile.py      # Canonical casefile entity
    permission.py    # ACL models
  mappers/
    casefile_mapper.py  # DTO ↔ domain transformations
  tools/
    CasefileService_*   # YAML tool specs referencing these operations
```

## Key Abstractions

| Concept | Definition | Related Modules |
| --- | --- | --- |
| `CasefileRepository` | Firestore gateway for casefile documents + subcollections | `repository.py` |
| `CasefileService` | Business logic, inherits `ContextAwareService` | `service.py` |
| `CasefileModel` | Canonical entity used in persistence and mapping | `models/casefile.py` |
| `CasefileMapper` | Generated mapper aligning DTOs with canonical model | `mappers/casefile_mapper.py` |
| Tool templates | YAML definitions driving tool execution | `config/methodtools_v1/CasefileService_*` |

### Service Execution Details (service.py)

| Aspect | Description | Notes |
| --- | --- | --- |
| Base class | Extends `ContextAwareService` to obtain lifecycle hooks and context propagation | Integrates with metrics + audit systems |
| Dependencies | Requires `CasefileRepository`; optional mappers & metrics are injected | Wired via `ServiceContainer` |
| Operations | CRUD, permission grants/revocations, workspace sync, session linking | Mirrors operations in YAML tool templates |
| Context usage | Reads `ServiceContext` for user/case/session; enriches response metadata | Ensures audit trail alignment |
| Metrics hooks | Overrides `_record_metrics` to emit counters for create/update/list, etc. | Works with `ServiceMetrics` when provided |

### Auth & Routing Considerations

- Auth token should encode `user_id` plus authorized `casefile_id` / `session_id` (or `session_request_id`) to provide deterministic routing.
- Login flow must create or discover `session_request_id` under the Firestore casefile hierarchy; subsequent tool/casefile actions reuse it.
- Tool requests must validate token → session mapping before execution; missing/invalid mapping should return auth failure and log the attempt.
- Batch/script callers should use service tokens mapped to dedicated system sessions to keep the audit log complete.
- RequestHub `_prepare_context` should hydrate `session_request_id` so hooks and services write audit entries to the correct subcollection.

### Open Questions / Next Actions

1. Inspect `authservice` for token schema; extend to include routing identifiers if absent.
2. Add pre-execution gate in tool session handling to assert token/session alignment.
3. Define service-token usage for automated scripts and ensure audit metadata captures those actors.

## Navigation

- [[CORE_SERVICE_OVERVIEW.md|coreservice overview]]
- [[BRANCH_DEVELOPMENT_PLAN.md|branch development plan]]
