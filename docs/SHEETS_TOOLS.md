# Google Sheets Tools Documentation

## Overview

The Google Sheets toolset provides AI agents and users with structured access to Google Sheets spreadsheet data through Pydantic-validated tools. This implementation follows the N-tier layered architecture with YAML-driven tool generation.

**Status:** Week 2 - Mock Implementation (Real API integration planned for Week 3+)

**Architecture Flow:**
```
Agent/API Layer
    ↓
MDSContext(user_id, session_id, casefile_id)
    ↓
Tool Layer (sheets_batch_get)
    ↓
Client Layer (SheetsClient)
    ↓
DTOs (SheetsBatchGetRequest/Response)
    ↓
Canonical Models (SheetsSpreadsheet)
```

## Tools

### sheets_batch_get

Retrieves one or more ranges from a Google Sheets spreadsheet using A1 notation.

**Function Signature:**
```python
async def sheets_batch_get(
    ctx: MDSContext,
    spreadsheet_id: str,
    ranges: List[str]
) -> Dict[str, Any]
```

**Parameters:**

| Parameter | Type | Required | Constraints | Description |
|-----------|------|----------|-------------|-------------|
| `spreadsheet_id` | `string` | Yes | min_length: 1 | The ID of the spreadsheet (from URL: `https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/edit`) |
| `ranges` | `array[string]` | Yes | min_items: 1 | List of ranges in A1 notation (e.g., `["Sheet1!A1:D10", "Sheet2!B2:E5"]`) |

**Returns:**
```python
{
    "success": True,
    "data": {
        "spreadsheet_id": "1abc...",
        "spreadsheet_name": "Q1 Sales Data",
        "value_ranges": [
            {
                "range": "Sheet1!A1:D10",
                "major_dimension": "ROWS",
                "values": [
                    ["Header1", "Header2", "Header3", "Header4"],
                    ["Value1", "Value2", "Value3", "Value4"],
                    ...
                ]
            },
            ...
        ],
        "sheets": [
            {
                "sheet_id": 0,
                "title": "Sheet1",
                "index": 0,
                "sheet_type": "GRID"
            }
        ]
    },
    "metadata": {
        "tool_name": "sheets_batch_get",
        "timestamp": "2025-01-10T14:32:00Z",
        "user_id": "user_123",
        "session_id": "session_456",
        "casefile_id": "casefile_789"
    }
}
```

**A1 Notation Examples:**

| Notation | Description | Example Data |
|----------|-------------|--------------|
| `Sheet1!A1:D10` | Rectangle from A1 to D10 on Sheet1 | 10 rows × 4 columns |
| `Sheet1!A:A` | Entire column A | All rows in column A |
| `Sheet1!1:1` | Entire row 1 | All columns in row 1 |
| `Sheet1` | Entire sheet | All data on Sheet1 |
| `'My Sheet'!A1:B5` | Named sheet with space | Quote sheet names with spaces |

**Policy & Audit:**

- **Business Rules:**
  - `require_valid_spreadsheet_id`: Spreadsheet ID must be non-empty
  - `require_valid_ranges`: At least one range must be specified

- **Session Policies:**
  - `session_must_exist`: User must have active session

- **Casefile Policies:**
  - None (read-only operation)

- **Audit Events:**
  - `sheets.batch_get.success`: Successful data retrieval
  - `sheets.batch_get.failure`: Failed operation (invalid range, permission denied, etc.)

**Example Usage (Python):**

```python
from src.pydantic_ai_integration.dependencies import MDSContext

# Create context
ctx = MDSContext(
    user_id="user_abc",
    session_id="session_xyz",
    casefile_id="casefile_123"
)

# Get data from multiple ranges
result = await sheets_batch_get(
    ctx=ctx,
    spreadsheet_id="1abcXYZ...",
    ranges=["Sheet1!A1:D10", "Summary!B2:E5"]
)

print(result["data"]["value_ranges"][0]["values"])
# Output: [["Header1", "Header2", ...], ["Row1Val1", "Row1Val2", ...], ...]
```

**Example Usage (Service Layer):**

```python
from src.tool_sessionservice.models import ToolRequest

request = ToolRequest(
    tool_name="sheets_batch_get",
    parameters={
        "spreadsheet_id": "1abcXYZ...",
        "ranges": ["Sheet1!A1:D10", "Sheet2!B2:E5"]
    },
    user_id="user_abc",
    session_id="session_xyz",
    casefile_id="casefile_123"
)

response = await tool_session_service.execute_tool(request)
```

## Mock Implementation Details

**Current Behavior (Week 2):**

The SheetsClient returns hardcoded mock data for development and testing:

```python
# Mock spreadsheet structure
{
    "spreadsheet_id": "mock_spreadsheet_123",
    "spreadsheet_name": "Mock Spreadsheet",
    "value_ranges": [
        {
            "range": "Sheet1!A1:D3",  # Always returns this range
            "major_dimension": "ROWS",
            "values": [
                ["Name", "Age", "City", "Country"],
                ["Alice", "30", "New York", "USA"],
                ["Bob", "25", "London", "UK"]
            ]
        }
    ],
    "sheets": [
        {
            "sheet_id": 0,
            "title": "Sheet1",
            "index": 0,
            "sheet_type": "GRID"
        }
    ]
}
```

**Mock Limitations:**

1. **Ignores actual `ranges` parameter:** Always returns Sheet1!A1:D3 regardless of requested ranges
2. **Single sheet only:** Mock returns only Sheet1 metadata, even if multiple sheets exist
3. **No error simulation:** Cannot simulate invalid ranges, permission errors, or quota limits
4. **Static data:** No support for dynamic values, formulas, or cell formatting
5. **No major_dimension control:** Always returns ROWS layout (no COLUMNS support)

**Testing Strategy:**

```python
# Unit tests (tests/generated/test_sheets_batch_get.py)
# ✅ 4/6 passing (66.7%)
# - Parameter validation (spreadsheet_id min_length, ranges min_items)
# - Event registration
# - Error handling (missing parameters)

# ❌ Known failures:
# - test_get_data_from_multiple_ranges: Expects simplified dict structure,
#   mock returns full SheetsBatchGetResponse model
# - test_empty_ranges_list: Expects ValidationError, but empty list passes
#   client validation (should be caught at Pydantic level)
```

## Real API Integration (TODO - Week 3+)

**Authentication Setup:**

1. **Enable Google Sheets API:**
   ```bash
   # Visit: https://console.cloud.google.com/apis/library/sheets.googleapis.com
   # Enable for your project
   ```

2. **Create Service Account or OAuth Credentials:**
   ```bash
   # For service account:
   gcloud iam service-accounts create sheets-service-account
   gcloud iam service-accounts keys create credentials.json \
     --iam-account=sheets-service-account@PROJECT_ID.iam.gserviceaccount.com
   ```

3. **Set Environment Variable:**
   ```bash
   export GOOGLE_APPLICATION_CREDENTIALS="/path/to/credentials.json"
   ```

**Replace Mock Client:**

```python
# src/pydantic_ai_integration/google_workspace/clients.py

from googleapiclient.discovery import build
from google.oauth2 import service_account

class SheetsClient:
    def __init__(self):
        credentials = service_account.Credentials.from_service_account_file(
            os.getenv('GOOGLE_APPLICATION_CREDENTIALS'),
            scopes=['https://www.googleapis.com/auth/spreadsheets.readonly']
        )
        self.service = build('sheets', 'v4', credentials=credentials)

    async def batch_get(
        self,
        request: SheetsBatchGetRequest
    ) -> SheetsBatchGetResponse:
        """Real implementation using Google Sheets API v4."""
        try:
            # Get spreadsheet metadata
            spreadsheet = self.service.spreadsheets().get(
                spreadsheetId=request.spreadsheet_id,
                fields='spreadsheetId,properties.title,sheets(properties)'
            ).execute()

            # Get value ranges
            result = self.service.spreadsheets().values().batchGet(
                spreadsheetId=request.spreadsheet_id,
                ranges=request.ranges,
                majorDimension=request.major_dimension or 'ROWS'
            ).execute()

            # Map to canonical models
            value_ranges = [
                SheetsValueRange(
                    range=vr.get('range'),
                    major_dimension=vr.get('majorDimension', 'ROWS'),
                    values=vr.get('values', [])
                )
                for vr in result.get('valueRanges', [])
            ]

            sheets_metadata = [
                SheetsSheet(
                    sheet_id=sheet['properties']['sheetId'],
                    title=sheet['properties']['title'],
                    index=sheet['properties']['index'],
                    sheet_type=sheet['properties'].get('sheetType', 'GRID')
                )
                for sheet in spreadsheet.get('sheets', [])
            ]

            return SheetsBatchGetResponse(
                spreadsheet_id=request.spreadsheet_id,
                spreadsheet_name=spreadsheet['properties']['title'],
                value_ranges=value_ranges,
                sheets=sheets_metadata
            )

        except HttpError as e:
            if e.resp.status == 404:
                raise ValueError(f"Spreadsheet not found: {request.spreadsheet_id}")
            elif e.resp.status == 403:
                raise PermissionError(f"Access denied to spreadsheet: {request.spreadsheet_id}")
            else:
                raise RuntimeError(f"Sheets API error: {e}")
```

**API Quota Limits:**

| Metric | Free Tier | Notes |
|--------|-----------|-------|
| Read requests per day | 500 per user per project | Shared across all Sheets API calls |
| Read requests per 100 seconds | 100 per user per project | Rate limiting applies |
| Batch request size | 100 ranges max | Use batch_get to minimize API calls |

**Error Handling:**

```python
# Common API errors:
# - 400 Bad Request: Invalid range syntax (e.g., "SheetX!A1:Z")
# - 403 Forbidden: No access to spreadsheet or API not enabled
# - 404 Not Found: Spreadsheet doesn't exist or wrong ID
# - 429 Too Many Requests: Exceeded quota limits
# - 500 Internal Server Error: Google Sheets service issue
```

## Data Models

### Canonical Models (pydantic_models/workspace.py)

```python
class SheetsValueRange(BaseModel):
    """A range of values in a spreadsheet."""
    range: str
    major_dimension: str = "ROWS"  # or "COLUMNS"
    values: List[List[Any]]

class SheetsSheet(BaseModel):
    """Metadata about a sheet in a spreadsheet."""
    sheet_id: int
    title: str
    index: int
    sheet_type: str = "GRID"

class SheetsSpreadsheet(BaseModel):
    """Complete spreadsheet with data and metadata."""
    spreadsheet_id: str
    spreadsheet_name: str
    value_ranges: List[SheetsValueRange]
    sheets: List[SheetsSheet]
```

### DTOs (google_workspace/models.py)

```python
class SheetsBatchGetRequest(BaseModel):
    """Request to get multiple ranges from a spreadsheet."""
    spreadsheet_id: str = Field(min_length=1)
    ranges: List[str] = Field(min_length=1)
    major_dimension: Optional[str] = "ROWS"  # Future: support COLUMNS

class SheetsBatchGetResponse(BaseModel):
    """Response containing spreadsheet data."""
    spreadsheet_id: str
    spreadsheet_name: str
    value_ranges: List[SheetsValueRange]
    sheets: List[SheetsSheet]
```

## Advanced Usage Patterns

### Reading Multiple Sheets

```python
result = await sheets_batch_get(
    ctx=ctx,
    spreadsheet_id="1abcXYZ...",
    ranges=[
        "Sales!A1:F100",      # Sales data
        "Summary!A1:D10",     # Summary metrics
        "Config!A1:B5"        # Configuration values
    ]
)

# Process each range
for vr in result["data"]["value_ranges"]:
    print(f"Range: {vr['range']}")
    print(f"Rows: {len(vr['values'])}")
```

### Extracting Headers and Data

```python
result = await sheets_batch_get(
    ctx=ctx,
    spreadsheet_id="1abcXYZ...",
    ranges=["Sheet1!A1:D100"]
)

values = result["data"]["value_ranges"][0]["values"]
headers = values[0]  # First row
data_rows = values[1:]  # Remaining rows

# Convert to list of dicts
records = [
    dict(zip(headers, row))
    for row in data_rows
]
```

### Named Range Support (Future)

```python
# TODO: Support named ranges in addition to A1 notation
result = await sheets_batch_get(
    ctx=ctx,
    spreadsheet_id="1abcXYZ...",
    ranges=["SalesData", "QuarterlyMetrics"]  # Named ranges
)
```

## Integration Testing

**Test Structure (tests/integration/):**

```python
# TODO: Create test_google_workspace_sheets_integration.py

@pytest.mark.integration
@pytest.mark.sheets
async def test_sheets_batch_get_with_policies():
    """Test sheets_batch_get through service layer with policy enforcement."""
    request = ToolRequest(
        tool_name="sheets_batch_get",
        parameters={
            "spreadsheet_id": "mock_spreadsheet_123",
            "ranges": ["Sheet1!A1:D10"]
        },
        user_id="test_user",
        session_id="test_session",
        casefile_id="test_casefile"
    )
    
    response = await tool_session_service.execute_tool(request)
    
    assert response.success
    assert response.data["spreadsheet_id"] == "mock_spreadsheet_123"
    assert len(response.audit_trail) > 0
    assert response.audit_trail[0].event_type == "sheets.batch_get.success"
```

## Future Enhancements

### Write Operations (Week 4+)

```yaml
# config/tools/sheets_update_values.yaml
name: sheets_update_values
parameters:
  - name: spreadsheet_id
    type: string
    required: true
  - name: range
    type: string
    required: true
  - name: values
    type: array
    required: true
  - name: value_input_option
    type: string
    enum: [RAW, USER_ENTERED]
    default: USER_ENTERED
```

### Append Operations

```yaml
# config/tools/sheets_append_values.yaml
name: sheets_append_values
parameters:
  - name: spreadsheet_id
    type: string
  - name: range
    type: string
  - name: values
    type: array
  - name: value_input_option
    type: string
    enum: [RAW, USER_ENTERED]
```

### Spreadsheet Creation

```yaml
# config/tools/sheets_create_spreadsheet.yaml
name: sheets_create_spreadsheet
parameters:
  - name: title
    type: string
    required: true
  - name: sheet_names
    type: array
    description: "Initial sheet names"
```

### Formula Support

```python
# Support for reading formulas vs evaluated values
result = await sheets_batch_get(
    ctx=ctx,
    spreadsheet_id="1abcXYZ...",
    ranges=["Sheet1!A1:D10"],
    value_render_option="FORMULA"  # vs "FORMATTED_VALUE"
)
```

### Formatting and Styling

```python
# Future: Include cell formatting in response
# - Font size, color, weight
# - Cell background color
# - Number format (currency, date, percentage)
# - Borders and alignment
```

## Troubleshooting

### Common Issues

**1. Empty ranges returned:**
```python
# Problem: Range doesn't exist or has no data
result = await sheets_batch_get(ranges=["NonExistentSheet!A1:Z100"])

# Solution: Check sheet names, verify data exists
spreadsheet_metadata = result["data"]["sheets"]
print([sheet["title"] for sheet in spreadsheet_metadata])
```

**2. Invalid A1 notation:**
```python
# Problem: Malformed range syntax
ranges=["Sheet1:A1:D10"]  # ❌ Wrong (colon after sheet name)
ranges=["Sheet1!A1:D10"]  # ✅ Correct

ranges=["SheetX!A1:Z"]  # ❌ Wrong (column with no row)
ranges=["SheetX!A1:Z100"]  # ✅ Correct
```

**3. Permission denied:**
```python
# Problem: Service account doesn't have access
# Solution: Share spreadsheet with service account email
# sheets-service-account@PROJECT_ID.iam.gserviceaccount.com
```

**4. Quota exceeded:**
```python
# Problem: Too many API calls
# Solution: Use batch_get to fetch multiple ranges at once
# Instead of 10 separate calls:
for range in ranges:
    result = await sheets_batch_get(ranges=[range])  # ❌ 10 API calls

# Do this:
result = await sheets_batch_get(ranges=ranges)  # ✅ 1 API call
```

## Known Limitations (Week 2)

1. **Mock-only implementation:** No real Sheets API integration yet
2. **Read-only operations:** No write, append, or format operations
3. **Basic data types:** No support for formulas, formatting, charts
4. **Single major_dimension:** Only ROWS supported (no COLUMNS layout)
5. **No named range support:** Must use A1 notation
6. **No error simulation:** Cannot test API error handling with mocks
7. **Static mock data:** Always returns same hardcoded response

## References

- [Google Sheets API v4 Documentation](https://developers.google.com/sheets/api)
- [A1 Notation Reference](https://developers.google.com/sheets/api/guides/concepts#expandable-1)
- [OAuth 2.0 Setup](https://developers.google.com/sheets/api/quickstart/python)
- [Service Account Authentication](https://cloud.google.com/docs/authentication/production)
- [API Quota Limits](https://developers.google.com/sheets/api/limits)

---

**Document Version:** 1.0  
**Last Updated:** Week 2 Night Shift  
**Status:** Mock Implementation Complete  
**Next Steps:** Real API integration (Week 3+), Write operations (Week 4+)
