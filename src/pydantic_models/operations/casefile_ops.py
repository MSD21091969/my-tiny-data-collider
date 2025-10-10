"""
Casefile operation models (CRUD + ACL).

This module consolidates all casefile operation request/response models:
- CRUD operations: create, get, update, list, delete, add_session
- ACL operations: grant_permission, revoke_permission, list_permissions, check_permission

For canonical casefile entities, see pydantic_models.canonical.casefile and canonical.acl
"""

from typing import List, Literal, Optional

from pydantic import BaseModel, Field

from ..base.envelopes import BaseRequest, BaseResponse
from ..canonical.acl import CasefileACL, PermissionEntry, PermissionLevel
from ..canonical.casefile import CasefileModel
from ..views.casefile_views import CasefileSummary

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


# ============================================================================
# ACL OPERATIONS
# ============================================================================

class GrantPermissionPayload(BaseModel):
    """Payload for granting permission to a user."""
    casefile_id: str = Field(..., description="Casefile ID")
    target_user_id: str = Field(..., description="User to grant permission to")
    permission: PermissionLevel = Field(..., description="Permission level to grant")
    expires_at: Optional[str] = Field(None, description="Optional expiration timestamp")
    notes: Optional[str] = Field(None, description="Optional notes")


class GrantPermissionRequest(BaseRequest[GrantPermissionPayload]):
    """Request to grant permission to a user."""
    operation: Literal["grant_permission"] = "grant_permission"


class PermissionGrantedPayload(BaseModel):
    """Response payload for permission grant."""
    casefile_id: str
    target_user_id: str
    permission: PermissionLevel
    granted_by: str
    granted_at: str


class GrantPermissionResponse(BaseResponse[PermissionGrantedPayload]):
    """Response for grant permission."""
    pass


class RevokePermissionPayload(BaseModel):
    """Payload for revoking permission from a user."""
    casefile_id: str = Field(..., description="Casefile ID")
    target_user_id: str = Field(..., description="User to revoke permission from")


class RevokePermissionRequest(BaseRequest[RevokePermissionPayload]):
    """Request to revoke permission from a user."""
    operation: Literal["revoke_permission"] = "revoke_permission"


class PermissionRevokedPayload(BaseModel):
    """Response payload for permission revocation."""
    casefile_id: str
    target_user_id: str
    revoked_by: str
    revoked_at: str


class RevokePermissionResponse(BaseResponse[PermissionRevokedPayload]):
    """Response for revoke permission."""
    pass


class ListPermissionsPayload(BaseModel):
    """Payload for listing all permissions for a casefile."""
    casefile_id: str = Field(..., description="Casefile ID")


class ListPermissionsRequest(BaseRequest[ListPermissionsPayload]):
    """Request to list all permissions for a casefile."""
    operation: Literal["list_permissions"] = "list_permissions"


class PermissionListPayload(BaseModel):
    """Response payload with list of all permissions."""
    casefile_id: str
    owner_id: str
    public_access: PermissionLevel
    permissions: List[PermissionEntry]
    total_users: int


class ListPermissionsResponse(BaseResponse[PermissionListPayload]):
    """Response with list of permissions."""
    pass


# Legacy direct response model (for backward compatibility with API routers)
class PermissionListResponse(BaseModel):
    """Direct response with list of all permissions (legacy format)."""
    casefile_id: str
    owner_id: str
    public_access: PermissionLevel
    permissions: List[PermissionEntry]
    total_users: int


class CheckPermissionPayload(BaseModel):
    """Payload for checking if a user has permission."""
    casefile_id: str = Field(..., description="Casefile ID")
    user_id: str = Field(..., description="User ID to check")
    required_permission: PermissionLevel = Field(..., description="Required permission level")


class CheckPermissionRequest(BaseRequest[CheckPermissionPayload]):
    """Request to check if a user has permission."""
    operation: Literal["check_permission"] = "check_permission"


class PermissionCheckPayload(BaseModel):
    """Response payload with permission check result."""
    casefile_id: str
    user_id: str
    permission: PermissionLevel
    can_read: bool
    can_write: bool
    can_share: bool
    can_delete: bool
    has_required_permission: bool


class CheckPermissionResponse(BaseResponse[PermissionCheckPayload]):
    """Response for permission check."""
    pass


# ============================================================================
# STORE GMAIL MESSAGES (workspace sync)
# ============================================================================

class StoreGmailMessagesPayload(BaseModel):
    """Payload for storing Gmail messages in casefile."""
    casefile_id: str = Field(..., description="Casefile ID")
    messages: List[dict] = Field(..., description="Gmail messages (GmailMessage dicts)")
    sync_token: Optional[str] = Field(None, description="Incremental sync token from Gmail API")
    overwrite: bool = Field(False, description="Replace existing cache instead of merging")
    threads: Optional[List[dict]] = Field(None, description="Gmail thread metadata")
    labels: Optional[List[dict]] = Field(None, description="Gmail label metadata")


class StoreGmailMessagesRequest(BaseRequest[StoreGmailMessagesPayload]):
    """Request to store Gmail messages in casefile."""
    operation: Literal["store_gmail_messages"] = "store_gmail_messages"


class GmailStorageResultPayload(BaseModel):
    """Response payload for Gmail message storage."""
    casefile_id: str = Field(..., description="Casefile ID")
    messages_stored: int = Field(..., description="Number of messages stored")
    threads_stored: int = Field(0, description="Number of threads stored")
    labels_stored: int = Field(0, description="Number of labels stored")
    sync_status: str = Field(..., description="Sync status: completed, partial, failed")
    sync_token: Optional[str] = Field(None, description="New sync token")
    synced_at: str = Field(..., description="Sync timestamp")


class StoreGmailMessagesResponse(BaseResponse[GmailStorageResultPayload]):
    """Response for Gmail message storage."""
    pass


# ============================================================================
# STORE DRIVE FILES (workspace sync)
# ============================================================================

class StoreDriveFilesPayload(BaseModel):
    """Payload for storing Google Drive files in casefile."""
    casefile_id: str = Field(..., description="Casefile ID")
    files: List[dict] = Field(..., description="Drive files (DriveFile dicts)")
    sync_token: Optional[str] = Field(None, description="Incremental sync token from Drive API")
    overwrite: bool = Field(False, description="Replace existing cache instead of merging")


class StoreDriveFilesRequest(BaseRequest[StoreDriveFilesPayload]):
    """Request to store Drive files in casefile."""
    operation: Literal["store_drive_files"] = "store_drive_files"


class DriveStorageResultPayload(BaseModel):
    """Response payload for Drive file storage."""
    casefile_id: str = Field(..., description="Casefile ID")
    files_stored: int = Field(..., description="Number of files stored")
    sync_status: str = Field(..., description="Sync status: completed, partial, failed")
    sync_token: Optional[str] = Field(None, description="New sync token")
    synced_at: str = Field(..., description="Sync timestamp")


class StoreDriveFilesResponse(BaseResponse[DriveStorageResultPayload]):
    """Response for Drive file storage."""
    pass


# ============================================================================
# STORE SHEET DATA (workspace sync)
# ============================================================================

class StoreSheetDataPayload(BaseModel):
    """Payload for storing Google Sheets data in casefile."""
    casefile_id: str = Field(..., description="Casefile ID")
    sheet_payloads: List[dict] = Field(..., description="Sheet data (SheetData dicts)")
    sync_token: Optional[str] = Field(None, description="Incremental sync token from Sheets API")


class StoreSheetDataRequest(BaseRequest[StoreSheetDataPayload]):
    """Request to store Sheets data in casefile."""
    operation: Literal["store_sheet_data"] = "store_sheet_data"


class SheetStorageResultPayload(BaseModel):
    """Response payload for Sheets data storage."""
    casefile_id: str = Field(..., description="Casefile ID")
    sheets_stored: int = Field(..., description="Number of sheets stored")
    sync_status: str = Field(..., description="Sync status: completed, partial, failed")
    sync_token: Optional[str] = Field(None, description="New sync token")
    synced_at: str = Field(..., description="Sync timestamp")


class StoreSheetDataResponse(BaseResponse[SheetStorageResultPayload]):
    """Response for Sheets data storage."""
    pass
