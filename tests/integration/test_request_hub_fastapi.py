"""Integration tests for RequestHub dispatch workflows.

These tests exercise RequestHub with stubbed service implementations to
ensure high-level orchestration behaves as expected for tool execution and
chat processing operations.
"""

from __future__ import annotations

from typing import Any
from uuid import uuid4

import pytest

from coreservice.policy_patterns import PolicyPatternLoader
from coreservice.request_hub import RequestHub
from pydantic_ai_integration.tool_decorator import MANAGED_TOOLS
from pydantic_ai_integration.tool_definition import ManagedToolDefinition
from pydantic_models.base.types import RequestStatus
from pydantic_models.canonical.chat_session import MessageType
from pydantic_models.operations.casefile_ops import CasefileCreatedPayload
from pydantic_models.operations.tool_execution_ops import (
    ChatMessagePayload,
    ChatRequest,
    ChatRequestPayload,
    ChatResponse,
    ChatResultPayload,
    ToolRequest,
    ToolRequestPayload,
    ToolResponse,
    ToolResponsePayload,
)


class _StubSessionRecord:
    """Minimal session record to satisfy RequestHub context loading."""

    def __init__(self, session_id: str, user_id: str, casefile_id: str | None = None) -> None:
        self.session_id = session_id
        self.user_id = user_id
        self.casefile_id = casefile_id
        self.active = True

    def model_dump(self) -> dict[str, Any]:
        return {
            "session_id": self.session_id,
            "user_id": self.user_id,
            "casefile_id": self.casefile_id,
            "active": self.active,
        }


class _StubToolSessionRepository:
    """Stub repository exposing only the operations RequestHub relies on."""

    def __init__(self, session: _StubSessionRecord) -> None:
        self._session = session
        self.update_activity_calls: list[str] = []

    async def get_session(self, session_id: str) -> _StubSessionRecord | None:
        return self._session if session_id == self._session.session_id else None

    async def update_activity(self, session_id: str) -> None:
        self.update_activity_calls.append(session_id)


class _StubToolSessionService:
    """Stub tool session service that records processed tool requests."""

    def __init__(self, repository: _StubToolSessionRepository) -> None:
        self.repository = repository
        self.processed_requests: list[ToolRequest] = []

    async def process_tool_request(self, request: ToolRequest) -> ToolResponse:
        self.processed_requests.append(request)
        return ToolResponse(
            request_id=request.request_id,
            status=RequestStatus.COMPLETED,
            payload=ToolResponsePayload(
                result={"echo": request.payload.parameters},
                events=[{"event": "completed"}],
                session_request_id=request.payload.session_request_id,
            ),
            metadata={"operation": request.operation},
        )

    async def create_session(
        self, request: Any
    ) -> Any:  # pragma: no cover - unused helper for tests
        return None


class _StubCommunicationService:
    """Stub communication service capturing chat requests."""

    def __init__(self) -> None:
        self.processed_requests: list[ChatRequest] = []

    async def process_chat_request(self, request: ChatRequest) -> ChatResponse:
        self.processed_requests.append(request)
        payload = ChatResultPayload(
            message=ChatMessagePayload(
                content="ack",
                message_type=MessageType.ASSISTANT,
                tool_calls=[],
                session_request_id=request.payload.session_request_id,
                casefile_id=request.payload.casefile_id,
            ),
            related_messages=[],
            events=[{"event": "chat_processed"}],
        )
        return ChatResponse(
            request_id=request.request_id,
            status=RequestStatus.COMPLETED,
            payload=payload,
            metadata={"operation": request.operation},
        )


class _StubCasefileRepository:
    async def get_casefile(self, casefile_id: str) -> None:  # pragma: no cover - unused helper
        return None


class _StubCasefileService:
    def __init__(self) -> None:
        self.repository = _StubCasefileRepository()

    async def create_casefile(self, request: Any) -> Any:  # pragma: no cover - unused helper
        return CasefileCreatedPayload(
            casefile_id="cf_stub", title="stub", created_at="", created_by="tester"
        )


@pytest.fixture(autouse=True)
def _register_demo_tool() -> Any:
    demo_tool = ManagedToolDefinition(
        name="demo_tool",
        description="Stub tool for RequestHub integration tests",
        category="test",
        tags=[],
    )
    MANAGED_TOOLS["demo_tool"] = demo_tool
    try:
        yield
    finally:
        MANAGED_TOOLS.pop("demo_tool", None)


@pytest.mark.asyncio
async def test_dispatch_handles_tool_execution_with_hooks() -> None:
    session = _StubSessionRecord(session_id="ts_001", user_id="user-123", casefile_id="cf_123")
    repository = _StubToolSessionRepository(session)
    tool_service = _StubToolSessionService(repository)
    communication_service = _StubCommunicationService()

    hub = RequestHub(
        casefile_service=_StubCasefileService(),
        tool_session_service=tool_service,
        communication_service=communication_service,
        policy_loader=PolicyPatternLoader(),
    )

    request = ToolRequest(
        request_id=uuid4(),
        session_id=session.session_id,
        user_id=session.user_id,
        operation="tool_execution",
        payload=ToolRequestPayload(
            tool_name="demo_tool",
            parameters={"alpha": 1},
            casefile_id=session.casefile_id,
            session_request_id="req-001",
        ),
        hooks=["metrics", "audit", "session_lifecycle"],
        context_requirements=["session"],
        metadata={"client": "integration-test"},
    )

    response = await hub.dispatch(request)

    assert response.status is RequestStatus.COMPLETED
    assert tool_service.processed_requests[0].payload.parameters == {"alpha": 1}
    assert repository.update_activity_calls == [session.session_id]
    assert response.metadata.get("hook_events"), "expected hook events to be attached"
    assert any(event["hook"] == "metrics" for event in response.metadata["hook_events"])


@pytest.mark.asyncio
async def test_dispatch_handles_chat_processing_with_hooks() -> None:
    session = _StubSessionRecord(session_id="ts_002", user_id="user-456", casefile_id=None)
    repository = _StubToolSessionRepository(session)
    tool_service = _StubToolSessionService(repository)
    communication_service = _StubCommunicationService()

    hub = RequestHub(
        casefile_service=_StubCasefileService(),
        tool_session_service=tool_service,
        communication_service=communication_service,
        policy_loader=PolicyPatternLoader(),
    )

    request = ChatRequest(
        request_id=uuid4(),
        session_id="chat-001",
        user_id="user-456",
        operation="chat",
        payload=ChatRequestPayload(
            message="Hello there",
            session_id="chat-001",
            casefile_id=None,
            session_request_id="req-002",
        ),
        hooks=["metrics", "audit"],
        context_requirements=["session"],
        metadata={},
    )

    response = await hub.dispatch(request)

    assert response.status is RequestStatus.COMPLETED
    assert communication_service.processed_requests[0].payload.message == "Hello there"
    assert response.metadata.get("hook_events"), "expected hook events to be attached"
    assert any(event["hook"] == "audit" for event in response.metadata["hook_events"])
    # Tool session lifecycle hook should not update activity when session_id does not map to a tool session
    assert repository.update_activity_calls == []
