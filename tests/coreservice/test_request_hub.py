from datetime import datetime
from typing import Dict, Optional
from uuid import uuid4

import pytest

from coreservice.policy_patterns import PolicyPatternLoader
from coreservice.request_hub import RequestHub
from pydantic_models.base.types import RequestStatus
from pydantic_models.operations.casefile_ops import (
    AddSessionToCasefileRequest,
    AddSessionToCasefileResponse,
    CasefileCreatedPayload,
    CreateCasefilePayload,
    CreateCasefileRequest,
    CreateCasefileResponse,
    SessionAddedPayload,
)
from pydantic_models.operations.request_hub_ops import (
    CreateCasefileWithSessionPayload,
    CreateCasefileWithSessionRequest,
    CreateCasefileWithSessionResponse,
)
from pydantic_models.operations.tool_session_ops import (
    CreateSessionPayload,
    CreateSessionRequest,
    CreateSessionResponse,
    SessionCreatedPayload,
)


class _FakeCasefileRecord:
    def __init__(self, casefile_id: str, title: str, description: str, tags: Optional[list[str]] = None) -> None:
        self.casefile_id = casefile_id
        self.title = title
        self.description = description
        self.tags = tags or []
        self.session_ids: list[str] = []

    def model_dump(self) -> Dict[str, object]:
        return {
            "casefile_id": self.casefile_id,
            "title": self.title,
            "description": self.description,
            "tags": list(self.tags),
            "session_ids": list(self.session_ids),
        }


class _FakeCasefileRepository:
    def __init__(self) -> None:
        self._store: Dict[str, _FakeCasefileRecord] = {}

    async def get_casefile(self, casefile_id: str) -> Optional[_FakeCasefileRecord]:
        return self._store.get(casefile_id)

    def save(self, record: _FakeCasefileRecord) -> None:
        self._store[record.casefile_id] = record


class _FakeCasefileService:
    def __init__(self) -> None:
        self.repository = _FakeCasefileRepository()
        self.created_requests: list[CreateCasefileRequest] = []
        self.linked_sessions: list[tuple[str, str]] = []

    async def create_casefile(self, request: CreateCasefileRequest) -> CreateCasefileResponse:
        self.created_requests.append(request)
        casefile_id = f"cf_{len(self.created_requests):03d}"
        payload = CasefileCreatedPayload(
            casefile_id=casefile_id,
            title=request.payload.title,
            created_at=datetime.now().isoformat(),
            created_by=request.user_id,
        )
        record = _FakeCasefileRecord(
            casefile_id=casefile_id,
            title=request.payload.title,
            description=request.payload.description,
            tags=request.payload.tags,
        )
        self.repository.save(record)
        return CreateCasefileResponse(
            request_id=request.request_id,
            status=RequestStatus.COMPLETED,
            payload=payload,
            metadata={"operation": request.operation},
        )

    async def add_session_to_casefile(self, request: AddSessionToCasefileRequest) -> AddSessionToCasefileResponse:
        self.linked_sessions.append((request.payload.casefile_id, request.payload.session_id))
        record = self.repository._store.setdefault(
            request.payload.casefile_id,
            _FakeCasefileRecord(request.payload.casefile_id, title="", description=""),
        )
        record.session_ids.append(request.payload.session_id)
        response_payload = SessionAddedPayload(
            casefile_id=request.payload.casefile_id,
            session_id=request.payload.session_id,
            session_type=request.payload.session_type,
            total_sessions=len(record.session_ids),
        )
        return AddSessionToCasefileResponse(
            request_id=request.request_id,
            status=RequestStatus.COMPLETED,
            payload=response_payload,
            metadata={"operation": request.operation},
        )


class _FakeSessionRecord:
    def __init__(self, session_id: str, user_id: str, casefile_id: Optional[str] = None, title: Optional[str] = None) -> None:
        self.session_id = session_id
        self.user_id = user_id
        self.casefile_id = casefile_id
        self.title = title
        self.created_at = datetime.now().isoformat()
        self.updated_at = self.created_at

    def model_dump(self) -> Dict[str, object]:
        return {
            "session_id": self.session_id,
            "user_id": self.user_id,
            "casefile_id": self.casefile_id,
            "title": self.title,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }


class _FakeToolSessionRepository:
    def __init__(self) -> None:
        self._store: Dict[str, _FakeSessionRecord] = {}

    async def get_session(self, session_id: str) -> Optional[_FakeSessionRecord]:
        return self._store.get(session_id)

    def save(self, record: _FakeSessionRecord) -> None:
        self._store[record.session_id] = record


class _FakeToolSessionService:
    def __init__(self) -> None:
        self.repository = _FakeToolSessionRepository()
        self.created_requests: list[CreateSessionRequest] = []

    async def create_session(self, request: CreateSessionRequest) -> CreateSessionResponse:
        self.created_requests.append(request)
        session_id = f"ts_{len(self.created_requests):03d}"
        record = _FakeSessionRecord(
            session_id=session_id,
            user_id=request.user_id,
            casefile_id=request.payload.casefile_id,
            title=request.payload.title,
        )
        self.repository.save(record)
        payload = SessionCreatedPayload(
            session_id=session_id,
            casefile_id=request.payload.casefile_id,
            created_at=record.created_at,
        )
        return CreateSessionResponse(
            request_id=request.request_id,
            status=RequestStatus.COMPLETED,
            payload=payload,
            metadata={"operation": request.operation},
        )


@pytest.mark.asyncio
async def test_request_hub_executes_casefile_workflow_with_hooks() -> None:
    casefile_service = _FakeCasefileService()
    tool_session_service = _FakeToolSessionService()
    tool_session_service.repository.save(_FakeSessionRecord("ts_existing", user_id="user-1"))

    hub = RequestHub(
        casefile_service=casefile_service,
        tool_session_service=tool_session_service,
        policy_loader=PolicyPatternLoader(),
    )

    request = CreateCasefileRequest(
        request_id=uuid4(),
        session_id="ts_existing",
        user_id="user-1",
        operation="create_casefile",
        hooks=["metrics", "audit"],
        context_requirements=["session"],
        payload=CreateCasefilePayload(title="RHub", description="demo", tags=["hub"]),
        metadata={"client": "unit-test"},
    )

    response = await hub.dispatch(request)

    assert response.status is RequestStatus.COMPLETED
    assert response.payload.casefile_id.startswith("cf_")
    assert "hook_events" in response.metadata
    stages = {event["stage"] for event in response.metadata["hook_events"]}
    assert stages == {"pre", "post"}


@pytest.mark.asyncio
async def test_request_hub_composite_creates_casefile_and_session() -> None:
    casefile_service = _FakeCasefileService()
    tool_session_service = _FakeToolSessionService()
    tool_session_service.repository.save(_FakeSessionRecord("ts_parent", user_id="user-2"))

    hub = RequestHub(
        casefile_service=casefile_service,
        tool_session_service=tool_session_service,
        policy_loader=PolicyPatternLoader(),
    )

    payload = CreateCasefileWithSessionPayload(
        title="Composite",
        description="demo",
        tags=["workflow"],
        auto_start_session=True,
        session_title="Workflow Session",
        hook_channels=["metrics", "audit"],
    )

    request = CreateCasefileWithSessionRequest(
        request_id=uuid4(),
        session_id="ts_parent",
        user_id="user-2",
        hooks=["metrics"],
        context_requirements=["session", "casefile"],
        policy_hints={"pattern": "tool_session_observer"},
        payload=payload,
        metadata={"client": "unit-test"},
    )

    response = await hub.dispatch(request)

    assert isinstance(response, CreateCasefileWithSessionResponse)
    assert response.status is RequestStatus.COMPLETED
    assert response.payload.casefile_id.startswith("cf_")
    assert response.payload.session_id is not None
    assert casefile_service.linked_sessions == [(response.payload.casefile_id, response.payload.session_id)]
    assert response.metadata.get("hook_events")
    # Ensure casefile context was populated with linked session data
    stored_casefile = await casefile_service.repository.get_casefile(response.payload.casefile_id)
    assert stored_casefile is not None
    assert response.payload.session_id in stored_casefile.session_ids
