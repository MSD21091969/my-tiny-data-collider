"""
Tool session API router.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any, List, Optional
from datetime import datetime
from uuid import UUID

from ...tool_sessionservice import ToolSessionService
from ...pydantic_models.tool_session import ToolRequest, ToolResponse
from ...pydantic_models.tool_session.resume_models import SessionResumeRequest, SessionResumeResponse
from ..dependencies import get_tool_session_service, get_current_user_id, verify_casefile_access
from ...authservice import get_current_user
from ...casefileservice import CasefileService

router = APIRouter(
    prefix="/tool-sessions",
    tags=["tool-sessions"],
    responses={404: {"description": "Not found"}},
)

def get_casefile_service() -> CasefileService:
    """Get an instance of the CasefileService."""
    return CasefileService()

@router.post("/")
async def create_session(
    session_id: Optional[str] = None,
    casefile_id: Optional[str] = None,
    title: Optional[str] = None,
    service: ToolSessionService = Depends(get_tool_session_service),
    casefile_service: CasefileService = Depends(get_casefile_service),
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, str]:
    """Create or resume a tool session.
    
    Three scenarios:
    1. If session_id is provided, resume that session (requires matching user)
    2. If casefile_id is provided, create a new session for that casefile
    3. If neither is provided but title is, create a new casefile and session
    """
    user_id = current_user["user_id"]
    
    # Scenario 1: Resume existing session
    if session_id:
        try:
            # This will validate that the session exists and belongs to user
            resume_request = SessionResumeRequest(session_id=session_id)
            resume_response = await service.resume_session(user_id, resume_request)
            return {"session_id": resume_response.session_id}
        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e))
    
    # Scenario 2: Use existing casefile
    elif casefile_id:
        # Verify user has access to casefile
        try:
            casefile = await casefile_service.get_casefile(casefile_id)
            
            # Verify ownership
            if casefile["metadata"]["created_by"] != user_id and "admin" not in current_user.get("roles", []):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You do not have access to this casefile"
                )
                
            # Create new session with existing casefile
            return await service.create_session(user_id=user_id, casefile_id=casefile_id)
        except ValueError as e:
            raise HTTPException(status_code=404, detail=f"Casefile not found: {str(e)}")
    
    # Scenario 3: Create new casefile and session
    elif title:
        # Create a new casefile first
        casefile_response = await casefile_service.create_casefile(
            user_id=user_id,
            title=title,
            description=f"Casefile created on {datetime.now().isoformat()}"
        )
        
        # Then create a session for it
        new_casefile_id = casefile_response["casefile_id"]
        session_response = await service.create_session(user_id=user_id, casefile_id=new_casefile_id)
        
        # Link the session to the casefile
        await casefile_service.add_session_to_casefile(
            casefile_id=new_casefile_id,
            session_id=UUID(session_response["session_id"])
        )
        
        return {
            "session_id": session_response["session_id"],
            "casefile_id": new_casefile_id
        }
    
    # Error if no parameters provided
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either session_id, casefile_id, or title must be provided"
        )

@router.post("/execute")
async def execute_tool(
    request: ToolRequest,
    service: ToolSessionService = Depends(get_tool_session_service),
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> ToolResponse:
    """Execute a tool in a session."""
    try:
        # Verify session belongs to this user
        session = await service.get_session(str(request.session_id))
        if session["user_id"] != current_user["user_id"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have access to this session"
            )
            
        # If request has casefile context, verify user has access
        if request.payload.casefile_id:
            verify_casefile_access(request.payload.casefile_id, current_user)
            
        return await service.process_tool_request(request)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Tool execution failed: {str(e)}")

@router.get("/{session_id}")
async def get_session(
    session_id: str,
    service: ToolSessionService = Depends(get_tool_session_service),
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get details of a tool session."""
    try:
        session = await service.get_session(session_id)
        
        # Verify session belongs to this user
        if session["user_id"] != current_user["user_id"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have access to this session"
            )
            
        return session
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/")
async def list_sessions(
    casefile_id: Optional[str] = None,
    service: ToolSessionService = Depends(get_tool_session_service),
    # current_user: Dict[str, Any] = Depends(get_current_user)  # TEMPORARILY DISABLED
) -> List[Dict[str, Any]]:
    """List tool sessions for the current user, optionally filtered by casefile."""
    # Use mock user for now
    user_id = "sam123"
    
    # Skip casefile access verification for now
    # if casefile_id:
    #     verify_casefile_access(casefile_id, current_user)
        
    return await service.list_sessions(user_id=user_id, casefile_id=casefile_id)

@router.post("/{session_id}/close")
async def close_session(
    session_id: str,
    service: ToolSessionService = Depends(get_tool_session_service),
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """Close a tool session."""
    try:
        # Verify session belongs to this user
        session = await service.get_session(session_id)
        if session["user_id"] != current_user["user_id"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have access to this session"
            )
            
        return await service.close_session(session_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
        
@router.post("/resume", response_model=SessionResumeResponse)
async def resume_session(
    request: SessionResumeRequest,
    service: ToolSessionService = Depends(get_tool_session_service),
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> SessionResumeResponse:
    """Resume a previous tool session."""
    try:
        return await service.resume_session(current_user["user_id"], request)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))