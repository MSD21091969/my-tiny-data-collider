"""
Canonical casefile domain models.

This module contains the core casefile entity and its components:
- CasefileMetadata: Metadata sub-structure
- ResourceReference: Legacy resource links (deprecated)
- CasefileModel: The actual casefile entity (single source of truth)

For casefile operations (CRUD), see pydantic_models.operations.casefile_ops
For casefile summaries/views, see pydantic_models.views.casefile_views
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, computed_field, model_validator

from coreservice.id_service import get_id_service
from ..base.custom_types import ShortString, MediumString, TagList, IsoTimestamp

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
    title: ShortString = Field(
        ...,
        description="Casefile title",
        json_schema_extra={"example": "Investigation Case 2025-001"}
    )
    description: MediumString = Field(
        default="",
        description="Casefile description",
        json_schema_extra={"example": "Email investigation for incident #42"}
    )
    tags: TagList = Field(
        default_factory=list,
        description="Tags for categorization",
        json_schema_extra={"example": ["incident", "email", "security"]}
    )
    created_by: str = Field(
        ...,
        description="User who created the casefile",
        json_schema_extra={"example": "user@example.com"}
    )
    created_at: IsoTimestamp = Field(
        default_factory=lambda: datetime.now().isoformat(),
        description="Creation timestamp (ISO 8601)",
        json_schema_extra={"example": "2025-10-13T12:00:00"}
    )
    updated_at: IsoTimestamp = Field(
        default_factory=lambda: datetime.now().isoformat(),
        description="Last update timestamp (ISO 8601)",
        json_schema_extra={"example": "2025-10-13T12:30:00"}
    )
    
    @model_validator(mode='after')
    def validate_timestamp_order(self) -> 'CasefileMetadata':
        """Ensure created_at <= updated_at."""
        try:
            created = datetime.fromisoformat(self.created_at.replace('Z', '+00:00'))
            updated = datetime.fromisoformat(self.updated_at.replace('Z', '+00:00'))
            if created > updated:
                raise ValueError("created_at must be <= updated_at")
        except (ValueError, AttributeError) as e:
            # Timestamp validation happens in custom type, just check order here
            if "created_at must be <=" not in str(e):
                pass  # Let custom type validators handle format errors
            else:
                raise
        return self


class ResourceReference(BaseModel):
    """Reference to an external resource linked to a casefile."""
    resource_id: str = Field(
        ...,
        description="External resource ID",
        json_schema_extra={"example": "msg_123abc"}
    )
    resource_type: str = Field(
        ...,
        description="Type of resource (gmail, drive, etc.)",
        json_schema_extra={"example": "gmail"}
    )
    added_at: IsoTimestamp = Field(
        default_factory=lambda: datetime.now().isoformat(),
        description="When this was added (ISO 8601)",
        json_schema_extra={"example": "2025-10-13T12:00:00"}
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata",
        json_schema_extra={"example": {"subject": "Important Email"}}
    )


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
    
    @model_validator(mode='after')
    def validate_casefile_data(self) -> 'CasefileModel':
        """Ensure casefile has at least one data source or legacy resources."""
        has_typed_data = any([self.gmail_data, self.drive_data, self.sheets_data])
        has_legacy_resources = bool(self.resources)
        
        if not has_typed_data and not has_legacy_resources:
            raise ValueError(
                "Casefile must have at least one data source (gmail_data, drive_data, "
                "sheets_data) or legacy resources"
            )
        return self
