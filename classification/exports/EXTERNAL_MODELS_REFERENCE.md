# External Models Reference Guide

**Generated:** October 11, 2025  
**Purpose:** Maps your custom Pydantic models to official Google Workspace API documentation

---

## Overview: Your Models vs Google's API Models

Your models in `src/pydantic_models/workspace/` are **CUSTOM implementations** that wrap and simplify Google's official API responses. They are designed to:

1. **Store data in your casefiles** (persistent storage)
2. **Provide clean, typed Python interfaces**
3. **Add helper methods** (like `upsert_messages`, `unread_count`)
4. **Match your application's needs**

They are **NOT** direct imports from Google's libraries - they're **YOUR models** that structure Google's data for your use case.

---

## Gmail Models

**File:** `src/pydantic_models/workspace/gmail.py`

### GmailMessage

**Official Google Reference:** https://developers.google.com/gmail/api/reference/rest/v1/users.messages#Message

| Your Field | Google API Field | Notes |
|------------|------------------|-------|
| `id` | `id` | Direct mapping |
| `thread_id` | `threadId` | Direct mapping |
| `subject` | `payload.headers` | Extracted from headers |
| `sender` | `payload.headers` | From "From" header |
| `to_recipients` | `payload.headers` | From "To" header (parsed) |
| `cc_recipients` | `payload.headers` | From "Cc" header (parsed) |
| `bcc_recipients` | `payload.headers` | From "Bcc" header (parsed) |
| `snippet` | `snippet` | Direct mapping |
| `internal_date` | `internalDate` | Converted to ISO 8601 |
| `labels` | `labelIds` | Direct mapping |
| `has_attachments` | *(computed)* | Your computed field |
| `attachments` | `payload.parts` | Extracted & simplified |
| `body_text` | `payload.body` | Extracted from parts |
| `body_html` | `payload.body` | Extracted from parts |
| `fetched_at` | *(your addition)* | Not in Google API |

### GmailAttachment

**Official Google Reference:** https://developers.google.com/gmail/api/reference/rest/v1/users.messages#MessagePart

| Your Field | Google API Field | Notes |
|------------|------------------|-------|
| `filename` | `filename` | Direct mapping |
| `mime_type` | `mimeType` | Direct mapping |
| `size_bytes` | `body.size` | Direct mapping |
| `attachment_id` | `body.attachmentId` | Direct mapping |

### GmailThread

**Official Google Reference:** https://developers.google.com/gmail/api/reference/rest/v1/users.threads#Thread

| Your Field | Google API Field | Notes |
|------------|------------------|-------|
| `id` | `id` | Direct mapping |
| `message_ids` | `messages[].id` | Extracted from messages |
| `snippet` | `snippet` | Direct mapping |
| `history_id` | `historyId` | Direct mapping |
| `updated_at` | *(your addition)* | Tracking field |

### GmailLabel

**Official Google Reference:** https://developers.google.com/gmail/api/reference/rest/v1/users.labels#Label

| Your Field | Google API Field | Notes |
|------------|------------------|-------|
| `id` | `id` | Direct mapping |
| `name` | `name` | Direct mapping |
| `label_type` | `type` | Direct mapping |
| `message_visibility` | `messageListVisibility` | Direct mapping |

### CasefileGmailData

**This is YOUR CUSTOM container** - not in Google's API

- **Purpose:** Stores Gmail data within your casefile system
- **Adds:** sync tracking, `unread_count` computation, upsert methods

---

## Google Drive Models

**File:** `src/pydantic_models/workspace/drive.py`

### DriveFile

**Official Google Reference:** https://developers.google.com/drive/api/reference/rest/v3/files#File

| Your Field | Google API Field | Notes |
|------------|------------------|-------|
| `id` | `id` | Direct mapping |
| `name` | `name` | Direct mapping |
| `mime_type` | `mimeType` | Direct mapping |
| `size_bytes` | `size` | Direct mapping |
| `web_view_link` | `webViewLink` | Direct mapping |
| `icon_link` | `iconLink` | Direct mapping |
| `parents` | `parents` | Direct mapping |
| `owners` | `owners` | Simplified structure |
| `created_time` | `createdTime` | Direct mapping |
| `modified_time` | `modifiedTime` | Direct mapping |
| `trashed` | `trashed` | Direct mapping |

### DriveOwner

**Official Google Reference:** https://developers.google.com/drive/api/reference/rest/v3/files#File.Owner

| Your Field | Google API Field | Notes |
|------------|------------------|-------|
| `email` | `emailAddress` | Direct mapping |
| `display_name` | `displayName` | Direct mapping |

### DriveFolder

**Official Google Reference:** https://developers.google.com/drive/api/reference/rest/v3/files#File

*Note: Folders are files with `mimeType='application/vnd.google-apps.folder'`*

This is your simplified view of folder-type files.

### CasefileDriveData

**This is YOUR CUSTOM container** - not in Google's API

- **Purpose:** Stores Drive data within your casefile system
- **Adds:** sync tracking, upsert methods for files/folders

---

## Google Sheets Models

**File:** `src/pydantic_models/workspace/sheets.py`

### SheetRange

**Official Google Reference:** https://developers.google.com/sheets/api/reference/rest/v4/spreadsheets.values#ValueRange

| Your Field | Google API Field | Notes |
|------------|------------------|-------|
| `range` | `range` | Direct mapping (A1 notation) |
| `values` | `values` | Direct mapping (2D array) |
| `major_dimension` | `majorDimension` | Direct mapping |

### SheetMetadata

**Official Google Reference:** https://developers.google.com/sheets/api/reference/rest/v4/spreadsheets#Sheet

| Your Field | Google API Field | Notes |
|------------|------------------|-------|
| `sheet_id` | `properties.sheetId` | Direct mapping |
| `title` | `properties.title` | Direct mapping |
| `index` | `properties.index` | Direct mapping |
| `grid_properties` | `properties.gridProperties` | Direct mapping |

### SheetData

**Official Google Reference:** https://developers.google.com/sheets/api/reference/rest/v4/spreadsheets#Spreadsheet

| Your Field | Google API Field | Notes |
|------------|------------------|-------|
| `spreadsheet_id` | `spreadsheetId` | Direct mapping |
| `title` | `properties.title` | Direct mapping |
| `metadata` | `sheets[].properties` | Simplified |
| `ranges` | *(from values API)* | Separate API call results |
| `updated_at` | *(your addition)* | Tracking field |

### CasefileSheetsData

**This is YOUR CUSTOM container** - not in Google's API

- **Purpose:** Stores Sheets data within your casefile system
- **Adds:** sync tracking, multiple spreadsheet management, upsert methods

---

## Official Google API Documentation

### Gmail API Reference
- **Main Page:** https://developers.google.com/gmail/api/reference/rest
- **Key Endpoints:**
  - `users.messages.list`: https://developers.google.com/gmail/api/reference/rest/v1/users.messages/list
  - `users.messages.get`: https://developers.google.com/gmail/api/reference/rest/v1/users.messages/get
  - `users.threads.list`: https://developers.google.com/gmail/api/reference/rest/v1/users.threads/list
  - `users.labels.list`: https://developers.google.com/gmail/api/reference/rest/v1/users.labels/list

### Google Drive API Reference
- **Main Page:** https://developers.google.com/drive/api/reference/rest/v3
- **Key Endpoints:**
  - `files.list`: https://developers.google.com/drive/api/reference/rest/v3/files/list
  - `files.get`: https://developers.google.com/drive/api/reference/rest/v3/files/get

### Google Sheets API Reference
- **Main Page:** https://developers.google.com/sheets/api/reference/rest
- **Key Endpoints:**
  - `spreadsheets.get`: https://developers.google.com/sheets/api/reference/rest/v4/spreadsheets/get
  - `spreadsheets.values.get`: https://developers.google.com/sheets/api/reference/rest/v4/spreadsheets.values/get
  - `spreadsheets.values.batchGet`: https://developers.google.com/sheets/api/reference/rest/v4/spreadsheets.values/batchGet

---

## Python Client Libraries

Your code likely uses Google's official Python libraries:

### Installation
```bash
pip install google-api-python-client
```

### Gmail Example
```python
from googleapiclient.discovery import build

service = build('gmail', 'v1', credentials=creds)
messages = service.users().messages().list(userId='me').execute()
# Convert to your GmailMessage models
```

### Drive Example
```python
from googleapiclient.discovery import build

service = build('drive', 'v3', credentials=creds)
files = service.files().list().execute()
# Convert to your DriveFile models
```

### Sheets Example
```python
from googleapiclient.discovery import build

service = build('sheets', 'v4', credentials=creds)
result = service.spreadsheets().values().get(
    spreadsheetId=id, range='Sheet1!A1:D10'
).execute()
# Convert to your SheetRange models
```

**Documentation:** https://github.com/googleapis/google-api-python-client

---

## Where Your Models Add Value

Your custom Pydantic models provide benefits over using Google's raw API:

### 1. Type Safety
- Pydantic validates data at runtime
- IDE autocomplete works perfectly
- Catch errors early

### 2. Persistence Layer
- Designed to be stored in your casefile database
- Include sync tracking (`last_sync_token`, `synced_at`, `sync_status`)
- Can be serialized to JSON easily

### 3. Business Logic
- `unread_count()` computed field on `CasefileGmailData`
- `upsert_messages()` for merging new data
- Simplified structure (you don't need all of Google's 100+ fields)

### 4. Consistency
- All timestamps in ISO 8601 format
- Consistent naming conventions (`snake_case` vs Google's `camelCase`)
- Required vs optional fields match YOUR needs

---

## Example: Data Flow Trace

### 1. Call Gmail API
```python
service = build('gmail', 'v1', creds)
response = service.users().messages().get(userId='me', id=msg_id).execute()
```

### 2. Google's Response Format
```json
{
  "id": "18c1a2b3d4e5f6",
  "threadId": "18c1a2b3d4e5f6",
  "labelIds": ["INBOX", "UNREAD"],
  "snippet": "Hello there...",
  "internalDate": "1697097600000",
  "payload": {
    "headers": [
      {"name": "From", "value": "sender@example.com"},
      {"name": "Subject", "value": "Test Email"}
    ],
    "body": {"data": "...base64..."}
  }
}
```

### 3. Transform to Your Model
```python
message = GmailMessage(
    id=response['id'],
    thread_id=response['threadId'],
    subject=extract_header(response, 'Subject'),
    sender=extract_header(response, 'From'),
    labels=response.get('labelIds', []),
    snippet=response.get('snippet', ''),
    internal_date=convert_timestamp(response['internalDate']),
    # ... more fields
)
```

### 4. Store in Casefile
```python
casefile.gmail_data.messages.append(message)
casefile.save()  # Persisted in your database
```

---

## Quick Field Mappings

### Gmail
- `GmailMessage.id` ← Gmail API: `message.id`
- `GmailMessage.sender` ← Gmail API: `payload.headers` (From)
- `GmailMessage.labels` ← Gmail API: `labelIds`

### Drive
- `DriveFile.id` ← Drive API: `file.id`
- `DriveFile.mime_type` ← Drive API: `file.mimeType`
- `DriveFile.web_view_link` ← Drive API: `file.webViewLink`

### Sheets
- `SheetRange.range` ← Sheets API: `ValueRange.range`
- `SheetRange.values` ← Sheets API: `ValueRange.values`
- `SheetData.spreadsheet_id` ← Sheets API: `Spreadsheet.spreadsheetId`

---

## Summary

**Your models are custom-built Pydantic wrappers** designed specifically for your casefile system. They:

- Simplify Google's complex API responses
- Add business logic and helper methods
- Provide type safety and validation
- Are optimized for persistent storage
- Match your application's specific needs

You can always refer to Google's official documentation to understand the source data, then see how your models adapt it for your use case.
