# Google Sheets Tools Documentation

This document describes the Google Sheets toolset implemented for the MDS Objects API.

## Overview

The Sheets toolset provides four core operations for interacting with Google Spreadsheets:

1. **sheets_batch_get** - Read data from multiple ranges
2. **sheets_batch_update** - Update data in multiple ranges
3. **sheets_append** - Append rows to a sheet
4. **sheets_create** - Create a new spreadsheet

## Implementation Status

**Current Phase:** Week 2 - Mock Implementation

- ✅ YAML definitions created
- ✅ Parameter models with validation
- ✅ Mock implementations with realistic data structures
- ✅ 20+ comprehensive test cases
- ⏳ Real Google Sheets API integration (Week 4)

## Tools

### 1. sheets_batch_get

Read data from multiple ranges in a Google Spreadsheet.

**Category:** `google_workspace`  
**Permissions Required:** `sheets:read`  
**Timeout:** 30 seconds

#### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| spreadsheet_id | string | Yes | - | The ID of the spreadsheet to read from |
| ranges | array | Yes | - | List of A1 notation ranges (1-10 ranges) |
| major_dimension | string | No | "ROWS" | How to organize data ("ROWS" or "COLUMNS") |

#### Constraints

- `spreadsheet_id`: 1-100 characters, alphanumeric plus `_-`
- `ranges`: 1-10 ranges, each non-empty
- `major_dimension`: Must be "ROWS" or "COLUMNS"

#### Example Usage

```python
result = await sheets_batch_get(
    ctx,
    spreadsheet_id="1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms",
    ranges=["Sheet1!A1:D10", "Sheet2!B2:C5"],
    major_dimension="ROWS"
)
```

#### Response Structure

```json
{
  "spreadsheet_id": "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms",
  "value_ranges": [
    {
      "range": "Sheet1!A1:D10",
      "majorDimension": "ROWS",
      "values": [
        ["Column A", "Column B", "Column C", "Column D"],
        [1, "Item 1", 42.5, true],
        [2, "Item 2", 87.3, false]
      ]
    }
  ],
  "ranges_read": 2,
  "timestamp": "2025-10-02T10:30:00.123456",
  "event_id": "evt_abc123",
  "mock_data": true
}
```

---

### 2. sheets_batch_update

Update data in multiple ranges in a Google Spreadsheet.

**Category:** `google_workspace`  
**Permissions Required:** `sheets:write`  
**Timeout:** 45 seconds

#### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| spreadsheet_id | string | Yes | - | The ID of the spreadsheet to update |
| data | array | Yes | - | List of value ranges to update (1-10 entries) |
| value_input_option | string | No | "USER_ENTERED" | How to interpret input ("USER_ENTERED" or "RAW") |

#### Constraints

- `spreadsheet_id`: 1-100 characters, alphanumeric plus `_-`
- `data`: 1-10 value ranges, each must have `range` and `values` fields
- `value_input_option`: Must be "USER_ENTERED" or "RAW"

#### Example Usage

```python
result = await sheets_batch_update(
    ctx,
    spreadsheet_id="1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms",
    data=[
        {
            "range": "Sheet1!A1:B2",
            "values": [[1, 2], [3, 4]]
        },
        {
            "range": "Sheet2!C3:D4",
            "values": [["a", "b"], ["c", "d"]]
        }
    ],
    value_input_option="USER_ENTERED"
)
```

#### Response Structure

```json
{
  "spreadsheet_id": "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms",
  "total_updated_rows": 4,
  "total_updated_columns": 2,
  "total_updated_cells": 8,
  "updated_ranges": ["Sheet1!A1:B2", "Sheet2!C3:D4"],
  "value_input_option": "USER_ENTERED",
  "timestamp": "2025-10-02T10:30:00.123456",
  "event_id": "evt_def456",
  "mock_data": true
}
```

---

### 3. sheets_append

Append rows of data to a Google Spreadsheet.

**Category:** `google_workspace`  
**Permissions Required:** `sheets:write`  
**Timeout:** 30 seconds

#### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| spreadsheet_id | string | Yes | - | The ID of the spreadsheet to append to |
| range | string | Yes | - | The A1 notation range to append to |
| values | array | Yes | - | 2D array of values to append (1-1000 rows) |
| value_input_option | string | No | "USER_ENTERED" | How to interpret input |
| insert_data_option | string | No | "INSERT_ROWS" | How to insert ("INSERT_ROWS" or "OVERWRITE") |

#### Constraints

- `spreadsheet_id`: 1-100 characters, alphanumeric plus `_-`
- `range`: 1-100 characters
- `values`: 1-1000 rows, must be a 2D array
- `value_input_option`: Must be "USER_ENTERED" or "RAW"
- `insert_data_option`: Must be "INSERT_ROWS" or "OVERWRITE"

#### Example Usage

```python
result = await sheets_append(
    ctx,
    spreadsheet_id="1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms",
    range="Sheet1!A1",
    values=[
        ["John Doe", 30, "New York"],
        ["Jane Smith", 25, "Los Angeles"],
        ["Bob Johnson", 35, "Chicago"]
    ],
    value_input_option="USER_ENTERED",
    insert_data_option="INSERT_ROWS"
)
```

#### Response Structure

```json
{
  "spreadsheet_id": "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms",
  "table_range": "Sheet1!A1",
  "updates": {
    "spreadsheet_id": "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms",
    "updated_range": "Sheet1!A1:C3",
    "updated_rows": 3,
    "updated_columns": 3,
    "updated_cells": 9
  },
  "value_input_option": "USER_ENTERED",
  "insert_data_option": "INSERT_ROWS",
  "timestamp": "2025-10-02T10:30:00.123456",
  "event_id": "evt_ghi789",
  "mock_data": true
}
```

---

### 4. sheets_create

Create a new Google Spreadsheet.

**Category:** `google_workspace`  
**Permissions Required:** `sheets:create`  
**Timeout:** 30 seconds

#### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| title | string | Yes | - | The title of the new spreadsheet |
| sheets | array | No | null | List of sheet configurations (0-10 sheets) |
| locale | string | No | "en_US" | The locale of the spreadsheet |

#### Constraints

- `title`: 1-255 characters
- `sheets`: 0-10 sheet configurations
- `locale`: 2-10 characters

#### Sheet Configuration

Each sheet configuration can include:
- `title` (required): Sheet name
- `row_count` (optional): Number of rows (default: 1000)
- `column_count` (optional): Number of columns (default: 26)

#### Example Usage

```python
result = await sheets_create(
    ctx,
    title="Q4 Sales Report",
    sheets=[
        {
            "title": "Sales Data",
            "row_count": 500,
            "column_count": 12
        },
        {
            "title": "Summary",
            "row_count": 100,
            "column_count": 5
        }
    ],
    locale="en_US"
)
```

#### Response Structure

```json
{
  "spreadsheet_id": "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms",
  "spreadsheet_url": "https://docs.google.com/spreadsheets/d/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms/edit",
  "properties": {
    "title": "Q4 Sales Report",
    "locale": "en_US",
    "auto_recalc": "ON_CHANGE",
    "time_zone": "America/New_York"
  },
  "sheets": [
    {
      "sheet_id": 0,
      "title": "Sales Data",
      "index": 0,
      "sheet_type": "GRID",
      "grid_properties": {
        "row_count": 500,
        "column_count": 12
      }
    },
    {
      "sheet_id": 1,
      "title": "Summary",
      "index": 1,
      "sheet_type": "GRID",
      "grid_properties": {
        "row_count": 100,
        "column_count": 5
      }
    }
  ],
  "timestamp": "2025-10-02T10:30:00.123456",
  "event_id": "evt_jkl012",
  "mock_data": true
}
```

---

## Data Transforms

All tools include automatic data transforms:

### Input Transforms
- **Validation**: Pydantic models validate all inputs before execution
- **Type Coercion**: Parameters are coerced to correct types
- **Constraint Enforcement**: Min/max lengths, patterns, enums are enforced

### Output Transforms
- **Timestamp Addition**: All responses include ISO 8601 timestamps
- **Event Tracking**: Event IDs are added for audit trail
- **Context Integration**: Results are linked to session context

### Error Handling

All tools handle errors consistently:

```python
try:
    result = await sheets_batch_get(ctx, ...)
except ValidationError as e:
    # Parameter validation failed
    # Details in e.errors()
except Exception as e:
    # Tool execution failed
    # Event is still logged with error status
```

---

## Testing

The Sheets toolset includes 20+ comprehensive test cases covering:

### Parameter Validation Tests (Unit)
- Valid parameters accepted
- Invalid parameters rejected
- Edge cases (empty, max values, patterns)
- Type validation
- Constraint validation

### Execution Tests (Integration/Mock)
- Basic happy path execution
- Multiple ranges/sheets
- Different options (RAW vs USER_ENTERED, etc.)
- Event registration
- Result structure validation

### Running Tests

```bash
# Run all Sheets tests
pytest tests/test_sheets_tools.py -v

# Run only unit tests (fast)
pytest tests/test_sheets_tools.py -m unit -v

# Run only integration tests
pytest tests/test_sheets_tools.py -m integration -v

# Run with coverage
pytest tests/test_sheets_tools.py --cov=src.pydantic_ai_integration.tools.sheets_tools
```

---

## Mock Data Characteristics

Current mock implementation returns:
- **Realistic structure**: Matches Google Sheets API response format
- **Random data**: Each execution generates different mock data
- **Configurable size**: Based on input parameters (ranges, rows, etc.)
- **Type variety**: Mixes strings, numbers, booleans, nulls
- **Mock indicator**: All responses include `"mock_data": true`

---

## Future Enhancements (Week 4)

When transitioning to real Google Sheets API:

1. **API Client Wrapper**: Create `GoogleSheetsClient` class
2. **OAuth2 Authentication**: Implement credential flow
3. **Rate Limiting**: Add exponential backoff for API rate limits
4. **Error Handling**: Handle API-specific errors (quota, permissions, etc.)
5. **Batch Optimization**: Optimize batch requests for efficiency
6. **Caching**: Add response caching where appropriate
7. **Webhooks**: Support real-time updates via webhooks

---

## Architecture Notes

### Tool Registration

All tools use the `@register_mds_tool` decorator for unified registration:

```python
@register_mds_tool(
    name="sheets_batch_get",
    description="...",
    category="google_workspace",
    required_permissions=["sheets:read"],
    params_model=SheetsBatchGetParams,
    # ...
)
async def sheets_batch_get(ctx: MDSContext, ...) -> Dict[str, Any]:
    # Implementation
```

### Parameter Models

Parameter models use Pydantic for validation:

```python
class SheetsBatchGetParams(BaseModel):
    spreadsheet_id: str = Field(..., pattern=r"^[a-zA-Z0-9_-]+$")
    ranges: List[str] = Field(..., min_length=1, max_length=10)
    major_dimension: Literal["ROWS", "COLUMNS"] = "ROWS"
```

### Context Integration

All tools integrate with `MDSContext`:

```python
# Register event for audit trail
event_id = ctx.register_event("sheets_batch_get", params)

# Update event with results
if ctx.tool_events:
    last_event = ctx.tool_events[-1]
    last_event.result_summary = {"status": "success", ...}
    last_event.status = "success"
```

---

## Configuration Files

### YAML Definition

Tool definitions are stored in `config/tools/sheets_tools.yaml`:

```yaml
tools:
  - name: sheets_batch_get
    display_name: "Sheets Batch Get"
    description: "Read data from multiple ranges"
    category: "google_workspace"
    parameters:
      - name: spreadsheet_id
        type: string
        required: true
        pattern: "^[a-zA-Z0-9_-]+$"
      # ...
```

This YAML serves as the source of truth and can be used by:
- Documentation generators
- Tool discovery APIs
- Code generators (future)
- AI analysis tools (future)

---

## Related Documentation

- [TOOLENGINEERING_FOUNDATION.md](./TOOLENGINEERING_FOUNDATION.md) - Tool factory architecture
- [API_ERROR_RESPONSES.md](./API_ERROR_RESPONSES.md) - Error handling patterns
- [TESTING.md](./TESTING.md) - Testing guidelines

---

## Support & Contact

For questions or issues with the Sheets toolset:
1. Check test cases for usage examples
2. Review this documentation
3. Consult TOOLENGINEERING_FOUNDATION.md for architectural details
4. File an issue with reproduction steps

---

**Last Updated:** 2025-10-02  
**Version:** 1.0.0 (Mock Implementation)  
**Status:** ✅ Week 2 Complete - Ready for Week 4 Real API Integration
