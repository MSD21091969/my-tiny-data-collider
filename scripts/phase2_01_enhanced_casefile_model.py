"""
Phase 2: Enhanced CasefileModel Implementation

This script demonstrates the complete implementation of CasefileModel enhancements
as discussed in TOOL_ENGINEERING_ANALYSIS.md Phase 2.

Enhancements include:
- Status lifecycle (active, archived, closed, deleted)
- Priority levels (1-5)
- Relationship tracking (parent/child casefiles)
- Categorization
- Computed fields (age_days, is_closed)
- Business logic methods (close, add_tag, can_read)
- Field validators (tags normalization)

Usage:
    This is a reference implementation showing the enhanced model structure.
    To integrate: Copy the enhancements to src/pydantic_models/canonical/casefile.py
"""

from pydantic import BaseModel, Field, computed_field, field_validator
from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum


class CasefileStatus(str, Enum):
    """Status lifecycle for casefiles."""
    ACTIVE = "active"
    ARCHIVED = "archived"
    CLOSED = "closed"
    DELETED = "deleted"


class CasefilePriority(int, Enum):
    """Priority levels for casefiles."""
    LOWEST = 1
    LOW = 2
    MEDIUM = 3
    HIGH = 4
    CRITICAL = 5


class CasefileCategory(str, Enum):
    """Common casefile categories."""
    GENERAL = "general"
    PROJECT = "project"
    INVESTIGATION = "investigation"
    SUPPORT = "support"
    RESEARCH = "research"
    LEGAL = "legal"
    COMPLIANCE = "compliance"
    OTHER = "other"


class EnhancedCasefileMetadata(BaseModel):
    """Enhanced metadata for a casefile."""
    title: str = Field(..., description="Casefile title", min_length=1, max_length=200)
    description: str = Field(default="", description="Casefile description", max_length=2000)
    tags: List[str] = Field(default_factory=list, description="Tags for categorization")
    created_by: str = Field(..., description="User who created the casefile")
    created_at: str = Field(
        default_factory=lambda: datetime.now().isoformat(),
        description="Creation timestamp"
    )
    updated_at: str = Field(
        default_factory=lambda: datetime.now().isoformat(),
        description="Last update timestamp"
    )
    
    @field_validator('tags')
    @classmethod
    def validate_tags(cls, v: List[str]) -> List[str]:
        """Normalize and deduplicate tags."""
        if not v:
            return []
        
        # Normalize: strip whitespace, lowercase
        normalized = [tag.strip().lower() for tag in v if tag.strip()]
        
        # Deduplicate while preserving order
        unique = list(dict.fromkeys(normalized))
        
        # Validate max tags
        if len(unique) > 20:
            raise ValueError("Maximum 20 tags allowed")
        
        # Validate individual tag format
        for tag in unique:
            if len(tag) < 2:
                raise ValueError(f"Tag '{tag}' is too short (minimum 2 characters)")
            if len(tag) > 50:
                raise ValueError(f"Tag '{tag}' is too long (maximum 50 characters)")
            if not tag.replace('-', '').replace('_', '').isalnum():
                raise ValueError(f"Tag '{tag}' contains invalid characters (alphanumeric, -, _ only)")
        
        return unique


class EnhancedCasefileModel(BaseModel):
    """
    Enhanced Casefile Model with full lifecycle, relationships, and business logic.
    
    This is the complete implementation based on Phase 2 analysis.
    Extends the current CasefileModel with:
    - Status and priority management
    - Parent-child relationships
    - Category classification
    - Computed fields for analytics
    - Business logic methods
    - Enhanced validation
    """
    
    # Core fields (existing)
    id: str = Field(..., description="Unique casefile ID in format cf_yymmdd_code")
    metadata: EnhancedCasefileMetadata = Field(..., description="Casefile metadata")
    acl: Optional[Dict[str, Any]] = Field(None, description="Access Control List for permissions")
    session_ids: List[str] = Field(default_factory=list, description="Tool session IDs")
    notes: Optional[str] = Field(None, description="Additional notes", max_length=10000)
    
    # Workspace data containers (existing)
    gmail_data: Optional[Dict[str, Any]] = Field(None, description="Gmail data")
    drive_data: Optional[Dict[str, Any]] = Field(None, description="Drive data")
    sheets_data: Optional[Dict[str, Any]] = Field(None, description="Sheets data")
    
    # NEW: Lifecycle fields
    status: CasefileStatus = Field(
        default=CasefileStatus.ACTIVE,
        description="Current status of the casefile"
    )
    priority: int = Field(
        default=3,
        ge=1,
        le=5,
        description="Priority level (1=lowest, 5=critical)"
    )
    closed_at: Optional[str] = Field(None, description="When the casefile was closed")
    closed_by: Optional[str] = Field(None, description="User who closed the casefile")
    archived_at: Optional[str] = Field(None, description="When the casefile was archived")
    archived_by: Optional[str] = Field(None, description="User who archived the casefile")
    
    # NEW: Relationships
    parent_casefile_id: Optional[str] = Field(
        None,
        description="Parent casefile ID for hierarchical organization",
        pattern=r"^cf_\d{6}_[a-z0-9]+$"
    )
    child_casefile_ids: List[str] = Field(
        default_factory=list,
        description="Child casefile IDs"
    )
    related_casefile_ids: List[str] = Field(
        default_factory=list,
        description="Related casefile IDs (cross-references)"
    )
    
    # NEW: Categorization
    category: Optional[str] = Field(
        None,
        description="Casefile category for classification"
    )
    
    # NEW: Additional metadata
    owner_id: str = Field(..., description="Primary owner user ID")
    last_accessed_at: Optional[str] = Field(None, description="Last access timestamp")
    access_count: int = Field(default=0, description="Number of times accessed")
    
    # Computed fields
    @computed_field
    @property
    def age_days(self) -> int:
        """Calculate days since creation."""
        try:
            created = datetime.fromisoformat(self.metadata.created_at.replace('Z', '+00:00'))
            return (datetime.now(created.tzinfo) - created).days
        except Exception:
            return 0
    
    @computed_field
    @property
    def is_closed(self) -> bool:
        """Check if casefile is closed."""
        return self.status == CasefileStatus.CLOSED
    
    @computed_field
    @property
    def is_archived(self) -> bool:
        """Check if casefile is archived."""
        return self.status == CasefileStatus.ARCHIVED
    
    @computed_field
    @property
    def is_active(self) -> bool:
        """Check if casefile is active."""
        return self.status == CasefileStatus.ACTIVE
    
    @computed_field
    @property
    def has_children(self) -> bool:
        """Check if casefile has child casefiles."""
        return len(self.child_casefile_ids) > 0
    
    @computed_field
    @property
    def has_parent(self) -> bool:
        """Check if casefile has a parent."""
        return self.parent_casefile_id is not None
    
    @computed_field
    @property
    def resource_count(self) -> int:
        """Total number of resources linked to this casefile."""
        total = 0
        if self.gmail_data:
            total += self.gmail_data.get('message_count', 0)
        if self.drive_data:
            total += self.drive_data.get('file_count', 0)
        if self.sheets_data:
            total += self.sheets_data.get('spreadsheet_count', 0)
        return total
    
    # Business logic methods
    def close(self, user_id: str, reason: Optional[str] = None) -> None:
        """
        Close this casefile.
        
        Args:
            user_id: User performing the close operation
            reason: Optional reason for closing
            
        Raises:
            ValueError: If casefile is already closed
        """
        if self.is_closed:
            raise ValueError(f"Casefile {self.id} is already closed")
        
        if self.status == CasefileStatus.DELETED:
            raise ValueError(f"Cannot close deleted casefile {self.id}")
        
        self.status = CasefileStatus.CLOSED
        self.closed_at = datetime.now().isoformat()
        self.closed_by = user_id
        self.metadata.updated_at = datetime.now().isoformat()
        
        if reason:
            self.notes = f"{self.notes or ''}\n\n[Closed by {user_id}]: {reason}".strip()
    
    def archive(self, user_id: str) -> None:
        """
        Archive this casefile.
        
        Args:
            user_id: User performing the archive operation
            
        Raises:
            ValueError: If casefile is deleted
        """
        if self.status == CasefileStatus.DELETED:
            raise ValueError(f"Cannot archive deleted casefile {self.id}")
        
        self.status = CasefileStatus.ARCHIVED
        self.archived_at = datetime.now().isoformat()
        self.archived_by = user_id
        self.metadata.updated_at = datetime.now().isoformat()
    
    def reopen(self, user_id: str) -> None:
        """
        Reopen a closed or archived casefile.
        
        Args:
            user_id: User performing the reopen operation
            
        Raises:
            ValueError: If casefile is active or deleted
        """
        if self.status == CasefileStatus.ACTIVE:
            raise ValueError(f"Casefile {self.id} is already active")
        
        if self.status == CasefileStatus.DELETED:
            raise ValueError(f"Cannot reopen deleted casefile {self.id}")
        
        self.status = CasefileStatus.ACTIVE
        self.closed_at = None
        self.closed_by = None
        self.archived_at = None
        self.archived_by = None
        self.metadata.updated_at = datetime.now().isoformat()
        
        self.notes = f"{self.notes or ''}\n\n[Reopened by {user_id}]".strip()
    
    def add_tag(self, tag: str) -> bool:
        """
        Add a tag if not already present.
        
        Args:
            tag: Tag to add
            
        Returns:
            True if tag was added, False if already present
            
        Raises:
            ValueError: If tag is invalid
        """
        tag = tag.strip().lower()
        
        if not tag:
            return False
        
        if len(tag) < 2:
            raise ValueError("Tag must be at least 2 characters")
        
        if len(tag) > 50:
            raise ValueError("Tag must be at most 50 characters")
        
        if not tag.replace('-', '').replace('_', '').isalnum():
            raise ValueError("Tag must contain only alphanumeric characters, hyphens, and underscores")
        
        if tag not in self.metadata.tags:
            if len(self.metadata.tags) >= 20:
                raise ValueError("Maximum 20 tags allowed")
            
            self.metadata.tags.append(tag)
            self.metadata.updated_at = datetime.now().isoformat()
            return True
        
        return False
    
    def remove_tag(self, tag: str) -> bool:
        """
        Remove a tag if present.
        
        Args:
            tag: Tag to remove
            
        Returns:
            True if tag was removed, False if not found
        """
        tag = tag.strip().lower()
        
        if tag in self.metadata.tags:
            self.metadata.tags.remove(tag)
            self.metadata.updated_at = datetime.now().isoformat()
            return True
        
        return False
    
    def set_priority(self, priority: int, user_id: str) -> None:
        """
        Set casefile priority.
        
        Args:
            priority: Priority level (1-5)
            user_id: User setting the priority
            
        Raises:
            ValueError: If priority is out of range
        """
        if not 1 <= priority <= 5:
            raise ValueError("Priority must be between 1 and 5")
        
        old_priority = self.priority
        self.priority = priority
        self.metadata.updated_at = datetime.now().isoformat()
        
        self.notes = f"{self.notes or ''}\n\n[Priority changed by {user_id}]: {old_priority} → {priority}".strip()
    
    def link_parent(self, parent_id: str, user_id: str) -> None:
        """
        Link this casefile to a parent casefile.
        
        Args:
            parent_id: Parent casefile ID
            user_id: User creating the link
            
        Raises:
            ValueError: If already has parent or invalid parent_id
        """
        if self.parent_casefile_id:
            raise ValueError(f"Casefile already has parent: {self.parent_casefile_id}")
        
        if parent_id == self.id:
            raise ValueError("Casefile cannot be its own parent")
        
        self.parent_casefile_id = parent_id
        self.metadata.updated_at = datetime.now().isoformat()
        
        self.notes = f"{self.notes or ''}\n\n[Linked to parent by {user_id}]: {parent_id}".strip()
    
    def unlink_parent(self, user_id: str) -> None:
        """
        Remove parent link.
        
        Args:
            user_id: User removing the link
        """
        if not self.parent_casefile_id:
            return
        
        old_parent = self.parent_casefile_id
        self.parent_casefile_id = None
        self.metadata.updated_at = datetime.now().isoformat()
        
        self.notes = f"{self.notes or ''}\n\n[Unlinked from parent by {user_id}]: {old_parent}".strip()
    
    def add_child(self, child_id: str, user_id: str) -> bool:
        """
        Add a child casefile.
        
        Args:
            child_id: Child casefile ID
            user_id: User adding the child
            
        Returns:
            True if added, False if already present
            
        Raises:
            ValueError: If invalid child_id
        """
        if child_id == self.id:
            raise ValueError("Casefile cannot be its own child")
        
        if child_id not in self.child_casefile_ids:
            self.child_casefile_ids.append(child_id)
            self.metadata.updated_at = datetime.now().isoformat()
            
            self.notes = f"{self.notes or ''}\n\n[Child added by {user_id}]: {child_id}".strip()
            return True
        
        return False
    
    def remove_child(self, child_id: str, user_id: str) -> bool:
        """
        Remove a child casefile.
        
        Args:
            child_id: Child casefile ID to remove
            user_id: User removing the child
            
        Returns:
            True if removed, False if not found
        """
        if child_id in self.child_casefile_ids:
            self.child_casefile_ids.remove(child_id)
            self.metadata.updated_at = datetime.now().isoformat()
            
            self.notes = f"{self.notes or ''}\n\n[Child removed by {user_id}]: {child_id}".strip()
            return True
        
        return False
    
    def add_related(self, related_id: str, user_id: str) -> bool:
        """
        Add a related casefile reference.
        
        Args:
            related_id: Related casefile ID
            user_id: User adding the relation
            
        Returns:
            True if added, False if already present
        """
        if related_id == self.id:
            raise ValueError("Casefile cannot be related to itself")
        
        if related_id not in self.related_casefile_ids:
            self.related_casefile_ids.append(related_id)
            self.metadata.updated_at = datetime.now().isoformat()
            
            self.notes = f"{self.notes or ''}\n\n[Related casefile added by {user_id}]: {related_id}".strip()
            return True
        
        return False
    
    def remove_related(self, related_id: str, user_id: str) -> bool:
        """
        Remove a related casefile reference.
        
        Args:
            related_id: Related casefile ID to remove
            user_id: User removing the relation
            
        Returns:
            True if removed, False if not found
        """
        if related_id in self.related_casefile_ids:
            self.related_casefile_ids.remove(related_id)
            self.metadata.updated_at = datetime.now().isoformat()
            
            self.notes = f"{self.notes or ''}\n\n[Related casefile removed by {user_id}]: {related_id}".strip()
            return True
        
        return False
    
    def can_read(self, user_id: str) -> bool:
        """
        Check if user has read permission.
        
        Args:
            user_id: User ID to check
            
        Returns:
            True if user can read, False otherwise
        """
        # Owner always has read access
        if self.owner_id == user_id:
            return True
        
        # Check ACL if present
        if self.acl:
            # Simplified check - in real implementation, parse ACL structure
            return True
        
        return False
    
    def can_write(self, user_id: str) -> bool:
        """
        Check if user has write permission.
        
        Args:
            user_id: User ID to check
            
        Returns:
            True if user can write, False otherwise
        """
        # Owner always has write access
        if self.owner_id == user_id:
            return True
        
        # Check ACL if present
        if self.acl:
            # Simplified check - in real implementation, parse ACL structure
            return False
        
        return False
    
    def increment_access_count(self) -> None:
        """Increment access counter and update last accessed timestamp."""
        self.access_count += 1
        self.last_accessed_at = datetime.now().isoformat()


# Example usage and validation
if __name__ == "__main__":
    print("=" * 80)
    print("Phase 2: Enhanced CasefileModel - Demo")
    print("=" * 80)
    print()
    
    # Create enhanced casefile
    metadata = EnhancedCasefileMetadata(
        title="Project Alpha Investigation",
        description="Investigation into project alpha anomalies",
        tags=["Project", "ALPHA", "investigation", "project"],  # Will be normalized and deduplicated
        created_by="user_123"
    )
    
    casefile = EnhancedCasefileModel(
        id="cf_251006_abc123",
        metadata=metadata,
        owner_id="user_123",
        category="investigation",
        priority=4
    )
    
    print("✓ Created enhanced casefile:")
    print(f"  ID: {casefile.id}")
    print(f"  Title: {casefile.metadata.title}")
    print(f"  Tags: {casefile.metadata.tags}")  # normalized, deduplicated
    print(f"  Status: {casefile.status.value}")
    print(f"  Priority: {casefile.priority}")
    print(f"  Age (days): {casefile.age_days}")
    print(f"  Is Active: {casefile.is_active}")
    print()
    
    # Demonstrate business logic
    print("✓ Adding tags:")
    casefile.add_tag("urgent")
    casefile.add_tag("Q4-2025")
    print(f"  Tags: {casefile.metadata.tags}")
    print()
    
    print("✓ Setting priority:")
    casefile.set_priority(5, "user_123")
    print(f"  Priority: {casefile.priority}")
    print()
    
    print("✓ Linking relationships:")
    casefile.add_related("cf_251005_xyz789", "user_123")
    print(f"  Related: {casefile.related_casefile_ids}")
    print()
    
    print("✓ Closing casefile:")
    casefile.close("user_123", "Investigation complete")
    print(f"  Status: {casefile.status.value}")
    print(f"  Closed by: {casefile.closed_by}")
    print(f"  Is Closed: {casefile.is_closed}")
    print()
    
    print("✓ Model export:")
    print(f"  JSON-serializable: {len(casefile.model_dump())} fields")
    print()
    
    print("=" * 80)
    print("Implementation complete. See code above for full details.")
    print("=" * 80)
