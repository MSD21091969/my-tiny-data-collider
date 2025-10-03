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
from ...pydantic_models.casefile.acl_models import (
    PermissionLevel,
    PermissionListResponse,
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
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> CreateCasefileResponse:
    """Create a new casefile."""
    user_id = current_user["user_id"]
    
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
    
    # Check ACL permissions (supports owner + shared access)
    casefile = response.payload.casefile
    if casefile.acl:
        if not casefile.acl.can_read(user_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to view this casefile"
            )
    else:
        # Legacy casefile without ACL - check owner only
        if casefile.metadata.created_by != user_id and "admin" not in current_user.get("roles", []):
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
    
    # First get casefile to check permissions
    get_request = GetCasefileRequest(
        user_id=user_id,
        operation="get_casefile",
        payload={"casefile_id": casefile_id}
    )
    get_response = await service.get_casefile(get_request)
    
    if get_response.status.value == "failed":
        raise HTTPException(status_code=404, detail=get_response.error or "Casefile not found")
    
    # Check ACL permissions (supports owner + editors)
    casefile = get_response.payload.casefile
    if casefile.acl:
        if not casefile.acl.can_write(user_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to edit this casefile"
            )
    else:
        # Legacy casefile without ACL - check owner only
        if casefile.metadata.created_by != user_id and "admin" not in current_user.get("roles", []):
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
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> ListCasefilesResponse:
    """List casefiles for the current user."""
    user_id = current_user["user_id"]
    
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
    
    # First get casefile to check permissions
    get_request = GetCasefileRequest(
        user_id=user_id,
        operation="get_casefile",
        payload={"casefile_id": casefile_id}
    )
    get_response = await service.get_casefile(get_request)
    
    if get_response.status.value == "failed":
        raise HTTPException(status_code=404, detail=get_response.error or "Casefile not found")
    
    # Check ACL permissions (only owner can delete)
    casefile = get_response.payload.casefile
    if casefile.acl:
        if not casefile.acl.can_delete(user_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only the owner can delete this casefile"
            )
    else:
        # Legacy casefile without ACL - check owner only
        if casefile.metadata.created_by != user_id and "admin" not in current_user.get("roles", []):
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


# ============================================================================
# ACL (Access Control List) Endpoints
# ============================================================================

@router.post("/{casefile_id}/share")
async def share_casefile(
    casefile_id: str,
    target_user_id: str,
    permission: PermissionLevel,
    expires_at: Optional[str] = None,
    notes: Optional[str] = None,
    service: CasefileService = Depends(get_casefile_service),
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """Grant permission to a user on a casefile.
    
    Args:
        casefile_id: Casefile ID
        target_user_id: User to grant permission to
        permission: Permission level (viewer, editor, admin)
        expires_at: Optional expiration timestamp (ISO format)
        notes: Optional notes about this permission
        
    Returns:
        Success message with permission details
    """
    user_id = current_user["user_id"]
    
    try:
        success = await service.grant_permission(
            casefile_id=casefile_id,
            granting_user_id=user_id,
            target_user_id=target_user_id,
            permission=permission,
            expires_at=expires_at,
            notes=notes
        )
        
        if success:
            return {
                "success": True,
                "message": f"Granted {permission.value} permission to user {target_user_id}",
                "casefile_id": casefile_id,
                "target_user_id": target_user_id,
                "permission": permission.value,
                "expires_at": expires_at
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to grant permission"
            )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )


@router.delete("/{casefile_id}/share/{target_user_id}")
async def revoke_casefile_permission(
    casefile_id: str,
    target_user_id: str,
    service: CasefileService = Depends(get_casefile_service),
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """Revoke permission from a user on a casefile.
    
    Args:
        casefile_id: Casefile ID
        target_user_id: User to revoke permission from
        
    Returns:
        Success message
    """
    user_id = current_user["user_id"]
    
    try:
        success = await service.revoke_permission(
            casefile_id=casefile_id,
            revoking_user_id=user_id,
            target_user_id=target_user_id
        )
        
        if success:
            return {
                "success": True,
                "message": f"Revoked permission from user {target_user_id}",
                "casefile_id": casefile_id,
                "target_user_id": target_user_id
            }
        else:
            return {
                "success": False,
                "message": f"No permission found for user {target_user_id}",
                "casefile_id": casefile_id,
                "target_user_id": target_user_id
            }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )


@router.get("/{casefile_id}/permissions", response_model=PermissionListResponse)
async def get_casefile_permissions(
    casefile_id: str,
    service: CasefileService = Depends(get_casefile_service),
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> PermissionListResponse:
    """Get all permissions for a casefile.
    
    Args:
        casefile_id: Casefile ID
        
    Returns:
        List of all permissions on the casefile
    """
    user_id = current_user["user_id"]
    
    try:
        acl = await service.list_permissions(
            casefile_id=casefile_id,
            requesting_user_id=user_id
        )
        
        return PermissionListResponse(
            casefile_id=casefile_id,
            owner_id=acl.owner_id,
            public_access=acl.public_access,
            permissions=acl.permissions,
            total_users=len(acl.permissions)
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )


@router.get("/{casefile_id}/my-permission")
async def get_my_casefile_permission(
    casefile_id: str,
    service: CasefileService = Depends(get_casefile_service),
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get current user's permission level on a casefile.
    
    Args:
        casefile_id: Casefile ID
        
    Returns:
        User's permission level and capabilities
    """
    user_id = current_user["user_id"]
    
    try:
        acl = await service.list_permissions(
            casefile_id=casefile_id,
            requesting_user_id=user_id
        )
        
        user_permission = acl.get_user_permission(user_id)
        
        return {
            "casefile_id": casefile_id,
            "user_id": user_id,
            "permission": user_permission.value,
            "can_read": acl.can_read(user_id),
            "can_write": acl.can_write(user_id),
            "can_share": acl.can_share(user_id),
            "can_delete": acl.can_delete(user_id),
            "is_owner": user_id == acl.owner_id
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )