# My Tiny Data Collider 🔬

**A Pydantic-based Tool Engineering Framework for AI Agents & Users**

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![Pydantic v2](https://img.shields.io/badge/pydantic-v2-green.svg)](https://docs.pydantic.dev/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-teal.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/license-MIT-lightgrey.svg)](LICENSE)

---

## 🎯 Overview

**My Tiny Data Collider** is a declarative tool engineering framework that enables rapid development of AI-agent-aware and user-facing tools through YAML-driven code generation. Built on Pydantic v2, FastAPI, and a layered N-tier architecture, it provides:

- 🏭 **Tool Factory**: Generate Python tools from YAML specifications
- 🔐 **Policy-Driven Execution**: Declarative session, casefile, and audit policies
- 🧪 **Multi-Level Testing**: Unit, integration, and API-level test strategies
- 📊 **Ready-to-Use Toolsets**: Pre-built tools for common workflows
- 🔄 **Context Propagation**: `MDSContext` flows user_id, session_id, casefile_id through all layers
- 📦 **SOLID Integration**: Experimental Solid Pod storage (see `src/solidservice/`)

---

## 🏗️ Architecture

### **N-Tier Layered Architecture**

```
┌─────────────────────────────────────────────────────────────┐
│  API Layer (FastAPI)                                        │
│  - HTTP endpoints, JWT auth, RequestEnvelope                │
│  Location: src/pydantic_api/routers/                        │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  Service Layer (Business Logic)                             │
│  - Policy enforcement, orchestration                        │
│  - ToolRequest/Response, ChatRequest/Response               │
│  Location: src/communicationservice/, src/tool_sessionservice/
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  Tool Layer (Execution)                                     │
│  - Tool implementations, MDSContext                         │
│  Location: src/pydantic_ai_integration/tools/               │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  Persistence Layer (Firestore)                              │
│  - Casefile, session, event storage                         │
│  Location: src/casefileservice/, src/communicationservice/repository/
└─────────────────────────────────────────────────────────────┘
```

**Key Principle**: Each layer uses different request/response models, enabling clean separation of concerns and independent testing strategies.

---

## 🚀 Quick Start

### **1. Install Dependencies**

```bash
# Create virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac

# Install requirements
pip install -r requirements.txt
```

### **2. Configure Environment**

```bash
cp .env.example .env
# Edit .env with your Firestore credentials
```

### **3. Generate a Tool from YAML**

```bash
# Run the tool factory
python -m scripts.main config/tools/echo_tool.yaml

# Generated files:
# - src/pydantic_ai_integration/tools/generated/echo_tool.py
# - tests/generated/test_echo_tool.py
```

### **4. Run Tests**

```bash
# Unit tests (tool layer only)
python -m pytest tests/generated/test_echo_tool.py -v

# Integration tests (all layers)
python -m pytest tests/ -v --tb=short
```

---

## 🏭 Tool Factory: YAML → Python

### **Declarative Tool Definition**

The Tool Factory generates **complete Pydantic models** from YAML, including:
- ✅ Parameter models with validation (min/max, patterns, required/optional)
- ✅ Return type specifications
- ✅ Policy configurations (session, casefile, audit)
- ✅ Implementation logic (inline, API calls, data transforms)

```yaml
# config/tools/echo_tool.yaml
name: echo_tool
description: "Echoes input message with metadata"

# Business rules define access control
business_rules:
  requires_auth: true
  required_permissions:
    - tools:execute
  timeout_seconds: 10

# Session policies control lifecycle behavior
session_policies:
  requires_active_session: true
  allow_new_session: false
  log_request_payload: true

# Casefile policies govern data access
casefile_policies:
  requires_casefile: false
  enforce_access_control: true

# Parameters → Pydantic model with validation
parameters:
  - name: message
    type: string
    required: true
    min_length: 1          # → Field(min_length=1)
    max_length: 500        # → Field(max_length=500)
  - name: repeat_count
    type: integer
    default: 1             # → Field(default=1)
    min_value: 1           # → Field(ge=1)
    max_value: 10          # → Field(le=10)

# Implementation logic (inline or external)
implementation:
  type: simple
  simple:
    logic: |
      echoed_messages = [message for _ in range(repeat_count)]
      result = {
        "original_message": message,
        "echoed_messages": echoed_messages,
        "total_length": sum(len(m) for m in echoed_messages)
      }

# Return type specification
returns:
  type: object
  properties:
    original_message: {type: string}
    echoed_messages: {type: array, items: {type: string}}
    total_length: {type: integer}

# Audit configuration
audit_events:
  success_event: tool_success
  log_response_fields:
    - total_length
```

### **Generated Python Tool**

```python
from pydantic import BaseModel, Field
from src.pydantic_ai_integration.dependencies import MDSContext
from src.pydantic_ai_integration.tool_decorator import register_mds_tool

class EchotoolParams(BaseModel):
    message: str = Field(..., min_length=1, max_length=500)
    repeat_count: int = Field(default=1, ge=1, le=10)

@register_mds_tool(
    name="echo_tool",
    description="Echoes input message with metadata",
    requires_auth=True,
    required_permissions=["tools:execute"],
    session_policies={"requires_active_session": True, ...},
    casefile_policies={"enforce_access_control": True, ...},
    audit_config={"success_event": "tool_success", ...}
)
async def echo_tool(
    ctx: MDSContext,
    message: str,
    repeat_count: int = 1
) -> Dict[str, Any]:
    params = EchotoolParams(message=message, repeat_count=repeat_count)
    
    # Implementation from YAML
    echoed_messages = [params.message for _ in range(params.repeat_count)]
    result = {
        "original_message": params.message,
        "echoed_messages": echoed_messages,
        "total_length": sum(len(m) for m in echoed_messages)
    }
    
    # Audit trail
    ctx.register_event("echo_tool", params.model_dump(), result_summary=result)
    return result
```

---

## 📊 Ready-to-Use Toolsets

### **Currently Available**

| Tool | Purpose | Layer | Location |
|------|---------|-------|----------|
| `echo_tool` | Example/testing | Tool | `tools/generated/echo_tool.py` |
| `unified_example_tools` | Demonstration suite | Tool | `tools/unified_example_tools.py` |
| `agent_aware_tools` | Agent integration | Tool | `tools/agent_aware_tools.py` |

### **In Development**

| Toolset | Purpose | Status |
|---------|---------|--------|
| Google Workspace | Gmail, Drive, Sheets API integration | 🚧 Week 2 |
| Document Analysis | PDF parsing, OCR, extraction | 📋 Planned |
| Web Scraping | URL fetch, HTML parsing | 📋 Planned |

---

## 🧪 Testing Strategy: Multi-Level Validation

### **Testing Philosophy**

Different layers require different testing approaches. We test at three distinct API entry points to validate different concerns:

### **1. Unit Tests: Tool Layer (Pure Logic)**

**Purpose**: Test tool implementation in isolation  
**Entry Point**: Direct tool function call  
**What's Tested**: Parameter validation, business logic, return values  
**What's NOT Tested**: Policies, auth, session management  

```python
# tests/generated/test_echo_tool.py
@pytest.mark.asyncio
async def test_echo_once():
    """Unit test: tool logic only."""
    ctx = MDSContext(user_id='test_user', session_id='test_session')
    
    result = await echo_tool(ctx, message='hello', repeat_count=1)
    
    assert result['original_message'] == 'hello'
    assert len(result['echoed_messages']) == 1
    assert result['total_length'] == 5
```

**Abstract Problem Solved**: *"Does the tool's core logic produce correct outputs for given inputs?"*

**Req/Resp Model**: `MDSContext` + params → `Dict[str, Any]`

---

### **2. Integration Tests: Service Layer (Policy Enforcement)**

**Purpose**: Test policy enforcement and orchestration  
**Entry Point**: Service layer methods  
**What's Tested**: Session policies, casefile policies, permission checks, audit logging  
**What's NOT Tested**: HTTP routing, JWT parsing  

```python
# tests/integration/test_tool_session_service.py
@pytest.mark.asyncio
async def test_session_policy_enforcement():
    """Integration test: service layer policies."""
    service = ToolSessionService()
    
    # Create request with missing session
    request = ToolRequest(
        user_id="test_user",
        operation="tool_execution",
        payload=ToolRequestPayload(
            tool_name="echo_tool",
            parameters={"message": "test"}
        )
    )
    
    # Should fail: requires_active_session=True
    with pytest.raises(SessionRequiredError):
        await service.execute_tool(request)
    
    # Create session, then should succeed
    session = await service.create_session("test_user")
    request.session_id = session["session_id"]
    response = await service.execute_tool(request)
    
    assert response.status == RequestStatus.COMPLETED
    assert "echoed_messages" in response.payload.result
```

**Abstract Problem Solved**: *"Are access control rules enforced correctly before tool execution?"*

**Req/Resp Model**: `ToolRequest` → `ToolResponse` (service-layer models)

---

### **3. API Tests: HTTP Layer (End-to-End)**

**Purpose**: Test complete request flow including auth  
**Entry Point**: FastAPI HTTP endpoints  
**What's Tested**: JWT authentication, HTTP routing, trace IDs, error handling, response formats  
**What's NOT Tested**: (all layers tested together)  

```python
# tests/api/test_tools_router.py
@pytest.mark.asyncio
async def test_execute_tool_endpoint():
    """API test: full HTTP flow."""
    from fastapi.testclient import TestClient
    from src.pydantic_api.app import app
    
    client = TestClient(app)
    
    # Generate JWT token
    token = create_test_token(user_id="test_user", permissions=["tools:execute"])
    
    # HTTP request
    response = client.post(
        "/api/tools/execute",
        json={
            "request": {
                "tool_name": "echo_tool",
                "parameters": {"message": "hello"},
                "casefile_id": "cf_251002_abc"
            },
            "trace_id": "test-trace-123"
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    
    # HTTP assertions
    assert response.status_code == 200
    data = response.json()
    assert data["trace_id"] == "test-trace-123"
    assert "result" in data
    assert data["result"]["original_message"] == "hello"
```

**Abstract Problem Solved**: *"Does the entire system work correctly when accessed via HTTP, including authentication and error handling?"*

**Req/Resp Model**: `RequestEnvelope` (HTTP) → JSON response

---

### **Testing Matrix: What Each Level Validates**

| Concern | Unit (Tool) | Integration (Service) | API (HTTP) |
|---------|-------------|----------------------|-----------|
| **Business Logic** | ✅ Primary focus | ⚠️ Smoke test | ⚠️ Smoke test |
| **Parameter Validation** | ✅ Exhaustive | ⚠️ Sample cases | ⚠️ Sample cases |
| **Policy Enforcement** | ❌ Not tested | ✅ Primary focus | ✅ Verified |
| **Authentication** | ❌ Not tested | ⚠️ Mocked | ✅ Primary focus |
| **Session Management** | ❌ Not tested | ✅ Primary focus | ✅ Verified |
| **Casefile Access Control** | ❌ Not tested | ✅ Primary focus | ✅ Verified |
| **Audit Trail** | ✅ Event creation | ✅ Persistence | ✅ End-to-end |
| **HTTP Routing** | ❌ Not applicable | ❌ Not applicable | ✅ Primary focus |
| **Error Handling** | ✅ Tool errors | ✅ Policy violations | ✅ HTTP codes |
| **Performance** | ✅ Tool speed | ⚠️ Service overhead | ✅ Full stack |

**Legend**: ✅ Primary focus | ⚠️ Tested but not focus | ❌ Not tested at this level

---

### **Test Discovery & Execution**

```bash
# Run all tests
python -m pytest tests/ -v

# Run by layer
python -m pytest tests/generated/ -v           # Unit tests (tool layer)
python -m pytest tests/integration/ -v         # Integration tests (service layer)
python -m pytest tests/api/ -v                 # API tests (HTTP layer)

# Run with coverage
python -m pytest tests/ --cov=src --cov-report=html

# Run specific test type
python -m pytest tests/ -m "unit" -v           # Unit tests only
python -m pytest tests/ -m "integration" -v    # Integration tests only
python -m pytest tests/ -m "api" -v            # API tests only
```

---

## 🔐 Policy System

Policies are **defined in YAML**, **stored in `ManagedToolDefinition`**, and **enforced at the service layer**.

### **Policy Types**

| Policy | Purpose | Example Use Case |
|--------|---------|------------------|
| **Business Rules** | Access control, availability | "Requires `tools:execute` permission" |
| **Session Policies** | Session lifecycle | "Must have active session, log all requests" |
| **Casefile Policies** | Data access control | "Enforce user owns casefile before access" |
| **Audit Config** | Compliance logging | "Log total_length field, redact sensitive data" |

### **Enforcement Flow**

```
1. Tool defined in YAML with policies
2. Tool Factory generates Python code
3. @register_mds_tool stores policies in MANAGED_TOOLS
4. Service layer reads policies before execution
5. Policies enforced (auth, session, casefile checks)
6. Tool executes if all policies pass
7. Audit trail created per audit_config
```

**Documentation**: See [docs/POLICY_AND_USER_ID_FLOW.md](docs/POLICY_AND_USER_ID_FLOW.md) and [docs/LAYERED_ARCHITECTURE_FLOW.md](docs/LAYERED_ARCHITECTURE_FLOW.md)

---

## 🧩 Context Propagation: MDSContext

`MDSContext` is the unified context object that flows through all layers:

```python
class MDSContext(BaseModel):
    # Core identifiers
    user_id: str                            # From JWT (always required)
    session_id: str                         # From session store (always required)
    casefile_id: Optional[str]              # From request (optional)
    
    # Audit trail
    tool_events: List[ToolEvent]            # Events registered during execution
    
    # State management
    transaction_context: Dict[str, Any]     # Request-scoped state
    persistent_state: Dict[str, Any]        # Cross-session state
    
    # Tool chaining
    previous_tools: List[Dict[str, Any]]    # Execution history
    next_planned_tools: List[Dict[str, Any]] # Planned chain
```

**Flow**:
```
JWT → user_id → MDSContext → Tool → Audit Trail
```

---

## 🗂️ Project Structure

```
my-tiny-data-collider/
├── config/
│   └── tools/                  # YAML tool definitions
│       └── echo_tool.yaml
├── docs/                       # Architecture documentation
│   ├── POLICY_AND_USER_ID_FLOW.md
│   ├── LAYERED_ARCHITECTURE_FLOW.md
│   └── TOOLENGINEERING_FOUNDATION.md
├── src/
│   ├── pydantic_api/           # API Layer (FastAPI routers)
│   │   └── routers/
│   ├── communicationservice/   # Service Layer (chat/agent)
│   ├── tool_sessionservice/    # Service Layer (tool execution)
│   ├── casefileservice/        # Service Layer (casefile management)
│   ├── pydantic_ai_integration/
│   │   ├── tools/
│   │   │   ├── factory/        # Tool Factory (YAML → Python)
│   │   │   └── generated/      # Generated tools
│   │   ├── tool_decorator.py   # @register_mds_tool
│   │   └── dependencies.py     # MDSContext
│   ├── pydantic_models/        # Request/Response models
│   │   ├── shared/             # Base models (RequestEnvelope)
│   │   ├── tool_session/       # ToolRequest/Response
│   │   └── communication/      # ChatRequest/Response
│   └── solidservice/           # 🔬 Experimental: Solid Pod integration
├── tests/
│   ├── generated/              # Unit tests (tool layer)
│   ├── integration/            # Integration tests (service layer)
│   └── api/                    # API tests (HTTP layer)
├── scripts/                    # Utility scripts
│   └── main.py                 # Tool factory CLI
└── templates/                  # Jinja2 templates for code generation
    ├── tool_template.py.jinja2
    └── test_template.py.jinja2
```

---

## 🔬 SOLID Side Project

**Status**: Experimental  
**Location**: `src/solidservice/`

This project includes experimental integration with **Solid Pods** (Social Linked Data) for decentralized user data storage. The Solid service provides an alternative to Firestore for storing user casefiles and tool events in user-controlled pods.

**Key Features**:
- Client credentials flow for pod authentication
- RDF/Turtle document storage
- User-owned data architecture

**Documentation**: See `solid-data/tiny-data-collider/SOLID_FINAL_STATUS.md`

**Note**: SOLID integration is experimental and not required for core tool engineering functionality.

---

## 📚 Documentation

### Core Documentation
- **[README (this file)](README.md)**: Project overview, quick start, testing philosophy
- **[Quick Reference](QUICK_REFERENCE.md)**: Daily commands and common patterns
- **[Changelog](CHANGELOG.md)**: Version history and changes

### Architecture & Design
- **[Layered Architecture Flow](docs/LAYERED_ARCHITECTURE_FLOW.md)**: N-tier architecture and request/response patterns
- **[Policy & User ID Flow](docs/POLICY_AND_USER_ID_FLOW.md)**: How policies and user_id propagate through layers
- **[Tool Composition](docs/TOOL_COMPOSITION.md)**: Advanced tool chaining and composition patterns
- **[YAML-Driven Models](docs/YAML_DRIVEN_MODELS.md)**: How payload models are generated from YAML

### Improvement & Enhancement
- **[Tool Engineering Improvements](docs/TOOL_ENGINEERING_IMPROVEMENTS.md)**: 🆕 Comprehensive analysis and recommendations for enhancing the framework
- **[Improvement Summary](docs/IMPROVEMENT_SUMMARY.md)**: 🆕 Quick reference for priority improvements
- **[Security Validation Improvements](docs/SECURITY_VALIDATION_IMPROVEMENTS.md)**: Security enhancements and validation patterns

### Tool-Specific Guides
- **[Gmail Tools](docs/GMAIL_TOOLS.md)**: Gmail integration tools
- **[Drive Tools](docs/DRIVE_TOOLS.md)**: Google Drive integration tools
- **[Sheets Tools](docs/SHEETS_TOOLS.md)**: Google Sheets integration tools

---

## 🛠️ Development

### **Adding a New Tool**

1. **Create YAML definition**:
   ```bash
   cp config/tools/echo_tool.yaml config/tools/my_new_tool.yaml
   # Edit YAML with your tool specification
   ```

2. **Generate code**:
   ```bash
   python -m scripts.main config/tools/my_new_tool.yaml
   ```

3. **Run tests**:
   ```bash
   python -m pytest tests/generated/test_my_new_tool.py -v
   ```

4. **Test at service layer** (optional):
   ```bash
   # Create integration test in tests/integration/
   python -m pytest tests/integration/test_my_new_tool_service.py -v
   ```

5. **Test via API** (optional):
   ```bash
   # Create API test in tests/api/
   python -m pytest tests/api/test_my_new_tool_api.py -v
   ```

### **Modifying Templates**

Tool and test templates are in `templates/`:
- `tool_template.py.jinja2`: Tool implementation template
- `test_template.py.jinja2`: Test suite template

After modifying templates, regenerate all tools:
```bash
python -m scripts.main config/tools/*.yaml
```

---

## 🧪 Testing Philosophy

**Key Principle**: Test at the appropriate layer for the concern being validated.

- **Unit tests** validate tool logic correctness
- **Integration tests** validate policy enforcement and orchestration
- **API tests** validate HTTP layer and end-to-end flow

**Each test level uses different models** to match the layer's abstraction:
- Unit: `MDSContext` + primitive types
- Integration: `ToolRequest` → `ToolResponse`
- API: `RequestEnvelope` → JSON

This approach enables:
- ✅ Fast feedback (unit tests run in milliseconds)
- ✅ Clear failure diagnosis (know which layer failed)
- ✅ Independent layer evolution (API changes don't break unit tests)
- ✅ Comprehensive coverage (all concerns validated somewhere)

---

## 🎯 Design Principles

1. **Declarative over Imperative**: Define tools in YAML, not code
2. **Layered Architecture**: Each layer has one responsibility
3. **Policy as Data**: Policies are configuration, not code
4. **Type Safety**: Pydantic v2 for validation at all layers
5. **Context Propagation**: `user_id` flows through all layers
6. **Audit by Default**: Every tool execution creates audit trail
7. **Test at the Right Level**: Match test strategy to layer concern

---

## 📦 Tech Stack

- **Python 3.12+**: Core language
- **Pydantic v2**: Data validation and serialization
- **FastAPI**: HTTP API framework
- **Firestore**: Persistence layer (Firestore Admin SDK)
- **PyYAML**: YAML parsing for tool definitions
- **Jinja2**: Template engine for code generation
- **pytest**: Testing framework
- **pytest-asyncio**: Async test support

---

## 🚦 Project Status

**Current Phase**: Week 1 Complete - Tool Factory MVP ✅

### **Completed**
- ✅ YAML-driven tool generation
- ✅ Policy system (session, casefile, audit)
- ✅ Template-based code generation
- ✅ Unit test generation
- ✅ Example tool (echo_tool) with 9/9 passing tests
- ✅ Architecture documentation

### **In Progress**
- 🚧 Integration test templates
- 🚧 API test templates
- 🚧 Google Workspace toolset

### **Planned**
- 📋 Tool composition (chains, workflows)
- 📋 Agent-driven tool selection
- 📋 Document analysis toolset
- 📋 Web scraping toolset

---

## 📄 License

MIT License - See [LICENSE](LICENSE) for details

---

## 🤝 Contributing

Contributions welcome! Please:
1. Follow the existing architecture patterns
2. Add tests at appropriate layers
3. Update documentation
4. Run full test suite before submitting

---

## 📧 Contact

**Repository**: [my-tiny-data-collider](https://github.com/MSD21091969/my-tiny-data-collider)  
**Branch**: `feature/tool-factory-week1`  
**Maintainer**: Tool Engineering Team

---

**Built with ❤️ using Pydantic, FastAPI, and declarative tool engineering principles.**
