"""
Service for managing casefiles.
"""

from typing import Dict, Any, Iterable, List, Optional
from datetime import datetime
import logging

from ..pydantic_models.casefile.models import CasefileModel, CasefileMetadata
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
        
    async def create_casefile(self, user_id: str, title: str, description: str = "", tags: List[str] = None) -> Dict[str, str]:
        """Create a new casefile.
        
        Args:
            user_id: ID of the user creating the casefile
            title: Title of the casefile
            description: Description of the casefile
            tags: Optional tags for the casefile
            
        Returns:
            Dictionary with the casefile ID
        """
        # Create metadata
        metadata = CasefileMetadata(
            title=title,
            description=description,
            tags=tags or [],
            created_by=user_id
        )
        
        # Create casefile
        casefile = CasefileModel(
            metadata=metadata
        )
        
        # Store in repository
        casefile_id = await self.repository.create_casefile(casefile)
        
        return {"casefile_id": casefile_id}
    
    async def get_casefile(self, casefile_id: str) -> Dict[str, Any]:
        """Get a casefile by ID.
        
        Args:
            casefile_id: ID of the casefile to retrieve
            
        Returns:
            The casefile data
            
        Raises:
            ValueError: If casefile not found
        """
        casefile = await self.repository.get_casefile(casefile_id)
        if not casefile:
            raise ValueError(f"Casefile {casefile_id} not found")
            
        return casefile.model_dump()
    
    async def update_casefile(self, casefile_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update a casefile.
        
        Args:
            casefile_id: ID of the casefile to update
            updates: Dictionary of fields to update
            
        Returns:
            The updated casefile data
            
        Raises:
            ValueError: If casefile not found
        """
        # Get existing casefile
        casefile = await self.repository.get_casefile(casefile_id)
        if not casefile:
            raise ValueError(f"Casefile {casefile_id} not found")
        
        # Update metadata fields
        metadata = casefile.metadata
        if "title" in updates:
            metadata.title = updates["title"]
        if "description" in updates:
            metadata.description = updates["description"]
        if "tags" in updates:
            metadata.tags = updates["tags"]
            
        # Update notes
        if "notes" in updates:
            casefile.notes = updates["notes"]
            
        # Update timestamp
        metadata.updated_at = datetime.now().isoformat()
        
        # Store updated casefile
        await self.repository.update_casefile(casefile)
        
        return casefile.model_dump()
    
    async def list_casefiles(self, user_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """List casefiles, optionally filtered by user.
        
        Args:
            user_id: Optional user ID to filter by
            
        Returns:
            List of casefile summaries
        """
        summaries = await self.repository.list_casefiles(user_id=user_id)
        return [summary.model_dump() for summary in summaries]
    
    async def delete_casefile(self, casefile_id: str) -> Dict[str, Any]:
        """Delete a casefile.
        
        Args:
            casefile_id: ID of the casefile to delete
            
        Returns:
            Status information
            
        Raises:
            ValueError: If casefile not found
        """
        # Verify casefile exists
        casefile = await self.repository.get_casefile(casefile_id)
        if not casefile:
            raise ValueError(f"Casefile {casefile_id} not found")
            
        # Delete casefile
        success = await self.repository.delete_casefile(casefile_id)
        
        if not success:
            raise ValueError(f"Failed to delete casefile {casefile_id}")
            
        return {
            "casefile_id": casefile_id,
            "status": "deleted"
        }
        
    async def add_session_to_casefile(self, casefile_id: str, session_id: str) -> Dict[str, Any]:
        """Add a session to a casefile.
        
        Args:
            casefile_id: ID of the casefile
            session_id: ID of the session to add
            
        Returns:
            Updated casefile data
            
        Raises:
            ValueError: If casefile not found
        """
        # Get existing casefile
        casefile = await self.repository.get_casefile(casefile_id)
        if not casefile:
            raise ValueError(f"Casefile {casefile_id} not found")
            
        # Add session if not already present
        if session_id not in casefile.session_ids:
            casefile.session_ids.append(session_id)
            casefile.metadata.updated_at = datetime.now().isoformat()
            
            # Store updated casefile
            await self.repository.update_casefile(casefile)
            
        return casefile.model_dump()

    async def store_gmail_messages(
        self,
        casefile_id: str,
        messages: Iterable[Dict[str, Any] | GmailMessage],
        *,
        sync_token: Optional[str] = None,
        overwrite: bool = False,
        threads: Optional[Iterable[Dict[str, Any]]] = None,
        labels: Optional[Iterable[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """Merge Gmail messages into the casefile's typed cache.

        Args:
            casefile_id: Casefile identifier
            messages: Iterable of Gmail message dicts or models
            sync_token: Optional incremental sync token returned by Gmail API
            overwrite: Replace existing cache instead of merging
            threads: Optional iterable of thread metadata records
            labels: Optional iterable of label metadata records

        Returns:
            Serialized Gmail cache payload
        """

        casefile = await self.repository.get_casefile(casefile_id)
        if not casefile:
            raise ValueError(f"Casefile {casefile_id} not found")

        gmail_data = casefile.gmail_data or CasefileGmailData()

        parsed_messages = [
            message if isinstance(message, GmailMessage) else GmailMessage.model_validate(message)
            for message in messages
        ]

        if overwrite:
            gmail_data.messages = parsed_messages
        else:
            gmail_data.upsert_messages(parsed_messages)

        if threads:
            parsed_threads = [
                thread if isinstance(thread, GmailThread) else GmailThread.model_validate(thread)
                for thread in threads
            ]
            gmail_data.upsert_threads(parsed_threads)

        if labels:
            parsed_labels = [
                label if isinstance(label, GmailLabel) else GmailLabel.model_validate(label)
                for label in labels
            ]
            gmail_data.upsert_labels(parsed_labels)

        gmail_data.synced_at = datetime.now().isoformat()
        gmail_data.sync_status = "completed"
        gmail_data.error_message = None
        if sync_token:
            gmail_data.last_sync_token = sync_token

        casefile.gmail_data = gmail_data
        casefile.metadata.updated_at = datetime.now().isoformat()
        await self.repository.update_casefile(casefile)
        return gmail_data.model_dump()

    async def store_drive_files(
        self,
        casefile_id: str,
        files: Iterable[Dict[str, Any] | DriveFile],
        *,
        sync_token: Optional[str] = None,
        overwrite: bool = False,
    ) -> Dict[str, Any]:
        """Merge Google Drive files into the casefile."""

        casefile = await self.repository.get_casefile(casefile_id)
        if not casefile:
            raise ValueError(f"Casefile {casefile_id} not found")

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
        return drive_data.model_dump()

    async def store_sheet_data(
        self,
        casefile_id: str,
        sheet_payloads: Iterable[Dict[str, Any] | SheetData],
        *,
        sync_token: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Upsert Google Sheets payloads for the casefile."""

        casefile = await self.repository.get_casefile(casefile_id)
        if not casefile:
            raise ValueError(f"Casefile {casefile_id} not found")

        sheets_data = casefile.sheets_data or CasefileSheetsData()
        for sheet_payload in sheet_payloads:
            sheet = sheet_payload if isinstance(sheet_payload, SheetData) else SheetData.model_validate(sheet_payload)
            sheets_data.upsert_sheet(sheet)

        sheets_data.synced_at = datetime.now().isoformat()
        sheets_data.sync_status = "completed"
        sheets_data.error_message = None
        if sync_token:
            sheets_data.last_sync_token = sync_token

        casefile.sheets_data = sheets_data
        casefile.metadata.updated_at = datetime.now().isoformat()
        await self.repository.update_casefile(casefile)
        return sheets_data.model_dump()