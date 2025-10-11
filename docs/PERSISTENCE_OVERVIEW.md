# persistence Overview

**Tags:** `firestore` `redis` `persistence` `connection-pool`

## Directory Snapshot

```text
src/persistence/
  firestore/            # Firestore repositories (context/casefile/session, etc.)
  firestore_pool.py     # Firestore async connection pool + health checks
  redis_cache.py        # Redis cache wrapper (TTL, serialization helpers)
```

## Key Components

| Module | Purpose | Notes |
| --- | --- | --- |
| `firestore_pool.py` | Manages Firestore client lifecycle, pooling, and health checks | Integrates with `ServiceCache` / `ServiceHealthChecker` |
| `redis_cache.py` | Abstraction around Redis operations for caching | Complements `service_caching` strategies |
| `firestore/*` | Repository implementations for domain services | Injected via `ServiceContainer` |

### Firestore Repositories

- Each repository (e.g., `casefile_repository.py`, `tool_session_repository.py`) encapsulates Firestore collections/subcollections corresponding to canonical models.
- Repositories expose async CRUD methods returning Pydantic canonical models.
- Integrated with `ServiceContainer` for dependency injection and `ContextAwareService` for audit metadata.

### Connection Pool & Health

- `firestore_pool.py` provides pooled access; `SystemHealthChecker` uses it to validate connectivity.
- Works alongside `ServiceCache` and `CircuitBreaker` to mitigate Firestore load.

### Redis Cache

- `redis_cache.py` offers a simple async cache interface (get/set/delete) with serialization, used for quick lookups.
- Can be registered in `ServiceContainer` when environment configuration enables caching.

## Open Questions / Next Actions

1. Confirm Firestore pooling and Redis caching configurations are surfaced via `MDSConfig` for environment-specific tuning.
2. Add integration tests verifying repository ↔ canonical model alignment and persistence of session request IDs.
3. Evaluate adding metrics hooks around Redis/Firestore operations to feed `service_metrics`.

## Navigation

- [[CORE_SERVICE_OVERVIEW.md|coreservice overview]]
- [[CASEFILE_SERVICE_OVERVIEW.md|casefileservice overview]]
- [[TOOL_SESSION_SERVICE_OVERVIEW.md|tool_sessionservice overview]]
- [[BRANCH_DEVELOPMENT_PLAN.md|branch development plan]]
