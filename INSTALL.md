# Installation and Setup Guide

Complete guide for new users to install, configure, and start developing with My Tiny Data Collider.

---

## Prerequisites

**Required:**
- Python 3.9 or higher
- Git
- pip (Python package installer)

**Optional (for Google Workspace tools):**
- Google Cloud Platform account
- Service account credentials JSON file

---

## Installation

### 1. Clone Repository

```powershell
git clone https://github.com/MSD21091969/my-tiny-data-collider.git
cd my-tiny-data-collider
```

### 2. Create Virtual Environment (Recommended)

```powershell
# Create virtual environment
python -m venv venv

# Activate (Windows)
.\venv\Scripts\activate

# Activate (Linux/Mac)
source venv/bin/activate
```

### 3. Install Package

```powershell
pip install -e ".[dev]"
```

**What this does:**
- Installs all runtime dependencies (pydantic, fastapi, google-api-python-client, etc.)
- Installs development tools (pytest, black, ruff, mypy)
- Installs package in **editable mode** (code changes take effect immediately, no reinstall needed)
- Creates `generate-tools` console command for tool generation

**Verify installation:**
```powershell
generate-tools --help
python -c "from src.pydantic_models.base import BaseRequest; print('✓ Package installed')"
```

---

## Environment Configuration

### Required Environment Variables

Create `.env` file in project root:

```bash
# Google Workspace APIs (if using Gmail/Drive/Sheets tools)
GOOGLE_APPLICATION_CREDENTIALS=path/to/service-account-credentials.json
GMAIL_USER_EMAIL=your-email@domain.com

# JWT Authentication (for API endpoints)
JWT_SECRET_KEY=your-secret-key-here-change-in-production
JWT_ALGORITHM=HS256

# Firestore (for persistence)
FIRESTORE_PROJECT_ID=your-gcp-project-id
```

### Google Cloud Setup (Optional)

If using Google Workspace tools (Gmail, Drive, Sheets):

1. **Create GCP project:** https://console.cloud.google.com/
2. **Enable APIs:**
   - Gmail API
   - Google Drive API
   - Google Sheets API
3. **Create service account:**
   - IAM & Admin → Service Accounts → Create
   - Download JSON key file
4. **Domain-wide delegation** (for Gmail):
   - Enable domain-wide delegation on service account
   - Add OAuth scopes in Google Workspace Admin

**Required OAuth Scopes:**
```
https://www.googleapis.com/auth/gmail.readonly
https://www.googleapis.com/auth/gmail.send
https://www.googleapis.com/auth/drive.readonly
https://www.googleapis.com/auth/spreadsheets.readonly
```

---

## Development Setup

### 1. Tool Classification System

All tools follow **domain/subdomain** folder structure matching YAML organization:

```
config/tools/
├── automation/pipelines/         # Domain: automation, Subdomain: pipelines
├── communication/email/          # Domain: communication, Subdomain: email
├── utilities/debugging/          # Domain: utilities, Subdomain: debugging
└── workspace/google/             # Domain: workspace, Subdomain: google
```

**YAML classification fields:**
```yaml
classification:
  domain: communication          # Top-level category
  subdomain: email               # Specific area
  capability: create             # CRUD operation
  complexity: atomic             # atomic|composite|pipeline
  maturity: stable               # experimental|beta|stable|deprecated
```

This classification determines:
- **Folder structure:** `config/tools/{domain}/{subdomain}/tool.yaml`
- **Generated code location:** `src/.../generated/{domain}/{subdomain}/tool.py`
- **Test organization:** `tests/unit/{domain}/{subdomain}/test_tool.py`

### 2. Generate Tools

**Generate all tools from YAML definitions:**
```powershell
generate-tools
```

**What this does:**
- Reads all YAML files from `config/tools/**/*.yaml`
- Generates tool implementations in `src/pydantic_ai_integration/tools/generated/{domain}/{subdomain}/`
- Generates unit tests in `tests/unit/{domain}/{subdomain}/`
- Generates integration tests in `tests/integration/{domain}/{subdomain}/`
- Generates API tests in `tests/api/{domain}/{subdomain}/`
- Creates `__init__.py` files for proper Python package structure

**Output structure:**
```
config/tools/communication/email/gmail_send.yaml
    ↓ generates
src/.../generated/communication/email/gmail_send.py
tests/unit/communication/email/test_gmail_send.py
tests/integration/communication/email/test_gmail_send_integration.py
tests/api/communication/email/test_gmail_send_api.py
```

### 3. Run Tests

**Unit tests** (fast, mocked):
```powershell
pytest tests/unit/ -v
```

**Integration tests** (service layer):
```powershell
pytest tests/integration/ -v
```

**API tests** (HTTP endpoints):
```powershell
pytest tests/api/ -v
```

**Run specific test:**
```powershell
pytest tests/unit/communication/email/test_gmail_send.py -v
```

**Run with coverage:**
```powershell
pytest tests/unit/ --cov=src --cov-report=html
```

### 4. Start API Server

```powershell
uvicorn src.pydantic_api.app:app --reload
```

**Verify server:**
- API docs: http://localhost:8000/docs
- Health check: http://localhost:8000/health

---

## Tool Lifecycle

Understanding the complete tool development workflow:

### 1. YAML Definition (Source of Truth)

Create tool definition with classification:

```yaml
# config/tools/communication/email/gmail_send_message.yaml
name: gmail_send_message
description: "Send email via Gmail API"

classification:
  domain: communication        # Folder structure
  subdomain: email             # Folder structure
  capability: create           # CRUD operation type
  complexity: atomic           # Single-purpose tool
  maturity: stable             # Production-ready

business_rules:
  enabled: true
  requires_auth: true
  required_permissions: ['gmail:send']
  timeout_seconds: 30

session_policies:
  requires_active_session: true
  allow_new_session: false

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

**YAML versioning:**
- YAML files are versioned in Git (single source of truth)
- Changes to YAML = changes to tool behavior
- Commit YAML changes with semantic commit messages
- Generated Python code is disposable (can regenerate anytime)

### 2. Code Generation

Run generation:
```powershell
generate-tools
```

**Generated files (organized by classification):**
```
src/pydantic_ai_integration/tools/generated/
└── communication/              # domain from YAML
    └── email/                  # subdomain from YAML
        └── gmail_send_message.py

tests/unit/
└── communication/
    └── email/
        └── test_gmail_send_message.py

tests/integration/
└── communication/
    └── email/
        └── test_gmail_send_message_integration.py

tests/api/
└── communication/
    └── email/
        └── test_gmail_send_message_api.py
```

### 3. Tool Registration

**Automatic at import time:**
```python
# Generated tool code
@register_mds_tool(
    name="gmail_send_message",
    params_model=GmailSendMessageParams,
    description="Send email via Gmail API"
)
async def gmail_send_message(ctx: MDSContext, to: str, subject: str, body: str):
    # Implementation
    pass
```

**Tool registry:**
```python
# All tools stored in global registry
from src.pydantic_ai_integration.tool_decorator import MANAGED_TOOLS

# Check registered tools
print(f"Registered: {len(MANAGED_TOOLS)} tools")
print(MANAGED_TOOLS.keys())
```

### 4. Testing

**Test organization mirrors classification:**
```
tests/unit/communication/email/test_gmail_send.py          # Unit tests
tests/integration/communication/email/test_gmail_send_integration.py  # Service tests
tests/api/communication/email/test_gmail_send_api.py       # HTTP tests
```

**Run tests by classification:**
```powershell
# Test all email tools
pytest tests/unit/communication/email/ -v

# Test all communication tools
pytest tests/unit/communication/ -v

# Test specific domain
pytest tests/unit/automation/ -v
```

### 5. Execution Flow

```
HTTP Request
    ↓
FastAPI Router (/tool_sessions/{id}/execute)
    ↓
Service Layer (ToolSessionService.execute_tool)
    ↓
Policy Enforcement (check enabled, permissions, session, casefile)
    ↓
Tool Registry Lookup (MANAGED_TOOLS[tool_name])
    ↓
Parameter Validation (Pydantic model)
    ↓
Tool Execution (async function call)
    ↓
Audit Trail (record event)
    ↓
Response (BaseResponse[ToolResponse])
```

---

## Configuration Reference

### Tool Session Policies

Control session requirements for tool execution:

```yaml
session_policies:
  requires_active_session: true     # Must have active session (status=active)
  allow_new_session: false          # Can create session if none exists
  allow_session_resume: true        # Can resume inactive session
  session_event_type: request       # Event type in audit trail
```

### Tool Casefile Policies

Control casefile context requirements:

```yaml
casefile_policies:
  requires_casefile: true           # Must execute within casefile context
  allowed_casefile_states: [active] # Casefile must be in these states
  enforce_access_control: true      # Check user ACL permissions
  audit_casefile_changes: true      # Log to casefile audit trail
```

### Tool Business Rules

Control tool availability and execution:

```yaml
business_rules:
  enabled: true                     # Tool available for execution
  requires_auth: true               # Requires authenticated user
  required_permissions:             # User must have these permissions
    - gmail:send
    - gmail:read
  timeout_seconds: 30               # Max execution time
  rate_limit:
    requests_per_minute: 10         # Rate limiting
  allowed_environments:             # Where tool can execute
    - development
    - production
```

### Tool Classification Reference

**Domain examples:**
- `automation` - Orchestration, pipelines, workflows
- `communication` - Email, chat, notifications
- `utilities` - Debugging, testing, helpers
- `workspace` - External integrations (Google, Microsoft)

**Subdomain examples:**
- `automation/pipelines` - Multi-step orchestration
- `communication/email` - Gmail, SMTP tools
- `utilities/debugging` - Echo, test tools
- `workspace/google` - Drive, Sheets, Gmail

**Capability (CRUD):**
- `create` - Create new resources
- `read` - Fetch/query data
- `update` - Modify existing resources
- `delete` - Remove resources
- `list` - Bulk read operations
- `search` - Query with filters

**Complexity:**
- `atomic` - Single operation, no dependencies
- `composite` - Calls multiple atomic tools
- `pipeline` - Multi-step workflow with state

**Maturity:**
- `experimental` - In development, may change
- `beta` - Feature complete, testing
- `stable` - Production-ready
- `deprecated` - Scheduled for removal

---

## Daily Workflow

### Adding New Tool

1. **Create YAML definition:**
   ```powershell
   # File: config/tools/communication/sms/send_sms.yaml
   ```

2. **Define classification:**
   ```yaml
   classification:
     domain: communication
     subdomain: sms
     capability: create
     complexity: atomic
     maturity: beta
   ```

3. **Generate code:**
   ```powershell
   generate-tools
   ```

4. **Verify structure created:**
   ```
   src/.../generated/communication/sms/send_sms.py ✓
   tests/unit/communication/sms/test_send_sms.py ✓
   ```

5. **Run tests:**
   ```powershell
   pytest tests/unit/communication/sms/test_send_sms.py -v
   ```

6. **Commit YAML + generated files:**
   ```powershell
   git add config/tools/communication/sms/send_sms.yaml
   git add src/.../generated/communication/sms/
   git add tests/unit/communication/sms/
   git commit -m "feat(communication): Add send_sms tool"
   ```

### Modifying Existing Tool

1. **Edit YAML definition:**
   ```powershell
   # Edit config/tools/communication/email/gmail_send.yaml
   ```

2. **Regenerate:**
   ```powershell
   generate-tools
   ```

3. **Test changes:**
   ```powershell
   pytest tests/unit/communication/email/test_gmail_send.py -v
   ```

4. **Commit YAML only** (generated files update automatically):
   ```powershell
   git add config/tools/communication/email/gmail_send.yaml
   git commit -m "refactor(communication): Update gmail_send timeout to 60s"
   ```

### Changing Tool Classification

If you need to reorganize tools (change domain/subdomain):

1. **Move YAML file:**
   ```powershell
   # From: config/tools/old_domain/old_sub/tool.yaml
   # To: config/tools/new_domain/new_sub/tool.yaml
   git mv config/tools/old_domain/old_sub/tool.yaml config/tools/new_domain/new_sub/tool.yaml
   ```

2. **Update classification in YAML:**
   ```yaml
   classification:
     domain: new_domain
     subdomain: new_sub
   ```

3. **Regenerate (creates new structure, old files become orphans):**
   ```powershell
   generate-tools
   ```

4. **Delete old generated files:**
   ```powershell
   git rm -r src/.../generated/old_domain/old_sub/
   git rm -r tests/unit/old_domain/old_sub/
   ```

5. **Commit reorganization:**
   ```powershell
   git add -A
   git commit -m "refactor: Move tool from old_domain/old_sub to new_domain/new_sub"
   ```

---

## Troubleshooting

### Import Errors

**Symptom:** `ModuleNotFoundError: No module named 'src'`

**Solution:**
```powershell
pip install -e ".[dev]"
```

### Tool Not Found in Registry

**Symptom:** `KeyError: 'tool_name' not in MANAGED_TOOLS`

**Solutions:**
1. Regenerate tools:
   ```powershell
   generate-tools
   ```

2. Check tool imports in conftest.py (should auto-import all from `generated/`):
   ```python
   # tests/api/conftest.py or tests/integration/conftest.py
   import_tools_recursively(tools_generated_dir)
   ```

3. Verify tool registration:
   ```python
   python -c "from src.pydantic_ai_integration.tool_decorator import MANAGED_TOOLS; print(MANAGED_TOOLS.keys())"
   ```

### Test Failures After Reorganization

**Symptom:** Tests fail with import errors after moving tools

**Solution:**
```powershell
# Clean pytest cache
Remove-Item -Recurse -Force .pytest_cache

# Regenerate all
generate-tools

# Reinstall package
pip install -e ".[dev]"

# Run tests
pytest tests/unit/ -v
```

### Generated Files in Wrong Location

**Symptom:** Tools generated in old category-based folders instead of domain/subdomain

**Cause:** Using old YAML with `category` field instead of `classification`

**Solution:**
1. Update YAML to use classification:
   ```yaml
   classification:
     domain: communication
     subdomain: email
   ```

2. Remove deprecated `category` field from YAML

3. Regenerate:
   ```powershell
   generate-tools
   ```

### API Server Won't Start

**Symptom:** `uvicorn` fails with missing `.env` or import errors

**Solutions:**
1. Check `.env` file exists and has required variables
2. Check port 8000 not in use:
   ```powershell
   netstat -ano | findstr :8000
   ```
3. Reinstall dependencies:
   ```powershell
   pip install -e ".[dev]"
   ```
4. Check logs for specific error

### YAML Validation Errors

**Symptom:** `generate-tools` fails with YAML parse errors

**Common issues:**
- Incorrect indentation (use 2 spaces)
- Missing required fields (`name`, `classification`, `parameters`)
- Invalid classification values (check allowed domains/subdomains)

**Validation:**
```powershell
# Test YAML syntax
python -c "import yaml; yaml.safe_load(open('config/tools/path/to/tool.yaml'))"
```

---

## When to Reinstall

Run `pip install -e ".[dev]"` after:

✅ **Git operations:**
- `git pull` with dependency changes in `setup.py` or `requirements.txt`
- Switching branches with different dependencies

✅ **Configuration changes:**
- Modifying `setup.py` (dependencies, entry points)
- Adding/removing packages

✅ **Environment issues:**
- Setting up on new machine
- Creating new virtual environment
- Python version upgrade

✅ **Import errors:**
- `ModuleNotFoundError` after reorganization
- Package structure changes

❌ **NOT needed after:**
- Editing YAML files
- Running `generate-tools`
- Modifying Python source files (editable mode handles this)
- Test failures (unless import-related)

---

## Next Steps

After installation:

1. **Read CONTRIBUTING.md** - Developer guidelines and coding standards
2. **Review README.md** - Complete architecture documentation
3. **Generate tools** - `generate-tools` to create initial codebase
4. **Run tests** - `pytest tests/unit/ -v` to validate setup
5. **Start developing** - Create your first tool YAML and test the workflow

**Questions?** Check:
- `README.md` - Architecture overview
- `CONTRIBUTING.md` - Development workflow
- `src/pydantic_models/README.md` - Model organization
- `src/pydantic_api/README.md` - API patterns
- `src/pydantic_ai_integration/README.md` - Tool development
