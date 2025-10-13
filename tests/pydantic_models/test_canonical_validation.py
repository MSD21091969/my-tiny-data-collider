"""
Tests for canonical model validators and business rules.

Validates that canonical models properly enforce domain integrity rules.
"""

import pytest
from datetime import datetime, timedelta
from pydantic import ValidationError

from src.pydantic_models.canonical.casefile import CasefileModel, CasefileMetadata
from src.pydantic_models.canonical.acl import CasefileACL, PermissionEntry, PermissionLevel
from src.pydantic_models.canonical.tool_session import ToolSession, ToolEvent
from src.pydantic_models.canonical.chat_session import ChatSession


class TestCasefileValidation:
    """Test casefile model validation rules."""

    def test_valid_casefile_with_gmail_data(self):
        """Test casefile creation with Gmail data source."""
        from src.pydantic_models.workspace.gmail import CasefileGmailData, GmailMessage
        
        metadata = CasefileMetadata(
            title="Test Casefile",
            created_by="user@example.com"
        )
        
        gmail_data = CasefileGmailData(
            messages=[
                GmailMessage(
                    id="msg1",
                    thread_id="thread1",
                    sender="sender@example.com",
                    internal_date="2025-10-13T12:00:00"
                )
            ]
        )
        
        casefile = CasefileModel(
            metadata=metadata,
            gmail_data=gmail_data
        )
        
        assert casefile.id.startswith("cf_")
        assert casefile.resource_count == 1

    def test_casefile_requires_data_source(self):
        """Test that casefile validation requires at least one data source."""
        metadata = CasefileMetadata(
            title="Test Casefile",
            created_by="user@example.com"
        )
        
        with pytest.raises(ValidationError, match="at least one data source"):
            CasefileModel(
                metadata=metadata,
                resources={},  # Empty resources
                gmail_data=None,
                drive_data=None,
                sheets_data=None
            )

    def test_casefile_with_legacy_resources(self):
        """Test casefile with legacy resource format."""
        from src.pydantic_models.canonical.casefile import ResourceReference
        
        metadata = CasefileMetadata(
            title="Test Casefile",
            created_by="user@example.com"
        )
        
        casefile = CasefileModel(
            metadata=metadata,
            resources={
                "gmail": [
                    ResourceReference(
                        resource_id="msg123",
                        resource_type="gmail"
                    )
                ]
            }
        )
        
        assert casefile.resource_count == 1

    def test_casefile_metadata_timestamp_order(self):
        """Test that created_at must be <= updated_at."""
        # Valid: created before updated
        metadata1 = CasefileMetadata(
            title="Test",
            created_by="user@example.com",
            created_at="2025-10-13T12:00:00",
            updated_at="2025-10-13T13:00:00"
        )
        assert metadata1.created_at < metadata1.updated_at
        
        # Invalid: created after updated
        with pytest.raises(ValidationError, match="created_at must be <="):
            CasefileMetadata(
                title="Test",
                created_by="user@example.com",
                created_at="2025-10-13T14:00:00",
                updated_at="2025-10-13T13:00:00"
            )


class TestACLValidation:
    """Test ACL model validation and permission checks."""

    def test_owner_has_full_permissions(self):
        """Test that owner has all permissions."""
        acl = CasefileACL(owner_id="owner@example.com")
        
        assert acl.can_read("owner@example.com")
        assert acl.can_write("owner@example.com")
        assert acl.can_share("owner@example.com")
        assert acl.can_delete("owner@example.com")

    def test_explicit_permissions(self):
        """Test explicit permission grants."""
        acl = CasefileACL(
            owner_id="owner@example.com",
            permissions=[
                PermissionEntry(
                    user_id="editor@example.com",
                    permission=PermissionLevel.EDITOR,
                    granted_by="owner@example.com"
                ),
                PermissionEntry(
                    user_id="viewer@example.com",
                    permission=PermissionLevel.VIEWER,
                    granted_by="owner@example.com"
                )
            ]
        )
        
        # Editor can read and write
        assert acl.can_read("editor@example.com")
        assert acl.can_write("editor@example.com")
        assert not acl.can_share("editor@example.com")
        assert not acl.can_delete("editor@example.com")
        
        # Viewer can only read
        assert acl.can_read("viewer@example.com")
        assert not acl.can_write("viewer@example.com")

    def test_public_access(self):
        """Test public access level."""
        acl = CasefileACL(
            owner_id="owner@example.com",
            public_access=PermissionLevel.VIEWER
        )
        
        # Any user has viewer access
        assert acl.can_read("anyone@example.com")
        assert not acl.can_write("anyone@example.com")

    def test_expired_permissions(self):
        """Test that expired permissions are not granted."""
        past_time = (datetime.now() - timedelta(days=1)).isoformat()
        
        acl = CasefileACL(
            owner_id="owner@example.com",
            permissions=[
                PermissionEntry(
                    user_id="user@example.com",
                    permission=PermissionLevel.EDITOR,
                    granted_by="owner@example.com",
                    expires_at=past_time
                )
            ]
        )
        
        # Expired permission should not be granted
        assert not acl.can_write("user@example.com")

    def test_permission_hierarchy(self):
        """Test permission hierarchy (admin > editor > viewer)."""
        acl = CasefileACL(
            owner_id="owner@example.com",
            permissions=[
                PermissionEntry(
                    user_id="admin@example.com",
                    permission=PermissionLevel.ADMIN,
                    granted_by="owner@example.com"
                )
            ]
        )
        
        # Admin has admin, editor, and viewer permissions
        assert acl.has_permission("admin@example.com", PermissionLevel.VIEWER)
        assert acl.has_permission("admin@example.com", PermissionLevel.EDITOR)
        assert acl.has_permission("admin@example.com", PermissionLevel.ADMIN)
        assert not acl.has_permission("admin@example.com", PermissionLevel.OWNER)


class TestToolSessionValidation:
    """Test tool session model validation."""

    def test_valid_tool_session(self):
        """Test valid tool session creation."""
        session = ToolSession(
            session_id="ts_abc123",
            user_id="user@example.com"
        )
        
        assert session.session_id == "ts_abc123"
        assert session.active is True
        assert len(session.request_ids) == 0

    def test_tool_session_with_casefile(self):
        """Test tool session linked to casefile."""
        session = ToolSession(
            session_id="ts_abc123",
            user_id="user@example.com",
            casefile_id="cf_251013_xyz789"
        )
        
        assert session.casefile_id == "cf_251013_xyz789"

    def test_tool_session_timestamp_order(self):
        """Test tool session timestamp validation."""
        # Valid timestamps
        session1 = ToolSession(
            session_id="ts_abc123",
            user_id="user@example.com",
            created_at="2025-10-13T12:00:00",
            updated_at="2025-10-13T13:00:00"
        )
        assert session1.created_at < session1.updated_at
        
        # Invalid timestamps
        with pytest.raises(ValidationError, match="created_at must be <="):
            ToolSession(
                session_id="ts_abc123",
                user_id="user@example.com",
                created_at="2025-10-13T14:00:00",
                updated_at="2025-10-13T13:00:00"
            )

    def test_tool_event_serialization(self):
        """Test tool event ensures serializable data."""
        event = ToolEvent(
            event_type="tool_execution_completed",
            tool_name="test_tool",
            parameters={"key": "value"},
            result_summary={"result": "success"}
        )
        
        # Should be serializable
        storage_format = event.to_storage_format()
        assert isinstance(storage_format, dict)
        assert storage_format["event_type"] == "tool_execution_completed"


class TestChatSessionValidation:
    """Test chat session model validation."""

    def test_valid_chat_session(self):
        """Test valid chat session creation."""
        session = ChatSession(
            session_id="cs_abc123",
            user_id="user@example.com"
        )
        
        assert session.session_id == "cs_abc123"
        assert session.active is True
        assert len(session.messages) == 0

    def test_chat_session_with_casefile(self):
        """Test chat session linked to casefile."""
        session = ChatSession(
            session_id="cs_abc123",
            user_id="user@example.com",
            casefile_id="cf_251013_xyz789"
        )
        
        assert session.casefile_id == "cf_251013_xyz789"

    def test_chat_session_timestamp_order(self):
        """Test chat session timestamp validation."""
        # Valid timestamps
        session1 = ChatSession(
            session_id="cs_abc123",
            user_id="user@example.com",
            created_at="2025-10-13T12:00:00",
            updated_at="2025-10-13T13:00:00"
        )
        assert session1.created_at < session1.updated_at
        
        # Invalid timestamps
        with pytest.raises(ValidationError, match="created_at must be <="):
            ChatSession(
                session_id="cs_abc123",
                user_id="user@example.com",
                created_at="2025-10-13T14:00:00",
                updated_at="2025-10-13T13:00:00"
            )

    def test_chat_session_with_messages(self):
        """Test chat session with message data."""
        session = ChatSession(
            session_id="cs_abc123",
            user_id="user@example.com",
            messages=[
                {"role": "user", "content": "Hello"},
                {"role": "assistant", "content": "Hi there!"}
            ]
        )
        
        assert len(session.messages) == 2
        assert session.messages[0]["role"] == "user"


class TestIDValidation:
    """Test ID format validation across models."""

    def test_casefile_id_format(self):
        """Test casefile ID validation."""
        metadata = CasefileMetadata(
            title="Test",
            created_by="user@example.com"
        )
        
        # Valid ID from generator
        casefile = CasefileModel(
            metadata=metadata,
            resources={"test": []}
        )
        assert casefile.id.startswith("cf_")

    def test_tool_session_id_format(self):
        """Test tool session ID format."""
        # Valid format
        session = ToolSession(
            session_id="ts_abc123",
            user_id="user@example.com"
        )
        assert session.session_id == "ts_abc123"
        
        # Invalid format
        with pytest.raises(ValidationError, match="must start with 'ts_'"):
            ToolSession(
                session_id="invalid_id",
                user_id="user@example.com"
            )

    def test_chat_session_id_format(self):
        """Test chat session ID format."""
        # Valid format
        session = ChatSession(
            session_id="cs_abc123",
            user_id="user@example.com"
        )
        assert session.session_id == "cs_abc123"
        
        # Invalid format
        with pytest.raises(ValidationError, match="must start with 'cs_'"):
            ChatSession(
                session_id="invalid_id",
                user_id="user@example.com"
            )
