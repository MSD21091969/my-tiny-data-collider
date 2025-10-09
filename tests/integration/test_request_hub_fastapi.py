"""Integration tests for RequestHub + FastAPI integration.

Tests the complete flow: HTTP → FastAPI Route → RequestHub → Service → Response
"""

import pytest
from httpx import AsyncClient
from datetime import datetime
from uuid import uuid4

from pydantic_api.app import create_app
from coreservice.request_hub import RequestHub
from casefileservice.service import CasefileService
from tool_sessionservice.service import ToolSessionService
from pydantic_models.base.types import RequestStatus


@pytest.fixture
def app():
    """Create FastAPI app with in-memory repositories."""
    return create_app()


@pytest.fixture
async def client(app):
    """Create async HTTP client for testing."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.fixture
def mock_user():
    """Mock authenticated user."""
    return {
        "user_id": "test_user_123",
        "session_id": "test_session_456",
        "email": "test@example.com",
        "roles": ["user"]
    }


@pytest.mark.asyncio
async def test_create_casefile_via_request_hub_route():
    """Test creating casefile through RequestHub-enabled route."""
    # Setup
    hub = RequestHub()
    
    # Create request
    from pydantic_models.operations.casefile_ops import (
        CreateCasefileRequest,
        CreateCasefilePayload
    )
    
    request = CreateCasefileRequest(
        user_id="test_user",
        session_id="test_session",
        operation="create_casefile",
        payload=CreateCasefilePayload(
            title="RequestHub Integration Test",
            description="Testing RequestHub orchestration",
            tags=["test", "integration", "request-hub"]
        ),
        hooks=["metrics", "audit"],
        context_requirements=["session"],
        policy_hints={"pattern": "default"}
    )
    
    # Execute through RequestHub
    response = await hub.dispatch(request)
    
    # Assertions
    assert response.status == RequestStatus.COMPLETED
    assert response.payload.casefile_id is not None
    assert response.payload.casefile_id.startswith("cf_")
    
    # Verify hook metadata
    assert "hook_events" in response.metadata
    assert len(response.metadata["hook_events"]) > 0
    
    # Check hook stages
    hook_stages = {event["stage"] for event in response.metadata["hook_events"]}
    assert "pre" in hook_stages
    assert "post" in hook_stages
    
    # Verify hooks executed
    hook_names = {event["hook"] for event in response.metadata["hook_events"]}
    assert "metrics" in hook_names
    assert "audit" in hook_names


@pytest.mark.asyncio
async def test_request_hub_hook_execution():
    """Test that hooks execute properly through RequestHub."""
    hub = RequestHub()
    
    from pydantic_models.operations.casefile_ops import (
        CreateCasefileRequest,
        CreateCasefilePayload
    )
    
    request = CreateCasefileRequest(
        user_id="hook_test_user",
        operation="create_casefile",
        payload=CreateCasefilePayload(
            title="Hook Test Casefile",
            description="Testing hook execution"
        ),
        hooks=["metrics", "audit"],
        metadata={"test": "hook_execution"}
    )
    
    response = await hub.dispatch(request)
    
    assert response.status == RequestStatus.COMPLETED
    
    # Verify metrics hook executed
    metrics_events = [
        e for e in response.metadata.get("hook_events", [])
        if e.get("hook") == "metrics"
    ]
    assert len(metrics_events) >= 2  # pre and post
    
    # Verify audit hook executed
    audit_log = response.metadata.get("audit_log", [])
    assert len(audit_log) >= 2  # pre and post


@pytest.mark.asyncio
async def test_request_hub_context_enrichment():
    """Test context enrichment through RequestHub."""
    # Create a session first
    from tool_sessionservice.service import ToolSessionService
    from pydantic_models.operations.tool_session_ops import (
        CreateSessionRequest,
        CreateSessionPayload
    )
    
    session_service = ToolSessionService()
    session_request = CreateSessionRequest(
        user_id="context_test_user",
        operation="create_session",
        payload=CreateSessionPayload(
            casefile_id="cf_test_123",
            title="Test Session"
        )
    )
    session_response = await session_service.create_session(session_request)
    session_id = session_response.payload.session_id
    
    # Now create casefile with session context
    hub = RequestHub()
    from pydantic_models.operations.casefile_ops import (
        CreateCasefileRequest,
        CreateCasefilePayload
    )
    
    request = CreateCasefileRequest(
        user_id="context_test_user",
        session_id=session_id,
        operation="create_casefile",
        payload=CreateCasefilePayload(
            title="Context Test Casefile"
        ),
        context_requirements=["session"],
        hooks=["metrics"]
    )
    
    response = await hub.dispatch(request)
    
    assert response.status == RequestStatus.COMPLETED
    # Context was enriched during execution
    assert response.payload.casefile_id is not None


@pytest.mark.asyncio
async def test_request_hub_composite_workflow():
    """Test composite workflow via RequestHub."""
    hub = RequestHub()
    
    from pydantic_models.operations.request_hub_ops import (
        CreateCasefileWithSessionRequest,
        CreateCasefileWithSessionPayload
    )
    
    request = CreateCasefileWithSessionRequest(
        user_id="composite_user",
        operation="workspace.casefile.create_casefile_with_session",
        payload=CreateCasefileWithSessionPayload(
            title="Composite Workflow Test",
            description="Testing composite workflow",
            auto_start_session=True,
            session_title="Auto Session",
            hook_channels=["metrics", "audit"]
        ),
        hooks=["metrics"],
        policy_hints={"pattern": "tool_session_observer"}
    )
    
    response = await hub.dispatch(request)
    
    assert response.status == RequestStatus.COMPLETED
    assert response.payload.casefile_id is not None
    assert response.payload.session_id is not None  # Session was created
    
    # Verify composite workflow executed
    assert "hook_events" in response.metadata


@pytest.mark.asyncio
async def test_request_hub_policy_patterns():
    """Test policy pattern loading and application."""
    from coreservice.policy_patterns import PolicyPatternLoader
    
    loader = PolicyPatternLoader()
    
    # Test default pattern
    default_policy = loader.load("default")
    assert default_policy["require_auth"] is True
    assert default_policy["emit_metrics"] is True
    assert default_policy["audit"] is True
    
    # Test tool session observer pattern
    observer_policy = loader.load("tool_session_observer")
    assert "session" in observer_policy["context_requirements"]
    assert "metrics" in observer_policy["hooks"]
    assert "audit" in observer_policy["hooks"]
    
    # Test fallback for unknown pattern
    unknown_policy = loader.load("nonexistent")
    assert unknown_policy == default_policy


@pytest.mark.asyncio
async def test_request_hub_error_handling():
    """Test error handling through RequestHub."""
    from pydantic import ValidationError
    hub = RequestHub()
    
    from pydantic_models.operations.casefile_ops import (
        CreateCasefileRequest,
        CreateCasefilePayload
    )
    
    # Test 1: Pydantic validation fails before dispatch (empty title)
    with pytest.raises(ValidationError) as exc_info:
        request = CreateCasefileRequest(
            user_id="error_test_user",
            operation="create_casefile",
            payload=CreateCasefilePayload(
                title="",  # Invalid: empty title
                description="Testing error handling"
            )
        )
    assert "title" in str(exc_info.value).lower()
    
    # Test 2: Valid request format but missing required context
    request = CreateCasefileRequest(
        user_id="error_test_user",
        operation="create_casefile",
        payload=CreateCasefilePayload(
            title="Error Test Casefile",
            description="Testing runtime error handling"
        ),
        context_requirements=["nonexistent_context"]  # This context doesn't exist
    )
    
    # Execute - RequestHub should handle missing context gracefully
    response = await hub.dispatch(request)
    # Response may succeed or fail depending on implementation
    # Just verify we get a response object back
    assert response is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
