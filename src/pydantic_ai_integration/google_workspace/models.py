"""Pydantic DTOs for Google Workspace client requests/responses."""

from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field

from ...pydantic_models.workspace import (
    DriveFile,
    GmailMessage,
    SheetData,
)


class GmailListMessagesRequest(BaseModel):
    """Parameters for listing Gmail messages."""

    max_results: int = Field(10, ge=1, le=100, description="Maximum results to return")
    query: str = Field("", max_length=2048, description="Gmail search query")
    page_token: Optional[str] = Field(None, description="Pagination token from previous call")


class GmailListMessagesResponse(BaseModel):
    """Response envelope for Gmail list messages."""

    messages: List[GmailMessage] = Field(default_factory=list, description="Gmail messages returned by the API")
    next_page_token: Optional[str] = Field(None, description="Token for fetching the next page")
    result_size_estimate: int = Field(0, ge=0, description="Google's estimated result size")


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


class SheetsBatchGetRequest(BaseModel):
    """Request for retrieving multiple ranges from a spreadsheet."""

    spreadsheet_id: str = Field(..., description="Spreadsheet identifier")
    ranges: List[str] = Field(..., description="List of A1 notation ranges")


class SheetsBatchGetResponse(BaseModel):
    """Response payload for Sheets batch get."""

    spreadsheet: SheetData = Field(..., description="Spreadsheet data that mirrors selected ranges")
