"""
Async repository for casefile data persistence with connection pooling.
"""

import logging
import os

from google.cloud.firestore import AsyncClient

from pydantic_models.canonical.casefile import CasefileModel
from pydantic_models.views.casefile_views import CasefileSummary

logger = logging.getLogger(__name__)


class CasefileAsyncRepository:
    """Async repository for casefile data persistence with connection pooling."""

    def __init__(self, pool):
        """Initialize the repository with connection pool.

        Args:
            pool: FirestoreConnectionPool instance
        """
        self.pool = pool
        self.mode = os.environ.get("CASEFILE_REPOSITORY_MODE", "firestore").lower()
        self._store: dict[str, CasefileModel] = {}

        if self.mode == "memory":
            logger.info("CasefileAsyncRepository running in in-memory mode")

    async def create_casefile(self, casefile: CasefileModel) -> str:
        """Create a new casefile.

        Args:
            casefile: The casefile to create

        Returns:
            ID of the created casefile
        """
        if self.mode == "memory":
            stored = casefile.model_copy(deep=True)
            self._store[stored.id] = stored
            return stored.id

        client: AsyncClient = await self.pool.acquire()
        try:
            casefile_id = casefile.id
            casefile_dict = casefile.model_dump(exclude_none=True)
            casefile_dict["session_ids"] = list(casefile.session_ids)

            doc_ref = client.collection("casefiles").document(casefile_id)
            await doc_ref.set(casefile_dict)

            return casefile_id
        finally:
            await self.pool.release(client)

    async def get_casefile(self, casefile_id: str) -> CasefileModel | None:
        """Get a casefile by ID.

        Args:
            casefile_id: ID of the casefile to retrieve

        Returns:
            The casefile, or None if not found
        """
        if self.mode == "memory":
            if casefile_id not in self._store:
                return None
            return self._store[casefile_id].model_copy(deep=True)

        client: AsyncClient = await self.pool.acquire()
        try:
            doc_ref = client.collection("casefiles").document(casefile_id)
            doc = await doc_ref.get()

            if doc.exists:
                casefile_data = doc.to_dict()
                if "sessions" in casefile_data and "session_ids" not in casefile_data:
                    casefile_data["session_ids"] = casefile_data.pop("sessions")
                casefile_data.setdefault("session_ids", [])
                return CasefileModel.model_validate(casefile_data)
            return None
        finally:
            await self.pool.release(client)

    async def update_casefile(self, casefile: CasefileModel) -> None:
        """Update a casefile.

        Args:
            casefile: The casefile to update
        """
        if self.mode == "memory":
            self._store[casefile.id] = casefile.model_copy(deep=True)
            return

        client: AsyncClient = await self.pool.acquire()
        try:
            casefile_dict = casefile.model_dump(exclude_none=True)
            casefile_dict["session_ids"] = list(casefile.session_ids)

            doc_ref = client.collection("casefiles").document(casefile.id)
            await doc_ref.set(casefile_dict)
        finally:
            await self.pool.release(client)

    async def list_casefiles(self, user_id: str | None = None) -> list[CasefileSummary]:
        """List casefiles, optionally filtered by user.

        Args:
            user_id: Optional user ID to filter by

        Returns:
            List of casefile summaries
        """
        if self.mode == "memory":
            summaries: list[CasefileSummary] = []
            for stored in self._store.values():
                if user_id and stored.metadata.created_by != user_id:
                    continue
                summaries.append(
                    CasefileSummary(
                        casefile_id=stored.id,
                        title=stored.metadata.title,
                        description=stored.metadata.description,
                        tags=stored.metadata.tags,
                        created_at=stored.metadata.created_at,
                        resource_count=stored.resource_count,
                        session_count=len(stored.session_ids),
                    )
                )
            return summaries

        client: AsyncClient = await self.pool.acquire()
        try:
            collection_ref = client.collection("casefiles")

            if user_id:
                query = collection_ref.where("metadata.created_by", "==", user_id)
                docs = query.stream()
            else:
                docs = collection_ref.stream()

            results = []
            async for doc in docs:
                data = doc.to_dict()

                if "sessions" in data and "session_ids" not in data:
                    data["session_ids"] = data.pop("sessions")
                data.setdefault("session_ids", [])

                casefile = CasefileModel.model_validate(data)

                results.append(
                    CasefileSummary(
                        casefile_id=casefile.id,
                        title=casefile.metadata.title,
                        description=casefile.metadata.description,
                        tags=casefile.metadata.tags,
                        created_at=casefile.metadata.created_at,
                        resource_count=casefile.resource_count,
                        session_count=len(casefile.session_ids),
                    )
                )

            return results
        finally:
            await self.pool.release(client)

    async def delete_casefile(self, casefile_id: str) -> bool:
        """Delete a casefile.

        Args:
            casefile_id: ID of the casefile to delete

        Returns:
            Whether deletion was successful
        """
        if self.mode == "memory":
            return self._store.pop(casefile_id, None) is not None

        client: AsyncClient = await self.pool.acquire()
        try:
            doc_ref = client.collection("casefiles").document(casefile_id)
            await doc_ref.delete()
            return True
        except Exception as e:
            logger.error(f"Error deleting casefile {casefile_id}: {e}")
            return False
        finally:
            await self.pool.release(client)
