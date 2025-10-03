# Gmail Tools

## Overview

Gmail toolset provides email management capabilities through the Google Workspace API integration. All tools enforce session/casefile policies defined in YAML and maintain comprehensive audit trails per the N-tier architecture.

**Status**: Week 2 MVP - Mock implementations with full Pydantic models  
**Branch**: `feature/google-workspace-gmail`  
**Real API Integration**: TODO (Week 3+)

## Architecture

### Layered Structure (per Copilot Instructions)

```
API Layer (src/pydantic_api/routers/)
    ↓ JWT auth, RequestEnvelope handling
Service Layer (src/tool_sessionservice/)
    ↓ Policy enforcement (PRIMARY ENFORCEMENT POINT)
Tool Layer (src/pydantic_ai_integration/tools/generated/)
    ↓ Business logic, calls GmailClient
Gmail Client (src/pydantic_ai_integration/google_workspace/clients.py)
    ↓ Mock async methods returning DTOs
Request/Response DTOs (src/pydantic_ai_integration/google_workspace/models.py)
    ↓ References canonical models
Canonical Models (src/pydantic_models/workspace.py)
```

### Policy Enforcement Flow

1. **YAML Definition**: Policies declared in `config/tools/gmail_*.yaml`
2. **Tool Factory**: Generates Python with `@register_mds_tool` decorator
3. **MANAGED_TOOLS Registry**: Stores policies for runtime enforcement
4. **Service Layer**: Enforces policies before tool execution (NO policy checks in tool layer)
5. **Tool Execution**: Business logic only, calls `GmailClient` methods
6. **Audit Trail**: Created per `audit_events` config in YAML

## Available Tools

### 1. `gmail_list_messages`

**Purpose**: List messages in user's Gmail inbox with optional filters

**YAML Source**: `config/tools/gmail_list_messages.yaml`  
**Generated Tool**: `src/pydantic_ai_integration/tools/generated/gmail_list_messages.py`  
**Generated Tests**: `tests/generated/test_gmail_list_messages.py`

**Parameters**:
- `max_results` (int, optional): Maximum messages to return (default: 10, range: 1-100)
- `query` (str, optional): Gmail search query (e.g., `"is:unread"`, `"from:example@gmail.com"`)
- `label_ids` (List[str], optional): Filter by label IDs (e.g., `["INBOX", "UNREAD"]`)

**Returns**: `GmailListMessagesResponse` with:
- `messages`: List of `GmailMessage` objects (full Pydantic models)
- `next_page_token`: Pagination token (optional)

**Policies** (from YAML):
- Requires active session
- Requires `gmail.readonly` permission
- Session timeout: 30 seconds
- Logs request payload, not full response (PII concern)

**Example Usage**:
```python
from src.pydantic_ai_integration.dependencies import MDSContext
from src.pydantic_ai_integration.tools.generated.gmail_list_messages import gmail_list_messages

ctx = MDSContext(user_id="user123", session_id="sess456", casefile_id="case789")
result = await gmail_list_messages(ctx, max_results=20, query="is:unread")
# result["messages"] contains list of GmailMessage Pydantic models
```

**Mock Behavior**:
- Returns 2 hardcoded messages with realistic structure
- Ignores query/label filters (Week 2 limitation)
- Simulates 100ms API latency via `asyncio.sleep(0.1)`

---

### 2. `gmail_send_message`

**Purpose**: Send email via user's Gmail account

**YAML Source**: `config/tools/gmail_send_message.yaml`  
**Generated Tool**: `src/pydantic_ai_integration/tools/generated/gmail_send_message.py`  
**Generated Tests**: `tests/generated/test_gmail_send_message.py`

**Parameters**:
- `to` (str, required): Recipient email address (validated via Pydantic EmailStr)
- `subject` (str, required): Email subject (1-200 chars)
- `body` (str, required): Email body plain text (min 1 char)
- `cc` (str, optional): CC recipients (comma-separated)
- `bcc` (str, optional): BCC recipients (comma-separated)

**Returns**: `GmailSendMessageResponse` with:
- `message_id`: ID of sent message
- `thread_id`: Thread ID
- `label_ids`: Labels applied (e.g., `["SENT"]`)

**Policies** (from YAML):
- Requires active session
- Requires `gmail.send` permission
- Session timeout: 30 seconds
- Logs full request and response for audit

**Example Usage**:
```python
result = await gmail_send_message(
    ctx,
    to="recipient@example.com",
    subject="Project Update",
    body="The milestone has been completed."
)
# result["message_id"] contains sent message ID
```

**Mock Behavior**:
- Returns timestamped message ID (e.g., `"mock-sent-1696320000"`)
- Does not actually send email
- Simulates 200ms API latency

---

### 3. `gmail_search_messages`

**Purpose**: Advanced search with pagination support

**YAML Source**: `config/tools/gmail_search_messages.yaml`  
**Generated Tool**: `src/pydantic_ai_integration/tools/generated/gmail_search_messages.py`  
**Generated Tests**: `tests/generated/test_gmail_search_messages.py`

**Parameters**:
- `query` (str, required): Gmail search query (1-2048 chars)
- `max_results` (int, optional): Results per page (default: 10, range: 1-100)
- `page_token` (str, optional): Pagination token from previous search

**Returns**: `GmailSearchMessagesResponse` with:
- `messages`: List of `GmailMessage` objects matching query
- `next_page_token`: Token for next page (if more results exist)
- `result_size_estimate`: Estimated total matching messages

**Policies** (from YAML):
- Requires active session
- Requires `gmail.readonly` permission
- Query complexity limits enforced at service layer
- Session timeout: 30 seconds

**Example Usage**:
```python
result = await gmail_search_messages(
    ctx,
    query="from:notifications@example.com is:unread",
    max_results=50
)
# result["messages"] contains matching GmailMessage models
# result["next_page_token"] for pagination
```

**Mock Behavior**:
- Returns 1 search result with query echoed in subject
- `next_page_token` always None (no pagination in mock)
- Simulates 150ms API latency

---

### 4. `gmail_get_message`

**Purpose**: Retrieve full message details by ID

**YAML Source**: `config/tools/gmail_get_message.yaml`  
**Generated Tool**: `src/pydantic_ai_integration/tools/generated/gmail_get_message.py`  
**Generated Tests**: `tests/generated/test_gmail_get_message.py`

**Parameters**:
- `message_id` (str, required): Gmail message ID (min 1 char)
- `format` (str, optional): Response format - `"full"`, `"metadata"`, `"minimal"` (default: `"full"`)

**Returns**: `GmailGetMessageResponse` with:
- `message`: Complete `GmailMessage` Pydantic model with:
  - Headers (from, to, subject, date)
  - Body (text and/or HTML)
  - Attachments list
  - Labels
  - Thread ID

**Policies** (from YAML):
- Requires active session
- Requires `gmail.readonly` permission
- Casefile logging enabled (logs message access for compliance)
- Session timeout: 30 seconds

**Example Usage**:
```python
result = await gmail_get_message(
    ctx,
    message_id="msg_18c3f2a9b4e5d6f7",
    format="full"
)
# result["message"] contains full GmailMessage with body/attachments
```

**Mock Behavior**:
- Returns hardcoded message with provided `message_id`
- Ignores `format` parameter (always returns full details)
- Simulates 100ms API latency

---

## Testing Strategy

### Unit Tests (`tests/generated/test_gmail_*.py`)

**What's Tested**:
- ✅ Parameter validation (Pydantic constraints: min/max values, lengths)
- ✅ Default values and optional parameters
- ✅ MDSContext propagation (user_id, session_id, casefile_id)
- ✅ Audit event registration via `ctx.register_event()`
- ⚠️ Response structure validation (currently failing due to mock data mismatch)

**Test Execution**:
```powershell
# Run all Gmail unit tests
python -m pytest tests/generated -k gmail -v

# Run specific tool tests
python -m pytest tests/generated/test_gmail_list_messages.py -v

# Run with coverage
python -m pytest tests/generated -k gmail --cov=src/pydantic_ai_integration/tools/generated --cov-report=html
```

**Current Status** (Week 2):
- ✅ 19/25 tests passing (76% success rate)
- ❌ 6 tests failing due to:
  1. Mock response structure mismatch (tests expect simplified dicts, client returns full Pydantic models)
  2. Error scenario tests expecting exceptions (mock client doesn't raise)
  
**Known Test Issues** (TODO Week 3):
```python
# Expected by tests (from YAML examples):
{"messages": [{"id": "mock-msg-1", "subject": "Mock subject"}]}

# Actually returned by mock client:
{"messages": [GmailMessage(id="mock-msg-1", thread_id="...", subject="...", sender="...", ...)]}
```

**Fix Approach** (Week 3):
- Option A: Update YAML examples to match full Pydantic model structure
- Option B: Add `.model_dump()` serialization layer in tool implementation
- Option C: Update test expectations to validate against Pydantic models directly

### Integration Tests (`tests/integration/`)

**Status**: Not yet implemented for Gmail tools  
**Planned** (Week 3):
- Test policy enforcement (rate limits, session validation)
- Test service layer orchestration
- Test audit trail creation (Firestore writes)
- Test error handling (quota exceeded, invalid credentials)
- Test casefile logging when `log_to_casefile: true`

**Example Integration Test** (TODO):
```python
async def test_gmail_list_with_policy_enforcement():
    """Test that service layer enforces max_results policy."""
    # Attempt to request 200 messages (exceeds business_rules.max_results: 100)
    response = await tool_session_service.execute_tool(
        tool_name="gmail_list_messages",
        params={"max_results": 200},
        context={"user_id": "test_user", "session_id": "test_session"}
    )
    assert response.status == "rejected"
    assert "exceeds maximum allowed" in response.error_message
```

### API Tests (`tests/api/`)

**Status**: Not yet implemented for Gmail tools  
**Planned** (Week 3):
- End-to-end HTTP tests with JWT authentication
- Test `RequestEnvelope` → JSON response flow
- Test HTTP status codes (401 Unauthorized, 403 Forbidden, 429 Rate Limited, 500 Internal Error)
- Test CORS headers and content negotiation

**Example API Test** (TODO):
```python
def test_gmail_list_endpoint_requires_auth(client: TestClient):
    """Test that /tool-sessions/execute requires valid JWT."""
    response = client.post(
        "/tool-sessions/execute",
        json={
            "tool_name": "gmail_list_messages",
            "params": {"max_results": 10}
        }
    )
    assert response.status_code == 401
    assert "authentication required" in response.json()["detail"].lower()
```

---

## Mock Data Patterns

### Mock Client (`GmailClient` in `clients.py`)

```python
class GmailClient:
    def __init__(self, user_id: str, *, use_mock: Optional[bool] = None):
        # Mock mode enabled by default (from config.google_workspace.mock_mode)
        self.use_mock = use_mock if use_mock is not None else True
        self.user_id = user_id
    
    async def list_messages(self, request: GmailListMessagesRequest) -> GmailListMessagesResponse:
        if not self.use_mock:
            raise NotImplementedError("Real Gmail API integration not implemented.")
        await asyncio.sleep(0.1)  # Simulate API latency
        return GmailListMessagesResponse(
            messages=[
                GmailMessage(id="mock-msg-1", thread_id="...", ...),
                GmailMessage(id="mock-msg-2", thread_id="...", ...),
            ],
            next_page_token=None
        )
```

### Mock Response Examples

**List Messages**:
```json
{
  "messages": [
    {
      "id": "mock-msg-1",
      "thread_id": "mock-thread-1",
      "subject": "Mock subject",
      "sender": "notifications@example.com",
      "to_recipients": ["test_user@example.com"],
      "snippet": "This is a mock Gmail message",
      "internal_date": "2025-10-03T01:47:26.526783",
      "labels": ["INBOX", "MOCK"],
      "has_attachments": false,
      "body_text": "Mock email body"
    }
  ],
  "next_page_token": null
}
```

**Send Message**:
```json
{
  "message_id": "mock-sent-1696320000",
  "thread_id": "mock-thread-sent-1696320000",
  "label_ids": ["SENT"]
}
```

**Search Messages**:
```json
{
  "messages": [
    {
      "id": "mock-search-1",
      "subject": "Search Result for: from:notifications@example.com",
      "snippet": "This message matches your search"
    }
  ],
  "next_page_token": null,
  "result_size_estimate": 1
}
```

---

## Real API Integration (TODO)

### Prerequisites

1. **Enable Gmail API** in Google Cloud Console
2. **Configure OAuth 2.0** credentials:
   - Application type: Web application
   - Authorized redirect URIs: `https://your-domain.com/auth/callback`
3. **Store refresh tokens** in Firestore per user:
   ```python
   firestore.collection("user_credentials").document(user_id).set({
       "google_refresh_token": encrypted_token,
       "google_scopes": ["https://www.googleapis.com/auth/gmail.modify"],
       "token_expires_at": timestamp
   })
   ```
4. **Implement token refresh flow** in `GmailClient.__init__()`:
   ```python
   from google.oauth2.credentials import Credentials
   from googleapiclient.discovery import build
   
   creds = Credentials(
       token=access_token,
       refresh_token=refresh_token,
       token_uri="https://oauth2.googleapis.com/token",
       client_id=os.getenv("GOOGLE_CLIENT_ID"),
       client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
       scopes=["https://www.googleapis.com/auth/gmail.modify"]
   )
   self.service = build("gmail", "v1", credentials=creds)
   ```

### Environment Variables

```bash
# .env or environment config
GOOGLE_CLIENT_ID=your_client_id_from_console.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your_client_secret
GOOGLE_REDIRECT_URI=https://your-domain.com/auth/callback
GMAIL_API_SCOPES=https://www.googleapis.com/auth/gmail.modify,https://www.googleapis.com/auth/gmail.readonly
```

### Real Implementation Example

**Replace Mock in `GmailClient.list_messages()`**:
```python
async def list_messages(self, request: GmailListMessagesRequest) -> GmailListMessagesResponse:
    if self.use_mock:
        # ... existing mock implementation
        return GmailListMessagesResponse(...)
    
    # Real Gmail API call
    try:
        results = self.service.users().messages().list(
            userId='me',
            maxResults=request.max_results,
            q=request.query,
            labelIds=request.label_ids,
            pageToken=request.page_token
        ).execute()
        
        messages = []
        for msg_summary in results.get('messages', []):
            # Fetch full message details
            msg = self.service.users().messages().get(
                userId='me',
                id=msg_summary['id'],
                format='metadata'
            ).execute()
            
            # Parse headers
            headers = {h['name']: h['value'] for h in msg['payload']['headers']}
            
            messages.append(GmailMessage(
                id=msg['id'],
                thread_id=msg['threadId'],
                subject=headers.get('Subject', ''),
                sender=headers.get('From', ''),
                snippet=msg.get('snippet', ''),
                internal_date=msg.get('internalDate'),
                labels=msg.get('labelIds', []),
                # ... parse other fields
            ))
        
        return GmailListMessagesResponse(
            messages=messages,
            next_page_token=results.get('nextPageToken')
        )
    except Exception as e:
        logger.error(f"Gmail API error: {e}")
        raise
```

### Rate Limiting & Quotas

Gmail API quotas (as of 2025):
- **List/Get**: 250 quota units per user per second
- **Send**: 100 messages per user per day (standard), 2,000 for Workspace accounts
- **Search**: 250 quota units per user per second

**Recommended approach**:
1. Implement exponential backoff for `429 Too Many Requests`
2. Cache message lists in Firestore with TTL (5 minutes)
3. Batch message fetches using `users().messages().batchGet()`
4. Surface quota errors to user via policy enforcement

---

## Known Limitations (Week 2)

### Mock Implementation Constraints

1. **No Real API Calls**: All responses are hardcoded in `GmailClient`
2. **No Query Filtering**: Mock ignores `query` and `label_ids` parameters
3. **No Pagination**: `next_page_token` always `None`
4. **No Attachments**: Attachment handling not implemented
5. **No Thread Operations**: Reply/forward not supported
6. **No Batch Operations**: One message at a time

### Test Coverage Gaps

1. **Integration Tests**: Not yet implemented (service layer policy enforcement)
2. **API Tests**: No end-to-end HTTP tests with JWT auth
3. **Error Scenarios**: Mock doesn't raise exceptions (e.g., message not found, invalid token)
4. **Performance Tests**: No load testing or concurrent request handling

### Architecture TODOs

1. **OAuth Flow**: User consent screen and token management not implemented
2. **Token Refresh**: Automatic refresh before expiry not implemented
3. **Multi-User Support**: Credentials stored per-user in Firestore (planned)
4. **Webhook Support**: Gmail Push notifications for real-time updates (future)
5. **Label Management**: Create/update/delete labels (future tools)
6. **Draft Management**: Save drafts, send drafts (future tools)

---

## Development Workflow

### Adding New Gmail Tools

1. **Create YAML definition** in `config/tools/`:
   ```yaml
   name: gmail_create_draft
   description: "Create a draft email"
   category: google_workspace
   parameters:
     - name: subject
       type: string
       required: true
   implementation:
     type: api_call
     api_call:
       client_module: src.pydantic_ai_integration.google_workspace
       client_class: GmailClient
       method_name: create_draft
       request_type: GmailCreateDraftRequest
   ```

2. **Add client method** in `clients.py`:
   ```python
   async def create_draft(self, request: GmailCreateDraftRequest) -> GmailCreateDraftResponse:
       # Mock implementation
       return GmailCreateDraftResponse(draft_id="mock-draft-123")
   ```

3. **Add DTO models** in `models.py`:
   ```python
   class GmailCreateDraftRequest(BaseModel):
       subject: str
       body: str
   
   class GmailCreateDraftResponse(BaseModel):
       draft_id: str
   ```

4. **Generate tool and tests**:
   ```powershell
   python scripts/generate_tools.py gmail_create_draft
   ```

5. **Run tests**:
   ```powershell
   python -m pytest tests/generated/test_gmail_create_draft.py -v
   ```

### Regenerating Tools After YAML Changes

```powershell
# Regenerate all Gmail tools
python -c "from src.pydantic_ai_integration.tools.factory import ToolFactory; factory = ToolFactory(); [factory.process_tool(factory.config_dir / f'{t}.yaml') for t in ['gmail_list_messages', 'gmail_send_message', 'gmail_search_messages', 'gmail_get_message']]"

# Run tests to verify
python -m pytest tests/generated -k gmail -v
```

---

## Related Documentation

- **[Policy and User ID Flow](POLICY_AND_USER_ID_FLOW.md)**: Policy enforcement architecture, user_id propagation
- **[Layered Architecture Flow](LAYERED_ARCHITECTURE_FLOW.md)**: N-tier architecture, request/response patterns
- **[Tool Engineering Foundation](TOOLENGINEERING_FOUNDATION.md)**: Core design principles, YAML-driven generation
- **[YAML Driven Models](YAML_DRIVEN_MODELS.md)**: Tool Factory patterns, template system

---

## Week 2 Completion Status

### ✅ Completed

- Gmail YAML tool definitions (4 tools: list/send/search/get)
- `GmailClient` mock implementations in `clients.py`
- Request/Response DTOs in `google_workspace/models.py`
- Canonical `GmailMessage` model in `workspace.py`
- Tool Factory generation with API call integration
- Generated unit tests (19/25 passing, 76% coverage)
- Tool template enhancements (List import, ValidationError import)
- Unicode fix in Tool Factory CLI

### ⚠️ Known Issues

- 6 unit tests failing due to mock response structure mismatch
- Integration tests not implemented
- API tests not implemented
- Test expectations need alignment with Pydantic model structure

### 📋 Week 3 Priorities

1. **Fix Unit Tests**: Align test expectations with Pydantic response models
2. **Integration Tests**: Service layer policy enforcement, audit trail validation
3. **API Tests**: End-to-end HTTP with JWT auth
4. **Real API Integration**: OAuth flow, token management, actual Gmail API calls
5. **Error Handling**: Proper exception raising in mock for error scenario tests
6. **Documentation**: API reference, integration guides, troubleshooting

---

## Support & Troubleshooting

### Common Issues

**Issue**: `NameError: name 'List' is not defined` in generated tools  
**Fix**: Tool template now imports `List` from `typing` (fixed in Week 2)

**Issue**: `NameError: name 'ValidationError' is not defined` in tests  
**Fix**: Test template now always imports `ValidationError` from `pydantic` (fixed in Week 2)

**Issue**: Tests expect simple dict, got Pydantic model  
**Fix**: Update test expectations or add `.model_dump()` in tool implementation (TODO Week 3)

**Issue**: Mock doesn't raise exceptions for error scenarios  
**Fix**: Enhance `GmailClient` to detect invalid inputs and raise (TODO Week 3)

### Getting Help

- **Architecture Questions**: See [`.github/copilot-instructions.md`](.github/copilot-instructions.md)
- **YAML Syntax**: See `config/tool_schema_v2.yaml`
- **Test Patterns**: See `tests/generated/test_echo_tool.py` (reference implementation)
- **GitHub Issues**: Tag with `gmail-tools`, `google-workspace`, or `tool-factory`

---

**Last Updated**: October 3, 2025  
**Contributors**: GitHub Copilot (night-shift automation)  
**Status**: Week 2 Complete, Ready for PR Review
