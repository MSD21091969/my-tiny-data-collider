"""
Tests for custom Pydantic types with validation.

Validates that custom types properly enforce constraints and provide
clear error messages when validation fails.
"""

import pytest
from datetime import datetime
from pydantic import BaseModel, ValidationError

from src.pydantic_models.base.custom_types import (
    CasefileId,
    ToolSessionId,
    ChatSessionId,
    SessionId,
    PositiveInt,
    NonNegativeInt,
    PositiveFloat,
    NonNegativeFloat,
    Percentage,
    FileSizeBytes,
    NonEmptyString,
    ShortString,
    MediumString,
    LongString,
    IsoTimestamp,
    TagList,
    EmailList,
)


class TestIDTypes:
    """Test ID type validation."""

    def test_valid_casefile_id(self):
        """Test valid casefile ID format."""
        class Model(BaseModel):
            id: CasefileId

        # Valid formats
        m1 = Model(id="cf_251013_abc123")
        assert m1.id == "cf_251013_abc123"
        
        # Should normalize to lowercase
        m2 = Model(id="CF_251013_ABC123")
        assert m2.id == "cf_251013_abc123"

    def test_invalid_casefile_id_prefix(self):
        """Test casefile ID with invalid prefix."""
        class Model(BaseModel):
            id: CasefileId

        with pytest.raises(ValidationError, match="must start with 'cf_'"):
            Model(id="xx_251013_abc123")

    def test_invalid_casefile_id_format(self):
        """Test casefile ID with invalid format."""
        class Model(BaseModel):
            id: CasefileId

        with pytest.raises(ValidationError, match="format: cf_YYMMDD_code"):
            Model(id="cf_abc123")  # Missing date part

    def test_invalid_casefile_id_date(self):
        """Test casefile ID with invalid date part."""
        class Model(BaseModel):
            id: CasefileId

        with pytest.raises(ValidationError, match="must be 6 digits"):
            Model(id="cf_2025_abc123")  # Date part not 6 digits

    def test_valid_tool_session_id(self):
        """Test valid tool session ID format."""
        class Model(BaseModel):
            id: ToolSessionId

        m = Model(id="ts_abc123xyz")
        assert m.id == "ts_abc123xyz"

    def test_invalid_tool_session_id(self):
        """Test invalid tool session ID."""
        class Model(BaseModel):
            id: ToolSessionId

        with pytest.raises(ValidationError, match="must start with 'ts_'"):
            Model(id="cs_abc123")

    def test_valid_chat_session_id(self):
        """Test valid chat session ID format."""
        class Model(BaseModel):
            id: ChatSessionId

        m = Model(id="cs_abc123xyz")
        assert m.id == "cs_abc123xyz"

    def test_invalid_chat_session_id(self):
        """Test invalid chat session ID."""
        class Model(BaseModel):
            id: ChatSessionId

        with pytest.raises(ValidationError, match="must start with 'cs_'"):
            Model(id="ts_abc123")

    def test_valid_session_id_either_type(self):
        """Test SessionId accepts both tool and chat session IDs."""
        class Model(BaseModel):
            id: SessionId

        m1 = Model(id="ts_abc123")
        assert m1.id == "ts_abc123"

        m2 = Model(id="cs_xyz789")
        assert m2.id == "cs_xyz789"

    def test_invalid_session_id(self):
        """Test invalid session ID."""
        class Model(BaseModel):
            id: SessionId

        with pytest.raises(ValidationError):
            Model(id="invalid_session")


class TestNumericTypes:
    """Test numeric type validation."""

    def test_positive_int(self):
        """Test PositiveInt validation."""
        class Model(BaseModel):
            count: PositiveInt

        m = Model(count=5)
        assert m.count == 5

        with pytest.raises(ValidationError, match="greater than 0"):
            Model(count=0)

        with pytest.raises(ValidationError, match="greater than 0"):
            Model(count=-1)

    def test_non_negative_int(self):
        """Test NonNegativeInt validation."""
        class Model(BaseModel):
            count: NonNegativeInt

        m1 = Model(count=0)
        assert m1.count == 0

        m2 = Model(count=5)
        assert m2.count == 5

        with pytest.raises(ValidationError, match="greater than or equal to 0"):
            Model(count=-1)

    def test_positive_float(self):
        """Test PositiveFloat validation."""
        class Model(BaseModel):
            value: PositiveFloat

        m = Model(value=3.14)
        assert m.value == 3.14

        with pytest.raises(ValidationError, match="greater than 0"):
            Model(value=0.0)

    def test_percentage(self):
        """Test Percentage validation."""
        class Model(BaseModel):
            pct: Percentage

        m1 = Model(pct=0.0)
        assert m1.pct == 0.0

        m2 = Model(pct=50.5)
        assert m2.pct == 50.5

        m3 = Model(pct=100.0)
        assert m3.pct == 100.0

        with pytest.raises(ValidationError, match="less than or equal to 100"):
            Model(pct=100.1)

        with pytest.raises(ValidationError, match="greater than or equal to 0"):
            Model(pct=-0.1)

    def test_file_size_bytes(self):
        """Test FileSizeBytes validation."""
        class Model(BaseModel):
            size: FileSizeBytes

        m1 = Model(size=0)
        assert m1.size == 0

        m2 = Model(size=1024000)
        assert m2.size == 1024000

        with pytest.raises(ValidationError, match="greater than or equal to 0"):
            Model(size=-1)


class TestStringTypes:
    """Test string type validation."""

    def test_non_empty_string(self):
        """Test NonEmptyString validation."""
        class Model(BaseModel):
            text: NonEmptyString

        m = Model(text="hello")
        assert m.text == "hello"

        with pytest.raises(ValidationError, match="at least 1 character"):
            Model(text="")

    def test_short_string(self):
        """Test ShortString validation (1-200 chars)."""
        class Model(BaseModel):
            text: ShortString

        m = Model(text="hello")
        assert m.text == "hello"

        # Max length
        m2 = Model(text="x" * 200)
        assert len(m2.text) == 200

        with pytest.raises(ValidationError, match="at least 1 character"):
            Model(text="")

        with pytest.raises(ValidationError, match="at most 200 characters"):
            Model(text="x" * 201)

    def test_medium_string(self):
        """Test MediumString validation (1-2000 chars)."""
        class Model(BaseModel):
            text: MediumString

        m = Model(text="hello" * 100)
        assert len(m.text) == 500

        with pytest.raises(ValidationError, match="at most 2000 characters"):
            Model(text="x" * 2001)

    def test_long_string(self):
        """Test LongString validation (1-5000 chars)."""
        class Model(BaseModel):
            text: LongString

        m = Model(text="hello" * 1000)
        assert len(m.text) == 5000

        with pytest.raises(ValidationError, match="at most 5000 characters"):
            Model(text="x" * 5001)


class TestTimestampTypes:
    """Test timestamp type validation."""

    def test_valid_iso_timestamp(self):
        """Test valid ISO 8601 timestamps."""
        class Model(BaseModel):
            ts: IsoTimestamp

        # Standard format
        m1 = Model(ts="2025-10-13T12:00:00")
        assert "2025-10-13" in m1.ts

        # With timezone
        m2 = Model(ts="2025-10-13T12:00:00+00:00")
        assert "2025-10-13" in m2.ts

        # UTC with Z
        m3 = Model(ts="2025-10-13T12:00:00Z")
        assert "2025-10-13" in m3.ts

    def test_invalid_iso_timestamp(self):
        """Test invalid timestamp format."""
        class Model(BaseModel):
            ts: IsoTimestamp

        with pytest.raises(ValidationError, match="Invalid ISO 8601 timestamp"):
            Model(ts="2025-13-40")  # Invalid date

        with pytest.raises(ValidationError, match="Invalid ISO 8601 timestamp"):
            Model(ts="not-a-date")

        with pytest.raises(ValidationError, match="Timestamp cannot be empty"):
            Model(ts="")


class TestCollectionTypes:
    """Test collection type validation."""

    def test_tag_list(self):
        """Test TagList validation."""
        class Model(BaseModel):
            tags: TagList

        m = Model(tags=["tag1", "tag2", "tag3"])
        assert m.tags == ["tag1", "tag2", "tag3"]

        m2 = Model(tags=[])
        assert m2.tags == []

    def test_email_list(self):
        """Test EmailList validation."""
        class Model(BaseModel):
            emails: EmailList

        m = Model(emails=["user1@example.com", "user2@example.com"])
        assert len(m.emails) == 2

        with pytest.raises(ValidationError, match="value is not a valid email address"):
            Model(emails=["valid@example.com", "invalid-email"])


class TestIntegrationScenarios:
    """Test real-world usage scenarios."""

    def test_casefile_metadata_model(self):
        """Test using custom types in a realistic model."""
        class CasefileMetadata(BaseModel):
            title: ShortString
            description: MediumString
            tags: TagList
            created_at: IsoTimestamp

        metadata = CasefileMetadata(
            title="Test Casefile",
            description="This is a test casefile description",
            tags=["test", "example"],
            created_at="2025-10-13T12:00:00"
        )

        assert metadata.title == "Test Casefile"
        assert len(metadata.tags) == 2
        assert "2025-10-13" in metadata.created_at

    def test_pagination_model(self):
        """Test using numeric types for pagination."""
        class PaginationParams(BaseModel):
            limit: PositiveInt
            offset: NonNegativeInt

        params = PaginationParams(limit=50, offset=0)
        assert params.limit == 50
        assert params.offset == 0

        with pytest.raises(ValidationError):
            PaginationParams(limit=0, offset=0)  # limit must be positive

        with pytest.raises(ValidationError):
            PaginationParams(limit=10, offset=-1)  # offset can't be negative

    def test_session_reference_model(self):
        """Test using ID types in session references."""
        class SessionReference(BaseModel):
            casefile_id: CasefileId
            session_id: SessionId

        ref = SessionReference(
            casefile_id="cf_251013_test123",
            session_id="ts_session456"
        )

        assert ref.casefile_id == "cf_251013_test123"
        assert ref.session_id == "ts_session456"
