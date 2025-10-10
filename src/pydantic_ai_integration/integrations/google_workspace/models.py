"""Pydantic DTOs for Google Workspace client requests/responses."""

from __future__ import annotations

from typing import List, Optional, Union

from pydantic import BaseModel, Field

from src.pydantic_models.workspace import (
    DriveFile,
    GmailMessage,
    SheetData,
)

# ============================================================================
# ERROR MODELS
# ============================================================================

class GoogleWorkspaceError(BaseModel):
    """Standardized error response for Google Workspace API failures."""
    
    error_code: str = Field(..., description="Error code (API_ERROR, AUTH_ERROR, RATE_LIMIT, etc.)")
    error_message: str = Field(..., description="Human-readable error message")
    api_error_details: Optional[dict] = Field(None, description="Raw Google API error details")
    retry_after_seconds: Optional[int] = Field(None, description="Retry delay for rate limits")


# ============================================================================
# GMAIL MODELS
# ============================================================================


class GmailListMessagesRequest(BaseModel):
    """Parameters for listing Gmail messages."""

    max_results: int = Field(10, ge=1, le=100, description="Maximum results to return")
    query: str = Field("", max_length=2048, description="Gmail search query")
    page_token: Optional[str] = Field(None, description="Pagination token from previous call")
    label_ids: List[str] = Field(default_factory=list, description="Filter results to specific label IDs")


class GmailListMessagesResponse(BaseModel):
    """Response envelope for Gmail list messages."""

    messages: List[GmailMessage] = Field(default_factory=list, description="Gmail messages returned by the API")
    next_page_token: Optional[str] = Field(None, description="Token for fetching the next page")
    result_size_estimate: int = Field(0, ge=0, description="Google's estimated result size")
    error: Optional[GoogleWorkspaceError] = Field(None, description="Error details if request failed")


class GmailSendMessageRequest(BaseModel):
    """Parameters for sending a Gmail message."""

    to: str = Field(..., description="Recipient email address")
    subject: str = Field(..., description="Email subject line")
    body: str = Field(..., description="Email body content (plain text)")
    cc: str = Field("", description="CC recipients (comma-separated)")
    bcc: str = Field("", description="BCC recipients (comma-separated)")


class GmailSendMessageResponse(BaseModel):
    """Response envelope for sending a Gmail message."""

    message_id: str = Field(..., description="ID of the sent message")
    thread_id: str = Field(..., description="Thread ID the message belongs to")
    label_ids: List[str] = Field(default_factory=list, description="Labels applied to the sent message")
    error: Optional[GoogleWorkspaceError] = Field(None, description="Error details if request failed")


class GmailSearchMessagesRequest(BaseModel):
    """Parameters for searching Gmail messages."""

    query: str = Field(..., description="Gmail search query string")
    max_results: int = Field(10, ge=1, le=100, description="Maximum results to return")
    page_token: Optional[str] = Field(None, description="Pagination token")
    include_spam_trash: bool = Field(False, description="Include SPAM and TRASH in search results")


class GmailSearchMessagesResponse(BaseModel):
    """Response envelope for Gmail search."""

    messages: List[GmailMessage] = Field(default_factory=list, description="Messages matching the search")
    next_page_token: Optional[str] = Field(None, description="Token for next page")
    result_size_estimate: int = Field(0, ge=0, description="Estimated total results")
    query_used: Optional[str] = Field(None, description="The actual query executed in the search")
    error: Optional[GoogleWorkspaceError] = Field(None, description="Error details if request failed")


class GmailGetMessageRequest(BaseModel):
    """Parameters for getting a specific Gmail message."""

    message_id: str = Field(..., description="Gmail message ID to retrieve")
    format: str = Field("full", description="Message format (minimal|full|raw|metadata)")
    include_headers: bool = Field(True, description="Include email headers in the response payload")


class GmailGetMessageResponse(BaseModel):
    """Response envelope for getting a single message."""

    message: GmailMessage = Field(..., description="The requested Gmail message")
    error: Optional[GoogleWorkspaceError] = Field(None, description="Error details if request failed")


class DriveListFilesRequest(BaseModel):
    """Parameters for listing Google Drive files."""

    page_size: int = Field(10, ge=1, le=1000, description="Number of files to return per page")
    query: Optional[str] = Field(None, description="Drive query string")
    fields: str = Field("files(id,name,mimeType,owners,parents,webViewLink,size,trashed)", description="Fields projection for Drive API")
    page_token: Optional[str] = Field(None, description="Pagination token from previous call")


class DriveListFilesResponse(BaseModel):
    """Response payload for Drive file listing."""

    files: List[DriveFile] = Field(default_factory=list, description="Drive files returned by the API")
    next_page_token: Optional[str] = Field(None, description="Pagination token for next call")
    error: Optional[GoogleWorkspaceError] = Field(None, description="Error details if request failed")


class SheetsBatchGetRequest(BaseModel):
    """Request for retrieving multiple ranges from a spreadsheet."""

    spreadsheet_id: str = Field(..., description="Spreadsheet identifier")
    ranges: List[str] = Field(..., description="List of A1 notation ranges")


class SheetsBatchGetResponse(BaseModel):
    """Response payload for Sheets batch get."""

    spreadsheet: SheetData = Field(..., description="Spreadsheet data that mirrors selected ranges")
    error: Optional[GoogleWorkspaceError] = Field(None, description="Error details if request failed")
