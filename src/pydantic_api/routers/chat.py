"""
Router for chat API endpoints.
"""

from typing import Any

from fastapi import APIRouter, Depends, HTTPException

from src.authservice import get_current_user
from src.communicationservice.service import CommunicationService
from src.coreservice.request_hub import RequestHub
from src.pydantic_models.base.envelopes import RequestEnvelope
from src.pydantic_models.operations.chat_session_ops import (
    CloseChatSessionRequest,
    CloseChatSessionResponse,
    CreateChatSessionRequest,
    CreateChatSessionResponse,
    GetChatSessionRequest,
    GetChatSessionResponse,
    ListChatSessionsRequest,
    ListChatSessionsResponse,
)

from ..dependencies import get_request_hub

router = APIRouter(prefix="/api/chat", tags=["chat"])

router = APIRouter(prefix="/api/chat", tags=["chat"])


async def get_communication_service():
    """Dependency to get the communication service."""
    return CommunicationService()


@router.post("/sessions", response_model=CreateChatSessionResponse)
async def create_session(
    request: RequestEnvelope,
    hub: RequestHub = Depends(get_request_hub),
    current_user: dict[str, Any] = Depends(get_current_user),
) -> CreateChatSessionResponse:
    """Create a new chat session."""

    # Extract user_id from JWT (trusted source)
    user_id = current_user["user_id"]

    # Extract casefile_id from request
    casefile_id = request.request.get("casefile_id")

    # Create session request with JWT-validated user_id
    create_request = CreateChatSessionRequest(
        user_id=user_id,
        operation="create_chat_session",
        payload={"casefile_id": casefile_id},
        hooks=["metrics", "audit"],
        context_requirements=["session"],
    )

    response = await hub.dispatch(create_request)

    # Add trace_id to metadata if needed
    if response.metadata:
        response.metadata["trace_id"] = request.trace_id
    else:
        response.metadata = {"trace_id": request.trace_id}

    return response


@router.post("/sessions/{session_id}/messages")
async def send_message(
    session_id: str,
    request: RequestEnvelope,
    service: CommunicationService = Depends(get_communication_service),
    current_user: dict[str, Any] = Depends(get_current_user),
):
    """Send a message in a chat session."""

    # Extract user_id from JWT
    user_id = current_user["user_id"]

    # Verify session ownership before processing message
    get_request = GetChatSessionRequest(
        user_id=user_id,
        operation="get_chat_session",
        payload={"session_id": session_id, "include_messages": False},
    )

    get_response = await service.get_session(get_request)

    if get_response.status.value == "failed":
        raise HTTPException(status_code=404, detail=get_response.error or "Session not found")

    # Verify ownership
    if get_response.payload.user_id != user_id:
        raise HTTPException(status_code=403, detail="You do not have access to this session")

    # Extract request data and create ChatRequest
    message_data = request.request
    message_data["session_id"] = session_id

    from pydantic_models.canonical.chat_session import MessageType
    from pydantic_models.operations.tool_execution_ops import ChatMessagePayload, ChatRequest

    try:
        # Construct the chat request
        # The user message comes in the request payload
        content = message_data.get("content", "")
        message_type = message_data.get("message_type", MessageType.USER)
        tool_calls = message_data.get("tool_calls", [])
        session_request_id = message_data.get("session_request_id")
        casefile_id = message_data.get("casefile_id")

        # Create the message payload
        chat_payload = ChatMessagePayload(
            content=content,
            message_type=message_type,
            tool_calls=tool_calls,
            session_request_id=session_request_id,
            casefile_id=casefile_id,
        )

        # Create the request with JWT-validated user_id
        chat_request = ChatRequest(
            session_id=session_id, user_id=user_id, operation="chat_message", payload=chat_payload
        )

        # Process the request
        response = await service.process_chat_request(chat_request)

        # Merge trace_id into response
        result = response.model_dump()
        result["trace_id"] = request.trace_id

        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing message: {str(e)}")


@router.get("/sessions/{session_id}", response_model=GetChatSessionResponse)
async def get_session(
    session_id: str,
    include_messages: bool = True,
    hub: RequestHub = Depends(get_request_hub),
    current_user: dict[str, Any] = Depends(get_current_user),
) -> GetChatSessionResponse:
    """Get a chat session."""

    # Extract user_id from JWT
    user_id = current_user["user_id"]

    # Create request with JWT-validated user_id
    get_request = GetChatSessionRequest(
        user_id=user_id,
        operation="get_chat_session",
        payload={"session_id": session_id, "include_messages": include_messages},
        hooks=["metrics", "audit"],
        context_requirements=["session"],
    )

    response = await hub.dispatch(get_request)

    if response.status.value == "failed":
        raise HTTPException(status_code=404, detail=response.error or "Session not found")

    return response


@router.get("/sessions", response_model=ListChatSessionsResponse)
async def list_sessions(
    casefile_id: str | None = None,
    active_only: bool = True,
    limit: int = 50,
    offset: int = 0,
    hub: RequestHub = Depends(get_request_hub),
    current_user: dict[str, Any] = Depends(get_current_user),
) -> ListChatSessionsResponse:
    """List chat sessions for the authenticated user."""

    # Extract user_id from JWT
    user_id = current_user["user_id"]

    # Create request - filter by authenticated user
    list_request = ListChatSessionsRequest(
        user_id=user_id,
        operation="list_chat_sessions",
        payload={
            "user_id": user_id,  # Only list sessions for this user
            "casefile_id": casefile_id,
            "active_only": active_only,
            "limit": limit,
            "offset": offset,
        },
        hooks=["metrics", "audit"],
        context_requirements=["session"],
    )

    return await hub.dispatch(list_request)


@router.post("/sessions/{session_id}/close", response_model=CloseChatSessionResponse)
async def close_session(
    session_id: str,
    hub: RequestHub = Depends(get_request_hub),
    current_user: dict[str, Any] = Depends(get_current_user),
) -> CloseChatSessionResponse:
    """Close a chat session."""

    # Extract user_id from JWT
    user_id = current_user["user_id"]

    # First verify session belongs to this user via RequestHub
    get_request = GetChatSessionRequest(
        user_id=user_id,
        operation="get_chat_session",
        payload={"session_id": session_id, "include_messages": False},
        hooks=["metrics", "audit"],
        context_requirements=["session"],
    )

    get_response = await hub.dispatch(get_request)

    if get_response.status.value == "failed":
        raise HTTPException(status_code=404, detail=get_response.error or "Session not found")

    if get_response.payload.user_id != user_id:
        raise HTTPException(status_code=403, detail="You do not have access to this session")

    # Now close the session via RequestHub
    close_request = CloseChatSessionRequest(
        user_id=user_id,
        operation="close_chat_session",
        payload={"session_id": session_id},
        hooks=["metrics", "audit"],
        context_requirements=["session"],
    )

    response = await hub.dispatch(close_request)

    if response.status.value == "failed":
        raise HTTPException(status_code=500, detail=response.error or "Failed to close session")

    return response
