"""
Common test fixtures for MDS Objects API testing.

These fixtures provide pre-configured instances of core models used throughout
the application, reducing boilerplate in test files.

Usage:
    import pytest
    from tests.fixtures.common import sample_casefile, sample_tool_session
    
    @pytest.mark.unit
    def test_something(sample_casefile):
        assert sample_casefile.id.startswith("cf_")
"""

import pytest
from datetime import datetime
from uuid import uuid4

from src.pydantic_models.canonical.casefile import (
    CasefileModel,
    CasefileMetadata,
    ResourceReference
)
from src.pydantic_models.views.casefile_views import CasefileSummary
from src.pydantic_models.canonical.tool_session import (
    ToolSession,
    ToolEvent,
)
from src.pydantic_models.operations.tool_execution_ops import (
    ToolRequestPayload,
    ToolResponsePayload,
)
# Note: ToolDefinition and ToolParameter are DEPRECATED - removed
from src.pydantic_ai_integration.dependencies import MDSContext


# =============================================================================
# User Fixtures
# =============================================================================

@pytest.fixture
def sample_user_id() -> str:
    """Provides a sample user ID for testing."""
    return "test_user_12345"


@pytest.fixture
def sample_user_email() -> str:
    """Provides a sample user email for testing."""
    return "test.user@example.com"


# =============================================================================
# Casefile Fixtures
# =============================================================================

@pytest.fixture
def sample_casefile_metadata() -> CasefileMetadata:
    """Provides sample casefile metadata."""
    return CasefileMetadata(
        title="Sample Investigation Case",
        description="A test casefile for unit testing purposes",
        tags=["test", "investigation", "sample"],
        created_by="test_user_12345",
        created_at="2025-10-01T10:00:00",
        updated_at="2025-10-01T10:00:00"
    )


@pytest.fixture
def sample_resource_reference() -> ResourceReference:
    """Provides a sample resource reference."""
    return ResourceReference(
        resource_id="email_123456",
        resource_type="gmail",
        added_at="2025-10-01T10:30:00",
        metadata={
            "subject": "Test Email",
            "from": "sender@example.com",
            "to": "recipient@example.com"
        }
    )


@pytest.fixture
def sample_casefile(sample_casefile_metadata, sample_resource_reference) -> CasefileModel:
    """
    Provides a complete sample casefile for testing.
    
    Includes:
    - Metadata with title, description, tags
    - One Gmail resource
    - Two tool session IDs
    - Additional notes
    """
    return CasefileModel(
        id="cf_251001_ABC123",
        metadata=sample_casefile_metadata,
        resources={
            "gmail": [sample_resource_reference]
        },
        session_ids=["ts_uuid1", "ts_uuid2"],
        notes="This is a test casefile for unit testing"
    )


@pytest.fixture
def sample_casefile_summary(sample_user_id) -> CasefileSummary:
    """Provides a casefile summary for testing."""
    return CasefileSummary(
        id="cf_251001_ABC123",
        title="Sample Investigation Case",
        description="A test casefile for unit testing purposes",
        tags=["test", "investigation"],
        created_at="2025-10-01T10:00:00",
        resource_count=3,
        session_count=2
    )


@pytest.fixture
def empty_casefile() -> CasefileModel:
    """Provides an empty casefile with minimal data."""
    return CasefileModel(
        id="cf_251001_EMPTY1",
        metadata=CasefileMetadata(
            title="Empty Test Case",
            description="",
            tags=[],
            created_by="test_user_12345"
        ),
        resources={},
        session_ids=[],
        notes=None
    )


# =============================================================================
# Tool Session Fixtures
# =============================================================================

@pytest.fixture
def sample_tool_event() -> ToolEvent:
    """Provides a sample tool execution event."""
    return ToolEvent(
        event_id="te_test123",
        event_type="tool_execution_completed",
        tool_name="example_tool",
        timestamp="2025-10-01T11:00:00",
        parameters={"input": "test_value"},
        result_summary={"output": "success", "count": 5},
        duration_ms=150,
        status="success",
        initiator="user",
        chain_id=str(uuid4())
    )


# ============================================================================
# DEPRECATED FIXTURES (ToolParameter, ToolDefinition removed in migration)
# These have been replaced by ManagedToolDefinition in pydantic_ai_integration
# ============================================================================

# @pytest.fixture
# def sample_tool_parameter():
#     """DEPRECATED: ToolParameter model has been removed."""
#     raise NotImplementedError("ToolParameter is deprecated. Use ManagedToolDefinition instead.")

# @pytest.fixture
# def sample_tool_definition():
#     """DEPRECATED: ToolDefinition model has been removed."""
#     raise NotImplementedError("ToolDefinition is deprecated. Use ManagedToolDefinition instead.")


@pytest.fixture
def sample_tool_session(sample_user_id) -> ToolSession:
    """
    Provides a complete tool session for testing.
    
    Includes:
    - User ID
    - Session ID (UUID format with ts_ prefix)
    - Casefile ID
    - Request IDs
    - Active status
    """
    return ToolSession(
        user_id=sample_user_id,
        session_id="ts_" + str(uuid4()),
        casefile_id="cf_251001_ABC123",
        created_at="2025-10-01T11:00:00",
        updated_at="2025-10-01T11:05:00",
        request_ids=["req_12345", "req_67890"],
        active=True
    )


@pytest.fixture
def sample_tool_request(sample_user_id) -> ToolRequestPayload:
    """Provides a sample tool request payload."""
    return ToolRequestPayload(
        tool_name="example_tool",
        parameters={"input_text": "test input"},
        prompt=None,
        casefile_id="cf_251001_ABC123",
        session_request_id="req_test123"
    )


@pytest.fixture
def sample_tool_response() -> ToolResponsePayload:
    """Provides a sample tool response payload."""
    return ToolResponsePayload(
        result={"output": "processed result", "success": True},
        events=[{"event_type": "completed", "timestamp": "2025-10-01T11:00:00"}],
        session_request_id="req_test123"
    )


# =============================================================================
# MDSContext Fixtures
# =============================================================================

@pytest.fixture
def sample_mds_context(sample_user_id, sample_tool_event) -> MDSContext:
    """
    Provides a complete MDSContext for testing.
    
    Includes:
    - User and session identifiers
    - Tool events
    - Transaction context
    - Conversation history
    - User preferences
    """
    return MDSContext(
        user_id=sample_user_id,
        session_id="ts_" + str(uuid4()),
        casefile_id="cf_251001_ABC123",
        session_request_id="req_" + str(uuid4())[:8],
        tool_events=[sample_tool_event],
        transaction_context={
            "current_step": "analysis",
            "data_source": "gmail"
        },
        persistent_state={
            "user_timezone": "UTC",
            "preferred_language": "en"
        },
        previous_tools=[
            {"tool_name": "search_emails", "status": "completed"}
        ],
        next_planned_tools=[
            {"tool_name": "analyze_sentiment", "priority": "high"}
        ],
        conversation_history=[
            {
                "role": "user",
                "content": "Find my emails about project X",
                "timestamp": "2025-10-01T10:00:00"
            },
            {
                "role": "assistant",
                "content": "Found 5 emails about project X",
                "timestamp": "2025-10-01T10:01:00"
            }
        ],
        user_preferences={
            "notification_enabled": True,
            "auto_save": True
        },
        related_documents=[
            {
                "doc_id": "doc_123",
                "title": "Project X Specifications",
                "relevance_score": 0.95
            }
        ],
        knowledge_graph={
            "entities": ["Project X", "Team A"],
            "relationships": [{"from": "Project X", "to": "Team A", "type": "assigned_to"}]
        },
        environment="development",
        created_at="2025-10-01T10:00:00",
        updated_at="2025-10-01T11:00:00"
    )


@pytest.fixture
def minimal_mds_context(sample_user_id) -> MDSContext:
    """Provides a minimal MDSContext with only required fields."""
    return MDSContext(
        user_id=sample_user_id,
        session_id="ts_" + str(uuid4()),
        casefile_id=None,
        session_request_id=None,
        tool_events=[],
        environment="test"
    )


# =============================================================================
# Utility Fixtures
# =============================================================================

@pytest.fixture
def current_timestamp() -> str:
    """Provides the current timestamp in ISO format."""
    return datetime.now().isoformat()


@pytest.fixture
def sample_uuid() -> str:
    """Provides a sample UUID for testing."""
    return str(uuid4())


@pytest.fixture
def sample_session_id(sample_uuid) -> str:
    """Provides a session ID in the correct format (ts_ prefix)."""
    return f"ts_{sample_uuid}"


@pytest.fixture
def sample_casefile_id() -> str:
    """Provides a casefile ID in the correct format (cf_yymmdd_code)."""
    return "cf_251001_TEST01"


# =============================================================================
# Mock Service Fixtures
# =============================================================================

@pytest.fixture
def mock_use_mocks_true() -> bool:
    """Flag to use mock services instead of real ones."""
    return True


@pytest.fixture
def mock_use_mocks_false() -> bool:
    """Flag to use real services instead of mocks."""
    return False
