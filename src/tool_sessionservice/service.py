"""
Service for handling tool sessions and tool execution.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

from ..pydantic_models.tool_session import ToolRequest, ToolResponse, ToolSession, ToolRequestPayload, ToolResponsePayload, ToolEvent
from ..pydantic_models.tool_session.resume_models import SessionResumeRequest, SessionResumeResponse
from ..pydantic_ai_integration.dependencies import MDSContext
from ..pydantic_ai_integration.agents.base import get_agent_for_toolset
from ..pydantic_models.shared.base_models import RequestStatus
from .repository import ToolSessionRepository
from ..coreservice.id_service import get_id_service

logger = logging.getLogger(__name__)

class ToolSessionService:
    """Service for handling tool sessions and tool execution (Firestore only)."""

    def __init__(self):
        self.repository = ToolSessionRepository()
        self.id_service = get_id_service()
        
    async def create_session(self, user_id: str, casefile_id: Optional[str] = None) -> Dict[str, str]:
        """Create a new tool session.
        
        Args:
            user_id: ID of the user creating the session
            casefile_id: Optional casefile ID to associate with the session
            
        Returns:
            Dictionary with the session ID
        """
        session_id = self.id_service.new_tool_session_id(user_id=user_id, casefile_id=casefile_id)
        
        # Create session record
        session = ToolSession(
            session_id=session_id,
            user_id=user_id,
            casefile_id=casefile_id
        )
        
        # Store in repository
        await self.repository.create_session(session)
        
        # If this session is linked to a casefile, update the casefile to include this session
        if casefile_id:
            try:
                from ..casefileservice.service import CasefileService
                # CasefileService signature previously allowed use_mocks; now Firestore-only
                casefile_service = CasefileService()
                await casefile_service.add_session_to_casefile(casefile_id, session_id)
                logger.info(f"Successfully linked session {session_id} to casefile {casefile_id}")
            except Exception as e:
                logger.warning(f"Failed to link session {session_id} to casefile {casefile_id}: {e}")
                # Don't fail the session creation if casefile linking fails
        
        return {"session_id": session_id}
    
    async def process_tool_request(self, request: ToolRequest) -> ToolResponse:
        """Process a tool request.
        
        Args:
            request: The tool request to process
            
        Returns:
            The tool response
        """
        # Clean computed fields before revalidation
        request_data = request.model_dump(
            mode="json",
            exclude={"operation_key", "timestamp", "has_casefile_context"}
        )
        cleaned_request = ToolRequest.model_validate(request_data)
        
        # Get the session
        session_id = cleaned_request.session_id
        if not session_id:
            raise ValueError("Session ID is required for tool execution")
        
        session = await self.repository.get_session(session_id)
        if not session:
            raise ValueError(f"Session {cleaned_request.session_id} not found")
            
        request_id = str(cleaned_request.request_id)
        
        # Add request to session
        session.request_ids.append(request_id)
        session.updated_at = datetime.now().isoformat()
        await self.repository.update_session(session)
        
        # Store request in subcollection
        await self.repository.add_request_to_session(session_id, cleaned_request)
        
        # Create context for tool execution
        context = MDSContext(
            user_id=session.user_id,
            session_id=session.session_id,
            casefile_id=session.casefile_id,
            environment="development"
        )
        
        # Handle client-provided session request ID if present
        client_session_request_id = cleaned_request.payload.session_request_id
        session_request_id = client_session_request_id or self.id_service.new_session_request_id()
        context.create_session_request(session_request_id)

        # Create tool_request_received event
        request_received_event = ToolEvent(
            event_type="tool_request_received",
            tool_name=cleaned_request.payload.tool_name,
            parameters=cleaned_request.payload.parameters,
        )
        await self.repository.add_event_to_request(session_id, request_id, request_received_event)
        cleaned_request.event_ids.append(request_received_event.event_id)
        
        # Get the appropriate agent for this tool
        agent = get_agent_for_toolset(cleaned_request.payload.tool_name)
        
        try:
            # Create tool_execution_started event
            start_time = datetime.now()
            execution_started_event = ToolEvent(
                event_type="tool_execution_started",
                tool_name=cleaned_request.payload.tool_name,
                parameters=cleaned_request.payload.parameters,
                status="pending"
            )
            await self.repository.add_event_to_request(session_id, request_id, execution_started_event)
            cleaned_request.event_ids.append(execution_started_event.event_id)
            
            # Execute the tool via agent
            prompt = cleaned_request.payload.prompt or f"Execute the {cleaned_request.payload.tool_name} tool"
            
            logger.info(f"Running tool {cleaned_request.payload.tool_name} with parameters: {cleaned_request.payload.parameters}")
            
            # Direct execution for example tools
            tool_name = cleaned_request.payload.tool_name
            tool_params = cleaned_request.payload.parameters
            
            if tool_name == "example_tool":
                from ..pydantic_ai_integration.tools.enhanced_example_tools import example_tool
                value = tool_params.get("value", 42)
                result_data = await example_tool(context, value)
                result = type('AgentResult', (), {'output': result_data})
            elif tool_name == "another_example_tool":
                from ..pydantic_ai_integration.tools.enhanced_example_tools import another_example_tool
                name = tool_params.get("name", "Example User")
                count = tool_params.get("count", 3)
                result_data = await another_example_tool(context, name, count)
                result = type('AgentResult', (), {'output': result_data})
            else:
                if cleaned_request.payload.parameters:
                    import json
                    params_json = json.dumps(cleaned_request.payload.parameters)
                    prompt = f"{prompt} with parameters: {params_json}"
                result = await agent.run(prompt, deps=context)
            
            # Calculate duration
            duration_ms = int((datetime.now() - start_time).total_seconds() * 1000)
            
            # Create tool_execution_completed event
            execution_completed_event = ToolEvent(
                event_type="tool_execution_completed",
                tool_name=cleaned_request.payload.tool_name,
                parameters=cleaned_request.payload.parameters,
                result_summary=result.output,
                duration_ms=duration_ms,
                status="success"
            )
            await self.repository.add_event_to_request(session_id, request_id, execution_completed_event)
            cleaned_request.event_ids.append(execution_completed_event.event_id)
            
            # Create response
            response = ToolResponse(
                request_id=cleaned_request.request_id,
                status=RequestStatus.COMPLETED,
                payload=ToolResponsePayload(
                    result=result.output,
                    events=[],
                    session_request_id=session_request_id
                ),
                timestamp=datetime.now().isoformat()
            )
            
        except Exception as e:
            logger.exception(f"Error executing tool {cleaned_request.payload.tool_name}: {e}")
            
            # Calculate duration
            duration_ms = int((datetime.now() - start_time).total_seconds() * 1000)
            
            # Create tool_execution_failed event
            execution_failed_event = ToolEvent(
                event_type="tool_execution_failed",
                tool_name=cleaned_request.payload.tool_name,
                parameters=cleaned_request.payload.parameters,
                duration_ms=duration_ms,
                status="error",
                error_message=str(e)
            )
            await self.repository.add_event_to_request(session_id, request_id, execution_failed_event)
            cleaned_request.event_ids.append(execution_failed_event.event_id)
            
            # Create error response
            response = ToolResponse(
                request_id=cleaned_request.request_id,
                status=RequestStatus.FAILED,
                payload=ToolResponsePayload(
                    result={},
                    events=[],
                    session_request_id=session_request_id
                ),
                timestamp=datetime.now().isoformat(),
                error=str(e)
            )
        
        # Create tool_response_sent event  
        response_sent_event = ToolEvent(
            event_type="tool_response_sent",
            tool_name=cleaned_request.payload.tool_name,
            parameters={},
            status="success" if response.error is None else "error",
            result_summary={"response_status": response.status.value, "has_error": response.error is not None}
        )
        await self.repository.add_event_to_request(session_id, request_id, response_sent_event)
        cleaned_request.event_ids.append(response_sent_event.event_id)
        
        # Update response in repository
        await self.repository.update_request_response(session_id, request_id, response)
        
        # Update session timestamp
        session.updated_at = datetime.now().isoformat()
        await self.repository.update_session(session)
        
        return response
    
    async def get_session(self, session_id: str) -> Dict[str, Any]:
        """Get a session by ID.
        
        Args:
            session_id: ID of the session to retrieve
            
        Returns:
            The session data
        """
        session = await self.repository.get_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")
            
        return session.model_dump()
    
    async def list_sessions(self, user_id: Optional[str] = None, casefile_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """List sessions, optionally filtered by user or casefile.
        
        Args:
            user_id: Optional user ID to filter by
            casefile_id: Optional casefile ID to filter by
            
        Returns:
            List of session summaries
        """
        sessions = await self.repository.list_sessions(
            user_id=user_id,
            casefile_id=casefile_id
        )
        
        # Return simplified summary view
        return [
            {
                "session_id": session.session_id,
                "user_id": session.user_id,
                "casefile_id": session.casefile_id if session.casefile_id else None,
                "created_at": session.created_at,
                "updated_at": session.updated_at,
                "request_count": len(session.request_ids),
                "active": session.active
            }
            for session in sessions
        ]
    
    async def close_session(self, session_id: str) -> Dict[str, Any]:
        """Close a session.
        
        Args:
            session_id: ID of the session to close
            
        Returns:
            Status information
        """
        session = await self.repository.get_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")
            
        session.active = False
        session.updated_at = datetime.now().isoformat()
        await self.repository.update_session(session)
        
        return {
            "session_id": session.session_id,
            "status": "closed",
            "updated_at": session.updated_at
        }
        
    async def resume_session(self, user_id: str, request: SessionResumeRequest) -> SessionResumeResponse:
        """Resume a previous session.
        
        Args:
            user_id: ID of the user resuming the session
            request: Session resume request with session ID
            
        Returns:
            Session resume response with session details
            
        Raises:
            ValueError: If session not found or doesn't belong to the user
        """
        session_id = request.session_id
        session = await self.repository.get_session(session_id)
        
        if not session:
            raise ValueError(f"Session {session_id} not found")
            
        # Verify ownership
        if session.user_id != user_id:
            raise ValueError(f"Session {session_id} does not belong to user {user_id}")
            
        # Ensure session is active
        if not session.active:
            session.active = True
            session.updated_at = datetime.now().isoformat()
            await self.repository.update_session(session)
            
        # Get last request ID
        last_request_id = session.request_ids[-1] if session.request_ids else None
        
        # Create context summary
        context_summary = {
            "user_id": session.user_id,
            "casefile_id": session.casefile_id if session.casefile_id else None,
            "active": session.active,
            "created_at": session.created_at,
            "updated_at": session.updated_at
        }
        
        return SessionResumeResponse(
            session_id=session_id,
            last_request_id=last_request_id,
            last_response_id=last_request_id,  # Same as request ID in new structure
            updated_at=session.updated_at,
            request_count=len(session.request_ids),
            context_summary=context_summary
        )