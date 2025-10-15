"""Service for handling chat sessions and message processing."""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import uuid4

# TODO: Re-enable when agents module is implemented
# from pydantic_ai_integration.agents.base import import_tools
from coreservice.id_service import get_id_service
from pydantic_ai_integration.dependencies import MDSContext
from src.pydantic_models.base.types import RequestStatus
from src.pydantic_models.canonical.chat_session import ChatSession, MessageType
from src.pydantic_models.operations.chat_session_ops import (
    ChatSessionClosedPayload,
    ChatSessionCreatedPayload,
    ChatSessionDataPayload,
    ChatSessionListPayload,
    CloseChatSessionRequest,
    CloseChatSessionResponse,
    CreateChatSessionRequest,
    CreateChatSessionResponse,
    GetChatSessionRequest,
    GetChatSessionResponse,
    ListChatSessionsRequest,
    ListChatSessionsResponse,
)
from src.pydantic_models.operations.tool_execution_ops import (
    ChatMessagePayload,
    ChatRequest,
    ChatResponse,
    ChatResultPayload,
    ToolRequest,
    ToolRequestPayload,
)
from src.pydantic_models.operations.tool_session_ops import CreateSessionRequest
from src.pydantic_models.views.session_views import ChatSessionSummary
from tool_sessionservice.service import ToolSessionService

from .repository import ChatSessionRepository
from pydantic_ai_integration.method_decorator import register_service_method

# TODO: Re-enable when agents module is implemented
# import_tools()

logger = logging.getLogger(__name__)


class CommunicationService:
    """Service for handling chat sessions and message processing (Firestore only)."""

    def __init__(self, repository: ChatSessionRepository | None = None, tool_service: ToolSessionService | None = None, id_service=None) -> None:
        """Initialize the communication and tool session services."""
        self.repository = repository or ChatSessionRepository()
        self.tool_service = tool_service or ToolSessionService()
        self.id_service = id_service or get_id_service()

    @register_service_method(
        name="create_session",
        description="Create chat session with linked tool session",
        service_name="CommunicationService",
        service_module="src.communicationservice.service",
        classification={
            "domain": "communication",
            "subdomain": "chat_session",
            "capability": "create",
            "complexity": "composite",
            "maturity": "stable",
            "integration_tier": "internal"
        },
        required_permissions=["chat:create"],
        requires_casefile=False,
        enabled=True,
        requires_auth=True,
        timeout_seconds=30,
        version="1.0.0",
        dependencies=["ToolSessionService.create_session"]
    )
    async def create_session(self, request: CreateChatSessionRequest) -> CreateChatSessionResponse:
        """Create a new chat session and its linked tool session."""
        start_time = datetime.now()

        user_id = request.user_id
        casefile_id = request.payload.casefile_id

        session_id = self.id_service.new_chat_session_id(user_id=user_id, casefile_id=casefile_id)

        session = ChatSession(
            session_id=session_id,
            user_id=user_id,
            casefile_id=casefile_id,
        )
        await self.repository.create_session(session)

        # Create tool session using new Request/Response pattern
        tool_request = CreateSessionRequest(
            user_id=user_id, operation="create_tool_session", payload={"casefile_id": casefile_id}
        )
        tool_response = await self.tool_service.create_session(tool_request)
        tool_session_id = tool_response.payload.session_id

        session.metadata = session.metadata or {}
        session.metadata["tool_session_id"] = tool_session_id
        session.updated_at = datetime.now().isoformat()
        await self.repository.update_session(session)

        logger.info("Created chat session %s with tool session %s", session_id, tool_session_id)

        execution_time_ms = int((datetime.now() - start_time).total_seconds() * 1000)

        return CreateChatSessionResponse(
            request_id=request.request_id,
            status=RequestStatus.COMPLETED,
            payload=ChatSessionCreatedPayload(
                session_id=session_id,
                tool_session_id=tool_session_id,
                casefile_id=casefile_id,
                created_at=session.created_at,
            ),
            metadata={
                "execution_time_ms": execution_time_ms,
                "user_id": user_id,
                "operation": "create_chat_session",
            },
        )

    @register_service_method(
        name="process_chat_request",
        description="Parse message, call LLM, handle tool calls",
        service_name="CommunicationService",
        service_module="src.communicationservice.service",
        classification={
            "domain": "communication",
            "subdomain": "chat_processing",
            "capability": "process",
            "complexity": "pipeline",
            "maturity": "stable",
            "integration_tier": "hybrid"
        },
        required_permissions=["chat:write"],
        requires_casefile=False,
        enabled=True,
        requires_auth=True,
        timeout_seconds=120,
        version="1.0.0",
        dependencies=["ToolSessionService.process_tool_request", "LLM provider"]
    )
    async def process_chat_request(self, request: ChatRequest) -> ChatResponse:
        """Process a chat request and run any associated tool calls."""

        request_data = request.model_dump(
            mode="json",
            exclude={"operation_key", "timestamp"},
        )
        cleaned_request = ChatRequest.model_validate(request_data)

        session = await self.repository.get_session(cleaned_request.session_id)
        if not session:
            raise ValueError(f"Session {cleaned_request.session_id} not found")

        client_session_request_id = (
            cleaned_request.payload.session_request_id or self.id_service.new_session_request_id()
        )
        tool_session_id = await self._ensure_tool_session(session)

        context = MDSContext(
            user_id=session.user_id,
            session_id=tool_session_id,
            casefile_id=session.casefile_id,
            environment="development",
        )

        session_request_id = context.create_session_request(client_session_request_id)

        message_id = str(uuid4())
        message_data = cleaned_request.payload.model_dump()
        message_data.update(
            {
                "message_id": message_id,
                "request_id": session_request_id,
                "timestamp": datetime.now().isoformat(),
            }
        )

        session.messages.append(message_data)
        session.message_index[message_id] = len(session.messages) - 1
        session.request_index.setdefault(client_session_request_id, []).append(message_id)
        session.events.append(
            {
                "type": "message",
                "message_type": cleaned_request.payload.message_type.value,
                "timestamp": datetime.now().isoformat(),
                "message_id": message_id,
                "request_id": session_request_id,
                "session_request_id": client_session_request_id,
            }
        )

        try:
            start_time = datetime.now()
            context.register_event(
                "chat_message",
                {"content_length": len(cleaned_request.payload.content)},
            )

            tool_calls: List[Dict[str, Any]] = []
            for tool_call in cleaned_request.payload.tool_calls or []:
                tool_name = tool_call.get("name")
                tool_params = tool_call.get("arguments", {})
                if not tool_name:
                    continue

                tool_request = ToolRequest(
                    session_id=tool_session_id,
                    user_id=session.user_id,
                    operation="tool_execution",
                    payload=ToolRequestPayload(
                        tool_name=tool_name,
                        parameters=tool_params,
                        session_request_id=client_session_request_id,
                        casefile_id=session.casefile_id,
                    ),
                )
                tool_response = await self.tool_service.process_tool_request(tool_request)
                tool_calls.append(
                    {
                        "name": tool_name,
                        "result": tool_response.payload.result,
                    }
                )

            duration_ms = int((datetime.now() - start_time).total_seconds() * 1000)

            assistant_message = ChatMessagePayload(
                content=f"Received message: {cleaned_request.payload.content[:50]}...",
                message_type=MessageType.ASSISTANT,
                tool_calls=tool_calls,
                session_request_id=client_session_request_id,
                casefile_id=session.casefile_id,
            )

            response = ChatResponse(
                request_id=cleaned_request.request_id,
                status=RequestStatus.COMPLETED,
                session_request_id=client_session_request_id,
                payload=ChatResponsePayload(
                    message=assistant_message,
                    related_messages=[],
                    events=[event.model_dump() for event in context.tool_events],
                ),
            )

            assistant_message_id = str(uuid4())
            assistant_message_data = assistant_message.model_dump()
            assistant_message_data.update(
                {
                    "message_id": assistant_message_id,
                    "request_id": session_request_id,
                    "timestamp": datetime.now().isoformat(),
                }
            )
            session.messages.append(assistant_message_data)
            session.message_index[assistant_message_id] = len(session.messages) - 1
            session.request_index.setdefault(client_session_request_id, []).append(
                assistant_message_id
            )
            session.events.append(
                {
                    "type": "message",
                    "message_type": MessageType.ASSISTANT.value,
                    "timestamp": datetime.now().isoformat(),
                    "message_id": assistant_message_id,
                    "request_id": session_request_id,
                    "session_request_id": client_session_request_id,
                }
            )

            if context.tool_events:
                last_event = context.tool_events[-1]
                last_event.duration_ms = duration_ms
                last_event.result_summary = {"status": "success"}

        except Exception as exc:
            logger.exception("Error processing chat message: %s", exc)

            error_message = ChatMessagePayload(
                content=f"Error processing message: {exc}",
                message_type=MessageType.ERROR,
                session_request_id=client_session_request_id,
                casefile_id=session.casefile_id,
            )

            response = ChatResponse(
                request_id=cleaned_request.request_id,
                status=RequestStatus.FAILED,
                session_request_id=client_session_request_id,
                error=str(exc),
                payload=ChatResponsePayload(
                    message=error_message,
                    related_messages=[],
                    events=[event.model_dump() for event in context.tool_events],
                ),
            )

            error_message_id = str(uuid4())
            error_message_data = error_message.model_dump()
            error_message_data.update(
                {
                    "message_id": error_message_id,
                    "request_id": session_request_id,
                    "timestamp": datetime.now().isoformat(),
                }
            )
            session.messages.append(error_message_data)
            session.message_index[error_message_id] = len(session.messages) - 1
            session.request_index.setdefault(client_session_request_id, []).append(error_message_id)
            session.events.append(
                {
                    "type": "message",
                    "message_type": MessageType.ERROR.value,
                    "timestamp": datetime.now().isoformat(),
                    "message_id": error_message_id,
                    "request_id": session_request_id,
                    "session_request_id": client_session_request_id,
                    "error": str(exc),
                }
            )

            if context.tool_events:
                last_event = context.tool_events[-1]
                last_event.result_summary = {"status": "error", "message": str(exc)}

        session.updated_at = datetime.now().isoformat()
        await self.repository.update_session(session)

        return response

    @register_service_method(
        name="get_session",
        description="Retrieve chat session by ID",
        service_name="CommunicationService",
        service_module="src.communicationservice.service",
        classification={
            "domain": "communication",
            "subdomain": "chat_session",
            "capability": "read",
            "complexity": "atomic",
            "maturity": "stable",
            "integration_tier": "internal"
        },
        required_permissions=["chat:read"],
        requires_casefile=False,
        enabled=True,
        requires_auth=True,
        timeout_seconds=30,
        version="1.0.0"
    )
    async def get_session(self, request: GetChatSessionRequest) -> GetChatSessionResponse:
        """Return a chat session by ID."""
        start_time = datetime.now()

        session_id = request.payload.session_id
        include_messages = request.payload.include_messages

        session = await self.repository.get_session(session_id)
        if not session:
            execution_time_ms = int((datetime.now() - start_time).total_seconds() * 1000)
            return GetChatSessionResponse(
                request_id=request.request_id,
                status=RequestStatus.FAILED,
                error=f"Session {session_id} not found",
                payload=None,
                metadata={
                    "execution_time_ms": execution_time_ms,
                    "session_id": session_id,
                    "operation": "get_chat_session",
                },
            )

        # SECURITY: Verify session belongs to requesting user
        if session.user_id != request.user_id:
            execution_time_ms = int((datetime.now() - start_time).total_seconds() * 1000)
            return GetChatSessionResponse(
                request_id=request.request_id,
                status=RequestStatus.FAILED,
                error=f"Access denied: Session {session_id} does not belong to user {request.user_id}",
                payload=None,
                metadata={
                    "execution_time_ms": execution_time_ms,
                    "session_id": session_id,
                    "operation": "get_chat_session",
                    "security_check": "ownership_verification_failed",
                },
            )

        # Calculate message count
        message_count = len(session.messages)

        # Get messages if requested
        messages = session.messages if include_messages else None

        execution_time_ms = int((datetime.now() - start_time).total_seconds() * 1000)

        return GetChatSessionResponse(
            request_id=request.request_id,
            status=RequestStatus.COMPLETED,
            payload=ChatSessionDataPayload(
                session_id=session.session_id,
                user_id=session.user_id,
                casefile_id=session.casefile_id,
                created_at=session.created_at,
                updated_at=session.updated_at,
                active=session.active,
                message_count=message_count,
                messages=messages,
                metadata=session.metadata,
            ),
            metadata={
                "execution_time_ms": execution_time_ms,
                "include_messages": include_messages,
                "operation": "get_chat_session",
            },
        )

    @register_service_method(
        name="list_sessions",
        description="List chat sessions with filters",
        service_name="CommunicationService",
        service_module="src.communicationservice.service",
        classification={
            "domain": "communication",
            "subdomain": "chat_session",
            "capability": "search",
            "complexity": "atomic",
            "maturity": "stable",
            "integration_tier": "internal"
        },
        required_permissions=["chat:read"],
        requires_casefile=False,
        enabled=True,
        requires_auth=True,
        timeout_seconds=30,
        version="1.0.0"
    )
    async def list_sessions(self, request: ListChatSessionsRequest) -> ListChatSessionsResponse:
        """List chat sessions, optionally filtered by user or casefile."""
        start_time = datetime.now()

        user_id = request.payload.user_id
        casefile_id = request.payload.casefile_id
        active_only = request.payload.active_only
        limit = request.payload.limit
        offset = request.payload.offset

        sessions = await self.repository.list_sessions(user_id=user_id, casefile_id=casefile_id)

        # Filter by active status if requested
        if active_only:
            sessions = [s for s in sessions if s.active]

        # Apply pagination
        total_count = len(sessions)
        paginated_sessions = sessions[offset : offset + limit]

        # Build summaries
        summaries = [
            ChatSessionSummary(
                session_id=session.session_id,
                user_id=session.user_id,
                casefile_id=session.casefile_id,
                created_at=session.created_at,
                updated_at=session.updated_at,
                message_count=len(session.messages),
                active=session.active,
            )
            for session in paginated_sessions
        ]

        execution_time_ms = int((datetime.now() - start_time).total_seconds() * 1000)

        return ListChatSessionsResponse(
            request_id=request.request_id,
            status=RequestStatus.COMPLETED,
            payload=ChatSessionListPayload(
                sessions=summaries, total_count=total_count, offset=offset, limit=limit
            ),
            metadata={
                "execution_time_ms": execution_time_ms,
                "filters_applied": {
                    "user_id": user_id,
                    "casefile_id": casefile_id,
                    "active_only": active_only,
                },
                "operation": "list_chat_sessions",
            },
        )

    @register_service_method(
        name="close_session",
        description="Close chat session",
        service_name="CommunicationService",
        service_module="src.communicationservice.service",
        classification={
            "domain": "communication",
            "subdomain": "chat_session",
            "capability": "update",
            "complexity": "atomic",
            "maturity": "stable",
            "integration_tier": "internal"
        },
        required_permissions=["chat:write"],
        requires_casefile=False,
        enabled=True,
        requires_auth=True,
        timeout_seconds=30,
        version="1.0.0"
    )
    async def close_session(self, request: CloseChatSessionRequest) -> CloseChatSessionResponse:
        """Close a chat session and any linked tool session."""
        start_time = datetime.now()

        session_id = request.payload.session_id

        session = await self.repository.get_session(session_id)
        if not session:
            execution_time_ms = int((datetime.now() - start_time).total_seconds() * 1000)
            return CloseChatSessionResponse(
                request_id=request.request_id,
                status=RequestStatus.FAILED,
                error=f"Session {session_id} not found",
                payload=None,
                metadata={
                    "execution_time_ms": execution_time_ms,
                    "session_id": session_id,
                    "operation": "close_chat_session",
                },
            )

        # SECURITY: Verify session belongs to requesting user
        if session.user_id != request.user_id:
            execution_time_ms = int((datetime.now() - start_time).total_seconds() * 1000)
            return CloseChatSessionResponse(
                request_id=request.request_id,
                status=RequestStatus.FAILED,
                error=f"Access denied: Session {session_id} does not belong to user {request.user_id}",
                payload=None,
                metadata={
                    "execution_time_ms": execution_time_ms,
                    "session_id": session_id,
                    "operation": "close_chat_session",
                    "security_check": "ownership_verification_failed",
                },
            )

        # Calculate statistics before closing
        message_count = len(session.messages)
        event_count = len(session.events)
        created_at_dt = (
            datetime.fromisoformat(session.created_at)
            if isinstance(session.created_at, str)
            else session.created_at
        )
        duration_seconds = int((datetime.now() - created_at_dt).total_seconds())

        session.active = False
        session.updated_at = datetime.now().isoformat()
        await self.repository.update_session(session)

        tool_session_id = (session.metadata or {}).get("tool_session_id")
        tool_session_closed = False
        tool_session_error = None

        if tool_session_id:
            try:
                logger.info("Closing tool session %s", tool_session_id)
                from ..pydantic_models.operations.tool_session_ops import CloseSessionRequest

                close_tool_request = CloseSessionRequest(
                    user_id=request.user_id,
                    operation="close_session",
                    payload={"session_id": tool_session_id},
                )
                await self.tool_service.close_session(close_tool_request)
                tool_session_closed = True
            except Exception as exc:
                logger.warning("Failed to close tool session %s: %s", tool_session_id, exc)
                tool_session_error = str(exc)

        execution_time_ms = int((datetime.now() - start_time).total_seconds() * 1000)

        return CloseChatSessionResponse(
            request_id=request.request_id,
            status=RequestStatus.COMPLETED,
            payload=ChatSessionClosedPayload(
                session_id=session.session_id,
                closed_at=session.updated_at,
                message_count=message_count,
                event_count=event_count,
                duration_seconds=duration_seconds,
                tool_session_id=tool_session_id,
                tool_session_closed=tool_session_closed,
            ),
            metadata={
                "execution_time_ms": execution_time_ms,
                "tool_session_error": tool_session_error,
                "operation": "close_chat_session",
            },
        )

    @register_service_method(
        name="_ensure_tool_session",
        description="Internal: ensure tool session exists for chat",
        service_name="CommunicationService",
        service_module="src.communicationservice.service",
        classification={
            "domain": "communication",
            "subdomain": "chat_session",
            "capability": "process",
            "complexity": "atomic",
            "maturity": "stable",
            "integration_tier": "internal"
        },
        required_permissions=[],
        requires_casefile=False,
        enabled=True,
        requires_auth=True,
        timeout_seconds=30,
        version="1.0.0",
        visibility="private"
    )
    async def _ensure_tool_session(self, session: ChatSession) -> str:
        """Ensure the chat session has a corresponding tool session."""

        metadata = session.metadata or {}
        tool_session_id = metadata.get("tool_session_id")

        if not tool_session_id:
            tool_request = CreateSessionRequest(
                user_id=session.user_id,
                operation="create_tool_session",
                payload={"casefile_id": session.casefile_id},
            )
            tool_response = await self.tool_service.create_session(tool_request)
            tool_session_id = tool_response.payload.session_id
            metadata["tool_session_id"] = tool_session_id
            session.metadata = metadata

        return tool_session_id
