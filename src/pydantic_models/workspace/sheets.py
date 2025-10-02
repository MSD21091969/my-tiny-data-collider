"""Pydantic models for Google Sheets data persisted with casefiles."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class SheetRange(BaseModel):
    """Represents a rectangular range of spreadsheet values."""

    range: str = Field(..., description="A1-notation range (e.g. Sheet1!A1:C10)")
    values: List[List[Any]] = Field(default_factory=list, description="2D array of cell values")
    major_dimension: str = Field(default="ROWS", description="Rows or COLUMNS orientation")


class SheetMetadata(BaseModel):
    """Metadata for a Google Sheet tab."""

    sheet_id: int = Field(..., description="Numeric sheet identifier")
    title: str = Field(..., description="Sheet title")
    index: Optional[int] = Field(None, description="Zero-based sheet index")
    grid_properties: Dict[str, Any] = Field(default_factory=dict, description="Raw grid properties from API")


class SheetData(BaseModel):
    """Top-level spreadsheet data captured for a casefile."""

    spreadsheet_id: str = Field(..., description="Spreadsheet ID")
    title: str = Field(..., description="Spreadsheet title")
    metadata: List[SheetMetadata] = Field(default_factory=list, description="Sheet metadata entries")
    ranges: List[SheetRange] = Field(default_factory=list, description="Captured ranges for the spreadsheet")
    updated_at: str = Field(default_factory=lambda: datetime.now().isoformat(), description="Timestamp of last update")


class CasefileSheetsData(BaseModel):
    """Typed Sheets data stored on a casefile."""

    spreadsheets: Dict[str, SheetData] = Field(default_factory=dict, description="Spreadsheet data keyed by spreadsheet ID")
    last_sync_token: Optional[str] = Field(None, description="Incremental sync token")
    synced_at: Optional[str] = Field(None, description="Timestamp of the most recent sync")
    sync_status: str = Field(default="idle", description="Current sync status (idle|syncing|error)")
    error_message: Optional[str] = Field(None, description="Last sync error")

    def upsert_sheet(self, sheet_data: SheetData) -> None:
        """Insert or update stored sheet data for the given spreadsheet."""

        self.spreadsheets[sheet_data.spreadsheet_id] = sheet_data
