"""Repository for tool session data persistence using base repository pattern."""

import logging
from datetime import datetime

# Firestore imports for subcollections
try:
    from firebase_admin import firestore  # type: ignore
except ImportError:  # pragma: no cover
    from pydantic_ai_integration.execution import firebase_stub as firebase_admin  # type: ignore

    firestore = firebase_admin.firestore

from persistence.base_repository import BaseRepository
from persistence.firestore_pool import FirestoreConnectionPool
from persistence.redis_cache import RedisCacheService
from src.pydantic_models.canonical.tool_session import ToolEvent, ToolSession
from src.pydantic_models.operations.tool_execution_ops import ToolRequest, ToolResponse

logger = logging.getLogger(__name__)


class ToolSessionRepository(BaseRepository[ToolSession]):
    """Repository for tool session data persistence with subcollection support."""

    def __init__(
        self,
        firestore_pool: FirestoreConnectionPool,
        redis_cache: RedisCacheService | None = None,
    ):
        """Initialize the repository.

        Args:
            firestore_pool: Firestore connection pool
            redis_cache: Optional Redis cache service
        """
        super().__init__(
            collection_name="sessions",
            firestore_pool=firestore_pool,
            redis_cache=redis_cache,
            cache_ttl=1800,  # 30 minutes cache for sessions
        )
        logger.info("ToolSessionRepository initialized with base repository pattern")

    def _to_dict(self, model: ToolSession) -> dict[str, any]:
        """Convert ToolSession to Firestore document.

        Args:
            model: The tool session model to convert

        Returns:
            Dictionary representation for Firestore
        """
        return {
            "session_id": model.session_id,
            "user_id": model.user_id,
            "casefile_id": model.casefile_id,
            "created_at": model.created_at,
            "updated_at": model.updated_at,
            "request_ids": model.request_ids,
            "active": model.active,
        }

    def _from_dict(self, doc_id: str, data: dict[str, any]) -> ToolSession:
        """Convert Firestore document to ToolSession.

        Args:
            doc_id: Document ID (session_id)
            data: Firestore document data

        Returns:
            ToolSession instance
        """
        return ToolSession(
            session_id=data.get("session_id", doc_id),
            user_id=data["user_id"],
            casefile_id=data.get("casefile_id"),
            created_at=data.get("created_at", datetime.now().isoformat()),
            updated_at=data.get("updated_at", datetime.now().isoformat()),
            request_ids=data.get("request_ids", []),
            active=data.get("active", True),
        )

    # ------------------------------------------------------------------
    # Public API - Main session operations using BaseRepository
    # ------------------------------------------------------------------

    async def create_session(self, session: ToolSession) -> None:
        """Create a new session in Firestore."""
        await self.create(session.session_id, session)

    async def get_session(self, session_id: str) -> ToolSession | None:
        """Get session by ID with caching."""
        return await self.get_by_id(session_id, use_cache=True)

    async def update_session(self, session: ToolSession) -> None:
        """Update session metadata."""
        await self.update(session.session_id, session)

    async def list_sessions(
        self,
        user_id: str | None = None,
        casefile_id: str | None = None,
    ) -> list[ToolSession]:
        """List sessions with optional filtering."""
        if user_id:
            return await self.list_by_field("user_id", user_id)
        elif casefile_id:
            return await self.list_by_field("casefile_id", casefile_id)
        else:
            # List all sessions (use empty field filter)
            return await self.list_by_field("active", True)

    async def delete_session(self, session_id: str) -> None:
        """Delete a session and all its subcollections."""
        # First delete subcollections (requests and events)
        client = await self.firestore_pool.acquire()
        try:
            session_doc = client.collection(self.collection_name).document(session_id)

            # Delete all requests and their events
            requests_collection = session_doc.collection("requests")
            async for request_doc in requests_collection.stream():
                # Delete events subcollection
                events_collection = request_doc.reference.collection("events")
                async for event_doc in events_collection.stream():
                    await event_doc.reference.delete()
                # Delete request
                await request_doc.reference.delete()
        finally:
            await self.firestore_pool.release(client)

        # Then delete the session itself using BaseRepository
        await self.delete(session_id)

    # ------------------------------------------------------------------
    # Subcollection operations (requests and events)
    # ------------------------------------------------------------------

    async def add_request_to_session(
        self,
        session_id: str,
        request: ToolRequest,
        response: ToolResponse | None = None,
    ) -> None:
        """Add a request (and optional response) to a session."""
        request_id = str(request.request_id)

        client = await self.firestore_pool.acquire()
        try:
            # Store in /sessions/{session_id}/requests/{request_id}
            request_doc = (
                client.collection(self.collection_name)
                .document(session_id)
                .collection("requests")
                .document(request_id)
            )
            request_data = {
                "request": request.model_dump(mode="json"),
                "response": response.model_dump(mode="json") if response else None,
                "event_ids": request.event_ids,
                "created_at": request.timestamp,
                "updated_at": datetime.now().isoformat(),
            }
            await request_doc.set(request_data)
        finally:
            await self.firestore_pool.release(client)

    async def update_request_response(
        self, session_id: str, request_id: str, response: ToolResponse
    ) -> None:
        """Update the response for a request."""
        client = await self.firestore_pool.acquire()
        try:
            request_doc = (
                client.collection(self.collection_name)
                .document(session_id)
                .collection("requests")
                .document(request_id)
            )
            await request_doc.set(
                {
                    "response": response.model_dump(mode="json"),
                    "updated_at": datetime.now().isoformat(),
                },
                merge=True,
            )
        finally:
            await self.firestore_pool.release(client)

    async def add_event_to_request(
        self, session_id: str, request_id: str, event: ToolEvent
    ) -> None:
        """Add a ToolEvent to a request's events subcollection."""
        client = await self.firestore_pool.acquire()
        try:
            # Store in /sessions/{session_id}/requests/{request_id}/events/{event_id}
            event_doc = (
                client.collection(self.collection_name)
                .document(session_id)
                .collection("requests")
                .document(request_id)
                .collection("events")
                .document(event.event_id)
            )
            await event_doc.set(event.model_dump(mode="json"))

            # Update request's event_ids list
            request_doc = (
                client.collection(self.collection_name)
                .document(session_id)
                .collection("requests")
                .document(request_id)
            )
            await request_doc.set({"event_ids": firestore.ArrayUnion([event.event_id])}, merge=True)
        finally:
            await self.firestore_pool.release(client)

    async def get_request(self, session_id: str, request_id: str) -> dict[str, any] | None:
        """Get a request with its response."""
        client = await self.firestore_pool.acquire()
        try:
            request_doc = (
                client.collection(self.collection_name)
                .document(session_id)
                .collection("requests")
                .document(request_id)
            )
            doc = await request_doc.get()
            if not doc.exists:
                return None
            return doc.to_dict()
        finally:
            await self.firestore_pool.release(client)

    async def get_request_events(self, session_id: str, request_id: str) -> list[ToolEvent]:
        """Get all events for a request."""
        client = await self.firestore_pool.acquire()
        try:
            events_collection = (
                client.collection(self.collection_name)
                .document(session_id)
                .collection("requests")
                .document(request_id)
                .collection("events")
            )

            events = []
            async for event_doc in events_collection.order_by("timestamp").stream():
                event_data = event_doc.to_dict()
                events.append(ToolEvent(**event_data))
            return events
        finally:
            await self.firestore_pool.release(client)
