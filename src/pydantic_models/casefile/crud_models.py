"""
CRUD request/response models for casefile operations.

These models handle casefile lifecycle operations (create, get, update, list, delete, add_session).
Replaces Dict[str, Any] returns with fully typed Pydantic models.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Literal

from ..shared.base_models import BaseRequest, BaseResponse
from .models import CasefileModel, CasefileSummary


# ============================================================================
# CREATE CASEFILE
# ============================================================================

class CreateCasefilePayload(BaseModel):
    """Payload for creating a new casefile."""
    title: str = Field(..., min_length=1, max_length=200, description="Casefile title")
    description: str = Field(default="", max_length=2000, description="Casefile description")
    tags: List[str] = Field(default_factory=list, description="Tags for categorization")


class CreateCasefileRequest(BaseRequest[CreateCasefilePayload]):
    """Request to create a new casefile."""
    operation: Literal["create_casefile"] = "create_casefile"


class CasefileCreatedPayload(BaseModel):
    """Response payload for casefile creation."""
    casefile_id: str = Field(..., description="Created casefile ID (cf_yymmdd_xxx)")
    title: str = Field(..., description="Casefile title")
    created_at: str = Field(..., description="Creation timestamp (ISO 8601)")
    created_by: str = Field(..., description="User who created the casefile")


class CreateCasefileResponse(BaseResponse[CasefileCreatedPayload]):
    """Response for casefile creation."""
    pass


# ============================================================================
# GET CASEFILE
# ============================================================================

class GetCasefilePayload(BaseModel):
    """Payload for retrieving a casefile."""
    casefile_id: str = Field(..., description="Casefile ID to retrieve")


class GetCasefileRequest(BaseRequest[GetCasefilePayload]):
    """Request to get casefile details."""
    operation: Literal["get_casefile"] = "get_casefile"


class CasefileDataPayload(BaseModel):
    """Response payload with full casefile data."""
    casefile: CasefileModel = Field(..., description="Complete casefile model")


class GetCasefileResponse(BaseResponse[CasefileDataPayload]):
    """Response with casefile details."""
    pass


# ============================================================================
# UPDATE CASEFILE (SECURITY CRITICAL - No Dict[str, Any])
# ============================================================================

class UpdateCasefilePayload(BaseModel):
    """
    Payload for updating a casefile.
    
    SECURITY: Uses explicit fields instead of Dict[str, Any] to prevent injection.
    All fields are optional - only provided fields will be updated.
    """
    casefile_id: str = Field(..., description="Casefile ID to update")
    title: Optional[str] = Field(None, min_length=1, max_length=200, description="New title")
    description: Optional[str] = Field(None, max_length=2000, description="New description")
    tags: Optional[List[str]] = Field(None, description="New tags (replaces existing)")
    notes: Optional[str] = Field(None, max_length=5000, description="New notes")


class UpdateCasefileRequest(BaseRequest[UpdateCasefilePayload]):
    """Request to update a casefile."""
    operation: Literal["update_casefile"] = "update_casefile"


class CasefileUpdatedPayload(BaseModel):
    """Response payload for casefile update."""
    casefile: CasefileModel = Field(..., description="Updated casefile model")
    updated_fields: List[str] = Field(..., description="List of fields that were updated")


class UpdateCasefileResponse(BaseResponse[CasefileUpdatedPayload]):
    """Response for casefile update."""
    pass


# ============================================================================
# LIST CASEFILES
# ============================================================================

class ListCasefilesPayload(BaseModel):
    """Payload for listing casefiles with filters."""
    user_id: Optional[str] = Field(None, description="Filter by user ID (owner)")
    tags: Optional[List[str]] = Field(None, description="Filter by tags (any match)")
    search_query: Optional[str] = Field(None, description="Search in title/description")
    limit: int = Field(default=50, ge=1, le=100, description="Maximum results to return")
    offset: int = Field(default=0, ge=0, description="Offset for pagination")


class ListCasefilesRequest(BaseRequest[ListCasefilesPayload]):
    """Request to list casefiles."""
    operation: Literal["list_casefiles"] = "list_casefiles"


class CasefileListPayload(BaseModel):
    """Response payload with list of casefiles."""
    casefiles: List[CasefileSummary] = Field(default_factory=list, description="List of casefile summaries")
    total_count: int = Field(..., description="Total matching casefiles")
    offset: int = Field(..., description="Current offset")
    limit: int = Field(..., description="Current limit")


class ListCasefilesResponse(BaseResponse[CasefileListPayload]):
    """Response with list of casefiles."""
    pass


# ============================================================================
# DELETE CASEFILE
# ============================================================================

class DeleteCasefilePayload(BaseModel):
    """Payload for deleting a casefile."""
    casefile_id: str = Field(..., description="Casefile ID to delete")
    confirm: bool = Field(default=False, description="Confirmation flag for deletion")


class DeleteCasefileRequest(BaseRequest[DeleteCasefilePayload]):
    """Request to delete a casefile."""
    operation: Literal["delete_casefile"] = "delete_casefile"


class CasefileDeletedPayload(BaseModel):
    """Response payload for casefile deletion."""
    casefile_id: str = Field(..., description="Deleted casefile ID")
    deleted_at: str = Field(..., description="Deletion timestamp")
    title: str = Field(..., description="Title of deleted casefile (for confirmation)")


class DeleteCasefileResponse(BaseResponse[CasefileDeletedPayload]):
    """Response for casefile deletion."""
    pass


# ============================================================================
# ADD SESSION TO CASEFILE
# ============================================================================

class AddSessionToCasefilePayload(BaseModel):
    """Payload for linking a session to a casefile."""
    casefile_id: str = Field(..., description="Casefile ID")
    session_id: str = Field(..., description="Session ID to add (ts_* or cs_*)")
    session_type: Literal["tool", "chat"] = Field(..., description="Type of session")


class AddSessionToCasefileRequest(BaseRequest[AddSessionToCasefilePayload]):
    """Request to add a session to a casefile."""
    operation: Literal["add_session_to_casefile"] = "add_session_to_casefile"


class SessionAddedPayload(BaseModel):
    """Response payload for session addition."""
    casefile_id: str = Field(..., description="Casefile ID")
    session_id: str = Field(..., description="Added session ID")
    session_type: str = Field(..., description="Session type")
    total_sessions: int = Field(..., description="Total sessions now linked to casefile")


class AddSessionToCasefileResponse(BaseResponse[SessionAddedPayload]):
    """Response for adding session to casefile."""
    pass
