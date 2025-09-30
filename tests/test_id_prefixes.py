import pytest

from src.casefileservice.service import CasefileService
from src.communicationservice.service import CommunicationService
from src.coreservice.id_service import get_id_service
from src.pydantic_models.communication.models import ChatMessagePayload, ChatRequest, MessageType
from src.pydantic_models.tool_session.models import ToolRequest, ToolRequestPayload
from src.tool_sessionservice.service import ToolSessionService


@pytest.fixture(autouse=True)
def use_mocks(monkeypatch: pytest.MonkeyPatch) -> None:
    """Force services to use mock persistence for determinism."""
    monkeypatch.setenv("USE_MOCKS", "true")


@pytest.mark.asyncio
async def test_casefile_and_session_id_prefixes() -> None:
    service = CasefileService(use_mocks=True)

    result = await service.create_casefile(
        user_id="user_123",
        title="Prefix Tracking",
        description="Ensure generated IDs have expected prefixes",
    )

    casefile_id = result["casefile_id"]
    assert casefile_id.startswith("cf_"), casefile_id

    stored = await service.repository.get_casefile(casefile_id)
    assert stored is not None
    assert stored.id == casefile_id

    tool_service = ToolSessionService(use_mocks=True)
    session_info = await tool_service.create_session("user_123", casefile_id)
    tool_session_id = session_info["session_id"]
    assert tool_session_id.startswith("ts_"), tool_session_id

    await service.add_session_to_casefile(casefile_id, tool_session_id)
    updated = await service.repository.get_casefile(casefile_id)
    assert updated is not None
    assert tool_session_id in updated.sessions
    assert all(session.startswith("ts_") for session in updated.sessions)


@pytest.mark.asyncio
async def test_tool_session_request_and_event_prefixes() -> None:
    tool_service = ToolSessionService(use_mocks=True)

    casefile_id = get_id_service().new_casefile_id()
    session_info = await tool_service.create_session("agent@example.com", casefile_id)
    session_id = session_info["session_id"]
    assert session_id.startswith("ts_"), session_id

    request = ToolRequest(
        session_id=session_id,
        user_id="agent@example.com",
        operation="tool_execution",
        payload=ToolRequestPayload(
            tool_name="example_tool",
            parameters={"value": 3},
            casefile_id=casefile_id,
        ),
    )

    response = await tool_service.process_tool_request(request)
    assert response.payload.session_request_id.startswith("sr_")
    assert all(event["event_id"].startswith("te_") for event in response.payload.events)

    stored_session = await tool_service.repository.get_session(session_id)
    assert stored_session is not None
    assert all(key.startswith("sr_") for key in stored_session.requests.keys())
    assert all(key.startswith("sr_") for key in stored_session.responses.keys())
    assert all(event["session_request_id"].startswith("sr_") for event in stored_session.events)


@pytest.mark.asyncio
async def test_chat_session_and_events_use_prefixed_ids() -> None:
    comm_service = CommunicationService(use_mocks=True)

    casefile_id = get_id_service().new_casefile_id()
    session_info = await comm_service.create_session("analyst", casefile_id)
    chat_session_id = session_info["session_id"]
    tool_session_id = session_info["tool_session_id"]

    assert chat_session_id.startswith("cs_"), chat_session_id
    assert tool_session_id.startswith("ts_"), tool_session_id

    payload = ChatMessagePayload(
        content="Please run the example tool",
        message_type=MessageType.USER,
        tool_calls=[{"name": "example_tool", "arguments": {"value": 7}}],
        casefile_id=casefile_id,
    )

    chat_request = ChatRequest(
        session_id=chat_session_id,
        user_id="analyst",
        payload=payload,
    )

    response = await comm_service.process_chat_request(chat_request)
    assert response.session_request_id is not None
    assert response.session_request_id.startswith("sr_")
    assert all(event["event_id"].startswith("te_") for event in response.payload.events)

    stored_chat = await comm_service.repository.get_session(chat_session_id)
    assert stored_chat is not None
    assert stored_chat.metadata.get("tool_session_id", "").startswith("ts_")
    assert all(key.startswith("sr_") for key in stored_chat.request_index.keys())
    assert all(message["request_id"].startswith("sr_") for message in stored_chat.messages)
    assert all(event["session_request_id"].startswith("sr_") for event in stored_chat.events)
