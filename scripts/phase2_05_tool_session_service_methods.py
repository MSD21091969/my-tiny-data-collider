"""
Phase 2: ToolSessionService New Methods Implementation

This script demonstrates the implementation of 4 new service methods for ToolSessionService
as discussed in TOOL_ENGINEERING_ANALYSIS.md Phase 2.

New methods include:
1. get_session_metrics - Performance metrics and success rates
2. get_session_timeline - Chronological event view
3. export_session_logs - Complete audit trail export
4. close_inactive_sessions - Bulk close idle sessions

Usage:
    This is a reference implementation showing the complete method patterns.
    To integrate: Add these methods to src/tool_sessionservice/service.py
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel, Field
import json
import logging

logger = logging.getLogger(__name__)


# ============================================================================
# REQUEST/RESPONSE MODELS FOR NEW OPERATIONS
# ============================================================================

class SessionMetricsPayload(BaseModel):
    """Payload for session metrics request."""
    session_id: str = Field(..., description="Session ID")
    include_detailed_stats: bool = Field(default=False, description="Include detailed statistics")


class SessionTimelinePayload(BaseModel):
    """Payload for session timeline request."""
    session_id: str = Field(..., description="Session ID")
    event_types: Optional[List[str]] = Field(None, description="Filter by event types")
    limit: int = Field(default=100, ge=1, le=1000, description="Max events to return")


class ExportSessionLogsPayload(BaseModel):
    """Payload for export logs request."""
    session_id: str = Field(..., description="Session ID")
    format: str = Field(default="json", description="Export format: json, csv, txt")
    include_metadata: bool = Field(default=True, description="Include metadata")


class CloseInactiveSessionsPayload(BaseModel):
    """Payload for closing inactive sessions."""
    inactive_hours: int = Field(default=24, ge=1, le=720, description="Hours of inactivity")
    user_id: Optional[str] = Field(None, description="Filter by user (admin only)")
    dry_run: bool = Field(default=False, description="Preview without closing")


# ============================================================================
# SERVICE METHOD IMPLEMENTATIONS
# ============================================================================

class ToolSessionServiceExtended:
    """
    Extended ToolSessionService with Phase 2 methods.
    
    This class demonstrates the implementation of 4 new service methods
    following the established patterns in the codebase.
    """
    
    def __init__(self):
        """Initialize the service."""
        # In real implementation: self.repository = ToolSessionRepository()
        pass
    
    # ------------------------------------------------------------------------
    # 1. GET SESSION METRICS
    # ------------------------------------------------------------------------
    
    async def get_session_metrics(self, request) -> Dict[str, Any]:
        """
        Get performance metrics and statistics for a session.
        
        Returns:
        - Total/successful/failed request counts
        - Success rate
        - Average execution time
        - Request distribution over time
        - Tool usage statistics
        - Error analysis
        
        Args:
            request: Request with session_id
            
        Returns:
            Response with comprehensive session metrics
        """
        start_time = datetime.now()
        user_id = request.user_id
        session_id = request.payload.session_id
        include_detailed = request.payload.include_detailed_stats
        
        # Get session
        # session = await self.repository.get_session(session_id)
        session = None  # Placeholder
        
        if not session:
            execution_time_ms = int((datetime.now() - start_time).total_seconds() * 1000)
            return {
                'request_id': request.request_id,
                'status': 'FAILED',
                'error': f'Session {session_id} not found',
                'payload': {},
                'metadata': {'execution_time_ms': execution_time_ms}
            }
        
        # Verify access
        if session.get('user_id') != user_id:
            execution_time_ms = int((datetime.now() - start_time).total_seconds() * 1000)
            return {
                'request_id': request.request_id,
                'status': 'FAILED',
                'error': 'Insufficient permissions',
                'payload': {},
                'metadata': {'execution_time_ms': execution_time_ms}
            }
        
        # Calculate basic metrics
        metrics = {
            'session_id': session_id,
            'total_requests': session.get('total_requests', 0),
            'successful_requests': session.get('successful_requests', 0),
            'failed_requests': session.get('failed_requests', 0),
            'success_rate': 0.0,
            'failure_rate': 0.0,
            'average_execution_time_ms': 0.0,
            'total_execution_time_ms': session.get('total_execution_time_ms', 0),
            'session_age_seconds': 0,
            'status': session.get('status', 'active')
        }
        
        # Calculate rates
        if metrics['total_requests'] > 0:
            metrics['success_rate'] = metrics['successful_requests'] / metrics['total_requests']
            metrics['failure_rate'] = metrics['failed_requests'] / metrics['total_requests']
            metrics['average_execution_time_ms'] = (
                metrics['total_execution_time_ms'] / metrics['total_requests']
            )
        
        # Calculate session age
        try:
            created = datetime.fromisoformat(session.get('created_at'))
            metrics['session_age_seconds'] = int((datetime.now() - created).total_seconds())
        except Exception:
            pass
        
        # Detailed statistics (if requested)
        if include_detailed:
            # Get all events for this session
            # events = await self.repository.get_session_events(session_id)
            events = []  # Placeholder
            
            # Tool usage statistics
            tool_usage = {}
            for event in events:
                tool_name = event.get('tool_name')
                if tool_name:
                    if tool_name not in tool_usage:
                        tool_usage[tool_name] = {
                            'count': 0,
                            'success_count': 0,
                            'failure_count': 0,
                            'total_time_ms': 0
                        }
                    tool_usage[tool_name]['count'] += 1
                    if event.get('status') == 'success':
                        tool_usage[tool_name]['success_count'] += 1
                    else:
                        tool_usage[tool_name]['failure_count'] += 1
                    tool_usage[tool_name]['total_time_ms'] += event.get('duration_ms', 0)
            
            metrics['tool_usage'] = tool_usage
            
            # Request distribution (by hour)
            hourly_distribution = {}
            for event in events:
                try:
                    timestamp = datetime.fromisoformat(event.get('timestamp'))
                    hour = timestamp.hour
                    hourly_distribution[hour] = hourly_distribution.get(hour, 0) + 1
                except Exception:
                    pass
            
            metrics['hourly_distribution'] = hourly_distribution
            
            # Error analysis
            error_types = {}
            for event in events:
                if event.get('status') != 'success' and event.get('error_message'):
                    error_msg = event.get('error_message')
                    # Extract error type (first word)
                    error_type = error_msg.split(':')[0] if ':' in error_msg else 'Unknown'
                    error_types[error_type] = error_types.get(error_type, 0) + 1
            
            metrics['error_types'] = error_types
        
        execution_time_ms = int((datetime.now() - start_time).total_seconds() * 1000)
        
        logger.info(f"Session metrics for {session_id}: {metrics['total_requests']} requests")
        
        return {
            'request_id': request.request_id,
            'status': 'COMPLETED',
            'payload': metrics,
            'metadata': {
                'execution_time_ms': execution_time_ms,
                'detailed_stats_included': include_detailed
            }
        }
    
    # ------------------------------------------------------------------------
    # 2. GET SESSION TIMELINE
    # ------------------------------------------------------------------------
    
    async def get_session_timeline(self, request) -> Dict[str, Any]:
        """
        Get chronological timeline of events for a session.
        
        Returns events in order:
        - Session created
        - Tool requests received
        - Tool executions started/completed
        - Errors encountered
        - Session state changes
        
        Args:
            request: Request with session_id and optional filters
            
        Returns:
            Response with event timeline
        """
        start_time = datetime.now()
        user_id = request.user_id
        session_id = request.payload.session_id
        event_types = request.payload.event_types
        limit = request.payload.limit
        
        # Get session
        # session = await self.repository.get_session(session_id)
        session = None  # Placeholder
        
        if not session:
            execution_time_ms = int((datetime.now() - start_time).total_seconds() * 1000)
            return {
                'request_id': request.request_id,
                'status': 'FAILED',
                'error': f'Session {session_id} not found',
                'payload': {},
                'metadata': {'execution_time_ms': execution_time_ms}
            }
        
        # Verify access
        if session.get('user_id') != user_id:
            execution_time_ms = int((datetime.now() - start_time).total_seconds() * 1000)
            return {
                'request_id': request.request_id,
                'status': 'FAILED',
                'error': 'Insufficient permissions',
                'payload': {},
                'metadata': {'execution_time_ms': execution_time_ms}
            }
        
        # Get all events
        # events = await self.repository.get_session_events(session_id)
        events = []  # Placeholder
        
        # Build timeline
        timeline = []
        
        # Add session creation event
        timeline.append({
            'event_type': 'session_created',
            'timestamp': session.get('created_at'),
            'user_id': session.get('user_id'),
            'details': {
                'title': session.get('title'),
                'casefile_id': session.get('casefile_id')
            }
        })
        
        # Add tool events
        for event in events:
            timeline_event = {
                'event_type': event.get('event_type'),
                'timestamp': event.get('timestamp'),
                'tool_name': event.get('tool_name'),
                'status': event.get('status'),
                'duration_ms': event.get('duration_ms'),
                'details': {}
            }
            
            # Add relevant details based on event type
            if event.get('error_message'):
                timeline_event['details']['error'] = event.get('error_message')
            
            if event.get('result_summary'):
                timeline_event['details']['result_summary'] = event.get('result_summary')
            
            timeline.append(timeline_event)
        
        # Filter by event types if specified
        if event_types:
            timeline = [e for e in timeline if e.get('event_type') in event_types]
        
        # Sort by timestamp
        timeline.sort(key=lambda e: e.get('timestamp', ''))
        
        # Apply limit
        timeline = timeline[:limit]
        
        execution_time_ms = int((datetime.now() - start_time).total_seconds() * 1000)
        
        return {
            'request_id': request.request_id,
            'status': 'COMPLETED',
            'payload': {
                'session_id': session_id,
                'events': timeline,
                'total_events': len(timeline),
                'filtered': event_types is not None
            },
            'metadata': {
                'execution_time_ms': execution_time_ms
            }
        }
    
    # ------------------------------------------------------------------------
    # 3. EXPORT SESSION LOGS
    # ------------------------------------------------------------------------
    
    async def export_session_logs(self, request) -> Dict[str, Any]:
        """
        Export complete audit trail for a session.
        
        Supports formats:
        - JSON: Full structured export
        - CSV: Tabular event data
        - TXT: Human-readable log format
        
        Args:
            request: Request with session_id and format
            
        Returns:
            Response with exported data
        """
        start_time = datetime.now()
        user_id = request.user_id
        session_id = request.payload.session_id
        export_format = request.payload.format
        include_metadata = request.payload.include_metadata
        
        # Get session
        # session = await self.repository.get_session(session_id)
        session = None  # Placeholder
        
        if not session:
            execution_time_ms = int((datetime.now() - start_time).total_seconds() * 1000)
            return {
                'request_id': request.request_id,
                'status': 'FAILED',
                'error': f'Session {session_id} not found',
                'payload': {},
                'metadata': {'execution_time_ms': execution_time_ms}
            }
        
        # Verify access
        if session.get('user_id') != user_id:
            execution_time_ms = int((datetime.now() - start_time).total_seconds() * 1000)
            return {
                'request_id': request.request_id,
                'status': 'FAILED',
                'error': 'Insufficient permissions',
                'payload': {},
                'metadata': {'execution_time_ms': execution_time_ms}
            }
        
        # Get all events
        # events = await self.repository.get_session_events(session_id)
        events = []  # Placeholder
        
        # Build export data
        export_data = {
            'session': session,
            'events': events,
            'export_timestamp': datetime.now().isoformat(),
            'total_events': len(events)
        }
        
        # Format export based on requested format
        if export_format == 'json':
            exported_content = json.dumps(export_data, indent=2)
            content_type = 'application/json'
        
        elif export_format == 'csv':
            # Convert events to CSV format
            csv_lines = [
                'timestamp,event_type,tool_name,status,duration_ms,error_message'
            ]
            for event in events:
                csv_lines.append(
                    f"{event.get('timestamp')},"
                    f"{event.get('event_type')},"
                    f"{event.get('tool_name', '')},"
                    f"{event.get('status', '')},"
                    f"{event.get('duration_ms', '')},"
                    f"\"{event.get('error_message', '')}\""
                )
            exported_content = '\n'.join(csv_lines)
            content_type = 'text/csv'
        
        elif export_format == 'txt':
            # Human-readable log format
            lines = [
                f"Session Log Export",
                f"=" * 80,
                f"Session ID: {session_id}",
                f"User: {session.get('user_id')}",
                f"Created: {session.get('created_at')}",
                f"Status: {session.get('status')}",
                f"Total Events: {len(events)}",
                f"=" * 80,
                ""
            ]
            
            for event in events:
                lines.append(
                    f"[{event.get('timestamp')}] "
                    f"{event.get('event_type')} - "
                    f"{event.get('tool_name', 'N/A')}"
                )
                if event.get('status'):
                    lines.append(f"  Status: {event.get('status')}")
                if event.get('duration_ms'):
                    lines.append(f"  Duration: {event.get('duration_ms')}ms")
                if event.get('error_message'):
                    lines.append(f"  Error: {event.get('error_message')}")
                lines.append("")
            
            exported_content = '\n'.join(lines)
            content_type = 'text/plain'
        
        else:
            execution_time_ms = int((datetime.now() - start_time).total_seconds() * 1000)
            return {
                'request_id': request.request_id,
                'status': 'FAILED',
                'error': f'Unsupported format: {export_format}',
                'payload': {},
                'metadata': {'execution_time_ms': execution_time_ms}
            }
        
        execution_time_ms = int((datetime.now() - start_time).total_seconds() * 1000)
        
        logger.info(f"Exported session {session_id} as {export_format}")
        
        return {
            'request_id': request.request_id,
            'status': 'COMPLETED',
            'payload': {
                'session_id': session_id,
                'format': export_format,
                'content': exported_content,
                'content_type': content_type,
                'size_bytes': len(exported_content)
            },
            'metadata': {
                'execution_time_ms': execution_time_ms,
                'events_exported': len(events)
            }
        }
    
    # ------------------------------------------------------------------------
    # 4. CLOSE INACTIVE SESSIONS
    # ------------------------------------------------------------------------
    
    async def close_inactive_sessions(self, request) -> Dict[str, Any]:
        """
        Bulk close sessions that have been inactive for specified duration.
        
        Useful for:
        - Cleaning up stale sessions
        - Resource management
        - Security (auto-logout)
        
        Args:
            request: Request with inactivity threshold
            
        Returns:
            Response with list of closed sessions
        """
        start_time = datetime.now()
        user_id = request.user_id
        inactive_hours = request.payload.inactive_hours
        target_user_id = request.payload.user_id
        dry_run = request.payload.dry_run
        
        # Calculate cutoff time
        cutoff = datetime.now() - timedelta(hours=inactive_hours)
        
        # Get sessions to close
        # In real implementation: query repository for inactive sessions
        # if target_user_id:
        #     sessions = await self.repository.get_user_sessions(target_user_id)
        # else:
        #     sessions = await self.repository.get_all_sessions()
        sessions = []  # Placeholder
        
        # Filter for inactive sessions
        inactive_sessions = []
        for session in sessions:
            if not session.get('active'):
                continue  # Already closed
            
            last_activity = session.get('last_activity_at') or session.get('updated_at')
            try:
                activity_time = datetime.fromisoformat(last_activity)
                if activity_time < cutoff:
                    inactive_sessions.append(session)
            except Exception:
                continue
        
        # Close sessions (unless dry-run)
        closed_count = 0
        closed_session_ids = []
        
        if not dry_run:
            for session in inactive_sessions:
                session_id = session.get('session_id')
                try:
                    # await self.repository.close_session(
                    #     session_id,
                    #     reason='auto_closed_inactive'
                    # )
                    closed_count += 1
                    closed_session_ids.append(session_id)
                except Exception as e:
                    logger.error(f"Failed to close session {session_id}: {e}")
        
        execution_time_ms = int((datetime.now() - start_time).total_seconds() * 1000)
        
        logger.info(
            f"{'Would close' if dry_run else 'Closed'} "
            f"{len(inactive_sessions)} inactive sessions (>{inactive_hours}h)"
        )
        
        return {
            'request_id': request.request_id,
            'status': 'COMPLETED',
            'payload': {
                'inactive_hours': inactive_hours,
                'sessions_found': len(inactive_sessions),
                'sessions_closed': closed_count if not dry_run else 0,
                'closed_session_ids': closed_session_ids,
                'dry_run': dry_run
            },
            'metadata': {
                'execution_time_ms': execution_time_ms,
                'cutoff_time': cutoff.isoformat()
            }
        }


# ============================================================================
# USAGE EXAMPLE
# ============================================================================

if __name__ == "__main__":
    print("=" * 80)
    print("Phase 2: ToolSessionService New Methods - Demo")
    print("=" * 80)
    print()
    
    print("✓ New service methods implemented:")
    print("  1. get_session_metrics - Performance metrics and success rates")
    print("  2. get_session_timeline - Chronological event view")
    print("  3. export_session_logs - Complete audit trail export")
    print("  4. close_inactive_sessions - Bulk close idle sessions")
    print()
    
    print("✓ All methods follow the standard pattern:")
    print("  - Performance tracking (execution_time_ms)")
    print("  - Structured responses (RequestStatus)")
    print("  - Metadata enrichment")
    print("  - Error handling with proper logging")
    print("  - Permission checks at service layer")
    print("  - Validation with clear error messages")
    print()
    
    print("✓ Key features:")
    print("  - Session metrics with detailed statistics")
    print("  - Comprehensive timeline with filtering")
    print("  - Multiple export formats (JSON, CSV, TXT)")
    print("  - Bulk operations with dry-run support")
    print()
    
    print("=" * 80)
    print("Implementation complete. See code above for full details.")
    print("=" * 80)
