"""
Router for chat API endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import Optional

from ...communicationservice.service import CommunicationService
from ...pydantic_models.shared.base_models import RequestEnvelope

router = APIRouter(
    prefix="/api/chat",
    tags=["chat"]
)

async def get_communication_service():
    """Dependency to get the communication service."""
    return CommunicationService()

@router.post("/sessions")
async def create_session(
    request: RequestEnvelope,
    service: CommunicationService = Depends(get_communication_service)
):
    """Create a new chat session."""
    
    # Extract request data
    user_id = request.request.get("user_id")
    casefile_id = request.request.get("casefile_id")
    
    if not user_id:
        raise HTTPException(status_code=400, detail="Missing user_id")
    
    # Create session
    result = await service.create_session(user_id, casefile_id)
    return {"session_id": result["session_id"], "trace_id": request.trace_id}

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

@router.get("/sessions/{session_id}")
async def get_session(
    session_id: str,
    service: CommunicationService = Depends(get_communication_service)
):
    """Get a chat session."""
    try:
        session = await service.get_session(session_id)
        return session
    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving session: {str(e)}"
        )

@router.get("/sessions")
async def list_sessions(
    user_id: Optional[str] = None,
    casefile_id: Optional[str] = None,
    service: CommunicationService = Depends(get_communication_service)
):
    """List chat sessions."""
    try:
        sessions = await service.list_sessions(user_id, casefile_id)
        return {"sessions": sessions}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error listing sessions: {str(e)}"
        )

@router.post("/sessions/{session_id}/close")
async def close_session(
    session_id: str,
    service: CommunicationService = Depends(get_communication_service)
):
    """Close a chat session."""
    try:
        result = await service.close_session(session_id)
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error closing session: {str(e)}"
        )