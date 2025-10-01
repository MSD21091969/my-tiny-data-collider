# Tool Engineering Foundation - MVP Strategy

**Project:** MDS Objects API  
**Date:** October 2, 2025  
**Status:** 🎯 Strategy Document  
**Purpose:** Define MVP architecture for declarative, test-driven tool development

---

## Executive Summary

**Vision:** Create a declarative tool engineering system where new tools can be mass-produced through:
1. **Factory Pattern** - Single configuration generates tool implementation, tests, and documentation
2. **AI Supervision** - AI analyzes model relationships and suggests optimal tool patterns
3. **CI/CD Integration** - Automated testing validates tool behavior before deployment
4. **Data-Driven** - Casefiles serve as context containers for tool execution and data storage

**Current State:**
- ✅ Excellent foundation: `tool_definition.py` has clear metadata/business-logic separation
- ✅ Clean registration: `@register_mds_tool` decorator provides single source of truth
- ✅ Validation infrastructure: Pydantic models enforce guardrails
- ⚠️ Gap: Tools are manually written, no factory/template system
- ⚠️ Gap: No automated test generation from tool definitions
- ⚠️ Gap: Casefile data model is generic (needs tool-specific schemas)

---

## Critical Analysis

### ✅ What's Working Well

#### 1. **`tool_definition.py` - Excellent Architecture**

**Strengths:**
- Clear separation: `ToolMetadata` (what) vs `ToolBusinessRules` (when/where) vs implementation (how)
- Comprehensive: Covers discovery, validation, authorization, execution
- Extensible: Easy to add new fields without breaking existing tools
- OpenAPI-ready: `get_openapi_schema()` auto-generates docs

**Field Purpose Clarity:**
```python
# METADATA (immutable, descriptive)
metadata: ToolMetadata  # name, description, version, tags, category

# BUSINESS LOGIC (mutable, policy)
business_rules: ToolBusinessRules  # enabled, permissions, rate_limits, timeout

# EXECUTION (runtime, functional)
implementation: Callable  # The actual async function
params_model: Type[BaseModel]  # Pydantic validator

# AUDIT (temporal, tracking)
registered_at: str  # When tool was registered
```

**Verdict:** ✅ **Keep as-is. This is your single source of truth.**

#### 2. **`unified_example_tools.py` - Clean Pattern**

**Strengths:**
- Decorator-driven: `@register_mds_tool` is declarative
- Validated upfront: Pydantic models enforce guardrails before execution
- Context-aware: `MDSContext` provides user_id, session_id, casefile_id
- Audit trail: Automatic event registration

**Pattern:**
```python
# 1. Define params model (guardrails)
class MyToolParams(BaseModel):
    value: int = Field(..., ge=0, le=100)  # GUARDRAILS

# 2. Register with decorator (metadata + business rules)
@register_mds_tool(
    name="my_tool",  # METADATA
    required_permissions=["tools:write"],  # BUSINESS LOGIC
    params_model=MyToolParams  # EXECUTION
)
async def my_tool(ctx: MDSContext, value: int) -> Dict[str, Any]:
    # Implementation here (validation already done!)
    pass
```

**Verdict:** ✅ **This is the template for all new tools. Don't change the pattern.**

#### 3. **`tool_params.py` - Consistent Structure**

**Strengths:**
- One class per tool (clear boundaries)
- Examples included (`json_schema_extra`)
- Guardrails explicit (`ge=`, `le=`, `min_length=`)

**Verdict:** ✅ **Good practice. Keep one file per tool category, or split by domain.**

---

### ⚠️ Critical Gaps

#### **Gap 1: No Tool Factory**

**Problem:** Each tool requires manual coding:
- Write `MyToolParams` class
- Write `@register_mds_tool` decorator
- Write `async def my_tool()` implementation
- Write tests manually
- Write documentation manually

**Impact:** Slow tool development. Can't "mass produce" tools.

#### **Gap 2: No Test Generation**

**Problem:** Tests are disconnected from tool definitions.

**Current state:**
- Tool has `ToolParameterDef` with constraints
- Tests don't automatically verify those constraints
- No automated test generation from `params_model`

**Impact:** Easy to miss edge cases, constraints not validated.

#### **Gap 3: Casefile Data Model is Generic**

**Problem:** `CasefileModel.resources` is just `Dict[str, List[ResourceReference]]`.

**Current:**
```python
resources: Dict[str, List[ResourceReference]] = Field(...)
# Generic! No schema enforcement.
```

**Needed:**
```python
# Tool-specific schemas
gmail_messages: List[GmailMessageSchema]
drive_files: List[DriveFileSchema]
sheets_data: List[SheetDataSchema]
```

**Impact:** Can't validate data structure, hard to query, no type safety.

---

## MVP Strategy: Three-Phase Approach

### Phase 1: Tool Factory (Declarative Tool Generation) 🎯 **START HERE**

**Goal:** Generate tool implementation, tests, and docs from a single YAML/JSON config.

**Architecture:**
```
config/tools/
  ├── gmail_tools.yaml      # Tool definitions
  ├── drive_tools.yaml
  └── sheets_tools.yaml

scripts/
  └── generate_tools.py     # Factory that reads YAML → generates code

generated/
  ├── tools/
  │   ├── gmail_tools.py   # Auto-generated tool implementations
  │   └── drive_tools.py
  ├── params/
  │   ├── gmail_params.py  # Auto-generated param models
  │   └── drive_params.py
  └── tests/
      ├── test_gmail_tools.py  # Auto-generated tests
      └── test_drive_tools.py
```

**YAML Config Example:**
```yaml
# config/tools/gmail_tools.yaml
tools:
  - name: gmail_list_messages
    display_name: "List Gmail Messages"
    description: "List messages from Gmail inbox"
    category: google_workspace
    version: "1.0.0"
    tags: [gmail, messages, list]
    
    # BUSINESS RULES
    requires_auth: true
    required_permissions: [gmail:read]
    requires_casefile: true
    timeout_seconds: 30
    
    # PARAMETERS
    parameters:
      - name: max_results
        type: integer
        required: false
        default: 10
        min_value: 1
        max_value: 100
        description: "Maximum number of messages to return"
      
      - name: query
        type: string
        required: false
        default: ""
        max_length: 500
        description: "Gmail search query"
    
    # IMPLEMENTATION TEMPLATE
    implementation_template: gmail_api_call
    api_method: gmail.users.messages.list
    response_mapping:
      messages: messages
      result_size_estimate: resultSizeEstimate
    
    # DATA STORAGE
    stores_in_casefile: true
    casefile_resource_type: gmail_messages
    casefile_schema: GmailMessageSchema
```

**Factory Output:**

1. **Generated Tool (`generated/tools/gmail_tools.py`):**
```python
from pydantic import BaseModel, Field
from typing import Dict, Any
from ...tool_decorator import register_mds_tool
from ...dependencies import MDSContext
from .gmail_client import GmailClient  # Pre-written API wrapper

class GmailListMessagesParams(BaseModel):
    """Auto-generated params for gmail_list_messages."""
    max_results: int = Field(10, ge=1, le=100, description="Maximum number of messages to return")
    query: str = Field("", max_length=500, description="Gmail search query")

@register_mds_tool(
    name="gmail_list_messages",
    display_name="List Gmail Messages",
    description="List messages from Gmail inbox",
    category="google_workspace",
    version="1.0.0",
    tags=["gmail", "messages", "list"],
    requires_auth=True,
    required_permissions=["gmail:read"],
    requires_casefile=True,
    timeout_seconds=30,
    params_model=GmailListMessagesParams,
)
async def gmail_list_messages(
    ctx: MDSContext,
    max_results: int = 10,
    query: str = ""
) -> Dict[str, Any]:
    """Auto-generated implementation for gmail_list_messages."""
    event_id = ctx.register_event("gmail_list_messages", {"max_results": max_results, "query": query})
    
    # Use pre-written API client
    client = GmailClient(ctx.user_id)
    result = await client.list_messages(max_results=max_results, query=query)
    
    # Store in casefile if configured
    if ctx.casefile_id:
        await ctx.store_casefile_data(
            resource_type="gmail_messages",
            data=result["messages"],
            schema=GmailMessageSchema
        )
    
    # Update audit trail
    if ctx.tool_events:
        last_event = ctx.tool_events[-1]
        last_event.result_summary = {"status": "success", "message_count": len(result["messages"])}
        last_event.status = "success"
    
    return result
```

2. **Generated Tests (`generated/tests/test_gmail_tools.py`):**
```python
import pytest
from unittest.mock import AsyncMock, patch
from src.pydantic_ai_integration.dependencies import MDSContext
from generated.tools.gmail_tools import gmail_list_messages, GmailListMessagesParams

@pytest.mark.asyncio
async def test_gmail_list_messages_validates_max_results():
    """Test that max_results constraint is enforced."""
    with pytest.raises(ValueError, match="greater than or equal to 1"):
        GmailListMessagesParams(max_results=0)  # Below minimum
    
    with pytest.raises(ValueError, match="less than or equal to 100"):
        GmailListMessagesParams(max_results=101)  # Above maximum

@pytest.mark.asyncio
async def test_gmail_list_messages_validates_query_length():
    """Test that query length constraint is enforced."""
    with pytest.raises(ValueError, match="ensure this value has at most 500 characters"):
        GmailListMessagesParams(query="a" * 501)  # Too long

@pytest.mark.asyncio
@patch('generated.tools.gmail_tools.GmailClient')
async def test_gmail_list_messages_success(mock_client):
    """Test successful message listing."""
    # Setup
    mock_client_instance = AsyncMock()
    mock_client_instance.list_messages.return_value = {
        "messages": [{"id": "msg1"}, {"id": "msg2"}],
        "resultSizeEstimate": 2
    }
    mock_client.return_value = mock_client_instance
    
    ctx = MDSContext(user_id="test_user", session_id="test_session")
    
    # Execute
    result = await gmail_list_messages(ctx, max_results=10, query="")
    
    # Assert
    assert result["messages"] == [{"id": "msg1"}, {"id": "msg2"}]
    assert mock_client_instance.list_messages.called_once_with(max_results=10, query="")
```

**Benefits:**
- ✅ Write YAML, get tool + tests + docs
- ✅ Constraints defined once, enforced everywhere
- ✅ Consistent patterns across all tools
- ✅ Easy to add 50+ Google Workspace tools

**Next Steps:**
1. Create `scripts/generate_tools.py` factory script
2. Define YAML schema for tool configs
3. Create templates for common patterns (API calls, data transforms, etc.)
4. Add validation: Factory validates YAML before generating code

---

### Phase 2: AI-Supervised Tool Engineering 🤖

**Goal:** AI analyzes tool definitions and suggests optimal implementations.

**Architecture:**
```
AI Workflow:
1. Developer writes YAML config
2. AI reads all Pydantic models (tool_definition.py, casefile models, etc.)
3. AI suggests:
   - Parameter constraints based on model relationships
   - Test cases based on edge cases
   - Error handling patterns
   - Casefile schema optimizations
4. Developer reviews and approves
5. Factory generates code with AI suggestions
```

**AI Analysis Example:**

**Input:** Developer writes:
```yaml
tools:
  - name: create_casefile_with_gmail
    parameters:
      - name: title
        type: string
      - name: gmail_message_ids
        type: array
```

**AI Analysis:**
```
🤖 AI Suggestions:

1. PARAMETER CONSTRAINTS:
   - title: Should match CasefileMetadata.title constraints
     Suggested: min_length=1, max_length=200
   
   - gmail_message_ids: Should validate Gmail message ID format
     Suggested: pattern="^[0-9a-f]+$", max_items=100

2. MODEL RELATIONSHIPS:
   - This tool creates a CasefileModel
   - gmail_message_ids should be stored as ResourceReference objects
   - Suggested schema:
     resources.gmail_messages = [
       ResourceReference(
         resource_id=msg_id,
         resource_type="gmail_message",
         metadata={"fetched_at": timestamp}
       )
     ]

3. BUSINESS RULES:
   - Similar tool 'create_casefile' has required_permissions=["casefiles:write"]
   - Suggest: required_permissions=["casefiles:write", "gmail:read"]
   - Suggest: requires_casefile=False (this tool creates the casefile)

4. TEST CASES:
   - Empty gmail_message_ids array
   - Duplicate message IDs
   - Invalid message ID format
   - Title too long/empty
   - User doesn't have gmail:read permission

5. ERROR HANDLING:
   - Gmail API might return 404 for invalid message ID
   - Suggest: Validate all IDs exist before creating casefile
   - Suggest: Partial success pattern (create casefile, log failures)
```

**Benefits:**
- ✅ AI catches constraint mismatches
- ✅ AI suggests test cases humans forget
- ✅ AI enforces consistency with existing patterns
- ✅ Faster development with fewer bugs

**Implementation:**
- Use Claude/GPT-4 with full codebase context
- Feed AI: All Pydantic models + existing tool patterns
- AI outputs: Validated YAML + test suggestions
- Human approves before code generation

---

### Phase 3: Declarative Data Schemas (Casefile Evolution) 📊

**Goal:** Casefile becomes a strongly-typed data container with tool-specific schemas.

**Current Problem:**
```python
# Generic - no validation!
casefile.resources = {
    "gmail_messages": [
        {"resource_id": "msg1", "resource_type": "gmail_message", "metadata": {...}}
    ]
}
```

**Proposed Solution:**
```python
# Strongly typed!
from pydantic_models.workspace.gmail import GmailMessageSchema
from pydantic_models.workspace.drive import DriveFileSchema

casefile.gmail_data = CasefileGmailData(
    messages=[
        GmailMessageSchema(
            id="msg1",
            thread_id="thread1",
            subject="Important",
            from_email="sender@example.com",
            to_emails=["recipient@example.com"],
            body="...",
            labels=["INBOX", "IMPORTANT"],
            received_at="2025-10-02T10:00:00Z",
            has_attachments=True,
            attachments=[
                GmailAttachmentSchema(
                    filename="document.pdf",
                    mime_type="application/pdf",
                    size_bytes=12345,
                    attachment_id="att_123"
                )
            ]
        )
    ],
    threads=[...],
    labels=[...],
    last_sync_token="sync_token_123",
    synced_at="2025-10-02T10:05:00Z"
)

casefile.drive_data = CasefileDriveData(
    files=[
        DriveFileSchema(
            id="file1",
            name="Report.docx",
            mime_type="application/vnd.google-apps.document",
            parents=["folder1"],
            owners=["owner@example.com"],
            created_time="2025-10-01T09:00:00Z",
            modified_time="2025-10-02T08:00:00Z",
            size_bytes=45678,
            web_view_link="https://docs.google.com/..."
        )
    ],
    folders=[...],
    shared_drives=[...]
)
```

**Architecture:**
```
src/pydantic_models/workspace/
  ├── __init__.py
  ├── gmail.py          # GmailMessageSchema, GmailThreadSchema, etc.
  ├── drive.py          # DriveFileSchema, DriveFolderSchema, etc.
  ├── sheets.py         # SheetSchema, SheetDataSchema, etc.
  ├── calendar.py       # CalendarEventSchema, etc.
  └── docs.py           # GoogleDocSchema, etc.

src/pydantic_models/casefile/
  ├── models.py         # Base CasefileModel
  └── workspace_data.py # CasefileGmailData, CasefileDriveData, etc.
```

**Benefits:**
- ✅ **Type safety:** Pydantic validates all data
- ✅ **Queryable:** Can search casefile.gmail_data.messages.filter(label="IMPORTANT")
- ✅ **Versioned:** Schema changes are explicit
- ✅ **Documented:** OpenAPI auto-generates schemas
- ✅ **AI-friendly:** AI knows exact structure for analysis

**Migration Path:**
1. Create workspace schemas (gmail.py, drive.py, etc.)
2. Add `CasefileWorkspaceData` model
3. Tools write to typed fields instead of generic `resources`
4. Maintain backward compatibility: Keep `resources` for 2 versions
5. Deprecation notice: "Use typed fields, `resources` will be removed in v3.0"

---

## Recommended MVP Roadmap

### Week 1: Tool Factory Foundation
**Goal:** Generate 1 tool from YAML config

**Tasks:**
1. Design YAML schema for tool definitions ✅
2. Create `scripts/generate_tools.py` factory script
3. Create templates:
   - `templates/tool_template.py.jinja2` (tool implementation)
   - `templates/params_template.py.jinja2` (params model)
   - `templates/test_template.py.jinja2` (tests)
4. Generate 1 simple tool (e.g., `echo_tool`) from YAML
5. Validate generated code runs and tests pass

**Success Criteria:**
- ✅ YAML → Generated code → Tests pass
- ✅ Generated tool registers correctly
- ✅ Generated tests validate all constraints

### Week 2: Google Workspace Mock Tools
**Goal:** 10 mock Google Workspace tools for testing

**Why Mock First:**
- Don't need real Google API credentials
- Fast iteration on patterns
- Validate factory works for real use cases

**Tools to Generate:**
```yaml
# config/tools/google_workspace_mocks.yaml
tools:
  - gmail_list_messages
  - gmail_get_message
  - gmail_send_message
  - drive_list_files
  - drive_get_file
  - drive_create_file
  - sheets_get_values
  - sheets_update_values
  - calendar_list_events
  - calendar_create_event
```

**Each tool:**
- Returns mock data (realistic structure)
- Validates parameters (real constraints)
- Stores data in casefile (prepares for real implementation)
- Has 5-10 generated tests

**Success Criteria:**
- ✅ 10 tools generated from YAML
- ✅ All tests pass (50-100 tests total)
- ✅ Tools discoverable via API
- ✅ Mock data stored in casefiles

### Week 3: AI Analysis Integration
**Goal:** AI suggests improvements to tool definitions

**Tasks:**
1. Create AI prompt template with:
   - All Pydantic models
   - Existing tool patterns
   - New tool YAML
2. AI analyzes and suggests:
   - Parameter constraints
   - Test cases
   - Error handling
   - Schema improvements
3. Developer reviews and approves
4. Factory generates with AI suggestions

**Success Criteria:**
- ✅ AI correctly identifies constraint mismatches
- ✅ AI suggests 5+ test cases per tool
- ✅ AI suggestions improve code quality

### Week 4: Real Google Workspace Integration
**Goal:** Replace mocks with real API calls

**Tasks:**
1. Create Google Workspace API client wrappers
2. Add OAuth2 authentication
3. Replace mock implementations with real API calls
4. Add error handling (rate limits, API errors)
5. Test with real Google Workspace data

**Success Criteria:**
- ✅ 10 tools work with real Google APIs
- ✅ OAuth2 flow works
- ✅ Error handling tested
- ✅ Data stored in casefiles correctly

---

## Alternative Approaches (Critical Review)

### Alternative 1: Keep Manual Tool Development ❌

**Pros:**
- Simple, no factory complexity
- Full control over each tool

**Cons:**
- Slow: Can't mass-produce tools
- Inconsistent: Each developer uses different patterns
- Error-prone: Easy to forget tests or constraints
- Doesn't scale: Need 100+ tools eventually

**Verdict:** ❌ **Reject. Too slow for scale.**

---

### Alternative 2: Pure Code Generation (No YAML) ⚠️

**Idea:** AI generates Python code directly from natural language prompts.

**Example:**
```
Prompt: "Create a tool that lists Gmail messages with pagination"
AI Output: Complete Python file with tool + tests
```

**Pros:**
- No YAML schema to maintain
- Very fast prototyping

**Cons:**
- No single source of truth (YAML serves as config)
- Hard to version control (diffs are Python code, not config)
- Consistency issues (AI might use different patterns)
- Debugging is harder (AI-generated code varies)

**Verdict:** ⚠️ **Hybrid approach:**
- Use YAML as source of truth (versioned, consistent)
- AI helps generate YAML from natural language
- Factory generates code from YAML (deterministic)

---

### Alternative 3: Dynamic Tool Registration (No Code Generation) ⚠️

**Idea:** Tools are YAML only, executed dynamically at runtime.

**Example:**
```yaml
tools:
  - name: gmail_list_messages
    implementation_type: api_call
    api:
      method: GET
      url: "https://gmail.googleapis.com/gmail/v1/users/me/messages"
      params:
        maxResults: "{{max_results}}"
        q: "{{query}}"
    response_mapping:
      messages: data.messages
```

**Pros:**
- No code generation needed
- Tools can be updated without deployment
- Very flexible

**Cons:**
- Complex template engine needed
- Hard to debug (no Python code to inspect)
- Limited: Can't express complex logic
- Performance: Runtime interpretation overhead

**Verdict:** ⚠️ **Hybrid approach:**
- Use for simple API-call tools (80% of tools)
- Generate Python code for complex tools (20%)
- Start with code generation, add dynamic execution later

---

## Data Strategy: Casefile as Context Container

### Current State
```python
class CasefileModel(BaseModel):
    id: str
    metadata: CasefileMetadata  # title, description, tags, timestamps
    resources: Dict[str, List[ResourceReference]]  # Generic!
    session_ids: List[str]
    notes: Optional[str]
```

**Problems:**
1. `resources` is untyped (just `Dict[str, List]`)
2. No validation of resource structure
3. Hard to query (need to parse dict keys)
4. No relationship modeling (e.g., "which Gmail messages reference which Drive files?")

### Proposed Structure

```python
class CasefileModel(BaseModel):
    """Enhanced casefile with typed data containers."""
    
    # Core metadata (unchanged)
    id: str
    metadata: CasefileMetadata
    session_ids: List[str]
    notes: Optional[str]
    
    # WORKSPACE DATA (strongly typed)
    gmail_data: Optional[CasefileGmailData] = None
    drive_data: Optional[CasefileDriveData] = None
    sheets_data: Optional[CasefileSheetsData] = None
    calendar_data: Optional[CasefileCalendarData] = None
    
    # GENERIC RESOURCES (backward compatibility)
    resources: Dict[str, List[ResourceReference]] = Field(
        default_factory=dict,
        deprecated=True,  # Mark for removal
        description="DEPRECATED: Use typed data fields instead"
    )
    
    # RELATIONSHIPS (tracks connections between data)
    relationships: List[DataRelationship] = Field(
        default_factory=list,
        description="Tracks relationships between resources"
    )

class CasefileGmailData(BaseModel):
    """Gmail data container within a casefile."""
    messages: List[GmailMessageSchema] = Field(default_factory=list)
    threads: List[GmailThreadSchema] = Field(default_factory=list)
    labels: List[GmailLabelSchema] = Field(default_factory=list)
    
    # Sync metadata
    last_sync_token: Optional[str] = None
    synced_at: Optional[str] = None
    sync_status: str = "idle"  # idle, syncing, error
    
    @computed_field
    def unread_count(self) -> int:
        return sum(1 for msg in self.messages if "UNREAD" in msg.labels)

class GmailMessageSchema(BaseModel):
    """Schema for a Gmail message stored in casefile."""
    id: str = Field(..., description="Gmail message ID")
    thread_id: str = Field(..., description="Gmail thread ID")
    subject: str = Field(..., description="Message subject")
    from_email: str = Field(..., description="Sender email")
    to_emails: List[str] = Field(..., description="Recipient emails")
    cc_emails: List[str] = Field(default_factory=list)
    bcc_emails: List[str] = Field(default_factory=list)
    body_text: Optional[str] = None
    body_html: Optional[str] = None
    labels: List[str] = Field(default_factory=list)
    received_at: str = Field(..., description="ISO 8601 timestamp")
    snippet: str = Field(..., description="Short preview")
    has_attachments: bool = False
    attachments: List[GmailAttachmentSchema] = Field(default_factory=list)
    
    # Metadata
    added_to_casefile_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    fetched_by_tool: str = Field(..., description="Tool that fetched this")

class DataRelationship(BaseModel):
    """Tracks relationship between two resources."""
    source_type: str  # e.g., "gmail_message"
    source_id: str    # e.g., "msg_123"
    target_type: str  # e.g., "drive_file"
    target_id: str    # e.g., "file_456"
    relationship_type: str  # e.g., "mentions", "attached_in", "created_from"
    confidence: float = 1.0  # 0.0-1.0 (for AI-detected relationships)
    detected_by: str  # e.g., "gmail_list_messages", "ai_analyzer"
    detected_at: str = Field(default_factory=lambda: datetime.now().isoformat())
```

**Benefits:**
1. **Type Safety:** Pydantic validates all data
2. **Queryable:** `casefile.gmail_data.messages.filter(lambda m: "IMPORTANT" in m.labels)`
3. **Relationships:** Track which Gmail mentions which Drive file
4. **AI-Friendly:** AI can analyze relationships and suggest actions
5. **Versioned:** Schema changes are explicit migrations

**Example Usage:**
```python
# Tool stores Gmail messages
@register_mds_tool(name="gmail_list_messages", ...)
async def gmail_list_messages(ctx: MDSContext, query: str) -> Dict[str, Any]:
    messages = await gmail_client.list_messages(query=query)
    
    # Store in casefile (strongly typed!)
    if ctx.casefile_id:
        casefile = await get_casefile(ctx.casefile_id)
        
        if not casefile.gmail_data:
            casefile.gmail_data = CasefileGmailData()
        
        for msg in messages:
            gmail_msg = GmailMessageSchema(
                id=msg["id"],
                thread_id=msg["threadId"],
                subject=msg["subject"],
                from_email=msg["from"],
                to_emails=msg["to"],
                body_text=msg["body"],
                labels=msg["labelIds"],
                received_at=msg["internalDate"],
                snippet=msg["snippet"],
                has_attachments=len(msg.get("attachments", [])) > 0,
                attachments=[
                    GmailAttachmentSchema(**att)
                    for att in msg.get("attachments", [])
                ],
                fetched_by_tool="gmail_list_messages"
            )
            casefile.gmail_data.messages.append(gmail_msg)
        
        # Update sync status
        casefile.gmail_data.synced_at = datetime.now().isoformat()
        casefile.gmail_data.sync_status = "completed"
        
        await update_casefile(casefile)
    
    return {"messages": messages, "stored_in_casefile": True}

# Later: Query casefile data
casefile = await get_casefile("cf_251002_abc123")
important_unread = [
    msg for msg in casefile.gmail_data.messages
    if "IMPORTANT" in msg.labels and "UNREAD" in msg.labels
]
```

---

## Open Questions for User Decision

### 1. **Tool Factory Implementation Priority** 🎯

**Question:** Start with Python Jinja2 templates or YAML-only dynamic execution?

**Option A: Jinja2 Templates (Generate Python)**
- ✅ Full Python features, easy debugging
- ✅ Type checking with Pylance/MyPy
- ❌ More complex, need template maintenance

**Option B: YAML-Only Dynamic (Runtime interpreter)**
- ✅ Simpler, no code generation
- ✅ Can update tools without deployment
- ❌ Limited expressiveness, harder debugging

**Recommendation:** Start with Option A (Python generation), add Option B later for simple tools.

---

### 2. **AI Integration Depth** 🤖

**Question:** How much AI supervision do you want?

**Option A: AI Suggests (Human Approves)**
- Human writes YAML → AI suggests improvements → Human reviews → Factory generates
- ✅ Human control, AI assists
- ❌ Slower (human approval step)

**Option B: AI Generates (Human Spot-Checks)**
- Human gives prompt → AI generates YAML + code → Human spot-checks → Deploy
- ✅ Very fast, AI does heavy lifting
- ❌ Need strong validation, risk of AI errors

**Option C: Manual (No AI)**
- Human writes YAML → Factory generates → Tests validate
- ✅ Simple, deterministic
- ❌ Slower, no AI insights

**Recommendation:** Start with Option C (manual), add Option A (AI assists) in Week 3.

---

### 3. **Casefile Data Migration** 📊

**Question:** Migrate existing casefiles or start fresh?

**Option A: Big Bang Migration**
- Stop system → Convert all `resources` → Start with new schema
- ✅ Clean, no backward compatibility
- ❌ Risky, requires downtime

**Option B: Gradual Migration**
- New tools write to typed fields
- Old data stays in `resources`
- Read from both, write to typed
- After 6 months, deprecate `resources`
- ✅ No downtime, safe
- ❌ Complexity, maintain two paths

**Option C: Fresh Start**
- New casefile schema, old casefiles unchanged
- ✅ Clean, no migration risk
- ❌ Lose old data

**Recommendation:** Option B (gradual migration). Mark `resources` as deprecated, give 2 versions notice.

---

### 4. **Test Strategy** ✅

**Question:** How comprehensive should auto-generated tests be?

**Option A: Basic Coverage**
- Test param validation (min/max/length)
- Test happy path
- ~5 tests per tool

**Option B: Comprehensive Coverage**
- Param validation
- Happy path
- Edge cases (empty, max values)
- Error cases (API failures)
- Permission checks
- Casefile storage
- ~15 tests per tool

**Option C: AI-Generated Tests**
- AI analyzes tool → Suggests test cases → Generate tests
- ✅ Catches edge cases humans miss
- ❌ Need AI integration

**Recommendation:** Start Option A, add Option C (AI-generated) in Week 3.

---

## Next Immediate Actions (This Week)

### Action 1: Validate YAML Schema Design ✅
**Owner:** You (review) + AI (implement)
**Time:** 2 hours
**Output:** `config/tool_schema.yaml` with example

```yaml
# config/tool_schema.yaml
tool_definition_schema:
  name: string (required, unique)
  display_name: string (optional)
  description: string (required)
  category: string (required)
  version: semver (default "1.0.0")
  tags: list[string] (default [])
  
  business_rules:
    enabled: bool (default true)
    requires_auth: bool (default true)
    required_permissions: list[string] (default [])
    requires_casefile: bool (default false)
    timeout_seconds: int (default 30)
    max_retries: int (default 0)
  
  parameters:
    - name: string (required)
      type: string|integer|float|boolean|array|object (required)
      required: bool (default false)
      default: any (optional)
      description: string (optional)
      
      # Constraints (based on type)
      min_value: number (for numeric types)
      max_value: number (for numeric types)
      min_length: int (for string/array types)
      max_length: int (for string/array types)
      pattern: regex (for string types)
      enum_values: list (for any type)
      
  implementation:
    template: string (required) # e.g., "api_call", "data_transform", "custom"
    # Template-specific fields...
```

**Decision Needed:** Approve YAML schema structure.

---

### Action 2: Create Factory Script Skeleton ✅
**Owner:** AI implements
**Time:** 3 hours
**Output:** `scripts/generate_tools.py`

```python
# scripts/generate_tools.py
"""Tool factory that generates code from YAML configs."""
import yaml
from pathlib import Path
from jinja2 import Environment, FileSystemLoader

def load_tool_config(yaml_path: Path) -> dict:
    """Load and validate tool YAML."""
    pass

def generate_params_model(tool_config: dict) -> str:
    """Generate Pydantic params model."""
    pass

def generate_tool_implementation(tool_config: dict) -> str:
    """Generate tool function."""
    pass

def generate_tests(tool_config: dict) -> str:
    """Generate pytest tests."""
    pass

def main():
    """Generate all tools from config/tools/*.yaml."""
    pass

if __name__ == "__main__":
    main()
```

---

### Action 3: Create First Template ✅
**Owner:** AI implements
**Time:** 2 hours
**Output:** `templates/tool_template.py.jinja2`

```python
# templates/tool_template.py.jinja2
"""Auto-generated tool: {{ tool.name }}"""
from pydantic import BaseModel, Field
from typing import Dict, Any
from ...tool_decorator import register_mds_tool
from ...dependencies import MDSContext

class {{ tool.name | capitalize }}Params(BaseModel):
    """Parameters for {{ tool.name }}."""
    {% for param in tool.parameters %}
    {{ param.name }}: {{ param.python_type }} = Field(
        {% if param.required %}...,{% else %}{{ param.default }},{% endif %}
        {% if param.min_value %}ge={{ param.min_value }},{% endif %}
        {% if param.max_value }}le={{ param.max_value }},{% endif %}
        description="{{ param.description }}"
    )
    {% endfor %}

@register_mds_tool(
    name="{{ tool.name }}",
    description="{{ tool.description }}",
    category="{{ tool.category }}",
    # ... more fields ...
    params_model={{ tool.name | capitalize }}Params,
)
async def {{ tool.name }}(
    ctx: MDSContext,
    {% for param in tool.parameters %}
    {{ param.name }}: {{ param.python_type }}{% if not param.required %} = {{ param.default }}{% endif %}{% if not loop.last %},{% endif %}
    {% endfor %}
) -> Dict[str, Any]:
    """{{ tool.description }}"""
    # Implementation here
    pass
```

---

### Action 4: Test with Echo Tool ✅
**Owner:** You + AI
**Time:** 1 hour
**Output:** Working generated tool

```bash
# Create config
cat > config/tools/echo_tool.yaml << EOF
name: echo_tool
description: "Echoes input back with metadata"
category: examples
parameters:
  - name: message
    type: string
    required: true
    min_length: 1
    max_length: 500
    description: "Message to echo"
EOF

# Generate tool
python scripts/generate_tools.py

# Verify generated files
ls generated/tools/echo_tool.py
ls generated/tests/test_echo_tool.py

# Run tests
pytest generated/tests/test_echo_tool.py -v
```

---

## Summary & Critical Decision Points

### ✅ Keep As-Is (Excellent Foundation)
1. `tool_definition.py` - Perfect metadata/business-logic separation
2. `@register_mds_tool` decorator - Clean registration pattern
3. Pydantic param models - Strong validation

### 🎯 Build Next (MVP)
1. **Tool Factory** - Generate tools from YAML configs
2. **10 Mock Google Workspace Tools** - Test factory at scale
3. **Typed Casefile Data** - Strongly-typed Gmail/Drive/Sheets schemas

### 🤖 Add Later (Enhancements)
1. AI-supervised tool generation
2. Dynamic YAML-only execution
3. Advanced relationship modeling

### ❌ Don't Do
1. Manual tool development (too slow)
2. Pure AI code generation without YAML (no source of truth)
3. Big-bang casefile migration (too risky)

---

## Conclusion

**Your codebase has an excellent foundation.** The `tool_definition.py` architecture is sound, the decorator pattern is clean, and Pydantic provides strong guardrails.

**The critical gap is scale:** You can't manually write 100+ tools. The factory pattern solves this by making tool development declarative and repeatable.

**Start small:** Get the factory working for 1 tool this week. Then scale to 10 mock Google Workspace tools next week. By Week 4, you'll have a production-ready system that can mass-produce tools.

**Data strategy:** Evolve casefiles to strongly-typed containers. This enables queryability, relationships, and AI analysis.

**Your MVP path is clear and achievable.** Focus on the factory first. Everything else builds on that foundation.

---

**Ready to proceed?** Which action do you want to tackle first?
