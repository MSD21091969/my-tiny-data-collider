# Fix: Missing `event_type` Field in ToolEvent

## The Problem

**Error:**
```json
{
  "request_id": "a960cf93-a858-4c58-b65f-340ebd56a5f4",
  "status": "failed",
  "payload": {
    "result": {},
    "events": [],
    "session_request_id": "sr_251001_035e39"
  },
  "timestamp": "2025-10-01T10:20:06.304368",
  "error": "1 validation error for ToolEvent\nevent_type\n  Field required [type=missing, input_value={'tool_name': 'example_to...None, 'reasoning': None}, input_type=dict]",
  "metadata": {}
}
```

**Root Cause:**
The `MDSContext.register_event()` method was creating `ToolEvent` objects **without the required `event_type` field**.

## The ToolEvent Model

```python
class ToolEvent(BaseModel):
    event_id: str = Field(default_factory=lambda: ToolEvent._get_id_service_static().new_tool_event_id())
    event_type: str = Field(..., description="Type of event: tool_request_received, tool_execution_started, tool_execution_completed, tool_execution_failed, tool_response_sent")  # ← REQUIRED!
    tool_name: str
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    parameters: Dict[str, Any] = Field(default_factory=dict)
    result_summary: Optional[Dict[str, Any]] = None
    duration_ms: Optional[int] = None
    status: Optional[str] = Field(None, description="Event status: success, error, pending")
    error_message: Optional[str] = Field(None, description="Error message if status is error")
    # ... other fields
```

The `event_type` field uses `Field(...)` which means **NO DEFAULT VALUE** - it's **required**.

## The Bug Location

**File:** `src/pydantic_ai_integration/dependencies.py`

**Old Code (BROKEN):**
```python
@with_persistence
def register_event(self, tool_name: str, parameters: Dict[str, Any], 
                  result_summary: Optional[Dict[str, Any]] = None,
                  duration_ms: Optional[int] = None,
                  chain_context: Optional[Dict[str, Any]] = None) -> str:
    """Register a tool event in the audit trail and return its ID."""
    # ... chain logic ...
    
    # Create the event
    event = ToolEvent(
        tool_name=tool_name,  # ❌ Missing event_type!
        parameters=parameters,
        result_summary=result_summary,
        duration_ms=duration_ms,
        chain_id=chain_id,
        chain_position=chain_position,
        reasoning=chain_context.get("reasoning") if chain_context else None
    )
```

## The Fix

**File:** `src/pydantic_ai_integration/dependencies.py`

**New Code (FIXED):**
```python
@with_persistence
def register_event(self, tool_name: str, parameters: Dict[str, Any], 
                  result_summary: Optional[Dict[str, Any]] = None,
                  duration_ms: Optional[int] = None,
                  chain_context: Optional[Dict[str, Any]] = None,
                  event_type: str = "tool_execution_completed") -> str:  # ✅ Added parameter with default
    """Register a tool event in the audit trail and return its ID.
    
    Args:
        tool_name: Name of the tool being executed
        parameters: Tool parameters
        result_summary: Summary of tool results
        duration_ms: Execution duration in milliseconds
        chain_context: Context for tool chaining
        event_type: Type of event (default: "tool_execution_completed")  # ✅ Documented
    
    Returns:
        Event ID
    """
    # ... chain logic ...
    
    # Create the event
    event = ToolEvent(
        event_type=event_type,  # ✅ Now passed!
        tool_name=tool_name,
        parameters=parameters,
        result_summary=result_summary,
        duration_ms=duration_ms,
        chain_id=chain_id,
        chain_position=chain_position,
        reasoning=chain_context.get("reasoning") if chain_context else None
    )
```

## What Changed

1. **Added `event_type` parameter** to `register_event()` signature with default value `"tool_execution_completed"`
2. **Pass `event_type` to ToolEvent constructor** - now the required field is always populated
3. **Backward compatibility** - existing tool code doesn't need to change (uses default value)

## Why Default to "tool_execution_completed"?

The `MDSContext.register_event()` method is typically called **by tools after they finish execution**, so `"tool_execution_completed"` is the most sensible default.

The **service layer** (`ToolSessionService`) creates the other event types explicitly:
- `tool_request_received` - When request arrives
- `tool_execution_started` - Before tool execution
- `tool_execution_completed` - After successful execution (via tool's `register_event()`)
- `tool_execution_failed` - After failed execution
- `tool_response_sent` - When response is returned

## How Tool Code Uses It

**Tools don't need to change:**
```python
@default_agent.tool
async def example_tool(ctx: Any, value: int) -> Dict[str, Any]:
    mds_context = ctx.deps if hasattr(ctx, 'deps') else ctx
    
    # This now works! Uses default event_type="tool_execution_completed"
    event_id = mds_context.register_event(
        "example_tool",
        {"value": value}
    )
    
    # ... tool logic ...
    
    return result
```

**Service layer can specify event types:**
```python
# In ToolSessionService.process_tool_request()

# Start event
context.register_event(
    tool_name=tool_name,
    parameters=parameters,
    event_type="tool_execution_started"  # ✅ Explicitly specified
)

# Completion event (tools call this with default)
# Tool calls: context.register_event(tool_name, params)
# → Uses default event_type="tool_execution_completed"

# Failure event
context.register_event(
    tool_name=tool_name,
    parameters=parameters,
    event_type="tool_execution_failed",  # ✅ Explicitly specified
    error_message=str(e)
)
```

## Testing the Fix

### 1. Via Swagger UI

1. Start server: `python scripts/main.py`
2. Go to http://localhost:8000/docs
3. Get token from `/auth/token`
4. Create casefile via `/api/casefiles/create`
5. Create session via `/tool-sessions/?casefile_id={casefile_id}`
6. Execute tool via `/tool-sessions/execute?session_id={session_id}`:
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

**Expected Result:**
```json
{
  "request_id": "...",
  "status": "completed",  // ✅ Not "failed"!
  "payload": {
    "result": {
      "original_value": 42,
      "squared": 1764,
      "cubed": 74088,
      "is_even": true,
      "timestamp": "2025-10-01T..."
    },
    "events": [],
    "session_request_id": "sr_251001_..."
  },
  "timestamp": "2025-10-01T...",
  "error": null  // ✅ No error!
}
```

### 2. Via Python Tests

```bash
python -m pytest tests/test_tool_session_service.py -v
```

All tests should pass now that `event_type` is properly populated.

### 3. Via Script

```bash
python scripts/test_create_session.py
# Choose option 2 (Full workflow)
```

Should complete successfully without validation errors.

## Impact Analysis

### Files Modified:
- ✅ `src/pydantic_ai_integration/dependencies.py` - Added `event_type` parameter to `register_event()`

### Files NOT Modified (backward compatible):
- ✅ `src/pydantic_ai_integration/tools/enhanced_example_tools.py` - Uses default
- ✅ `src/pydantic_ai_integration/tools/example_tools.py` - Uses default
- ✅ `src/pydantic_ai_integration/tools/agent_aware_tools.py` - Uses default
- ✅ `src/communicationservice/service.py` - Uses default

### Affected Functionality:
- ✅ Tool execution via `/tool-sessions/execute` endpoint
- ✅ Direct tool calls from PydanticAI agents
- ✅ MDSContext audit trail tracking
- ✅ Event storage in Firestore subcollections

## Verification Checklist

- [x] `event_type` parameter added to `register_event()` signature
- [x] Default value `"tool_execution_completed"` provides backward compatibility
- [x] `event_type` passed to `ToolEvent` constructor
- [x] Server restarts successfully (reload works)
- [ ] Test via Swagger UI (pending user verification)
- [ ] All pytest tests pass (pending)
- [ ] No validation errors in logs (pending)

## Event Types Reference

Valid `event_type` values:
1. **`tool_request_received`** - Request arrived at service layer
2. **`tool_execution_started`** - Tool execution beginning
3. **`tool_execution_completed`** - Tool finished successfully (DEFAULT for `register_event()`)
4. **`tool_execution_failed`** - Tool execution failed with error
5. **`tool_response_sent`** - Response sent back to client

## Next Steps

1. ✅ **Fix applied** - `event_type` now passed to ToolEvent
2. 🔄 **Server restarted** - Changes live at http://localhost:8000
3. ⏳ **Test via Swagger** - Execute the same request that failed before
4. ⏳ **Verify logs** - No more validation errors
5. ⏳ **Run test suite** - Confirm all tests pass

---

## Summary

**Problem:** Missing required field `event_type` in ToolEvent  
**Solution:** Added `event_type` parameter with default value to `register_event()`  
**Result:** ✅ Backward compatible fix, no changes needed in tool code  
**Status:** 🟢 **FIXED** - Ready for testing
