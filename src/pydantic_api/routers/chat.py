"""
Router for chat API endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import Optional

from ...communicationservice.service import CommunicationService
from ...pydantic_models.communication.session_models import (
    CloseChatSessionRequest,
    CloseChatSessionResponse,
    CreateChatSessionRequest,
    CreateChatSessionResponse,
    GetChatSessionRequest,
    GetChatSessionResponse,
    ListChatSessionsRequest,
    ListChatSessionsResponse,
)
from ...pydantic_models.shared.base_models import RequestEnvelope

router = APIRouter(
    prefix="/api/chat",
    tags=["chat"]
)

async def get_communication_service():
    """Dependency to get the communication service."""
    return CommunicationService()

@router.post("/sessions", response_model=CreateChatSessionResponse)
async def create_session(
    request: RequestEnvelope,
    service: CommunicationService = Depends(get_communication_service)
) -> CreateChatSessionResponse:
    """Create a new chat session."""
    
    # Extract request data
    user_id = request.request.get("user_id")
    casefile_id = request.request.get("casefile_id")
    
    if not user_id:
        raise HTTPException(status_code=400, detail="Missing user_id")
    
    # Create session request
    create_request = CreateChatSessionRequest(
        user_id=user_id,
        operation="create_chat_session",
        payload={"casefile_id": casefile_id}
    )
    
    response = await service.create_session(create_request)
    
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
    service: CommunicationService = Depends(get_communication_service)
):
    """Send a message in a chat session."""
    
    # Extract request data and create ChatRequest
    message_data = request.request
    message_data["session_id"] = session_id
    
    try:
        # Construct the chat request
        from ...pydantic_models.communication.models import ChatRequest, ChatMessagePayload, MessageType
        
        # The user message comes in the request payload
        content = message_data.get("content", "")
        message_type = message_data.get("message_type", MessageType.USER)
        tool_calls = message_data.get("tool_calls", [])
        session_request_id = message_data.get("session_request_id")
        casefile_id = message_data.get("casefile_id")
        user_id = message_data.get("user_id", "anonymous")
        
        # Create the message payload
        chat_payload = ChatMessagePayload(
            content=content,
            message_type=message_type,
            tool_calls=tool_calls,
            session_request_id=session_request_id,
            casefile_id=casefile_id
        )
        
        # Create the request
        chat_request = ChatRequest(
            session_id=session_id,
            user_id=user_id,
            operation="chat_message",
            payload=chat_payload
        )
        
        # Process the request
        response = await service.process_chat_request(chat_request)
        
        # Merge trace_id into response
        result = response.model_dump()
        result["trace_id"] = request.trace_id
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing message: {str(e)}"
        )

@router.get("/sessions/{session_id}", response_model=GetChatSessionResponse)
async def get_session(
    session_id: str,
    include_messages: bool = True,
    service: CommunicationService = Depends(get_communication_service)
) -> GetChatSessionResponse:
    """Get a chat session."""
    try:
        # Create request
        get_request = GetChatSessionRequest(
            user_id="anonymous",  # TODO: Get from auth
            operation="get_chat_session",
            payload={
                "session_id": session_id,
                "include_messages": include_messages
            }
        )
        
        response = await service.get_session(get_request)
        
        if response.status.value == "failed":
            raise HTTPException(status_code=404, detail=response.error or "Session not found")
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving session: {str(e)}"
        )

@router.get("/sessions", response_model=ListChatSessionsResponse)
async def list_sessions(
    user_id: Optional[str] = None,
    casefile_id: Optional[str] = None,
    active_only: bool = True,
    limit: int = 50,
    offset: int = 0,
    service: CommunicationService = Depends(get_communication_service)
) -> ListChatSessionsResponse:
    """List chat sessions."""
    try:
        # Create request
        list_request = ListChatSessionsRequest(
            user_id=user_id or "anonymous",  # TODO: Get from auth
            operation="list_chat_sessions",
            payload={
                "user_id": user_id,
                "casefile_id": casefile_id,
                "active_only": active_only,
                "limit": limit,
                "offset": offset
            }
        )
        
        return await service.list_sessions(list_request)
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error listing sessions: {str(e)}"
        )

@router.post("/sessions/{session_id}/close", response_model=CloseChatSessionResponse)
async def close_session(
    session_id: str,
    service: CommunicationService = Depends(get_communication_service)
) -> CloseChatSessionResponse:
    """Close a chat session."""
    try:
        # Create request
        close_request = CloseChatSessionRequest(
            user_id="anonymous",  # TODO: Get from auth
            operation="close_chat_session",
            payload={"session_id": session_id}
        )
        
        response = await service.close_session(close_request)
        
        if response.status.value == "failed":
            raise HTTPException(status_code=404, detail=response.error or "Session not found")
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error closing session: {str(e)}"
        )