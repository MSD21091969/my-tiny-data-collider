"""
Models for casefile data and metadata.
"""

from pydantic import BaseModel, Field, computed_field
from typing import Dict, Any, List, Optional
from datetime import datetime

from ...coreservice.id_service import get_id_service

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
    resources: Dict[str, List[ResourceReference]] = Field(default_factory=dict, description="Linked resources by type")
    session_ids: List[str] = Field(default_factory=list, description="Tool session IDs associated with this casefile")
    notes: Optional[str] = Field(None, description="Additional notes")
    
    @computed_field
    def resource_count(self) -> int:
        """Total number of resources linked to this casefile."""
        return sum(len(resources) for resources in self.resources.values())

class CasefileSummary(BaseModel):
    """Summary view of a casefile."""
    id: str = Field(..., description="Casefile ID in format yymmdd_code")
    title: str = Field(..., description="Casefile title")
    description: str = Field(..., description="Casefile description")
    tags: List[str] = Field(..., description="Casefile tags")
    created_at: str = Field(..., description="Creation timestamp")
    resource_count: int = Field(..., description="Total number of linked resources")
    session_count: int = Field(..., description="Total number of associated sessions")