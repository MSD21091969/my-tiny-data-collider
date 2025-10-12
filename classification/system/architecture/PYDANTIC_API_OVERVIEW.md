# pydantic_api Overview

**Tags:** `fastapi` `routers` `middleware` `metrics`

## Directory Snapshot

```text
src/pydantic_api/
  app.py                 # FastAPI app factory + middleware stack
  dependencies.py        # FastAPI dependency providers (auth, context)
  middleware.py          # Custom middleware orchestrating logging, errors, auth
  prometheus_metrics.py  # Prometheus instrumentation / endpoint helpers
  routers/
    health.py            # `/health`, `/ready`, `/live` endpoints
    tools.py             # Tool execution HTTP endpoints
    sessions.py          # Tool session management APIs
    casefiles.py         # Casefile CRUD/permission routes
    communication.py     # Chat session endpoints
    ...                  # Other domain routers wired into RequestHub/services
```

## App Composition

| Component | Purpose | Notes |
| --- | --- | --- |
| `app.py` | Creates FastAPI instance, registers middleware, mounts routers | Imports RequestHub/services via DI container |
| `middleware.py` | Defines core middleware (auth, request ID, error handling) | Aligns with ServiceContext + metrics hooks |
| `dependencies.py` | Provides FastAPI `Depends` utilities (auth token parsing, context setup) | Bridges HTTP layer and ServiceManager |
| `prometheus_metrics.py` | Exposes Prometheus metrics collector + HTTP endpoint | Integrates with `service_metrics` instrumentation |
| `routers/` | Per-domain routers mapping HTTP routes to service requests | Uses operations DTOs from `pydantic_models` |

## Request Flow Pattern

```mermaid
flowchart TD
    Client --> FastAPI
    FastAPI -->|middleware stack| Dependencies
    Dependencies --> RequestHub
    RequestHub --> ServiceManager
    ServiceManager --> Services
    Services --> Response DTOs
    Response DTOs --> FastAPI --> Client
```

- Routers construct `BaseRequest` DTOs from HTTP payloads.
- Dependencies resolve auth/session context and inject ServiceManager RequestHub.
- Middleware handles logging, error translation, metrics, correlation IDs.

## Integration Points

- **Service Container**: `app.py` initializes `ServiceManager` ensuring all routers share DI-managed services.
- **Metrics**: Prometheus exporter surfaces counters/gauges fed by `service_metrics` and middleware timing.
- **Auth**: `dependencies.py` parses tokens (mock or real) and populates context used by RequestHub hooks.

## Open Questions / Next Actions

1. Align token parsing with the auth-routing hardening plan (session_request_id, casefile enforcement).
2. Audit router coverage vs. tool inventory to ensure every YAML-defined operation has an HTTP surface when needed.
3. Consider adding API schema documentation exports linked to the classification system for discoverability.

## Navigation

- [[CORE_SERVICE_OVERVIEW.md|coreservice overview]]
- [[PYDANTIC_AI_INTEGRATION_OVERVIEW.md|pydantic_ai_integration overview]]
- [[BRANCH_DEVELOPMENT_PLAN.md|branch development plan]]
