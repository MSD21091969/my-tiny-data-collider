"""
Integration Test Configuration and Fixtures

Provides service mocks and test utilities for MVP integration tests.
"""

import pytest
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import jwt

# Move imports inside functions to avoid circular imports
# from src.authservice.token import SECRET_KEY, ALGORITHM


@pytest.fixture(scope="session", autouse=True)
def initialize_tool_registry():
    """Initialize the tool registry for integration tests."""
    import os
    # Set environment variable to skip auto-initialization
    os.environ["SKIP_AUTO_INIT"] = "true"
    # Skip tool validation for MVP tests (using mock tool names)
    os.environ["SKIP_TOOL_VALIDATION"] = "true"
    
    try:
        from src.pydantic_ai_integration import initialize_registries
        result = initialize_registries()
        if not result:
            pytest.fail("Tool registry initialization failed")
    except Exception as e:
        pytest.fail(f"Tool registry initialization failed: {e}")


@pytest.fixture
def mock_casefile_service():
    """Mock CasefileService for integration testing."""
    service = AsyncMock()

    # Mock create_casefile
    async def mock_create_casefile(request):
        from src.pydantic_models.canonical.casefile import CasefileModel, CasefileMetadata
        from src.pydantic_models.operations.casefile_ops import CreateCasefileResponse, CasefileCreatedPayload
        from src.pydantic_models.base.types import RequestStatus

        # Create proper metadata
        metadata = CasefileMetadata(
            title=request.payload.title,
            description=request.payload.description or "",
            tags=request.payload.tags or [],
            created_by=request.user_id
        )

        # Create casefile with required data source (minimal gmail_data)
        casefile = CasefileModel(
            id=request.metadata.get("casefile_id", f"cf_241013_{uuid4().hex[:6]}"),
            metadata=metadata,
            gmail_data={"messages": [], "sync_status": "completed"}  # Minimal data source
        )

        # Create proper response payload
        payload = CasefileCreatedPayload(
            casefile_id=casefile.id,
            title=casefile.metadata.title,
            created_at=casefile.metadata.created_at,
            created_by=casefile.metadata.created_by
        )

        return CreateCasefileResponse(
            request_id=request.request_id,
            status=RequestStatus.COMPLETED,
            payload=payload,
            metadata={"operation": request.operation}
        )

    service.create_casefile = mock_create_casefile

    # Mock get_casefile
    async def mock_get_casefile(request):
        from src.pydantic_models.canonical.casefile import CasefileModel, CasefileMetadata
        from src.pydantic_models.operations.casefile_ops import GetCasefileResponse, CasefileDataPayload
        from src.pydantic_models.base.types import RequestStatus

        # Create proper metadata
        metadata = CasefileMetadata(
            title="Test Casefile",
            description="Test description",
            tags=["test"],
            created_by=request.user_id
        )

        # Create casefile with required data source
        casefile = CasefileModel(
            id=request.payload.casefile_id,
            metadata=metadata,
            gmail_data={"messages": [], "sync_status": "completed"}
        )

        # Create proper response payload
        payload = CasefileDataPayload(casefile=casefile)

        return GetCasefileResponse(
            request_id=request.request_id,
            status=RequestStatus.COMPLETED,
            payload=payload,
            metadata={"operation": request.operation}
        )

    service.get_casefile = mock_get_casefile

    return service


@pytest.fixture
def mock_tool_session_service():
    """Mock ToolSessionService for integration testing."""
    service = AsyncMock()

    # Mock create_session
    async def mock_create_session(request):
        from src.pydantic_models.operations.tool_session_ops import CreateSessionResponse, SessionCreatedPayload
        from src.pydantic_models.base.types import RequestStatus

        payload = SessionCreatedPayload(
            session_id=f"ts_241013_{uuid4().hex[:6]}",
            casefile_id=getattr(request.payload, "casefile_id", None),
            created_at="2025-10-14T13:00:00+00:00",
        )

        return CreateSessionResponse(
            request_id=request.request_id,
            status=RequestStatus.COMPLETED,
            payload=payload,
            metadata={"operation": request.operation}
        )

    service.create_session = mock_create_session

    # Mock get_session
    async def mock_get_session(request):
        from src.pydantic_models.canonical.tool_session import ToolSession
        from src.pydantic_models.operations.tool_session_ops import GetSessionResponse
        from src.pydantic_models.base.types import RequestStatus

        session = ToolSession(
            session_id=request.payload.session_id,
            user_id=request.user_id,
            casefile_id=request.metadata.get("casefile_id"),
            title="Test Session",
            status="active",
            created_at="2025-10-14T13:00:00Z",
            updated_at="2025-10-14T13:00:00Z",
        )

        return GetSessionResponse(
            request_id=request.request_id,
            status=RequestStatus.COMPLETED,
            payload=session,
            metadata={"operation": request.operation}
        )

    service.get_session = mock_get_session

    # Mock process_tool_request
    async def mock_process_tool_request(request, auth_context=None):
        from src.pydantic_models.operations.tool_execution_ops import ToolResponse
        from src.pydantic_models.base.types import RequestStatus

        return ToolResponse(
            request_id=request.request_id,
            status=RequestStatus.COMPLETED,
            payload={
                "result": {
                    "status": "completed",
                    "tool_name": request.payload.tool_name,
                    "parameters": request.payload.parameters or {},
                    "execution_time_ms": 150,
                }
            },
            metadata={"operation": request.operation}
        )

    service.process_tool_request = mock_process_tool_request

    # Mock close_session
    async def mock_close_session(request):
        from src.pydantic_models.canonical.tool_session import ToolSession
        from src.pydantic_models.operations.tool_session_ops import CloseSessionResponse
        from src.pydantic_models.base.types import RequestStatus

        session = ToolSession(
            session_id=request.payload.session_id,
            user_id=request.user_id,
            casefile_id=request.metadata.get("casefile_id"),
            title="Test Session",
            status="closed",
            created_at="2025-10-14T13:00:00Z",
            updated_at="2025-10-14T13:00:00Z",
            closed_at="2025-10-14T13:05:00Z",
        )

        return CloseSessionResponse(
            request_id=request.request_id,
            status=RequestStatus.COMPLETED,
            payload=session,
            metadata={"operation": request.operation}
        )

    service.close_session = mock_close_session

    return service


@pytest.fixture
def mock_request_hub(mock_casefile_service, mock_tool_session_service):
    """Mock RequestHub with service dependencies."""
    from src.coreservice.request_hub import RequestHub
    from src.coreservice.service_container import ServiceManager

    # Create mock service manager
    service_manager = MagicMock()
    service_manager.casefile_service = mock_casefile_service
    service_manager.tool_session_service = mock_tool_session_service

    # Create RequestHub with mocked services
    hub = RequestHub(service_manager=service_manager)

    return hub


@pytest.fixture
def sample_auth_context():
    """Sample auth context for testing."""
    return {
        "user_id": "test_user_123",
        "username": "test_user",
        "casefile_id": f"casefile_{uuid4()}",
        "session_id": f"session_{uuid4()}",
        "session_request_id": f"req_{uuid4()}",
        "permissions": ["casefiles:read", "casefiles:write", "tools:execute"],
    }


@pytest.fixture
def integration_test_ids():
    """Generate consistent IDs for integration tests."""
    return {
        "user_id": "test_user_123",
        "username": "test_user",
        "casefile_id": f"cf_241013_{uuid4().hex[:6]}",
        "session_id": f"session_{uuid4()}",
        "session_request_id": f"req_{uuid4()}",
    }


def decode_test_token(token: str) -> dict:
    """
    Decode a JWT token for testing without FastAPI dependency injection.

    This bypasses the HTTPAuthorizationCredentials wrapper that get_current_user expects.
    """
    from src.authservice.token import SECRET_KEY, ALGORITHM
    decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    return decoded
