"""
Tests for canonical model validation rules.

Validates that canonical models properly enforce business rules,
cross-field validation, and domain integrity constraints.
"""

import pytest
from datetime import datetime, timedelta
from pydantic import ValidationError

from src.pydantic_models.canonical.casefile import (
    CasefileModel,
    CasefileMetadata,
    ResourceReference,
)
from src.pydantic_models.canonical.acl import (
    CasefileACL,
    PermissionEntry,
    PermissionLevel,
)
from src.pydantic_models.canonical.tool_session import (
    ToolSession,
    ToolEvent,
    AuthToken,
)
from src.pydantic_models.canonical.chat_session import (
    ChatSession,
    MessageType,
)


class TestCasefileMetadataValidation:
    """Test CasefileMetadata validation rules."""

    def test_valid_metadata_creation(self):
        """Test creating metadata with valid data."""
        metadata = CasefileMetadata(
            title="Test Casefile",
            description="Test description",
            tags=["test", "example"],
            created_by="user@example.com"
        )
        
        assert metadata.title == "Test Casefile"
        assert len(metadata.tags) == 2
        assert "test" in metadata.tags

    def test_timestamp_order_validation_pass(self):
        """Test that valid timestamp order passes validation."""
        now = datetime.now()
        later = now + timedelta(minutes=30)
        
        metadata = CasefileMetadata(
            title="Test",
            created_by="user@example.com",
            created_at=now.isoformat(),
            updated_at=later.isoformat()
        )
        
        assert metadata.created_at <= metadata.updated_at

    def test_timestamp_order_validation_fail(self):
        """Test that invalid timestamp order fails validation."""
        now = datetime.now()
        earlier = now - timedelta(hours=1)
        
        with pytest.raises(ValidationError, match="created_at must be <="):
            CasefileMetadata(
                title="Test",
                created_by="user@example.com",
                created_at=now.isoformat(),
                updated_at=earlier.isoformat()
            )

    def test_title_length_constraints(self):
        """Test title length validation (ShortString 1-200 chars)."""
        # Valid length
        metadata = CasefileMetadata(
            title="Valid Title",
            created_by="user@example.com"
        )
        assert metadata.title == "Valid Title"
        
        # Empty title should fail
        with pytest.raises(ValidationError):
            CasefileMetadata(
                title="",
                created_by="user@example.com"
            )
        
        # Too long title should fail
        with pytest.raises(ValidationError):
            CasefileMetadata(
                title="x" * 201,
                created_by="user@example.com"
            )

    def test_description_length_constraints(self):
        """Test description length validation (MediumString 1-2000 chars)."""
        # Valid length
        metadata = CasefileMetadata(
            title="Test",
            description="Valid description",
            created_by="user@example.com"
        )
        assert metadata.description == "Valid description"
        
        # Empty description is allowed (default)
        metadata = CasefileMetadata(
            title="Test",
            created_by="user@example.com"
        )
        assert metadata.description == ""


class TestCasefileModelValidation:
    """Test CasefileModel business rule validation."""

    def test_casefile_with_typed_data_valid(self):
        """Test casefile with typed data sources passes validation."""
        from src.pydantic_models.workspace.gmail import CasefileGmailData
        
        casefile = CasefileModel(
            metadata=CasefileMetadata(
                title="Test Case",
                created_by="user@example.com"
            ),
            gmail_data=CasefileGmailData()
        )
        
        assert casefile.gmail_data is not None

    def test_casefile_with_legacy_resources_valid(self):
        """Test casefile with legacy resources passes validation."""
        casefile = CasefileModel(
            metadata=CasefileMetadata(
                title="Test Case",
                created_by="user@example.com"
            ),
            resources={
                "gmail": [
                    ResourceReference(
                        resource_id="msg_123",
                        resource_type="gmail"
                    )
                ]
            }
        )
        
        assert len(casefile.resources["gmail"]) == 1

    def test_casefile_without_data_sources_fails(self):
        """Test that casefile without any data source fails validation."""
        with pytest.raises(ValidationError, match="at least one data source"):
            CasefileModel(
                metadata=CasefileMetadata(
                    title="Test Case",
                    created_by="user@example.com"
                )
            )

    def test_casefile_id_format(self):
        """Test casefile ID format validation."""
        casefile = CasefileModel(
            id="cf_251013_test123",
            metadata=CasefileMetadata(
                title="Test",
                created_by="user@example.com"
            ),
            resources={"test": []}
        )
        
        # ID should be normalized to lowercase
        assert casefile.id == "cf_251013_test123"
        assert casefile.id.startswith("cf_")

    def test_resource_count_computed_field(self):
        """Test resource_count computed field calculation."""
        from src.pydantic_models.workspace.gmail import CasefileGmailData, GmailMessage
        
        casefile = CasefileModel(
            metadata=CasefileMetadata(
                title="Test",
                created_by="user@example.com"
            ),
            gmail_data=CasefileGmailData(
                messages=[
                    GmailMessage(
                        id="msg1",
                        thread_id="thread1",
                        sender="sender@example.com",
                        internal_date="2025-10-13T12:00:00"
                    ),
                    GmailMessage(
                        id="msg2",
                        thread_id="thread1",
                        sender="sender@example.com",
                        internal_date="2025-10-13T12:01:00"
                    )
                ]
            )
        )
        
        assert casefile.resource_count == 2


class TestCasefileACLValidation:
    """Test ACL permission checking and validation."""

    def test_owner_has_full_permissions(self):
        """Test that owner always has full permissions."""
        acl = CasefileACL(
            owner_id="owner@example.com",
            public_access=PermissionLevel.NONE
        )
        
        assert acl.get_user_permission("owner@example.com") == PermissionLevel.OWNER
        assert acl.can_read("owner@example.com")
        assert acl.can_write("owner@example.com")
        assert acl.can_share("owner@example.com")
        assert acl.can_delete("owner@example.com")

    def test_explicit_permission_overrides_public(self):
        """Test that explicit permissions override public access."""
        acl = CasefileACL(
            owner_id="owner@example.com",
            public_access=PermissionLevel.VIEWER,
            permissions=[
                PermissionEntry(
                    user_id="editor@example.com",
                    permission=PermissionLevel.EDITOR,
                    granted_by="owner@example.com"
                )
            ]
        )
        
        # Explicit permission
        assert acl.get_user_permission("editor@example.com") == PermissionLevel.EDITOR
        assert acl.can_write("editor@example.com")
        
        # Public access
        assert acl.get_user_permission("random@example.com") == PermissionLevel.VIEWER
        assert acl.can_read("random@example.com")
        assert not acl.can_write("random@example.com")

    def test_permission_hierarchy(self):
        """Test permission level hierarchy."""
        acl = CasefileACL(
            owner_id="owner@example.com",
            permissions=[
                PermissionEntry(
                    user_id="admin@example.com",
                    permission=PermissionLevel.ADMIN,
                    granted_by="owner@example.com"
                ),
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
        
        # Admin can read, write, share (but not delete)
        assert acl.can_read("admin@example.com")
        assert acl.can_write("admin@example.com")
        assert acl.can_share("admin@example.com")
        assert not acl.can_delete("admin@example.com")
        
        # Editor can read, write (but not share)
        assert acl.can_read("editor@example.com")
        assert acl.can_write("editor@example.com")
        assert not acl.can_share("editor@example.com")
        
        # Viewer can only read
        assert acl.can_read("viewer@example.com")
        assert not acl.can_write("viewer@example.com")

    def test_expired_permission_ignored(self):
        """Test that expired permissions are ignored."""
        past = (datetime.now() - timedelta(days=1)).isoformat()
        
        acl = CasefileACL(
            owner_id="owner@example.com",
            public_access=PermissionLevel.NONE,
            permissions=[
                PermissionEntry(
                    user_id="expired@example.com",
                    permission=PermissionLevel.EDITOR,
                    granted_by="owner@example.com",
                    expires_at=past
                )
            ]
        )
        
        # Expired permission should fall back to public access
        assert acl.get_user_permission("expired@example.com") == PermissionLevel.NONE
        assert not acl.can_read("expired@example.com")


class TestToolSessionValidation:
    """Test ToolSession validation rules."""

    def test_valid_tool_session_creation(self):
        """Test creating a valid tool session."""
        session = ToolSession(
            session_id="ts_test123",
            user_id="user@example.com"
        )
        
        assert session.session_id == "ts_test123"
        assert session.active is True
        assert len(session.request_ids) == 0

    def test_session_id_format_validation(self):
        """Test that session ID format is validated."""
        # Valid format
        session = ToolSession(
            session_id="ts_abc123",
            user_id="user@example.com"
        )
        assert session.session_id == "ts_abc123"
        
        # Invalid format should fail
        with pytest.raises(ValidationError, match="must start with 'ts_'"):
            ToolSession(
                session_id="cs_abc123",  # Chat session ID
                user_id="user@example.com"
            )

    def test_casefile_id_validation(self):
        """Test that casefile_id is validated when present."""
        # Valid casefile ID
        session = ToolSession(
            session_id="ts_test123",
            user_id="user@example.com",
            casefile_id="cf_251013_abc123"
        )
        assert session.casefile_id == "cf_251013_abc123"
        
        # Invalid casefile ID should fail
        with pytest.raises(ValidationError):
            ToolSession(
                session_id="ts_test123",
                user_id="user@example.com",
                casefile_id="invalid_id"
            )

    def test_timestamp_order_validation(self):
        """Test timestamp order validation for sessions."""
        now = datetime.now()
        later = now + timedelta(hours=1)
        
        session = ToolSession(
            session_id="ts_test123",
            user_id="user@example.com",
            created_at=now.isoformat(),
            updated_at=later.isoformat()
        )
        
        assert session.created_at <= session.updated_at


class TestChatSessionValidation:
    """Test ChatSession validation rules."""

    def test_valid_chat_session_creation(self):
        """Test creating a valid chat session."""
        session = ChatSession(
            session_id="cs_test123",
            user_id="user@example.com"
        )
        
        assert session.session_id == "cs_test123"
        assert session.active is True
        assert len(session.messages) == 0

    def test_session_id_format_validation(self):
        """Test that session ID format is validated."""
        # Valid format
        session = ChatSession(
            session_id="cs_abc123",
            user_id="user@example.com"
        )
        assert session.session_id == "cs_abc123"
        
        # Invalid format should fail
        with pytest.raises(ValidationError, match="must start with 'cs_'"):
            ChatSession(
                session_id="ts_abc123",  # Tool session ID
                user_id="user@example.com"
            )

    def test_message_type_enum(self):
        """Test MessageType enum values."""
        assert MessageType.USER == "user"
        assert MessageType.ASSISTANT == "assistant"
        assert MessageType.SYSTEM == "system"
        assert MessageType.TOOL == "tool"
        assert MessageType.ERROR == "error"


class TestToolEventValidation:
    """Test ToolEvent validation and serialization."""

    def test_valid_tool_event_creation(self):
        """Test creating a valid tool event."""
        event = ToolEvent(
            event_type="tool_execution_completed",
            tool_name="create_casefile_tool",
            parameters={"title": "Test Casefile"},
            status="success",
            duration_ms=250
        )
        
        assert event.event_type == "tool_execution_completed"
        assert event.duration_ms == 250
        assert event.parameters["title"] == "Test Casefile"

    def test_duration_must_be_non_negative(self):
        """Test that duration_ms must be non-negative."""
        # Valid duration
        event = ToolEvent(
            event_type="tool_execution_completed",
            tool_name="test_tool",
            duration_ms=0
        )
        assert event.duration_ms == 0
        
        # Negative duration should fail
        with pytest.raises(ValidationError, match="greater than or equal to 0"):
            ToolEvent(
                event_type="tool_execution_completed",
                tool_name="test_tool",
                duration_ms=-1
            )

    def test_chain_position_must_be_non_negative(self):
        """Test that chain_position must be non-negative."""
        # Valid position
        event = ToolEvent(
            event_type="tool_execution_completed",
            tool_name="test_tool",
            chain_position=0
        )
        assert event.chain_position == 0
        
        # Negative position should fail
        with pytest.raises(ValidationError):
            ToolEvent(
                event_type="tool_execution_completed",
                tool_name="test_tool",
                chain_position=-1
            )

    def test_ensure_serializable_validator(self):
        """Test that ensure_serializable makes all fields JSON-safe."""
        class NonSerializable:
            def __str__(self):
                return "custom_object"
        
        event = ToolEvent(
            event_type="test",
            tool_name="test_tool",
            parameters={"obj": NonSerializable()}
        )
        
        # Should convert to string
        assert isinstance(event.parameters["obj"], str)
        assert "custom_object" in event.parameters["obj"]


class TestAuthTokenValidation:
    """Test AuthToken validation."""

    def test_valid_auth_token(self):
        """Test creating a valid auth token."""
        now = int(datetime.now().timestamp())
        future = now + 3600
        
        token = AuthToken(
            user_id="user@example.com",
            iat=now,
            exp=future
        )
        
        assert token.user_id == "user@example.com"
        assert token.exp > token.iat

    def test_timestamps_must_be_positive(self):
        """Test that timestamps must be positive integers."""
        now = int(datetime.now().timestamp())
        
        # Valid positive timestamps
        token = AuthToken(
            user_id="user@example.com",
            iat=now,
            exp=now + 3600
        )
        assert token.iat > 0
        
        # Negative timestamps should fail
        with pytest.raises(ValidationError, match="greater than 0"):
            AuthToken(
                user_id="user@example.com",
                iat=-1,
                exp=now
            )
