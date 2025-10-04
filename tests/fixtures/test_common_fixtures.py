"""
Tests to verify that all common fixtures work correctly.

This file serves dual purposes:
1. Validates that fixtures are properly configured
2. Provides examples of how to use fixtures in tests
"""

import pytest
from tests.fixtures.common import (
    sample_user_id,
    sample_casefile,
    sample_tool_session,
    sample_mds_context,
    minimal_mds_context,
    sample_tool_event,
    sample_casefile_summary,
    empty_casefile,
    sample_tool_request,
    sample_tool_response
)


# =============================================================================
# User Fixture Tests
# =============================================================================

@pytest.mark.unit
def test_sample_user_id(sample_user_id):
    """Verify user ID fixture is properly formatted."""
    assert isinstance(sample_user_id, str)
    assert len(sample_user_id) > 0
    assert sample_user_id == "test_user_12345"


# =============================================================================
# Casefile Fixture Tests
# =============================================================================

@pytest.mark.unit
def test_sample_casefile(sample_casefile):
    """Verify casefile fixture has all expected fields."""
    assert sample_casefile.id.startswith("cf_")
    assert sample_casefile.metadata is not None
    assert sample_casefile.metadata.title == "Sample Investigation Case"
    assert "test" in sample_casefile.metadata.tags
    assert len(sample_casefile.session_ids) == 2
    assert "gmail" in sample_casefile.resources
    assert sample_casefile.resource_count == 1


@pytest.mark.unit
def test_sample_casefile_summary(sample_casefile_summary):
    """Verify casefile summary fixture."""
    assert sample_casefile_summary.id.startswith("cf_")
    assert sample_casefile_summary.resource_count == 3
    assert sample_casefile_summary.session_count == 2
    assert len(sample_casefile_summary.tags) > 0


@pytest.mark.unit
def test_empty_casefile(empty_casefile):
    """Verify empty casefile fixture has minimal data."""
    assert empty_casefile.id.startswith("cf_")
    assert len(empty_casefile.resources) == 0
    assert len(empty_casefile.session_ids) == 0
    assert empty_casefile.notes is None
    assert empty_casefile.resource_count == 0


# =============================================================================
# Tool Session Fixture Tests
# =============================================================================

@pytest.mark.unit
def test_sample_tool_event(sample_tool_event):
    """Verify tool event fixture is complete."""
    assert sample_tool_event.event_id.startswith("te_")
    assert sample_tool_event.event_type == "tool_execution_completed"
    assert sample_tool_event.tool_name == "example_tool"
    assert sample_tool_event.status == "success"
    assert sample_tool_event.duration_ms == 150
    assert "input" in sample_tool_event.parameters
    assert sample_tool_event.result_summary is not None


@pytest.mark.unit
def test_sample_tool_session(sample_tool_session):
    """Verify tool session fixture has all fields."""
    assert sample_tool_session.session_id.startswith("ts_")
    assert sample_tool_session.user_id is not None
    assert sample_tool_session.casefile_id == "cf_251001_ABC123"
    assert len(sample_tool_session.request_ids) == 2
    assert sample_tool_session.active is True


@pytest.mark.unit
def test_sample_tool_request(sample_tool_request):
    """Verify tool request fixture."""
    assert sample_tool_request.tool_name == "example_tool"
    assert "input_text" in sample_tool_request.parameters
    assert sample_tool_request.casefile_id == "cf_251001_ABC123"


@pytest.mark.unit
def test_sample_tool_response(sample_tool_response):
    """Verify tool response fixture."""
    assert sample_tool_response.result is not None
    assert "output" in sample_tool_response.result
    assert len(sample_tool_response.events) > 0


# =============================================================================
# MDSContext Fixture Tests
# =============================================================================

@pytest.mark.unit
def test_sample_mds_context(sample_mds_context):
    """Verify MDSContext fixture has comprehensive data."""
    assert sample_mds_context.user_id is not None
    assert sample_mds_context.session_id.startswith("ts_")
    assert sample_mds_context.casefile_id == "cf_251001_ABC123"
    assert len(sample_mds_context.tool_events) == 1
    assert len(sample_mds_context.conversation_history) == 2
    assert len(sample_mds_context.previous_tools) == 1
    assert len(sample_mds_context.next_planned_tools) == 1
    assert sample_mds_context.environment == "development"
    assert "current_step" in sample_mds_context.transaction_context
    assert "user_timezone" in sample_mds_context.persistent_state


@pytest.mark.unit
def test_minimal_mds_context(minimal_mds_context):
    """Verify minimal MDSContext has only required fields."""
    assert minimal_mds_context.user_id is not None
    assert minimal_mds_context.session_id.startswith("ts_")
    assert minimal_mds_context.casefile_id is None
    assert len(minimal_mds_context.tool_events) == 0
    assert len(minimal_mds_context.conversation_history) == 0
    assert minimal_mds_context.environment == "test"


# =============================================================================
# Fixture Interaction Tests
# =============================================================================

@pytest.mark.unit
def test_casefile_and_session_relationship(sample_casefile, sample_tool_session):
    """Verify casefile and session fixtures are compatible."""
    assert sample_casefile.id == sample_tool_session.casefile_id


@pytest.mark.unit
def test_session_and_context_relationship(sample_tool_session, sample_mds_context):
    """Verify session and context share the same casefile."""
    assert sample_tool_session.casefile_id == sample_mds_context.casefile_id
    assert sample_tool_session.user_id == sample_mds_context.user_id


@pytest.mark.unit
def test_user_consistency_across_fixtures(
    sample_user_id,
    sample_casefile,
    sample_tool_session,
    sample_mds_context
):
    """Verify user_id is consistent across all fixtures."""
    assert sample_casefile.metadata.created_by == sample_user_id
    assert sample_tool_session.user_id == sample_user_id
    assert sample_mds_context.user_id == sample_user_id


# =============================================================================
# Fixture Modification Tests
# =============================================================================

@pytest.mark.unit
def test_fixture_can_be_modified(sample_casefile):
    """Verify fixtures can be safely modified in tests."""
    original_title = sample_casefile.metadata.title
    sample_casefile.metadata.title = "Modified Title"
    
    assert sample_casefile.metadata.title == "Modified Title"
    assert sample_casefile.metadata.title != original_title


@pytest.mark.unit
def test_fixture_isolation(sample_casefile):
    """
    Verify fixture modifications don't affect other tests.
    
    This test modifies the fixture and subsequent tests should
    still get a fresh, unmodified version.
    """
    sample_casefile.metadata.tags.append("modified_tag")
    assert "modified_tag" in sample_casefile.metadata.tags


@pytest.mark.unit
def test_fixture_isolation_verification(sample_casefile):
    """
    Verify that the previous test's modification didn't persist.
    
    This test runs after test_fixture_isolation and should receive
    a fresh fixture without the "modified_tag".
    """
    assert "modified_tag" not in sample_casefile.metadata.tags


# =============================================================================
# Type Validation Tests
# =============================================================================

@pytest.mark.unit
def test_fixture_types(
    sample_casefile,
    sample_tool_session,
    sample_mds_context
):
    """Verify fixtures return correct types."""
    from src.pydantic_models.canonical.casefile import CasefileModel
    from src.pydantic_models.canonical.tool_session import ToolSession
    from src.pydantic_ai_integration.dependencies import MDSContext
    
    assert isinstance(sample_casefile, CasefileModel)
    assert isinstance(sample_tool_session, ToolSession)
    assert isinstance(sample_mds_context, MDSContext)


# =============================================================================
# Example Usage Patterns
# =============================================================================

@pytest.mark.unit
@pytest.mark.integration
def test_example_service_with_fixture(sample_mds_context):
    """
    Example: Using MDSContext fixture in a service test.
    
    This demonstrates how you'd use fixtures in real service tests.
    """
    # Simulate a service operation
    assert sample_mds_context.user_id is not None
    
    # Add a tool event
    sample_mds_context.tool_events.append(
        {
            "tool_name": "test_tool",
            "status": "completed"
        }
    )
    
    assert len(sample_mds_context.tool_events) == 2


@pytest.mark.unit
def test_example_multiple_fixtures(
    sample_casefile,
    sample_tool_session,
    sample_user_id
):
    """
    Example: Using multiple fixtures in one test.
    
    This shows how to combine fixtures for complex test scenarios.
    """
    # Verify relationships
    assert sample_tool_session.casefile_id == sample_casefile.id
    assert sample_tool_session.user_id == sample_user_id
    assert sample_casefile.metadata.created_by == sample_user_id
    
    # Simulate adding session to casefile
    sample_casefile.session_ids.append(sample_tool_session.session_id)
    assert sample_tool_session.session_id in sample_casefile.session_ids
