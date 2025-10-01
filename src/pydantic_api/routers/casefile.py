"""
Casefile API router.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any, List, Optional

from ...casefileservice import CasefileService
from ...authservice import get_current_user

router = APIRouter(
    prefix="/casefiles",
    tags=["casefiles"],
    responses={404: {"description": "Not found"}},
)

def get_casefile_service() -> CasefileService:
    """Get an instance of the CasefileService."""
    return CasefileService()

@router.post("/")
async def create_casefile(
    title: str,
    description: str = "",
    tags: Optional[List[str]] = None,
    service: CasefileService = Depends(get_casefile_service),
    # user_id: str = Depends(get_current_user_id)  # TEMPORARILY DISABLED
) -> Dict[str, str]:
    """Create a new casefile."""
    # Use mock user for now
    user_id = "sam123"
    
    return await service.create_casefile(
        user_id=user_id,
        title=title,
        description=description,
        tags=tags or []
    )

@router.get("/{casefile_id}")
async def get_casefile(
    casefile_id: str,
    service: CasefileService = Depends(get_casefile_service),
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get details of a casefile."""
    try:
        casefile = await service.get_casefile(casefile_id)
        
        # Verify casefile belongs to this user or user is admin
        if (casefile["metadata"]["created_by"] != current_user["user_id"] and
            "admin" not in current_user.get("roles", [])):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have access to this casefile"
            )
            
        return casefile
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.put("/{casefile_id}")
async def update_casefile(
    casefile_id: str,
    updates: Dict[str, Any],
    service: CasefileService = Depends(get_casefile_service),
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """Update a casefile."""
    try:
        # First get casefile to check ownership
        casefile = await service.get_casefile(casefile_id)
        
        # Verify casefile belongs to this user or user is admin
        if (casefile["metadata"]["created_by"] != current_user["user_id"] and
            "admin" not in current_user.get("roles", [])):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have access to this casefile"
            )
            
        return await service.update_casefile(casefile_id, updates)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/")
async def list_casefiles(
    service: CasefileService = Depends(get_casefile_service),
    # current_user: Dict[str, Any] = Depends(get_current_user)  # TEMPORARILY DISABLED
) -> List[Dict[str, Any]]:
    """List casefiles for the current user."""
    # Use mock user for now
    user_id = "sam123"
    
    return await service.list_casefiles(user_id=user_id)

@router.delete("/{casefile_id}")
async def delete_casefile(
    casefile_id: str,
    service: CasefileService = Depends(get_casefile_service),
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """Delete a casefile."""
    try:
        # First get casefile to check ownership
        casefile = await service.get_casefile(casefile_id)
        
        # Verify casefile belongs to this user or user is admin
        if (casefile["metadata"]["created_by"] != current_user["user_id"] and
            "admin" not in current_user.get("roles", [])):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have access to this casefile"
            )
            
        return await service.delete_casefile(casefile_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))