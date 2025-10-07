"""
Service for handling tool sessions and tool execution.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import logging
from pydantic import ValidationError

from pydantic_models.operations.tool_execution_ops import (
    ToolRequest, ToolResponse, ToolResponsePayload, ToolRequestPayload
)
from pydantic_models.canonical.tool_session import ToolSession, ToolEvent
from pydantic_models.operations.tool_session_ops import (
    CreateSessionRequest, CreateSessionResponse, SessionCreatedPayload,
    GetSessionRequest, GetSessionResponse, SessionDataPayload,
    ListSessionsRequest, ListSessionsResponse, SessionListPayload,
    CloseSessionRequest, CloseSessionResponse, SessionClosedPayload,
)
from pydantic_models.views.session_views import SessionSummary
from pydantic_ai_integration.dependencies import MDSContext
from pydantic_ai_integration.tool_decorator import (
    get_tool_definition,
    validate_tool_exists,
    get_tool_names
)
from pydantic_models.base.types import RequestStatus
from .repository import ToolSessionRepository
from coreservice.id_service import get_id_service

logger = logging.getLogger(__name__)

class ToolSessionService:
    """Service for handling tool sessions and tool execution (Firestore only)."""

    def __init__(self):
        self.repository = ToolSessionRepository()
        self.id_service = get_id_service()
        
    async def create_session(self, request: CreateSessionRequest) -> CreateSessionResponse:
        """Create a new tool session.
        
        Args:
            request: CreateSessionRequest with casefile_id and optional title
            
        Returns:
            CreateSessionResponse with session_id and creation details
        """
        start_time = datetime.now()
        user_id = request.user_id
        casefile_id = request.payload.casefile_id
        
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
                from casefileservice.service import CasefileService
                casefile_service = CasefileService()
                await casefile_service.add_session_to_casefile(casefile_id, session_id)
                logger.info(f"Successfully linked session {session_id} to casefile {casefile_id}")
            except Exception as e:
                logger.warning(f"Failed to link session {session_id} to casefile {casefile_id}: {e}")
                # Don't fail the session creation if casefile linking fails
        
        execution_time_ms = int((datetime.now() - start_time).total_seconds() * 1000)
        
        return CreateSessionResponse(
            request_id=request.request_id,
            status=RequestStatus.COMPLETED,
            payload=SessionCreatedPayload(
                session_id=session_id,
                casefile_id=casefile_id,
                created_at=session.created_at
            ),
            metadata={
                "execution_time_ms": execution_time_ms,
                "user_id": user_id,
                "operation": "create_session"
            }
        )
    
    async def process_tool_request(self, request: ToolRequest) -> ToolResponse:
        """Process a tool request using the unified MANAGED_TOOLS registry.
        
        This method:
        1. Validates the session exists
        2. Validates the tool is registered in MANAGED_TOOLS
        3. Validates parameters using the tool's Pydantic model
        4. Executes the tool with validated parameters
        5. Records audit events throughout
        
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
            raise ValueError(f"Session {session_id} not found")
            
        request_id = str(cleaned_request.request_id)
        tool_name = cleaned_request.payload.tool_name
        
        # Validate tool is registered in MANAGED_TOOLS
        if not validate_tool_exists(tool_name):
            available = ', '.join(get_tool_names())
            raise ValueError(f"Tool '{tool_name}' not registered. Available tools: {available}")
        
        # Get tool definition (single source of truth)
        tool_def = get_tool_definition(tool_name)
        
        # Validate parameters using tool's Pydantic model
        try:
            validated_params = tool_def.validate_params(cleaned_request.payload.parameters)
        except ValidationError as e:
            raise ValueError(f"Invalid parameters for {tool_name}: {e}")
        
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
            tool_name=tool_name,
            parameters=cleaned_request.payload.parameters,
        )
        await self.repository.add_event_to_request(session_id, request_id, request_received_event)
        cleaned_request.event_ids.append(request_received_event.event_id)
        
        try:
            # Create tool_execution_started event
            start_time = datetime.now()
            execution_started_event = ToolEvent(
                event_type="tool_execution_started",
                tool_name=tool_name,
                parameters=cleaned_request.payload.parameters,
                status="pending"
            )
            await self.repository.add_event_to_request(session_id, request_id, execution_started_event)
            cleaned_request.event_ids.append(execution_started_event.event_id)
            
            logger.info(f"Executing tool {tool_name} with validated parameters: {validated_params}")
            
            # Execute tool via tool definition (parameters already validated)
            result_data = await tool_def.implementation(
                context,
                **validated_params.model_dump()
            )
            
            # Calculate duration
            duration_ms = int((datetime.now() - start_time).total_seconds() * 1000)
            
            # Create tool_execution_completed event
            execution_completed_event = ToolEvent(
                event_type="tool_execution_completed",
                tool_name=tool_name,
                parameters=cleaned_request.payload.parameters,
                result_summary=result_data,
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
                    result=result_data,
                    events=[],
                    session_request_id=session_request_id
                ),
                timestamp=datetime.now().isoformat()
            )
            
        except Exception as e:
            logger.exception(f"Error executing tool {tool_name}: {e}")
            
            # Calculate duration
            duration_ms = int((datetime.now() - start_time).total_seconds() * 1000)
            
            # Create tool_execution_failed event
            execution_failed_event = ToolEvent(
                event_type="tool_execution_failed",
                tool_name=tool_name,
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
            tool_name=tool_name,
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
    
    async def get_session(self, request: GetSessionRequest) -> GetSessionResponse:
        """Get a session by ID.
        
        Args:
            request: GetSessionRequest with session_id
            
        Returns:
            GetSessionResponse with full session data and request counts
        """
        start_time = datetime.now()
        session_id = request.payload.session_id
        
        session = await self.repository.get_session(session_id)
        if not session:
            return GetSessionResponse(
                request_id=request.request_id,
                status=RequestStatus.FAILED,
                error=f"Session {session_id} not found",
                payload=SessionDataPayload(
                    session_id=session_id,
                    user_id="",
                    casefile_id="",
                    created_at="",
                    updated_at="",
                    active=False,
                    request_count=0,
                    event_count=0
                )
            )
        
        # SECURITY: Verify session belongs to requesting user
        if session.user_id != request.user_id:
            execution_time_ms = int((datetime.now() - start_time).total_seconds() * 1000)
            return GetSessionResponse(
                request_id=request.request_id,
                status=RequestStatus.FAILED,
                error=f"Access denied: Session {session_id} does not belong to user {request.user_id}",
                payload=SessionDataPayload(
                    session_id=session_id,
                    user_id="",
                    casefile_id="",
                    created_at="",
                    updated_at="",
                    active=False,
                    request_count=0,
                    event_count=0
                ),
                metadata={
                    "execution_time_ms": execution_time_ms,
                    "operation": "get_session",
                    "security_check": "ownership_verification_failed"
                }
            )
        
        # Count events across all requests
        event_count = 0
        for req_id in session.request_ids:
            events = await self.repository.get_request_events(session_id, req_id)
            event_count += len(events)
        
        execution_time_ms = int((datetime.now() - start_time).total_seconds() * 1000)
        
        return GetSessionResponse(
            request_id=request.request_id,
            status=RequestStatus.COMPLETED,
            payload=SessionDataPayload(
                session_id=session.session_id,
                user_id=session.user_id,
                casefile_id=session.casefile_id or "",
                created_at=session.created_at,
                updated_at=session.updated_at,
                active=session.active,
                title=None,
                request_count=len(session.request_ids),
                event_count=event_count,
                metadata={}
            ),
            metadata={
                "execution_time_ms": execution_time_ms,
                "operation": "get_session"
            }
        )
    
    async def list_sessions(self, request: ListSessionsRequest) -> ListSessionsResponse:
        """List sessions, optionally filtered by user or casefile.
        
        Args:
            request: ListSessionsRequest with optional user_id, casefile_id filters
            
        Returns:
            ListSessionsResponse with session summaries and pagination info
        """
        start_time = datetime.now()
        payload = request.payload
        
        sessions = await self.repository.list_sessions(
            user_id=payload.user_id,
            casefile_id=payload.casefile_id
        )
        
        # Filter by active status if requested
        if payload.active_only:
            sessions = [s for s in sessions if s.active]
        
        # Apply pagination
        total_count = len(sessions)
        start_idx = payload.offset
        end_idx = start_idx + payload.limit
        paginated_sessions = sessions[start_idx:end_idx]
        
        # Build summaries
        summaries = [
            SessionSummary(
                session_id=session.session_id,
                user_id=session.user_id,
                casefile_id=session.casefile_id or "",
                title=None,
                created_at=session.created_at,
                updated_at=session.updated_at,
                active=session.active,
                request_count=len(session.request_ids)
            )
            for session in paginated_sessions
        ]
        
        execution_time_ms = int((datetime.now() - start_time).total_seconds() * 1000)
        
        return ListSessionsResponse(
            request_id=request.request_id,
            status=RequestStatus.COMPLETED,
            payload=SessionListPayload(
                sessions=summaries,
                total_count=total_count,
                offset=payload.offset,
                limit=payload.limit
            ),
            metadata={
                "execution_time_ms": execution_time_ms,
                "operation": "list_sessions",
                "filters_applied": {
                    "user_id": payload.user_id,
                    "casefile_id": payload.casefile_id,
                    "active_only": payload.active_only
                }
            }
        )
    
    async def close_session(self, request: CloseSessionRequest) -> CloseSessionResponse:
        """Close a session.
        
        Args:
            request: CloseSessionRequest with session_id
            
        Returns:
            CloseSessionResponse with closure details and statistics
        """
        start_time = datetime.now()
        session_id = request.payload.session_id
        
        session = await self.repository.get_session(session_id)
        if not session:
            return CloseSessionResponse(
                request_id=request.request_id,
                status=RequestStatus.FAILED,
                error=f"Session {session_id} not found",
                payload=SessionClosedPayload(
                    session_id=session_id,
                    closed_at=datetime.now().isoformat(),
                    total_requests=0,
                    total_events=0
                )
            )
        
        # SECURITY: Verify session belongs to requesting user
        if session.user_id != request.user_id:
            execution_time_ms = int((datetime.now() - start_time).total_seconds() * 1000)
            return CloseSessionResponse(
                request_id=request.request_id,
                status=RequestStatus.FAILED,
                error=f"Access denied: Session {session_id} does not belong to user {request.user_id}",
                payload=SessionClosedPayload(
                    session_id=session_id,
                    closed_at=datetime.now().isoformat(),
                    total_requests=0,
                    total_events=0
                ),
                metadata={
                    "execution_time_ms": execution_time_ms,
                    "operation": "close_session",
                    "security_check": "ownership_verification_failed"
                }
            )
        
        # Calculate statistics
        total_requests = len(session.request_ids)
        total_events = 0
        for req_id in session.request_ids:
            events = await self.repository.get_request_events(session_id, req_id)
            total_events += len(events)
        
        # Calculate duration
        created_time = datetime.fromisoformat(session.created_at.replace('Z', '+00:00'))
        closed_time = datetime.now()
        duration_seconds = int((closed_time - created_time).total_seconds())
        
        # Update session
        session.active = False
        session.updated_at = closed_time.isoformat()
        await self.repository.update_session(session)
        
        execution_time_ms = int((datetime.now() - start_time).total_seconds() * 1000)
        
        return CloseSessionResponse(
            request_id=request.request_id,
            status=RequestStatus.COMPLETED,
            payload=SessionClosedPayload(
                session_id=session.session_id,
                closed_at=session.updated_at,
                total_requests=total_requests,
                total_events=total_events,
                duration_seconds=duration_seconds
            ),
            metadata={
                "execution_time_ms": execution_time_ms,
                "operation": "close_session",
                "user_id": session.user_id,
                "casefile_id": session.casefile_id
            }
        )
    
    async def process_tool_request_with_session_management(
        self,
        user_id: str,
        tool_name: str,
        parameters: Dict[str, Any],
        casefile_id: Optional[str] = None,
        session_token: Optional[str] = None,
        client_request_id: Optional[str] = None,
        auto_create_session: bool = True
    ) -> ToolResponse:
        """
        Process a tool request with automatic session management.
        
        This method automatically handles session creation/resumption, making it
        easier for tools to be invoked without explicit session management.
        
        Args:
            user_id: User executing the tool
            tool_name: Name of the tool to execute
            parameters: Tool parameters
            casefile_id: Optional casefile context
            session_token: Optional existing session to resume
            client_request_id: Optional client request ID
            auto_create_session: Whether to create session if none exists
            
        Returns:
            Tool response
        """
        from pydantic_ai_integration.session_manager import ensure_session_for_tool
        
        # Get or create session context
        context, session_created = await ensure_session_for_tool(
            user_id=user_id,
            tool_name=tool_name,
            casefile_id=casefile_id,
            session_token=session_token,
            client_request_id=client_request_id,
            auto_create=auto_create_session
        )
        
        # Create tool request using the session context
        tool_request = ToolRequest(
            user_id=user_id,
            session_id=context.session_id,
            payload=ToolRequestPayload(
                tool_name=tool_name,
                parameters=parameters,
                session_request_id=context.session_request_id
            )
        )
        
        # Process the tool request
        response = await self.process_tool_request(tool_request)
        
        # Add session metadata to response
        if response.metadata is None:
            response.metadata = {}
        response.metadata.update({
            "session_created": session_created,
            "session_id": context.session_id,
            "session_request_id": context.session_request_id
        })
        
        return response
