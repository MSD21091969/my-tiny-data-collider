"""Casefile API router."""

from __future__ import annotations

from typing import Any, cast

from fastapi import APIRouter, Depends, HTTPException, status

from authservice import get_current_user
from coreservice.request_hub import RequestHub
from src.pydantic_models.base.envelopes import BaseResponse
from src.pydantic_models.base.types import RequestStatus
from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from src.pydantic_models.base.envelopes import BaseResponse
from src.pydantic_models.base.types import RequestStatus
from src.pydantic_models.operations.casefile_ops import (
    CheckPermissionPayload,
    CheckPermissionRequest,
    CheckPermissionResponse,
    CreateCasefilePayload,
    CreateCasefileRequest,
    CreateCasefileResponse,
    DeleteCasefilePayload,
    DeleteCasefileRequest,
    DeleteCasefileResponse,
    GetCasefilePayload,
    GetCasefileRequest,
    GetCasefileResponse,
    GrantPermissionPayload,
    GrantPermissionRequest,
    GrantPermissionResponse,
    ListCasefilesPayload,
    ListCasefilesRequest,
    ListCasefilesResponse,
    ListPermissionsPayload,
    ListPermissionsRequest,
    ListPermissionsResponse,
    PermissionLevel,
    RevokePermissionPayload,
    RevokePermissionRequest,
    RevokePermissionResponse,
    UpdateCasefilePayload,
    UpdateCasefileRequest,
    UpdateCasefileResponse,
)

from ..dependencies import get_request_hub

router = APIRouter(
    prefix="/casefiles",
    tags=["casefiles"],
    responses={404: {"description": "Not found"}},
)


def _raise_for_failure(
    response: BaseResponse[Any], *, default_status: int = status.HTTP_400_BAD_REQUEST
) -> None:
    if response.status is RequestStatus.FAILED:
        detail = response.error or "Request failed"
        lowered = detail.lower()
        if "not found" in lowered:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail)
        if "permission" in lowered or "access" in lowered:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=detail)
        raise HTTPException(status_code=default_status, detail=detail)


def _context_requirements(include_casefile: bool, session_id: str | None) -> list[str]:
    requirements: list[str] = []
    if include_casefile:
        requirements.append("casefile")
    if session_id:
        requirements.append("session")
    return requirements


@router.post("/", response_model=CreateCasefileResponse)
async def create_casefile(
    title: str,
    description: str = "",
    tags: list[str] | None = None,
    hub: RequestHub = Depends(get_request_hub),
    current_user: dict[str, Any] = Depends(get_current_user),
) -> CreateCasefileResponse:
    """Create a new casefile via RequestHub with automatic hooks."""
    user_id = current_user["user_id"]
    session_id: str | None = current_user.get("session_id")

    request = CreateCasefileRequest(
        user_id=user_id,
        session_id=session_id,
        operation="create_casefile",
        payload=CreateCasefilePayload(title=title, description=description, tags=tags or []),
        hooks=["metrics", "audit"],
        context_requirements=_context_requirements(False, session_id),
        metadata={"source": "fastapi", "endpoint": "/casefiles"},
    )
    response = cast(CreateCasefileResponse, await hub.dispatch(request))
    _raise_for_failure(response)
    return response


@router.post("/hub", response_model=CreateCasefileResponse)
async def create_casefile_via_hub(
    title: str,
    description: str = "",
    tags: list[str] | None = None,
    enable_hooks: bool = True,
    hub: RequestHub = Depends(get_request_hub),
    current_user: dict[str, Any] = Depends(get_current_user),
) -> CreateCasefileResponse:
    """Create a new casefile via RequestHub with hook execution and context enrichment."""
    user_id = current_user["user_id"]
    session_id: str | None = current_user.get("session_id")

    request = CreateCasefileRequest(
        user_id=user_id,
        session_id=session_id,
        operation="create_casefile",
        payload=CreateCasefilePayload(title=title, description=description, tags=tags or []),
        hooks=["metrics", "audit"] if enable_hooks else [],
        context_requirements=_context_requirements(False, session_id),
        policy_hints={"pattern": "default"},
        metadata={
            "source": "fastapi",
            "endpoint": "/casefiles/hub",
            "hooks_enabled": enable_hooks,
        },
    )
    response = cast(CreateCasefileResponse, await hub.dispatch(request))
    _raise_for_failure(response)
    return response


@router.get("/{casefile_id}", response_model=GetCasefileResponse)
async def get_casefile(
    casefile_id: str,
    hub: RequestHub = Depends(get_request_hub),
    current_user: dict[str, Any] = Depends(get_current_user),
) -> GetCasefileResponse:
    """Get details of a casefile via RequestHub."""
    user_id = current_user["user_id"]
    session_id: str | None = current_user.get("session_id")

    request = GetCasefileRequest(
        user_id=user_id,
        session_id=session_id,
        operation="get_casefile",
        payload=GetCasefilePayload(casefile_id=casefile_id),
        hooks=["metrics", "audit"],
        context_requirements=_context_requirements(True, session_id),
        metadata={"source": "fastapi", "endpoint": f"/casefiles/{casefile_id}"},
    )
    response = cast(GetCasefileResponse, await hub.dispatch(request))
    _raise_for_failure(response, default_status=status.HTTP_404_NOT_FOUND)

    casefile = response.payload.casefile
    if casefile.acl:
        if not casefile.acl.can_read(user_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to view this casefile",
            )
    elif casefile.metadata.created_by != user_id and "admin" not in current_user.get("roles", []):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this casefile",
        )

    return response


@router.put("/{casefile_id}", response_model=UpdateCasefileResponse)
async def update_casefile(
    casefile_id: str,
    title: str | None = None,
    description: str | None = None,
    tags: list[str] | None = None,
    notes: str | None = None,
    hub: RequestHub = Depends(get_request_hub),
    current_user: dict[str, Any] = Depends(get_current_user),
) -> UpdateCasefileResponse:
    """Update a casefile via RequestHub."""
    user_id = current_user["user_id"]
    session_id: str | None = current_user.get("session_id")

    preflight_request = GetCasefileRequest(
        user_id=user_id,
        session_id=session_id,
        operation="get_casefile",
        payload=GetCasefilePayload(casefile_id=casefile_id),
        hooks=["metrics", "audit"],
        context_requirements=_context_requirements(True, session_id),
        metadata={"source": "fastapi", "endpoint": f"/casefiles/{casefile_id}"},
    )
    preflight_response = cast(GetCasefileResponse, await hub.dispatch(preflight_request))
    _raise_for_failure(preflight_response, default_status=status.HTTP_404_NOT_FOUND)

    casefile = preflight_response.payload.casefile
    if casefile.acl:
        if not casefile.acl.can_write(user_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to edit this casefile",
            )
    elif casefile.metadata.created_by != user_id and "admin" not in current_user.get("roles", []):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this casefile",
        )

    update_request = UpdateCasefileRequest(
        user_id=user_id,
        session_id=session_id,
        operation="update_casefile",
        payload=UpdateCasefilePayload(
            casefile_id=casefile_id,
            title=title,
            description=description,
            tags=tags,
            notes=notes,
        ),
        hooks=["metrics", "audit"],
        context_requirements=_context_requirements(True, session_id),
        metadata={"source": "fastapi", "endpoint": f"/casefiles/{casefile_id}"},
    )
    response = cast(UpdateCasefileResponse, await hub.dispatch(update_request))
    _raise_for_failure(response)
    return response


@router.get("/", response_model=ListCasefilesResponse)
async def list_casefiles(
    limit: int = 50,
    offset: int = 0,
    hub: RequestHub = Depends(get_request_hub),
    current_user: dict[str, Any] = Depends(get_current_user),
) -> ListCasefilesResponse:
    """List casefiles for the current user via RequestHub."""
    user_id = current_user["user_id"]
    session_id: str | None = current_user.get("session_id")

    request = ListCasefilesRequest(
        user_id=user_id,
        session_id=session_id,
        operation="list_casefiles",
        payload=ListCasefilesPayload(user_id=user_id, limit=limit, offset=offset),
        hooks=["metrics", "audit"],
        context_requirements=_context_requirements(False, session_id),
        metadata={"source": "fastapi", "endpoint": "/casefiles"},
    )
    response = cast(ListCasefilesResponse, await hub.dispatch(request))
    _raise_for_failure(response)
    return response


@router.delete("/{casefile_id}", response_model=DeleteCasefileResponse)
async def delete_casefile(
    casefile_id: str,
    hub: RequestHub = Depends(get_request_hub),
    current_user: dict[str, Any] = Depends(get_current_user),
) -> DeleteCasefileResponse:
    """Delete a casefile via RequestHub."""
    user_id = current_user["user_id"]
    session_id: str | None = current_user.get("session_id")

    preflight_request = GetCasefileRequest(
        user_id=user_id,
        session_id=session_id,
        operation="get_casefile",
        payload=GetCasefilePayload(casefile_id=casefile_id),
        hooks=["metrics", "audit"],
        context_requirements=_context_requirements(True, session_id),
        metadata={"source": "fastapi", "endpoint": f"/casefiles/{casefile_id}"},
    )
    preflight_response = cast(GetCasefileResponse, await hub.dispatch(preflight_request))
    _raise_for_failure(preflight_response, default_status=status.HTTP_404_NOT_FOUND)

    casefile = preflight_response.payload.casefile
    if casefile.acl:
        if not casefile.acl.can_delete(user_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only the owner can delete this casefile",
            )
    elif casefile.metadata.created_by != user_id and "admin" not in current_user.get("roles", []):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this casefile",
        )

    delete_request = DeleteCasefileRequest(
        user_id=user_id,
        session_id=session_id,
        operation="delete_casefile",
        payload=DeleteCasefilePayload(casefile_id=casefile_id, confirm=True),
        hooks=["metrics", "audit"],
        context_requirements=_context_requirements(True, session_id),
        metadata={"source": "fastapi", "endpoint": f"/casefiles/{casefile_id}"},
    )
    response = cast(DeleteCasefileResponse, await hub.dispatch(delete_request))
    _raise_for_failure(response)
    return response


@router.post("/{casefile_id}/share", response_model=GrantPermissionResponse)
async def share_casefile(
    casefile_id: str,
    target_user_id: str,
    permission: PermissionLevel,
    expires_at: str | None = None,
    notes: str | None = None,
    hub: RequestHub = Depends(get_request_hub),
    current_user: dict[str, Any] = Depends(get_current_user),
) -> GrantPermissionResponse:
    """Grant permission to a user on a casefile via RequestHub."""
    user_id = current_user["user_id"]
    session_id: str | None = current_user.get("session_id")

    request = GrantPermissionRequest(
        user_id=user_id,
        session_id=session_id,
        operation="grant_permission",
        payload=GrantPermissionPayload(
            casefile_id=casefile_id,
            target_user_id=target_user_id,
            permission=permission,
            expires_at=expires_at,
            notes=notes,
        ),
        hooks=["metrics", "audit"],
        context_requirements=_context_requirements(True, session_id),
        metadata={"source": "fastapi", "endpoint": f"/casefiles/{casefile_id}/share"},
    )
    response = cast(GrantPermissionResponse, await hub.dispatch(request))
    _raise_for_failure(response, default_status=status.HTTP_403_FORBIDDEN)
    return response


@router.delete("/{casefile_id}/share/{target_user_id}", response_model=RevokePermissionResponse)
async def revoke_casefile_permission(
    casefile_id: str,
    target_user_id: str,
    hub: RequestHub = Depends(get_request_hub),
    current_user: dict[str, Any] = Depends(get_current_user),
) -> RevokePermissionResponse:
    """Revoke permission from a user on a casefile via RequestHub."""
    user_id = current_user["user_id"]
    session_id: str | None = current_user.get("session_id")

    request = RevokePermissionRequest(
        user_id=user_id,
        session_id=session_id,
        operation="revoke_permission",
        payload=RevokePermissionPayload(casefile_id=casefile_id, target_user_id=target_user_id),
        hooks=["metrics", "audit"],
        context_requirements=_context_requirements(True, session_id),
        metadata={
            "source": "fastapi",
            "endpoint": f"/casefiles/{casefile_id}/share/{target_user_id}",
        },
    )
    response = cast(RevokePermissionResponse, await hub.dispatch(request))
    _raise_for_failure(response, default_status=status.HTTP_403_FORBIDDEN)
    return response


@router.get("/{casefile_id}/permissions", response_model=ListPermissionsResponse)
async def get_casefile_permissions(
    casefile_id: str,
    hub: RequestHub = Depends(get_request_hub),
    current_user: dict[str, Any] = Depends(get_current_user),
) -> ListPermissionsResponse:
    """Get all permissions for a casefile via RequestHub."""
    user_id = current_user["user_id"]
    session_id: str | None = current_user.get("session_id")

    request = ListPermissionsRequest(
        user_id=user_id,
        session_id=session_id,
        operation="list_permissions",
        payload=ListPermissionsPayload(casefile_id=casefile_id),
        hooks=["metrics", "audit"],
        context_requirements=_context_requirements(True, session_id),
        metadata={"source": "fastapi", "endpoint": f"/casefiles/{casefile_id}/permissions"},
    )
    response = cast(ListPermissionsResponse, await hub.dispatch(request))
    _raise_for_failure(response, default_status=status.HTTP_404_NOT_FOUND)
    return response


@router.get("/{casefile_id}/my-permission", response_model=CheckPermissionResponse)
async def get_my_casefile_permission(
    casefile_id: str,
    hub: RequestHub = Depends(get_request_hub),
    current_user: dict[str, Any] = Depends(get_current_user),
) -> CheckPermissionResponse:
    """Get current user's permission level on a casefile via RequestHub."""
    user_id = current_user["user_id"]
    session_id: str | None = current_user.get("session_id")

    request = CheckPermissionRequest(
        user_id=user_id,
        session_id=session_id,
        operation="check_permission",
        payload=CheckPermissionPayload(
            casefile_id=casefile_id,
            user_id=user_id,
            required_permission=PermissionLevel.VIEWER,
        ),
        hooks=["metrics", "audit"],
        context_requirements=_context_requirements(True, session_id),
        metadata={"source": "fastapi", "endpoint": f"/casefiles/{casefile_id}/my-permission"},
    )
    response = cast(CheckPermissionResponse, await hub.dispatch(request))
    _raise_for_failure(response, default_status=status.HTTP_403_FORBIDDEN)
    return response
