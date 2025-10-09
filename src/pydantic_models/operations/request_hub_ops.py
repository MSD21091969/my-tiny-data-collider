"""RequestHub-specific DTOs for composite workflows."""

from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field

from ..base.envelopes import BaseRequest, BaseResponse


class CreateCasefileWithSessionPayload(BaseModel):
    """Payload for composite workflow that creates a casefile and session."""

    title: str = Field(..., min_length=1, max_length=200, description="Casefile title")
    description: Optional[str] = Field(None, max_length=2000, description="Casefile description")
    tags: List[str] = Field(default_factory=list, description="Tags for categorization")
    auto_start_session: bool = Field(True, description="Whether a tool session should be created")
    session_title: Optional[str] = Field(None, description="Optional explicit session title")
    hook_channels: List[str] = Field(
        default_factory=list,
        description="Optional hook identifiers to activate for this workflow.",
    )


class CreateCasefileWithSessionRequest(BaseRequest[CreateCasefileWithSessionPayload]):
    """Composite RequestHub workflow request."""

    operation: str = Field(
        "workspace.casefile.create_casefile_with_session",
        description="Composite workflow operation name",
    )


class CasefileWithSessionResultPayload(BaseModel):
    """Result payload returning both casefile and session identifiers."""

    casefile_id: str = Field(..., description="Created casefile identifier")
    session_id: Optional[str] = Field(None, description="Created session identifier when requested")
    hooks_executed: List[str] = Field(default_factory=list, description="Hooks executed during workflow")


class CreateCasefileWithSessionResponse(BaseResponse[CasefileWithSessionResultPayload]):
    """Response envelope for the composite workflow."""
