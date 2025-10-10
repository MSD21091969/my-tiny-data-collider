"""
Canonical Access Control List (ACL) models for casefile permissions.

This module contains the ACL entity and its components:
- PermissionLevel: Enum defining permission hierarchy
- PermissionEntry: Single permission grant for a user
- CasefileACL: The ACL entity with permission checking logic

For ACL operations (grant, revoke, list, check), see pydantic_models.operations.casefile_ops
"""

from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class PermissionLevel(str, Enum):
    """Permission levels for casefile access."""
    OWNER = "owner"       # Full control, can delete, manage permissions
    ADMIN = "admin"       # Can edit, share, but not delete
    EDITOR = "editor"     # Can edit content but not share
    VIEWER = "viewer"     # Read-only access
    NONE = "none"         # No access


class PermissionEntry(BaseModel):
    """Single permission entry for a user on a casefile."""
    user_id: str = Field(..., description="User ID granted permission")
    permission: PermissionLevel = Field(..., description="Level of access granted")
    granted_by: str = Field(..., description="User who granted this permission")
    granted_at: str = Field(
        default_factory=lambda: datetime.now().isoformat(),
        description="When permission was granted"
    )
    expires_at: Optional[str] = Field(None, description="Optional expiration timestamp")
    notes: Optional[str] = Field(None, description="Optional notes about this permission")


class CasefileACL(BaseModel):
    """Access Control List for a casefile."""
    owner_id: str = Field(..., description="Casefile owner (has all permissions)")
    permissions: List[PermissionEntry] = Field(
        default_factory=list,
        description="List of user permissions"
    )
    public_access: PermissionLevel = Field(
        default=PermissionLevel.NONE,
        description="Default access level for all users"
    )
    inherit_from_parent: bool = Field(
        default=False,
        description="Whether to inherit permissions from parent (future use)"
    )
    
    def get_user_permission(self, user_id: str) -> PermissionLevel:
        """Get effective permission level for a user.
        
        Args:
            user_id: User ID to check
            
        Returns:
            PermissionLevel for the user
        """
        # Owner has full access
        if user_id == self.owner_id:
            return PermissionLevel.OWNER
        
        # Check explicit permissions
        for entry in self.permissions:
            if entry.user_id == user_id:
                # Check if expired
                if entry.expires_at:
                    if datetime.fromisoformat(entry.expires_at) < datetime.now():
                        continue
                return entry.permission
        
        # Fall back to public access
        return self.public_access
    
    def has_permission(self, user_id: str, required_level: PermissionLevel) -> bool:
        """Check if user has at least the required permission level.
        
        Args:
            user_id: User ID to check
            required_level: Minimum permission level required
            
        Returns:
            True if user has required permission or higher
        """
        user_level = self.get_user_permission(user_id)
        
        # Permission hierarchy (higher level includes lower permissions)
        hierarchy = {
            PermissionLevel.OWNER: 4,
            PermissionLevel.ADMIN: 3,
            PermissionLevel.EDITOR: 2,
            PermissionLevel.VIEWER: 1,
            PermissionLevel.NONE: 0,
        }
        
        return hierarchy.get(user_level, 0) >= hierarchy.get(required_level, 0)
    
    def can_read(self, user_id: str) -> bool:
        """Check if user can read casefile."""
        return self.has_permission(user_id, PermissionLevel.VIEWER)
    
    def can_write(self, user_id: str) -> bool:
        """Check if user can edit casefile."""
        return self.has_permission(user_id, PermissionLevel.EDITOR)
    
    def can_share(self, user_id: str) -> bool:
        """Check if user can manage permissions."""
        return self.has_permission(user_id, PermissionLevel.ADMIN)
    
    def can_delete(self, user_id: str) -> bool:
        """Check if user can delete casefile."""
        return user_id == self.owner_id
