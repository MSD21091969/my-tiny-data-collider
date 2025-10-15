"""RequestHub-specific DTOs for composite workflows."""

from __future__ import annotations

from pydantic import BaseModel, Field

from ..base.custom_types import CasefileId, IsoTimestamp, PositiveInt, SessionId, ShortString, MediumString, TagList
from ..base.envelopes import BaseRequest, BaseResponse


class CreateCasefileWithSessionPayload(BaseModel):
    """Payload for composite workflow that creates a casefile and session."""

    title: ShortString = Field(..., description="Casefile title")
    description: MediumString | None = Field(None, description="Casefile description")
    tags: TagList = Field(default_factory=list, description="Tags for categorization")
    auto_start_session: bool = Field(True, description="Whether a tool session should be created")
    session_title: ShortString | None = Field(None, description="Optional explicit session title")
    hook_channels: list[ShortString] = Field(
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

    casefile_id: CasefileId = Field(..., description="Created casefile identifier")
    session_id: SessionId | None = Field(None, description="Created session identifier when requested")
    hooks_executed: list[ShortString] = Field(default_factory=list, description="Hooks executed during workflow")


class CreateCasefileWithSessionResponse(BaseResponse[CasefileWithSessionResultPayload]):
    """Response envelope for the composite workflow."""


# ============================================================================
# CREATE SESSION AND LINK TO CASEFILE
# ============================================================================

class CreateSessionWithCasefilePayload(BaseModel):
    """Payload for creating a session and linking it to an existing casefile."""
    
    casefile_id: CasefileId = Field(..., description="Existing casefile ID to link session to")
    title: ShortString | None = Field(None, description="Optional session title")
    session_type: ShortString = Field("tool", description="Type of session to create (tool or chat)")
class CreateSessionWithCasefileRequest(BaseRequest[CreateSessionWithCasefilePayload]):
    """Request to create a session and link it to a casefile."""

    operation: str = Field(
        "workspace.session.create_session_with_casefile",
        description="Composite workflow operation name",
    )


class SessionWithCasefileResultPayload(BaseModel):
    """Result payload for session creation and casefile linking."""

    session_id: SessionId = Field(..., description="Created session ID")
    casefile_id: CasefileId = Field(..., description="Casefile ID the session was linked to")
    session_type: ShortString = Field(..., description="Type of session created")
    created_at: IsoTimestamp = Field(..., description="Session creation timestamp")
    total_sessions: PositiveInt = Field(..., description="Total sessions now linked to casefile")


class CreateSessionWithCasefileResponse(BaseResponse[SessionWithCasefileResultPayload]):
    """Response for session creation and casefile linking."""
