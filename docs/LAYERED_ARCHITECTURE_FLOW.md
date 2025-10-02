# Layered Architecture Flow: Policies & Request/Response Patterns

**Date:** October 2, 2025  
**Status:** 📐 Architecture Reference  
**Purpose:** Document how policies flow through all architectural layers with different request/response models

---

## 🎯 Your Question Answered

**Yes, exactly correct!**

1. ✅ **Policies defined in YAML** as declarative parameters
2. ✅ **Flow crosses all layers**: API → Service → Tool
3. ✅ **Each layer uses different Request/Response models**
4. ✅ **Right term**: **"Layered Architecture"** or **"N-Tier Architecture"**

---

## 🏗️ The Layered Architecture (N-Tier)

```
┌─────────────────────────────────────────────────────────────────┐
│  Layer 1: API LAYER (FastAPI Routers)                          │
│  Purpose: HTTP endpoint, auth extraction, request validation    │
│  Models: RequestEnvelope, HTTPRequest/Response                  │
│  Location: src/pydantic_api/routers/                            │
└─────────────────────────────────────────────────────────────────┘
                            ↓
                    Transforms HTTP → Service Request
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│  Layer 2: SERVICE LAYER (Business Logic)                        │
│  Purpose: Orchestration, policy enforcement, session management │
│  Models: ChatRequest/Response, ToolRequest/Response             │
│  Location: src/communicationservice/, src/tool_sessionservice/  │
└─────────────────────────────────────────────────────────────────┘
                            ↓
                    Creates MDSContext + Validates Policies
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│  Layer 3: TOOL LAYER (Tool Execution)                           │
│  Purpose: Execute tool logic, return results                    │
│  Models: MDSContext, Pydantic parameter models, Dict results    │
│  Location: src/pydantic_ai_integration/tools/generated/         │
└─────────────────────────────────────────────────────────────────┘
                            ↓
                    Tool Result → Service Response
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│  Layer 4: PERSISTENCE LAYER (Data Storage)                      │
│  Purpose: Store sessions, casefiles, events in Firestore        │
│  Models: Firestore documents (dict format)                      │
│  Location: src/casefileservice/, src/communicationservice/repo/ │
└─────────────────────────────────────────────────────────────────┘
```

**Key Terms:**
- **N-Tier Architecture** = Multiple layers, each with specific responsibility
- **Separation of Concerns** = Each layer handles one aspect (HTTP, business logic, execution, storage)
- **Request/Response Pattern** = Each layer transforms input → output using different models

---

## 🔄 Complete Flow with Different Models

### **Example: User Executes `echo_tool`**

---

## **LAYER 1: API LAYER**

### **Incoming HTTP Request**

```http
POST /api/tools/execute
Authorization: Bearer eyJhbGc...  ← JWT with user_id
Content-Type: application/json

{
  "request": {
    "tool_name": "echo_tool",
    "parameters": {
      "message": "hello world",
      "repeat_count": 3
    },
    "casefile_id": "cf_251002_abc123"
  },
  "trace_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

### **API Layer Model: `RequestEnvelope`**

```python
# src/pydantic_models/shared/base_models.py
class RequestEnvelope(BaseModel):
    """Envelope for HTTP requests with auth and tracing."""
    request: Dict[str, Any]           # The actual request data
    auth_token: Optional[str]         # JWT token
    trace_id: UUID                    # For distributed tracing
    client_info: Dict[str, Any]       # Browser/client metadata
```

### **API Router Code**

```python
# src/pydantic_api/routers/tools.py (hypothetical)
@router.post("/api/tools/execute")
async def execute_tool(
    envelope: RequestEnvelope,                           # ← HTTP model
    current_user: User = Depends(get_current_user),     # ← Extract from JWT
    tool_service: ToolSessionService = Depends(...)
):
    # Extract data from HTTP envelope
    tool_name = envelope.request["tool_name"]
    parameters = envelope.request["parameters"]
    casefile_id = envelope.request.get("casefile_id")
    
    # Transform to SERVICE LAYER model
    service_request = ToolRequest(
        user_id=current_user.id,              # ← From JWT
        operation="tool_execution",
        payload=ToolRequestPayload(
            tool_name=tool_name,
            parameters=parameters,
            casefile_id=casefile_id
        )
    )
    
    # Call service layer
    service_response = await tool_service.execute_tool(service_request)
    
    # Transform back to HTTP response
    return {
        "trace_id": envelope.trace_id,
        "result": service_response.payload.result,
        "status": service_response.status
    }
```

**Key Point:** API layer uses **`RequestEnvelope`** (HTTP-specific) → transforms to **`ToolRequest`** (service-specific)

---

## **LAYER 2: SERVICE LAYER**

### **Service Layer Model: `ToolRequest`**

```python
# src/pydantic_models/tool_session/models.py
class ToolRequestPayload(BaseModel):
    """Payload specific to tool execution."""
    tool_name: str
    parameters: Dict[str, Any]
    prompt: Optional[str]
    casefile_id: Optional[str]
    session_request_id: Optional[str]

class ToolRequest(BaseRequest[ToolRequestPayload]):
    """Service-layer request for tool execution."""
    request_id: UUID                    # Auto-generated
    session_id: Optional[str]           # Tool session
    user_id: str                        # From auth
    operation: Literal["tool_execution"]
    payload: ToolRequestPayload         # Tool-specific data
    timestamp: str
    metadata: Dict[str, Any]
```

### **Service Layer: Policy Enforcement**

```python
# src/tool_sessionservice/service.py
class ToolSessionService:
    async def execute_tool(self, request: ToolRequest) -> ToolResponse:
        """Execute tool with policy enforcement."""
        
        # 1. Get tool definition (policies stored here)
        from ..pydantic_ai_integration.tool_decorator import MANAGED_TOOLS
        tool_def = MANAGED_TOOLS[request.payload.tool_name]
        
        # 2. ENFORCE BUSINESS RULES (from YAML)
        if not tool_def.business_rules.enabled:
            raise ToolDisabledError()
        
        if tool_def.business_rules.requires_auth:
            # Auth already validated by API layer, but check here too
            pass
        
        # Get user permissions (from database or JWT claims)
        user_permissions = await self._get_user_permissions(request.user_id)
        if not tool_def.check_permission(user_permissions):
            raise PermissionError(
                f"Missing permissions: {tool_def.business_rules.required_permissions}"
            )
        
        # 3. ENFORCE SESSION POLICIES (from YAML)
        if tool_def.session_policies.requires_active_session:
            session = await self._get_active_session(request.user_id)
            if not session:
                if tool_def.session_policies.allow_new_session:
                    session = await self._create_session(request.user_id)
                else:
                    raise SessionRequiredError()
        
        # 4. ENFORCE CASEFILE POLICIES (from YAML)
        casefile_id = request.payload.casefile_id
        if tool_def.casefile_policies.requires_casefile and not casefile_id:
            if tool_def.casefile_policies.create_if_missing:
                casefile_id = await self._create_casefile(request.user_id)
            else:
                raise CasefileRequiredError()
        
        if casefile_id and tool_def.casefile_policies.enforce_access_control:
            casefile = await self.casefile_service.get_casefile(casefile_id)
            if casefile.metadata.created_by != request.user_id:
                raise CasefileAccessDeniedError()
        
        # 5. CREATE TOOL CONTEXT (from service request)
        ctx = MDSContext(
            user_id=request.user_id,
            session_id=session.session_id,
            casefile_id=casefile_id
        )
        
        # 6. EXECUTE TOOL (call tool layer)
        tool_func = tool_def.implementation
        result = await tool_func(ctx, **request.payload.parameters)
        
        # 7. HANDLE AUDIT (from YAML audit_events)
        if tool_def.audit_config:
            await self._log_audit_event(
                event_type=tool_def.audit_config.success_event,
                user_id=request.user_id,
                tool_name=request.payload.tool_name,
                result=self._filter_audit_fields(
                    result,
                    tool_def.audit_config.log_response_fields
                )
            )
        
        # 8. RETURN SERVICE RESPONSE
        return ToolResponse(
            request_id=request.request_id,
            status=RequestStatus.COMPLETED,
            payload=ToolResponsePayload(
                result=result,
                events=[event.model_dump() for event in ctx.tool_events]
            )
        )
```

**Key Point:** Service layer:
- Uses **`ToolRequest`/`ToolResponse`** models (service-specific)
- **Enforces policies** from YAML before calling tool
- Creates **`MDSContext`** for tool execution
- Transforms to **tool function signature** (next layer)

---

## **LAYER 3: TOOL LAYER**

### **Tool Layer Model: `MDSContext` + Parameters**

```python
# Tool function signature (generated from YAML)
@register_mds_tool(
    name="echo_tool",
    # Policies from YAML stored in decorator
    session_policies={...},
    casefile_policies={...},
    audit_config={...}
)
async def echo_tool(
    ctx: MDSContext,              # ← Context from service layer
    message: str,                 # ← Parameters from request
    repeat_count: int = 1
) -> Dict[str, Any]:              # ← Tool-specific return
    """Tool implementation."""
    
    # Tool has access to:
    # - ctx.user_id (from JWT → service → context)
    # - ctx.session_id (from service layer)
    # - ctx.casefile_id (from request, if provided)
    
    # Execute tool logic
    echoed_messages = [message for _ in range(repeat_count)]
    total_length = sum(len(msg) for msg in echoed_messages)
    
    # Register audit event (stored in ctx.tool_events)
    ctx.register_event(
        "echo_tool",
        {"message": message, "repeat_count": repeat_count},
        result_summary={"total_length": total_length}
    )
    
    # Return simple dict (not a Pydantic model)
    return {
        "original_message": message,
        "repeat_count": repeat_count,
        "echoed_messages": echoed_messages,
        "total_length": total_length
    }
```

**Key Point:** Tool layer:
- Uses **`MDSContext`** + simple Python types (str, int, Dict)
- **No policy enforcement** (already done by service layer)
- Returns **plain dict** (not wrapped in response model)
- Registers events in context for audit trail

---

## **LAYER 4: PERSISTENCE LAYER**

### **Persistence Models: Firestore Documents**

```python
# Service layer calls persistence layer
await self.repository.store_tool_event(
    session_id=ctx.session_id,
    event=ctx.tool_events[-1]
)

# Persistence layer converts to Firestore format
# src/tool_sessionservice/repository.py
class ToolSessionRepository:
    async def store_tool_event(self, session_id: str, event: ToolEvent):
        """Store event in Firestore."""
        
        # Convert Pydantic model to dict for Firestore
        event_data = event.model_dump(mode='json')
        
        # Firestore document structure
        doc_ref = self.db.collection('tool_sessions').document(session_id)
        doc_ref.collection('events').add({
            'event_id': event_data['event_id'],
            'event_type': event_data['event_type'],
            'tool_name': event_data['tool_name'],
            'user_id': event_data.get('user_id'),  # From session
            'parameters': event_data['parameters'],
            'result_summary': event_data['result_summary'],
            'timestamp': event_data['timestamp'],
            'status': event_data['status']
        })
```

**Key Point:** Persistence layer:
- Converts **Pydantic models → dicts** for Firestore
- No request/response models (just storage operations)
- Links data by IDs (session_id, user_id, casefile_id)

---

## 📋 Summary: Request/Response Models by Layer

| Layer | Incoming Model | Outgoing Model | Purpose |
|-------|---------------|----------------|---------|
| **API** | `RequestEnvelope` (HTTP) | `Dict` (JSON response) | HTTP-specific wrapping, auth, tracing |
| **Service** | `ToolRequest` (service) | `ToolResponse` (service) | Business logic, policy enforcement |
| **Tool** | `MDSContext` + params | `Dict[str, Any]` | Tool execution, simple I/O |
| **Persistence** | Pydantic models | Firestore dicts | Data storage, serialization |

---

## 🔐 Policy Flow Through Layers

### **1. YAML Definition (Declarative)**

```yaml
# config/tools/echo_tool.yaml
business_rules:
  requires_auth: true
  required_permissions:
    - tools:execute

session_policies:
  requires_active_session: true
  allow_new_session: false

casefile_policies:
  requires_casefile: false
  enforce_access_control: true

audit_events:
  success_event: tool_success
  log_response_fields:
    - total_length
```

### **2. Tool Factory → Decorator (Registration)**

```python
# Generated: src/pydantic_ai_integration/tools/generated/echo_tool.py
@register_mds_tool(
    name="echo_tool",
    requires_auth=True,                    # ← From business_rules
    required_permissions=["tools:execute"], # ← From business_rules
    session_policies={                     # ← From session_policies
        "requires_active_session": True,
        "allow_new_session": False
    },
    casefile_policies={                    # ← From casefile_policies
        "requires_casefile": False,
        "enforce_access_control": True
    },
    audit_config={                         # ← From audit_events
        "success_event": "tool_success",
        "log_response_fields": ["total_length"]
    }
)
async def echo_tool(ctx: MDSContext, ...):
    # Implementation
```

### **3. Service Layer (Enforcement)**

```python
# Service reads policies from MANAGED_TOOLS registry
tool_def = MANAGED_TOOLS["echo_tool"]

# Check business_rules
if not tool_def.check_permission(user.permissions):
    raise PermissionError()  # ← Enforced HERE

# Check session_policies
if tool_def.session_policies.requires_active_session:
    if not session:
        raise SessionRequiredError()  # ← Enforced HERE

# Check casefile_policies
if casefile_id and tool_def.casefile_policies.enforce_access_control:
    if casefile.owner != user_id:
        raise AccessDeniedError()  # ← Enforced HERE
```

### **4. Tool Execution (No Policy Checks)**

```python
# Tool just executes logic - policies already enforced
async def echo_tool(ctx: MDSContext, message: str, repeat_count: int):
    result = {"original_message": message, ...}
    ctx.register_event("echo_tool", {...})  # ← Uses audit_config
    return result
```

---

## 🎯 Key Architectural Principles

### **1. Separation of Concerns**

Each layer has ONE job:
- **API Layer**: HTTP handling, authentication
- **Service Layer**: Business logic, policy enforcement
- **Tool Layer**: Tool execution
- **Persistence Layer**: Data storage

### **2. Request/Response Transformation**

```
HTTP Request (RequestEnvelope)
    ↓ transform
Service Request (ToolRequest)
    ↓ transform
Tool Call (MDSContext + params)
    ↓ transform
Tool Result (Dict)
    ↓ transform
Service Response (ToolResponse)
    ↓ transform
HTTP Response (JSON)
```

### **3. Policy Enforcement at Service Layer**

**WHY?**
- API layer = too early (no business context)
- Tool layer = too late (should only execute)
- Service layer = perfect (has context, can enforce rules)

### **4. Context Propagation**

```python
user_id (from JWT)
    ↓
ToolRequest(user_id=...)
    ↓
MDSContext(user_id=...)
    ↓
Tool function (ctx.user_id)
    ↓
Audit trail (event.user_id via session)
```

---

## 📊 Visual: Complete Request Flow

```
┌─────────────────────────────────────────────────────────────────┐
│ CLIENT                                                          │
│ curl -H "Authorization: Bearer TOKEN" \                        │
│      -d '{"tool_name":"echo_tool","parameters":{...}}'          │
└─────────────────────────────────────────────────────────────────┘
                            ↓ HTTP POST
┌─────────────────────────────────────────────────────────────────┐
│ LAYER 1: API ROUTER                                             │
│ - Parse RequestEnvelope                                         │
│ - Extract user_id from JWT                                      │
│ - Create ToolRequest(user_id, tool_name, parameters)            │
│ Model: RequestEnvelope → ToolRequest                            │
└─────────────────────────────────────────────────────────────────┘
                            ↓ service.execute_tool(request)
┌─────────────────────────────────────────────────────────────────┐
│ LAYER 2: SERVICE LAYER                                          │
│ - Get tool_def from MANAGED_TOOLS                               │
│ - ✓ Check business_rules.requires_auth                          │
│ - ✓ Check business_rules.required_permissions                   │
│ - ✓ Check session_policies.requires_active_session              │
│ - ✓ Check casefile_policies.enforce_access_control              │
│ - Create MDSContext(user_id, session_id, casefile_id)           │
│ Model: ToolRequest → MDSContext                                 │
└─────────────────────────────────────────────────────────────────┘
                            ↓ await tool_func(ctx, **params)
┌─────────────────────────────────────────────────────────────────┐
│ LAYER 3: TOOL EXECUTION                                         │
│ - Execute tool logic                                            │
│ - ctx.register_event() for audit                                │
│ - Return Dict[str, Any]                                         │
│ Model: MDSContext + params → Dict result                        │
└─────────────────────────────────────────────────────────────────┘
                            ↓ result Dict
┌─────────────────────────────────────────────────────────────────┐
│ LAYER 2: SERVICE LAYER (continued)                              │
│ - Log audit event per audit_config                              │
│ - Create ToolResponse(result, events)                           │
│ Model: Dict → ToolResponse                                      │
└─────────────────────────────────────────────────────────────────┘
                            ↓ return response
┌─────────────────────────────────────────────────────────────────┐
│ LAYER 1: API ROUTER (continued)                                 │
│ - Transform ToolResponse → JSON                                 │
│ - Add trace_id                                                  │
│ - Return HTTP 200 with JSON body                                │
│ Model: ToolResponse → JSON                                      │
└─────────────────────────────────────────────────────────────────┘
                            ↓ HTTP 200 OK
┌─────────────────────────────────────────────────────────────────┐
│ CLIENT                                                          │
│ Receives: {"result": {...}, "trace_id": "..."}                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🎓 Terminology Reference

| Term | Definition | Example in Code |
|------|-----------|-----------------|
| **N-Tier Architecture** | System divided into layers (presentation, business, data) | API → Service → Tool → Persistence |
| **Layered Architecture** | Same as N-Tier | Same as above |
| **Separation of Concerns** | Each component has one responsibility | API handles HTTP, Service enforces policies |
| **Request/Response Pattern** | Each layer transforms input to output | `RequestEnvelope` → `ToolRequest` → `MDSContext` |
| **Data Transfer Object (DTO)** | Model for passing data between layers | `ToolRequestPayload`, `ToolResponsePayload` |
| **Context Propagation** | Passing context (user_id) through layers | JWT → user_id → MDSContext → tool |
| **Policy Enforcement Point** | Where rules are checked | Service layer checks policies before tool call |

---

## 📚 Related Documentation

- [Policy and User ID Flow](./POLICY_AND_USER_ID_FLOW.md)
- [Tool Engineering Foundation](./TOOLENGINEERING_FOUNDATION.md)
- [Security Validation Improvements](./SECURITY_VALIDATION_IMPROVEMENTS.md)

---

**Last Updated:** October 2, 2025  
**Maintained By:** Tool Engineering Team
