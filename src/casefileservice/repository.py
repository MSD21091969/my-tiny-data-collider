"""
Repository for casefile data persistence using base repository pattern.
"""

import logging

from persistence.base_repository import BaseRepository
from persistence.firestore_pool import FirestoreConnectionPool
from persistence.redis_cache import RedisCacheService
from pydantic_models.canonical.casefile import CasefileModel
from pydantic_models.views.casefile_views import CasefileSummary

logger = logging.getLogger(__name__)


class CasefileRepository(BaseRepository[CasefileModel]):
    """Repository for casefile data persistence."""

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
            collection_name="casefiles",
            firestore_pool=firestore_pool,
            redis_cache=redis_cache,
            cache_ttl=3600,  # 1 hour cache for casefiles
        )
        logger.info("CasefileRepository initialized with base repository pattern")

    def _to_dict(self, model: CasefileModel) -> dict[str, any]:
        """Convert CasefileModel to Firestore document.

        Args:
            model: The casefile model to convert

        Returns:
            Dictionary representation for Firestore
        """
        casefile_dict = model.model_dump(exclude_none=True)
        # Convert set to list for Firestore
        casefile_dict["session_ids"] = list(model.session_ids)
        return casefile_dict

    def _from_dict(self, doc_id: str, data: dict[str, any]) -> CasefileModel:
        """Convert Firestore document to CasefileModel.

        Args:
            doc_id: Document ID
            data: Firestore document data

        Returns:
            CasefileModel instance
        """
        # Handle legacy field name
        if "sessions" in data and "session_ids" not in data:
            data["session_ids"] = data.pop("sessions")
        data.setdefault("session_ids", [])

        # Ensure ID is set
        data["id"] = doc_id

        return CasefileModel.model_validate(data)

    # Compatibility methods delegating to BaseRepository

    async def create_casefile(self, casefile: CasefileModel) -> str:
        """Create a new casefile.

        Args:
            casefile: The casefile to create

        Returns:
            ID of the created casefile
        """
        await self.create(casefile.id, casefile)
        return casefile.id

    async def get_casefile(self, casefile_id: str) -> CasefileModel | None:
        """Get a casefile by ID.

        Args:
            casefile_id: ID of the casefile to retrieve

        Returns:
            The casefile, or None if not found
        """
        return await self.get_by_id(casefile_id, use_cache=True)

    async def update_casefile(self, casefile: CasefileModel) -> None:
        """Update a casefile.

        Args:
            casefile: The casefile to update
        """
        await self.update(casefile.id, casefile)

    async def list_casefiles(self, user_id: str | None = None) -> list[CasefileSummary]:
        """List casefiles, optionally filtered by user.

        Args:
            user_id: Optional user ID to filter by

        Returns:
            List of casefile summaries
        """
        # Use base repository list_by_field if user_id provided
        if user_id:
            casefiles = await self.list_by_field("metadata.created_by", user_id)
        else:
            # For all casefiles, query without filter
            casefiles = await self.list_by_field("id", "", limit=None)  # type: ignore

        # Convert to summaries
        return [
            CasefileSummary(
                casefile_id=casefile.id,
                title=casefile.metadata.title,
                description=casefile.metadata.description,
                tags=casefile.metadata.tags,
                created_at=casefile.metadata.created_at,
                resource_count=casefile.resource_count,
                session_count=len(casefile.session_ids),
            )
            for casefile in casefiles
        ]

    async def delete_casefile(self, casefile_id: str) -> bool:
        """Delete a casefile.

        Args:
            casefile_id: ID of the casefile to delete

        Returns:
            Whether deletion was successful
        """
        try:
            await self.delete(casefile_id)
            return True
        except Exception as e:
            logger.error(f"Error deleting casefile {casefile_id}: {e}")
            return False
