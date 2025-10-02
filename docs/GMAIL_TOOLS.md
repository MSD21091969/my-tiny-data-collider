# Gmail Tools Documentation

## Overview

The Gmail toolset provides real API integration with Gmail for listing, reading, sending, and searching email messages. These tools follow the MDS Objects tool engineering foundation patterns and include full OAuth2 authentication support.

## Features

- ✅ **Real Gmail API Integration**: Direct integration with Google Gmail API v1
- ✅ **OAuth2 Authentication**: Secure authentication with credential refresh
- ✅ **4 Core Operations**: List, Get, Send, and Search messages
- ✅ **Full Parameter Validation**: Pydantic-based validation with constraints
- ✅ **Event Tracking**: Automatic audit trail in MDS context
- ✅ **Error Handling**: Comprehensive error handling and reporting
- ✅ **20+ Test Cases**: Extensive test coverage for all scenarios

## Prerequisites

### 1. Google Cloud Project Setup

1. Create a project in [Google Cloud Console](https://console.cloud.google.com)
2. Enable the Gmail API for your project
3. Create OAuth2 credentials (Desktop application type)
4. Download the credentials JSON file

### 2. Environment Configuration

Add the following to your `.env` file:

```bash
# Gmail API Configuration
GOOGLE_OAUTH_CREDENTIALS=/path/to/oauth2_credentials.json
GOOGLE_TOKEN_PATH=/path/to/token.json  # Optional, defaults to token.json

# Optional: Override default scopes (not recommended)
# GMAIL_SCOPES=https://www.googleapis.com/auth/gmail.readonly,https://www.googleapis.com/auth/gmail.send
```

### 3. Dependencies

The following packages are required (already in `requirements.txt`):

```
google-api-python-client>=2.80.0
google-auth>=2.19.0
google-auth-oauthlib>=1.0.0
```

## Tools

### 1. gmail_list_messages

Lists messages from Gmail inbox with optional filtering.

**Parameters:**
- `max_results` (int, optional): Maximum number of messages to return (1-100, default: 10)
- `query` (str, optional): Gmail search query (max 500 chars, default: "")
- `label_ids` (list, optional): List of label IDs to filter by
- `include_spam_trash` (bool, optional): Include spam and trash (default: false)

**Returns:**
```json
{
  "messages": [
    {"id": "msg123", "threadId": "thread456"}
  ],
  "result_size_estimate": 100,
  "message_count": 10,
  "next_page_token": "token123"
}
```

**Example:**
```python
from src.pydantic_ai_integration.tools.gmail_tools import gmail_list_messages
from src.pydantic_ai_integration.dependencies import MDSContext

ctx = MDSContext(user_id="user123", session_id="session456")
result = await gmail_list_messages(
    ctx,
    max_results=50,
    query="from:sender@example.com is:unread"
)
```

### 2. gmail_get_message

Retrieves a specific Gmail message by ID with full details.

**Parameters:**
- `message_id` (str, required): The ID of the message to retrieve (1-100 chars)
- `format` (str, optional): Message format - "full", "metadata", "minimal", or "raw" (default: "full")
- `metadata_headers` (list, optional): List of headers to return when format="metadata"

**Returns:**
```json
{
  "id": "msg123",
  "thread_id": "thread456",
  "label_ids": ["INBOX", "UNREAD"],
  "snippet": "Message preview text...",
  "headers": [
    {"name": "Subject", "value": "Email Subject"},
    {"name": "From", "value": "sender@example.com"}
  ],
  "mime_type": "text/plain",
  "body": {"data": "base64_encoded_body"}
}
```

**Example:**
```python
result = await gmail_get_message(
    ctx,
    message_id="msg123",
    format="metadata",
    metadata_headers=["Subject", "From", "Date"]
)
```

### 3. gmail_send_message

Sends an email message via Gmail.

**Parameters:**
- `to` (str, required): Recipient email address (5-500 chars)
- `subject` (str, required): Email subject (1-500 chars)
- `body` (str, required): Email body text (1-50000 chars)
- `from_email` (str, optional): Sender email (uses authenticated user if not provided)
- `cc` (str, optional): CC recipients (comma-separated, max 500 chars)
- `bcc` (str, optional): BCC recipients (comma-separated, max 500 chars)

**Returns:**
```json
{
  "id": "sent123",
  "thread_id": "thread456",
  "to": "recipient@example.com",
  "subject": "Email Subject",
  "status": "sent"
}
```

**Example:**
```python
result = await gmail_send_message(
    ctx,
    to="recipient@example.com",
    subject="Meeting Follow-up",
    body="Thank you for attending the meeting...",
    cc="manager@example.com"
)
```

### 4. gmail_search_messages

Searches Gmail messages using Gmail query syntax.

**Parameters:**
- `query` (str, required): Gmail search query (1-500 chars)
- `max_results` (int, optional): Maximum number of messages to return (1-100, default: 10)
- `label_ids` (list, optional): List of label IDs to filter by

**Returns:**
```json
{
  "messages": [
    {"id": "msg123", "threadId": "thread456"}
  ],
  "result_size_estimate": 25,
  "message_count": 10,
  "query": "from:sender@example.com subject:report"
}
```

**Example:**
```python
result = await gmail_search_messages(
    ctx,
    query="from:sender@example.com subject:report after:2024/01/01",
    max_results=25
)
```

## Gmail Query Syntax

The `query` parameter in `gmail_list_messages` and `gmail_search_messages` supports Gmail's powerful search syntax:

### Common Query Operators

- `from:sender@example.com` - Emails from specific sender
- `to:recipient@example.com` - Emails to specific recipient
- `subject:keyword` - Emails with keyword in subject
- `has:attachment` - Emails with attachments
- `is:unread` - Unread emails
- `is:starred` - Starred emails
- `after:2024/01/01` - Emails after date
- `before:2024/12/31` - Emails before date
- `newer_than:7d` - Emails newer than 7 days
- `older_than:1m` - Emails older than 1 month
- `label:inbox` - Emails in inbox
- `has:drive` - Emails with Google Drive attachments

### Combining Operators

Use AND/OR logic:
- `from:sender@example.com subject:report` (implicit AND)
- `from:sender@example.com OR from:other@example.com`
- `from:sender@example.com -subject:draft` (exclude drafts)

## Authentication Flow

### First-Time Authentication

1. When you first call a Gmail tool, the OAuth2 flow will automatically start
2. A browser window will open asking you to sign in to Google
3. Grant the requested permissions
4. The tool will receive a token and save it to `token.json`
5. Subsequent calls will use the saved token

### Token Refresh

- Access tokens expire after 1 hour
- The authentication module automatically refreshes expired tokens using the refresh token
- If refresh fails, you'll need to re-authenticate

### Revoking Access

To revoke Gmail API access:

```python
from src.google_workspace.auth import GoogleWorkspaceAuth

auth = GoogleWorkspaceAuth()
auth.revoke_credentials()
```

This will:
1. Revoke the access token with Google
2. Delete the local `token.json` file

## Error Handling

All Gmail tools include comprehensive error handling:

### Common Errors

**Authentication Errors:**
```json
{
  "error": "Failed to list Gmail messages",
  "details": "Failed to obtain valid credentials"
}
```

**API Errors:**
```json
{
  "error": "Failed to get Gmail message msg123",
  "details": "404: Message not found"
}
```

**Validation Errors:**
```json
{
  "error": "Parameter validation failed",
  "details": [
    {
      "loc": ["max_results"],
      "msg": "ensure this value is less than or equal to 100"
    }
  ]
}
```

### Error Recovery

Tools automatically:
1. Log errors with full context
2. Update the MDS context event status to "failed"
3. Return error information in a consistent format
4. Preserve context for subsequent operations

## Event Tracking

All Gmail tool executions are automatically tracked in the MDS context:

```python
# After calling a tool
event = ctx.tool_events[-1]
print(f"Tool: {event.tool_name}")
print(f"Status: {event.status}")
print(f"Result: {event.result_summary}")
```

Event information includes:
- Tool name
- Parameters used
- Result summary (message counts, IDs, etc.)
- Status (success/failed)
- Timestamp
- Duration

## Testing

### Running Tests

```bash
# Run all Gmail tool tests
pytest tests/test_gmail_tools.py -v

# Run specific test class
pytest tests/test_gmail_tools.py::TestGmailListMessages -v

# Run with coverage
pytest tests/test_gmail_tools.py --cov=src.pydantic_ai_integration.tools.gmail_tools
```

### Test Coverage

The test suite includes:
- ✅ Parameter validation tests (12 tests)
- ✅ Successful operation tests (4 tests)
- ✅ Error handling tests (4 tests)
- ✅ Integration tests (2 tests)
- ✅ Edge case tests (multiple scenarios)

Total: 20+ test cases covering all functionality

## Architecture

### Component Structure

```
src/
├── google_workspace/
│   ├── __init__.py           # Package initialization
│   ├── auth.py               # OAuth2 authentication
│   └── gmail_client.py       # Gmail API client wrapper
└── pydantic_ai_integration/
    └── tools/
        └── gmail_tools.py    # Tool implementations

config/
└── tools/
    └── gmail/
        ├── gmail_list_messages.yaml
        ├── gmail_get_message.yaml
        ├── gmail_send_message.yaml
        └── gmail_search_messages.yaml

tests/
└── test_gmail_tools.py       # Comprehensive test suite
```

### Design Patterns

1. **Tool Decorator Pattern**: Tools use `@register_mds_tool` for registration
2. **Pydantic Validation**: All parameters validated via Pydantic models
3. **Client Wrapper Pattern**: `GmailClient` abstracts API complexity
4. **Async/Await**: All operations are async for better performance
5. **Event Sourcing**: All operations tracked in MDS context

## YAML Configuration

Each tool has a YAML definition in `config/tools/gmail/` that specifies:
- Tool metadata (name, description, category)
- Business rules (auth requirements, permissions)
- Parameters with validation rules
- Response schema
- Casefile storage settings

These YAML files serve as documentation and can be used for code generation in future iterations.

## Security Considerations

1. **OAuth2 Credentials**: Never commit `credentials.json` or `token.json` to git
2. **Token Storage**: Store tokens securely with appropriate file permissions
3. **Scopes**: Request only the minimum required scopes
4. **User Isolation**: Each user should have their own authentication
5. **Error Messages**: Don't expose sensitive data in error messages

## Performance

### Best Practices

1. **Pagination**: Use `max_results` to limit data transfer
2. **Caching**: Consider caching message lists for frequently accessed data
3. **Batch Operations**: Use search queries to filter at the API level
4. **Token Reuse**: Authentication tokens are reused automatically

### Rate Limits

Gmail API has rate limits:
- 250 quota units per user per second
- 1,000,000,000 quota units per day

Each operation consumes quota units:
- `list_messages`: 5 units
- `get_message`: 5 units
- `send_message`: 100 units

## Future Enhancements

Potential improvements for future versions:

1. **Attachment Handling**: Support for downloading/uploading attachments
2. **Draft Management**: Create, update, and send drafts
3. **Label Management**: Create and manage custom labels
4. **Thread Operations**: Operate on entire threads
5. **Batch Requests**: Batch multiple operations for efficiency
6. **Watch/Push Notifications**: Real-time message notifications
7. **Message Modification**: Mark as read/unread, archive, trash
8. **Advanced Search**: Support for more complex queries

## Troubleshooting

### Issue: "Credentials file not found"

**Solution**: Ensure `GOOGLE_OAUTH_CREDENTIALS` points to valid credentials JSON

### Issue: "Invalid authentication credentials"

**Solution**: Re-download credentials from Google Cloud Console and update path

### Issue: "Token has been expired or revoked"

**Solution**: Delete `token.json` and re-authenticate

### Issue: "Insufficient permissions"

**Solution**: Ensure OAuth consent screen is properly configured with required scopes

### Issue: "Quota exceeded"

**Solution**: Wait for quota to reset or request quota increase in Google Cloud Console

## Support

For issues or questions:
1. Check this documentation
2. Review test cases in `tests/test_gmail_tools.py`
3. Consult Google's [Gmail API documentation](https://developers.google.com/gmail/api)
4. Review the tool engineering foundation in `docs/TOOLENGINEERING_FOUNDATION.md`

## License

This implementation follows the project's licensing terms.
