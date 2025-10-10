"""
Redis cache service for session and casefile data.
"""

import json
import logging
from typing import Any

import redis.asyncio as aioredis

logger = logging.getLogger(__name__)


class RedisCacheService:
    """Redis cache service for high-frequency data."""

    def __init__(self, redis_url: str = "redis://localhost:6379/0", ttl: int = 3600):
        """Initialize Redis cache service.

        Args:
            redis_url: Redis connection URL
            ttl: Default TTL in seconds (default: 1 hour)
        """
        self.redis_url = redis_url
        self.ttl = ttl
        self._client: aioredis.Redis | None = None
        logger.info(f"RedisCacheService initialized with URL: {redis_url}, TTL: {ttl}s")

    async def initialize(self) -> None:
        """Initialize Redis connection."""
        if self._client is None:
            self._client = await aioredis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=True,
            )
            logger.info("Redis connection initialized")

    async def close(self) -> None:
        """Close Redis connection."""
        if self._client:
            await self._client.aclose()
            self._client = None
            logger.info("Redis connection closed")

    async def get(self, key: str) -> Any | None:
        """Get value from cache.

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found
        """
        if not self._client:
            logger.warning("Redis client not initialized, skipping get")
            return None

        try:
            value = await self._client.get(key)
            if value:
                logger.debug(f"Cache hit: {key}")
                return json.loads(value)
            logger.debug(f"Cache miss: {key}")
            return None
        except Exception as e:
            logger.error(f"Redis get error for key {key}: {e}")
            return None

    async def set(self, key: str, value: Any, ttl: int | None = None) -> bool:
        """Set value in cache.

        Args:
            key: Cache key
            value: Value to cache (will be JSON serialized)
            ttl: TTL in seconds (uses default if None)

        Returns:
            True if successful
        """
        if not self._client:
            logger.warning("Redis client not initialized, skipping set")
            return False

        try:
            serialized = json.dumps(value)
            ttl_to_use = ttl or self.ttl
            await self._client.setex(key, ttl_to_use, serialized)
            logger.debug(f"Cache set: {key} (TTL: {ttl_to_use}s)")
            return True
        except Exception as e:
            logger.error(f"Redis set error for key {key}: {e}")
            return False

    async def delete(self, key: str) -> bool:
        """Delete key from cache.

        Args:
            key: Cache key

        Returns:
            True if key was deleted
        """
        if not self._client:
            logger.warning("Redis client not initialized, skipping delete")
            return False

        try:
            deleted = await self._client.delete(key)
            if deleted:
                logger.debug(f"Cache deleted: {key}")
            return deleted > 0
        except Exception as e:
            logger.error(f"Redis delete error for key {key}: {e}")
            return False

    async def invalidate_pattern(self, pattern: str) -> int:
        """Delete all keys matching pattern.

        Args:
            pattern: Key pattern (e.g., "casefile:*")

        Returns:
            Number of keys deleted
        """
        if not self._client:
            logger.warning("Redis client not initialized, skipping invalidate_pattern")
            return 0

        try:
            keys = []
            async for key in self._client.scan_iter(match=pattern):
                keys.append(key)

            if keys:
                deleted = await self._client.delete(*keys)
                logger.info(f"Invalidated {deleted} keys matching pattern: {pattern}")
                return deleted
            return 0
        except Exception as e:
            logger.error(f"Redis invalidate_pattern error for pattern {pattern}: {e}")
            return 0

    async def health_check(self) -> dict[str, Any]:
        """Check Redis health.

        Returns:
            Health status dictionary
        """
        if not self._client:
            return {
                "status": "not_initialized",
                "connected": False,
            }

        try:
            await self._client.ping()
            info = await self._client.info("stats")
            return {
                "status": "healthy",
                "connected": True,
                "total_connections_received": info.get("total_connections_received"),
                "total_commands_processed": info.get("total_commands_processed"),
            }
        except Exception as e:
            logger.error(f"Redis health check failed: {e}")
            return {
                "status": "unhealthy",
                "connected": False,
                "error": str(e),
            }
