"""
Phase 2: UserModel Implementation

This script demonstrates the implementation of UserModel as a new canonical model
as discussed in TOOL_ENGINEERING_ANALYSIS.md Phase 2.

The UserModel represents users in the system with:
- User identification and profile information
- Permission and role management
- User preferences and settings
- Activity tracking
- Business logic methods

Usage:
    This is a reference implementation showing the UserModel structure.
    To integrate: Create new file src/pydantic_models/canonical/user.py
"""

from pydantic import BaseModel, Field, field_validator, computed_field, EmailStr
from typing import Dict, Any, List, Optional, Set
from datetime import datetime
from enum import Enum


class UserStatus(str, Enum):
    """Status of a user account."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    DELETED = "deleted"


class UserRole(str, Enum):
    """Standard user roles."""
    ADMIN = "admin"
    USER = "user"
    VIEWER = "viewer"
    ANALYST = "analyst"
    MANAGER = "manager"
    DEVELOPER = "developer"


class PermissionScope(str, Enum):
    """Permission scopes in the system."""
    CASEFILE_CREATE = "casefile:create"
    CASEFILE_READ = "casefile:read"
    CASEFILE_UPDATE = "casefile:update"
    CASEFILE_DELETE = "casefile:delete"
    CASEFILE_SHARE = "casefile:share"
    SESSION_CREATE = "session:create"
    SESSION_READ = "session:read"
    SESSION_MANAGE = "session:manage"
    TOOL_EXECUTE = "tool:execute"
    TOOL_ADMIN = "tool:admin"
    WORKSPACE_ACCESS = "workspace:access"
    USER_MANAGE = "user:manage"
    ADMIN_ACCESS = "admin:access"


class UserPreferences(BaseModel):
    """User preferences and settings."""
    
    # Display preferences
    theme: str = Field(default="light", description="UI theme (light, dark, auto)")
    language: str = Field(default="en", description="Preferred language code")
    timezone: str = Field(default="UTC", description="User timezone")
    date_format: str = Field(default="YYYY-MM-DD", description="Preferred date format")
    time_format: str = Field(default="24h", description="Time format (12h, 24h)")
    
    # Notification preferences
    email_notifications: bool = Field(default=True, description="Enable email notifications")
    push_notifications: bool = Field(default=False, description="Enable push notifications")
    notification_frequency: str = Field(default="realtime", description="Notification frequency")
    
    # Tool preferences
    default_tool_view: str = Field(default="list", description="Default tool view")
    auto_close_sessions: bool = Field(default=False, description="Auto-close idle sessions")
    session_timeout_minutes: int = Field(default=30, ge=5, le=480, description="Session timeout")
    
    # Custom settings
    custom_settings: Dict[str, Any] = Field(
        default_factory=dict,
        description="Custom user settings"
    )


class UserProfile(BaseModel):
    """User profile information."""
    
    display_name: str = Field(..., description="Display name", min_length=1, max_length=100)
    email: EmailStr = Field(..., description="Email address")
    
    # Optional profile fields
    first_name: Optional[str] = Field(None, description="First name", max_length=50)
    last_name: Optional[str] = Field(None, description="Last name", max_length=50)
    phone: Optional[str] = Field(None, description="Phone number", max_length=20)
    avatar_url: Optional[str] = Field(None, description="Avatar image URL")
    bio: Optional[str] = Field(None, description="User biography", max_length=500)
    
    # Organization info
    organization: Optional[str] = Field(None, description="Organization name", max_length=100)
    department: Optional[str] = Field(None, description="Department", max_length=100)
    job_title: Optional[str] = Field(None, description="Job title", max_length=100)
    
    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v: Optional[str]) -> Optional[str]:
        """Validate phone number format."""
        if v is None:
            return v
        
        # Remove common formatting characters
        cleaned = ''.join(c for c in v if c.isdigit() or c == '+')
        
        if not cleaned:
            return None
        
        if len(cleaned) < 10:
            raise ValueError("Phone number too short")
        
        return v


class UserModel(BaseModel):
    """
    Complete User Model representing system users.
    
    This is a new canonical model for Phase 2 implementation.
    Provides:
    - User identification and authentication context
    - Profile information management
    - Permission and role-based access control
    - User preferences and settings
    - Activity tracking and statistics
    - Business logic for permission checks
    """
    
    # Core identification
    user_id: str = Field(..., description="Unique user ID")
    profile: UserProfile = Field(..., description="User profile information")
    
    # Status and lifecycle
    status: UserStatus = Field(
        default=UserStatus.ACTIVE,
        description="Current user status"
    )
    created_at: str = Field(
        default_factory=lambda: datetime.now().isoformat(),
        description="Account creation timestamp"
    )
    updated_at: str = Field(
        default_factory=lambda: datetime.now().isoformat(),
        description="Last update timestamp"
    )
    
    # Authentication context
    last_login_at: Optional[str] = Field(
        None,
        description="Last login timestamp"
    )
    last_active_at: Optional[str] = Field(
        None,
        description="Last activity timestamp"
    )
    login_count: int = Field(
        default=0,
        ge=0,
        description="Total number of logins"
    )
    
    # Access control
    roles: List[str] = Field(
        default_factory=list,
        description="User roles for role-based access"
    )
    permissions: List[str] = Field(
        default_factory=list,
        description="Explicit permissions granted to user"
    )
    
    # Preferences
    preferences: UserPreferences = Field(
        default_factory=UserPreferences,
        description="User preferences and settings"
    )
    
    # Activity and statistics
    casefile_count: int = Field(default=0, ge=0, description="Number of casefiles owned")
    session_count: int = Field(default=0, ge=0, description="Number of sessions created")
    total_requests: int = Field(default=0, ge=0, description="Total tool requests made")
    
    # Metadata
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional user metadata"
    )
    
    @field_validator('roles')
    @classmethod
    def validate_roles(cls, v: List[str]) -> List[str]:
        """Validate and deduplicate roles."""
        if not v:
            return []
        
        # Normalize to lowercase
        normalized = [role.lower() for role in v if role.strip()]
        
        # Deduplicate
        unique = list(dict.fromkeys(normalized))
        
        return unique
    
    @field_validator('permissions')
    @classmethod
    def validate_permissions(cls, v: List[str]) -> List[str]:
        """Validate and deduplicate permissions."""
        if not v:
            return []
        
        # Normalize to lowercase
        normalized = [perm.lower() for perm in v if perm.strip()]
        
        # Deduplicate
        unique = list(dict.fromkeys(normalized))
        
        return unique
    
    # Computed fields
    @computed_field
    @property
    def is_active(self) -> bool:
        """Check if user is active."""
        return self.status == UserStatus.ACTIVE
    
    @computed_field
    @property
    def is_admin(self) -> bool:
        """Check if user has admin role."""
        return "admin" in self.roles
    
    @computed_field
    @property
    def full_name(self) -> Optional[str]:
        """Get full name if available."""
        if self.profile.first_name and self.profile.last_name:
            return f"{self.profile.first_name} {self.profile.last_name}"
        return None
    
    @computed_field
    @property
    def account_age_days(self) -> int:
        """Calculate account age in days."""
        try:
            created = datetime.fromisoformat(self.created_at.replace('Z', '+00:00'))
            return (datetime.now(created.tzinfo) - created).days
        except Exception:
            return 0
    
    @computed_field
    @property
    def all_permissions(self) -> Set[str]:
        """Get all permissions (from roles + explicit permissions)."""
        perms = set(self.permissions)
        
        # Add role-based permissions
        role_permission_map = {
            'admin': [
                'casefile:create', 'casefile:read', 'casefile:update', 
                'casefile:delete', 'casefile:share', 'session:create',
                'session:read', 'session:manage', 'tool:execute',
                'tool:admin', 'workspace:access', 'user:manage', 'admin:access'
            ],
            'manager': [
                'casefile:create', 'casefile:read', 'casefile:update',
                'casefile:share', 'session:create', 'session:read',
                'session:manage', 'tool:execute', 'workspace:access'
            ],
            'analyst': [
                'casefile:create', 'casefile:read', 'casefile:update',
                'session:create', 'session:read', 'tool:execute',
                'workspace:access'
            ],
            'user': [
                'casefile:create', 'casefile:read', 'session:create',
                'session:read', 'tool:execute', 'workspace:access'
            ],
            'viewer': [
                'casefile:read', 'session:read', 'workspace:access'
            ],
            'developer': [
                'casefile:read', 'tool:execute', 'tool:admin',
                'workspace:access', 'session:create', 'session:read'
            ]
        }
        
        for role in self.roles:
            if role in role_permission_map:
                perms.update(role_permission_map[role])
        
        return perms
    
    # Business logic methods
    def has_permission(self, permission: str) -> bool:
        """
        Check if user has a specific permission.
        
        Args:
            permission: Permission to check (e.g., 'casefile:create')
            
        Returns:
            True if user has permission
        """
        if not self.is_active:
            return False
        
        # Admins have all permissions
        if self.is_admin:
            return True
        
        # Check explicit permission
        permission_lower = permission.lower()
        return permission_lower in self.all_permissions
    
    def has_role(self, role: str) -> bool:
        """
        Check if user has a specific role.
        
        Args:
            role: Role to check
            
        Returns:
            True if user has role
        """
        return role.lower() in self.roles
    
    def grant_permission(self, permission: str) -> bool:
        """
        Grant a permission to the user.
        
        Args:
            permission: Permission to grant
            
        Returns:
            True if permission was added, False if already present
        """
        permission_lower = permission.lower()
        
        if permission_lower not in self.permissions:
            self.permissions.append(permission_lower)
            self.updated_at = datetime.now().isoformat()
            return True
        
        return False
    
    def revoke_permission(self, permission: str) -> bool:
        """
        Revoke a permission from the user.
        
        Args:
            permission: Permission to revoke
            
        Returns:
            True if permission was removed, False if not found
        """
        permission_lower = permission.lower()
        
        if permission_lower in self.permissions:
            self.permissions.remove(permission_lower)
            self.updated_at = datetime.now().isoformat()
            return True
        
        return False
    
    def assign_role(self, role: str) -> bool:
        """
        Assign a role to the user.
        
        Args:
            role: Role to assign
            
        Returns:
            True if role was added, False if already present
        """
        role_lower = role.lower()
        
        if role_lower not in self.roles:
            self.roles.append(role_lower)
            self.updated_at = datetime.now().isoformat()
            return True
        
        return False
    
    def remove_role(self, role: str) -> bool:
        """
        Remove a role from the user.
        
        Args:
            role: Role to remove
            
        Returns:
            True if role was removed, False if not found
        """
        role_lower = role.lower()
        
        if role_lower in self.roles:
            self.roles.remove(role_lower)
            self.updated_at = datetime.now().isoformat()
            return True
        
        return False
    
    def activate(self) -> None:
        """Activate user account."""
        if self.status == UserStatus.DELETED:
            raise ValueError("Cannot activate deleted user")
        
        self.status = UserStatus.ACTIVE
        self.updated_at = datetime.now().isoformat()
    
    def deactivate(self, reason: Optional[str] = None) -> None:
        """
        Deactivate user account.
        
        Args:
            reason: Optional reason for deactivation
        """
        self.status = UserStatus.INACTIVE
        self.updated_at = datetime.now().isoformat()
        
        if reason:
            self.metadata['deactivation_reason'] = reason
            self.metadata['deactivated_at'] = datetime.now().isoformat()
    
    def suspend(self, reason: Optional[str] = None) -> None:
        """
        Suspend user account.
        
        Args:
            reason: Optional reason for suspension
        """
        self.status = UserStatus.SUSPENDED
        self.updated_at = datetime.now().isoformat()
        
        if reason:
            self.metadata['suspension_reason'] = reason
            self.metadata['suspended_at'] = datetime.now().isoformat()
    
    def record_login(self) -> None:
        """Record a user login."""
        now = datetime.now().isoformat()
        self.last_login_at = now
        self.last_active_at = now
        self.login_count += 1
        self.updated_at = now
    
    def record_activity(self) -> None:
        """Update last activity timestamp."""
        now = datetime.now().isoformat()
        self.last_active_at = now
        self.updated_at = now
    
    def increment_casefile_count(self, delta: int = 1) -> None:
        """
        Increment casefile count.
        
        Args:
            delta: Amount to increment (can be negative)
        """
        self.casefile_count = max(0, self.casefile_count + delta)
        self.updated_at = datetime.now().isoformat()
    
    def increment_session_count(self, delta: int = 1) -> None:
        """
        Increment session count.
        
        Args:
            delta: Amount to increment (can be negative)
        """
        self.session_count = max(0, self.session_count + delta)
        self.updated_at = datetime.now().isoformat()
    
    def increment_request_count(self, delta: int = 1) -> None:
        """
        Increment request count.
        
        Args:
            delta: Amount to increment (can be negative)
        """
        self.total_requests = max(0, self.total_requests + delta)
        self.updated_at = datetime.now().isoformat()
    
    def update_profile(self, **kwargs) -> None:
        """
        Update profile fields.
        
        Args:
            **kwargs: Profile fields to update
        """
        for key, value in kwargs.items():
            if hasattr(self.profile, key):
                setattr(self.profile, key, value)
        
        self.updated_at = datetime.now().isoformat()
    
    def get_summary(self) -> Dict[str, Any]:
        """
        Get user summary.
        
        Returns:
            Dictionary with user summary information
        """
        return {
            'user_id': self.user_id,
            'display_name': self.profile.display_name,
            'email': self.profile.email,
            'status': self.status.value,
            'is_active': self.is_active,
            'is_admin': self.is_admin,
            'roles': self.roles,
            'permission_count': len(self.all_permissions),
            'casefile_count': self.casefile_count,
            'session_count': self.session_count,
            'total_requests': self.total_requests,
            'account_age_days': self.account_age_days,
            'login_count': self.login_count,
            'last_login_at': self.last_login_at,
        }


# Example usage and validation
if __name__ == "__main__":
    print("=" * 80)
    print("Phase 2: UserModel - Demo")
    print("=" * 80)
    print()
    
    # Create user profile
    profile = UserProfile(
        display_name="Alice Johnson",
        email="alice.johnson@example.com",
        first_name="Alice",
        last_name="Johnson",
        job_title="Senior Analyst",
        department="Data Analytics"
    )
    
    # Create user
    user = UserModel(
        user_id="user_alice_123",
        profile=profile,
        roles=["analyst", "user"]
    )
    
    print("✓ Created user:")
    print(f"  ID: {user.user_id}")
    print(f"  Name: {user.profile.display_name}")
    print(f"  Email: {user.profile.email}")
    print(f"  Roles: {user.roles}")
    print(f"  Status: {user.status.value}")
    print()
    
    # Check permissions
    print("✓ Permission checks:")
    print(f"  Can create casefile: {user.has_permission('casefile:create')}")
    print(f"  Can delete casefile: {user.has_permission('casefile:delete')}")
    print(f"  Can manage users: {user.has_permission('user:manage')}")
    print(f"  Total permissions: {len(user.all_permissions)}")
    print()
    
    # Grant additional permission
    print("✓ Granting permission:")
    user.grant_permission("casefile:delete")
    print(f"  Can delete casefile: {user.has_permission('casefile:delete')}")
    print()
    
    # Assign role
    print("✓ Assigning role:")
    user.assign_role("manager")
    print(f"  Roles: {user.roles}")
    print(f"  Total permissions: {len(user.all_permissions)}")
    print()
    
    # Record activity
    print("✓ Recording activity:")
    user.record_login()
    user.increment_casefile_count(3)
    user.increment_session_count(5)
    user.increment_request_count(15)
    print(f"  Login count: {user.login_count}")
    print(f"  Casefiles: {user.casefile_count}")
    print(f"  Sessions: {user.session_count}")
    print(f"  Requests: {user.total_requests}")
    print()
    
    # Get summary
    print("✓ User summary:")
    summary = user.get_summary()
    for key, value in summary.items():
        if value is not None:
            print(f"  {key}: {value}")
    print()
    
    print("=" * 80)
    print("Implementation complete. See code above for full details.")
    print("=" * 80)
