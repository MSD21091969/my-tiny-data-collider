# Google Drive Tools Documentation

## Overview

The Drive toolset provides mock implementations of Google Drive file operations following the Tool Engineering Foundation pattern. This is a **Week 2 deliverable** with mock data; real Google Drive API integration is planned for **Week 4**.

## Architecture

The Drive toolset follows the established MDS tool engineering patterns:

```
config/tools/drive_tools.yaml          # Tool definitions (YAML config)
src/pydantic_ai_integration/tools/
  ├── drive_params.py                   # Parameter models (Pydantic guardrails)
  ├── drive_tools.py                    # Tool implementations
  └── mock_drive_client.py              # Mock Google Drive API client
tests/test_drive_tools.py               # 54 comprehensive test cases
```

### Design Principles

1. **Declarative Configuration**: Tools are defined in YAML with metadata and business rules
2. **Pydantic Validation**: All parameters validated using Pydantic models (guardrails)
3. **Single Registration**: `@register_mds_tool` decorator handles all registration
4. **Event Tracking**: Complete audit trail via `MDSContext.register_event()`
5. **Mock First**: Test patterns with mock data before real API integration

## Available Tools

### 1. drive_list_files

List files from Google Drive with optional filtering and sorting.

**Category**: `google_workspace`  
**Permissions Required**: `drive:read`  
**Timeout**: 30 seconds

#### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `query` | string | No | `""` | Google Drive search query (max 500 chars) |
| `max_results` | integer | No | `10` | Maximum files to return (1-100) |
| `order_by` | string | No | `"modifiedTime desc"` | Sort order |

#### Query Examples

```python
# List all files
query=""

# Filter by type
query="type:pdf"

# Filter by name
query='name contains "report"'

# Filter by date
query="modifiedTime > '2025-01-01'"
```

#### Example Usage

```python
from src.pydantic_ai_integration.dependencies import MDSContext
from src.pydantic_ai_integration.tools.drive_tools import drive_list_files

# Create context
ctx = MDSContext(
    user_id="user_123",
    session_id="ts_abc123"
)

# List PDF files
result = await drive_list_files(
    ctx,
    query="type:pdf",
    max_results=25,
    order_by="name"
)

# Response structure
{
    "files": [
        {
            "id": "file_001",
            "name": "Project Report.pdf",
            "mime_type": "application/pdf",
            "created_time": "2025-01-15T10:30:00Z",
            "modified_time": "2025-01-20T15:45:00Z",
            "size": 245760,
            "parents": ["root"]
        }
    ],
    "total_count": 1,
    "next_page_token": null,
    "query": "type:pdf",
    "event_id": "evt_123",
    "timestamp": "2025-01-22T14:30:00Z"
}
```

### 2. drive_get_file

Get metadata and optionally content of a specific file.

**Category**: `google_workspace`  
**Permissions Required**: `drive:read`  
**Timeout**: 60 seconds

#### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `file_id` | string | Yes | - | Google Drive file ID (alphanumeric, dash, underscore only) |
| `include_content` | boolean | No | `false` | Whether to include file content |

#### Example Usage

```python
# Get file metadata only
result = await drive_get_file(
    ctx,
    file_id="file_001"
)

# Get file with content
result = await drive_get_file(
    ctx,
    file_id="file_001",
    include_content=True
)

# Response structure
{
    "file": {
        "id": "file_001",
        "name": "Project Report.pdf",
        "mime_type": "application/pdf",
        "created_time": "2025-01-15T10:30:00Z",
        "modified_time": "2025-01-20T15:45:00Z",
        "size": 245760,
        "parents": ["root"],
        "content": "Mock PDF content..."  # Only if include_content=True
    },
    "event_id": "evt_124",
    "timestamp": "2025-01-22T14:31:00Z"
}
```

### 3. drive_upload_file

Upload a file to Google Drive.

**Category**: `google_workspace`  
**Permissions Required**: `drive:write`  
**Timeout**: 120 seconds

#### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `file_name` | string | Yes | - | Name for the file (1-255 chars) |
| `content` | string | Yes | - | File content (base64 for binary) |
| `mime_type` | string | No | `"application/octet-stream"` | MIME type |
| `parent_folder_id` | string | No | `null` | Parent folder ID (optional) |

#### Example Usage

```python
import base64

# Upload text file
result = await drive_upload_file(
    ctx,
    file_name="document.txt",
    content="Hello World",
    mime_type="text/plain"
)

# Upload binary file (base64 encoded)
with open("report.pdf", "rb") as f:
    content_b64 = base64.b64encode(f.read()).decode()

result = await drive_upload_file(
    ctx,
    file_name="report.pdf",
    content=content_b64,
    mime_type="application/pdf",
    parent_folder_id="folder_abc123"
)

# Response structure
{
    "file": {
        "id": "file_new123",
        "name": "document.txt",
        "mime_type": "text/plain",
        "created_time": "2025-01-22T14:32:00Z",
        "modified_time": "2025-01-22T14:32:00Z",
        "size": 11,
        "parents": ["root"]
    },
    "event_id": "evt_125",
    "timestamp": "2025-01-22T14:32:00Z"
}
```

### 4. drive_create_folder

Create a new folder in Google Drive.

**Category**: `google_workspace`  
**Permissions Required**: `drive:write`  
**Timeout**: 30 seconds

#### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `folder_name` | string | Yes | - | Name for the folder (1-255 chars) |
| `parent_folder_id` | string | No | `null` | Parent folder ID (optional) |

#### Example Usage

```python
# Create folder in root
result = await drive_create_folder(
    ctx,
    folder_name="Project Files"
)

# Create nested folder
result = await drive_create_folder(
    ctx,
    folder_name="2025 Reports",
    parent_folder_id="folder_abc123"
)

# Response structure
{
    "folder": {
        "id": "folder_new123",
        "name": "Project Files",
        "mime_type": "application/vnd.google-apps.folder",
        "created_time": "2025-01-22T14:33:00Z",
        "modified_time": "2025-01-22T14:33:00Z",
        "size": 0,
        "parents": ["root"]
    },
    "event_id": "evt_126",
    "timestamp": "2025-01-22T14:33:00Z"
}
```

### 5. drive_share_file

Share a file with specific users or generate a shareable link.

**Category**: `google_workspace`  
**Permissions Required**: `drive:write`, `drive:share`  
**Timeout**: 30 seconds

#### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `file_id` | string | Yes | - | File ID to share |
| `email` | string | No | `null` | Email address to share with |
| `role` | string | No | `"reader"` | Permission role (`reader`, `writer`, `commenter`, `owner`) |
| `generate_link` | boolean | No | `false` | Generate a shareable link |

#### Example Usage

```python
# Share with specific user
result = await drive_share_file(
    ctx,
    file_id="file_001",
    email="colleague@example.com",
    role="writer"
)

# Generate shareable link
result = await drive_share_file(
    ctx,
    file_id="file_001",
    generate_link=True
)

# Share with user AND generate link
result = await drive_share_file(
    ctx,
    file_id="file_001",
    email="user@example.com",
    role="reader",
    generate_link=True
)

# Response structure
{
    "permission": {
        "id": "perm_abc123",
        "type": "user",
        "role": "writer",
        "email_address": "colleague@example.com"
    },
    "file_id": "file_001",
    "link": "https://drive.google.com/file/d/file_001/view",  # Only if generate_link=True
    "event_id": "evt_127",
    "timestamp": "2025-01-22T14:34:00Z"
}
```

## Parameter Validation (Guardrails)

All parameters are validated using Pydantic models before tool execution. This ensures:

### String Constraints
- **Length limits**: `min_length`, `max_length`
- **Pattern matching**: Regex validation for IDs, emails
- **Empty strings**: Allowed only when explicitly permitted

### Numeric Constraints
- **Range limits**: `ge` (>=), `le` (<=) for min/max values
- **Integer types**: Automatic type coercion and validation

### Enum Constraints
- **Literal values**: `role` must be one of: `reader`, `writer`, `commenter`, `owner`
- **Type safety**: Enforced at compile time and runtime

### Example Validation Errors

```python
# Query too long (max 500 chars)
DriveListFilesParams(query="x" * 501)
# ValidationError: String should have at most 500 characters

# Invalid file_id format
DriveGetFileParams(file_id="file@123")
# ValidationError: file_id must contain only alphanumeric characters, dashes, and underscores

# Invalid role
DriveShareFileParams(file_id="file_001", role="admin")
# ValidationError: Input should be 'reader', 'writer', 'commenter' or 'owner'

# Invalid email
DriveShareFileParams(file_id="file_001", email="not-an-email")
# ValidationError: Invalid email format
```

## Event Tracking

All Drive tools automatically track events in the MDSContext for audit trail:

```python
# After tool execution
ctx.tool_events[-1]
{
    "event_type": "drive_list_files",
    "timestamp": "2025-01-22T14:30:00Z",
    "parameters": {"query": "type:pdf", "max_results": 10},
    "result_summary": {"status": "success", "file_count": 3},
    "status": "success",
    "duration_ms": 150
}
```

### Event Fields
- `event_type`: Tool name
- `timestamp`: ISO 8601 timestamp
- `parameters`: Input parameters (sanitized)
- `result_summary`: High-level result info
- `status`: `success` or `error`
- `duration_ms`: Execution time

## Testing

The Drive toolset includes 54 comprehensive test cases:

### Test Categories

#### 1. Parameter Validation Tests (21 tests)
- Valid parameter combinations
- Default values
- Constraint enforcement (length, range, pattern)
- Required vs optional fields
- Edge cases and boundaries

#### 2. Mock Client Tests (14 tests)
- Client initialization
- List operations with filtering and sorting
- Get operations with/without content
- Upload operations
- Folder creation
- Sharing operations
- Error handling
- Singleton pattern

#### 3. Tool Execution Tests (15 tests)
- Basic tool execution
- Parameter variations
- Event tracking validation
- Error handling
- Correlation ID tracking

#### 4. Edge Cases (4 tests)
- Empty values
- Maximum values
- Optional parameters
- Boundary conditions

### Running Tests

```bash
# Run all Drive tool tests
pytest tests/test_drive_tools.py -v

# Run only unit tests
pytest tests/test_drive_tools.py -m unit -v

# Run only integration tests
pytest tests/test_drive_tools.py -m integration -v

# Run with coverage
pytest tests/test_drive_tools.py --cov=src/pydantic_ai_integration/tools/drive_tools -v
```

### Test Markers

- `@pytest.mark.unit`: Fast unit tests (parameter validation, mock client)
- `@pytest.mark.integration`: Integration tests (tool execution with mock backend)
- `@pytest.mark.mock`: Tests using mock implementations

## Mock Data

The mock Drive client returns realistic data structures:

### Sample Files

The mock client initializes with 3 sample files:

1. **Project Report.pdf** (PDF, 245 KB)
2. **Meeting Notes.docx** (Word, 15 KB)
3. **Budget.xlsx** (Excel, 51 KB)

### Mock Behavior

- **File IDs**: Generated with prefix `file_` + random alphanumeric
- **Folder IDs**: Same format as file IDs
- **Permission IDs**: Generated with prefix `perm_` + random alphanumeric
- **Timestamps**: Current time in ISO 8601 format
- **Content**: Mock text based on file type

## Integration with Casefiles

While casefile storage is logged in Week 2, full integration is planned for Week 3:

```python
# Tools log casefile intent
if ctx.casefile_id:
    logger.info(f"Storing {len(result['files'])} files in casefile {ctx.casefile_id}")
```

### Resource Types

Drive tools will store resources as:
- `drive_files`: File metadata
- `drive_folders`: Folder metadata
- `drive_permissions`: Sharing permissions

### Future Casefile Schema

```python
casefile.drive_data = CasefileDriveData(
    files=[
        DriveFileSchema(
            id="file_001",
            name="Report.docx",
            mime_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            parents=["folder_123"],
            created_time="2025-01-15T10:30:00Z",
            modified_time="2025-01-20T15:45:00Z",
            size=245760
        )
    ]
)
```

## Future Enhancements (Week 4)

### Real Google Drive API Integration

1. **OAuth2 Authentication**
   - Replace mock client with `google-api-python-client`
   - Implement OAuth2 credential management
   - Handle token refresh

2. **API Client Wrapper**
   ```python
   class GoogleDriveClient:
       def __init__(self, credentials):
           self.service = build('drive', 'v3', credentials=credentials)
       
       def list_files(self, query, max_results, order_by):
           results = self.service.files().list(
               q=query,
               pageSize=max_results,
               orderBy=order_by,
               fields='files(id, name, mimeType, createdTime, modifiedTime, size, parents)'
           ).execute()
           return results
   ```

3. **Error Handling**
   - Rate limit handling (exponential backoff)
   - API error codes (404, 403, 500, etc.)
   - Quota management
   - Network retry logic

4. **Advanced Features**
   - Real file uploads/downloads
   - Binary content handling
   - Large file streaming
   - Batch operations
   - Change notifications (webhooks)

## API Reference

### Tool Registration

All Drive tools are registered via `@register_mds_tool` decorator:

```python
@register_mds_tool(
    name="drive_list_files",
    display_name="List Drive Files",
    description="List files from Google Drive with optional filtering",
    category="google_workspace",
    version="1.0.0",
    tags=["drive", "files", "list", "google_workspace"],
    enabled=True,
    requires_auth=True,
    required_permissions=["drive:read"],
    requires_casefile=False,
    timeout_seconds=30,
    params_model=DriveListFilesParams,
)
async def drive_list_files(ctx: MDSContext, ...) -> Dict[str, Any]:
    ...
```

### Registry Access

Tools are stored in the global `MANAGED_TOOLS` registry:

```python
from src.pydantic_ai_integration.tool_decorator import MANAGED_TOOLS

# Get tool definition
tool_def = MANAGED_TOOLS["drive_list_files"]

# List all Drive tools
drive_tools = {
    name: tool for name, tool in MANAGED_TOOLS.items()
    if tool.metadata.category == "google_workspace"
}
```

## Best Practices

### 1. Always Use MDSContext

```python
# ✅ Good: Pass context to tools
ctx = MDSContext(user_id="user_123", session_id="ts_abc123")
result = await drive_list_files(ctx, query="type:pdf")

# ❌ Bad: Don't call tools without context
result = await drive_list_files(None, query="type:pdf")  # Will fail
```

### 2. Handle Errors Gracefully

```python
try:
    result = await drive_get_file(ctx, file_id="nonexistent")
except ValueError as e:
    print(f"File not found: {e}")
    # Handle error appropriately
```

### 3. Validate Parameters Early

```python
# Let Pydantic validate parameters
try:
    params = DriveListFilesParams(
        query="type:pdf",
        max_results=150  # Invalid: exceeds 100
    )
except ValidationError as e:
    print(f"Invalid parameters: {e}")
```

### 4. Check Event Status

```python
result = await drive_list_files(ctx, query="type:pdf")

# Check if operation succeeded
last_event = ctx.tool_events[-1]
if last_event.status == "success":
    print(f"Found {len(result['files'])} files")
else:
    print(f"Error: {last_event.result_summary}")
```

## Support and Troubleshooting

### Common Issues

**Issue**: `ValidationError` on file_id parameter  
**Solution**: Ensure file_id contains only alphanumeric characters, dashes, and underscores

**Issue**: `ValueError: File not found`  
**Solution**: Check that file_id exists in mock storage or wait for Week 4 real API

**Issue**: Tests fail with import errors  
**Solution**: Ensure pytest and dependencies are installed: `pip install -r requirements.txt`

### Debug Mode

Enable detailed logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Tools will log operations
result = await drive_list_files(ctx, query="type:pdf")
# DEBUG: Listing files with query: type:pdf
# DEBUG: Found 1 files
```

## Contributing

When adding new Drive tools:

1. Update `config/tools/drive_tools.yaml`
2. Add parameter model in `drive_params.py`
3. Implement tool in `drive_tools.py` using `@register_mds_tool`
4. Update mock client if needed
5. Add 5-10 test cases per tool
6. Update this documentation

## Related Documentation

- [TOOLENGINEERING_FOUNDATION.md](./TOOLENGINEERING_FOUNDATION.md) - Overall tool engineering strategy
- [unified_example_tools.py](../src/pydantic_ai_integration/tools/unified_example_tools.py) - Reference implementation
- [tool_params.py](../src/pydantic_ai_integration/tools/tool_params.py) - Parameter model examples

## Version History

- **v1.0.0** (Week 2): Initial mock implementation with 5 tools and 54 tests
- **v2.0.0** (Week 4, planned): Real Google Drive API integration
