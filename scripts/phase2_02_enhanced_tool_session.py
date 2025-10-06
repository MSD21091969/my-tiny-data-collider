"""
Phase 2: Enhanced ToolSession Implementation

This script demonstrates the complete implementation of ToolSession enhancements
as discussed in TOOL_ENGINEERING_ANALYSIS.md Phase 2.

Enhancements include:
- Session metadata (title, purpose, tags)
- Session statistics (request counts, success rates)
- Computed fields (success_rate, duration_seconds, average_duration)
- Business logic methods (record_request, calculate_metrics, is_stale)
- Session lifecycle management

Usage:
    This is a reference implementation showing the enhanced model structure.
    To integrate: Copy the enhancements to src/pydantic_models/canonical/tool_session.py
"""

from pydantic import BaseModel, Field, computed_field, field_validator
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from enum import Enum


class SessionStatus(str, Enum):
    """Status of a tool session."""
    ACTIVE = "active"
    IDLE = "idle"
    CLOSED = "closed"
    EXPIRED = "expired"


class CloseReason(str, Enum):
    """Reasons for closing a session."""
    USER_INITIATED = "user_initiated"
    TIMEOUT = "timeout"
    ERROR = "error"
    COMPLETED = "completed"
    ADMIN_CLOSED = "admin_closed"


class EnhancedToolSession(BaseModel):
    """
    Enhanced Tool Session Model with statistics, metrics, and business logic.
    
    This is the complete implementation based on Phase 2 analysis.
    Extends the current ToolSession with:
    - Session metadata (title, purpose, tags)
    - Request statistics (success/failure tracking)
    - Computed fields for analytics
    - Business logic methods
    - Session health monitoring
    """
    
    # Core fields (existing)
    session_id: str = Field(..., description="Unique session ID (ts_ prefix)")
    user_id: str = Field(..., description="User who created the session")
    casefile_id: Optional[str] = Field(
        None,
        description="Associated casefile ID",
        pattern=r"^cf_\d{6}_[a-z0-9]+$"
    )
    created_at: str = Field(
        default_factory=lambda: datetime.now().isoformat(),
        description="Session creation timestamp"
    )
    updated_at: str = Field(
        default_factory=lambda: datetime.now().isoformat(),
        description="Last update timestamp"
    )
    request_ids: List[str] = Field(
        default_factory=list,
        description="List of request IDs in this session"
    )
    active: bool = Field(default=True, description="Whether this session is active")
    
    # NEW: Session metadata
    title: Optional[str] = Field(
        None,
        description="Human-readable session title",
        max_length=200
    )
    purpose: Optional[str] = Field(
        None,
        description="Purpose or goal of this session",
        max_length=1000
    )
    tags: List[str] = Field(
        default_factory=list,
        description="Tags for session categorization"
    )
    
    # NEW: Session statistics
    total_requests: int = Field(
        default=0,
        ge=0,
        description="Total number of requests in this session"
    )
    successful_requests: int = Field(
        default=0,
        ge=0,
        description="Number of successful requests"
    )
    failed_requests: int = Field(
        default=0,
        ge=0,
        description="Number of failed requests"
    )
    
    # NEW: Performance metrics
    total_execution_time_ms: int = Field(
        default=0,
        ge=0,
        description="Cumulative execution time in milliseconds"
    )
    
    # NEW: Session lifecycle
    closed_at: Optional[str] = Field(
        None,
        description="When the session was closed"
    )
    close_reason: Optional[str] = Field(
        None,
        description="Reason for closing the session"
    )
    last_activity_at: Optional[str] = Field(
        None,
        description="Last activity timestamp (request or access)"
    )
    
    # NEW: Session context
    client_info: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Client information (user agent, IP, etc.)"
    )
    session_metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional session metadata"
    )
    
    @field_validator('tags')
    @classmethod
    def validate_tags(cls, v: List[str]) -> List[str]:
        """Normalize and deduplicate tags."""
        if not v:
            return []
        
        # Normalize: strip, lowercase
        normalized = [tag.strip().lower() for tag in v if tag.strip()]
        
        # Deduplicate
        unique = list(dict.fromkeys(normalized))
        
        # Validate max tags
        if len(unique) > 10:
            raise ValueError("Maximum 10 tags allowed per session")
        
        return unique
    
    # Computed fields
    @computed_field
    @property
    def success_rate(self) -> float:
        """
        Calculate success rate as percentage.
        
        Returns:
            Success rate (0.0 to 1.0)
        """
        if self.total_requests == 0:
            return 0.0
        return self.successful_requests / self.total_requests
    
    @computed_field
    @property
    def failure_rate(self) -> float:
        """
        Calculate failure rate as percentage.
        
        Returns:
            Failure rate (0.0 to 1.0)
        """
        if self.total_requests == 0:
            return 0.0
        return self.failed_requests / self.total_requests
    
    @computed_field
    @property
    def duration_seconds(self) -> Optional[int]:
        """
        Calculate session duration in seconds.
        
        Returns:
            Duration in seconds, or None if session is still active
        """
        if not self.closed_at:
            return None
        
        try:
            created = datetime.fromisoformat(self.created_at.replace('Z', '+00:00'))
            closed = datetime.fromisoformat(self.closed_at.replace('Z', '+00:00'))
            return int((closed - created).total_seconds())
        except Exception:
            return None
    
    @computed_field
    @property
    def age_seconds(self) -> int:
        """
        Calculate session age in seconds.
        
        Returns:
            Age in seconds
        """
        try:
            created = datetime.fromisoformat(self.created_at.replace('Z', '+00:00'))
            return int((datetime.now(created.tzinfo) - created).total_seconds())
        except Exception:
            return 0
    
    @computed_field
    @property
    def average_request_time_ms(self) -> float:
        """
        Calculate average execution time per request.
        
        Returns:
            Average execution time in milliseconds
        """
        if self.total_requests == 0:
            return 0.0
        return self.total_execution_time_ms / self.total_requests
    
    @computed_field
    @property
    def is_idle(self) -> bool:
        """
        Check if session is idle (no activity for over 30 minutes).
        
        Returns:
            True if session is idle
        """
        if not self.last_activity_at:
            # Use updated_at as fallback
            activity_time = self.updated_at
        else:
            activity_time = self.last_activity_at
        
        try:
            last_activity = datetime.fromisoformat(activity_time.replace('Z', '+00:00'))
            idle_threshold = datetime.now(last_activity.tzinfo) - timedelta(minutes=30)
            return last_activity < idle_threshold
        except Exception:
            return False
    
    @computed_field
    @property
    def is_stale(self) -> bool:
        """
        Check if session is stale (no activity for over 24 hours).
        
        Returns:
            True if session is stale
        """
        if not self.last_activity_at:
            activity_time = self.updated_at
        else:
            activity_time = self.last_activity_at
        
        try:
            last_activity = datetime.fromisoformat(activity_time.replace('Z', '+00:00'))
            stale_threshold = datetime.now(last_activity.tzinfo) - timedelta(hours=24)
            return last_activity < stale_threshold
        except Exception:
            return False
    
    @computed_field
    @property
    def status(self) -> SessionStatus:
        """
        Determine current session status.
        
        Returns:
            SessionStatus enum value
        """
        if not self.active:
            return SessionStatus.CLOSED
        
        if self.is_stale:
            return SessionStatus.EXPIRED
        
        if self.is_idle:
            return SessionStatus.IDLE
        
        return SessionStatus.ACTIVE
    
    @computed_field
    @property
    def has_casefile(self) -> bool:
        """Check if session has associated casefile."""
        return self.casefile_id is not None
    
    # Business logic methods
    def record_request(
        self,
        request_id: str,
        success: bool,
        execution_time_ms: int
    ) -> None:
        """
        Record a request execution.
        
        Args:
            request_id: Request ID
            success: Whether request was successful
            execution_time_ms: Execution time in milliseconds
        """
        # Add request ID if not already present
        if request_id not in self.request_ids:
            self.request_ids.append(request_id)
        
        # Update statistics
        self.total_requests += 1
        if success:
            self.successful_requests += 1
        else:
            self.failed_requests += 1
        
        # Update performance metrics
        self.total_execution_time_ms += execution_time_ms
        
        # Update timestamps
        now = datetime.now().isoformat()
        self.updated_at = now
        self.last_activity_at = now
    
    def close_session(
        self,
        reason: str = CloseReason.USER_INITIATED,
        user_id: Optional[str] = None
    ) -> None:
        """
        Close this session.
        
        Args:
            reason: Reason for closing
            user_id: Optional user ID who closed the session
            
        Raises:
            ValueError: If session is already closed
        """
        if not self.active:
            raise ValueError(f"Session {self.session_id} is already closed")
        
        self.active = False
        self.closed_at = datetime.now().isoformat()
        self.close_reason = reason
        self.updated_at = datetime.now().isoformat()
        
        if user_id:
            self.session_metadata['closed_by'] = user_id
    
    def add_tag(self, tag: str) -> bool:
        """
        Add a tag to this session.
        
        Args:
            tag: Tag to add
            
        Returns:
            True if added, False if already present
        """
        tag = tag.strip().lower()
        
        if not tag:
            return False
        
        if tag not in self.tags:
            if len(self.tags) >= 10:
                raise ValueError("Maximum 10 tags allowed per session")
            
            self.tags.append(tag)
            self.updated_at = datetime.now().isoformat()
            return True
        
        return False
    
    def remove_tag(self, tag: str) -> bool:
        """
        Remove a tag from this session.
        
        Args:
            tag: Tag to remove
            
        Returns:
            True if removed, False if not found
        """
        tag = tag.strip().lower()
        
        if tag in self.tags:
            self.tags.remove(tag)
            self.updated_at = datetime.now().isoformat()
            return True
        
        return False
    
    def associate_casefile(self, casefile_id: str, user_id: str) -> None:
        """
        Associate a casefile with this session.
        
        Args:
            casefile_id: Casefile ID to associate
            user_id: User performing the association
            
        Raises:
            ValueError: If session already has a casefile
        """
        if self.casefile_id:
            raise ValueError(
                f"Session already associated with casefile: {self.casefile_id}"
            )
        
        self.casefile_id = casefile_id
        self.updated_at = datetime.now().isoformat()
        self.session_metadata['casefile_associated_by'] = user_id
        self.session_metadata['casefile_associated_at'] = datetime.now().isoformat()
    
    def disassociate_casefile(self, user_id: str) -> None:
        """
        Remove casefile association.
        
        Args:
            user_id: User performing the disassociation
        """
        if not self.casefile_id:
            return
        
        old_casefile = self.casefile_id
        self.casefile_id = None
        self.updated_at = datetime.now().isoformat()
        self.session_metadata['casefile_disassociated_by'] = user_id
        self.session_metadata['casefile_disassociated_at'] = datetime.now().isoformat()
        self.session_metadata['previous_casefile_id'] = old_casefile
    
    def update_activity(self) -> None:
        """Update last activity timestamp."""
        now = datetime.now().isoformat()
        self.last_activity_at = now
        self.updated_at = now
    
    def get_metrics(self) -> Dict[str, Any]:
        """
        Get session metrics summary.
        
        Returns:
            Dictionary of metrics
        """
        return {
            'session_id': self.session_id,
            'status': self.status.value,
            'total_requests': self.total_requests,
            'successful_requests': self.successful_requests,
            'failed_requests': self.failed_requests,
            'success_rate': round(self.success_rate * 100, 2),
            'failure_rate': round(self.failure_rate * 100, 2),
            'average_request_time_ms': round(self.average_request_time_ms, 2),
            'total_execution_time_ms': self.total_execution_time_ms,
            'age_seconds': self.age_seconds,
            'duration_seconds': self.duration_seconds,
            'is_idle': self.is_idle,
            'is_stale': self.is_stale,
            'has_casefile': self.has_casefile,
            'casefile_id': self.casefile_id,
        }
    
    def should_auto_close(self) -> bool:
        """
        Determine if session should be automatically closed.
        
        Returns:
            True if session should be auto-closed
        """
        # Auto-close if stale (24+ hours inactive)
        if self.is_stale:
            return True
        
        # Auto-close if idle with no requests
        if self.is_idle and self.total_requests == 0:
            return True
        
        return False
    
    def get_health_status(self) -> Dict[str, Any]:
        """
        Get session health status.
        
        Returns:
            Dictionary with health indicators
        """
        health = {
            'healthy': True,
            'warnings': [],
            'issues': []
        }
        
        # Check for issues
        if self.failure_rate > 0.5:
            health['issues'].append('High failure rate (>50%)')
            health['healthy'] = False
        
        if self.is_stale:
            health['issues'].append('Session is stale (>24h inactive)')
            health['healthy'] = False
        
        # Check for warnings
        if self.is_idle:
            health['warnings'].append('Session is idle (>30min inactive)')
        
        if self.failure_rate > 0.2:
            health['warnings'].append('Elevated failure rate (>20%)')
        
        if self.average_request_time_ms > 5000:
            health['warnings'].append('High average request time (>5s)')
        
        return health


# Example usage and validation
if __name__ == "__main__":
    print("=" * 80)
    print("Phase 2: Enhanced ToolSession - Demo")
    print("=" * 80)
    print()
    
    # Create enhanced session
    session = EnhancedToolSession(
        session_id="ts_251006_xyz123",
        user_id="user_123",
        title="Data Analysis Session",
        purpose="Analyze project metrics and generate reports",
        tags=["analysis", "REPORTING", "q4-2025", "analysis"]  # Will be normalized
    )
    
    print("✓ Created enhanced session:")
    print(f"  ID: {session.session_id}")
    print(f"  Title: {session.title}")
    print(f"  Tags: {session.tags}")
    print(f"  Status: {session.status.value}")
    print(f"  Success Rate: {session.success_rate * 100:.1f}%")
    print()
    
    # Simulate requests
    print("✓ Recording requests:")
    session.record_request("req_001", success=True, execution_time_ms=1234)
    session.record_request("req_002", success=True, execution_time_ms=987)
    session.record_request("req_003", success=False, execution_time_ms=5000)
    session.record_request("req_004", success=True, execution_time_ms=1500)
    
    print(f"  Total: {session.total_requests}")
    print(f"  Successful: {session.successful_requests}")
    print(f"  Failed: {session.failed_requests}")
    print(f"  Success Rate: {session.success_rate * 100:.1f}%")
    print(f"  Avg Time: {session.average_request_time_ms:.0f}ms")
    print()
    
    # Associate casefile
    print("✓ Associating casefile:")
    session.associate_casefile("cf_251006_abc789", "user_123")
    print(f"  Casefile: {session.casefile_id}")
    print(f"  Has Casefile: {session.has_casefile}")
    print()
    
    # Get metrics
    print("✓ Session metrics:")
    metrics = session.get_metrics()
    for key, value in metrics.items():
        if value is not None:
            print(f"  {key}: {value}")
    print()
    
    # Health check
    print("✓ Health status:")
    health = session.get_health_status()
    print(f"  Healthy: {health['healthy']}")
    if health['warnings']:
        print(f"  Warnings: {health['warnings']}")
    if health['issues']:
        print(f"  Issues: {health['issues']}")
    print()
    
    print("=" * 80)
    print("Implementation complete. See code above for full details.")
    print("=" * 80)
