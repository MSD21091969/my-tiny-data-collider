# GitHub Copilot Chore List
## Tiny Data Collider - Post-Refactoring Implementation Tasks

**Created:** October 1, 2025  
**Status:** Ready for Copilot Automation  
**Context:** Following successful unified tool system refactoring (commit `b6b7955`)

---

## 🎯 Overview

This document provides structured, well-defined tasks for GitHub Copilot to work on in the cloud repository. Each chore is independent, testable, and follows established patterns from the refactoring.

---

## 📋 Priority 1: SOLID Pod Integration (Foundation)

### Chore #1: Create Solid Pod Client Service
**Priority:** HIGH  
**Estimated Effort:** 2-3 hours  
**Dependencies:** None

**Description:**  
Implement `src/solidservice/client.py` following the pattern in `docs/SOLID_INTEGRATION_PLAN.md`.

**Requirements:**
1. Create `SolidPodClient` class with methods:
   - `read_resource(path)` - Read RDF data from pod
   - `write_resource(path, data)` - Write RDF data to pod
   - `create_container(path)` - Create folder structure
2. Use `rdflib` for RDF parsing/serialization
3. Support authentication via bearer token
4. Convert Python dicts ↔ RDF Turtle format
5. Handle HTTP responses (200, 201, 404, 403)

**Acceptance Criteria:**
- [ ] Client can connect to Solid Pod
- [ ] Can create containers (folders)
- [ ] Can write/read Turtle RDF data
- [ ] Includes error handling for common cases
- [ ] Has docstrings and type hints

**Test Script:**
```python
# scripts/test_solid_client.py
async def test_solid_client():
    client = SolidPodClient(
        pod_url="http://localhost:3000/test/",
        webid="http://localhost:3000/test/profile/card#me"
    )
    
    # Test create container
    assert await client.create_container("test-data/")
    
    # Test write
    data = {"title": "Test", "value": 42}
    assert await client.write_resource("test-data/sample.ttl", data)
    
    # Test read
    retrieved = await client.read_resource("test-data/sample.ttl")
    assert retrieved["title"] == "Test"
```

**Files to Create:**
- `src/solidservice/__init__.py`
- `src/solidservice/client.py`
- `tests/test_solid_client.py`
- `scripts/test_solid_client.py`

---

### Chore #2: Add Solid Mirror to CasefileService
**Priority:** HIGH  
**Estimated Effort:** 1-2 hours  
**Dependencies:** Chore #1

**Description:**  
Extend `CasefileService` to mirror casefiles to Solid Pod (dual persistence pattern from SOLID_INTEGRATION_PLAN.md Option 1).

**Requirements:**
1. Add `solid_client` attribute to `CasefileService.__init__()`
2. Update `create_casefile()` to also write to Solid Pod
3. Update `get_casefile()` to fallback to Solid Pod if Firestore fails
4. Only activate if `SOLID_ENABLED=true` in config
5. Log all Solid operations (info level)

**Acceptance Criteria:**
- [ ] Casefiles written to both Firestore AND Solid Pod
- [ ] Can retrieve from Solid if Firestore unavailable
- [ ] Gracefully handles Solid Pod failures (doesn't break existing flow)
- [ ] Config flag controls Solid integration
- [ ] Logging shows Solid operations

**Test Script:**
```python
# tests/test_casefile_solid_mirror.py
async def test_casefile_dual_persistence():
    service = CasefileService()  # SOLID_ENABLED=true in .env.test
    
    casefile_id = await service.create_casefile(
        user_id="test_user",
        title="Test Casefile"
    )
    
    # Verify in Firestore
    from_firestore = await service.repository.get_casefile(casefile_id)
    assert from_firestore is not None
    
    # Verify in Solid Pod
    solid_path = f"tiny-data-collider/casefiles/{casefile_id}.ttl"
    from_solid = await service.solid_client.read_resource(solid_path)
    assert from_solid["metadata"]["title"] == "Test Casefile"
```

**Files to Modify:**
- `src/casefileservice/service.py`
- `src/coreservice/config.py` (add SOLID_ENABLED, SOLID_POD_URL, SOLID_WEBID)

**Files to Create:**
- `tests/test_casefile_solid_mirror.py`
- `.env.example` (add SOLID_* variables)

---

## 📋 Priority 2: Tool Engineering Factory

### Chore #3: Create ToolDefinitionValidator
**Priority:** MEDIUM  
**Estimated Effort:** 2 hours  
**Dependencies:** None

**Description:**  
Build a validator that analyzes new tool definitions for completeness and consistency (supports pydantic toolengineering.txt vision).

**Requirements:**
1. Create `src/pydantic_ai_integration/tool_validator.py`
2. Validate tool definition has:
   - All required metadata fields
   - Valid parameter model (extends BaseModel)
   - Consistent field types
   - Proper docstrings
3. Check for common anti-patterns:
   - Missing `ge=`/`le=` constraints on integers
   - Missing `min_length=` on strings
   - Missing descriptions on Fields
4. Return validation report with warnings/errors

**Acceptance Criteria:**
- [ ] Can validate `ManagedToolDefinition` instances
- [ ] Detects missing metadata
- [ ] Warns about missing constraints
- [ ] Returns structured validation report
- [ ] Includes severity levels (error, warning, info)

**Test Script:**
```python
# tests/test_tool_validator.py
def test_tool_validator():
    from src.pydantic_ai_integration.tool_validator import ToolDefinitionValidator
    from src.pydantic_ai_integration.tool_decorator import get_tool_definition
    
    validator = ToolDefinitionValidator()
    
    # Test valid tool
    tool = get_tool_definition("example_tool")
    report = validator.validate(tool)
    assert report.is_valid
    assert len(report.errors) == 0
    
    # Test incomplete tool
    class BadParams(BaseModel):
        value: int  # Missing constraints!
    
    incomplete_tool = ManagedToolDefinition(
        metadata=ToolMetadata(name="bad_tool", description="..."),
        business_rules=ToolBusinessRules(),
        execution=ToolExecution(
            params_model=BadParams,
            implementation=lambda ctx, value: {"result": value}
        )
    )
    
    report = validator.validate(incomplete_tool)
    assert not report.is_valid
    assert any("constraint" in err.message.lower() for err in report.warnings)
```

**Files to Create:**
- `src/pydantic_ai_integration/tool_validator.py`
- `tests/test_tool_validator.py`

---

### Chore #4: Implement Tool Template Generator
**Priority:** MEDIUM  
**Estimated Effort:** 2-3 hours  
**Dependencies:** Chore #3

**Description:**  
Create a CLI tool that generates boilerplate for new tools (declarative tool engineering from pydantic toolengineering.txt).

**Requirements:**
1. Create `scripts/generate_tool.py`
2. Accept tool metadata via command line:
   ```bash
   python scripts/generate_tool.py \
     --name my_tool \
     --description "Does something" \
     --category utilities \
     --param name:str \
     --param count:int:ge=1:le=100
   ```
3. Generate three files:
   - Parameter model in `tool_params.py`
   - Implementation in `tools/my_tool.py`
   - Test in `tests/test_my_tool.py`
4. Follow existing patterns from `unified_example_tools.py`
5. Include TODO comments for business logic

**Acceptance Criteria:**
- [ ] CLI script accepts tool metadata
- [ ] Generates valid parameter model with constraints
- [ ] Generates implementation stub with decorator
- [ ] Generates test template
- [ ] Generated code passes validation (Chore #3)
- [ ] Includes comprehensive docstrings

**Example Output:**
```python
# Generated: src/pydantic_ai_integration/tools/tool_params.py (append)
class MyToolParams(BaseModel):
    """Parameters for my_tool."""
    name: str = Field(..., min_length=1, description="Name parameter")
    count: int = Field(..., ge=1, le=100, description="Count parameter")

# Generated: src/pydantic_ai_integration/tools/my_tool.py
@register_mds_tool(
    name="my_tool",
    description="Does something",
    category="utilities",
    version="1.0.0",
    enabled=True,
    requires_auth=True,
    params_model=MyToolParams,
    timeout_seconds=30
)
async def my_tool(ctx: MDSContext, name: str, count: int) -> Dict[str, Any]:
    """
    Implementation for my_tool.
    
    Args:
        ctx: MDS context with session info
        name: Name parameter
        count: Count parameter (1-100)
        
    Returns:
        Result dictionary
    """
    # TODO: Implement business logic
    return {"result": "pending"}
```

**Files to Create:**
- `scripts/generate_tool.py`
- `tests/test_tool_generator.py`

---

## 📋 Priority 3: Google Workspace Mock Tools

### Chore #5: Create MockGoogleDriveClient
**Priority:** MEDIUM  
**Estimated Effort:** 3-4 hours  
**Dependencies:** None

**Description:**  
Build mock Google Drive client for testing casefile CRUD operations (supports "mock google workspace tools casefile crud" from pydantic toolengineering.txt).

**Requirements:**
1. Create `src/integrations/google_workspace/mock_drive.py`
2. Implement in-memory file system:
   ```python
   class MockGoogleDriveClient:
       async def create_file(self, name, content, parent_id=None)
       async def read_file(self, file_id)
       async def update_file(self, file_id, content)
       async def delete_file(self, file_id)
       async def list_files(self, parent_id=None, query=None)
       async def create_folder(self, name, parent_id=None)
   ```
3. Return Google Drive API-compatible responses
4. Support metadata (created_at, modified_at, owner)
5. Implement search by name/query

**Acceptance Criteria:**
- [ ] Full CRUD operations work
- [ ] Folder hierarchy supported
- [ ] Search/query functionality
- [ ] Returns API-compatible responses
- [ ] In-memory persistence (no external dependencies)
- [ ] Thread-safe operations

**Test Script:**
```python
# tests/test_mock_google_drive.py
async def test_mock_drive_crud():
    client = MockGoogleDriveClient()
    
    # Create folder
    folder = await client.create_folder("My Casefiles")
    assert folder["id"] is not None
    
    # Create file
    file = await client.create_file(
        name="casefile_001.json",
        content='{"title": "Test"}',
        parent_id=folder["id"]
    )
    assert file["id"] is not None
    
    # Read file
    content = await client.read_file(file["id"])
    assert "Test" in content
    
    # Update file
    await client.update_file(file["id"], '{"title": "Updated"}')
    
    # List files
    files = await client.list_files(parent_id=folder["id"])
    assert len(files) == 1
    
    # Delete file
    await client.delete_file(file["id"])
    files = await client.list_files(parent_id=folder["id"])
    assert len(files) == 0
```

**Files to Create:**
- `src/integrations/__init__.py`
- `src/integrations/google_workspace/__init__.py`
- `src/integrations/google_workspace/mock_drive.py`
- `tests/test_mock_google_drive.py`

---

### Chore #6: Create Google Drive Tools
**Priority:** MEDIUM  
**Estimated Effort:** 2-3 hours  
**Dependencies:** Chore #5

**Description:**  
Implement tools that use MockGoogleDriveClient for casefile data operations.

**Requirements:**
1. Create 4 tools in `src/pydantic_ai_integration/tools/google_drive_tools.py`:
   - `drive_create_casefile_folder` - Create folder for casefile
   - `drive_upload_casefile_data` - Upload casefile data as JSON
   - `drive_list_casefile_files` - List files in casefile folder
   - `drive_download_casefile_data` - Download casefile data
2. Each tool uses `@register_mds_tool` decorator
3. Parameter models in `tool_params.py`
4. Tools use casefile_id to organize data
5. Integration test shows full workflow

**Acceptance Criteria:**
- [ ] 4 tools registered in MANAGED_TOOLS
- [ ] Tools work with MockGoogleDriveClient
- [ ] Parameter validation enforced
- [ ] Can create/upload/list/download casefile data
- [ ] E2E test demonstrates workflow
- [ ] Error handling for common cases

**Test Script:**
```python
# scripts/test_google_drive_workflow.py
async def test_drive_workflow():
    # 1. Create casefile
    casefile_id = "cf_251001_test123"
    
    # 2. Create folder tool
    request = ToolRequest(
        user_id="test",
        operation="tool_execution",
        session_id="ts_test",
        payload=ToolRequestPayload(
            tool_name="drive_create_casefile_folder",
            parameters={"casefile_id": casefile_id, "folder_name": "Test Case"}
        )
    )
    response = await tool_service.process_tool_request(request)
    folder_id = response.payload.result["folder_id"]
    
    # 3. Upload data
    request2 = ToolRequest(
        user_id="test",
        operation="tool_execution",
        session_id="ts_test",
        payload=ToolRequestPayload(
            tool_name="drive_upload_casefile_data",
            parameters={
                "casefile_id": casefile_id,
                "file_name": "metadata.json",
                "content": '{"title": "Test"}',
                "folder_id": folder_id
            }
        )
    )
    response2 = await tool_service.process_tool_request(request2)
    
    # 4. List files
    request3 = ToolRequest(
        user_id="test",
        operation="tool_execution",
        session_id="ts_test",
        payload=ToolRequestPayload(
            tool_name="drive_list_casefile_files",
            parameters={"casefile_id": casefile_id, "folder_id": folder_id}
        )
    )
    response3 = await tool_service.process_tool_request(request3)
    assert len(response3.payload.result["files"]) == 1
```

**Files to Create:**
- `src/pydantic_ai_integration/tools/google_drive_tools.py`
- Update `src/pydantic_ai_integration/tools/tool_params.py`
- `scripts/test_google_drive_workflow.py`
- `tests/test_google_drive_tools.py`

---

## 📋 Priority 4: Observability & Metrics

### Chore #7: Add Tool Execution Metrics
**Priority:** LOW  
**Estimated Effort:** 2 hours  
**Dependencies:** None

**Description:**  
Track tool usage statistics for monitoring and analytics.

**Requirements:**
1. Create `src/coreservice/metrics.py`
2. Track per tool:
   - Execution count
   - Success/failure rate
   - Average duration
   - Parameter patterns
3. Store metrics in memory (dict)
4. Provide summary endpoint
5. Optional: Export to Prometheus format

**Acceptance Criteria:**
- [ ] Metrics tracked per tool execution
- [ ] Can retrieve metrics summary
- [ ] Includes success/failure breakdown
- [ ] Shows average/p50/p95/p99 durations
- [ ] Lightweight (< 10ms overhead)

**Test Script:**
```python
# tests/test_tool_metrics.py
def test_metrics_tracking():
    from src.coreservice.metrics import ToolMetrics
    
    metrics = ToolMetrics()
    
    # Record executions
    metrics.record_execution("example_tool", success=True, duration_ms=100)
    metrics.record_execution("example_tool", success=True, duration_ms=150)
    metrics.record_execution("example_tool", success=False, duration_ms=50)
    
    # Get summary
    summary = metrics.get_summary("example_tool")
    assert summary["total_executions"] == 3
    assert summary["success_rate"] == 2/3
    assert summary["avg_duration_ms"] == 100
```

**Files to Create:**
- `src/coreservice/metrics.py`
- `src/pydantic_api/routers/metrics.py` (GET /metrics/tools)
- `tests/test_tool_metrics.py`

---

### Chore #8: Implement Structured Logging
**Priority:** LOW  
**Estimated Effort:** 1-2 hours  
**Dependencies:** None

**Description:**  
Enhance logging with structured JSON output for better observability.

**Requirements:**
1. Create `src/coreservice/logging_config.py`
2. Configure structured JSON logging:
   - timestamp
   - level
   - message
   - tool_name
   - session_id
   - user_id
   - duration_ms
3. Environment-aware (dev: pretty, prod: JSON)
4. Include correlation IDs

**Acceptance Criteria:**
- [ ] Logs output as JSON in production
- [ ] Pretty-printed in development
- [ ] Includes context (session_id, user_id, tool_name)
- [ ] Easy to parse for log aggregation
- [ ] Backwards compatible

**Files to Create:**
- `src/coreservice/logging_config.py`
- Update `src/tool_sessionservice/service.py` to use structured logging

---

## 📋 Priority 5: Documentation & Examples

### Chore #9: Create Tool Development Guide
**Priority:** LOW  
**Estimated Effort:** 1-2 hours  
**Dependencies:** Chore #4

**Description:**  
Write comprehensive guide for tool developers.

**Requirements:**
1. Create `docs/TOOL_DEVELOPMENT_GUIDE.md`
2. Sections:
   - Quick start (5-minute tool)
   - Field categorization explained
   - Parameter validation patterns
   - Best practices
   - Testing guidelines
   - Common pitfalls
3. Include code examples
4. Link to generated templates

**Acceptance Criteria:**
- [ ] New developer can create tool in <10 minutes
- [ ] Explains all decorator parameters
- [ ] Shows validation patterns
- [ ] Includes full example
- [ ] Links to relevant files

---

### Chore #10: Create API Usage Examples
**Priority:** LOW  
**Estimated Effort:** 1 hour  
**Dependencies:** None

**Description:**  
Document API usage with curl/Python examples.

**Requirements:**
1. Create `docs/API_EXAMPLES.md`
2. Show examples for:
   - List tools (`GET /tool-sessions/tools`)
   - Get tool schema (`GET /tool-sessions/tools/{name}/schema`)
   - Execute tool (`POST /tool-sessions/execute`)
   - Create casefile + session + execute workflow
3. Include both curl and Python requests
4. Show error handling

**Acceptance Criteria:**
- [ ] Working examples for all endpoints
- [ ] Both curl and Python versions
- [ ] Shows authentication
- [ ] Includes error scenarios
- [ ] Copy-pasteable code

---

## 🔧 Execution Guidelines for Copilot

### General Principles
1. **Follow existing patterns** - Study `unified_example_tools.py` before creating new tools
2. **Test-driven** - Write tests first or alongside implementation
3. **Type hints** - Use full type annotations everywhere
4. **Docstrings** - Every function needs comprehensive docstrings
5. **Error handling** - Graceful degradation, clear error messages
6. **Logging** - Log important operations at appropriate levels

### Code Style
- **Black** formatting
- **isort** for imports
- **flake8** compliant
- **mypy** type checking passes

### Testing Requirements
- Unit tests for all new functions
- Integration tests for workflows
- E2E tests for major features
- Minimum 80% coverage

### Git Workflow
- One chore = one branch
- Branch name: `chore/{number}-{short-description}`
- Example: `chore/1-solid-pod-client`
- PR title: "Chore #{number}: {title}"
- Link to this file in PR description

---

## 📊 Progress Tracking

| Chore | Status | Branch | PR | Completed |
|-------|--------|--------|-----|-----------|
| #1: Solid Pod Client | ⏳ | - | - | - |
| #2: Solid Mirror | ⏳ | - | - | - |
| #3: Tool Validator | ⏳ | - | - | - |
| #4: Tool Generator | ⏳ | - | - | - |
| #5: Mock Drive Client | ⏳ | - | - | - |
| #6: Drive Tools | ⏳ | - | - | - |
| #7: Metrics | ⏳ | - | - | - |
| #8: Structured Logging | ⏳ | - | - | - |
| #9: Dev Guide | ⏳ | - | - | - |
| #10: API Examples | ⏳ | - | - | - |

**Legend:** ⏳ Not Started | 🚧 In Progress | ✅ Complete | ❌ Blocked

---

## 🎯 Success Metrics

Each completed chore should:
- [ ] Pass all tests (unit + integration)
- [ ] Have >80% code coverage
- [ ] Include comprehensive documentation
- [ ] Follow existing architectural patterns
- [ ] Be reviewed and merged to main

---

## 📝 Notes

- **Context Files:**
  - `docs/REFACTORING_COMPLETE.md` - Recent refactoring details
  - `docs/SOLID_INTEGRATION_PLAN.md` - Solid Pod integration architecture
  - `docs/pydantic toolengineering.txt` - Tool engineering vision
  - `.github/copilot-instructions.md` - General project guidelines

- **Key Patterns:**
  - Tool registration: `@register_mds_tool` decorator
  - Parameter validation: Pydantic BaseModel with Field() constraints
  - Service layer: Queries `get_tool_definition()` from MANAGED_TOOLS
  - Testing: Use `scripts/test_*.py` for manual tests, `tests/test_*.py` for pytest

- **Contact:**
  - Issues with chores: Create GitHub issue with `copilot-chore` label
  - Questions: Reference this file and relevant docs

---

**Ready for Copilot automation! 🤖**
