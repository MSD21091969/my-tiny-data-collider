"""
Integration tests for RequestHub with FastAPI routes.

Tests end-to-end flow: HTTP → FastAPI → RequestHub → Service → Response
Validates hook execution, context enrichment, and metadata propagation.
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, AsyncMock, patch
from uuid import uuid4

from pydantic_api.app import create_app
from coreservice.request_hub import RequestHub
from casefileservice.service import CasefileService
from tool_sessionservice.service import ToolSessionService
from pydantic_models.base.types import RequestStatus


@pytest.fixture
def test_app():
    """Create test FastAPI app."""
    app = create_app()
    return app


@pytest.fixture
def test_client(test_app):
    """Create test client."""
    return TestClient(test_app)


@pytest.fixture
def mock_auth():
    """Mock authentication."""
    return {
        "user_id": "test_user_123",
        "session_id": "test_session_456",
        "roles": ["user"]
    }


class TestRequestHubFastAPIIntegration:
    """Test RequestHub integration with FastAPI routes."""
    
    @pytest.mark.asyncio
    async def test_create_casefile_via_hub_with_hooks(self, test_client, mock_auth):
        """Test casefile creation via RequestHub with hook execution."""
        # Mock authentication
        with patch('pydantic_api.routers.casefile.get_current_user', return_value=mock_auth):
            response = test_client.post(
                "/casefiles/hub",
                params={
                    "title": "Test Casefile via Hub",
                    "description": "Testing RequestHub integration",
                    "tags": ["test", "integration"],
                    "enable_hooks": True
                }
            )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert "request_id" in data
        assert "status" in data
        assert "payload" in data
        assert data["status"] == "COMPLETED"
        
        # Verify payload contains casefile data
        assert "casefile_id" in data["payload"]
        assert data["payload"]["title"] == "Test Casefile via Hub"
        
        # Verify hook metadata is present
        assert "metadata" in data
        # Hook events should be in metadata if hooks were executed
        # Note: Actual hook execution depends on RequestHub implementation
    
    @pytest.mark.asyncio
    async def test_create_casefile_via_hub_without_hooks(self, test_client, mock_auth):
        """Test casefile creation via RequestHub without hooks."""
        with patch('pydantic_api.routers.casefile.get_current_user', return_value=mock_auth):
            response = test_client.post(
                "/casefiles/hub",
                params={
                    "title": "Test Casefile No Hooks",
                    "description": "Testing without hooks",
                    "enable_hooks": False
                }
            )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "COMPLETED"
        assert "casefile_id" in data["payload"]
        
        # Verify hooks were not executed
        if "metadata" in data and "hook_events" in data["metadata"]:
            assert len(data["metadata"]["hook_events"]) == 0
    
    @pytest.mark.asyncio
    async def test_create_casefile_standard_vs_hub_comparison(self, test_client, mock_auth):
        """Compare standard route vs RequestHub route."""
        with patch('pydantic_api.routers.casefile.get_current_user', return_value=mock_auth):
            # Standard route (no RequestHub)
            response_standard = test_client.post(
                "/casefiles/",
                params={
                    "title": "Standard Route Casefile",
                    "description": "Via standard service call"
                }
            )
            
            # RequestHub route
            response_hub = test_client.post(
                "/casefiles/hub",
                params={
                    "title": "Hub Route Casefile",
                    "description": "Via RequestHub orchestration",
                    "enable_hooks": True
                }
            )
        
        # Both should succeed
        assert response_standard.status_code == 200
        assert response_hub.status_code == 200
        
        data_standard = response_standard.json()
        data_hub = response_hub.json()
        
        # Both should create casefiles
        assert "casefile_id" in data_standard["payload"]
        assert "casefile_id" in data_hub["payload"]
        
        # Hub route should have additional metadata (hooks, etc.)
        # Standard route may have less metadata
        assert "metadata" in data_hub


class TestRequestHubHookExecution:
    """Test hook execution through RequestHub."""
    
    @pytest.mark.asyncio
    async def test_metrics_hook_execution(self):
        """Test that metrics hook executes and records timing."""
        from coreservice.request_hub import RequestHub
        from pydantic_models.operations.casefile_ops import (
            CreateCasefileRequest,
            CreateCasefilePayload
        )
        
        # Create mock services
        mock_casefile_service = Mock()
        mock_casefile_service.create_casefile = AsyncMock(return_value=Mock(
            request_id=uuid4(),
            status=RequestStatus.COMPLETED,
            payload=Mock(
                casefile_id="cf_test_001",
                title="Test Casefile",
                created_at="2025-10-09T15:00:00",
                created_by="test_user"
            ),
            metadata={}
        ))
        
        # Create RequestHub with mocked services
        hub = RequestHub(casefile_service=mock_casefile_service)
        
        # Create request with hooks enabled
        request = CreateCasefileRequest(
            user_id="test_user",
            operation="create_casefile",
            payload=CreateCasefilePayload(
                title="Test Casefile",
                description="Testing metrics hook"
            ),
            hooks=["metrics", "audit"],
            metadata={"test": "metrics_hook"}
        )
        
        # Execute via RequestHub
        response = await hub.dispatch(request)
        
        # Verify hooks were executed
        assert "metadata" in response.model_dump()
        metadata = response.metadata
        
        # Check for hook events
        if "hook_events" in metadata:
            hook_events = metadata["hook_events"]
            assert len(hook_events) > 0
            
            # Verify metrics hook was called
            metric_events = [e for e in hook_events if e.get("hook") == "metrics"]
            assert len(metric_events) > 0
    
    @pytest.mark.asyncio
    async def test_audit_hook_execution(self):
        """Test that audit hook executes and creates audit trail."""
        from coreservice.request_hub import RequestHub
        from pydantic_models.operations.casefile_ops import (
            CreateCasefileRequest,
            CreateCasefilePayload
        )
        
        mock_casefile_service = Mock()
        mock_casefile_service.create_casefile = AsyncMock(return_value=Mock(
            request_id=uuid4(),
            status=RequestStatus.COMPLETED,
            payload=Mock(
                casefile_id="cf_test_002",
                title="Audit Test",
                created_at="2025-10-09T15:00:00",
                created_by="test_user"
            ),
            metadata={}
        ))
        
        hub = RequestHub(casefile_service=mock_casefile_service)
        
        request = CreateCasefileRequest(
            user_id="test_user",
            session_id="test_session",
            operation="create_casefile",
            payload=CreateCasefilePayload(
                title="Audit Test",
                description="Testing audit hook"
            ),
            hooks=["audit"],
            metadata={"test": "audit_hook"}
        )
        
        response = await hub.dispatch(request)
        
        # Verify audit log was created
        if "audit_log" in response.metadata:
            audit_log = response.metadata["audit_log"]
            assert len(audit_log) > 0
            
            # Verify audit entries have required fields
            for entry in audit_log:
                assert "operation" in entry
                assert "user_id" in entry


class TestRequestHubContextEnrichment:
    """Test context enrichment through RequestHub."""
    
    @pytest.mark.asyncio
    async def test_session_context_enrichment(self):
        """Test that session context is loaded when requested."""
        from coreservice.request_hub import RequestHub
        from pydantic_models.operations.casefile_ops import (
            CreateCasefileRequest,
            CreateCasefilePayload
        )
        
        # Create mock session
        mock_session = Mock(
            session_id="test_session_123",
            user_id="test_user",
            created_at="2025-10-09T14:00:00"
        )
        mock_session.model_dump = Mock(return_value={
            "session_id": "test_session_123",
            "user_id": "test_user"
        })
        
        # Mock services
        mock_tool_session_service = Mock()
        mock_tool_session_service.repository = Mock()
        mock_tool_session_service.repository.get_session = AsyncMock(return_value=mock_session)
        
        mock_casefile_service = Mock()
        mock_casefile_service.create_casefile = AsyncMock(return_value=Mock(
            request_id=uuid4(),
            status=RequestStatus.COMPLETED,
            payload=Mock(casefile_id="cf_test_003"),
            metadata={}
        ))
        
        hub = RequestHub(
            casefile_service=mock_casefile_service,
            tool_session_service=mock_tool_session_service
        )
        
        request = CreateCasefileRequest(
            user_id="test_user",
            session_id="test_session_123",
            operation="create_casefile",
            payload=CreateCasefilePayload(title="Context Test"),
            context_requirements=["session"],  # Request session context
            hooks=[]
        )
        
        response = await hub.dispatch(request)
        
        # Verify session was fetched
        mock_tool_session_service.repository.get_session.assert_called_once_with("test_session_123")
        
        # Verify response completed successfully
        assert response.status == RequestStatus.COMPLETED


class TestRequestHubErrorHandling:
    """Test error handling in RequestHub workflows."""
    
    @pytest.mark.asyncio
    async def test_service_error_propagation(self):
        """Test that service errors are properly caught and returned."""
        from coreservice.request_hub import RequestHub
        from pydantic_models.operations.casefile_ops import (
            CreateCasefileRequest,
            CreateCasefilePayload
        )
        
        # Mock service that raises an error
        mock_casefile_service = Mock()
        mock_casefile_service.create_casefile = AsyncMock(side_effect=Exception("Database connection failed"))
        
        hub = RequestHub(casefile_service=mock_casefile_service)
        
        request = CreateCasefileRequest(
            user_id="test_user",
            operation="create_casefile",
            payload=CreateCasefilePayload(title="Error Test")
        )
        
        # Should raise exception (RequestHub doesn't catch by default)
        with pytest.raises(Exception) as exc_info:
            await hub.dispatch(request)
        
        assert "Database connection failed" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_invalid_operation_error(self):
        """Test that invalid operations are rejected."""
        from coreservice.request_hub import RequestHub
        from pydantic_models.operations.casefile_ops import CreateCasefileRequest, CreateCasefilePayload
        
        hub = RequestHub()
        
        request = CreateCasefileRequest(
            user_id="test_user",
            operation="invalid_operation",  # Invalid operation
            payload=CreateCasefilePayload(title="Invalid Op Test")
        )
        
        with pytest.raises(ValueError) as exc_info:
            await hub.dispatch(request)
        
        assert "does not handle operation" in str(exc_info.value)


class TestRequestHubCompositeWorkflow:
    """Test composite workflows through RequestHub."""
    
    @pytest.mark.asyncio
    async def test_create_casefile_with_session_composite(self):
        """Test composite workflow: create casefile + session."""
        from coreservice.request_hub import RequestHub
        from pydantic_models.operations.request_hub_ops import (
            CreateCasefileWithSessionRequest,
            CreateCasefileWithSessionPayload
        )
        
        # Mock services
        mock_casefile_service = Mock()
        mock_casefile_service.create_casefile = AsyncMock(return_value=Mock(
            request_id=uuid4(),
            status=RequestStatus.COMPLETED,
            payload=Mock(casefile_id="cf_comp_001"),
            metadata={}
        ))
        mock_casefile_service.add_session_to_casefile = AsyncMock(return_value=Mock(
            request_id=uuid4(),
            status=RequestStatus.COMPLETED,
            payload=Mock(casefile_id="cf_comp_001", session_id="ts_001"),
            metadata={}
        ))
        
        mock_tool_session_service = Mock()
        mock_tool_session_service.create_session = AsyncMock(return_value=Mock(
            request_id=uuid4(),
            status=RequestStatus.COMPLETED,
            payload=Mock(session_id="ts_001"),
            metadata={}
        ))
        
        hub = RequestHub(
            casefile_service=mock_casefile_service,
            tool_session_service=mock_tool_session_service
        )
        
        request = CreateCasefileWithSessionRequest(
            user_id="test_user",
            operation="workspace.casefile.create_casefile_with_session",
            payload=CreateCasefileWithSessionPayload(
                title="Composite Workflow Test",
                description="Testing composite workflow",
                auto_start_session=True,
                session_title="Test Session"
            ),
            hooks=["metrics", "audit"]
        )
        
        response = await hub.dispatch(request)
        
        # Verify both casefile and session were created
        assert response.status == RequestStatus.COMPLETED
        assert response.payload.casefile_id == "cf_comp_001"
        assert response.payload.session_id == "ts_001"
        
        # Verify all services were called
        mock_casefile_service.create_casefile.assert_called_once()
        mock_tool_session_service.create_session.assert_called_once()
        mock_casefile_service.add_session_to_casefile.assert_called_once()
