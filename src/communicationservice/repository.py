"""
Repository for chat sessions using base repository pattern.
"""

import logging

from persistence.base_repository import BaseRepository
from persistence.firestore_pool import FirestoreConnectionPool
from persistence.redis_cache import RedisCacheService
from typing import Dict, List, Optional

from src.pydantic_models.canonical.chat_session import ChatSession

logger = logging.getLogger(__name__)


class ChatSessionRepository(BaseRepository[ChatSession]):
    """Repository for chat sessions using Firestore storage."""

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
            collection_name="chat_sessions",
            firestore_pool=firestore_pool,
            redis_cache=redis_cache,
            cache_ttl=1800,  # 30 minutes cache for chat sessions
        )
        logger.info("ChatSessionRepository initialized with base repository pattern")

    def _to_dict(self, model: ChatSession) -> dict[str, any]:
        """Convert ChatSession to Firestore document.

        Args:
            model: The chat session model to convert

        Returns:
            Dictionary representation for Firestore
        """
        return model.model_dump(mode="json")

    def _from_dict(self, doc_id: str, data: dict[str, any]) -> ChatSession:
        """Convert Firestore document to ChatSession.

        Args:
            doc_id: Document ID (session_id)
            data: Firestore document data

        Returns:
            ChatSession instance
        """
        # Ensure ID is set
        data["session_id"] = doc_id
        return ChatSession.model_validate(data)

    # Compatibility methods delegating to BaseRepository

    async def create_session(self, session: ChatSession) -> None:
        """Create a new chat session.

        Args:
            session: The session to create
        """
        await self.create(session.session_id, session)

    async def update_session(self, session: ChatSession) -> None:
        """Update an existing chat session.

        Args:
            session: The session to update
        """
        await self.update(session.session_id, session)

    async def get_session(self, session_id: str) -> ChatSession | None:
        """Get a chat session by ID with caching.

        Args:
            session_id: ID of the session to retrieve

        Returns:
            The session or None if not found
        """
        return await self.get_by_id(session_id, use_cache=True)

    async def list_sessions(
        self, user_id: str | None = None, casefile_id: str | None = None
    ) -> list[ChatSession]:
        """List sessions, optionally filtered by user or casefile.

        Args:
            user_id: Optional user ID to filter by
            casefile_id: Optional casefile ID to filter by

        Returns:
            List of matching sessions
        """
        if user_id:
            return await self.list_by_field("user_id", user_id)
        elif casefile_id:
            return await self.list_by_field("casefile_id", casefile_id)
        else:
            # List all chat sessions
            return await self.list_by_field("session_id", "", limit=None)  # type: ignore
