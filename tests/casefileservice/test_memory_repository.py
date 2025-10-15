"""Unit tests for the in-memory CasefileRepository backend."""

from __future__ import annotations

import pytest
from unittest.mock import AsyncMock, MagicMock

from casefileservice.repository import CasefileRepository
from src.pydantic_models.canonical.casefile import CasefileMetadata, CasefileModel
from src.pydantic_models.workspace import CasefileGmailData


def _make_casefile(created_by: str = "user_123") -> CasefileModel:
    metadata = CasefileMetadata(
        title="Test Casefile",
        description="Memory repository test",
        tags=["test"],
        created_by=created_by,
    )
    
    # Add minimal gmail data to satisfy validation
    gmail_data = CasefileGmailData()
    
    return CasefileModel(metadata=metadata, gmail_data=gmail_data)


@pytest.mark.asyncio
async def test_memory_repository_crud_cycle(monkeypatch: pytest.MonkeyPatch) -> None:
    """Ensure the memory backend supports standard CRUD operations."""
    # Create mock firestore pool
    mock_pool = MagicMock()
    mock_client = MagicMock()  # Use MagicMock for synchronous operations
    mock_pool.acquire = AsyncMock(return_value=mock_client)
    mock_pool.release = AsyncMock(return_value=None)

    # Set up mock Firestore operations with placeholder data
    call_count = [0]
    is_deleted = [False]  # Track if delete was called
    
    def get_mock_doc():
        if is_deleted[0]:
            # After delete, document should not exist
            mock_doc = MagicMock()
            mock_doc.exists = False
            mock_doc.to_dict.return_value = None
            return mock_doc
            
        call_count[0] += 1
        data = {
            "id": "placeholder_id",
            "metadata": {
                "title": "Test Casefile" if call_count[0] == 1 else "Updated Title",
                "description": "Memory repository test", 
                "tags": ["test"],
                "created_by": "user_123",
                "created_at": "2025-01-01T00:00:00",
                "updated_at": "2025-01-01T00:00:00"
            },
            "acl": {
                "owner_id": "user_123",
                "permissions": [],
                "public_access": "none"
            },
            "session_ids": [],
            "gmail_data": {
                "messages": [],
                "threads": [],
                "labels": [],
                "synced_at": "2025-01-01T00:00:00",
                "sync_status": "completed",
                "last_sync_token": None,
                "error_message": None
            }
        }
        
        mock_doc = MagicMock()
        mock_doc.exists = True
        mock_doc.to_dict.return_value = data
        return mock_doc
    
    mock_doc_ref = MagicMock()
    mock_doc_ref.get = AsyncMock(side_effect=get_mock_doc)
    mock_doc_ref.set = AsyncMock(return_value=None)
    mock_doc_ref.update = AsyncMock(return_value=None)
    mock_doc_ref.delete = AsyncMock(side_effect=lambda: is_deleted.__setitem__(0, True))  # Mark as deleted
    
    # Mock query document for list operations
    mock_query_doc = MagicMock()
    mock_query_doc.id = "placeholder_id"
    mock_query_doc.to_dict.return_value = {
        "id": "placeholder_id",
        "metadata": {
            "title": "Updated Title",
            "description": "Memory repository test", 
            "tags": ["test"],
            "created_by": "user_123",
            "created_at": "2025-01-01T00:00:00",
            "updated_at": "2025-01-01T00:00:00"
        },
        "acl": {
            "owner_id": "user_123",
            "permissions": [],
            "public_access": "none"
        },
        "session_ids": [],
        "gmail_data": {
            "messages": [],
            "threads": [],
            "labels": [],
            "synced_at": "2025-01-01T00:00:00",
            "sync_status": "completed",
            "last_sync_token": None,
            "error_message": None
        }
    }
    
    # Mock query for list operations
    def get_query_results():
        if is_deleted[0]:
            return []  # No results after delete
        return [mock_query_doc]
    
    mock_query = MagicMock()
    mock_query.get = AsyncMock(side_effect=get_query_results)
    mock_query.limit = MagicMock(return_value=mock_query)
    
    mock_collection = MagicMock()
    mock_collection.document.return_value = mock_doc_ref
    mock_collection.where = MagicMock(return_value=mock_query)
    mock_client.collection = MagicMock(return_value=mock_collection)

    repository = CasefileRepository(firestore_pool=mock_pool)
    assert repository.collection_name == "casefiles"

    casefile = _make_casefile()
    casefile_id = await repository.create_casefile(casefile)
    assert casefile_id == casefile.id

    # Update mock data with actual casefile ID
    def update_mock_with_real_id(real_id: str):
        # Update document data
        def get_mock_doc_with_id():
            if is_deleted[0]:
                # After delete, document should not exist
                mock_doc = MagicMock()
                mock_doc.exists = False
                mock_doc.to_dict.return_value = None
                return mock_doc
                
            call_count[0] += 1
            data = {
                "id": real_id,
                "metadata": {
                    "title": "Test Casefile" if call_count[0] == 1 else "Updated Title",
                    "description": "Memory repository test", 
                    "tags": ["test"],
                    "created_by": "user_123",
                    "created_at": "2025-01-01T00:00:00",
                    "updated_at": "2025-01-01T00:00:00"
                },
                "acl": {
                    "owner_id": "user_123",
                    "permissions": [],
                    "public_access": "none"
                },
                "session_ids": [],
                "gmail_data": {
                    "messages": [],
                    "threads": [],
                    "labels": [],
                    "synced_at": "2025-01-01T00:00:00",
                    "sync_status": "completed",
                    "last_sync_token": None,
                    "error_message": None
                }
            }
            
            mock_doc = MagicMock()
            mock_doc.exists = True
            mock_doc.to_dict.return_value = data
            return mock_doc
        
        mock_doc_ref.get.side_effect = get_mock_doc_with_id
        
        # Update query doc
        mock_query_doc.id = real_id
        mock_query_doc.to_dict.return_value["id"] = real_id
    
    update_mock_with_real_id(casefile.id)

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
