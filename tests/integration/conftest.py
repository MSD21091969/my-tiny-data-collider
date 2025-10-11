"""
Integration Test Configuration and Fixtures

Provides service mocks and test utilities for MVP integration tests.
"""

import pytest
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import jwt

from src.authservice.token import SECRET_KEY, ALGORITHM


@pytest.fixture
def mock_casefile_service():
    """Mock CasefileService for integration testing."""
    service = AsyncMock()

    # Mock create_casefile
    async def mock_create_casefile(request):
        from src.pydantic_models.canonical.casefile import CasefileModel
        from src.pydantic_models.operations.casefile_ops import CreateCasefileResponse

        casefile = CasefileModel(
            casefile_id=request.metadata.get("casefile_id", f"casefile_{uuid4()}"),
            user_id=request.user_id,
            title=request.payload.title,
            description=request.payload.description or "",
            tags=request.payload.tags or [],
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

        return CreateCasefileResponse(
            request_id=request.request_id,
            success=True,
            message="Casefile created successfully",
            payload=casefile,
        )

    service.create_casefile = mock_create_casefile

    # Mock get_casefile
    async def mock_get_casefile(request):
        from src.pydantic_models.canonical.casefile import CasefileModel
        from src.pydantic_models.operations.casefile_ops import GetCasefileResponse

        casefile = CasefileModel(
            casefile_id=request.payload.casefile_id,
            user_id=request.user_id,
            title="Test Casefile",
            description="Test description",
            tags=["test"],
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

        return GetCasefileResponse(
            request_id=request.request_id,
            success=True,
            message="Casefile retrieved successfully",
            payload=casefile,
        )

    service.get_casefile = mock_get_casefile

    return service


@pytest.fixture
def mock_tool_session_service():
    """Mock ToolSessionService for integration testing."""
    service = AsyncMock()

    # Mock create_session
    async def mock_create_session(request):
        from src.pydantic_models.canonical.tool_session import ToolSession
        from src.pydantic_models.operations.tool_session_ops import CreateSessionResponse

        session = ToolSession(
            session_id=f"session_{uuid4()}",
            user_id=request.user_id,
            casefile_id=getattr(request.payload, "casefile_id", None),
            title=getattr(request.payload, "title", "Test Session"),
            status="active",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

        return CreateSessionResponse(
            request_id=request.request_id,
            success=True,
            message="Session created successfully",
            payload=session,
        )

    service.create_session = mock_create_session

    # Mock get_session
    async def mock_get_session(request):
        from src.pydantic_models.canonical.tool_session import ToolSession
        from src.pydantic_models.operations.tool_session_ops import GetSessionResponse

        session = ToolSession(
            session_id=request.payload.session_id,
            user_id=request.user_id,
            casefile_id=request.metadata.get("casefile_id"),
            title="Test Session",
            status="active",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

        return GetSessionResponse(
            request_id=request.request_id,
            success=True,
            message="Session retrieved successfully",
            payload=session,
        )

    service.get_session = mock_get_session

    # Mock process_tool_request
    async def mock_process_tool_request(request, auth_context=None):
        from src.pydantic_models.operations.tool_execution_ops import ToolResponse

        return ToolResponse(
            request_id=request.request_id,
            success=True,
            message=f"Tool {request.payload.tool_name} executed successfully",
            payload={
                "result": "success",
                "tool_name": request.payload.tool_name,
                "parameters": request.payload.parameters or {},
                "execution_time_ms": 150,
            },
        )

    service.process_tool_request = mock_process_tool_request

    # Mock close_session
    async def mock_close_session(request):
        from src.pydantic_models.canonical.tool_session import ToolSession
        from src.pydantic_models.operations.tool_session_ops import CloseSessionResponse

        session = ToolSession(
            session_id=request.payload.session_id,
            user_id=request.user_id,
            casefile_id=request.metadata.get("casefile_id"),
            title="Test Session",
            status="closed",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            closed_at=datetime.utcnow(),
        )

        return CloseSessionResponse(
            request_id=request.request_id,
            success=True,
            message="Session closed successfully",
            payload=session,
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
        "casefile_id": f"casefile_{uuid4()}",
        "session_id": f"session_{uuid4()}",
        "session_request_id": f"req_{uuid4()}",
    }


def decode_test_token(token: str) -> dict:
    """
    Decode a JWT token for testing without FastAPI dependency injection.
    
    This bypasses the HTTPAuthorizationCredentials wrapper that get_current_user expects.
    """
    decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    return decoded
