"""
Service for handling tool sessions and tool execution.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

from ..pydantic_models.tool_session import ToolRequest, ToolResponse, ToolSession, ToolRequestPayload, ToolResponsePayload
from ..pydantic_models.tool_session.resume_models import SessionResumeRequest, SessionResumeResponse
from ..pydantic_ai_integration.dependencies import MDSContext
from ..pydantic_ai_integration.agents.base import get_agent_for_toolset
from ..pydantic_models.shared.base_models import RequestStatus
from .repository import ToolSessionRepository
from ..coreservice.id_service import get_id_service

logger = logging.getLogger(__name__)

class ToolSessionService:
    """Service for handling tool sessions and tool execution."""
    
    def __init__(self, use_mocks: bool = None):
        """Initialize the service.
        
        Args:
            use_mocks: Whether to use mock implementations. If None, determined from environment.
        """
        from ..coreservice.config import get_use_mocks
        self.use_mocks = use_mocks if use_mocks is not None else get_use_mocks()
        self.repository = ToolSessionRepository(use_mocks=self.use_mocks)
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
                casefile_service = CasefileService(use_mocks=self.use_mocks)
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
            
        # Handle client-provided session request ID if present
        client_session_request_id = cleaned_request.payload.session_request_id
        
        # Create context for tool execution
        context = MDSContext(
            user_id=session.user_id,
            session_id=session.session_id,
            casefile_id=session.casefile_id,
            use_mocks=self.use_mocks,
            environment="development"  # Would get from config in real implementation
        )
        
        # Create request ID - use client-provided ID if available
        session_request_id = client_session_request_id or self.id_service.new_session_request_id()
        request_id = context.create_session_request(session_request_id)

        # Store request in session
        request_key = str(request_id)
        session.requests[request_key] = cleaned_request
        
        # Add to request index for easier lookup
        if session_request_id not in session.request_index:
            session.request_index[session_request_id] = []
        session.request_index[session_request_id].append(request_key)
        
        # Add to events chronologically
        session.events.append({
            "type": "request",
            "timestamp": datetime.now().isoformat(),
            "request_id": request_key,
            "session_request_id": session_request_id,
            "tool_name": cleaned_request.payload.tool_name
        })
        
        await self.repository.update_session(session)
        
        # Get the appropriate agent for this tool
        agent = get_agent_for_toolset(cleaned_request.payload.tool_name)
        
        try:
            # Log the start of tool execution
            start_time = datetime.now()
            context.register_event(
                cleaned_request.payload.tool_name, 
                cleaned_request.payload.parameters
            )
            
            # Execute the tool via agent
            prompt = cleaned_request.payload.prompt or f"Execute the {cleaned_request.payload.tool_name} tool"
            
            # Log the prompt and parameters for debugging
            logger.info(f"Running tool {cleaned_request.payload.tool_name} with parameters: {cleaned_request.payload.parameters}")
            logger.info(f"Using prompt: {prompt}")
            
            # Direct execution for example_tool and another_example_tool
            tool_name = cleaned_request.payload.tool_name
            tool_params = cleaned_request.payload.parameters
            
            logger.info(f"Tool name: {tool_name}")
            logger.info(f"Tool parameters: {tool_params}")
            
            # Try direct tool execution first
            if tool_name == "example_tool":
                logger.info("Executing example_tool directly")
                try:
                    # Import and call directly for testing
                    from ..pydantic_ai_integration.tools.enhanced_example_tools import example_tool
                    value = tool_params.get("value", 42)  # Default to 42 if not provided
                    logger.info(f"Calling example_tool with value={value}")
                    result_data = await example_tool(context, value)
                    logger.info(f"Got result: {result_data}")
                    result = type('AgentResult', (), {'output': result_data})
                except Exception as e:
                    logger.exception(f"Error executing example_tool directly: {e}")
                    raise
            elif tool_name == "another_example_tool":
                logger.info("Executing another_example_tool directly")
                try:
                    # Import and call directly for testing
                    from ..pydantic_ai_integration.tools.enhanced_example_tools import another_example_tool
                    name = tool_params.get("name", "Example User")
                    count = tool_params.get("count", 3)
                    logger.info(f"Calling another_example_tool with name={name}, count={count}")
                    result_data = await another_example_tool(context, name, count)
                    logger.info(f"Got result: {result_data}")
                    result = type('AgentResult', (), {'output': result_data})
                except Exception as e:
                    logger.exception(f"Error executing another_example_tool directly: {e}")
                    raise
            else:
                # Make sure we include the parameters in the prompt for the agent's simple parsing
                if cleaned_request.payload.parameters:
                    import json
                    params_json = json.dumps(cleaned_request.payload.parameters)
                    prompt = f"{prompt} with parameters: {params_json}"
                    
                # Use the agent for other tools
                logger.info(f"Using agent for tool: {tool_name}")
                result = await agent.run(prompt, deps=context)
            
            # Calculate duration
            duration_ms = int((datetime.now() - start_time).total_seconds() * 1000)
            
            # Create response
            response = ToolResponse(
                request_id=cleaned_request.request_id,
                status=RequestStatus.COMPLETED,
                payload=ToolResponsePayload(
                    result=result.output,
                    events=[event.model_dump() for event in context.tool_events],
                    session_request_id=session_request_id
                ),
                timestamp=datetime.now().isoformat()
            )
            
            # Update the last event with result summary and duration
            if context.tool_events:
                last_event = context.tool_events[-1]
                last_event.duration_ms = duration_ms
                last_event.result_summary = {"status": "success"}
            
        except Exception as e:
            # Log the error
            logger.exception(f"Error executing tool {cleaned_request.payload.tool_name}: {e}")
            
            # Create error response
            response = ToolResponse(
                request_id=cleaned_request.request_id,
                status=RequestStatus.FAILED,
                payload=ToolResponsePayload(
                    result={},
                    events=[event.model_dump() for event in context.tool_events],
                    session_request_id=session_request_id
                ),
                timestamp=datetime.now().isoformat(),
                error=str(e)
            )
            
            # Update the last event with error information
            if context.tool_events:
                last_event = context.tool_events[-1]
                last_event.result_summary = {"status": "error", "message": str(e)}
        
        # Session request ID is already set in the payload
        
        # Store response in session
        response_id = request_key
        session.responses[response_id] = response
        session.updated_at = datetime.now().isoformat()
        
        # Add to events chronologically
        session.events.append({
            "type": "response",
            "timestamp": datetime.now().isoformat(),
            "request_id": response_id,
            "session_request_id": session_request_id,
            "tool_name": cleaned_request.payload.tool_name,
            "status": "success" if response.error is None else "error"
        })
        
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
                "request_count": len(session.requests),
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
            
        # Get last request and response IDs
        last_request_id = None
        last_response_id = None
        
        if session.events:
            # Find the last event of each type
            for event in reversed(session.events):
                if event["type"] == "request" and not last_request_id:
                    last_request_id = event["request_id"]
                if event["type"] == "response" and not last_response_id:
                    last_response_id = event["request_id"]
                    
                if last_request_id and last_response_id:
                    break
        
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
            last_response_id=last_response_id,
            updated_at=session.updated_at,
            request_count=len(session.requests),
            context_summary=context_summary
        )