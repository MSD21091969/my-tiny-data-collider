"""Service for handling chat sessions and message processing."""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import uuid4

from ..coreservice.id_service import get_id_service
from ..pydantic_ai_integration.agents.base import import_tools
from ..pydantic_ai_integration.dependencies import MDSContext
from ..pydantic_models.communication.models import (
    ChatMessagePayload,
    ChatRequest,
    ChatResponse,
    ChatResponsePayload,
    ChatSession,
    MessageType,
)
from ..pydantic_models.shared.base_models import RequestStatus
from ..pydantic_models.tool_session.models import ToolRequest, ToolRequestPayload
from ..tool_sessionservice.service import ToolSessionService
from .repository import ChatSessionRepository

import_tools()

logger = logging.getLogger(__name__)

class CommunicationService:
    """Service for handling chat sessions and message processing."""
    
    def __init__(self, use_mocks: Optional[bool] = None) -> None:
        """Initialize the communication and tool session services."""

        from ..coreservice.config import get_use_mocks

        self.use_mocks = use_mocks if use_mocks is not None else get_use_mocks()
        self.repository = ChatSessionRepository(use_mocks=self.use_mocks)
        self.tool_service = ToolSessionService(use_mocks=self.use_mocks)
        self.id_service = get_id_service()
        
    async def create_session(self, user_id: str, casefile_id: Optional[str] = None) -> Dict[str, str]:
        """Create a new chat session and its linked tool session."""

        session_id = self.id_service.new_chat_session_id(user_id=user_id, casefile_id=casefile_id)

        session = ChatSession(
            session_id=session_id,
            user_id=user_id,
            casefile_id=casefile_id,
        )
        await self.repository.create_session(session)

        tool_session = await self.tool_service.create_session(user_id, casefile_id)

        session.metadata = session.metadata or {}
        session.metadata["tool_session_id"] = tool_session["session_id"]
        session.updated_at = datetime.now().isoformat()
        await self.repository.update_session(session)

        logger.info("Created chat session %s with tool session %s", session_id, tool_session["session_id"])

        return {"session_id": session_id, "tool_session_id": tool_session["session_id"]}
    
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
            use_mocks=self.use_mocks,
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
            session.request_index.setdefault(client_session_request_id, []).append(assistant_message_id)
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
    
    async def get_session(self, session_id: str) -> Dict[str, Any]:
        """Return a chat session by ID."""

        session = await self.repository.get_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")

        return session.model_dump()

    async def list_sessions(
        self,
        user_id: Optional[str] = None,
        casefile_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """List chat sessions, optionally filtered by user or casefile."""

        sessions = await self.repository.list_sessions(user_id=user_id, casefile_id=casefile_id)
        return [
            {
                "session_id": session.session_id,
                "user_id": session.user_id,
                "casefile_id": session.casefile_id,
                "created_at": session.created_at,
                "updated_at": session.updated_at,
                "message_count": len(session.messages),
                "active": session.active,
            }
            for session in sessions
        ]

    async def close_session(self, session_id: str) -> Dict[str, Any]:
        """Close a chat session and any linked tool session."""

        session = await self.repository.get_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")

        session.active = False
        session.updated_at = datetime.now().isoformat()
        await self.repository.update_session(session)

        tool_session_id = (session.metadata or {}).get("tool_session_id")
        if tool_session_id:
            try:
                logger.info("Closing tool session %s", tool_session_id)
                await self.tool_service.close_session(tool_session_id)
            except Exception as exc:
                logger.warning("Failed to close tool session %s: %s", tool_session_id, exc)

        return {
            "session_id": session.session_id,
            "status": "closed",
            "updated_at": session.updated_at,
        }

    async def _ensure_tool_session(self, session: ChatSession) -> str:
        """Ensure the chat session has a corresponding tool session."""

        metadata = session.metadata or {}
        tool_session_id = metadata.get("tool_session_id")

        if not tool_session_id:
            tool_session = await self.tool_service.create_session(session.user_id, session.casefile_id)
            tool_session_id = tool_session["session_id"]
            metadata["tool_session_id"] = tool_session_id
            session.metadata = metadata

        return tool_session_id


