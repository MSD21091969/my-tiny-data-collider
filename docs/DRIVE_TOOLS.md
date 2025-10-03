# Google Drive Tools

## Overview

Google Drive toolset provides file management and storage capabilities through the Google Workspace API integration. All tools follow the N-tier layered architecture with policy enforcement at the service layer.

**Status**: Week 2 MVP - Mock implementations with full Pydantic models  
**Branch**: `feature/google-workspace-drive`  
**Real API Integration**: TODO (Week 3+)

## Architecture

### Layered Structure

```
API Layer → Service Layer (policy enforcement) → Tool Layer → DriveClient → Request/Response DTOs → Canonical Models
```

**Key Points**:
- Service layer is PRIMARY policy enforcement point
- Tool layer contains business logic only (NO policy checks)
- `DriveClient` returns full Pydantic DTOs for type safety
- Mock mode enabled by default (Week 2 focus)

## Available Tools

### 1. `drive_list_files`

**Purpose**: List files in user's Google Drive with optional filtering and pagination

**YAML Source**: `config/tools/drive_list_files.yaml`  
**Generated Tool**: `src/pydantic_ai_integration/tools/generated/drive_list_files.py`  
**Generated Tests**: `tests/generated/test_drive_list_files.py`

**Parameters**:
- `page_size` (int, optional): Maximum files per page (default: 25, range: 1-1000)
- `query` (str, optional): Drive query string using [Drive API query syntax](https://developers.google.com/drive/api/guides/search-files)
  - Examples: `"name contains 'report'"`, `"mimeType = 'application/pdf'"`, `"trashed = false"`
- `order_by` (str, optional): Sort order (e.g., `"modifiedTime desc"`, `"name"`, `"createdTime"`)
- `page_token` (str, optional): Pagination token from previous response

**Returns**: `DriveListFilesResponse` with:
- `files`: List of `DriveFile` Pydantic models (full file metadata)
- `next_page_token`: Token for next page (optional)

**Policies** (from YAML):
- Requires active session
- Requires `drive.readonly` permission
- Session timeout: 30 seconds
- Logs request payload, not full response (large file lists)

**Example Usage**:
```python
from src.pydantic_ai_integration.dependencies import MDSContext
from src.pydantic_ai_integration.tools.generated.drive_list_files import drive_list_files

ctx = MDSContext(user_id="user123", session_id="sess456", casefile_id="case789")
result = await drive_list_files(
    ctx,
    page_size=50,
    query="mimeType = 'application/pdf' and trashed = false",
    order_by="modifiedTime desc"
)
# result contains DriveListFilesResponse with full DriveFile models
for file in result["files"]:
    print(f"{file.name}: {file.web_view_link}")
```

**Mock Behavior**:
- Returns 2 hardcoded files (Document + PDF)
- Ignores `query`, `order_by`, `page_token` (Week 2 limitation)
- `next_page_token` always `None`
- File IDs: `"mock-file-1"`, `"mock-file-2"`
- Simulates API latency (timing not specified in client)

**Drive File Model**:
```python
class DriveFile(BaseModel):
    id: str                    # Unique file ID
    name: str                  # File name
    mime_type: str             # MIME type (e.g., 'application/pdf')
    owners: List[DriveOwner]   # File owners with email/display name
    parents: List[str]         # Parent folder IDs
    web_view_link: str         # URL to view file in Drive UI
    size_bytes: int            # File size in bytes
    trashed: bool              # Whether file is in trash
    created_time: str          # ISO 8601 timestamp
    modified_time: str         # ISO 8601 timestamp
```

---

## Testing Strategy

### Unit Tests (`tests/generated/test_drive_list_files.py`)

**Test Results** (Week 2):
```
✅ 6/7 tests passing (85.7% success rate)
❌ 1 test failing (mock response structure mismatch)
```

**Passing Tests**:
- Parameter validation (`page_size` min/max constraints: 1-1000)
- Query max length validation (4096 chars)
- Default parameter values
- MDSContext propagation
- Audit event registration
- Error scenario (invalid `page_size`)

**Failing Test**:
- `test_list_recent_files_in_drive_root`: Expects simplified dict `{"files": [...]}`, gets full Pydantic response

**Expected vs. Actual**:
```python
# Test expectation (from YAML example):
{
    "files": [
        {"id": "mock-file-1", "name": "Important Document"}
    ]
}

# Actual mock response (from DriveClient):
DriveListFilesResponse(
    files=[
        DriveFile(
            id="mock-file-1",
            name="Important Document",
            mime_type="application/vnd.google-apps.document",
            owners=[DriveOwner(...)],
            parents=["root"],
            web_view_link="https://drive.google.com/mock-file-1",
            size_bytes=1024,
            trashed=False,
            created_time="2025-10-03T...",
            modified_time="2025-10-03T..."
        ),
        DriveFile(id="mock-file-2", name="Quarterly Report", ...)
    ],
    next_page_token=None
)
```

**Fix Approach** (Week 3):
- Option A: Update test expectations to validate Pydantic models
- Option B: Add `.model_dump()` serialization in tool implementation
- Option C: Update YAML examples to match full model structure

### Integration Tests (TODO Week 3)

**Planned Tests**:
- Service layer policy enforcement (page_size limits, permissions)
- Audit trail creation (Firestore writes)
- Error handling (quota exceeded, invalid query syntax)
- Casefile logging when `log_to_casefile: true`

**Example Integration Test**:
```python
async def test_drive_list_with_invalid_query():
    """Test that invalid Drive query syntax returns proper error."""
    response = await tool_session_service.execute_tool(
        tool_name="drive_list_files",
        params={"query": "invalid syntax here"},
        context={"user_id": "test_user", "session_id": "test_session"}
    )
    assert response.status == "error"
    assert "query syntax" in response.error_message.lower()
```

### API Tests (TODO Week 3)

**Planned Tests**:
- End-to-end HTTP with JWT authentication
- Test `RequestEnvelope` → JSON response flow
- HTTP status codes (401, 403, 429, 500)
- Pagination handling (follow `next_page_token`)

---

## Mock Data Patterns

### Mock Client (`DriveClient` in `clients.py`)

```python
class DriveClient:
    def __init__(self, user_id: str, *, use_mock: Optional[bool] = None):
        config = get_config()
        self.user_id = user_id
        self._use_mock = config.get("enable_mock_drive", True) if use_mock is None else use_mock
    
    async def list_files(
        self,
        request: Optional[DriveListFilesRequest] = None,
        **kwargs
    ) -> DriveListFilesResponse:
        req = request or DriveListFilesRequest(**kwargs)
        
        if self._use_mock:
            logger.debug("Returning mock Drive files for user %s", self.user_id)
            now_iso = datetime.now().isoformat()
            mock_files = [
                DriveFile(
                    id="mock-file-1",
                    name="Important Document",
                    mime_type="application/vnd.google-apps.document",
                    owners=[DriveOwner(display_name="Mock Owner", email=f"{self.user_id}@example.com")],
                    parents=["root"],
                    web_view_link="https://drive.google.com/mock-file-1",
                    size_bytes=1024,
                    trashed=False,
                    created_time=now_iso,
                    modified_time=now_iso
                ),
                # ... more mock files
            ]
            return DriveListFilesResponse(files=mock_files, next_page_token=None)
        
        raise NotImplementedError("Real Drive API integration not yet implemented")
```

### Mock Response Example

```json
{
  "files": [
    {
      "id": "mock-file-1",
      "name": "Important Document",
      "mime_type": "application/vnd.google-apps.document",
      "owners": [
        {
          "display_name": "Mock Owner",
          "email": "test_user@example.com"
        }
      ],
      "parents": ["root"],
      "web_view_link": "https://drive.google.com/mock-file-1",
      "size_bytes": 1024,
      "trashed": false,
      "created_time": "2025-10-03T02:00:00.000000",
      "modified_time": "2025-10-03T02:00:00.000000"
    },
    {
      "id": "mock-file-2",
      "name": "Quarterly Report",
      "mime_type": "application/pdf",
      "owners": [...],
      "parents": ["root"],
      "web_view_link": "https://drive.google.com/mock-file-2",
      "size_bytes": 2048,
      "trashed": false,
      "created_time": "2025-10-03T02:00:00.000000",
      "modified_time": "2025-10-03T02:00:00.000000"
    }
  ],
  "next_page_token": null
}
```

---

## Real API Integration (TODO)

### Prerequisites

1. **Enable Drive API** in Google Cloud Console
2. **Configure OAuth 2.0** credentials (same as Gmail)
3. **Store refresh tokens** in Firestore per user
4. **Implement token refresh** in `DriveClient.__init__()`

### Environment Variables

```bash
GOOGLE_CLIENT_ID=your_client_id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your_client_secret
GOOGLE_REDIRECT_URI=https://your-domain.com/auth/callback
DRIVE_API_SCOPES=https://www.googleapis.com/auth/drive.readonly,https://www.googleapis.com/auth/drive.file
```

### Real Implementation Example

```python
async def list_files(self, request: DriveListFilesRequest) -> DriveListFilesResponse:
    if self._use_mock:
        # ... existing mock implementation
        return DriveListFilesResponse(...)
    
    # Real Drive API call
    try:
        # Build query with proper escaping
        query_parts = []
        if request.query:
            query_parts.append(request.query)
        query_parts.append("trashed = false")  # Always exclude trashed
        
        results = self.service.files().list(
            pageSize=request.page_size,
            q=" and ".join(query_parts),
            fields="nextPageToken, files(id, name, mimeType, owners, parents, webViewLink, size, trashed, createdTime, modifiedTime)",
            orderBy=request.order_by or None,
            pageToken=request.page_token or None
        ).execute()
        
        files = []
        for item in results.get('files', []):
            files.append(DriveFile(
                id=item['id'],
                name=item['name'],
                mime_type=item.get('mimeType', 'application/octet-stream'),
                owners=[
                    DriveOwner(
                        display_name=owner.get('displayName', ''),
                        email=owner.get('emailAddress', '')
                    ) for owner in item.get('owners', [])
                ],
                parents=item.get('parents', []),
                web_view_link=item.get('webViewLink', ''),
                size_bytes=int(item.get('size', 0)),
                trashed=item.get('trashed', False),
                created_time=item.get('createdTime'),
                modified_time=item.get('modifiedTime')
            ))
        
        return DriveListFilesResponse(
            files=files,
            next_page_token=results.get('nextPageToken')
        )
    except Exception as e:
        logger.error(f"Drive API error: {e}")
        raise
```

### Drive API Quotas

- **Queries per day**: 1,000,000,000 (1 billion)
- **Queries per 100 seconds per user**: 1,000
- **Queries per 100 seconds**: 10,000

**Rate Limiting Strategy**:
- Implement exponential backoff for `429 Too Many Requests`
- Cache file lists in Firestore with 5-minute TTL
- Use `fields` parameter to minimize response size
- Batch operations when possible

---

## Drive Query Syntax Reference

### Common Query Examples

```python
# Files by name
"name = 'Report.pdf'"
"name contains 'invoice'"

# Files by MIME type
"mimeType = 'application/pdf'"
"mimeType = 'application/vnd.google-apps.folder'"
"mimeType = 'image/jpeg'"

# Files by owner
"'owner@example.com' in owners"

# Files in specific folder
"'folder_id_here' in parents"

# Files modified after date
"modifiedTime > '2025-01-01T00:00:00'"

# Combine with AND/OR
"name contains 'report' and mimeType = 'application/pdf' and trashed = false"

# NOT operator
"not mimeType = 'application/vnd.google-apps.folder'"
```

### Full Documentation
[Google Drive API Search Query Terms](https://developers.google.com/drive/api/guides/search-files)

---

## Known Limitations (Week 2)

### Mock Implementation Constraints

1. **No Real API Calls**: All responses hardcoded in `DriveClient`
2. **No Query Filtering**: Mock ignores `query`, `order_by`, `page_token`
3. **No Pagination**: `next_page_token` always `None`
4. **Fixed Response**: Always returns same 2 files
5. **No File Operations**: Upload/download/delete not implemented
6. **No Folder Navigation**: Parent/child relationships not traversable

### Test Coverage Gaps

1. **Integration Tests**: Not implemented (service layer policy enforcement)
2. **API Tests**: No end-to-end HTTP tests
3. **Error Scenarios**: Mock doesn't raise exceptions for invalid queries
4. **Pagination Tests**: No multi-page result handling

### Planned Features (Week 3+)

1. **File Upload**: `drive_upload_file` tool
2. **File Download**: `drive_download_file` tool
3. **File Delete/Trash**: `drive_delete_file`, `drive_trash_file` tools
4. **Folder Management**: `drive_create_folder`, `drive_list_folder_contents` tools
5. **File Sharing**: `drive_share_file`, `drive_update_permissions` tools
6. **File Metadata**: `drive_get_file`, `drive_update_file_metadata` tools

---

## Development Workflow

### Adding New Drive Tools

1. **Create YAML** in `config/tools/`:
```yaml
name: drive_upload_file
description: "Upload a file to Google Drive"
category: google_workspace
parameters:
  - name: file_name
    type: string
    required: true
  - name: file_content
    type: string  # Base64 encoded
    required: true
  - name: parent_folder_id
    type: string
    required: false
    default: "root"
implementation:
  type: api_call
  api_call:
    client_module: src.pydantic_ai_integration.google_workspace
    client_class: DriveClient
    method_name: upload_file
    request_type: DriveUploadFileRequest
```

2. **Add client method** in `clients.py`:
```python
async def upload_file(self, request: DriveUploadFileRequest) -> DriveUploadFileResponse:
    if self._use_mock:
        return DriveUploadFileResponse(
            file_id="mock-upload-123",
            web_view_link="https://drive.google.com/mock-upload-123"
        )
    # Real implementation here
```

3. **Add DTOs** in `models.py`:
```python
class DriveUploadFileRequest(BaseModel):
    file_name: str
    file_content: str
    parent_folder_id: str = "root"

class DriveUploadFileResponse(BaseModel):
    file_id: str
    web_view_link: str
```

4. **Generate tool**:
```powershell
python -c "from src.pydantic_ai_integration.tools.factory import ToolFactory; factory = ToolFactory(); factory.process_tool(factory.config_dir / 'drive_upload_file.yaml')"
```

5. **Run tests**:
```powershell
python -m pytest tests/generated/test_drive_upload_file.py -v
```

---

## Related Documentation

- **[Gmail Tools](GMAIL_TOOLS.md)**: Gmail toolset reference (similar patterns)
- **[Policy and User ID Flow](POLICY_AND_USER_ID_FLOW.md)**: Policy enforcement architecture
- **[Layered Architecture Flow](LAYERED_ARCHITECTURE_FLOW.md)**: N-tier structure
- **[Tool Engineering Foundation](TOOLENGINEERING_FOUNDATION.md)**: YAML-driven generation

---

## Week 2 Completion Status

### ✅ Completed

- Drive YAML tool definition (`drive_list_files.yaml`)
- `DriveClient` mock implementation in `clients.py`
- Request/Response DTOs in `google_workspace/models.py`
- Canonical `DriveFile` model in `workspace.py`
- Tool Factory generation with API call integration
- Generated unit tests (6/7 passing, 85.7% coverage)
- Documentation (`docs/DRIVE_TOOLS.md`)

### ⚠️ Known Issues

- 1 unit test failing (mock response structure mismatch)
- Integration tests not implemented
- API tests not implemented
- Mock doesn't support query filtering or pagination

### 📋 Week 3 Priorities

1. Fix unit test expectations (align with Pydantic response models)
2. Add integration tests (policy enforcement, audit trails)
3. Add API tests (end-to-end HTTP with JWT)
4. Implement real Drive API OAuth flow
5. Add file upload/download/delete tools
6. Add folder management tools
7. Error handling (invalid queries, quota exceeded)

---

## Support & Troubleshooting

### Common Issues

**Issue**: Test expects `{"files": [...]}`, got `DriveListFilesResponse(...)`  
**Fix**: Same as Gmail - update test expectations or add `.model_dump()` (Week 3)

**Issue**: Mock ignores query parameter  
**Fix**: Expected for Week 2 - real filtering comes with real API integration

**Issue**: `page_size` validation error with value 2000  
**Fix**: Working as designed - max is 1000 per Drive API limits

---

**Last Updated**: October 3, 2025  
**Contributors**: GitHub Copilot (night-shift automation)  
**Status**: Week 2 Complete, Ready for PR Review
