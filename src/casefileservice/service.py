"""
Service for managing casefiles.
"""

from typing import Dict, Any, Iterable, List, Optional
from datetime import datetime
import logging

from ..pydantic_models.operations.casefile_ops import (
    AddSessionToCasefileRequest,
    AddSessionToCasefileResponse,
    CasefileCreatedPayload,
    CasefileDataPayload,
    CasefileDeletedPayload,
    CasefileListPayload,
    SessionAddedPayload,
    CasefileUpdatedPayload,
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
    PermissionLevel,
    GrantPermissionRequest,
    GrantPermissionResponse,
    PermissionGrantedPayload,
    RevokePermissionRequest,
    RevokePermissionResponse,
    PermissionRevokedPayload,
    StoreGmailMessagesRequest,
    StoreGmailMessagesResponse,
    GmailStorageResultPayload,
    StoreDriveFilesRequest,
    StoreDriveFilesResponse,
    DriveStorageResultPayload,
    StoreSheetDataRequest,
    StoreSheetDataResponse,
    SheetStorageResultPayload,
)
from ..pydantic_models.canonical.casefile import CasefileModel, CasefileMetadata
from ..pydantic_models.canonical.acl import CasefileACL, PermissionEntry
from ..pydantic_models.base.types import RequestStatus
from ..pydantic_models.workspace import (
    CasefileDriveData,
    CasefileGmailData,
    CasefileSheetsData,
    DriveFile,
    GmailLabel,
    GmailMessage,
    GmailThread,
    SheetData,
)
from .repository import CasefileRepository

logger = logging.getLogger(__name__)

class CasefileService:
    """Service for managing casefiles (Firestore only)."""
    
    def __init__(self):
        """Initialize the service."""
        self.repository = CasefileRepository()
        
    async def create_casefile(self, request: CreateCasefileRequest) -> CreateCasefileResponse:
        """Create a new casefile.
        
        Args:
            request: Request containing user_id, title, description, and tags
            
        Returns:
            Response with the created casefile ID and metadata
        """
        start_time = datetime.now()
        
        user_id = request.user_id
        title = request.payload.title
        description = request.payload.description
        tags = request.payload.tags
        
        # Create metadata
        metadata = CasefileMetadata(
            title=title,
            description=description,
            tags=tags or [],
            created_by=user_id
        )
        
        # Create ACL with owner
        acl = CasefileACL(
            owner_id=user_id,
            permissions=[],
            public_access=PermissionLevel.NONE
        )
        
        # Create casefile
        casefile = CasefileModel(
            metadata=metadata,
            acl=acl
        )
        
        # Store in repository
        casefile_id = await self.repository.create_casefile(casefile)
        
        execution_time_ms = int((datetime.now() - start_time).total_seconds() * 1000)
        
        return CreateCasefileResponse(
            request_id=request.request_id,
            status=RequestStatus.COMPLETED,
            payload=CasefileCreatedPayload(
                casefile_id=casefile_id,
                title=title,
                created_at=metadata.created_at,
                created_by=user_id
            ),
            metadata={
                "execution_time_ms": execution_time_ms,
                "user_id": user_id,
                "operation": "create_casefile"
            }
        )
    
    async def get_casefile(self, request: GetCasefileRequest) -> GetCasefileResponse:
        """Get a casefile by ID.
        
        Args:
            request: Request containing casefile_id
            
        Returns:
            Response with the casefile data
        """
        start_time = datetime.now()
        
        casefile_id = request.payload.casefile_id
        
        casefile = await self.repository.get_casefile(casefile_id)
        if not casefile:
            execution_time_ms = int((datetime.now() - start_time).total_seconds() * 1000)
            return GetCasefileResponse(
                request_id=request.request_id,
                status=RequestStatus.FAILED,
                error=f"Casefile {casefile_id} not found",
                payload=None,
                metadata={
                    "execution_time_ms": execution_time_ms,
                    "casefile_id": casefile_id,
                    "operation": "get_casefile"
                }
            )
            
        execution_time_ms = int((datetime.now() - start_time).total_seconds() * 1000)
        
        return GetCasefileResponse(
            request_id=request.request_id,
            status=RequestStatus.COMPLETED,
            payload=CasefileDataPayload(
                casefile=casefile
            ),
            metadata={
                "execution_time_ms": execution_time_ms,
                "casefile_id": casefile_id,
                "operation": "get_casefile"
            }
        )
    
    async def update_casefile(self, request: UpdateCasefileRequest) -> UpdateCasefileResponse:
        """Update a casefile.
        
        Args:
            request: Request containing casefile_id and update fields
            
        Returns:
            Response with the updated casefile data
        """
        start_time = datetime.now()
        
        casefile_id = request.payload.casefile_id
        
        # Get existing casefile
        casefile = await self.repository.get_casefile(casefile_id)
        if not casefile:
            execution_time_ms = int((datetime.now() - start_time).total_seconds() * 1000)
            return UpdateCasefileResponse(
                request_id=request.request_id,
                status=RequestStatus.FAILED,
                error=f"Casefile {casefile_id} not found",
                payload=None,
                metadata={
                    "execution_time_ms": execution_time_ms,
                    "casefile_id": casefile_id,
                    "operation": "update_casefile"
                }
            )
        
        # Track what was updated
        updates_applied = []
        
        # Update metadata fields
        metadata = casefile.metadata
        if request.payload.title is not None:
            metadata.title = request.payload.title
            updates_applied.append("title")
        if request.payload.description is not None:
            metadata.description = request.payload.description
            updates_applied.append("description")
        if request.payload.tags is not None:
            metadata.tags = request.payload.tags
            updates_applied.append("tags")
            
        # Update notes
        if request.payload.notes is not None:
            casefile.notes = request.payload.notes
            updates_applied.append("notes")
            
        # Update timestamp
        metadata.updated_at = datetime.now().isoformat()
        
        # Store updated casefile
        await self.repository.update_casefile(casefile)
        
        execution_time_ms = int((datetime.now() - start_time).total_seconds() * 1000)
        
        return UpdateCasefileResponse(
            request_id=request.request_id,
            status=RequestStatus.COMPLETED,
            payload=CasefileUpdatedPayload(
                casefile_id=casefile_id,
                updated_at=metadata.updated_at,
                casefile=casefile
            ),
            metadata={
                "execution_time_ms": execution_time_ms,
                "updates_applied": updates_applied,
                "operation": "update_casefile"
            }
        )
    
    async def list_casefiles(self, request: ListCasefilesRequest) -> ListCasefilesResponse:
        """List casefiles, optionally filtered by user.
        
        Args:
            request: Request containing optional user_id filter and pagination
            
        Returns:
            Response with list of casefile summaries
        """
        start_time = datetime.now()
        
        user_id = request.payload.user_id
        limit = request.payload.limit
        offset = request.payload.offset
        
        summaries = await self.repository.list_casefiles(user_id=user_id)
        
        # Apply pagination
        total_count = len(summaries)
        paginated_summaries = summaries[offset:offset + limit]
        
        execution_time_ms = int((datetime.now() - start_time).total_seconds() * 1000)
        
        return ListCasefilesResponse(
            request_id=request.request_id,
            status=RequestStatus.COMPLETED,
            payload=CasefileListPayload(
                casefiles=paginated_summaries,
                total_count=total_count,
                offset=offset,
                limit=limit
            ),
            metadata={
                "execution_time_ms": execution_time_ms,
                "filter_user_id": user_id,
                "operation": "list_casefiles"
            }
        )
    
    async def delete_casefile(self, request: DeleteCasefileRequest) -> DeleteCasefileResponse:
        """Delete a casefile.
        
        Args:
            request: Request containing casefile_id
            
        Returns:
            Response with deletion status information
        """
        start_time = datetime.now()
        
        casefile_id = request.payload.casefile_id
        
        # Verify casefile exists
        casefile = await self.repository.get_casefile(casefile_id)
        if not casefile:
            execution_time_ms = int((datetime.now() - start_time).total_seconds() * 1000)
            return DeleteCasefileResponse(
                request_id=request.request_id,
                status=RequestStatus.FAILED,
                error=f"Casefile {casefile_id} not found",
                payload=None,
                metadata={
                    "execution_time_ms": execution_time_ms,
                    "casefile_id": casefile_id,
                    "operation": "delete_casefile"
                }
            )
            
        # Delete casefile
        success = await self.repository.delete_casefile(casefile_id)
        
        if not success:
            execution_time_ms = int((datetime.now() - start_time).total_seconds() * 1000)
            return DeleteCasefileResponse(
                request_id=request.request_id,
                status=RequestStatus.FAILED,
                error=f"Failed to delete casefile {casefile_id}",
                payload=None,
                metadata={
                    "execution_time_ms": execution_time_ms,
                    "casefile_id": casefile_id,
                    "operation": "delete_casefile"
                }
            )
            
        execution_time_ms = int((datetime.now() - start_time).total_seconds() * 1000)
        
        return DeleteCasefileResponse(
            request_id=request.request_id,
            status=RequestStatus.COMPLETED,
            payload=CasefileDeletedPayload(
                casefile_id=casefile_id,
                deleted_at=datetime.now().isoformat()
            ),
            metadata={
                "execution_time_ms": execution_time_ms,
                "operation": "delete_casefile"
            }
        )
        
    async def add_session_to_casefile(self, request: AddSessionToCasefileRequest) -> AddSessionToCasefileResponse:
        """Add a session to a casefile.
        
        Args:
            request: Request containing casefile_id and session_id
            
        Returns:
            Response with updated casefile data
        """
        start_time = datetime.now()
        
        casefile_id = request.payload.casefile_id
        session_id = request.payload.session_id
        
        # Get existing casefile
        casefile = await self.repository.get_casefile(casefile_id)
        if not casefile:
            execution_time_ms = int((datetime.now() - start_time).total_seconds() * 1000)
            return AddSessionToCasefileResponse(
                request_id=request.request_id,
                status=RequestStatus.FAILED,
                error=f"Casefile {casefile_id} not found",
                payload=None,
                metadata={
                    "execution_time_ms": execution_time_ms,
                    "casefile_id": casefile_id,
                    "session_id": session_id,
                    "operation": "add_session_to_casefile"
                }
            )
            
        # Add session if not already present
        was_added = False
        if session_id not in casefile.session_ids:
            casefile.session_ids.append(session_id)
            casefile.metadata.updated_at = datetime.now().isoformat()
            
            # Store updated casefile
            await self.repository.update_casefile(casefile)
            was_added = True
            
        execution_time_ms = int((datetime.now() - start_time).total_seconds() * 1000)
        
        return AddSessionToCasefileResponse(
            request_id=request.request_id,
            status=RequestStatus.COMPLETED,
            payload=SessionAddedPayload(
                casefile_id=casefile_id,
                session_id=session_id,
                session_type="tool" if session_id.startswith("ts_") else "chat",
                total_sessions=len(casefile.session_ids)
            ),
            metadata={
                "execution_time_ms": execution_time_ms,
                "operation": "add_session_to_casefile"
            }
        )

    async def store_gmail_messages(
        self,
        request: StoreGmailMessagesRequest
    ) -> StoreGmailMessagesResponse:
        """Merge Gmail messages into the casefile's typed cache.

        Args:
            request: Request containing casefile_id and messages

        Returns:
            Response with storage result
        """
        start_time = datetime.now()
        
        casefile_id = request.payload.casefile_id
        messages = request.payload.messages
        sync_token = request.payload.sync_token
        overwrite = request.payload.overwrite
        threads = request.payload.threads
        labels = request.payload.labels

        casefile = await self.repository.get_casefile(casefile_id)
        if not casefile:
            execution_time_ms = int((datetime.now() - start_time).total_seconds() * 1000)
            return StoreGmailMessagesResponse(
                request_id=request.request_id,
                status=RequestStatus.FAILED,
                error=f"Casefile {casefile_id} not found",
                payload=None,
                metadata={
                    "execution_time_ms": execution_time_ms,
                    "operation": "store_gmail_messages"
                }
            )

        gmail_data = casefile.gmail_data or CasefileGmailData()

        parsed_messages = [
            message if isinstance(message, GmailMessage) else GmailMessage.model_validate(message)
            for message in messages
        ]

        if overwrite:
            gmail_data.messages = parsed_messages
        else:
            gmail_data.upsert_messages(parsed_messages)

        threads_stored = 0
        if threads:
            parsed_threads = [
                thread if isinstance(thread, GmailThread) else GmailThread.model_validate(thread)
                for thread in threads
            ]
            gmail_data.upsert_threads(parsed_threads)
            threads_stored = len(parsed_threads)

        labels_stored = 0
        if labels:
            parsed_labels = [
                label if isinstance(label, GmailLabel) else GmailLabel.model_validate(label)
                for label in labels
            ]
            gmail_data.upsert_labels(parsed_labels)
            labels_stored = len(parsed_labels)

        gmail_data.synced_at = datetime.now().isoformat()
        gmail_data.sync_status = "completed"
        gmail_data.error_message = None
        if sync_token:
            gmail_data.last_sync_token = sync_token

        casefile.gmail_data = gmail_data
        casefile.metadata.updated_at = datetime.now().isoformat()
        await self.repository.update_casefile(casefile)
        
        execution_time_ms = int((datetime.now() - start_time).total_seconds() * 1000)
        
        return StoreGmailMessagesResponse(
            request_id=request.request_id,
            status=RequestStatus.COMPLETED,
            payload=GmailStorageResultPayload(
                casefile_id=casefile_id,
                messages_stored=len(parsed_messages),
                threads_stored=threads_stored,
                labels_stored=labels_stored,
                sync_status=gmail_data.sync_status,
                sync_token=gmail_data.last_sync_token,
                synced_at=gmail_data.synced_at
            ),
            metadata={
                "execution_time_ms": execution_time_ms,
                "operation": "store_gmail_messages"
            }
        )

    async def store_drive_files(
        self,
        request: StoreDriveFilesRequest
    ) -> StoreDriveFilesResponse:
        """Merge Google Drive files into the casefile.

        Args:
            request: Request containing casefile_id and files

        Returns:
            Response with storage result
        """
        start_time = datetime.now()
        
        casefile_id = request.payload.casefile_id
        files = request.payload.files
        sync_token = request.payload.sync_token
        overwrite = request.payload.overwrite

        casefile = await self.repository.get_casefile(casefile_id)
        if not casefile:
            execution_time_ms = int((datetime.now() - start_time).total_seconds() * 1000)
            return StoreDriveFilesResponse(
                request_id=request.request_id,
                status=RequestStatus.FAILED,
                error=f"Casefile {casefile_id} not found",
                payload=None,
                metadata={
                    "execution_time_ms": execution_time_ms,
                    "operation": "store_drive_files"
                }
            )

        drive_data = casefile.drive_data or CasefileDriveData()
        parsed_files = [
            drive_file if isinstance(drive_file, DriveFile) else DriveFile.model_validate(drive_file)
            for drive_file in files
        ]

        if overwrite:
            drive_data.files = parsed_files
        else:
            drive_data.upsert_files(parsed_files)

        drive_data.synced_at = datetime.now().isoformat()
        drive_data.sync_status = "completed"
        drive_data.error_message = None
        if sync_token:
            drive_data.last_sync_token = sync_token

        casefile.drive_data = drive_data
        casefile.metadata.updated_at = datetime.now().isoformat()
        await self.repository.update_casefile(casefile)
        
        execution_time_ms = int((datetime.now() - start_time).total_seconds() * 1000)
        
        return StoreDriveFilesResponse(
            request_id=request.request_id,
            status=RequestStatus.COMPLETED,
            payload=DriveStorageResultPayload(
                casefile_id=casefile_id,
                files_stored=len(parsed_files),
                sync_status=drive_data.sync_status,
                sync_token=drive_data.last_sync_token,
                synced_at=drive_data.synced_at
            ),
            metadata={
                "execution_time_ms": execution_time_ms,
                "operation": "store_drive_files"
            }
        )

    async def store_sheet_data(
        self,
        request: StoreSheetDataRequest
    ) -> StoreSheetDataResponse:
        """Upsert Google Sheets payloads for the casefile.

        Args:
            request: Request containing casefile_id and sheet_payloads

        Returns:
            Response with storage result
        """
        start_time = datetime.now()
        
        casefile_id = request.payload.casefile_id
        sheet_payloads = request.payload.sheet_payloads
        sync_token = request.payload.sync_token

        casefile = await self.repository.get_casefile(casefile_id)
        if not casefile:
            execution_time_ms = int((datetime.now() - start_time).total_seconds() * 1000)
            return StoreSheetDataResponse(
                request_id=request.request_id,
                status=RequestStatus.FAILED,
                error=f"Casefile {casefile_id} not found",
                payload=None,
                metadata={
                    "execution_time_ms": execution_time_ms,
                    "operation": "store_sheet_data"
                }
            )

        sheets_data = casefile.sheets_data or CasefileSheetsData()
        sheets_count = 0
        for sheet_payload in sheet_payloads:
            sheet = sheet_payload if isinstance(sheet_payload, SheetData) else SheetData.model_validate(sheet_payload)
            sheets_data.upsert_sheet(sheet)
            sheets_count += 1

        sheets_data.synced_at = datetime.now().isoformat()
        sheets_data.sync_status = "completed"
        sheets_data.error_message = None
        if sync_token:
            sheets_data.last_sync_token = sync_token

        casefile.sheets_data = sheets_data
        casefile.metadata.updated_at = datetime.now().isoformat()
        await self.repository.update_casefile(casefile)
        
        execution_time_ms = int((datetime.now() - start_time).total_seconds() * 1000)
        
        return StoreSheetDataResponse(
            request_id=request.request_id,
            status=RequestStatus.COMPLETED,
            payload=SheetStorageResultPayload(
                casefile_id=casefile_id,
                sheets_stored=sheets_count,
                sync_status=sheets_data.sync_status,
                sync_token=sheets_data.last_sync_token,
                synced_at=sheets_data.synced_at
            ),
            metadata={
                "execution_time_ms": execution_time_ms,
                "operation": "store_sheet_data"
            }
        )
        sheets_data.sync_status = "completed"
        sheets_data.error_message = None
        if sync_token:
            sheets_data.last_sync_token = sync_token

        casefile.sheets_data = sheets_data
        casefile.metadata.updated_at = datetime.now().isoformat()
        await self.repository.update_casefile(casefile)
        return sheets_data.model_dump()
    
    # ============================================================================
    # ACL (Access Control List) Methods
    # ============================================================================
    
    async def grant_permission(self, request: GrantPermissionRequest) -> GrantPermissionResponse:
        """Grant permission to a user on a casefile.
        
        Args:
            request: Request containing casefile_id, target_user_id, permission, etc.
            
        Returns:
            Response with permission grant details
        """
        start_time = datetime.now()
        
        casefile_id = request.payload.casefile_id
        granting_user_id = request.user_id
        target_user_id = request.payload.target_user_id
        permission = request.payload.permission
        expires_at = request.payload.expires_at
        notes = request.payload.notes
        
        casefile = await self.repository.get_casefile(casefile_id)
        if not casefile:
            execution_time_ms = int((datetime.now() - start_time).total_seconds() * 1000)
            return GrantPermissionResponse(
                request_id=request.request_id,
                status=RequestStatus.FAILED,
                error=f"Casefile {casefile_id} not found",
                payload=None,
                metadata={
                    "execution_time_ms": execution_time_ms,
                    "operation": "grant_permission"
                }
            )
        
        # Initialize ACL if not present (for legacy casefiles)
        if not casefile.acl:
            casefile.acl = CasefileACL(
                owner_id=casefile.metadata.created_by,
                permissions=[],
                public_access=PermissionLevel.NONE
            )
        
        # Check if granting user can share
        if not casefile.acl.can_share(granting_user_id):
            execution_time_ms = int((datetime.now() - start_time).total_seconds() * 1000)
            return GrantPermissionResponse(
                request_id=request.request_id,
                status=RequestStatus.FAILED,
                error=f"User {granting_user_id} does not have permission to share casefile {casefile_id}",
                payload=None,
                metadata={
                    "execution_time_ms": execution_time_ms,
                    "operation": "grant_permission"
                }
            )
        
        # Remove existing permission for this user (if any)
        casefile.acl.permissions = [
            p for p in casefile.acl.permissions if p.user_id != target_user_id
        ]
        
        # Add new permission
        entry = PermissionEntry(
            user_id=target_user_id,
            permission=permission,
            granted_by=granting_user_id,
            expires_at=expires_at,
            notes=notes
        )
        casefile.acl.permissions.append(entry)
        
        # Update casefile
        casefile.metadata.updated_at = datetime.now().isoformat()
        await self.repository.update_casefile(casefile)
        
        execution_time_ms = int((datetime.now() - start_time).total_seconds() * 1000)
        
        logger.info(f"Granted {permission.value} permission on casefile {casefile_id} to user {target_user_id}")
        
        return GrantPermissionResponse(
            request_id=request.request_id,
            status=RequestStatus.COMPLETED,
            payload=PermissionGrantedPayload(
                casefile_id=casefile_id,
                target_user_id=target_user_id,
                permission=permission,
                granted_by=granting_user_id,
                granted_at=datetime.now().isoformat()
            ),
            metadata={
                "execution_time_ms": execution_time_ms,
                "operation": "grant_permission"
            }
        )
    
    async def revoke_permission(self, request: RevokePermissionRequest) -> RevokePermissionResponse:
        """Revoke permission from a user on a casefile.
        
        Args:
            request: Request containing casefile_id and target_user_id
            
        Returns:
            Response with revocation details
        """
        start_time = datetime.now()
        
        casefile_id = request.payload.casefile_id
        revoking_user_id = request.user_id
        target_user_id = request.payload.target_user_id
        casefile = await self.repository.get_casefile(casefile_id)
        if not casefile:
            execution_time_ms = int((datetime.now() - start_time).total_seconds() * 1000)
            return RevokePermissionResponse(
                request_id=request.request_id,
                status=RequestStatus.FAILED,
                error=f"Casefile {casefile_id} not found",
                payload=None,
                metadata={
                    "execution_time_ms": execution_time_ms,
                    "operation": "revoke_permission"
                }
            )
        
        if not casefile.acl:
            execution_time_ms = int((datetime.now() - start_time).total_seconds() * 1000)
            return RevokePermissionResponse(
                request_id=request.request_id,
                status=RequestStatus.FAILED,
                error=f"Casefile {casefile_id} has no ACL",
                payload=None,
                metadata={
                    "execution_time_ms": execution_time_ms,
                    "operation": "revoke_permission"
                }
            )
        
        # Check if revoking user can share
        if not casefile.acl.can_share(revoking_user_id):
            execution_time_ms = int((datetime.now() - start_time).total_seconds() * 1000)
            return RevokePermissionResponse(
                request_id=request.request_id,
                status=RequestStatus.FAILED,
                error=f"User {revoking_user_id} does not have permission to manage casefile {casefile_id}",
                payload=None,
                metadata={
                    "execution_time_ms": execution_time_ms,
                    "operation": "revoke_permission"
                }
            )
        
        # Cannot revoke owner's permissions
        if target_user_id == casefile.acl.owner_id:
            execution_time_ms = int((datetime.now() - start_time).total_seconds() * 1000)
            return RevokePermissionResponse(
                request_id=request.request_id,
                status=RequestStatus.FAILED,
                error="Cannot revoke owner's permissions",
                payload=None,
                metadata={
                    "execution_time_ms": execution_time_ms,
                    "operation": "revoke_permission"
                }
            )
        
        # Remove permission
        original_count = len(casefile.acl.permissions)
        casefile.acl.permissions = [
            p for p in casefile.acl.permissions if p.user_id != target_user_id
        ]
        
        if len(casefile.acl.permissions) == original_count:
            execution_time_ms = int((datetime.now() - start_time).total_seconds() * 1000)
            logger.warning(f"No permission found for user {target_user_id} on casefile {casefile_id}")
            return RevokePermissionResponse(
                request_id=request.request_id,
                status=RequestStatus.FAILED,
                error=f"No permission found for user {target_user_id}",
                payload=None,
                metadata={
                    "execution_time_ms": execution_time_ms,
                    "operation": "revoke_permission"
                }
            )
        
        # Update casefile
        casefile.metadata.updated_at = datetime.now().isoformat()
        await self.repository.update_casefile(casefile)
        
        execution_time_ms = int((datetime.now() - start_time).total_seconds() * 1000)
        
        logger.info(f"Revoked permission on casefile {casefile_id} from user {target_user_id}")
        
        return RevokePermissionResponse(
            request_id=request.request_id,
            status=RequestStatus.COMPLETED,
            payload=PermissionRevokedPayload(
                casefile_id=casefile_id,
                target_user_id=target_user_id,
                revoked_by=revoking_user_id,
                revoked_at=datetime.now().isoformat()
            ),
            metadata={
                "execution_time_ms": execution_time_ms,
                "operation": "revoke_permission"
            }
        )
    
    async def list_permissions(self, casefile_id: str, requesting_user_id: str) -> CasefileACL:
        """List all permissions for a casefile.
        
        Args:
            casefile_id: Casefile ID
            requesting_user_id: User requesting permissions list (must have read access)
            
        Returns:
            CasefileACL object
            
        Raises:
            ValueError: If casefile not found or user lacks permission
        """
        casefile = await self.repository.get_casefile(casefile_id)
        if not casefile:
            raise ValueError(f"Casefile {casefile_id} not found")
        
        if not casefile.acl:
            # Initialize ACL for legacy casefiles
            casefile.acl = CasefileACL(
                owner_id=casefile.metadata.created_by,
                permissions=[],
                public_access=PermissionLevel.NONE
            )
        
        # Check if requesting user can read
        if not casefile.acl.can_read(requesting_user_id):
            raise ValueError(f"User {requesting_user_id} does not have permission to view casefile {casefile_id}")
        
        return casefile.acl
    
    async def check_permission(
        self,
        casefile_id: str,
        user_id: str,
        required_permission: PermissionLevel
    ) -> bool:
        """Check if a user has specific permission on a casefile.
        
        Args:
            casefile_id: Casefile ID
            user_id: User ID to check
            required_permission: Required permission level
            
        Returns:
            True if user has required permission or higher
        """
        casefile = await self.repository.get_casefile(casefile_id)
        if not casefile:
            return False
        
        if not casefile.acl:
            # Legacy casefile - only owner has access
            return user_id == casefile.metadata.created_by
        
        return casefile.acl.has_permission(user_id, required_permission)
