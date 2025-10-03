"""
Casefile API router.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any, List, Optional

from ...casefileservice import CasefileService
from ...pydantic_models.casefile.crud_models import (
    CreateCasefileRequest,
    CreateCasefileResponse,
    DeleteCasefileRequest,
    DeleteCasefileResponse,
    GetCasefileRequest,
    GetCasefileResponse,
    ListCasefilesRequest,
    ListCasefilesResponse,
    UpdateCasefileRequest,
    UpdateCasefileResponse,
)
from ...authservice import get_current_user

router = APIRouter(
    prefix="/casefiles",
    tags=["casefiles"],
    responses={404: {"description": "Not found"}},
)

def get_casefile_service() -> CasefileService:
    """Get an instance of the CasefileService."""
    return CasefileService()

@router.post("/", response_model=CreateCasefileResponse)
async def create_casefile(
    title: str,
    description: str = "",
    tags: Optional[List[str]] = None,
    service: CasefileService = Depends(get_casefile_service),
    # user_id: str = Depends(get_current_user_id)  # TEMPORARILY DISABLED
) -> CreateCasefileResponse:
    """Create a new casefile."""
    # Use mock user for now
    user_id = "sam123"
    
    request = CreateCasefileRequest(
        user_id=user_id,
        operation="create_casefile",
        payload={
            "title": title,
            "description": description,
            "tags": tags or []
        }
    )
    
    return await service.create_casefile(request)

@router.get("/{casefile_id}", response_model=GetCasefileResponse)
async def get_casefile(
    casefile_id: str,
    service: CasefileService = Depends(get_casefile_service),
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> GetCasefileResponse:
    """Get details of a casefile."""
    user_id = current_user["user_id"]
    
    request = GetCasefileRequest(
        user_id=user_id,
        operation="get_casefile",
        payload={"casefile_id": casefile_id}
    )
    
    response = await service.get_casefile(request)
    
    if response.status.value == "failed":
        raise HTTPException(status_code=404, detail=response.error or "Casefile not found")
    
    # Verify casefile belongs to this user or user is admin
    if (response.payload.casefile.metadata.created_by != user_id and
        "admin" not in current_user.get("roles", [])):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this casefile"
        )
        
    return response

@router.put("/{casefile_id}", response_model=UpdateCasefileResponse)
async def update_casefile(
    casefile_id: str,
    title: Optional[str] = None,
    description: Optional[str] = None,
    tags: Optional[List[str]] = None,
    notes: Optional[str] = None,
    service: CasefileService = Depends(get_casefile_service),
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> UpdateCasefileResponse:
    """Update a casefile."""
    user_id = current_user["user_id"]
    
    # First get casefile to check ownership
    get_request = GetCasefileRequest(
        user_id=user_id,
        operation="get_casefile",
        payload={"casefile_id": casefile_id}
    )
    get_response = await service.get_casefile(get_request)
    
    if get_response.status.value == "failed":
        raise HTTPException(status_code=404, detail=get_response.error or "Casefile not found")
    
    # Verify casefile belongs to this user or user is admin
    if (get_response.payload.casefile.metadata.created_by != user_id and
        "admin" not in current_user.get("roles", [])):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this casefile"
        )
    
    # Build update request
    update_request = UpdateCasefileRequest(
        user_id=user_id,
        operation="update_casefile",
        payload={
            "casefile_id": casefile_id,
            "title": title,
            "description": description,
            "tags": tags,
            "notes": notes
        }
    )
    
    return await service.update_casefile(update_request)

@router.get("/", response_model=ListCasefilesResponse)
async def list_casefiles(
    limit: int = 50,
    offset: int = 0,
    service: CasefileService = Depends(get_casefile_service),
    # current_user: Dict[str, Any] = Depends(get_current_user)  # TEMPORARILY DISABLED
) -> ListCasefilesResponse:
    """List casefiles for the current user."""
    # Use mock user for now
    user_id = "sam123"
    
    request = ListCasefilesRequest(
        user_id=user_id,
        operation="list_casefiles",
        payload={
            "user_id": user_id,
            "limit": limit,
            "offset": offset
        }
    )
    
    return await service.list_casefiles(request)

@router.delete("/{casefile_id}", response_model=DeleteCasefileResponse)
async def delete_casefile(
    casefile_id: str,
    service: CasefileService = Depends(get_casefile_service),
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> DeleteCasefileResponse:
    """Delete a casefile."""
    user_id = current_user["user_id"]
    
    # First get casefile to check ownership
    get_request = GetCasefileRequest(
        user_id=user_id,
        operation="get_casefile",
        payload={"casefile_id": casefile_id}
    )
    get_response = await service.get_casefile(get_request)
    
    if get_response.status.value == "failed":
        raise HTTPException(status_code=404, detail=get_response.error or "Casefile not found")
    
    # Verify casefile belongs to this user or user is admin
    if (get_response.payload.casefile.metadata.created_by != user_id and
        "admin" not in current_user.get("roles", [])):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this casefile"
        )
    
    # Delete casefile
    delete_request = DeleteCasefileRequest(
        user_id=user_id,
        operation="delete_casefile",
        payload={"casefile_id": casefile_id}
    )
    
    return await service.delete_casefile(delete_request)