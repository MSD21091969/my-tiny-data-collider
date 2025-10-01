# How to Start a Session - Complete Guide

## Overview

There are **3 main ways** to start a tool session:

1. **Swagger UI** (easiest for manual testing)
2. **Direct API call** (via curl, Postman, etc.)
3. **Python script** (calling service directly)

---

## Method 1: Swagger UI (Recommended for Testing)

### Steps:

1. **Start the server**
   ```bash
   python scripts/main.py
   ```

2. **Open Swagger UI**
   ```
   http://localhost:8000/docs
   ```

3. **Get authentication token**
   - Find the `POST /auth/token` endpoint
   - Click "Try it out"
   - Enter:
     ```json
     {
       "user_id": "user123",
       "roles": ["user"]
     }
     ```
   - Click "Execute"
   - Copy the `access_token` from response

4. **Authorize Swagger**
   - Click the green "Authorize" button at top
   - Paste token in "Value" field
   - Click "Authorize", then "Close"

5. **Create a casefile first** (sessions require casefile)
   - Find `POST /api/casefiles/create`
   - Click "Try it out"
   - Enter:
     ```json
     {
       "metadata": {
         "title": "Test Case",
         "description": "Test description",
         "tags": ["test"],
         "created_by": "user123"
       }
     }
     ```
   - Click "Execute"
   - Copy the `id` from response (e.g., `251001_abc123`)

6. **Create a session**
   - Find `POST /tool-sessions/`
   - Click "Try it out"
   - Enter the casefile_id from step 5
   - Click "Execute"
   - Copy the `session_id` from response (e.g., `ts_251001_user123_case_abc`)

7. **Execute a tool** (optional)
   - Find `POST /tool-sessions/execute`
   - Enter the session_id
   - Enter request body:
     ```json
     {
       "user_id": "user123",
       "operation": "tool_execution",
       "payload": {
         "tool_name": "example_tool",
         "parameters": {
           "value": 42
         }
       },
       "session_id": "ts_251001_user123_case_abc"
     }
     ```
   - Click "Execute"

---

## Method 2: Direct API Call (curl/Postman)

### Prerequisites:
```bash
# Server must be running
python scripts/main.py
```

### Step 1: Get Token
```bash
curl -X POST "http://localhost:8000/auth/token" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user123",
    "roles": ["user"]
  }'
```

**Response:**
```json
{
  "access_token": "eyJhbGc...",
  "token_type": "bearer"
}
```

### Step 2: Create Casefile
```bash
curl -X POST "http://localhost:8000/api/casefiles/create" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -d '{
    "metadata": {
      "title": "Test Case",
      "description": "Test casefile",
      "tags": ["test"],
      "created_by": "user123"
    }
  }'
```

**Response:**
```json
{
  "id": "251001_abc123",
  "metadata": {...},
  "session_ids": []
}
```

### Step 3: Create Session
```bash
curl -X POST "http://localhost:8000/tool-sessions/?casefile_id=251001_abc123" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

**Response:**
```json
{
  "session_id": "ts_251001_user123_251001_abc123_xyz789"
}
```

### Step 4: Execute Tool (optional)
```bash
curl -X POST "http://localhost:8000/tool-sessions/execute?session_id=ts_251001_user123_251001_abc123_xyz789" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -d '{
    "user_id": "user123",
    "operation": "tool_execution",
    "payload": {
      "tool_name": "example_tool",
      "parameters": {
        "value": 42
      }
    },
    "session_id": "ts_251001_user123_251001_abc123_xyz789"
  }'
```

---

## Method 3: Python Script (Direct Service Call)

### Create a test script:

```python
# scripts/test_create_session.py
"""
Test script to create a session directly via service layer.
"""

import asyncio
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.tool_sessionservice import ToolSessionService
from src.casefileservice import CasefileService
from src.pydantic_models.casefile import CasefileModel, CasefileMetadata


async def create_session_example():
    """Example of creating a session directly via service."""
    
    print("=" * 60)
    print("Creating Session via Service Layer")
    print("=" * 60)
    
    # 1. Create casefile service and session service
    casefile_service = CasefileService()
    session_service = ToolSessionService()
    
    # 2. Create a casefile first (sessions require casefile)
    print("\n1. Creating casefile...")
    metadata = CasefileMetadata(
        title="Test Casefile for Session",
        description="Created via script",
        tags=["test", "script"],
        created_by="user123"
    )
    
    casefile = CasefileModel(metadata=metadata)
    casefile_id = await casefile_service.create_casefile(casefile)
    print(f"   ✅ Casefile created: {casefile_id}")
    
    # 3. Create a session linked to the casefile
    print("\n2. Creating session...")
    result = await session_service.create_session(
        user_id="user123",
        casefile_id=casefile_id
    )
    session_id = result["session_id"]
    print(f"   ✅ Session created: {session_id}")
    
    # 4. Get the session to verify
    print("\n3. Retrieving session...")
    session_data = await session_service.get_session(session_id)
    print(f"   ✅ Session retrieved:")
    print(f"      - Session ID: {session_data['session_id']}")
    print(f"      - User ID: {session_data['user_id']}")
    print(f"      - Casefile ID: {session_data['casefile_id']}")
    print(f"      - Active: {session_data['active']}")
    print(f"      - Request IDs: {session_data['request_ids']}")
    
    # 5. Verify casefile has session linked
    print("\n4. Verifying casefile linkage...")
    casefile_data = await casefile_service.get_casefile(casefile_id)
    print(f"   ✅ Casefile has {len(casefile_data['session_ids'])} session(s)")
    print(f"      - Session IDs: {casefile_data['session_ids']}")
    
    print("\n" + "=" * 60)
    print("✅ Complete! Session created successfully")
    print("=" * 60)
    
    return session_id


async def create_and_execute_tool():
    """Example showing full workflow: create session + execute tool."""
    
    print("\n" + "=" * 60)
    print("Full Workflow: Create Session + Execute Tool")
    print("=" * 60)
    
    from src.pydantic_models.tool_session import ToolRequest, ToolRequestPayload
    
    # 1. Setup services
    casefile_service = CasefileService()
    session_service = ToolSessionService()
    
    # 2. Create casefile
    print("\n1. Creating casefile...")
    metadata = CasefileMetadata(
        title="Full Workflow Test",
        created_by="user123"
    )
    casefile = CasefileModel(metadata=metadata)
    casefile_id = await casefile_service.create_casefile(casefile)
    print(f"   ✅ Casefile: {casefile_id}")
    
    # 3. Create session
    print("\n2. Creating session...")
    result = await session_service.create_session(
        user_id="user123",
        casefile_id=casefile_id
    )
    session_id = result["session_id"]
    print(f"   ✅ Session: {session_id}")
    
    # 4. Execute a tool
    print("\n3. Executing tool...")
    payload = ToolRequestPayload(
        tool_name="example_tool",
        parameters={"value": 42}
    )
    
    request = ToolRequest(
        user_id="user123",
        session_id=session_id,
        payload=payload
    )
    
    response = await session_service.process_tool_request(request)
    print(f"   ✅ Tool executed:")
    print(f"      - Status: {response.status}")
    print(f"      - Result: {response.payload.result}")
    
    # 5. Check session for events
    print("\n4. Checking session events...")
    session_data = await session_service.get_session(session_id)
    print(f"   ✅ Session now has {len(session_data['request_ids'])} request(s)")
    
    print("\n" + "=" * 60)
    print("✅ Complete! Full workflow successful")
    print("=" * 60)


if __name__ == "__main__":
    print("\nChoose an example:")
    print("1. Simple session creation")
    print("2. Full workflow (session + tool execution)")
    
    choice = input("\nEnter choice (1 or 2): ").strip()
    
    if choice == "1":
        asyncio.run(create_session_example())
    elif choice == "2":
        asyncio.run(create_and_execute_tool())
    else:
        print("Invalid choice!")
```

### Run the script:
```bash
python scripts/test_create_session.py
```

---

## Comparison

| Method | Pros | Cons | Best For |
|--------|------|------|----------|
| **Swagger UI** | ✅ Easy to use<br>✅ Visual interface<br>✅ Built-in auth | ❌ Manual clicks<br>❌ Not automated | Manual testing, exploration |
| **API Calls** | ✅ Scriptable<br>✅ Integration tests<br>✅ Automation | ❌ Requires token management<br>❌ More setup | CI/CD, automated tests |
| **Python Script** | ✅ Direct access<br>✅ Skip HTTP layer<br>✅ Easy debugging | ❌ Bypasses API validation<br>❌ Firestore access required | Development, unit tests |

---

## Quick Reference

### Endpoints for Session Management

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/tool-sessions/` | POST | Create new session |
| `/tool-sessions/{id}` | GET | Get session details |
| `/tool-sessions/execute` | POST | Execute tool in session |
| `/tool-sessions/{id}/close` | POST | Close session |
| `/tool-sessions/resume` | POST | Resume existing session |
| `/tool-sessions/` | GET | List all sessions |

### Required Fields

**To create session:**
- `casefile_id` (required) - Must exist first
- `user_id` - From auth token
- `session_id` (optional) - For resume

**To execute tool:**
- `session_id` - From create response
- `user_id` - Must match session
- `payload.tool_name` - Which tool to run
- `payload.parameters` - Tool inputs

---

## Troubleshooting

### "Casefile not found"
**Solution:** Create a casefile first using `POST /api/casefiles/create`

### "Session not found"
**Solution:** Check the session_id matches exactly what was returned from create

### "Authentication required"
**Solution:** Get a token from `/auth/token` and add to Authorization header

### "User does not have access"
**Solution:** Ensure user_id in token matches casefile.metadata.created_by

---

## Example Session Lifecycle

```
1. Create Casefile
   POST /api/casefiles/create
   → Returns: casefile_id

2. Create Session
   POST /tool-sessions/?casefile_id={casefile_id}
   → Returns: session_id

3. Execute Tools (repeat as needed)
   POST /tool-sessions/execute?session_id={session_id}
   → Returns: result + events

4. Get Session Details
   GET /tool-sessions/{session_id}
   → Returns: full session with request_ids

5. Close Session (optional)
   POST /tool-sessions/{session_id}/close
   → Returns: status
```

---

## New Architecture Notes

After refactoring, the session structure is:

```
Session (metadata only)
  └─> request_ids: ["uuid-1", "uuid-2"]  ← Just references
  
Firestore:
  /sessions/{session_id}/requests/{request_id}/events/{event_id}
```

So you can:
- **Create session** → Gets session_id
- **Execute tool** → Creates request, adds to session.request_ids
- **View events** → Query Firestore subcollections

All events are ToolEvent objects (not dicts) stored in subcollections! 🎉
