"""
Google Drive tools using unified @register_mds_tool decorator.

This module implements Drive toolset following the Tool Engineering Foundation:
1. Define Pydantic model for parameters (guardrails)
2. Use @register_mds_tool decorator (single registration)
3. Implement clean function (validation already done)

Week 2: Mock implementations for testing patterns
Week 4: Will replace with real Google Drive API integration

Tools implemented:
- drive_list_files: List files with filtering
- drive_get_file: Get file metadata and content
- drive_upload_file: Upload files to Drive
- drive_create_folder: Create folders
- drive_share_file: Share files and generate links
"""

from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
import asyncio
import logging

from ..tool_decorator import register_mds_tool
from ..dependencies import MDSContext
from .drive_params import (
    DriveListFilesParams,
    DriveGetFileParams,
    DriveUploadFileParams,
    DriveCreateFolderParams,
    DriveShareFileParams
)
from .mock_drive_client import get_mock_drive_client

logger = logging.getLogger(__name__)


# ============================================================================
# DRIVE TOOL IMPLEMENTATIONS
# ============================================================================

@register_mds_tool(
    # METADATA
    name="drive_list_files",
    display_name="List Drive Files",
    description="List files from Google Drive with optional filtering and sorting",
    category="google_workspace",
    version="1.0.0",
    tags=["drive", "files", "list", "google_workspace"],
    
    # BUSINESS LOGIC
    enabled=True,
    requires_auth=True,
    required_permissions=["drive:read"],
    requires_casefile=False,
    timeout_seconds=30,
    
    # EXECUTION
    params_model=DriveListFilesParams,
)
async def drive_list_files(
    ctx: MDSContext,
    query: str = "",
    max_results: int = 10,
    order_by: str = "modifiedTime desc"
) -> Dict[str, Any]:
    """
    List files from Google Drive with filtering.
    
    NOTE: Parameters are already validated by the decorator!
    The decorator ensures:
    - query is a string (max 500 chars)
    - max_results is between 1-100
    - order_by is a valid string
    
    Args:
        ctx: MDSContext with user_id, session_id, casefile_id
        query: Google Drive search query (optional)
        max_results: Maximum number of files to return (1-100)
        order_by: Sort order
        
    Returns:
        Dictionary with files list and metadata
    """
    # Register event
    event_id = ctx.register_event(
        "drive_list_files",
        {"query": query, "max_results": max_results, "order_by": order_by}
    )
    
    # Get mock client (Week 2: mock implementation)
    client = get_mock_drive_client()
    
    try:
        # List files
        result = client.list_files(
            query=query,
            max_results=max_results,
            order_by=order_by
        )
        
        # Store in casefile if available
        if ctx.casefile_id:
            logger.info(f"Storing {len(result['files'])} files in casefile {ctx.casefile_id}")
            # Note: Actual casefile storage will be implemented in Week 3
            # For now, we just log the intent
        
        # Update event with result summary
        if ctx.tool_events:
            last_event = ctx.tool_events[-1]
            last_event.result_summary = {
                "status": "success",
                "file_count": len(result['files']),
                "query": query
            }
            last_event.status = "success"
        
        # Build response
        response = {
            "files": result["files"],
            "total_count": result["total_count"],
            "next_page_token": result.get("next_page_token"),
            "query": query,
            "event_id": event_id,
            "timestamp": ctx.tool_events[-1].timestamp if ctx.tool_events else None
        }
        
        # Add correlation ID
        session_request_id = ctx.transaction_context.get("client_request_id")
        if session_request_id:
            response["correlation_id"] = session_request_id
        
        return response
        
    except Exception as e:
        logger.error(f"Error listing files: {e}")
        
        # Update event with error
        if ctx.tool_events:
            last_event = ctx.tool_events[-1]
            last_event.result_summary = {"status": "error", "error": str(e)}
            last_event.status = "error"
        
        raise


@register_mds_tool(
    # METADATA
    name="drive_get_file",
    display_name="Get Drive File",
    description="Get metadata and content of a specific file from Google Drive",
    category="google_workspace",
    version="1.0.0",
    tags=["drive", "file", "get", "google_workspace"],
    
    # BUSINESS LOGIC
    enabled=True,
    requires_auth=True,
    required_permissions=["drive:read"],
    requires_casefile=False,
    timeout_seconds=60,
    
    # EXECUTION
    params_model=DriveGetFileParams,
)
async def drive_get_file(
    ctx: MDSContext,
    file_id: str,
    include_content: bool = False
) -> Dict[str, Any]:
    """
    Get metadata and optionally content of a specific Drive file.
    
    NOTE: Parameters are already validated!
    - file_id matches pattern (alphanumeric, dash, underscore only)
    - include_content is a boolean
    
    Args:
        ctx: MDSContext
        file_id: Google Drive file ID
        include_content: Whether to include file content
        
    Returns:
        Dictionary with file metadata and optional content
    """
    # Register event
    event_id = ctx.register_event(
        "drive_get_file",
        {"file_id": file_id, "include_content": include_content}
    )
    
    # Get mock client
    client = get_mock_drive_client()
    
    try:
        # Get file
        file_data = client.get_file(
            file_id=file_id,
            include_content=include_content
        )
        
        # Store in casefile if available
        if ctx.casefile_id:
            logger.info(f"Storing file {file_id} in casefile {ctx.casefile_id}")
        
        # Update event
        if ctx.tool_events:
            last_event = ctx.tool_events[-1]
            last_event.result_summary = {
                "status": "success",
                "file_id": file_id,
                "file_name": file_data["name"],
                "includes_content": include_content
            }
            last_event.status = "success"
        
        # Build response
        response = {
            "file": file_data,
            "event_id": event_id,
            "timestamp": ctx.tool_events[-1].timestamp if ctx.tool_events else None
        }
        
        # Add correlation ID
        session_request_id = ctx.transaction_context.get("client_request_id")
        if session_request_id:
            response["correlation_id"] = session_request_id
        
        return response
        
    except ValueError as e:
        logger.error(f"File not found: {e}")
        
        # Update event with error
        if ctx.tool_events:
            last_event = ctx.tool_events[-1]
            last_event.result_summary = {"status": "error", "error": str(e)}
            last_event.status = "error"
        
        raise
    except Exception as e:
        logger.error(f"Error getting file: {e}")
        
        # Update event with error
        if ctx.tool_events:
            last_event = ctx.tool_events[-1]
            last_event.result_summary = {"status": "error", "error": str(e)}
            last_event.status = "error"
        
        raise


@register_mds_tool(
    # METADATA
    name="drive_upload_file",
    display_name="Upload File to Drive",
    description="Upload a file to Google Drive with optional metadata",
    category="google_workspace",
    version="1.0.0",
    tags=["drive", "upload", "file", "google_workspace"],
    
    # BUSINESS LOGIC
    enabled=True,
    requires_auth=True,
    required_permissions=["drive:write"],
    requires_casefile=False,
    timeout_seconds=120,
    
    # EXECUTION
    params_model=DriveUploadFileParams,
)
async def drive_upload_file(
    ctx: MDSContext,
    file_name: str,
    content: str,
    mime_type: str = "application/octet-stream",
    parent_folder_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Upload a file to Google Drive.
    
    NOTE: Parameters are already validated!
    - file_name is 1-255 chars
    - content is provided
    - mime_type has a default
    - parent_folder_id matches pattern if provided
    
    Args:
        ctx: MDSContext
        file_name: Name for the file
        content: File content (base64 for binary)
        mime_type: MIME type
        parent_folder_id: Optional parent folder
        
    Returns:
        Dictionary with uploaded file metadata
    """
    # Register event
    event_id = ctx.register_event(
        "drive_upload_file",
        {
            "file_name": file_name,
            "mime_type": mime_type,
            "parent_folder_id": parent_folder_id,
            "content_size": len(content)
        }
    )
    
    # Get mock client
    client = get_mock_drive_client()
    
    try:
        # Simulate upload delay
        await asyncio.sleep(0.3)
        
        # Upload file
        file_data = client.upload_file(
            file_name=file_name,
            mime_type=mime_type,
            content=content,
            parent_folder_id=parent_folder_id
        )
        
        # Store in casefile if available
        if ctx.casefile_id:
            logger.info(f"Storing uploaded file {file_data['id']} in casefile {ctx.casefile_id}")
        
        # Update event
        if ctx.tool_events:
            last_event = ctx.tool_events[-1]
            last_event.result_summary = {
                "status": "success",
                "file_id": file_data["id"],
                "file_name": file_name,
                "size": file_data["size"]
            }
            last_event.status = "success"
            last_event.duration_ms = 300
        
        # Build response
        response = {
            "file": file_data,
            "event_id": event_id,
            "timestamp": ctx.tool_events[-1].timestamp if ctx.tool_events else None
        }
        
        # Add correlation ID
        session_request_id = ctx.transaction_context.get("client_request_id")
        if session_request_id:
            response["correlation_id"] = session_request_id
        
        return response
        
    except Exception as e:
        logger.error(f"Error uploading file: {e}")
        
        # Update event with error
        if ctx.tool_events:
            last_event = ctx.tool_events[-1]
            last_event.result_summary = {"status": "error", "error": str(e)}
            last_event.status = "error"
        
        raise


@register_mds_tool(
    # METADATA
    name="drive_create_folder",
    display_name="Create Drive Folder",
    description="Create a new folder in Google Drive",
    category="google_workspace",
    version="1.0.0",
    tags=["drive", "folder", "create", "google_workspace"],
    
    # BUSINESS LOGIC
    enabled=True,
    requires_auth=True,
    required_permissions=["drive:write"],
    requires_casefile=False,
    timeout_seconds=30,
    
    # EXECUTION
    params_model=DriveCreateFolderParams,
)
async def drive_create_folder(
    ctx: MDSContext,
    folder_name: str,
    parent_folder_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create a new folder in Google Drive.
    
    NOTE: Parameters are already validated!
    - folder_name is 1-255 chars
    - parent_folder_id matches pattern if provided
    
    Args:
        ctx: MDSContext
        folder_name: Name for the folder
        parent_folder_id: Optional parent folder
        
    Returns:
        Dictionary with created folder metadata
    """
    # Register event
    event_id = ctx.register_event(
        "drive_create_folder",
        {"folder_name": folder_name, "parent_folder_id": parent_folder_id}
    )
    
    # Get mock client
    client = get_mock_drive_client()
    
    try:
        # Simulate operation delay
        await asyncio.sleep(0.2)
        
        # Create folder
        folder_data = client.create_folder(
            folder_name=folder_name,
            parent_folder_id=parent_folder_id
        )
        
        # Store in casefile if available
        if ctx.casefile_id:
            logger.info(f"Storing created folder {folder_data['id']} in casefile {ctx.casefile_id}")
        
        # Update event
        if ctx.tool_events:
            last_event = ctx.tool_events[-1]
            last_event.result_summary = {
                "status": "success",
                "folder_id": folder_data["id"],
                "folder_name": folder_name
            }
            last_event.status = "success"
            last_event.duration_ms = 200
        
        # Build response
        response = {
            "folder": folder_data,
            "event_id": event_id,
            "timestamp": ctx.tool_events[-1].timestamp if ctx.tool_events else None
        }
        
        # Add correlation ID
        session_request_id = ctx.transaction_context.get("client_request_id")
        if session_request_id:
            response["correlation_id"] = session_request_id
        
        return response
        
    except Exception as e:
        logger.error(f"Error creating folder: {e}")
        
        # Update event with error
        if ctx.tool_events:
            last_event = ctx.tool_events[-1]
            last_event.result_summary = {"status": "error", "error": str(e)}
            last_event.status = "error"
        
        raise


@register_mds_tool(
    # METADATA
    name="drive_share_file",
    display_name="Share Drive File",
    description="Share a Google Drive file with specific users or generate a shareable link",
    category="google_workspace",
    version="1.0.0",
    tags=["drive", "share", "permissions", "google_workspace"],
    
    # BUSINESS LOGIC
    enabled=True,
    requires_auth=True,
    required_permissions=["drive:write", "drive:share"],
    requires_casefile=False,
    timeout_seconds=30,
    
    # EXECUTION
    params_model=DriveShareFileParams,
)
async def drive_share_file(
    ctx: MDSContext,
    file_id: str,
    email: Optional[str] = None,
    role: str = "reader",
    generate_link: bool = False
) -> Dict[str, Any]:
    """
    Share a Google Drive file with users or generate a shareable link.
    
    NOTE: Parameters are already validated!
    - file_id matches pattern
    - email matches email pattern if provided
    - role is one of: reader, writer, commenter, owner
    - generate_link is boolean
    
    Args:
        ctx: MDSContext
        file_id: File to share
        email: Optional email address
        role: Permission role
        generate_link: Whether to generate link
        
    Returns:
        Dictionary with permission info and optional link
    """
    # Register event
    event_id = ctx.register_event(
        "drive_share_file",
        {
            "file_id": file_id,
            "email": email,
            "role": role,
            "generate_link": generate_link
        }
    )
    
    # Get mock client
    client = get_mock_drive_client()
    
    try:
        # Simulate operation delay
        await asyncio.sleep(0.2)
        
        # Share file
        share_result = client.share_file(
            file_id=file_id,
            email=email,
            role=role,
            generate_link=generate_link
        )
        
        # Store in casefile if available
        if ctx.casefile_id:
            logger.info(f"Storing permission for file {file_id} in casefile {ctx.casefile_id}")
        
        # Update event
        if ctx.tool_events:
            last_event = ctx.tool_events[-1]
            last_event.result_summary = {
                "status": "success",
                "file_id": file_id,
                "permission_id": share_result["permission"]["id"],
                "has_link": generate_link
            }
            last_event.status = "success"
            last_event.duration_ms = 200
        
        # Build response
        response = {
            "permission": share_result["permission"],
            "file_id": share_result["file_id"],
            "event_id": event_id,
            "timestamp": ctx.tool_events[-1].timestamp if ctx.tool_events else None
        }
        
        if "link" in share_result:
            response["link"] = share_result["link"]
        
        # Add correlation ID
        session_request_id = ctx.transaction_context.get("client_request_id")
        if session_request_id:
            response["correlation_id"] = session_request_id
        
        return response
        
    except ValueError as e:
        logger.error(f"File not found: {e}")
        
        # Update event with error
        if ctx.tool_events:
            last_event = ctx.tool_events[-1]
            last_event.result_summary = {"status": "error", "error": str(e)}
            last_event.status = "error"
        
        raise
    except Exception as e:
        logger.error(f"Error sharing file: {e}")
        
        # Update event with error
        if ctx.tool_events:
            last_event = ctx.tool_events[-1]
            last_event.result_summary = {"status": "error", "error": str(e)}
            last_event.status = "error"
        
        raise


# ============================================================================
# TOOL REGISTRATION SUMMARY
# ============================================================================
# All tools are automatically registered via @register_mds_tool decorator
# They are stored in MANAGED_TOOLS registry in tool_decorator.py
# Services query the registry for execution
# API routes query the registry for discovery
# ============================================================================
