"""
Session management utilities for automatic session creation and resumption.

This module provides session resumption capabilities for tool-to-tool invocations,
allowing tools to automatically create sessions when needed or resume existing
valid sessions based on tokens.
"""

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, Optional, Tuple

from pydantic_ai_integration.dependencies import MDSContext
from pydantic_models.base.types import RequestStatus
from pydantic_models.operations.tool_session_ops import CreateSessionRequest, GetSessionRequest
from tool_sessionservice.service import ToolSessionService

logger = logging.getLogger(__name__)


class SessionManager:
    """Manages automatic session creation and resumption for tool execution."""

    def __init__(self):
        self.session_service = ToolSessionService()

    async def ensure_session_context(
        self,
        user_id: str,
        casefile_id: Optional[str] = None,
        session_token: Optional[str] = None,
        client_request_id: Optional[str] = None,
        auto_create: bool = True
    ) -> Tuple[MDSContext, bool]:
        """
        Ensure a valid session context exists, creating or resuming as needed.

        Args:
            user_id: The user ID for the session
            casefile_id: Optional casefile ID to link the session to
            session_token: Optional existing session token to resume
            client_request_id: Optional client-provided request ID
            auto_create: Whether to create a new session if none exists

        Returns:
            Tuple of (MDSContext, was_created) where was_created indicates
            if a new session was created vs resumed
        """
        # Try to resume existing session if token provided
        if session_token:
            resumed_context = await self._try_resume_session(
                session_token, user_id, client_request_id
            )
            if resumed_context:
                logger.info(f"Resumed existing session {session_token} for user {user_id}")
                return resumed_context, False

        # Create new session if auto_create is enabled
        if auto_create:
            context = await self._create_new_session(
                user_id, casefile_id, client_request_id
            )
            logger.info(f"Created new session {context.session_id} for user {user_id}")
            return context, True

        # No session available and auto_create disabled
        raise ValueError("No valid session available and auto_create is disabled")

    async def _try_resume_session(
        self,
        session_token: str,
        user_id: str,
        client_request_id: Optional[str] = None
    ) -> Optional[MDSContext]:
        """
        Attempt to resume an existing session.

        Args:
            session_token: The session ID/token to resume
            user_id: Expected user ID for validation
            client_request_id: Optional client request ID

        Returns:
            MDSContext if session is valid and resumable, None otherwise
        """
        try:
            # Validate session exists and belongs to user
            get_request = GetSessionRequest(
                user_id=user_id,
                payload={"session_id": session_token}
            )

            response = await self.session_service.get_session(get_request)

            if response.status != RequestStatus.COMPLETED:
                logger.warning(f"Session {session_token} not found or access denied")
                return None

            # Check if session is active
            if not response.payload.active:
                logger.warning(f"Session {session_token} is not active")
                return None

            # Create context from session data
            context = MDSContext(
                user_id=user_id,
                session_id=session_token,
                casefile_id=response.payload.casefile_id or None,
                environment="development"
            )

            # Create new session request ID for this tool execution
            context.create_session_request(client_request_id)

            logger.debug(f"Successfully resumed session {session_token}")
            return context

        except Exception as e:
            logger.warning(f"Failed to resume session {session_token}: {e}")
            return None

    async def _create_new_session(
        self,
        user_id: str,
        casefile_id: Optional[str] = None,
        client_request_id: Optional[str] = None
    ) -> MDSContext:
        """
        Create a new tool session.

        Args:
            user_id: User ID for the session
            casefile_id: Optional casefile ID to link
            client_request_id: Optional client request ID

        Returns:
            MDSContext for the new session
        """
        create_request = CreateSessionRequest(
            user_id=user_id,
            payload={"casefile_id": casefile_id}
        )

        response = await self.session_service.create_session(create_request)

        if response.status != RequestStatus.COMPLETED:
            raise ValueError(f"Failed to create session: {response.error}")

        # Create context from new session
        context = MDSContext(
            user_id=user_id,
            session_id=response.payload.session_id,
            casefile_id=casefile_id,
            environment="development"
        )

        # Create session request ID
        context.create_session_request(client_request_id)

        return context

    async def validate_session_token(
        self,
        session_token: str,
        user_id: str
    ) -> bool:
        """
        Validate that a session token is valid and belongs to the user.

        Args:
            session_token: Session token to validate
            user_id: Expected user ID

        Returns:
            True if session is valid, False otherwise
        """
        try:
            get_request = GetSessionRequest(
                user_id=user_id,
                payload={"session_id": session_token}
            )

            response = await self.session_service.get_session(get_request)
            return response.status == RequestStatus.COMPLETED and response.payload.active

        except Exception:
            return False

    def create_tool_chain_context(
        self,
        parent_context: MDSContext,
        tool_name: str,
        chain_purpose: str = None
    ) -> MDSContext:
        """
        Create a context for tool chaining that inherits from parent context.

        Args:
            parent_context: The parent tool execution context
            tool_name: Name of the tool being chained
            chain_purpose: Optional description of why this tool is chained

        Returns:
            New MDSContext for the chained tool execution
        """
        # Create new context inheriting key properties
        chain_context = MDSContext(
            user_id=parent_context.user_id,
            session_id=parent_context.session_id,
            casefile_id=parent_context.casefile_id,
            environment=parent_context.environment
        )

        # Create new session request ID for this tool in the chain
        chain_context.create_session_request()

        # Record chaining information
        chain_context.previous_tools = parent_context.previous_tools.copy()
        chain_context.previous_tools.append({
            "tool_name": getattr(parent_context, '_current_tool', 'unknown'),
            "session_request_id": parent_context.session_request_id,
            "chained_to": tool_name,
            "chain_purpose": chain_purpose,
            "timestamp": datetime.now().isoformat()
        })

        # Set current tool for next chaining
        chain_context._current_tool = tool_name

        return chain_context


# Global session manager instance
_session_manager = None

def get_session_manager() -> SessionManager:
    """Get the global session manager instance."""
    global _session_manager
    if _session_manager is None:
        _session_manager = SessionManager()
    return _session_manager


async def ensure_session_for_tool(
    user_id: str,
    tool_name: str,
    casefile_id: Optional[str] = None,
    session_token: Optional[str] = None,
    client_request_id: Optional[str] = None,
    auto_create: bool = True
) -> Tuple[MDSContext, bool]:
    """
    Convenience function to ensure session context for tool execution.

    This is the main entry point for tools that want automatic session management.

    Args:
        user_id: User executing the tool
        tool_name: Name of the tool being executed
        casefile_id: Optional casefile context
        session_token: Optional existing session to resume
        client_request_id: Optional client request ID
        auto_create: Whether to create session if none exists

    Returns:
        Tuple of (context, was_created)
    """
    manager = get_session_manager()

    context, was_created = await manager.ensure_session_context(
        user_id=user_id,
        casefile_id=casefile_id,
        session_token=session_token,
        client_request_id=client_request_id,
        auto_create=auto_create
    )

    # Set current tool for chaining
    context._current_tool = tool_name

    return context, was_created


async def chain_tool_execution(
    parent_context: MDSContext,
    tool_name: str,
    chain_purpose: Optional[str] = None
) -> MDSContext:
    """
    Create context for chaining tool execution within the same session.

    Args:
        parent_context: Context from the parent tool execution
        tool_name: Name of the tool being chained
        chain_purpose: Optional[str] - purpose description

    Returns:
        New context for the chained tool execution
    """
    manager = get_session_manager()
    return manager.create_tool_chain_context(parent_context, tool_name, chain_purpose)