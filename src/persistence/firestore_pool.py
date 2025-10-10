"""
Firestore connection pooling for production performance.

Phase 10 implementation.
"""

import asyncio
import logging

from google.cloud import firestore
from google.cloud.firestore import AsyncClient

logger = logging.getLogger(__name__)


class FirestoreConnectionPool:
    """Connection pool for Firestore async clients."""

    def __init__(self, database: str = "mds-objects", pool_size: int = 10):
        self.database = database
        self.pool_size = pool_size
        self._pool: list[AsyncClient] = []
        self._lock = asyncio.Lock()
        self._initialized = False

    async def initialize(self) -> None:
        """Create connection pool on startup."""
        if self._initialized:
            return

        logger.info(f"Initializing Firestore pool (size={self.pool_size})")
        for i in range(self.pool_size):
            client = firestore.AsyncClient(database=self.database)
            self._pool.append(client)
            logger.debug(f"Created connection {i + 1}/{self.pool_size}")

        self._initialized = True
        logger.info("Firestore pool initialized")

    async def acquire(self) -> AsyncClient:
        """Get connection from pool."""
        async with self._lock:
            if not self._pool:
                logger.warning("Pool exhausted, creating temporary connection")
                return firestore.AsyncClient(database=self.database)

            client = self._pool.pop()
            logger.debug(f"Acquired connection (remaining: {len(self._pool)})")
            return client

    async def release(self, client: AsyncClient) -> None:
        """Return connection to pool."""
        async with self._lock:
            if len(self._pool) < self.pool_size:
                self._pool.append(client)
                logger.debug(f"Released connection (pool size: {len(self._pool)})")
            else:
                client.close()
                logger.debug("Pool full, closed excess connection")

    async def close_all(self) -> None:
        """Close all connections in pool."""
        logger.info("Closing all Firestore connections")
        async with self._lock:
            for client in self._pool:
                client.close()
            self._pool.clear()
        logger.info("All connections closed")

    async def health_check(self) -> bool:
        """Check if pool is healthy."""
        try:
            client = await self.acquire()
            # Try a simple operation
            await client.collection("_health").limit(1).get()
            await self.release(client)
            return True
        except Exception as e:
            logger.error(f"Pool health check failed: {e}")
            return False
