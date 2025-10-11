"""
Base Repository Pattern Implementation

Provides consistent interface for all persistence operations with:
- Connection pooling (Firestore)
- Caching (Redis)
- Metrics collection
- Error handling
- Transaction support
"""

import logging
from abc import ABC, abstractmethod
from typing import Any, Generic, Optional, TypeVar, Dict, List
from datetime import datetime

from google.cloud.firestore import AsyncClient, AsyncTransaction
from pydantic import BaseModel

from src.persistence.firestore_pool import FirestoreConnectionPool
from src.persistence.redis_cache import RedisCacheService

logger = logging.getLogger(__name__)

# Generic type for domain models
T = TypeVar("T", bound=BaseModel)


class BaseRepository(ABC, Generic[T]):
    """
    Abstract base repository providing consistent persistence interface.

    All repositories should inherit from this class to ensure:
    - Consistent CRUD operations
    - Connection pooling
    - Caching integration
    - Metrics collection
    - Error handling
    """

    def __init__(
        self,
        collection_name: str,
        firestore_pool: FirestoreConnectionPool,
        redis_cache: Optional[RedisCacheService] = None,
        cache_ttl: int = 3600,
    ):
        """
        Initialize base repository.

        Args:
            collection_name: Firestore collection name
            firestore_pool: Connection pool for Firestore
            redis_cache: Optional Redis cache service
            cache_ttl: Cache TTL in seconds (default: 1 hour)
        """
        self.collection_name = collection_name
        self.firestore_pool = firestore_pool
        self.redis_cache = redis_cache
        self.cache_ttl = cache_ttl
        self._metrics: Dict[str, int] = {
            "reads": 0,
            "writes": 0,
            "deletes": 0,
            "cache_hits": 0,
            "cache_misses": 0,
        }
        logger.info(f"Initialized {self.__class__.__name__} for collection '{collection_name}'")

    @abstractmethod
    def _to_dict(self, model: T) -> Dict[str, Any]:
        """Convert domain model to Firestore document."""
        pass

    @abstractmethod
    def _from_dict(self, doc_id: str, data: Dict[str, Any]) -> T:
        """Convert Firestore document to domain model."""
        pass

    def _cache_key(self, doc_id: str) -> str:
        """Generate cache key for document."""
        return f"{self.collection_name}:{doc_id}"

    async def get_by_id(self, doc_id: str, use_cache: bool = True) -> Optional[T]:
        """
        Get document by ID with caching.

        Args:
            doc_id: Document ID
            use_cache: Whether to use cache (default: True)

        Returns:
            Domain model or None if not found
        """
        # Try cache first
        if use_cache and self.redis_cache:
            cache_key = self._cache_key(doc_id)
            cached_data = await self.redis_cache.get(cache_key)
            if cached_data:
                self._metrics["cache_hits"] += 1
                logger.debug(f"Cache hit for {doc_id}")
                return self._from_dict(doc_id, cached_data)
            self._metrics["cache_misses"] += 1

        # Fetch from Firestore
        client = await self.firestore_pool.acquire()
        try:
            doc_ref = client.collection(self.collection_name).document(doc_id)
            doc = await doc_ref.get()

            if not doc.exists:
                logger.debug(f"Document not found: {doc_id}")
                return None

            self._metrics["reads"] += 1
            data = doc.to_dict()
            model = self._from_dict(doc_id, data)

            # Update cache
            if use_cache and self.redis_cache:
                await self.redis_cache.set(cache_key, data, self.cache_ttl)

            return model

        except Exception as e:
            logger.error(f"Error fetching document {doc_id}: {e}")
            raise
        finally:
            await self.firestore_pool.release(client)

    async def create(self, doc_id: str, model: T) -> T:
        """
        Create new document.

        Args:
            doc_id: Document ID
            model: Domain model to create

        Returns:
            Created domain model
        """
        client = await self.firestore_pool.acquire()
        try:
            doc_ref = client.collection(self.collection_name).document(doc_id)
            data = self._to_dict(model)
            data["created_at"] = datetime.utcnow()
            data["updated_at"] = datetime.utcnow()

            await doc_ref.set(data)
            self._metrics["writes"] += 1
            logger.info(f"Created document {doc_id}")

            # Invalidate/update cache
            if self.redis_cache:
                cache_key = self._cache_key(doc_id)
                await self.redis_cache.set(cache_key, data, self.cache_ttl)

            return self._from_dict(doc_id, data)

        except Exception as e:
            logger.error(f"Error creating document {doc_id}: {e}")
            raise
        finally:
            await self.firestore_pool.release(client)

    async def update(self, doc_id: str, model: T) -> T:
        """
        Update existing document.

        Args:
            doc_id: Document ID
            model: Domain model with updates

        Returns:
            Updated domain model
        """
        client = await self.firestore_pool.acquire()
        try:
            doc_ref = client.collection(self.collection_name).document(doc_id)
            data = self._to_dict(model)
            data["updated_at"] = datetime.utcnow()

            await doc_ref.update(data)
            self._metrics["writes"] += 1
            logger.info(f"Updated document {doc_id}")

            # Invalidate cache
            if self.redis_cache:
                cache_key = self._cache_key(doc_id)
                await self.redis_cache.delete(cache_key)

            return model

        except Exception as e:
            logger.error(f"Error updating document {doc_id}: {e}")
            raise
        finally:
            await self.firestore_pool.release(client)

    async def delete(self, doc_id: str) -> bool:
        """
        Delete document.

        Args:
            doc_id: Document ID

        Returns:
            True if deleted
        """
        client = await self.firestore_pool.acquire()
        try:
            doc_ref = client.collection(self.collection_name).document(doc_id)
            await doc_ref.delete()
            self._metrics["deletes"] += 1
            logger.info(f"Deleted document {doc_id}")

            # Invalidate cache
            if self.redis_cache:
                cache_key = self._cache_key(doc_id)
                await self.redis_cache.delete(cache_key)

            return True

        except Exception as e:
            logger.error(f"Error deleting document {doc_id}: {e}")
            raise
        finally:
            await self.firestore_pool.release(client)

    async def list_by_field(
        self,
        field: str,
        value: Any,
        limit: int = 100,
        use_cache: bool = False,
    ) -> List[T]:
        """
        List documents by field value.

        Args:
            field: Field name to filter by
            value: Field value
            limit: Maximum results
            use_cache: Whether to use cache (default: False for lists)

        Returns:
            List of domain models
        """
        cache_key = f"{self.collection_name}:list:{field}:{value}:{limit}" if use_cache else None

        # Try cache
        if use_cache and self.redis_cache and cache_key:
            cached_data = await self.redis_cache.get(cache_key)
            if cached_data:
                self._metrics["cache_hits"] += 1
                return [self._from_dict(doc["id"], doc["data"]) for doc in cached_data]
            self._metrics["cache_misses"] += 1

        # Fetch from Firestore
        client = await self.firestore_pool.acquire()
        try:
            query = client.collection(self.collection_name).where(field, "==", value).limit(limit)
            docs = await query.get()

            self._metrics["reads"] += len(docs)
            results = []
            cache_data = []

            for doc in docs:
                data = doc.to_dict()
                model = self._from_dict(doc.id, data)
                results.append(model)
                cache_data.append({"id": doc.id, "data": data})

            # Update cache
            if use_cache and self.redis_cache and cache_key:
                await self.redis_cache.set(cache_key, cache_data, self.cache_ttl)

            return results

        except Exception as e:
            logger.error(f"Error listing documents by {field}={value}: {e}")
            raise
        finally:
            await self.firestore_pool.release(client)

    async def transaction(self) -> AsyncTransaction:
        """
        Begin transaction.

        Returns:
            Firestore transaction
        """
        client = await self.firestore_pool.acquire()
        return client.transaction()

    def get_metrics(self) -> Dict[str, int]:
        """Get repository metrics."""
        return self._metrics.copy()

    def reset_metrics(self) -> None:
        """Reset metrics counters."""
        self._metrics = {
            "reads": 0,
            "writes": 0,
            "deletes": 0,
            "cache_hits": 0,
            "cache_misses": 0,
        }
