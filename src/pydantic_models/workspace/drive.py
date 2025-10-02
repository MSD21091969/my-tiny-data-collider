"""Pydantic models for Google Drive data stored alongside casefiles."""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class DriveOwner(BaseModel):
    """Metadata describing a file owner."""

    email: str = Field(..., description="Owner email")
    display_name: Optional[str] = Field(None, description="Owner display name")


class DriveFile(BaseModel):
    """Representation of a Google Drive file."""

    id: str = Field(..., description="Drive file ID")
    name: str = Field(..., description="File name")
    mime_type: str = Field(..., description="MIME type")
    size_bytes: Optional[int] = Field(None, ge=0, description="File size in bytes")
    web_view_link: Optional[str] = Field(None, description="Link for viewing the file")
    icon_link: Optional[str] = Field(None, description="Icon link for the file type")
    parents: List[str] = Field(default_factory=list, description="Parent folder IDs")
    owners: List[DriveOwner] = Field(default_factory=list, description="File owners")
    created_time: str = Field(default_factory=lambda: datetime.now().isoformat(), description="Creation timestamp")
    modified_time: str = Field(default_factory=lambda: datetime.now().isoformat(), description="Last modification timestamp")
    trashed: bool = Field(default=False, description="Whether the file is in trash")


class DriveFolder(BaseModel):
    """Representation of a Google Drive folder."""

    id: str = Field(..., description="Drive folder ID")
    name: str = Field(..., description="Folder name")
    parents: List[str] = Field(default_factory=list, description="Parent folder IDs")
    created_time: str = Field(default_factory=lambda: datetime.now().isoformat(), description="Creation timestamp")
    modified_time: str = Field(default_factory=lambda: datetime.now().isoformat(), description="Last modification timestamp")


class CasefileDriveData(BaseModel):
    """Typed Drive artifacts stored on a casefile."""

    files: List[DriveFile] = Field(default_factory=list, description="Tracked Drive files")
    folders: List[DriveFolder] = Field(default_factory=list, description="Tracked Drive folders")
    last_sync_token: Optional[str] = Field(None, description="Token for incremental Drive sync")
    synced_at: Optional[str] = Field(None, description="Timestamp of the most recent sync")
    sync_status: str = Field(default="idle", description="Current sync status (idle|syncing|error)")
    error_message: Optional[str] = Field(None, description="Last sync error message")

    def upsert_files(self, new_files: List[DriveFile]) -> None:
        """Merge Drive files into the casefile cache."""

        index = {file.id: file for file in self.files}
        for drive_file in new_files:
            index[drive_file.id] = drive_file
        self.files = list(index.values())

    def upsert_folders(self, new_folders: List[DriveFolder]) -> None:
        """Merge Drive folders into the casefile cache."""

        index = {folder.id: folder for folder in self.folders}
        for folder in new_folders:
            index[folder.id] = folder
        self.folders = list(index.values())
