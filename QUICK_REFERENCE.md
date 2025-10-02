# Quick Reference Guide

**My Tiny Data Collider** - Essential commands and patterns for daily development

---

## 🚀 Quick Start

```bash
# Setup
python -m venv .venv
.venv\Scripts\activate  # Windows
pip install -r requirements.txt

# Generate a tool
python -m scripts.main config/tools/echo_tool.yaml

# Run tests
python -m pytest tests/generated/test_echo_tool.py -v
```

---

## 🏭 Tool Factory Commands

```bash
# Generate single tool
python -m scripts.main config/tools/my_tool.yaml

# Generate all tools
python -m scripts.main config/tools/*.yaml

# Generate with verbose output
python -m scripts.main config/tools/my_tool.yaml --verbose
```

**Output:**
- Tool: `src/pydantic_ai_integration/tools/generated/my_tool.py`
- Tests: `tests/generated/test_my_tool.py`

---

## 🧪 Testing Commands

```bash
# Unit tests (tool layer)
python -m pytest tests/generated/ -v

# Integration tests (service layer)
python -m pytest tests/integration/ -v

# API tests (HTTP layer)
python -m pytest tests/api/ -v

# All tests
python -m pytest tests/ -v --tb=short

# With coverage
python -m pytest tests/ --cov=src --cov-report=html

# Specific test file
python -m pytest tests/generated/test_echo_tool.py -v

# Specific test function
python -m pytest tests/generated/test_echo_tool.py::TestToolEchotool::test_echo_once -v

# Watch mode (requires pytest-watch)
ptw tests/generated/ -- -v
```

---

## 📝 YAML Tool Definition Template

```yaml
name: my_tool
display_name: "My Tool"
description: "What this tool does"
category: utilities
version: "1.0.0"

# Access control
business_rules:
  enabled: true
  requires_auth: true
  required_permissions:
    - tools:execute
  timeout_seconds: 30

# Session lifecycle
session_policies:
  requires_active_session: true
  allow_new_session: false
  log_request_payload: true

# Casefile access
casefile_policies:
  requires_casefile: false
  enforce_access_control: true

# Parameters
parameters:
  - name: input_text
    type: string
    required: true
    min_length: 1
    max_length: 1000
    description: "Input text to process"

# Implementation
implementation:
  type: simple
  simple:
    logic: |
      result = {"processed": input_text.upper()}

# Audit
audit_events:
  success_event: tool_success
  log_response_fields:
    - processed
```

---

## 🔍 Common Patterns

### **Creating MDSContext**

```python
from src.pydantic_ai_integration.dependencies import MDSContext

ctx = MDSContext(
    user_id="user_123",
    session_id="ts_251002_abc",
    casefile_id="cf_251002_xyz"  # Optional
)
```

### **Calling a Tool (Unit Test)**

```python
from src.pydantic_ai_integration.tools.generated.echo_tool import echo_tool

result = await echo_tool(
    ctx=ctx,
    message="hello",
    repeat_count=3
)
```

### **Calling via Service Layer (Integration Test)**

```python
from src.tool_sessionservice.service import ToolSessionService
from src.pydantic_models.tool_session.models import ToolRequest, ToolRequestPayload

service = ToolSessionService()

request = ToolRequest(
    user_id="user_123",
    operation="tool_execution",
    payload=ToolRequestPayload(
        tool_name="echo_tool",
        parameters={"message": "hello", "repeat_count": 3}
    )
)

response = await service.execute_tool(request)
```

### **Registering Audit Event**

```python
ctx.register_event(
    tool_name="my_tool",
    parameters={"input": "value"},
    result_summary={"output": "result"},
    duration_ms=150
)
```

---

## 📊 Model Quick Reference

### **API Layer**
```python
from src.pydantic_models.shared.base_models import RequestEnvelope

envelope = RequestEnvelope(
    request={"tool_name": "echo_tool", "parameters": {...}},
    auth_token="Bearer ...",
    trace_id=uuid4()
)
```

### **Service Layer**
```python
from src.pydantic_models.tool_session.models import (
    ToolRequest,
    ToolRequestPayload,
    ToolResponse
)

request = ToolRequest(
    user_id="user_123",
    operation="tool_execution",
    payload=ToolRequestPayload(
        tool_name="echo_tool",
        parameters={...}
    )
)
```

### **Tool Layer**
```python
from src.pydantic_ai_integration.dependencies import MDSContext

async def my_tool(
    ctx: MDSContext,
    param1: str,
    param2: int = 10
) -> Dict[str, Any]:
    return {"result": "value"}
```

---

## 🔐 Policy Checklist

When defining a tool, consider:

- [ ] **Requires authentication?** → Set `business_rules.requires_auth: true`
- [ ] **Needs permissions?** → Add to `business_rules.required_permissions`
- [ ] **Needs active session?** → Set `session_policies.requires_active_session: true`
- [ ] **Needs casefile?** → Set `casefile_policies.requires_casefile: true`
- [ ] **User must own casefile?** → Set `casefile_policies.enforce_access_control: true`
- [ ] **Log request data?** → Set `session_policies.log_request_payload: true`
- [ ] **What to audit?** → Configure `audit_events.log_response_fields`

---

## 🐛 Debugging Tips

### **Check Tool Registry**
```python
from src.pydantic_ai_integration.tool_decorator import MANAGED_TOOLS, get_tool_names

print(get_tool_names())  # List all registered tools
tool_def = MANAGED_TOOLS["echo_tool"]  # Get tool definition
```

### **View Tool Policies**
```python
tool_def = MANAGED_TOOLS["echo_tool"]
print(tool_def.business_rules)
print(tool_def.session_policies)
print(tool_def.casefile_policies)
```

### **Check Context Events**
```python
ctx = MDSContext(user_id="test", session_id="test_session")
await my_tool(ctx, ...)

print(f"Events: {len(ctx.tool_events)}")
for event in ctx.tool_events:
    print(f"  - {event.tool_name}: {event.status}")
```

### **Validate Parameters**
```python
from src.pydantic_ai_integration.tools.generated.echo_tool import EchotoolParams

try:
    params = EchotoolParams(message="", repeat_count=1)
except ValidationError as e:
    print(e.errors())
```

---

## 📁 File Locations

```
Project Root
├── config/tools/              # YAML tool definitions
├── src/
│   ├── pydantic_api/routers/  # API endpoints
│   ├── communicationservice/  # Chat/agent service
│   ├── tool_sessionservice/   # Tool execution service
│   ├── casefileservice/       # Casefile management
│   └── pydantic_ai_integration/
│       ├── tools/generated/   # Generated tools (DO NOT EDIT)
│       ├── dependencies.py    # MDSContext
│       └── tool_decorator.py  # @register_mds_tool
├── tests/
│   ├── generated/             # Unit tests (tool layer)
│   ├── integration/           # Integration tests (service)
│   └── api/                   # API tests (HTTP)
├── templates/                 # Jinja2 templates
└── docs/                      # Architecture documentation
```

---

## 🔄 Workflow Examples

### **Add New Tool**
1. Create `config/tools/my_tool.yaml`
2. Run `python -m scripts.main config/tools/my_tool.yaml`
3. Test `python -m pytest tests/generated/test_my_tool.py -v`
4. Commit generated files

### **Modify Existing Tool**
1. Edit `config/tools/my_tool.yaml` (NOT the generated .py file)
2. Regenerate `python -m scripts.main config/tools/my_tool.yaml`
3. Re-run tests `python -m pytest tests/generated/test_my_tool.py -v`
4. Commit updated YAML and regenerated files

### **Change Tool Templates**
1. Edit `templates/tool_template.py.jinja2` or `templates/test_template.py.jinja2`
2. Regenerate all tools `python -m scripts.main config/tools/*.yaml`
3. Run full test suite `python -m pytest tests/ -v`
4. Commit template changes and regenerated files

---

## 📚 Documentation Links

- **README**: Project overview and testing philosophy
- **Architecture**: `docs/LAYERED_ARCHITECTURE_FLOW.md`
- **Policies**: `docs/POLICY_AND_USER_ID_FLOW.md`
- **Foundation**: `docs/TOOLENGINEERING_FOUNDATION.md`

---

## 🆘 Common Issues

### **Tool Not Found**
```
ValueError: Tool 'my_tool' not registered
```
**Solution**: Ensure tool is imported (add to `__init__.py` or import in service)

### **Validation Error**
```
ValidationError: 1 validation error for MyToolParams
```
**Solution**: Check parameter constraints in YAML (min/max length/value)

### **Session Required**
```
SessionRequiredError: Tool requires active session
```
**Solution**: Create session first or set `session_policies.allow_new_session: true`

### **Permission Denied**
```
PermissionError: Missing permissions: ['tools:execute']
```
**Solution**: Ensure user has required permissions in `business_rules.required_permissions`

---

**Last Updated**: October 2, 2025  
**Version**: 0.1.0
