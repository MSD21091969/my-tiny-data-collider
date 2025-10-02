"""
Google Sheets tools implementation.

This module implements mock Google Sheets tools for testing the tool factory pattern.
These tools follow the architecture from TOOLENGINEERING_FOUNDATION.md:
1. Define Pydantic models for parameters (guardrails)
2. Use @register_mds_tool decorator (single registration)
3. Implement clean functions (validation already done)
4. Return realistic mock data structures

Week 2: Mock implementations for testing
Week 4: Will be replaced with real Google Sheets API calls
"""

from pydantic import BaseModel, Field, field_validator
from typing import Dict, Any, List, Optional, Literal
import asyncio
from datetime import datetime
import random
import string

from ..tool_decorator import register_mds_tool
from ..dependencies import MDSContext


# ============================================================================
# PARAMETER MODELS (Pydantic = Guardrails)
# ============================================================================

class SheetsBatchGetParams(BaseModel):
    """
    Parameters for sheets_batch_get tool.
    
    Validates inputs for reading multiple ranges from a spreadsheet.
    """
    spreadsheet_id: str = Field(
        ...,
        min_length=1,
        max_length=100,
        pattern=r"^[a-zA-Z0-9_-]+$",
        description="The ID of the spreadsheet to read from"
    )
    ranges: List[str] = Field(
        ...,
        min_length=1,
        max_length=10,
        description="List of A1 notation ranges to read (e.g., ['Sheet1!A1:D10', 'Sheet2!B2:C5'])"
    )
    major_dimension: Literal["ROWS", "COLUMNS"] = Field(
        "ROWS",
        description="The major dimension that results should use"
    )
    
    @field_validator('ranges')
    @classmethod
    def validate_ranges(cls, v: List[str]) -> List[str]:
        """Validate that each range is non-empty."""
        if not all(r.strip() for r in v):
            raise ValueError("All ranges must be non-empty strings")
        return v


class ValueRange(BaseModel):
    """Represents a single value range update."""
    range: str = Field(..., description="The A1 notation range")
    values: List[List[Any]] = Field(..., description="2D array of values")


class SheetsBatchUpdateParams(BaseModel):
    """
    Parameters for sheets_batch_update tool.
    
    Validates inputs for updating multiple ranges in a spreadsheet.
    """
    spreadsheet_id: str = Field(
        ...,
        min_length=1,
        max_length=100,
        pattern=r"^[a-zA-Z0-9_-]+$",
        description="The ID of the spreadsheet to update"
    )
    data: List[Dict[str, Any]] = Field(
        ...,
        min_length=1,
        max_length=10,
        description="List of value ranges to update (each with range and values)"
    )
    value_input_option: Literal["USER_ENTERED", "RAW"] = Field(
        "USER_ENTERED",
        description="How input data should be interpreted"
    )
    
    @field_validator('data')
    @classmethod
    def validate_data(cls, v: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Validate that each data entry has required fields."""
        for item in v:
            if 'range' not in item or 'values' not in item:
                raise ValueError("Each data entry must have 'range' and 'values' fields")
            if not isinstance(item['values'], list):
                raise ValueError("'values' must be a list")
        return v


class SheetsAppendParams(BaseModel):
    """
    Parameters for sheets_append tool.
    
    Validates inputs for appending rows to a spreadsheet.
    """
    spreadsheet_id: str = Field(
        ...,
        min_length=1,
        max_length=100,
        pattern=r"^[a-zA-Z0-9_-]+$",
        description="The ID of the spreadsheet to append to"
    )
    range: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="The A1 notation range to append to (e.g., 'Sheet1!A1')"
    )
    values: List[List[Any]] = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="2D array of values to append (each inner array is a row)"
    )
    value_input_option: Literal["USER_ENTERED", "RAW"] = Field(
        "USER_ENTERED",
        description="How input data should be interpreted"
    )
    insert_data_option: Literal["INSERT_ROWS", "OVERWRITE"] = Field(
        "INSERT_ROWS",
        description="How data should be inserted"
    )
    
    @field_validator('values')
    @classmethod
    def validate_values(cls, v: List[List[Any]]) -> List[List[Any]]:
        """Validate that values is a proper 2D array."""
        if not all(isinstance(row, list) for row in v):
            raise ValueError("'values' must be a 2D array (list of lists)")
        return v


class SheetConfig(BaseModel):
    """Configuration for a single sheet within a spreadsheet."""
    title: str = Field(..., min_length=1, description="Sheet title")
    row_count: int = Field(1000, ge=1, le=10000, description="Number of rows")
    column_count: int = Field(26, ge=1, le=100, description="Number of columns")


class SheetsCreateParams(BaseModel):
    """
    Parameters for sheets_create tool.
    
    Validates inputs for creating a new spreadsheet.
    """
    title: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="The title of the new spreadsheet"
    )
    sheets: Optional[List[Dict[str, Any]]] = Field(
        None,
        max_length=10,
        description="List of sheet configurations"
    )
    locale: str = Field(
        "en_US",
        min_length=2,
        max_length=10,
        description="The locale of the spreadsheet"
    )


# ============================================================================
# MOCK DATA HELPERS
# ============================================================================

def generate_mock_spreadsheet_id() -> str:
    """Generate a realistic-looking spreadsheet ID."""
    return ''.join(random.choices(string.ascii_letters + string.digits + '_-', k=44))


def generate_mock_sheet_data(rows: int, cols: int) -> List[List[Any]]:
    """Generate mock data for a sheet range."""
    data = []
    for i in range(rows):
        row = []
        for j in range(cols):
            # Mix of different data types
            if i == 0:
                # Headers
                row.append(f"Column {chr(65 + j)}")
            elif j == 0:
                # First column: numbers
                row.append(i)
            elif j == 1:
                # Second column: strings
                row.append(f"Item {i}")
            else:
                # Other columns: mixed
                row.append(random.choice([
                    random.randint(1, 100),
                    f"Value {random.randint(1, 50)}",
                    round(random.uniform(0, 100), 2),
                    random.choice([True, False, None])
                ]))
        data.append(row)
    return data


# ============================================================================
# TOOL IMPLEMENTATIONS
# ============================================================================

@register_mds_tool(
    name="sheets_batch_get",
    display_name="Sheets Batch Get",
    description="Read data from multiple ranges in a Google Spreadsheet",
    category="google_workspace",
    version="1.0.0",
    tags=["sheets", "read", "batch", "google-workspace", "mock"],
    enabled=True,
    requires_auth=True,
    required_permissions=["sheets:read"],
    requires_casefile=False,
    timeout_seconds=30,
    params_model=SheetsBatchGetParams,
)
async def sheets_batch_get(
    ctx: MDSContext,
    spreadsheet_id: str,
    ranges: List[str],
    major_dimension: str = "ROWS"
) -> Dict[str, Any]:
    """
    Read data from multiple ranges in a Google Spreadsheet.
    
    This is a MOCK implementation that returns realistic data structures.
    In Week 4, this will be replaced with real Google Sheets API calls.
    
    Args:
        ctx: MDSContext with user_id, session_id, etc.
        spreadsheet_id: The ID of the spreadsheet (validated by decorator)
        ranges: List of A1 notation ranges (validated by decorator)
        major_dimension: How data should be organized (validated by decorator)
        
    Returns:
        Mock response matching Google Sheets API structure
    """
    # Register event for audit trail
    event_id = ctx.register_event(
        "sheets_batch_get",
        {
            "spreadsheet_id": spreadsheet_id,
            "ranges": ranges,
            "major_dimension": major_dimension
        }
    )
    
    # Simulate API call delay
    await asyncio.sleep(0.3)
    
    # Generate mock data for each range
    value_ranges = []
    for range_str in ranges:
        # Parse range to determine size (simplified)
        # In reality, would parse A1 notation properly
        rows = random.randint(5, 15)
        cols = random.randint(3, 6)
        
        value_ranges.append({
            "range": range_str,
            "majorDimension": major_dimension,
            "values": generate_mock_sheet_data(rows, cols)
        })
    
    result = {
        "spreadsheet_id": spreadsheet_id,
        "value_ranges": value_ranges,
        "timestamp": datetime.now().isoformat(),
        "event_id": event_id,
        "mock_data": True,
        "ranges_read": len(ranges)
    }
    
    # Update event with result summary
    if ctx.tool_events:
        last_event = ctx.tool_events[-1]
        last_event.result_summary = {
            "status": "success",
            "ranges_read": len(ranges),
            "total_cells": sum(len(vr["values"]) * len(vr["values"][0]) if vr["values"] else 0 for vr in value_ranges)
        }
        last_event.duration_ms = 300
        last_event.status = "success"
    
    return result


@register_mds_tool(
    name="sheets_batch_update",
    display_name="Sheets Batch Update",
    description="Update data in multiple ranges in a Google Spreadsheet",
    category="google_workspace",
    version="1.0.0",
    tags=["sheets", "write", "batch", "google-workspace", "mock"],
    enabled=True,
    requires_auth=True,
    required_permissions=["sheets:write"],
    requires_casefile=False,
    timeout_seconds=45,
    params_model=SheetsBatchUpdateParams,
)
async def sheets_batch_update(
    ctx: MDSContext,
    spreadsheet_id: str,
    data: List[Dict[str, Any]],
    value_input_option: str = "USER_ENTERED"
) -> Dict[str, Any]:
    """
    Update data in multiple ranges in a Google Spreadsheet.
    
    This is a MOCK implementation. Real implementation in Week 4.
    
    Args:
        ctx: MDSContext
        spreadsheet_id: The ID of the spreadsheet (validated)
        data: List of value ranges to update (validated)
        value_input_option: How to interpret input (validated)
        
    Returns:
        Mock response matching Google Sheets API structure
    """
    event_id = ctx.register_event(
        "sheets_batch_update",
        {
            "spreadsheet_id": spreadsheet_id,
            "ranges_count": len(data),
            "value_input_option": value_input_option
        }
    )
    
    await asyncio.sleep(0.4)
    
    # Calculate statistics about the update
    total_cells_updated = sum(
        len(item['values']) * len(item['values'][0]) if item['values'] and item['values'][0] else 0
        for item in data
    )
    
    # Mock response
    updated_ranges = [item['range'] for item in data]
    
    result = {
        "spreadsheet_id": spreadsheet_id,
        "total_updated_rows": sum(len(item['values']) for item in data),
        "total_updated_columns": max(len(item['values'][0]) if item['values'] and item['values'][0] else 0 for item in data),
        "total_updated_cells": total_cells_updated,
        "updated_ranges": updated_ranges,
        "value_input_option": value_input_option,
        "timestamp": datetime.now().isoformat(),
        "event_id": event_id,
        "mock_data": True
    }
    
    if ctx.tool_events:
        last_event = ctx.tool_events[-1]
        last_event.result_summary = {
            "status": "success",
            "ranges_updated": len(data),
            "cells_updated": total_cells_updated
        }
        last_event.duration_ms = 400
        last_event.status = "success"
    
    return result


@register_mds_tool(
    name="sheets_append",
    display_name="Sheets Append",
    description="Append rows of data to a Google Spreadsheet",
    category="google_workspace",
    version="1.0.0",
    tags=["sheets", "write", "append", "google-workspace", "mock"],
    enabled=True,
    requires_auth=True,
    required_permissions=["sheets:write"],
    requires_casefile=False,
    timeout_seconds=30,
    params_model=SheetsAppendParams,
)
async def sheets_append(
    ctx: MDSContext,
    spreadsheet_id: str,
    range: str,
    values: List[List[Any]],
    value_input_option: str = "USER_ENTERED",
    insert_data_option: str = "INSERT_ROWS"
) -> Dict[str, Any]:
    """
    Append rows of data to a Google Spreadsheet.
    
    This is a MOCK implementation. Real implementation in Week 4.
    
    Args:
        ctx: MDSContext
        spreadsheet_id: The ID of the spreadsheet (validated)
        range: The A1 notation range to append to (validated)
        values: 2D array of values to append (validated)
        value_input_option: How to interpret input (validated)
        insert_data_option: How to insert data (validated)
        
    Returns:
        Mock response matching Google Sheets API structure
    """
    event_id = ctx.register_event(
        "sheets_append",
        {
            "spreadsheet_id": spreadsheet_id,
            "range": range,
            "rows_count": len(values),
            "value_input_option": value_input_option,
            "insert_data_option": insert_data_option
        }
    )
    
    await asyncio.sleep(0.3)
    
    # Mock the updated range (where data was appended)
    # In real implementation, this would come from the API
    updated_range = f"{range}:{chr(65 + len(values[0]) - 1)}{len(values)}"
    
    result = {
        "spreadsheet_id": spreadsheet_id,
        "table_range": range,
        "updates": {
            "spreadsheet_id": spreadsheet_id,
            "updated_range": updated_range,
            "updated_rows": len(values),
            "updated_columns": len(values[0]) if values and values[0] else 0,
            "updated_cells": sum(len(row) for row in values)
        },
        "value_input_option": value_input_option,
        "insert_data_option": insert_data_option,
        "timestamp": datetime.now().isoformat(),
        "event_id": event_id,
        "mock_data": True
    }
    
    if ctx.tool_events:
        last_event = ctx.tool_events[-1]
        last_event.result_summary = {
            "status": "success",
            "rows_appended": len(values),
            "cells_appended": sum(len(row) for row in values)
        }
        last_event.duration_ms = 300
        last_event.status = "success"
    
    return result


@register_mds_tool(
    name="sheets_create",
    display_name="Sheets Create",
    description="Create a new Google Spreadsheet",
    category="google_workspace",
    version="1.0.0",
    tags=["sheets", "create", "google-workspace", "mock"],
    enabled=True,
    requires_auth=True,
    required_permissions=["sheets:create"],
    requires_casefile=False,
    timeout_seconds=30,
    params_model=SheetsCreateParams,
)
async def sheets_create(
    ctx: MDSContext,
    title: str,
    sheets: Optional[List[Dict[str, Any]]] = None,
    locale: str = "en_US"
) -> Dict[str, Any]:
    """
    Create a new Google Spreadsheet.
    
    This is a MOCK implementation. Real implementation in Week 4.
    
    Args:
        ctx: MDSContext
        title: The title of the new spreadsheet (validated)
        sheets: Optional list of sheet configurations (validated)
        locale: The locale of the spreadsheet (validated)
        
    Returns:
        Mock response matching Google Sheets API structure
    """
    event_id = ctx.register_event(
        "sheets_create",
        {
            "title": title,
            "sheets_count": len(sheets) if sheets else 1,
            "locale": locale
        }
    )
    
    await asyncio.sleep(0.5)
    
    # Generate mock spreadsheet ID
    spreadsheet_id = generate_mock_spreadsheet_id()
    spreadsheet_url = f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/edit"
    
    # Process sheets configuration
    if not sheets:
        sheets = [{"title": "Sheet1", "row_count": 1000, "column_count": 26}]
    
    mock_sheets = []
    for i, sheet_config in enumerate(sheets):
        sheet_title = sheet_config.get("title", f"Sheet{i + 1}")
        sheet_id = i
        mock_sheets.append({
            "sheet_id": sheet_id,
            "title": sheet_title,
            "index": i,
            "sheet_type": "GRID",
            "grid_properties": {
                "row_count": sheet_config.get("row_count", 1000),
                "column_count": sheet_config.get("column_count", 26)
            }
        })
    
    result = {
        "spreadsheet_id": spreadsheet_id,
        "spreadsheet_url": spreadsheet_url,
        "properties": {
            "title": title,
            "locale": locale,
            "auto_recalc": "ON_CHANGE",
            "time_zone": "America/New_York"
        },
        "sheets": mock_sheets,
        "timestamp": datetime.now().isoformat(),
        "event_id": event_id,
        "mock_data": True
    }
    
    if ctx.tool_events:
        last_event = ctx.tool_events[-1]
        last_event.result_summary = {
            "status": "success",
            "spreadsheet_id": spreadsheet_id,
            "sheets_created": len(mock_sheets)
        }
        last_event.duration_ms = 500
        last_event.status = "success"
    
    return result
