# Tool Engineering Technical Analysis

**Date:** October 6, 2025  
**Status:** Foundation Phase Analysis

---

## Executive Summary

**Architecture Quality:** Excellent - YAML-driven tools, unified decorator, proper envelopes, audit trail  
**Current Gap:** Only 11 service methods available for tools  
**Required:** 20-30 service methods before serious tool engineering  
**Timeline:** 3-4 weeks to establish foundation

---

## Architecture Overview

### Data Flow

```
YAML Definition → Tool Factory → Generated Tool → @register_mds_tool → MANAGED_TOOLS
                                                                              ↓
User Request → API → Service → Repository → Firestore
                ↓
        ToolSessionService.process_tool_request()
                ↓
        Tool Execution (validates params, runs implementation)
                ↓
        ToolEvent → ToolSession → Casefile (audit trail)
```

### Core Components

**1. Tool Definition System**
- `config/tool_schema_v2.yaml` - Complete YAML schema
- `config/tools/{domain}/{subdomain}/*.yaml` - Tool definitions
- `src/pydantic_ai_integration/tools/factory/__init__.py` - ToolFactory
- Jinja2 templates for code generation

**2. Tool Registry**
- `src/pydantic_ai_integration/tool_decorator.py` - @register_mds_tool
- `MANAGED_TOOLS` dict - Single source of truth
- Runtime validation via Pydantic models
- Discovery API (by domain, capability, maturity)

**3. Request/Response Contracts**
```python
BaseRequest[PayloadT]           BaseResponse[PayloadT]
  - request_id: UUID              - request_id: UUID
  - session_id: str               - status: RequestStatus
  - user_id: str                  - payload: PayloadT
  - operation: str                - error: Optional[str]
  - payload: PayloadT             - metadata: Dict
  - timestamp: str
  - metadata: Dict
```

**4. Canonical Models**
- `CasefileModel` - Complete casefile with metadata, ACL, workspace data
- `ToolSession` - Session lifecycle with request tracking
- `ToolEvent` - Audit events for tool execution
- `CasefileACL` - Permission management

**5. Service Layer**
- `CasefileService` - 11 methods (CRUD, ACL, Google Workspace storage)
- `ToolSessionService` - 4 methods (create, get, list, close, process_tool_request)
- `GoogleWorkspace clients` - Mock implementations (Gmail, Drive, Sheets)

---

## Current State Assessment

### ✅ Strengths

**Architecture:**
- YAML-driven tool definitions with comprehensive classification system
- Unified decorator pattern (`@register_mds_tool`) as single source of truth
- Generic envelope pattern for all operations (consistent structure)
- Tool Factory with Jinja2 templates for code generation
- Hierarchical discovery (domain → subdomain → capability)
- Composite tool support via ChainExecutor

**Models:**
- Proper canonical models for core entities
- Typed workspace data containers (not Dict[str, Any])
- Computed fields for derived data
- ACL integration for permissions

**Audit Trail:**
- Complete tracking: User → Session → Request → Event → Casefile
- ToolEvent captures execution details (params, result, duration, status)
- Metadata enrichment at every layer

**Patterns:**
- Service/Repository separation
- Pydantic validation at model and decorator level
- Error handling with proper status codes
- Performance tracking (execution_time_ms in every response)

### 🔧 Gaps

**Limited Service Methods:**
```
CasefileService:           11 methods
  - CRUD: create, get, update, delete, list
  - ACL: grant_permission, revoke_permission, list_permissions, check_permission
  - Workspace: store_gmail_messages, store_drive_files, store_sheet_data
  - Session: add_session_to_casefile

ToolSessionService:        4 methods
  - Lifecycle: create_session, get_session, list_sessions, close_session
  - Execution: process_tool_request (delegates to tools)

GoogleWorkspace:           3 mock clients
  - GmailClient: list_messages, send_message, search_messages, get_message
  - DriveClient: list_files
  - SheetsClient: batch_get
```

**Missing Methods (examples):**
- Search & filter (search_casefiles, filter_by_criteria)
- Analytics (get_statistics, get_activity_timeline)
- Bulk operations (bulk_update, archive_multiple)
- Advanced Gmail (batch_process, templates, scheduling)
- Advanced Drive (sync_folder, share_file, create_folder)
- Advanced Sheets (append_rows, create_chart, formatting)
- Validation utilities (validate_email, validate_json_schema)
- Transformation utilities (convert_format, extract_metadata)

**Missing Models:**
- UserModel (user profiles, permissions, preferences)
- WorkspaceModel (team/organization)
- NotificationModel (alerts)
- TemplateModel (reusable content)

**Model Enhancements Needed:**
- CasefileModel: status, priority, category, relationships (parent/child)
- ToolSession: title, purpose, statistics (success_rate, duration)
- Add validators, computed fields, business logic methods

---

## Technical Deep Dive

### 1. Canonical Models

#### Current CasefileModel
```python
class CasefileModel(BaseModel):
    id: str                                    # cf_yymmdd_code
    metadata: CasefileMetadata                 # title, description, tags, timestamps
    acl: Optional[CasefileACL]                 # permissions
    session_ids: List[str]                     # linked sessions
    notes: Optional[str]
    
    # Typed workspace data (excellent design)
    gmail_data: Optional[CasefileGmailData]
    drive_data: Optional[CasefileDriveData]
    sheets_data: Optional[CasefileSheetsData]
    
    @computed_field
    def resource_count(self) -> int:
        # Aggregates across all data sources
```

#### Recommended Enhancements
```python
class CasefileStatus(str, Enum):
    ACTIVE = "active"
    ARCHIVED = "archived"
    CLOSED = "closed"
    DELETED = "deleted"

class CasefileModel(BaseModel):
    # ... existing fields ...
    
    # Add lifecycle
    status: CasefileStatus = Field(default=CasefileStatus.ACTIVE)
    priority: int = Field(default=2, ge=1, le=5)
    closed_at: Optional[str] = None
    closed_by: Optional[str] = None
    
    # Add relationships
    parent_casefile_id: Optional[str] = None
    child_casefile_ids: List[str] = Field(default_factory=list)
    related_casefile_ids: List[str] = Field(default_factory=list)
    
    # Add categorization
    category: Optional[str] = None
    
    # Add computed fields
    @computed_field
    @property
    def age_days(self) -> int:
        created = datetime.fromisoformat(self.created_at.replace('Z', '+00:00'))
        return (datetime.now() - created).days
    
    @computed_field
    @property
    def is_closed(self) -> bool:
        return self.status == CasefileStatus.CLOSED
    
    # Add business logic
    def close(self, user_id: str) -> None:
        if self.is_closed:
            raise ValueError("Casefile already closed")
        self.status = CasefileStatus.CLOSED
        self.closed_at = datetime.now().isoformat()
        self.closed_by = user_id
        self.updated_at = datetime.now().isoformat()
    
    def add_tag(self, tag: str) -> bool:
        tag = tag.strip().lower()
        if tag and tag not in self.tags:
            self.tags.append(tag)
            self.updated_at = datetime.now().isoformat()
            return True
        return False
    
    def can_read(self, user_id: str) -> bool:
        if self.owner_id == user_id:
            return True
        return self.acl.can_read(user_id) if self.acl else False
```

#### Current ToolSession
```python
class ToolSession(BaseModel):
    session_id: str                # ts_yymmdd_code
    user_id: str
    casefile_id: Optional[str]
    active: bool = True
    request_ids: List[str]
    created_at: str
    updated_at: str
```

#### Recommended Enhancements
```python
class ToolSession(BaseModel):
    # ... existing fields ...
    
    # Add metadata
    title: Optional[str] = None
    purpose: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    
    # Add statistics (updated incrementally by service)
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    
    # Add lifecycle
    closed_at: Optional[str] = None
    close_reason: Optional[str] = None
    
    # Add computed fields
    @computed_field
    @property
    def success_rate(self) -> float:
        if self.total_requests == 0:
            return 0.0
        return self.successful_requests / self.total_requests
    
    @computed_field
    @property
    def duration_seconds(self) -> Optional[int]:
        if not self.closed_at:
            return None
        created = datetime.fromisoformat(self.created_at.replace('Z', '+00:00'))
        closed = datetime.fromisoformat(self.closed_at.replace('Z', '+00:00'))
        return int((closed - created).total_seconds())
```

### 2. Service Method Pattern

**Standard Structure (all methods follow this):**
```python
async def method_name(
    self,
    request: MethodRequest
) -> MethodResponse:
    # 1. Start timing
    start_time = datetime.now()
    
    # 2. Extract inputs
    user_id = request.user_id
    param = request.payload.param
    
    # 3. Validate inputs
    if validation_fails:
        return MethodResponse(
            request_id=request.request_id,
            status=RequestStatus.FAILED,
            error="Validation error message",
            payload=EmptyPayload(),
            metadata={
                "execution_time_ms": calculate_time(),
                "validation_failed": "field_name"
            }
        )
    
    # 4. Check permissions (if needed)
    if not await self._check_permission(user_id, "permission"):
        return error_response()
    
    # 5. Execute business logic
    try:
        result = await self._do_work(param)
        
        execution_time_ms = calculate_time()
        
        return MethodResponse(
            request_id=request.request_id,
            status=RequestStatus.COMPLETED,
            payload=ResultPayload(result=result),
            metadata={
                "execution_time_ms": execution_time_ms,
                "user_id": user_id,
                "operation": "method_name"
            }
        )
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        return error_response(str(e))
```

**Key Principles:**
1. Performance tracking (execution_time_ms)
2. Structured responses (always RequestStatus)
3. Metadata enrichment (operation, user_id, context)
4. Error handling (try/except with proper logging)
5. Permission checks (security at service layer)
6. Validation (fail fast with clear messages)

### 3. Tool Engineering

#### YAML Tool Definition
```yaml
name: tool_name
display_name: "Human Readable Name"
description: "What this tool does"
category: "workspace"
version: "1.0.0"

classification:
  domain: workspace              # communication, workspace, automation, utilities
  subdomain: casefile            # email, google, casefile, etc.
  capability: search             # create, read, update, delete, process, search
  complexity: atomic             # atomic, composite, pipeline
  maturity: stable               # experimental, beta, stable, deprecated
  integration_tier: internal     # internal, external, hybrid

parameters:
  - name: param_name
    type: string                 # string, integer, float, boolean, array, object
    required: true
    min_length: 2
    description: "Parameter description"

implementation:
  type: simple                   # simple, api_call, data_transform, composite
  simple:
    logic: |
      service = SomeService()
      result = await service.method(param)
      return {"result": result}

returns:
  type: object
  properties:
    result:
      type: string

examples:
  - description: "Example usage"
    context:
      session:
        user_id: "user_123"
        session_id: "session_456"
    input:
      param_name: "value"
    expected_output:
      result: "expected"
```

#### Generated Tool Code
```python
# Auto-generated by Tool Factory
from src.pydantic_ai_integration.tool_decorator import register_mds_tool
from pydantic import BaseModel, Field

class ToolNameParams(BaseModel):
    param_name: str = Field(..., min_length=2, description="Parameter description")

@register_mds_tool(
    name="tool_name",
    params_model=ToolNameParams,
    description="What this tool does",
    category="workspace",
    version="1.0.0"
)
async def tool_name(ctx: MDSContext, param_name: str) -> Dict[str, Any]:
    """Generated tool implementation."""
    service = SomeService()
    result = await service.method(param_name)
    return {"result": result}
```

#### Tool Decorator Flow
```python
@register_mds_tool(name="tool_name", params_model=Params, ...)
    ↓
1. Extracts parameter definitions from Pydantic model
2. Creates ManagedToolDefinition (metadata + business rules + implementation)
3. Stores in MANAGED_TOOLS registry
4. Wraps implementation with validation + error handling
5. Registers with agent runtime
    ↓
MANAGED_TOOLS["tool_name"] = ManagedToolDefinition(
    metadata=ToolMetadata(...),
    business_rules=ToolBusinessRules(...),
    parameters=List[ToolParameterDef],
    implementation=async_function,
    params_model=Params
)
```

#### Tool Execution Flow
```python
User Request
    ↓
ToolSessionService.process_tool_request(ToolRequest)
    ↓
1. Validates session exists
2. Validates tool exists in MANAGED_TOOLS
3. Gets tool definition: get_tool_definition(tool_name)
4. Validates parameters: tool_def.validate_params(params)
5. Creates MDSContext (user_id, session_id, casefile_id)
6. Executes: tool_def.implementation(ctx, **validated_params)
7. Records events: tool_request_received, tool_execution_started, 
                   tool_execution_completed, tool_response_sent
    ↓
ToolResponse (with status, result, events)
```

---

## Implementation Roadmap

### Phase 1: Enhance Canonical Models (3-4 days)

**CasefileModel:**
```python
# Add enums
class CasefileStatus(str, Enum): ...
class CasefilePriority(int, Enum): ...

# Add fields
status: CasefileStatus
priority: CasefilePriority
closed_at: Optional[str]
closed_by: Optional[str]
parent_casefile_id: Optional[str]
child_casefile_ids: List[str]
category: Optional[str]

# Add validators
@field_validator('tags')
@classmethod
def validate_tags(cls, v): ...

# Add computed fields
@computed_field
def age_days(self) -> int: ...
@computed_field
def is_closed(self) -> bool: ...

# Add business logic
def close(self, user_id: str): ...
def add_tag(self, tag: str) -> bool: ...
def can_read(self, user_id: str) -> bool: ...
```

**ToolSession:**
```python
# Add fields
title: Optional[str]
purpose: Optional[str]
tags: List[str]
total_requests: int
successful_requests: int
failed_requests: int
closed_at: Optional[str]

# Add computed fields
@computed_field
def success_rate(self) -> float: ...
@computed_field
def duration_seconds(self) -> Optional[int]: ...
```

**UserModel (new):**
```python
class UserModel(BaseModel):
    user_id: str
    email: str
    display_name: str
    permissions: List[str]
    roles: List[str]
    preferences: Dict[str, Any]
    active: bool
    created_at: str
    last_active_at: str
    
    def has_permission(self, permission: str) -> bool: ...
    def has_role(self, role: str) -> bool: ...
```

### Phase 2: Expand Service Methods (10-14 days)

**CasefileService (add 10 methods):**
```python
# Search & Query
async def search_casefiles(request) -> response:
    # Full-text search across title, description, notes
    
async def filter_casefiles(request) -> response:
    # Multi-criteria filtering (tags, status, dates, priority)

# Analytics
async def get_casefile_statistics(request) -> response:
    # Aggregate stats: count by status, top tags, date histogram
    
async def get_casefile_activity(request) -> response:
    # Activity timeline with events

# Relationships
async def link_casefiles(request) -> response:
    # Create parent/child or related relationships
    
async def get_related_casefiles(request) -> response:
    # Get parent, children, related

# Bulk Operations
async def bulk_update_casefiles(request) -> response:
    # Update multiple casefiles atomically
    
async def archive_casefiles(request) -> response:
    # Archive old/inactive casefiles

# Export/Import
async def export_casefile(request) -> response:
    # Export to JSON/ZIP with all data
    
async def import_casefile(request) -> response:
    # Import from external format
```

**ToolSessionService (add 4 methods):**
```python
async def get_session_metrics(request) -> response:
    # Performance metrics, success rates
    
async def get_session_timeline(request) -> response:
    # Chronological event view
    
async def export_session_logs(request) -> response:
    # Complete audit trail export
    
async def close_inactive_sessions(request) -> response:
    # Bulk close idle sessions
```

**GoogleWorkspace Services (add 8-10 methods):**
```python
# Gmail
async def batch_process_emails(request) -> response:
async def create_email_template(request) -> response:
async def schedule_email(request) -> response:

# Drive
async def sync_folder(request) -> response:
async def share_file(request) -> response:
async def create_folder(request) -> response:

# Sheets
async def append_rows(request) -> response:
async def create_chart(request) -> response:
async def apply_formatting(request) -> response:
```

**Target:** 20-30 total service methods

### Phase 3: Tool Engineering (3-5 days)

**Atomic Tools (5-10 tools):**
```yaml
# Each tool uses ONE service method
casefile_search.yaml          → search_casefiles()
casefile_filter.yaml          → filter_casefiles()
casefile_get_stats.yaml       → get_casefile_statistics()
session_get_metrics.yaml      → get_session_metrics()
gmail_batch_process.yaml      → batch_process_emails()
drive_sync_folder.yaml        → sync_folder()
sheets_append_data.yaml       → append_rows()
```

**Composite Tools (1-2 tools):**
```yaml
# Orchestrates multiple atomic tools
gmail_to_drive_pipeline.yaml:
  steps:
    - tool: gmail_search_messages
    - tool: extract_attachments
    - tool: drive_upload_files
    - tool: casefile_update_metadata
```

**Generate tools:**
```bash
python scripts/generate_tools.py tool_name
python scripts/generate_tools.py  # All tools
```

---

## Code Examples

### Example 1: Service Method Implementation

```python
async def search_casefiles(
    self,
    request: SearchCasefilesRequest
) -> SearchCasefilesResponse:
    """Full-text search across casefiles."""
    start_time = datetime.now()
    user_id = request.user_id
    query = request.payload.query
    limit = request.payload.limit or 20
    offset = request.payload.offset or 0
    
    # Validate query
    if not query or len(query) < 2:
        execution_time_ms = int((datetime.now() - start_time).total_seconds() * 1000)
        return SearchCasefilesResponse(
            request_id=request.request_id,
            status=RequestStatus.FAILED,
            error="Query must be at least 2 characters",
            payload=CasefileListPayload(casefiles=[], total_count=0, offset=offset, limit=limit),
            metadata={
                "execution_time_ms": execution_time_ms,
                "validation_failed": "query_length"
            }
        )
    
    # Execute search
    all_results = await self.repository.search_casefiles(query, user_id=user_id)
    
    # Filter by permissions
    accessible = [cf for cf in all_results if cf.can_read(user_id)]
    
    # Paginate
    total_count = len(accessible)
    paginated = accessible[offset:offset + limit]
    
    execution_time_ms = int((datetime.now() - start_time).total_seconds() * 1000)
    
    logger.info(f"Search '{query}' returned {total_count} results")
    
    return SearchCasefilesResponse(
        request_id=request.request_id,
        status=RequestStatus.COMPLETED,
        payload=CasefileListPayload(
            casefiles=paginated,
            total_count=total_count,
            offset=offset,
            limit=limit
        ),
        metadata={
            "execution_time_ms": execution_time_ms,
            "query": query,
            "results_found": total_count,
            "results_returned": len(paginated)
        }
    )
```

### Example 2: Model Enhancement

```python
class CasefileModel(BaseModel):
    # ... existing fields ...
    
    status: CasefileStatus = Field(default=CasefileStatus.ACTIVE)
    priority: int = Field(default=2, ge=1, le=5)
    
    @field_validator('tags')
    @classmethod
    def validate_tags(cls, v: List[str]) -> List[str]:
        """Normalize and deduplicate tags."""
        normalized = [tag.strip().lower() for tag in v if tag.strip()]
        unique = list(dict.fromkeys(normalized))
        if len(unique) > 20:
            raise ValueError("Maximum 20 tags allowed")
        return unique
    
    @computed_field
    @property
    def age_days(self) -> int:
        """Days since creation."""
        created = datetime.fromisoformat(self.created_at.replace('Z', '+00:00'))
        return (datetime.now() - created).days
    
    @computed_field
    @property
    def is_closed(self) -> bool:
        """Check if casefile is closed."""
        return self.status == CasefileStatus.CLOSED
    
    def close(self, user_id: str) -> None:
        """Close this casefile."""
        if self.is_closed:
            raise ValueError("Casefile already closed")
        self.status = CasefileStatus.CLOSED
        self.closed_at = datetime.now().isoformat()
        self.closed_by = user_id
        self.updated_at = datetime.now().isoformat()
    
    def add_tag(self, tag: str) -> bool:
        """Add tag if not present."""
        tag = tag.strip().lower()
        if tag and tag not in self.tags:
            self.tags.append(tag)
            self.updated_at = datetime.now().isoformat()
            return True
        return False
```

### Example 3: Tool YAML Definition

```yaml
name: casefile_search
display_name: "Search Casefiles"
description: "Full-text search across casefile metadata"
category: "casefile"
version: "1.0.0"

classification:
  domain: workspace
  subdomain: casefile
  capability: search
  complexity: atomic
  maturity: stable
  integration_tier: internal

parameters:
  - name: query
    type: string
    required: true
    min_length: 2
    description: "Search query"
  
  - name: limit
    type: integer
    required: false
    default: 20
    min_value: 1
    max_value: 100

implementation:
  type: simple
  simple:
    logic: |
      from src.casefileservice.service import CasefileService
      from src.pydantic_models.operations.casefile_ops import (
          SearchCasefilesRequest, SearchCasefilesPayload
      )
      
      service = CasefileService()
      request = SearchCasefilesRequest(
          user_id=ctx.user_id,
          session_id=ctx.session_id,
          payload=SearchCasefilesPayload(query=query, limit=limit)
      )
      
      response = await service.search_casefiles(request)
      
      return {
          "casefiles": [cf.model_dump() for cf in response.payload.casefiles],
          "total_count": response.payload.total_count
      }

returns:
  type: object
  properties:
    casefiles:
      type: array
    total_count:
      type: integer

examples:
  - description: "Search for project casefiles"
    context:
      session:
        user_id: "user_123"
        session_id: "session_456"
    input:
      query: "project"
      limit: 10
    expected_output:
      casefiles: []
      total_count: 0
```

---

## Testing Strategy

### Unit Tests (Service Methods)
```python
@pytest.mark.asyncio
async def test_search_casefiles_success():
    service = CasefileService()
    request = SearchCasefilesRequest(
        user_id="test_user",
        payload=SearchCasefilesPayload(query="test", limit=10)
    )
    response = await service.search_casefiles(request)
    assert response.status == RequestStatus.COMPLETED
    assert isinstance(response.payload.casefiles, list)

@pytest.mark.asyncio
async def test_search_casefiles_short_query():
    service = CasefileService()
    request = SearchCasefilesRequest(
        user_id="test_user",
        payload=SearchCasefilesPayload(query="a", limit=10)
    )
    response = await service.search_casefiles(request)
    assert response.status == RequestStatus.FAILED
    assert "at least 2 characters" in response.error
```

### Integration Tests (Tools)
```python
@pytest.mark.integration
@pytest.mark.asyncio
async def test_casefile_search_tool():
    from src.pydantic_ai_integration.dependencies import MDSContext
    from src.pydantic_ai_integration.tools.generated.casefile_search import casefile_search
    
    ctx = MDSContext(user_id="test_user", session_id="test_session")
    result = await casefile_search(ctx, query="test", limit=10)
    
    assert "casefiles" in result
    assert "total_count" in result
    assert isinstance(result["casefiles"], list)
```

### Model Tests (Validation)
```python
def test_casefile_model_validation():
    # Valid tags
    casefile = CasefileModel(
        title="Test",
        tags=["Tag1", "TAG1", "tag1"],  # Duplicates
        owner_id="user_123",
        created_by="user_123"
    )
    assert len(casefile.tags) == 1  # Deduplicated
    assert casefile.tags[0] == "tag1"  # Normalized
    
    # Too many tags
    with pytest.raises(ValidationError):
        CasefileModel(
            title="Test",
            tags=[f"tag{i}" for i in range(25)],
            owner_id="user_123",
            created_by="user_123"
        )
```

---

## Key Files Reference

```
Project Root
├── config/
│   ├── tool_schema_v2.yaml                    # YAML schema definition
│   └── tools/                                 # Tool definitions by domain
│       └── {domain}/{subdomain}/*.yaml
│
├── src/
│   ├── pydantic_models/
│   │   ├── base/
│   │   │   ├── envelopes.py                   # BaseRequest/BaseResponse
│   │   │   └── types.py                       # RequestStatus enum
│   │   ├── canonical/
│   │   │   ├── casefile.py                    # CasefileModel
│   │   │   ├── tool_session.py                # ToolSession, ToolEvent
│   │   │   └── acl.py                         # CasefileACL, PermissionEntry
│   │   └── operations/
│   │       ├── casefile_ops.py                # Casefile request/response
│   │       └── tool_execution_ops.py          # Tool request/response
│   │
│   ├── casefileservice/
│   │   ├── service.py                         # CasefileService (11 methods)
│   │   └── repository.py                      # Firestore persistence
│   │
│   ├── tool_sessionservice/
│   │   ├── service.py                         # ToolSessionService
│   │   └── repository.py                      # Session persistence
│   │
│   └── pydantic_ai_integration/
│       ├── tool_decorator.py                  # @register_mds_tool, MANAGED_TOOLS
│       ├── tool_definition.py                 # ManagedToolDefinition
│       ├── dependencies.py                    # MDSContext
│       └── tools/
│           ├── factory/
│           │   ├── __init__.py                # ToolFactory class
│           │   └── templates/
│           │       └── tool_template.py.jinja2
│           └── generated/                     # Generated tool code
│
└── scripts/
    ├── generate_tools.py                      # Tool generation CLI
    └── show_tools.py                          # List registered tools
```

---

## Command Reference

```bash
# Generate single tool
python scripts/generate_tools.py tool_name

# Generate all tools
python scripts/generate_tools.py

# Validate only (no code generation)
python scripts/generate_tools.py --validate-only

# Show registered tools
python scripts/show_tools.py

# Run tests
pytest                                          # All tests
pytest tests/unit/                              # Unit tests only
pytest tests/integration/                       # Integration tests only
pytest --cov=src --cov-report=html              # With coverage
```

---

## Success Metrics

After foundation building (3-4 weeks):

**Models:**
- ✅ 3 enhanced canonical models with validation, computed fields, business logic
- ✅ 10+ computed fields across models
- ✅ 15+ business logic methods

**Service Methods:**
- ✅ 20-30 service methods across all services
- ✅ Consistent patterns (timing, validation, error handling, audit)
- ✅ Complete test coverage

**Tools:**
- ✅ 5-10 atomic tools (one service method each)
- ✅ 1-2 composite tools (orchestration)
- ✅ Integration tests passing
- ✅ Documentation and examples

**Result:** Ready to engineer user and AI toolsets in series with confidence.

---

## Next Steps

1. **Days 1-3:** Enhance CasefileModel, ToolSession, create UserModel
2. **Days 4-10:** Implement 10 service methods (search, filter, analytics)
3. **Days 11-17:** Implement 10 more service methods (workspace integration, bulk ops)
4. **Days 18-21:** Create 5-10 atomic tool YAMLs and generate tools
5. **Days 22-25:** Create 1-2 composite tools and validate orchestration
6. **Day 26+:** Begin engineering user toolset, then AI toolset

---

**Document Version:** 1.0  
**Last Updated:** October 6, 2025
