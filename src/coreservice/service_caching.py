"""
Service Caching and Pooling for MDS Architecture.

This module provides caching and connection pooling capabilities for:
- Database connection pooling
- External API response caching
- Expensive computation result caching
- Service instance pooling
"""

import asyncio
import logging
import time
from contextlib import asynccontextmanager
from typing import Any, TypeVar
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

T = TypeVar('T')


class CacheStrategy(Enum):
    """Cache eviction strategies."""
    LRU = "lru"  # Least Recently Used
    LFU = "lfu"  # Least Frequently Used
    TTL = "ttl"  # Time To Live
    SIZE = "size"  # Size-based eviction


@dataclass
class CacheEntry[T]:
    """Cache entry with metadata."""
    value: T
    created_at: float
    accessed_at: float
    access_count: int
    ttl: float | None = None
    size: int = 1

    def is_expired(self) -> bool:
        """Check if entry has expired."""
        if self.ttl is None:
            return False
        return time.time() - self.created_at > self.ttl

    def touch(self) -> None:
        """Update access metadata."""
        self.accessed_at = time.time()
        self.access_count += 1


class Cache[T]:
    """Generic cache implementation with configurable eviction strategies."""

    def __init__(
        self,
        max_size: int = 1000,
        strategy: CacheStrategy = CacheStrategy.LRU,
        default_ttl: float | None = None
    ):
        self.max_size = max_size
        self.strategy = strategy
        self.default_ttl = default_ttl
        self._cache: dict[str, CacheEntry[T]] = {}
        self._lock = asyncio.Lock()

    async def get(self, key: str) -> T | None:
        """Get value from cache."""
        async with self._lock:
            entry = self._cache.get(key)
            if entry is None:
                return None

            if entry.is_expired():
                del self._cache[key]
                return None

            entry.touch()
            return entry.value

    async def put(self, key: str, value: T, ttl: float | None = None) -> None:
        """Put value in cache."""
        async with self._lock:
            if len(self._cache) >= self.max_size:
                await self._evict()

            entry = CacheEntry(
                value=value,
                created_at=time.time(),
                accessed_at=time.time(),
                access_count=1,
                ttl=ttl or self.default_ttl
            )
            self._cache[key] = entry

    async def delete(self, key: str) -> bool:
        """Delete value from cache."""
        async with self._lock:
            if key in self._cache:
                del self._cache[key]
                return True
            return False

    async def clear(self) -> None:
        """Clear all cache entries."""
        async with self._lock:
            self._cache.clear()

    async def size(self) -> int:
        """Get current cache size."""
        async with self._lock:
            return len(self._cache)

    async def _evict(self) -> None:
        """Evict entries based on strategy."""
        if not self._cache:
            return

        if self.strategy == CacheStrategy.LRU:
            # Evict least recently used
            oldest_key = min(self._cache.keys(), key=lambda k: self._cache[k].accessed_at)
            del self._cache[oldest_key]

        elif self.strategy == CacheStrategy.LFU:
            # Evict least frequently used
            least_used_key = min(self._cache.keys(), key=lambda k: self._cache[k].access_count)
            del self._cache[least_used_key]

        elif self.strategy == CacheStrategy.SIZE:
            # Evict largest entries first
            largest_key = max(self._cache.keys(), key=lambda k: self._cache[k].size)
            del self._cache[largest_key]

        elif self.strategy == CacheStrategy.TTL:
            # Evict expired entries
            expired_keys = [k for k, v in self._cache.items() if v.is_expired()]
            for key in expired_keys:
                del self._cache[key]

            # If still need to evict, fall back to LRU
            if len(self._cache) >= self.max_size:
                oldest_key = min(self._cache.keys(), key=lambda k: self._cache[k].accessed_at)
                del self._cache[oldest_key]


class ConnectionPool[T]:
    """Generic connection pool for managing reusable connections."""

    def __init__(
        self,
        factory: callable,
        min_size: int = 1,
        max_size: int = 10,
        max_idle_time: float = 300.0,  # 5 minutes
        max_lifetime: float = 3600.0   # 1 hour
    ):
        self.factory = factory
        self.min_size = min_size
        self.max_size = max_size
        self.max_idle_time = max_idle_time
        self.max_lifetime = max_lifetime

        self._pool: asyncio.Queue[T] = asyncio.Queue(maxsize=max_size)
        self._created_count = 0
        self._lock = asyncio.Lock()

    async def initialize(self) -> None:
        """Initialize the connection pool."""
        for _ in range(self.min_size):
            conn = await self._create_connection()
            await self._pool.put(conn)

    async def _create_connection(self) -> T:
        """Create a new connection."""
        self._created_count += 1
        return await self.factory()

    @asynccontextmanager
    async def acquire(self):
        """Acquire a connection from the pool."""
        conn = await self._get_connection()
        try:
            yield conn
        finally:
            await self._return_connection(conn)

    async def _get_connection(self) -> T:
        """Get a connection from the pool."""
        try:
            # Try to get existing connection
            conn = self._pool.get_nowait()
            # Check if connection is still valid
            if await self._is_connection_valid(conn):
                return conn
            else:
                # Connection is invalid, create new one
                return await self._create_connection()
        except asyncio.QueueEmpty:
            # Pool is empty, create new connection if under max_size
            async with self._lock:
                if self._created_count < self.max_size:
                    return await self._create_connection()
                else:
                    # Wait for a connection to become available
                    return await self._pool.get()

    async def _return_connection(self, conn: T) -> None:
        """Return a connection to the pool."""
        if await self._is_connection_valid(conn):
            try:
                await self._pool.put(conn)
            except asyncio.QueueFull:
                # Pool is full, close connection
                await self._close_connection(conn)
        else:
            # Connection is invalid, close it
            await self._close_connection(conn)

    async def _is_connection_valid(self, conn: T) -> bool:
        """Check if connection is still valid."""
        # Default implementation - override in subclasses
        return True

    async def _close_connection(self, conn: T) -> None:
        """Close a connection."""
        # Default implementation - override in subclasses
        pass

    async def close(self) -> None:
        """Close all connections in the pool."""
        while not self._pool.empty():
            try:
                conn = self._pool.get_nowait()
                await self._close_connection(conn)
            except asyncio.QueueEmpty:
                break


class DatabaseConnectionPool(ConnectionPool):
    """Database connection pool with health checking."""

    def __init__(self, dsn: str, **kwargs):
        super().__init__(factory=self._create_db_connection, **kwargs)
        self.dsn = dsn

    async def _create_db_connection(self):
        """Create a database connection."""
        # This would integrate with actual database driver
        # For now, return a mock connection
        return {"dsn": self.dsn, "created_at": time.time()}

    async def _is_connection_valid(self, conn) -> bool:
        """Check if database connection is valid."""
        # Implement actual connection validation
        return time.time() - conn["created_at"] < self.max_lifetime

    async def _close_connection(self, conn) -> None:
        """Close database connection."""
        # Implement actual connection closing
        pass


class ServiceCache:
    """Centralized service cache manager."""

    def __init__(self):
        self._caches: dict[str, Cache] = {}
        self._pools: dict[str, ConnectionPool] = {}

    def create_cache(
        self,
        name: str,
        max_size: int = 1000,
        strategy: CacheStrategy = CacheStrategy.LRU,
        default_ttl: float | None = None
    ) -> Cache:
        """Create a named cache."""
        cache = Cache(max_size=max_size, strategy=strategy, default_ttl=default_ttl)
        self._caches[name] = cache
        return cache

    def get_cache(self, name: str) -> Cache | None:
        """Get a named cache."""
        return self._caches.get(name)

    def create_pool(
        self,
        name: str,
        pool_class: type,
        **kwargs
    ) -> ConnectionPool:
        """Create a named connection pool."""
        pool = pool_class(**kwargs)
        self._pools[name] = pool
        return pool

    def get_pool(self, name: str) -> ConnectionPool | None:
        """Get a named connection pool."""
        return self._pools.get(name)

    async def initialize_pools(self) -> None:
        """Initialize all connection pools."""
        for pool in self._pools.values():
            await pool.initialize()

    async def close_all(self) -> None:
        """Close all caches and pools."""
        # Clear all caches
        for cache in self._caches.values():
            await cache.clear()

        # Close all pools
        for pool in self._pools.values():
            await pool.close()


# Global service cache instance
service_cache = ServiceCache()


class CachedServiceMixin:
    """Mixin to add caching capabilities to services."""

    def __init__(self, cache_name: str = None):
        self._cache_name = cache_name or f"{self.__class__.__name__}_cache"
        self._cache = service_cache.create_cache(self._cache_name)

    async def get_cached(self, key: str) -> Any | None:
        """Get value from service cache."""
        return await self._cache.get(key)

    async def set_cached(self, key: str, value: Any, ttl: float | None = None) -> None:
        """Set value in service cache."""
        await self._cache.put(key, value, ttl)

    async def invalidate_cache(self, key: str) -> bool:
        """Invalidate a cache entry."""
        return await self._cache.delete(key)

    async def clear_cache(self) -> None:
        """Clear all cache entries for this service."""
        await self._cache.clear()


# Circuit Breaker Implementation
class CircuitBreakerState(Enum):
    CLOSED = "closed"      # Normal operation
    OPEN = "open"         # Failing, requests rejected
    HALF_OPEN = "half_open"  # Testing if service recovered


@dataclass
class CircuitBreakerConfig:
    """Configuration for circuit breaker."""
    failure_threshold: int = 5  # Number of failures to open circuit
    recovery_timeout: float = 60.0  # Time to wait before trying again
    success_threshold: int = 3  # Number of successes needed to close circuit
    timeout: float = 10.0  # Request timeout


class CircuitBreaker:
    """Circuit breaker pattern implementation."""

    def __init__(self, name: str, config: CircuitBreakerConfig = None):
        self.name = name
        self.config = config or CircuitBreakerConfig()
        self.state = CircuitBreakerState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = 0.0
        self._lock = asyncio.Lock()

    async def call(self, func, *args, **kwargs):
        """Execute function with circuit breaker protection."""
        async with self._lock:
            if self.state == CircuitBreakerState.OPEN:
                if time.time() - self.last_failure_time > self.config.recovery_timeout:
                    self.state = CircuitBreakerState.HALF_OPEN
                    self.success_count = 0
                else:
                    raise CircuitBreakerOpenException(f"Circuit breaker {self.name} is OPEN")

            try:
                # Execute with timeout
                result = await asyncio.wait_for(
                    func(*args, **kwargs),
                    timeout=self.config.timeout
                )

                await self._on_success()
                return result

            except Exception as e:
                await self._on_failure()
                raise e

    async def _on_success(self):
        """Handle successful call."""
        if self.state == CircuitBreakerState.HALF_OPEN:
            self.success_count += 1
            if self.success_count >= self.config.success_threshold:
                self.state = CircuitBreakerState.CLOSED
                self.failure_count = 0
                logger.info(f"Circuit breaker {self.name} CLOSED")

    async def _on_failure(self):
        """Handle failed call."""
        self.failure_count += 1
        self.last_failure_time = time.time()

        if self.failure_count >= self.config.failure_threshold:
            self.state = CircuitBreakerState.OPEN
            logger.warning(f"Circuit breaker {self.name} OPENED after {self.failure_count} failures")

    def get_state(self) -> CircuitBreakerState:
        """Get current circuit breaker state."""
        return self.state


class CircuitBreakerOpenException(Exception):
    """Exception raised when circuit breaker is open."""
    pass


class CircuitBreakerRegistry:
    """Registry for managing circuit breakers."""

    def __init__(self):
        self._breakers: dict[str, CircuitBreaker] = {}

    def get_or_create(self, name: str, config: CircuitBreakerConfig = None) -> CircuitBreaker:
        """Get or create a circuit breaker."""
        if name not in self._breakers:
            self._breakers[name] = CircuitBreaker(name, config)
        return self._breakers[name]

    def get_all_states(self) -> dict[str, CircuitBreakerState]:
        """Get states of all circuit breakers."""
        return {name: breaker.get_state() for name, breaker in self._breakers.items()}


# Global circuit breaker registry
circuit_breaker_registry = CircuitBreakerRegistry()
