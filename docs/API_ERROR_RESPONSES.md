# API Error Response Formats

**API Version:** 0.1.0  
**Last Updated:** October 1, 2025  
**Framework:** FastAPI with Pydantic validation

---

## Overview

This document describes the standard error response formats for all MDS Objects API endpoints. Understanding these formats helps clients handle errors gracefully and provides clear debugging information.

---

## Standard Error Response Structure

### FastAPI Default Format

All API errors follow FastAPI's standard error response format:

```json
{
  "detail": "Human-readable error message"
}
```

For validation errors (Pydantic), the response includes detailed field information:

```json
{
  "detail": [
    {
      "type": "string_type",
      "loc": ["body", "field_name"],
      "msg": "Error message",
      "input": "invalid value",
      "ctx": {}
    }
  ]
}
```

---

## HTTP Status Codes

| Code | Status | Meaning | When Used |
|------|--------|---------|-----------|
| 200 | OK | Success | Successful GET, PATCH, or DELETE |
| 201 | Created | Resource created | Successful POST creating new resource |
| 400 | Bad Request | Invalid parameters | Missing required fields, invalid values |
| 401 | Unauthorized | Authentication failed | Missing, invalid, or expired JWT token |
| 403 | Forbidden | Permission denied | Valid authentication but insufficient permissions |
| 404 | Not Found | Resource doesn't exist | Requested resource not found in database |
| 422 | Unprocessable Entity | Validation failed | Pydantic validation error (invalid data types) |
| 500 | Internal Server Error | Server-side error | Unexpected exception, database failures |

---

## Error Response Examples

### 1. 400 Bad Request

**Scenario:** Invalid or missing required parameters

#### Example 1: Missing required field
```http
POST /tool-sessions/
Content-Type: application/json

{}
```

**Response:**
```json
{
  "detail": "Casefile not found: "
}
```
**Status:** `400 Bad Request`

#### Example 2: Session doesn't match casefile
```http
POST /tool-sessions/?session_id=ts_abc123&casefile_id=cf_251001_XYZ
```

**Response:**
```json
{
  "detail": "Session does not belong to the specified casefile"
}
```
**Status:** `400 Bad Request`

---

### 2. 401 Unauthorized

**Scenario:** Missing or invalid authentication token

#### Example: No JWT token provided
```http
GET /tool-sessions/ts_abc123
```

**Response:**
```json
{
  "detail": "Not authenticated"
}
```
**Status:** `401 Unauthorized`

**Headers:**
```
WWW-Authenticate: Bearer
```

---

### 3. 403 Forbidden

**Scenario:** Valid authentication but insufficient permissions

#### Example 1: Accessing another user's casefile
```http
GET /casefiles/cf_251001_ABC123
Authorization: Bearer <valid_token_for_different_user>
```

**Response:**
```json
{
  "detail": "You do not have access to this casefile"
}
```
**Status:** `403 Forbidden`

#### Example 2: Accessing another user's session
```http
POST /tool-sessions/execute
Authorization: Bearer <valid_token_for_different_user>

{
  "session_id": "ts_another_user_session",
  "payload": {
    "tool_name": "example_tool",
    "parameters": {}
  }
}
```

**Response:**
```json
{
  "detail": "You do not have access to this session"
}
```
**Status:** `403 Forbidden`

---

### 4. 404 Not Found

**Scenario:** Requested resource doesn't exist

#### Example 1: Non-existent casefile
```http
GET /casefiles/cf_999999_NOTFOUND
Authorization: Bearer <valid_token>
```

**Response:**
```json
{
  "detail": "Casefile not found: No casefile with ID cf_999999_NOTFOUND"
}
```
**Status:** `404 Not Found`

#### Example 2: Non-existent session
```http
GET /tool-sessions/ts_invalid_session_id
Authorization: Bearer <valid_token>
```

**Response:**
```json
{
  "detail": "Session not found"
}
```
**Status:** `404 Not Found`

---

### 5. 422 Unprocessable Entity

**Scenario:** Request body validation failed (Pydantic)

#### Example 1: Invalid field type
```http
POST /tool-sessions/execute
Authorization: Bearer <valid_token>
Content-Type: application/json

{
  "session_id": "not-a-valid-uuid",
  "payload": {
    "tool_name": 123,
    "parameters": "should-be-object"
  }
}
```

**Response:**
```json
{
  "detail": [
    {
      "type": "uuid_type",
      "loc": ["body", "session_id"],
      "msg": "Input should be a valid UUID",
      "input": "not-a-valid-uuid"
    },
    {
      "type": "string_type",
      "loc": ["body", "payload", "tool_name"],
      "msg": "Input should be a valid string",
      "input": 123
    },
    {
      "type": "dict_type",
      "loc": ["body", "payload", "parameters"],
      "msg": "Input should be a valid dictionary",
      "input": "should-be-object"
    }
  ]
}
```
**Status:** `422 Unprocessable Entity`

#### Example 2: Tool not registered
```http
POST /tool-sessions/execute
Authorization: Bearer <valid_token>
Content-Type: application/json

{
  "session_id": "ts_abc123",
  "payload": {
    "tool_name": "nonexistent_tool",
    "parameters": {}
  }
}
```

**Response:**
```json
{
  "detail": [
    {
      "type": "value_error",
      "loc": ["body", "payload", "tool_name"],
      "msg": "Value error, Tool 'nonexistent_tool' not registered. Available tools: example_tool, metadata_tool, context_tool",
      "input": "nonexistent_tool",
      "ctx": {
        "error": "Tool 'nonexistent_tool' not registered. Available tools: example_tool, metadata_tool, context_tool"
      }
    }
  ]
}
```
**Status:** `422 Unprocessable Entity`

---

### 6. 500 Internal Server Error

**Scenario:** Unexpected server-side error

#### Example: Tool execution failure
```http
POST /tool-sessions/execute
Authorization: Bearer <valid_token>
Content-Type: application/json

{
  "session_id": "ts_abc123",
  "payload": {
    "tool_name": "example_tool",
    "parameters": {"input": "causes_exception"}
  }
}
```

**Response:**
```json
{
  "detail": "Tool execution failed: Unexpected error in tool implementation"
}
```
**Status:** `500 Internal Server Error`

---

## Validation Error Details

### Pydantic Validation Error Structure

When request body validation fails, Pydantic returns detailed error information:

```json
{
  "detail": [
    {
      "type": "error_type",
      "loc": ["location", "of", "error"],
      "msg": "Human-readable message",
      "input": "<the invalid input>",
      "ctx": {
        "additional": "context"
      }
    }
  ]
}
```

**Field Descriptions:**
- **`type`**: Error category (e.g., `string_type`, `value_error`, `missing`)
- **`loc`**: Path to the field in the request (e.g., `["body", "payload", "tool_name"]`)
- **`msg`**: Human-readable error message
- **`input`**: The invalid value that was provided
- **`ctx`**: Additional context about the error (optional)

### Common Validation Error Types

| Type | Meaning | Example |
|------|---------|---------|
| `missing` | Required field not provided | `"Field required"` |
| `string_type` | Expected string, got different type | `"Input should be a valid string"` |
| `int_type` | Expected integer, got different type | `"Input should be a valid integer"` |
| `dict_type` | Expected dictionary/object | `"Input should be a valid dictionary"` |
| `uuid_type` | Invalid UUID format | `"Input should be a valid UUID"` |
| `value_error` | Custom validation failed | `"Tool 'X' not registered"` |
| `greater_than` | Number below minimum | `"Input should be greater than 0"` |
| `less_than` | Number above maximum | `"Input should be less than 100"` |
| `string_too_short` | String below minimum length | `"String should have at least 1 character"` |
| `string_too_long` | String above maximum length | `"String should have at most 500 characters"` |

---

## Error Handling Best Practices

### For API Clients

1. **Always check HTTP status code** before parsing response
2. **Handle validation errors** by parsing the `detail` array
3. **Display user-friendly messages** based on error type
4. **Log full error details** for debugging
5. **Implement retry logic** for 500 errors (with exponential backoff)
6. **Don't retry** 400, 401, 403, 404 errors (client errors)

### Example Client Code (Python)

```python
import requests

def call_api(endpoint, method="GET", json=None, token=None):
    """Make API call with proper error handling."""
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    
    response = requests.request(
        method=method,
        url=f"http://api.example.com{endpoint}",
        json=json,
        headers=headers
    )
    
    if response.status_code == 200:
        return response.json()
    
    elif response.status_code == 400:
        error = response.json()
        raise ValueError(f"Bad request: {error['detail']}")
    
    elif response.status_code == 401:
        raise PermissionError("Authentication required")
    
    elif response.status_code == 403:
        error = response.json()
        raise PermissionError(f"Access denied: {error['detail']}")
    
    elif response.status_code == 404:
        error = response.json()
        raise LookupError(f"Not found: {error['detail']}")
    
    elif response.status_code == 422:
        error = response.json()
        # Parse validation errors
        errors = error["detail"]
        messages = [f"{'.'.join(e['loc'])}: {e['msg']}" for e in errors]
        raise ValueError(f"Validation failed:\n" + "\n".join(messages))
    
    elif response.status_code >= 500:
        error = response.json()
        raise RuntimeError(f"Server error: {error['detail']}")
    
    else:
        raise RuntimeError(f"Unexpected status: {response.status_code}")
```

### Example Client Code (JavaScript)

```javascript
async function callAPI(endpoint, options = {}) {
  const { method = 'GET', body, token } = options;
  
  const headers = {
    'Content-Type': 'application/json',
  };
  
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  
  const response = await fetch(`http://api.example.com${endpoint}`, {
    method,
    headers,
    body: body ? JSON.stringify(body) : undefined,
  });
  
  const data = await response.json();
  
  if (!response.ok) {
    // Handle errors based on status code
    switch (response.status) {
      case 400:
        throw new Error(`Bad request: ${data.detail}`);
      
      case 401:
        throw new Error('Authentication required');
      
      case 403:
        throw new Error(`Access denied: ${data.detail}`);
      
      case 404:
        throw new Error(`Not found: ${data.detail}`);
      
      case 422:
        // Format validation errors
        const errors = data.detail
          .map(e => `${e.loc.join('.')}: ${e.msg}`)
          .join('\n');
        throw new Error(`Validation failed:\n${errors}`);
      
      case 500:
        throw new Error(`Server error: ${data.detail}`);
      
      default:
        throw new Error(`Unexpected error: ${response.status}`);
    }
  }
  
  return data;
}
```

---

## Interactive API Documentation

### Swagger UI

Access interactive API documentation at: `http://localhost:8000/docs`

Features:
- Try endpoints directly in browser
- See all possible responses
- View request/response schemas
- Test authentication

### ReDoc

Alternative documentation at: `http://localhost:8000/redoc`

Features:
- Clean, readable layout
- Code samples in multiple languages
- Detailed schema documentation

---

## Testing Error Responses

### Using curl

```bash
# Test 401 Unauthorized
curl -X GET http://localhost:8000/tool-sessions/ts_test

# Test 403 Forbidden (with wrong user's token)
curl -X GET http://localhost:8000/casefiles/cf_251001_ABC \
  -H "Authorization: Bearer <other_user_token>"

# Test 404 Not Found
curl -X GET http://localhost:8000/casefiles/cf_invalid \
  -H "Authorization: Bearer <valid_token>"

# Test 422 Validation Error
curl -X POST http://localhost:8000/tool-sessions/execute \
  -H "Authorization: Bearer <valid_token>" \
  -H "Content-Type: application/json" \
  -d '{"session_id": "invalid", "payload": {}}'
```

### Using pytest

```python
import pytest
from fastapi.testclient import TestClient
from src.pydantic_api.app import app

client = TestClient(app)

def test_unauthorized_access():
    """Test 401 error when no token provided."""
    response = client.get("/tool-sessions/ts_test")
    assert response.status_code == 401
    assert "detail" in response.json()

def test_not_found_error():
    """Test 404 error for non-existent resource."""
    response = client.get(
        "/casefiles/cf_invalid",
        headers={"Authorization": "Bearer <valid_token>"}
    )
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()

def test_validation_error():
    """Test 422 error for invalid request body."""
    response = client.post(
        "/tool-sessions/execute",
        json={"session_id": "not-uuid", "payload": {}},
        headers={"Authorization": "Bearer <valid_token>"}
    )
    assert response.status_code == 422
    assert isinstance(response.json()["detail"], list)
```

---

## Future Enhancements

### Planned Improvements

1. **Error Codes**: Add structured error codes for programmatic handling
   ```json
   {
     "error_code": "CASEFILE_NOT_FOUND",
     "detail": "Casefile not found: cf_251001_ABC",
     "timestamp": "2025-10-01T12:00:00Z"
   }
   ```

2. **Request ID**: Include request tracking ID
   ```json
   {
     "request_id": "req_abc123xyz",
     "detail": "Error message"
   }
   ```

3. **Localization**: Multi-language error messages
4. **Detailed Context**: More context in error responses
5. **Error Documentation Links**: URLs to relevant documentation

---

## Related Documents

- **API Documentation:** `/docs` (Swagger UI)
- **Authentication Guide:** `docs/AUTHENTICATION.md`
- **Tool Registration:** `docs/TOOL_ENGINEERING_SESSION_NOTES.md`
- **Environment Setup:** `docs/ENV_VAR_AUDIT.md`

---

**Last Updated:** October 1, 2025  
**Maintainer:** MDS Objects API Team  
**Feedback:** Submit issues via GitHub
