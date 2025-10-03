"""
Tool session API router.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any, List, Optional

from ...tool_sessionservice import ToolSessionService
from ...pydantic_models.casefile.crud_models import GetCasefileRequest
from ...pydantic_models.tool_session import ToolRequest, ToolResponse
from ...pydantic_models.tool_session.session_models import (
    CloseSessionRequest,
    CloseSessionResponse,
    CreateSessionRequest,
    CreateSessionResponse,
    GetSessionRequest,
    GetSessionResponse,
    ListSessionsRequest,
    ListSessionsResponse,
)
from ...pydantic_ai_integration.tool_decorator import (
    get_registered_tools,
    get_tool_definition,
    list_tools_by_category,
)
from ..dependencies import get_tool_session_service, verify_casefile_access
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

@router.post("/", response_model=CreateSessionResponse)
async def create_session(
    casefile_id: str,  # Make casefile_id required
    service: ToolSessionService = Depends(get_tool_session_service),
    casefile_service: CasefileService = Depends(get_casefile_service),
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> CreateSessionResponse:
    """Create a new tool session.
    
    Requires casefile_id - sessions must be associated with a casefile.
    
    Note: Session "resume" is implicit - simply use the existing session_id
    in subsequent ToolRequest calls. No need to explicitly "resume" a session.
    """
    user_id = current_user["user_id"]
    
    # Verify user has access to casefile
    try:
        get_casefile_request = GetCasefileRequest(
            user_id=user_id,
            operation="get_casefile",
            payload={"casefile_id": casefile_id}
        )
        casefile_response = await casefile_service.get_casefile(get_casefile_request)
        
        if casefile_response.status.value == "failed":
            raise HTTPException(status_code=404, detail=casefile_response.error or "Casefile not found")
        
        casefile = casefile_response.payload.casefile
        
        # Verify ownership
        if casefile.metadata.created_by != user_id and "admin" not in current_user.get("roles", []):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have access to this casefile"
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error verifying casefile: {str(e)}")
    
    # Create new session for casefile
    create_request = CreateSessionRequest(
        user_id=user_id,
        operation="create_session",
        payload={"casefile_id": casefile_id}
    )
    return await service.create_session(create_request)

@router.post("/execute")
async def execute_tool(
    request: ToolRequest,
    service: ToolSessionService = Depends(get_tool_session_service),
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> ToolResponse:
    """Execute a tool in a session."""
    try:
        user_id = current_user["user_id"]
        
        # Verify session belongs to this user
        get_request = GetSessionRequest(
            user_id=user_id,
            operation="get_session",
            payload={"session_id": str(request.session_id)}
        )
        
        get_response = await service.get_session(get_request)
        
        if get_response.status.value == "failed":
            raise HTTPException(status_code=404, detail=get_response.error or "Session not found")
        
        if get_response.payload.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have access to this session"
            )
            
        # If request has casefile context, verify user has access
        if request.payload.casefile_id:
            verify_casefile_access(request.payload.casefile_id, current_user)
            
        return await service.process_tool_request(request)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Tool execution failed: {str(e)}")

@router.get("/{session_id}", response_model=GetSessionResponse)
async def get_session(
    session_id: str,
    service: ToolSessionService = Depends(get_tool_session_service),
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> GetSessionResponse:
    """Get details of a tool session."""
    user_id = current_user["user_id"]
    
    request = GetSessionRequest(
        user_id=user_id,
        operation="get_session",
        payload={"session_id": session_id}
    )
    
    response = await service.get_session(request)
    
    if response.status.value == "failed":
        raise HTTPException(status_code=404, detail=response.error or "Session not found")
    
    # Verify session belongs to this user
    if response.payload.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this session"
        )
        
    return response

@router.get("/", response_model=ListSessionsResponse)
async def list_sessions(
    casefile_id: Optional[str] = None,
    active_only: bool = True,
    limit: int = 50,
    offset: int = 0,
    service: ToolSessionService = Depends(get_tool_session_service),
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> ListSessionsResponse:
    """List tool sessions for the current user, optionally filtered by casefile."""
    user_id = current_user["user_id"]
    
    # Skip casefile access verification for now
    # if casefile_id:
    #     verify_casefile_access(casefile_id, current_user)
    
    request = ListSessionsRequest(
        user_id=user_id,
        operation="list_sessions",
        payload={
            "user_id": user_id,
            "casefile_id": casefile_id,
            "active_only": active_only,
            "limit": limit,
            "offset": offset
        }
    )
        
    return await service.list_sessions(request)

@router.post("/{session_id}/close", response_model=CloseSessionResponse)
async def close_session(
    session_id: str,
    service: ToolSessionService = Depends(get_tool_session_service),
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> CloseSessionResponse:
    """Close a tool session."""
    user_id = current_user["user_id"]
    
    # First verify session belongs to this user
    get_request = GetSessionRequest(
        user_id=user_id,
        operation="get_session",
        payload={"session_id": session_id}
    )
    
    get_response = await service.get_session(get_request)
    
    if get_response.status.value == "failed":
        raise HTTPException(status_code=404, detail=get_response.error or "Session not found")
    
    if get_response.payload.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this session"
        )
    
    # Now close the session
    close_request = CloseSessionRequest(
        user_id=user_id,
        operation="close_session",
        payload={"session_id": session_id}
    )
    
    return await service.close_session(close_request)


# ============================================================================
# TOOL DISCOVERY ENDPOINTS (query MANAGED_TOOLS registry)
# ============================================================================

@router.get("/tools", response_model=Dict[str, Any])
async def list_available_tools(
    category: Optional[str] = None,
    enabled_only: bool = True
) -> Dict[str, Any]:
    """
    List available tools from MANAGED_TOOLS registry.
    
    Query params:
    - category: Filter by category (e.g., "examples", "documents")
    - enabled_only: Only show enabled tools (default: true)
    
    Returns:
        Dictionary with tools array and count
    """
    if category:
        tools = list_tools_by_category(category, enabled_only)
        tool_dict = {t.metadata.name: t for t in tools}
    else:
        tool_dict = get_registered_tools()
        if enabled_only:
            tool_dict = {
                name: tool for name, tool in tool_dict.items()
                if tool.business_rules.enabled
            }
    
    return {
        "tools": [
            tool.to_discovery_format()
            for tool in tool_dict.values()
        ],
        "count": len(tool_dict)
    }


@router.get("/tools/{tool_name}", response_model=Dict[str, Any])
async def get_tool_info(tool_name: str) -> Dict[str, Any]:
    """
    Get detailed information about a specific tool.
    
    Includes:
    - Metadata (name, description, category)
    - Business rules (permissions, timeout)
    - Parameter schema (OpenAPI format)
    
    Args:
        tool_name: Name of the tool
        
    Returns:
        Tool definition in discovery format
        
    Raises:
        HTTPException: If tool not found
    """
    tool = get_tool_definition(tool_name)
    if not tool:
        raise HTTPException(
            status_code=404,
            detail=f"Tool '{tool_name}' not found"
        )
    
    return tool.to_discovery_format()


@router.get("/tools/{tool_name}/schema", response_model=Dict[str, Any])
async def get_tool_parameter_schema(tool_name: str) -> Dict[str, Any]:
    """
    Get OpenAPI parameter schema for a tool.
    
    Used by clients to generate forms or validate input.
    
    Args:
        tool_name: Name of the tool
        
    Returns:
        Dictionary with tool_name and schema
        
    Raises:
        HTTPException: If tool not found
    """
    tool = get_tool_definition(tool_name)
    if not tool:
        raise HTTPException(
            status_code=404,
            detail=f"Tool '{tool_name}' not found"
        )
    
    return {
        "tool_name": tool_name,
        "schema": tool.get_openapi_schema()
    }