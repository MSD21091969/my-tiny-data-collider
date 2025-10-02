"""
Tests for Google Sheets tools.

This module contains comprehensive tests for all Sheets tools:
- sheets_batch_get
- sheets_batch_update
- sheets_append
- sheets_create

Tests cover:
- Parameter validation (guardrails)
- Happy path execution
- Edge cases
- Error cases
- Mock data structure validation
"""

import pytest
from typing import Dict, Any, List
from pydantic import ValidationError

from src.pydantic_ai_integration.tools.sheets_tools import (
    SheetsBatchGetParams,
    SheetsBatchUpdateParams,
    SheetsAppendParams,
    SheetsCreateParams,
    sheets_batch_get,
    sheets_batch_update,
    sheets_append,
    sheets_create,
)
from src.pydantic_ai_integration.dependencies import MDSContext


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def mock_context():
    """Create a minimal MDSContext for testing."""
    ctx = MDSContext(
        user_id="test_user",
        session_id="test_session",
        casefile_id=None
    )
    return ctx


@pytest.fixture
def valid_spreadsheet_id():
    """Return a valid spreadsheet ID."""
    return "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms"


# ============================================================================
# PARAMETER VALIDATION TESTS
# ============================================================================

@pytest.mark.unit
class TestSheetsBatchGetParams:
    """Test parameter validation for sheets_batch_get."""
    
    def test_valid_params(self):
        """Test that valid parameters are accepted."""
        params = SheetsBatchGetParams(
            spreadsheet_id="test_spreadsheet_123",
            ranges=["Sheet1!A1:D10", "Sheet2!B2:C5"]
        )
        assert params.spreadsheet_id == "test_spreadsheet_123"
        assert len(params.ranges) == 2
        assert params.major_dimension == "ROWS"
    
    def test_valid_params_with_columns(self):
        """Test that COLUMNS major_dimension is accepted."""
        params = SheetsBatchGetParams(
            spreadsheet_id="test_id",
            ranges=["Sheet1!A1:B2"],
            major_dimension="COLUMNS"
        )
        assert params.major_dimension == "COLUMNS"
    
    def test_invalid_spreadsheet_id_empty(self):
        """Test that empty spreadsheet_id is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            SheetsBatchGetParams(
                spreadsheet_id="",
                ranges=["Sheet1!A1:D10"]
            )
        assert "spreadsheet_id" in str(exc_info.value)
    
    def test_invalid_spreadsheet_id_pattern(self):
        """Test that invalid characters in spreadsheet_id are rejected."""
        with pytest.raises(ValidationError) as exc_info:
            SheetsBatchGetParams(
                spreadsheet_id="invalid@#$%id",
                ranges=["Sheet1!A1:D10"]
            )
        assert "spreadsheet_id" in str(exc_info.value)
    
    def test_invalid_ranges_empty_list(self):
        """Test that empty ranges list is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            SheetsBatchGetParams(
                spreadsheet_id="test_id",
                ranges=[]
            )
        assert "ranges" in str(exc_info.value)
    
    def test_invalid_ranges_too_many(self):
        """Test that more than 10 ranges is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            SheetsBatchGetParams(
                spreadsheet_id="test_id",
                ranges=[f"Sheet{i}!A1:B2" for i in range(11)]
            )
        assert "ranges" in str(exc_info.value)
    
    def test_invalid_ranges_empty_string(self):
        """Test that empty strings in ranges are rejected."""
        with pytest.raises(ValidationError) as exc_info:
            SheetsBatchGetParams(
                spreadsheet_id="test_id",
                ranges=["Sheet1!A1:B2", ""]
            )
        assert "ranges" in str(exc_info.value)
    
    def test_invalid_major_dimension(self):
        """Test that invalid major_dimension is rejected."""
        with pytest.raises(ValidationError):
            SheetsBatchGetParams(
                spreadsheet_id="test_id",
                ranges=["Sheet1!A1:B2"],
                major_dimension="INVALID"
            )


@pytest.mark.unit
class TestSheetsBatchUpdateParams:
    """Test parameter validation for sheets_batch_update."""
    
    def test_valid_params(self):
        """Test that valid parameters are accepted."""
        params = SheetsBatchUpdateParams(
            spreadsheet_id="test_id",
            data=[
                {"range": "Sheet1!A1:B2", "values": [[1, 2], [3, 4]]},
                {"range": "Sheet2!C3:D4", "values": [["a", "b"], ["c", "d"]]}
            ]
        )
        assert params.spreadsheet_id == "test_id"
        assert len(params.data) == 2
        assert params.value_input_option == "USER_ENTERED"
    
    def test_valid_params_raw_input(self):
        """Test that RAW value_input_option is accepted."""
        params = SheetsBatchUpdateParams(
            spreadsheet_id="test_id",
            data=[{"range": "Sheet1!A1:B2", "values": [[1, 2]]}],
            value_input_option="RAW"
        )
        assert params.value_input_option == "RAW"
    
    def test_invalid_data_empty_list(self):
        """Test that empty data list is rejected."""
        with pytest.raises(ValidationError):
            SheetsBatchUpdateParams(
                spreadsheet_id="test_id",
                data=[]
            )
    
    def test_invalid_data_too_many(self):
        """Test that more than 10 data entries is rejected."""
        with pytest.raises(ValidationError):
            SheetsBatchUpdateParams(
                spreadsheet_id="test_id",
                data=[{"range": f"Sheet{i}!A1:B2", "values": [[1, 2]]} for i in range(11)]
            )
    
    def test_invalid_data_missing_range(self):
        """Test that data without 'range' is rejected."""
        with pytest.raises(ValidationError):
            SheetsBatchUpdateParams(
                spreadsheet_id="test_id",
                data=[{"values": [[1, 2]]}]
            )
    
    def test_invalid_data_missing_values(self):
        """Test that data without 'values' is rejected."""
        with pytest.raises(ValidationError):
            SheetsBatchUpdateParams(
                spreadsheet_id="test_id",
                data=[{"range": "Sheet1!A1:B2"}]
            )
    
    def test_invalid_data_values_not_list(self):
        """Test that non-list values are rejected."""
        with pytest.raises(ValidationError):
            SheetsBatchUpdateParams(
                spreadsheet_id="test_id",
                data=[{"range": "Sheet1!A1:B2", "values": "not_a_list"}]
            )
    
    def test_invalid_value_input_option(self):
        """Test that invalid value_input_option is rejected."""
        with pytest.raises(ValidationError):
            SheetsBatchUpdateParams(
                spreadsheet_id="test_id",
                data=[{"range": "Sheet1!A1:B2", "values": [[1, 2]]}],
                value_input_option="INVALID"
            )


@pytest.mark.unit
class TestSheetsAppendParams:
    """Test parameter validation for sheets_append."""
    
    def test_valid_params(self):
        """Test that valid parameters are accepted."""
        params = SheetsAppendParams(
            spreadsheet_id="test_id",
            range="Sheet1!A1",
            values=[[1, 2, 3], [4, 5, 6]]
        )
        assert params.spreadsheet_id == "test_id"
        assert params.range == "Sheet1!A1"
        assert len(params.values) == 2
    
    def test_valid_params_with_options(self):
        """Test that all optional parameters are accepted."""
        params = SheetsAppendParams(
            spreadsheet_id="test_id",
            range="Sheet1!A1",
            values=[[1, 2]],
            value_input_option="RAW",
            insert_data_option="OVERWRITE"
        )
        assert params.value_input_option == "RAW"
        assert params.insert_data_option == "OVERWRITE"
    
    def test_invalid_values_empty(self):
        """Test that empty values list is rejected."""
        with pytest.raises(ValidationError):
            SheetsAppendParams(
                spreadsheet_id="test_id",
                range="Sheet1!A1",
                values=[]
            )
    
    def test_invalid_values_too_many(self):
        """Test that more than 1000 rows is rejected."""
        with pytest.raises(ValidationError):
            SheetsAppendParams(
                spreadsheet_id="test_id",
                range="Sheet1!A1",
                values=[[1, 2]] * 1001
            )
    
    def test_invalid_values_not_2d_array(self):
        """Test that non-2D array values are rejected."""
        with pytest.raises(ValidationError):
            SheetsAppendParams(
                spreadsheet_id="test_id",
                range="Sheet1!A1",
                values=[1, 2, 3]  # Should be [[1, 2, 3]]
            )
    
    def test_invalid_range_empty(self):
        """Test that empty range is rejected."""
        with pytest.raises(ValidationError):
            SheetsAppendParams(
                spreadsheet_id="test_id",
                range="",
                values=[[1, 2]]
            )


@pytest.mark.unit
class TestSheetsCreateParams:
    """Test parameter validation for sheets_create."""
    
    def test_valid_params_minimal(self):
        """Test that minimal valid parameters are accepted."""
        params = SheetsCreateParams(title="My Spreadsheet")
        assert params.title == "My Spreadsheet"
        assert params.locale == "en_US"
        assert params.sheets is None
    
    def test_valid_params_with_sheets(self):
        """Test that valid parameters with sheets are accepted."""
        params = SheetsCreateParams(
            title="My Spreadsheet",
            sheets=[
                {"title": "Sheet1", "row_count": 100, "column_count": 10},
                {"title": "Sheet2"}
            ],
            locale="fr_FR"
        )
        assert params.title == "My Spreadsheet"
        assert len(params.sheets) == 2
        assert params.locale == "fr_FR"
    
    def test_invalid_title_empty(self):
        """Test that empty title is rejected."""
        with pytest.raises(ValidationError):
            SheetsCreateParams(title="")
    
    def test_invalid_title_too_long(self):
        """Test that title longer than 255 chars is rejected."""
        with pytest.raises(ValidationError):
            SheetsCreateParams(title="a" * 256)
    
    def test_invalid_sheets_too_many(self):
        """Test that more than 10 sheets is rejected."""
        with pytest.raises(ValidationError):
            SheetsCreateParams(
                title="Test",
                sheets=[{"title": f"Sheet{i}"} for i in range(11)]
            )
    
    def test_invalid_locale_too_short(self):
        """Test that locale shorter than 2 chars is rejected."""
        with pytest.raises(ValidationError):
            SheetsCreateParams(title="Test", locale="a")


# ============================================================================
# TOOL EXECUTION TESTS
# ============================================================================

@pytest.mark.integration
@pytest.mark.mock
class TestSheetsBatchGetExecution:
    """Test execution of sheets_batch_get tool."""
    
    @pytest.mark.asyncio
    async def test_basic_execution(self, mock_context, valid_spreadsheet_id):
        """Test basic execution returns expected structure."""
        result = await sheets_batch_get(
            mock_context,
            spreadsheet_id=valid_spreadsheet_id,
            ranges=["Sheet1!A1:D10"]
        )
        
        assert result["spreadsheet_id"] == valid_spreadsheet_id
        assert "value_ranges" in result
        assert len(result["value_ranges"]) == 1
        assert result["mock_data"] is True
        assert "timestamp" in result
        assert "event_id" in result
    
    @pytest.mark.asyncio
    async def test_multiple_ranges(self, mock_context, valid_spreadsheet_id):
        """Test execution with multiple ranges."""
        result = await sheets_batch_get(
            mock_context,
            spreadsheet_id=valid_spreadsheet_id,
            ranges=["Sheet1!A1:D10", "Sheet2!B2:C5", "Sheet3!E1:F20"]
        )
        
        assert len(result["value_ranges"]) == 3
        assert result["ranges_read"] == 3
    
    @pytest.mark.asyncio
    async def test_columns_major_dimension(self, mock_context, valid_spreadsheet_id):
        """Test execution with COLUMNS major dimension."""
        result = await sheets_batch_get(
            mock_context,
            spreadsheet_id=valid_spreadsheet_id,
            ranges=["Sheet1!A1:D10"],
            major_dimension="COLUMNS"
        )
        
        assert result["value_ranges"][0]["majorDimension"] == "COLUMNS"
    
    @pytest.mark.asyncio
    async def test_event_registration(self, mock_context, valid_spreadsheet_id):
        """Test that event is registered in context."""
        result = await sheets_batch_get(
            mock_context,
            spreadsheet_id=valid_spreadsheet_id,
            ranges=["Sheet1!A1:D10"]
        )
        
        assert len(mock_context.tool_events) > 0
        last_event = mock_context.tool_events[-1]
        assert last_event.event_type == "tool_execution_completed"
        assert last_event.status == "success"
        assert last_event.tool_name == "sheets_batch_get"


@pytest.mark.integration
@pytest.mark.mock
class TestSheetsBatchUpdateExecution:
    """Test execution of sheets_batch_update tool."""
    
    @pytest.mark.asyncio
    async def test_basic_execution(self, mock_context, valid_spreadsheet_id):
        """Test basic execution returns expected structure."""
        result = await sheets_batch_update(
            mock_context,
            spreadsheet_id=valid_spreadsheet_id,
            data=[{"range": "Sheet1!A1:B2", "values": [[1, 2], [3, 4]]}]
        )
        
        assert result["spreadsheet_id"] == valid_spreadsheet_id
        assert result["total_updated_rows"] == 2
        assert result["total_updated_cells"] == 4
        assert result["mock_data"] is True
    
    @pytest.mark.asyncio
    async def test_multiple_ranges_update(self, mock_context, valid_spreadsheet_id):
        """Test updating multiple ranges."""
        result = await sheets_batch_update(
            mock_context,
            spreadsheet_id=valid_spreadsheet_id,
            data=[
                {"range": "Sheet1!A1:B2", "values": [[1, 2], [3, 4]]},
                {"range": "Sheet2!C3:D5", "values": [["a", "b"], ["c", "d"], ["e", "f"]]}
            ]
        )
        
        assert len(result["updated_ranges"]) == 2
        assert result["total_updated_rows"] == 5
    
    @pytest.mark.asyncio
    async def test_raw_input_option(self, mock_context, valid_spreadsheet_id):
        """Test with RAW value input option."""
        result = await sheets_batch_update(
            mock_context,
            spreadsheet_id=valid_spreadsheet_id,
            data=[{"range": "Sheet1!A1:B2", "values": [["=SUM(A1:A10)", "raw"]]}],
            value_input_option="RAW"
        )
        
        assert result["value_input_option"] == "RAW"


@pytest.mark.integration
@pytest.mark.mock
class TestSheetsAppendExecution:
    """Test execution of sheets_append tool."""
    
    @pytest.mark.asyncio
    async def test_basic_execution(self, mock_context, valid_spreadsheet_id):
        """Test basic execution returns expected structure."""
        result = await sheets_append(
            mock_context,
            spreadsheet_id=valid_spreadsheet_id,
            range="Sheet1!A1",
            values=[[1, 2, 3], [4, 5, 6]]
        )
        
        assert result["spreadsheet_id"] == valid_spreadsheet_id
        assert result["updates"]["updated_rows"] == 2
        assert result["updates"]["updated_cells"] == 6
        assert result["mock_data"] is True
    
    @pytest.mark.asyncio
    async def test_single_row_append(self, mock_context, valid_spreadsheet_id):
        """Test appending a single row."""
        result = await sheets_append(
            mock_context,
            spreadsheet_id=valid_spreadsheet_id,
            range="Sheet1!A1",
            values=[["Name", "Age", "City"]]
        )
        
        assert result["updates"]["updated_rows"] == 1
        assert result["updates"]["updated_columns"] == 3
    
    @pytest.mark.asyncio
    async def test_overwrite_option(self, mock_context, valid_spreadsheet_id):
        """Test with OVERWRITE insert option."""
        result = await sheets_append(
            mock_context,
            spreadsheet_id=valid_spreadsheet_id,
            range="Sheet1!A1",
            values=[[1, 2], [3, 4]],
            insert_data_option="OVERWRITE"
        )
        
        assert result["insert_data_option"] == "OVERWRITE"


@pytest.mark.integration
@pytest.mark.mock
class TestSheetsCreateExecution:
    """Test execution of sheets_create tool."""
    
    @pytest.mark.asyncio
    async def test_basic_execution(self, mock_context):
        """Test basic execution returns expected structure."""
        result = await sheets_create(
            mock_context,
            title="Test Spreadsheet"
        )
        
        assert result["properties"]["title"] == "Test Spreadsheet"
        assert "spreadsheet_id" in result
        assert "spreadsheet_url" in result
        assert len(result["sheets"]) == 1
        assert result["mock_data"] is True
    
    @pytest.mark.asyncio
    async def test_with_multiple_sheets(self, mock_context):
        """Test creating spreadsheet with multiple sheets."""
        result = await sheets_create(
            mock_context,
            title="Multi-Sheet Spreadsheet",
            sheets=[
                {"title": "Data", "row_count": 500, "column_count": 15},
                {"title": "Summary", "row_count": 100, "column_count": 5},
                {"title": "Archive"}
            ]
        )
        
        assert len(result["sheets"]) == 3
        assert result["sheets"][0]["title"] == "Data"
        assert result["sheets"][0]["grid_properties"]["row_count"] == 500
        assert result["sheets"][1]["title"] == "Summary"
        assert result["sheets"][2]["title"] == "Archive"
    
    @pytest.mark.asyncio
    async def test_with_locale(self, mock_context):
        """Test creating spreadsheet with custom locale."""
        result = await sheets_create(
            mock_context,
            title="French Spreadsheet",
            locale="fr_FR"
        )
        
        assert result["properties"]["locale"] == "fr_FR"
    
    @pytest.mark.asyncio
    async def test_generated_spreadsheet_id_format(self, mock_context):
        """Test that generated spreadsheet ID has correct format."""
        result = await sheets_create(
            mock_context,
            title="Test"
        )
        
        spreadsheet_id = result["spreadsheet_id"]
        assert len(spreadsheet_id) == 44
        assert all(c.isalnum() or c in '_-' for c in spreadsheet_id)
        assert result["spreadsheet_url"].startswith("https://docs.google.com/spreadsheets/d/")
