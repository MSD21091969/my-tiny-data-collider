"""
Gmail tool implementations using MDS tool decorator.

These tools provide real Gmail API integration following the tool engineering
foundation patterns defined in docs/TOOLENGINEERING_FOUNDATION.md.
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
import logging

from ..tool_decorator import register_mds_tool
from ..dependencies import MDSContext
from src.google_workspace.gmail_client import GmailClient

logger = logging.getLogger(__name__)


# ============================================================================
# Parameter Models
# ============================================================================

class GmailListMessagesParams(BaseModel):
    """Parameters for listing Gmail messages."""
    max_results: int = Field(
        default=10,
        ge=1,
        le=100,
        description="Maximum number of messages to return"
    )
    query: str = Field(
        default="",
        max_length=500,
        description="Gmail search query"
    )
    label_ids: Optional[List[str]] = Field(
        default=None,
        description="List of label IDs to filter by"
    )
    include_spam_trash: bool = Field(
        default=False,
        description="Whether to include spam and trash messages"
    )


class GmailGetMessageParams(BaseModel):
    """Parameters for getting a specific Gmail message."""
    message_id: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="The ID of the message to retrieve"
    )
    format: str = Field(
        default="full",
        description="The format to return the message in"
    )
    metadata_headers: Optional[List[str]] = Field(
        default=None,
        description="List of headers to return (when format='metadata')"
    )


class GmailSendMessageParams(BaseModel):
    """Parameters for sending a Gmail message."""
    to: str = Field(
        ...,
        min_length=5,
        max_length=500,
        description="Recipient email address"
    )
    subject: str = Field(
        ...,
        min_length=1,
        max_length=500,
        description="Email subject"
    )
    body: str = Field(
        ...,
        min_length=1,
        max_length=50000,
        description="Email body (plain text)"
    )
    from_email: Optional[str] = Field(
        default=None,
        description="Sender email (optional)"
    )
    cc: Optional[str] = Field(
        default=None,
        max_length=500,
        description="CC recipients (comma-separated)"
    )
    bcc: Optional[str] = Field(
        default=None,
        max_length=500,
        description="BCC recipients (comma-separated)"
    )


class GmailSearchMessagesParams(BaseModel):
    """Parameters for searching Gmail messages."""
    query: str = Field(
        ...,
        min_length=1,
        max_length=500,
        description="Gmail search query"
    )
    max_results: int = Field(
        default=10,
        ge=1,
        le=100,
        description="Maximum number of messages to return"
    )
    label_ids: Optional[List[str]] = Field(
        default=None,
        description="List of label IDs to filter by"
    )


# ============================================================================
# Tool Implementations
# ============================================================================

@register_mds_tool(
    name="gmail_list_messages",
    display_name="List Gmail Messages",
    description="List messages from Gmail inbox with optional query filtering",
    category="google_workspace",
    version="1.0.0",
    tags=["gmail", "messages", "list", "google"],
    requires_auth=True,
    required_permissions=["gmail:read"],
    requires_casefile=True,
    timeout_seconds=30,
    params_model=GmailListMessagesParams,
)
async def gmail_list_messages(
    ctx: MDSContext,
    max_results: int = 10,
    query: str = "",
    label_ids: Optional[List[str]] = None,
    include_spam_trash: bool = False
) -> Dict[str, Any]:
    """
    List messages from Gmail inbox.
    
    Args:
        ctx: MDS context for the operation
        max_results: Maximum number of messages to return
        query: Gmail search query
        label_ids: List of label IDs to filter by
        include_spam_trash: Whether to include spam and trash
        
    Returns:
        Dictionary with messages list and metadata
    """
    # Register event
    event_id = ctx.register_event(
        "gmail_list_messages",
        {
            "max_results": max_results,
            "query": query,
            "label_ids": label_ids,
            "include_spam_trash": include_spam_trash
        }
    )
    
    try:
        # Create Gmail client
        client = GmailClient(user_id=ctx.user_id)
        
        # Call API
        result = await client.list_messages(
            max_results=max_results,
            query=query,
            label_ids=label_ids,
            include_spam_trash=include_spam_trash
        )
        
        # Update audit trail
        if ctx.tool_events:
            last_event = ctx.tool_events[-1]
            last_event.result_summary = {
                "status": "success",
                "message_count": result.get("message_count", 0),
                "result_size_estimate": result.get("result_size_estimate", 0)
            }
            last_event.status = "success"
        
        return result
        
    except Exception as e:
        logger.error(f"Error listing Gmail messages: {e}")
        
        # Update audit trail with error
        if ctx.tool_events:
            last_event = ctx.tool_events[-1]
            last_event.result_summary = {
                "status": "error",
                "error": str(e)
            }
            last_event.status = "failed"
        
        return {
            "error": "Failed to list Gmail messages",
            "details": str(e),
            "messages": [],
            "message_count": 0
        }


@register_mds_tool(
    name="gmail_get_message",
    display_name="Get Gmail Message",
    description="Retrieve a specific Gmail message by ID with full details",
    category="google_workspace",
    version="1.0.0",
    tags=["gmail", "message", "get", "google"],
    requires_auth=True,
    required_permissions=["gmail:read"],
    requires_casefile=True,
    timeout_seconds=30,
    params_model=GmailGetMessageParams,
)
async def gmail_get_message(
    ctx: MDSContext,
    message_id: str,
    format: str = "full",
    metadata_headers: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Get a specific Gmail message by ID.
    
    Args:
        ctx: MDS context for the operation
        message_id: The ID of the message to retrieve
        format: The format to return the message in
        metadata_headers: List of headers to return
        
    Returns:
        Dictionary with message data
    """
    # Register event
    event_id = ctx.register_event(
        "gmail_get_message",
        {
            "message_id": message_id,
            "format": format,
            "metadata_headers": metadata_headers
        }
    )
    
    try:
        # Create Gmail client
        client = GmailClient(user_id=ctx.user_id)
        
        # Call API
        result = await client.get_message(
            message_id=message_id,
            format=format,
            metadata_headers=metadata_headers
        )
        
        # Update audit trail
        if ctx.tool_events:
            last_event = ctx.tool_events[-1]
            last_event.result_summary = {
                "status": "success",
                "message_id": result.get("id"),
                "snippet": result.get("snippet", "")[:100]
            }
            last_event.status = "success"
        
        return result
        
    except Exception as e:
        logger.error(f"Error getting Gmail message {message_id}: {e}")
        
        # Update audit trail with error
        if ctx.tool_events:
            last_event = ctx.tool_events[-1]
            last_event.result_summary = {
                "status": "error",
                "error": str(e)
            }
            last_event.status = "failed"
        
        return {
            "error": f"Failed to get Gmail message {message_id}",
            "details": str(e)
        }


@register_mds_tool(
    name="gmail_send_message",
    display_name="Send Gmail Message",
    description="Send an email message via Gmail",
    category="google_workspace",
    version="1.0.0",
    tags=["gmail", "send", "email", "google"],
    requires_auth=True,
    required_permissions=["gmail:send"],
    requires_casefile=True,
    timeout_seconds=30,
    params_model=GmailSendMessageParams,
)
async def gmail_send_message(
    ctx: MDSContext,
    to: str,
    subject: str,
    body: str,
    from_email: Optional[str] = None,
    cc: Optional[str] = None,
    bcc: Optional[str] = None
) -> Dict[str, Any]:
    """
    Send an email message via Gmail.
    
    Args:
        ctx: MDS context for the operation
        to: Recipient email address
        subject: Email subject
        body: Email body
        from_email: Sender email (optional)
        cc: CC recipients
        bcc: BCC recipients
        
    Returns:
        Dictionary with sent message ID and metadata
    """
    # Register event
    event_id = ctx.register_event(
        "gmail_send_message",
        {
            "to": to,
            "subject": subject,
            "body_length": len(body),
            "from_email": from_email,
            "has_cc": cc is not None,
            "has_bcc": bcc is not None
        }
    )
    
    try:
        # Create Gmail client
        client = GmailClient(user_id=ctx.user_id)
        
        # Call API
        result = await client.send_message(
            to=to,
            subject=subject,
            body=body,
            from_email=from_email,
            cc=cc,
            bcc=bcc
        )
        
        # Update audit trail
        if ctx.tool_events:
            last_event = ctx.tool_events[-1]
            last_event.result_summary = {
                "status": "success",
                "message_id": result.get("id"),
                "to": to,
                "subject": subject
            }
            last_event.status = "success"
        
        return result
        
    except Exception as e:
        logger.error(f"Error sending Gmail message: {e}")
        
        # Update audit trail with error
        if ctx.tool_events:
            last_event = ctx.tool_events[-1]
            last_event.result_summary = {
                "status": "error",
                "error": str(e)
            }
            last_event.status = "failed"
        
        return {
            "error": "Failed to send Gmail message",
            "details": str(e)
        }


@register_mds_tool(
    name="gmail_search_messages",
    display_name="Search Gmail Messages",
    description="Search Gmail messages using Gmail query syntax",
    category="google_workspace",
    version="1.0.0",
    tags=["gmail", "search", "query", "google"],
    requires_auth=True,
    required_permissions=["gmail:read"],
    requires_casefile=True,
    timeout_seconds=30,
    params_model=GmailSearchMessagesParams,
)
async def gmail_search_messages(
    ctx: MDSContext,
    query: str,
    max_results: int = 10,
    label_ids: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Search Gmail messages using Gmail query syntax.
    
    Args:
        ctx: MDS context for the operation
        query: Gmail search query
        max_results: Maximum number of messages to return
        label_ids: List of label IDs to filter by
        
    Returns:
        Dictionary with search results
    """
    # Register event
    event_id = ctx.register_event(
        "gmail_search_messages",
        {
            "query": query,
            "max_results": max_results,
            "label_ids": label_ids
        }
    )
    
    try:
        # Create Gmail client
        client = GmailClient(user_id=ctx.user_id)
        
        # Call API (search is just list with query)
        result = await client.search_messages(
            query=query,
            max_results=max_results,
            label_ids=label_ids
        )
        
        # Add query to result
        result["query"] = query
        
        # Update audit trail
        if ctx.tool_events:
            last_event = ctx.tool_events[-1]
            last_event.result_summary = {
                "status": "success",
                "query": query,
                "message_count": result.get("message_count", 0),
                "result_size_estimate": result.get("result_size_estimate", 0)
            }
            last_event.status = "success"
        
        return result
        
    except Exception as e:
        logger.error(f"Error searching Gmail messages: {e}")
        
        # Update audit trail with error
        if ctx.tool_events:
            last_event = ctx.tool_events[-1]
            last_event.result_summary = {
                "status": "error",
                "error": str(e)
            }
            last_event.status = "failed"
        
        return {
            "error": "Failed to search Gmail messages",
            "details": str(e),
            "query": query,
            "messages": [],
            "message_count": 0
        }
