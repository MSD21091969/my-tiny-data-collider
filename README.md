# My Tiny Data Collider - Architecture

YAML-driven tool generation framework with FastAPI service layer and Google Workspace integrations.

---

## Project Structure

```
my-tiny-data-collider/
├── config/
│   └── tools/                          # YAML tool definitions (SINGLE SOURCE OF TRUTH)
│       ├── automation/pipelines/       # Pipeline orchestration tools
│       ├── communication/email/        # Gmail tools
│       ├── utilities/debugging/        # Debug and example tools
│       └── workspace/google/           # Drive, Sheets tools
│
├── src/
│   ├── pydantic_models/                # Domain models (Layer 1)
│   │   ├── base/                       # BaseRequest, BaseResponse, RequestStatus
│   │   ├── canonical/                  # ToolSession, CasefileModel, ToolEvent
│   │   ├── operations/                 # Request/Response DTOs
│   │   ├── views/                      # Read-only projections
│   │   └── workspace/                  # External data models (Gmail, Drive, Sheets)
│   │
│   ├── pydantic_ai_integration/        # Tool framework (Layer 2)
│   │   ├── tool_definition.py          # ManagedToolDefinition (single source of truth)
│   │   ├── tool_decorator.py           # @register_mds_tool, MANAGED_TOOLS registry
│   │   ├── dependencies.py             # MDSContext
│   │   ├── integrations/               # External API contracts
│   │   │   └── google_workspace/
│   │   │       ├── clients.py          # Gmail, Drive, Sheets API clients
│   │   │       └── models.py           # Request/Response models
│   │   └── tools/
│   │       ├── factory/                # Code generator
│   │       │   ├── __init__.py         # ToolFactory class
│   │       │   └── templates/          # Jinja2 templates
│   │       │       ├── tool_template.py.jinja2
│   │       │       ├── test_template.py.jinja2
│   │       │       ├── integration_test_template.py.jinja2
│   │       │       └── api_test_template.py.jinja2
│   │       └── generated/              # Generated tools (Layer 3)
│   │           ├── automation/pipelines/
│   │           ├── communication/email/
│   │           ├── utilities/debugging/
│   │           └── workspace/google/
│   │
│   ├── pydantic_api/                   # FastAPI application
│   │   ├── app.py                      # Main FastAPI app
│   │   └── routers/
│   │       ├── casefile.py             # Casefile CRUD + ACL
│   │       ├── tool_session.py         # Tool session + execution
│   │       └── chat.py                 # Chat session + messaging
│   │
│   ├── tool_sessionservice/            # Tool execution service layer
│   ├── casefileservice/                # Casefile management service
│   ├── communicationservice/           # Chat/agent service
│   └── coreservice/                    # Core utilities (ID generation, config)
│
├── tests/
│   ├── unit/                           # Unit tests (generated from YAML)
│   │   ├── automation/pipelines/
│   │   ├── communication/email/
│   │   ├── utilities/debugging/
│   │   └── workspace/google/
│   ├── integration/                    # Integration tests (service layer)
│   │   ├── automation/pipelines/
│   │   ├── communication/email/
│   │   ├── utilities/debugging/
│   │   └── workspace/google/
│   ├── api/                            # API tests (HTTP endpoints)
│   │   ├── automation/pipelines/
│   │   ├── communication/email/
│   │   ├── utilities/debugging/
│   │   └── workspace/google/
│   └── fixtures/                       # Shared test fixtures
│       ├── common.py
│       └── auth_fixtures.py
│
└── scripts/
    └── generate_tools.py               # Tool generation wrapper script
```

---

## Tool Lifecycle

### 1. YAML Definition (Source of Truth)

```yaml
# config/tools/communication/email/gmail_send_message.yaml
name: gmail_send_message
description: "Send email via Gmail"
category: google_workspace

classification:
  domain: communication
  subdomain: email
  capability: create
  complexity: atomic
  maturity: stable

business_rules:
  enabled: true
  requires_auth: true
  required_permissions: ['gmail:send']
  timeout_seconds: 30

session_policies:
  requires_active_session: true
  allow_new_session: false
  session_event_type: request

parameters:
  - name: to
    type: string
    required: true
  - name: subject
    type: string
    required: true
  - name: body
    type: string
    required: true

implementation:
  type: api_call
  api_call:
    client_class: GmailClient
    method_name: send_message
```

**Folder structure:** `domain/subdomain/tool.yaml` (semantic organization)  
**category field:** Ignored for folder structure (legacy, kept for backward compatibility)

---

### 2. Code Generation

```bash
# Generate all tools
python scripts/generate_tools.py

# Or use module directly
python -m src.pydantic_ai_integration.tools.factory

# Or after installing package
generate-tools
```

**Generated files:**
```
src/pydantic_ai_integration/tools/generated/communication/email/
└── gmail_send_message.py              # Tool implementation

tests/unit/communication/email/
└── test_gmail_send_message.py         # Unit tests

tests/integration/communication/email/
└── test_gmail_send_message_integration.py

tests/api/communication/email/
└── test_gmail_send_message_api.py
```

**Generated tool structure:**
```python
# gmail_send_message.py
from pydantic import BaseModel, Field
from ...tool_decorator import register_mds_tool
from ...dependencies import MDSContext

class GmailSendMessageParams(BaseModel):
    """Generated Pydantic model for validation."""
    to: str = Field(...)
    subject: str = Field(...)
    body: str = Field(...)

@register_mds_tool(
    name="gmail_send_message",
    params_model=GmailSendMessageParams,
    description="Send email via Gmail",
    # ... business rules, policies
)
async def gmail_send_message(ctx: MDSContext, to: str, subject: str, body: str):
    # Implementation from YAML
    return {"status": "sent"}
```

---

### 3. Tool Registration

**Happens at import time via decorator:**

```python
# In tool_decorator.py
MANAGED_TOOLS: Dict[str, ManagedToolDefinition] = {}

def register_mds_tool(...):
    def decorator(func):
        tool_def = ManagedToolDefinition(
            metadata=ToolMetadata(name=name, ...),
            business_rules=ToolBusinessRules(...),
            parameters=extract_parameters(params_model),
            implementation=func,
            params_model=params_model
        )
        MANAGED_TOOLS[name] = tool_def
        return validated_wrapper(tool_def, func)
    return decorator
```

**Tool imports trigger registration:**
```python
# In tests/api/conftest.py and tests/integration/conftest.py
# Auto-imports all tools from generated/ folder
import_tools_recursively(tools_generated_dir)
```

---

### 4. Tool Execution Flow

```
HTTP Request → FastAPI Router → Service Layer → Tool Registry → Tool Execution → Response
```

**Step-by-step:**

```python
# 1. API Layer (pydantic_api/routers/tool_session.py)
@router.post("/sessions/{session_id}/execute")
async def execute_tool(session_id: str, request: ToolRequest):
    return await service.execute_tool(session_id, request)

# 2. Service Layer (tool_sessionservice/service.py)
async def execute_tool(self, session_id: str, request: ToolRequest):
    # Get tool from registry
    tool_def = get_tool_definition(request.payload.tool_name)
    
    # Check policies
    if not tool_def.check_enabled():
        raise ToolDisabledError()
    if not tool_def.check_permission(user_permissions):
        raise PermissionError()
    
    # Create execution context
    ctx = MDSContext(
        user_id=request.user_id,
        session_id=session_id,
        casefile_id=session.casefile_id
    )
    
    # Execute tool (decorator handles validation)
    result = await tool_def.implementation(ctx, **request.payload.parameters)
    
    # Record event
    session.events.append(ToolEvent(...))
    
    return ToolResponse(status=RequestStatus.COMPLETED, payload=result)

# 3. Tool Decorator (tool_decorator.py)
async def validated_wrapper(tool_def, func):
    # Validate parameters with Pydantic model
    validated_params = tool_def.params_model(**params)
    
    # Execute actual tool function
    result = await func(ctx, **validated_params.model_dump())
    
    # Wrap in ToolResponse envelope
    return ToolResponse(...)
```

---

## Data Models Architecture

### Three-Layer Pattern

**Layer 1: Domain Models (`pydantic_models/`)**
- Purpose: Core business entities and operations
- Organized by: Purpose (base, canonical, operations, views, workspace)
- Used by: All layers

**Layer 2: Integration Models (`pydantic_ai_integration/integrations/`)**
- Purpose: External API contracts
- Organized by: Integration type (google_workspace, etc.)
- Used by: Tool implementations calling external services

**Layer 3: Generated Tools (`pydantic_ai_integration/tools/generated/`)**
- Purpose: YAML-generated tool implementations
- Organized by: Domain/subdomain (matches YAML structure)
- Used by: Service layer for tool execution

### Purpose-Based Organization

**pydantic_models/base/**
- `envelopes.py`: BaseRequest[T], BaseResponse[T] generic wrappers
- `types.py`: RequestStatus enum, shared primitives

**pydantic_models/canonical/**
- `tool_session.py`: ToolSession, ToolEvent
- `casefile.py`: CasefileModel
- `acl.py`: CasefileACL, ACLEntry
- `chat_session.py`: ChatSession, ChatMessage

**pydantic_models/operations/**
- `tool_session_ops.py`: SessionCreatedPayload, SessionListPayload
- `tool_execution_ops.py`: ToolRequest, ToolResponse, ToolRequestPayload
- `casefile_ops.py`: CasefileCreateRequest, CasefileUpdateRequest
- `chat_session_ops.py`: ChatMessageRequest, ChatMessageResponse

**pydantic_models/views/**
- `casefile_views.py`: CasefileSummary, CasefileListItem
- `session_views.py`: SessionSummary, SessionListItem

**pydantic_models/workspace/**
- `gmail.py`: GmailMessage, GmailAttachment
- `drive.py`: DriveFile, DrivePermission
- `sheets.py`: SheetData, SheetRange

---

## Tool Definition Components

### ManagedToolDefinition (Single Source of Truth)

```python
class ManagedToolDefinition(BaseModel):
    # WHAT: Pure metadata
    metadata: ToolMetadata  # name, description, version, category, tags
    
    # WHEN/WHERE: Business logic
    business_rules: ToolBusinessRules  # enabled, auth, permissions, timeout
    session_policies: ToolSessionPolicies  # session requirements
    casefile_policies: ToolCasefilePolicies  # casefile requirements
    audit_config: ToolAuditConfig  # audit trail configuration
    
    # WHAT: Input specification
    parameters: List[ToolParameterDef]  # parameter definitions
    
    # HOW: Execution
    implementation: Callable  # actual async function
    params_model: Type[BaseModel]  # Pydantic validation model
    
    # WHEN: Audit
    registered_at: str  # ISO 8601 timestamp
```

### Validation and Authorization

**Parameter validation:**
```python
# Happens in decorator's validated_wrapper
validated_params = tool_def.params_model(**raw_params)
```

**Authorization checks:**
```python
# Service layer checks before execution
tool_def.check_enabled()  # enabled, not deprecated
tool_def.check_permission(user_permissions)  # required permissions
```

**Session/Casefile policies:**
```python
# Service layer enforces
if tool_def.session_policies.requires_active_session:
    validate_session_active(session_id)
if tool_def.casefile_policies.requires_casefile:
    validate_casefile_exists(casefile_id)
```

---

## Testing Strategy

### Three Test Layers

**Unit Tests (`tests/unit/`)**
- Test: Tool implementation logic
- Mock: External APIs, MDSContext
- Generated: From YAML via test_template.py.jinja2
- Run: `pytest tests/unit/`

**Integration Tests (`tests/integration/`)**
- Test: Service layer orchestration, policy enforcement
- Mock: External APIs only
- Generated: From YAML via integration_test_template.py.jinja2
- Run: `pytest tests/integration/`

**API Tests (`tests/api/`)**
- Test: HTTP endpoints, JWT auth, end-to-end flow
- Mock: External APIs only
- Generated: From YAML via api_test_template.py.jinja2
- Run: `pytest tests/api/`

### Test Organization

**Mirrors tool structure:**
```
config/tools/communication/email/gmail_send.yaml
  ↓
src/.../generated/communication/email/gmail_send.py
  ↓
tests/unit/communication/email/test_gmail_send.py
tests/integration/communication/email/test_gmail_send_integration.py
tests/api/communication/email/test_gmail_send_api.py
```

### Fixtures (`tests/fixtures/`)

**common.py:**
- `mock_context()`: Mock MDSContext
- `mock_user()`: Mock user data
- `mock_casefile()`: Mock casefile
- `mock_session()`: Mock tool session

**auth_fixtures.py:**
- `mock_jwt_token()`: Valid JWT token
- `auth_headers()`: Authorization headers

---

## Development Workflow

### Adding New Tool

1. **Create YAML definition**
   ```bash
   # config/tools/utilities/debugging/my_new_tool.yaml
   ```

2. **Generate code**
   ```bash
   python scripts/generate_tools.py
   # or: python -m src.pydantic_ai_integration.tools.factory
   ```

3. **Run tests**
   ```bash
   pytest tests/unit/utilities/debugging/test_my_new_tool.py -v
   ```

4. **Commit YAML + generated files**
   ```bash
   git add config/tools/utilities/debugging/my_new_tool.yaml
   git add src/.../generated/utilities/debugging/my_new_tool.py
   git add tests/unit/utilities/debugging/test_my_new_tool.py
   git commit -m "Add my_new_tool"
   ```

### Modifying Existing Tool

1. **Edit YAML**
   ```bash
   # config/tools/.../existing_tool.yaml
   ```

2. **Regenerate**
   ```bash
   python scripts/generate_tools.py
   ```

3. **Test changes**
   ```bash
   pytest tests/unit/.../test_existing_tool.py -v
   ```

4. **Commit YAML changes** (generated files update automatically)

### Changing Generation Templates

1. **Edit Jinja2 template**
   ```bash
   # src/.../tools/factory/templates/tool_template.py.jinja2
   ```

2. **Regenerate ALL tools**
   ```bash
   python scripts/generate_tools.py
   ```

3. **Test impact**
   ```bash
   pytest tests/unit/ -v
   ```

---

## Key Principles

### YAML as Single Source of Truth

- **YAML files are versioned** (in git)
- **Generated Python is disposable** (can regenerate anytime)
- **YAML structure determines folder structure** (domain/subdomain)
- **category field is legacy** (ignored for folder structure)

### Purpose-Based Model Organization

- **Not by domain** (no user/, casefile/, tool/ folders)
- **By purpose:** base/, canonical/, operations/, views/, workspace/
- **Benefit:** Clear separation of concerns, easy to find models

### Tool Registration at Import Time

- **Decorator runs when module imported** (not when function called)
- **MANAGED_TOOLS populated automatically** (global registry)
- **conftest.py imports all tools** (before tests run)

### Three-Layer Architecture

1. **Domain models** (pydantic_models/) - Business entities
2. **Integration models** (integrations/) - External APIs
3. **Generated tools** (generated/) - YAML-based implementations

---

## Getting Started Manual

### Prerequisites

- Python 3.9+
- Git
- Google Cloud Platform account (for Google Workspace tools)

### Initial Setup

**1. Clone and install:**
```powershell
git clone <repository-url>
cd my-tiny-data-collider
pip install -e ".[dev]"
```

This installs:
- All dependencies (pydantic, fastapi, google APIs, etc.)
- Development tools (pytest, black, ruff)
- Package in editable mode (code changes take effect immediately)
- `generate-tools` console command

**2. Configure environment:**

Create `.env` file in project root:
```bash
# Google Workspace
GOOGLE_APPLICATION_CREDENTIALS=path/to/credentials.json
GMAIL_USER_EMAIL=user@domain.com

# JWT Authentication
JWT_SECRET_KEY=your-secret-key-here
JWT_ALGORITHM=HS256

# Firestore
FIRESTORE_PROJECT_ID=your-project-id
```

**3. Generate tools:**
```powershell
generate-tools
# or: python scripts/generate_tools.py
```

**4. Run tests:**
```powershell
pytest tests/unit/ -v
pytest tests/integration/ -v
pytest tests/api/ -v
```

**5. Start API server:**
```powershell
uvicorn src.pydantic_api.app:app --reload
```

### Configuration Reference

**Tool session policies** (in YAML):
```yaml
session_policies:
  requires_active_session: true   # Must have active session
  allow_new_session: false        # Cannot create new session
  allow_session_resume: true      # Can resume inactive session
  session_event_type: request     # Event type for audit trail
```

**Tool casefile policies** (in YAML):
```yaml
casefile_policies:
  requires_casefile: true         # Must have casefile context
  allowed_casefile_states: [active]
  enforce_access_control: true    # Check ACL permissions
  audit_casefile_changes: true    # Log to casefile audit trail
```

**Tool business rules** (in YAML):
```yaml
business_rules:
  enabled: true                   # Tool available for execution
  requires_auth: true             # Requires authenticated user
  required_permissions: ['gmail:send']  # Required permissions
  timeout_seconds: 30             # Execution timeout
```

### API Endpoints

**Tool sessions:**
```
POST   /tool_sessions/                      # Create session
GET    /tool_sessions/{session_id}          # Get session details
DELETE /tool_sessions/{session_id}          # End session
POST   /tool_sessions/{session_id}/execute  # Execute tool
```

**Casefiles:**
```
POST   /casefiles/                  # Create casefile
GET    /casefiles/{casefile_id}     # Get casefile
PATCH  /casefiles/{casefile_id}     # Update casefile
DELETE /casefiles/{casefile_id}     # Delete casefile
POST   /casefiles/{casefile_id}/acl # Manage ACL
```

**Chat sessions:**
```
POST   /chat_sessions/                        # Create chat session
GET    /chat_sessions/{session_id}            # Get chat session
POST   /chat_sessions/{session_id}/messages   # Send message
```

### Daily Workflow

**Adding new tool:**
1. Create YAML: `config/tools/domain/subdomain/my_tool.yaml`
2. Run: `generate-tools`
3. Test: `pytest tests/unit/domain/subdomain/test_my_tool.py -v`
4. Commit YAML and generated files

**Modifying tool:**
1. Edit YAML: `config/tools/domain/subdomain/existing_tool.yaml`
2. Run: `generate-tools`
3. Test: `pytest tests/unit/domain/subdomain/test_existing_tool.py -v`
4. Commit YAML changes

**Changing templates:**
1. Edit template: `src/.../tools/factory/templates/*.jinja2`
2. Regenerate all: `generate-tools`
3. Test all: `pytest tests/unit/ -v`
4. Commit template + regenerated files

### Troubleshooting

**Import errors:**
```powershell
pip install -e ".[dev]"  # Reinstall package
```

**Tool not found:**
```powershell
generate-tools           # Regenerate tools
pytest tests/unit/ -v    # Verify registration
```

**Test failures:**
```powershell
pytest tests/unit/path/to/test.py -v -s  # Verbose with output
pytest --lf                              # Run last failed
```

**API not starting:**
- Check `.env` file exists with required variables
- Verify port 8000 not in use: `netstat -ano | findstr :8000`
- Check logs for missing dependencies

### When to Reinstall

Run `pip install -e ".[dev]"` after:
- Git pull with dependency changes
- Modifying `setup.py` dependencies
- Setting up on new machine
- Virtual environment recreation
