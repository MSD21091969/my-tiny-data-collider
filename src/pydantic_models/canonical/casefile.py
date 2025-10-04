"""
Canonical casefile domain models.

This module contains the core casefile entity and its components:
- CasefileMetadata: Metadata sub-structure
- ResourceReference: Legacy resource links (deprecated)
- CasefileModel: The actual casefile entity (single source of truth)

For casefile operations (CRUD), see pydantic_models.operations.casefile_ops
For casefile summaries/views, see pydantic_models.views.casefile_views
"""

from pydantic import BaseModel, Field, computed_field
from typing import Dict, Any, List, Optional
from datetime import datetime

from ...coreservice.id_service import get_id_service
from ..workspace import (
    CasefileDriveData,
    CasefileGmailData,
    CasefileSheetsData,
)
from .acl import CasefileACL


def generate_casefile_id() -> str:
    """Generate a casefile ID using the centralized ID service."""
    return get_id_service().new_casefile_id()


class CasefileMetadata(BaseModel):
    """Metadata for a casefile."""
    title: str = Field(..., description="Casefile title")
    description: str = Field(default="", description="Casefile description")
    tags: List[str] = Field(default_factory=list, description="Tags for categorization")
    created_by: str = Field(..., description="User who created the casefile")
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat(), description="Creation timestamp")
    updated_at: str = Field(default_factory=lambda: datetime.now().isoformat(), description="Last update timestamp")


class ResourceReference(BaseModel):
    """Reference to an external resource linked to a casefile."""
    resource_id: str = Field(..., description="External resource ID")
    resource_type: str = Field(..., description="Type of resource (gmail, drive, etc.)")
    added_at: str = Field(default_factory=lambda: datetime.now().isoformat(), description="When this was added")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class CasefileModel(BaseModel):
    """Complete casefile model with metadata and linked resources."""

    id: str = Field(default_factory=generate_casefile_id, description="Unique casefile ID in format cf_yymmdd_code")
    metadata: CasefileMetadata = Field(..., description="Casefile metadata")
    acl: Optional[CasefileACL] = Field(None, description="Access Control List for permissions")
    resources: Dict[str, List[ResourceReference]] = Field(
        default_factory=dict,
        description="Legacy resource references by type (deprecated)",
        json_schema_extra={"deprecated": True},
    )
    session_ids: List[str] = Field(default_factory=list, description="Tool session IDs associated with this casefile")
    notes: Optional[str] = Field(None, description="Additional notes")

    # Typed workspace data containers (preferred over `resources`)
    gmail_data: Optional[CasefileGmailData] = Field(
        None,
        description="Typed Gmail data captured for this casefile",
    )
    drive_data: Optional[CasefileDriveData] = Field(
        None,
        description="Typed Google Drive data captured for this casefile",
    )
    sheets_data: Optional[CasefileSheetsData] = Field(
        None,
        description="Typed Google Sheets data captured for this casefile",
    )
    
    @computed_field
    def resource_count(self) -> int:
        """Total number of resources linked to this casefile."""
        total = sum(len(resources) for resources in self.resources.values())
        if self.gmail_data:
            total += len(self.gmail_data.messages)
        if self.drive_data:
            total += len(self.drive_data.files)
        if self.sheets_data:
            total += sum(len(sheet.ranges) for sheet in self.sheets_data.spreadsheets.values())
        return total
