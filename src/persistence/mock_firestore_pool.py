"""Mock Firestore connection pool for testing and development."""

import logging
from typing import Any, Dict

logger = logging.getLogger(__name__)


class MockFirestoreClient:
    """Mock Firestore client for in-memory storage."""

    def __init__(self):
        """Initialize mock client with in-memory storage."""
        self._storage: Dict[str, Dict[str, Any]] = {}

    def collection(self, name: str) -> "MockCollection":
        """Get a collection reference."""
        return MockCollection(name, self._storage)

    async def health_check(self) -> Dict[str, Any]:
        """Check health of the mock client."""
        return {"status": "healthy", "type": "mock"}


class MockCollection:
    """Mock Firestore collection."""

    def __init__(self, name: str, storage: Dict[str, Dict[str, Any]]):
        """Initialize mock collection."""
        self.name = name
        self.storage = storage
        if name not in storage:
            storage[name] = {}

    def document(self, doc_id: str) -> "MockDocument":
        """Get a document reference."""
        return MockDocument(self.name, doc_id, self.storage)


class MockDocument:
    """Mock Firestore document."""

    def __init__(self, collection_name: str, doc_id: str, storage: Dict[str, Dict[str, Any]]):
        """Initialize mock document."""
        self.collection_name = collection_name
        self.doc_id = doc_id
        self.storage = storage

    async def set(self, data: Dict[str, Any]) -> None:
        """Set document data."""
        if self.collection_name not in self.storage:
            self.storage[self.collection_name] = {}
        self.storage[self.collection_name][self.doc_id] = data.copy()
        logger.debug(f"Mock Firestore: Created {self.collection_name}/{self.doc_id}")

    async def get(self) -> "MockDocumentSnapshot":
        """Get document data."""
        if self.collection_name in self.storage and self.doc_id in self.storage[self.collection_name]:
            data = self.storage[self.collection_name][self.doc_id]
            return MockDocumentSnapshot(self.doc_id, data, exists=True)
        return MockDocumentSnapshot(self.doc_id, None, exists=False)

    async def update(self, data: Dict[str, Any]) -> None:
        """Update document data."""
        if self.collection_name in self.storage and self.doc_id in self.storage[self.collection_name]:
            self.storage[self.collection_name][self.doc_id].update(data)
            logger.debug(f"Mock Firestore: Updated {self.collection_name}/{self.doc_id}")
        else:
            raise ValueError(f"Document {self.collection_name}/{self.doc_id} not found")

    async def delete(self) -> None:
        """Delete document."""
        if self.collection_name in self.storage and self.doc_id in self.storage[self.collection_name]:
            del self.storage[self.collection_name][self.doc_id]
            logger.debug(f"Mock Firestore: Deleted {self.collection_name}/{self.doc_id}")


class MockDocumentSnapshot:
    """Mock Firestore document snapshot."""

    def __init__(self, doc_id: str, data: Any, exists: bool):
        """Initialize mock snapshot."""
        self.id = doc_id
        self._data = data
        self.exists = exists

    def to_dict(self) -> Any:
        """Get document data as dict."""
        return self._data


class MockFirestoreConnectionPool:
    """Mock Firestore connection pool for development and testing."""

    def __init__(self, **kwargs):
        """Initialize mock pool."""
        self._client = MockFirestoreClient()
        logger.info("Mock Firestore pool initialized")

    async def initialize(self) -> None:
        """Initialize the pool (no-op for mock)."""
        logger.info("Mock Firestore pool startup")

    async def acquire(self) -> MockFirestoreClient:
        """Acquire a client from the pool."""
        return self._client

    async def release(self, client: MockFirestoreClient) -> None:
        """Release a client back to the pool (no-op for mock)."""
        pass

    async def close_all(self) -> None:
        """Close all connections (no-op for mock)."""
        logger.info("Mock Firestore pool shutdown")

    async def health_check(self) -> Dict[str, Any]:
        """Check health of the pool."""
        return {"status": "mock", "type": "mock_firestore_pool"}
