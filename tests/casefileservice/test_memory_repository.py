"""Unit tests for the in-memory CasefileRepository backend."""

from __future__ import annotations

import pytest

from casefileservice.repository import CasefileRepository
from pydantic_models.canonical.casefile import CasefileMetadata, CasefileModel


def _make_casefile(created_by: str = "user_123") -> CasefileModel:
    metadata = CasefileMetadata(
        title="Test Casefile",
        description="Memory repository test",
        tags=["test"],
        created_by=created_by,
    )
    return CasefileModel(metadata=metadata)


@pytest.mark.asyncio
async def test_memory_repository_crud_cycle(monkeypatch: pytest.MonkeyPatch) -> None:
    """Ensure the memory backend supports standard CRUD operations."""
    monkeypatch.setenv("CASEFILE_REPOSITORY_MODE", "memory")

    repository = CasefileRepository()
    assert repository.mode == "memory"

    casefile = _make_casefile()
    casefile_id = await repository.create_casefile(casefile)
    assert casefile_id == casefile.id

    fetched = await repository.get_casefile(casefile_id)
    assert fetched is not None
    assert fetched.id == casefile_id
    assert fetched is not casefile

    casefile.metadata.title = "Updated Title"
    await repository.update_casefile(casefile)

    updated = await repository.get_casefile(casefile_id)
    assert updated is not None
    assert updated.metadata.title == "Updated Title"

    summaries = await repository.list_casefiles(casefile.metadata.created_by)
    assert len(summaries) == 1
    assert summaries[0].casefile_id == casefile_id

    deleted = await repository.delete_casefile(casefile_id)
    assert deleted is True
    assert await repository.get_casefile(casefile_id) is None
