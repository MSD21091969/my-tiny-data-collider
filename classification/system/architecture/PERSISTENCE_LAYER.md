# Persistence Layer Architecture

**Version:** 2.0.0  
**Date:** October 11, 2025  
**Status:** Production Ready

## Overview

The MDS persistence layer provides a unified, efficient, and observable interface for all data operations. Built on Firestore and Redis, it ensures:

- **Performance**: Connection pooling, caching, and optimized queries
- **Consistency**: Standardized CRUD operations across all repositories
- **Observability**: Built-in metrics collection for all operations
- **Reliability**: Error handling, transaction support, and graceful degradation

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Service Layer                           │
│  (CasefileService, ToolSessionService, etc.)                │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│                  Repository Layer                           │
│  - CasefileRepository (extends BaseRepository)              │
│  - ToolSessionRepository (extends BaseRepository)           │
│  - ChatSessionRepository (extends BaseRepository)           │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│              Base Repository (Abstract)                     │
│  - CRUD operations                                          │
│  - Caching integration                                      │
│  - Metrics collection                                       │
│  - Transaction support                                      │
└──────────┬──────────────────────────┬───────────────────────┘
           │                          │
┌──────────▼──────────┐    ┌─────────▼────────────┐
│  Firestore Pool     │    │   Redis Cache        │
│  - Connection mgmt  │    │   - Session cache    │
│  - Health checks    │    │   - TTL management   │
│  - Pool sizing      │    │   - Key patterns     │
└─────────────────────┘    └──────────────────────┘
```

## Core Components

### 1. BaseRepository (Abstract)

**Location:** `src/persistence/base_repository.py`

**Purpose:** Provides consistent persistence interface for all domain models.

**Features:**
- Generic type support for domain models
- Automatic caching with Redis
- Metrics collection (reads, writes, cache hits/misses)
- Connection pool management
- Transaction support
- Error handling and logging

**Abstract Methods:**
```python
def _to_dict(self, model: T) -> dict[str, Any]:
    """Convert domain model to Firestore document."""
    
def _from_dict(self, doc_id: str, data: dict[str, Any]) -> T:
    """Convert Firestore document to domain model."""
```

**Standard Operations:**
- `get_by_id(doc_id, use_cache=True)` - Fetch with caching
- `create(doc_id, model)` - Create new document
- `update(doc_id, model)` - Update existing document
- `delete(doc_id)` - Delete document
- `list_by_field(field, value, limit)` - Query by field
- `transaction()` - Begin transaction
- `get_metrics()` - Retrieve metrics

### 2. FirestoreConnectionPool

**Location:** `src/persistence/firestore_pool.py`

**Purpose:** Manage pool of Firestore AsyncClient connections for high concurrency.

**Configuration:**
- `database`: Firestore database name (default: "mds-objects")
- `pool_size`: Number of connections (default: 10)

**Methods:**
- `initialize()` - Create connection pool
- `acquire()` - Get connection from pool
- `release(client)` - Return connection to pool
- `health_check()` - Verify pool health
- `close_all()` - Cleanup on shutdown

**Usage Pattern:**
```python
client = await pool.acquire()
try:
    # Perform Firestore operations
    doc = await client.collection("casefiles").document(id).get()
finally:
    await pool.release(client)
```

### 3. RedisCacheService

**Location:** `src/persistence/redis_cache.py`

**Purpose:** High-speed caching layer for frequently accessed data.

**Configuration:**
- `redis_url`: Connection string (default: "redis://localhost:6379/0")
- `ttl`: Default TTL in seconds (default: 3600)

**Methods:**
- `initialize()` - Connect to Redis
- `get(key)` - Retrieve cached value
- `set(key, value, ttl)` - Cache value with TTL
- `delete(key)` - Invalidate cache entry
- `health_check()` - Verify Redis connectivity
- `close()` - Cleanup connection

**Cache Key Patterns:**
```
{collection}:{doc_id}                    # Single document
{collection}:list:{field}:{value}:{limit} # Query results
```

## Implementation Guide

### Creating a New Repository

1. **Extend BaseRepository:**

```python
from src.persistence.base_repository import BaseRepository
from src.pydantic_models.canonical.my_model import MyModel

class MyRepository(BaseRepository[MyModel]):
    """Repository for MyModel domain objects."""
    
    def __init__(self, firestore_pool, redis_cache=None):
        super().__init__(
            collection_name="my_collection",
            firestore_pool=firestore_pool,
            redis_cache=redis_cache,
            cache_ttl=3600,  # 1 hour
        )
    
    def _to_dict(self, model: MyModel) -> dict:
        """Convert MyModel to Firestore document."""
        return {
            "field1": model.field1,
            "field2": model.field2,
            "metadata": model.metadata.model_dump(),
        }
    
    def _from_dict(self, doc_id: str, data: dict) -> MyModel:
        """Convert Firestore document to MyModel."""
        return MyModel(
            id=doc_id,
            field1=data["field1"],
            field2=data["field2"],
            metadata=data.get("metadata", {}),
        )
```

2. **Register in ServiceContainer:**

```python
# src/coreservice/service_container.py
self.my_repository = MyRepository(
    firestore_pool=self.firestore_pool,
    redis_cache=self.redis_cache,
)
```

3. **Use in Service:**

```python
class MyService:
    def __init__(self, repository: MyRepository):
        self.repository = repository
    
    async def get_by_id(self, id: str) -> MyModel:
        return await self.repository.get_by_id(id, use_cache=True)
```

### Hierarchical Data (Subcollections)

For nested data like `casefile → session → session_request`:

```python
class ToolSessionRepository(BaseRepository[ToolSession]):
    async def get_session_request(
        self,
        casefile_id: str,
        session_id: str,
        request_id: str,
    ) -> SessionRequest:
        """Get session request from subcollection."""
        client = await self.firestore_pool.acquire()
        try:
            doc_ref = (
                client.collection("casefiles")
                .document(casefile_id)
                .collection("sessions")
                .document(session_id)
                .collection("session_requests")
                .document(request_id)
            )
            doc = await doc_ref.get()
            return self._from_dict(request_id, doc.to_dict())
        finally:
            await self.firestore_pool.release(client)
```

### Transaction Example

```python
async def transfer_session(
    self,
    session_id: str,
    from_casefile: str,
    to_casefile: str,
) -> None:
    """Transfer session between casefiles atomically."""
    transaction = await self.repository.transaction()
    
    @firestore.async_transactional
    async def _transfer(tx):
        # Read session
        session = await self.repository.get_by_id(session_id)
        
        # Update casefile reference
        session.casefile_id = to_casefile
        
        # Write updated session
        await self.repository.update(session_id, session)
    
    await _transfer(transaction)
```

## Performance Optimization

### Caching Strategy

**Cache Aggressively:**
- Single document reads: Always cache (use_cache=True)
- Frequently accessed data: Lower TTL for freshness

**Skip Cache When:**
- Write operations: Always invalidate on update/delete
- List operations: Cache only for stable queries
- Real-time requirements: Fetch directly from Firestore

### Connection Pooling

**Pool Sizing Guidelines:**
- Development: 5-10 connections
- Production: 20-50 connections (based on load)
- High traffic: 50-100 connections

**Monitor:**
- Pool exhaustion warnings in logs
- Health check failures
- Connection acquisition latency

### Query Optimization

**Indexed Fields:**
Ensure Firestore indexes exist for all `list_by_field` queries:
```
casefiles:
  - user_id
  - status
  - created_at

sessions:
  - casefile_id
  - user_id
  - status
```

**Batch Operations:**
For bulk operations, use Firestore batch writes:
```python
batch = client.batch()
for doc_id, model in updates.items():
    ref = client.collection("casefiles").document(doc_id)
    batch.update(ref, self._to_dict(model))
await batch.commit()
```

## Metrics and Monitoring

### Repository Metrics

Each repository tracks:
- `reads`: Total Firestore reads
- `writes`: Total Firestore writes (create + update)
- `deletes`: Total deletions
- `cache_hits`: Successful cache retrievals
- `cache_misses`: Cache misses requiring Firestore fetch

**Access Metrics:**
```python
metrics = repository.get_metrics()
print(f"Cache hit rate: {metrics['cache_hits'] / (metrics['cache_hits'] + metrics['cache_misses']):.2%}")
```

### Health Checks

Monitor persistence layer health:
```python
# Check Firestore pool
firestore_ok = await firestore_pool.health_check()

# Check Redis cache
redis_ok = await redis_cache.health_check()

# Overall health
persistence_ok = firestore_ok and redis_ok
```

## Error Handling

### Graceful Degradation

**Cache Failures:**
- Log error, continue without cache
- Never fail request due to cache unavailability

**Pool Exhaustion:**
- Create temporary connection
- Log warning for capacity planning

**Firestore Errors:**
- Retry transient errors (429, 503)
- Surface persistent errors to service layer

### Logging Standards

All persistence operations log:
- DEBUG: Cache hits/misses, connection pool events
- INFO: CRUD operations, metrics
- WARNING: Pool exhaustion, cache failures
- ERROR: Firestore errors, data corruption

## Migration Path

### Existing Repositories

To migrate existing repositories to BaseRepository:

1. **Identify current patterns:**
   - Direct Firestore client usage
   - Manual caching logic
   - Inconsistent error handling

2. **Refactor to BaseRepository:**
   - Extend BaseRepository[YourModel]
   - Implement _to_dict and _from_dict
   - Remove manual caching code

3. **Test thoroughly:**
   - Unit tests for conversions
   - Integration tests for CRUD operations
   - Performance tests for caching

4. **Deploy incrementally:**
   - One repository at a time
   - Monitor metrics before/after
   - Roll back if issues arise

### Example Migration

**Before:**
```python
class OldRepository:
    def __init__(self, firestore_client):
        self.client = firestore_client
    
    async def get(self, id):
        doc = await self.client.collection("items").document(id).get()
        return doc.to_dict()
```

**After:**
```python
class NewRepository(BaseRepository[Item]):
    def __init__(self, firestore_pool, redis_cache):
        super().__init__("items", firestore_pool, redis_cache)
    
    def _to_dict(self, model: Item) -> dict:
        return model.model_dump()
    
    def _from_dict(self, doc_id: str, data: dict) -> Item:
        return Item(id=doc_id, **data)
```

## Best Practices

1. **Always use connection pool** - Never create direct Firestore clients
2. **Cache read-heavy data** - Use `use_cache=True` for frequent reads
3. **Invalidate on write** - BaseRepository does this automatically
4. **Monitor metrics** - Track cache hit rates and query performance
5. **Test with mocks** - Use BaseRepository mocks in unit tests
6. **Document schema** - Maintain Firestore schema documentation
7. **Index strategically** - Create indexes for all list_by_field queries
8. **Handle errors gracefully** - Log and degrade, don't fail hard

## Future Enhancements

### Planned (TIER 3)

- **Query Builder**: Fluent API for complex queries
- **Bulk Operations**: Batch CRUD for large datasets
- **Cache Warming**: Preload frequently accessed data
- **Replication**: Read replicas for geographic distribution

### Under Consideration

- **Multi-tenancy**: Tenant-scoped collections
- **Audit Trail**: Automatic change tracking
- **Soft Deletes**: Mark as deleted instead of physical removal
- **Versioning**: Document version history

## References

- Firestore Best Practices: https://firebase.google.com/docs/firestore/best-practices
- Redis Caching Patterns: https://redis.io/docs/manual/patterns/
- Connection Pooling: https://cloud.google.com/firestore/docs/best-practices#connection_pooling

---

**Document History:**

| Version | Date | Changes |
|---------|------|---------|
| 2.0.0 | 2025-10-11 | Complete persistence layer formalization with BaseRepository |
| 1.0.0 | 2025-10-06 | Initial connection pooling and caching implementation |
