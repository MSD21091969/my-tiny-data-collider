# Policy & User ID Flow Documentation

**Date:** October 2, 2025  
**Status:** 📘 Reference Documentation  
**Purpose:** Explain how policies and user_id flow through the tool execution pipeline

---

## 🎯 Executive Summary

The system implements a **declarative policy model** where policies are:
1. **Defined** in YAML or decorator parameters
2. **Stored** in `ManagedToolDefinition` 
3. **Enforced** by service/API layers before execution
4. **Audited** through `MDSContext` and `ToolEvent` tracking

The `user_id` flows through every layer, enabling:
- Authentication & authorization checks
- Casefile access control
- Audit trail attribution
- User-specific data access

---

## 📊 Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│  1. YAML Configuration (Declarative)                            │
│     config/tools/echo_tool.yaml                                 │
│     - session_policies                                          │
│     - casefile_policies                                         │
│     - audit_events                                              │
│     - business_rules (required_permissions, requires_auth)      │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│  2. Tool Factory (Generation)                                   │
│     src/pydantic_ai_integration/tools/factory/__init__.py       │
│     - Parses YAML                                               │
│     - Generates tool code                                       │
│     - Passes policies to decorator                              │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│  3. Tool Registration (@register_mds_tool)                      │
│     src/pydantic_ai_integration/tool_decorator.py               │
│     - Creates ManagedToolDefinition                             │
│     - Stores policies in MANAGED_TOOLS registry                 │
│     - Wraps function with validation                            │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│  4. API Request (Runtime)                                       │
│     User → API → Service Layer                                  │
│     - Extracts user_id from JWT/auth token                      │
│     - Creates MDSContext(user_id, session_id, casefile_id)      │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│  5. Policy Enforcement (Service Layer)                          │
│     - Check tool_def.business_rules.requires_auth               │
│     - Check tool_def.check_permission(user.permissions)         │
│     - Check session_policies.requires_active_session            │
│     - Check casefile_policies.enforce_access_control            │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│  6. Tool Execution                                              │
│     async def tool(ctx: MDSContext, **params) -> Dict:          │
│     - ctx.user_id available throughout                          │
│     - ctx.register_event() creates audit trail                  │
│     - ctx.casefile_id links to user's casefile                  │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│  7. Audit Trail (Post-execution)                                │
│     - ToolEvent stored with user_id, tool_name, timestamp       │
│     - Casefile updated if casefile_policies.audit_changes=True  │
│     - Audit config determines what gets logged                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔐 Policy Types & Purpose

### 1. **ToolSessionPolicies** (Session Lifecycle)

**Purpose:** Control how tools interact with user sessions

```python
class ToolSessionPolicies(BaseModel):
    requires_active_session: bool = True     # Must have active session?
    allow_new_session: bool = False          # Can create new session?
    allow_session_resume: bool = True        # Can resume inactive session?
    session_event_type: str = "request"      # Audit event type
    log_request_payload: bool = True         # Log full request?
    log_full_response: bool = True           # Log full response?
```

**Example from YAML:**
```yaml
session_policies:
  requires_active_session: true
  allow_new_session: false
  allow_session_resume: true
  session_event_type: request
  log_request_payload: true
  log_full_response: true
```

**Enforcement Point:** Service layer before tool execution
- Check if `ctx.session_id` is active
- If not, check `allow_new_session` or `allow_session_resume`
- Log request based on `log_request_payload`

---

### 2. **ToolCasefilePolicies** (Casefile Access)

**Purpose:** Control how tools interact with casefiles

```python
class ToolCasefilePolicies(BaseModel):
    requires_casefile: bool = False              # Casefile mandatory?
    allowed_casefile_states: List[str] = ["active"]  # Valid states
    create_if_missing: bool = False              # Auto-create casefile?
    enforce_access_control: bool = True          # Check user owns it?
    audit_casefile_changes: bool = True          # Log mutations?
```

**Example from YAML:**
```yaml
casefile_policies:
  requires_casefile: false
  allowed_casefile_states:
    - active
  create_if_missing: false
  enforce_access_control: true
  audit_casefile_changes: true
```

**Enforcement Point:** Service layer before tool execution
- Check if `ctx.casefile_id` is provided (if `requires_casefile=True`)
- Verify casefile state in `allowed_casefile_states`
- Check `user_id` owns the casefile (if `enforce_access_control=True`)
- Track changes if `audit_casefile_changes=True`

---

### 3. **ToolAuditConfig** (Audit Trail)

**Purpose:** Define what gets logged for compliance/debugging

```python
class ToolAuditConfig(BaseModel):
    success_event: str = "tool_success"         # Event type on success
    failure_event: str = "tool_failure"         # Event type on error
    log_response_fields: List[str] = []         # Fields to log
    redact_fields: List[str] = []               # Fields to redact
    emit_casefile_event: bool = True            # Add to casefile?
```

**Example from YAML:**
```yaml
audit_events:
  success_event: tool_success
  failure_event: tool_failure
  log_response_fields:
    - original_message
    - repeat_count
    - total_length
  redact_fields: []
  emit_casefile_event: false
```

**Enforcement Point:** After tool execution
- Create `ToolEvent` with appropriate event type
- Log only fields in `log_response_fields`
- Redact fields in `redact_fields`
- Emit to casefile if `emit_casefile_event=True`

---

### 4. **ToolBusinessRules** (Access Control)

**Purpose:** Core access control and availability rules

```python
class ToolBusinessRules(BaseModel):
    enabled: bool = True                        # Tool available?
    requires_auth: bool = True                  # Auth required?
    required_permissions: List[str] = []        # Permission list
    requires_casefile: bool = False             # Casefile needed?
    timeout_seconds: int = 30                   # Max execution time
```

**Example from YAML:**
```yaml
business_rules:
  enabled: true
  requires_auth: true
  required_permissions:
    - tools:execute
  requires_casefile: false
  timeout_seconds: 10
```

**Enforcement Point:** Service layer before tool execution
- Check `tool_def.business_rules.enabled`
- Check `tool_def.business_rules.requires_auth` (verify JWT)
- Check `tool_def.check_permission(user.permissions)`
- Check `tool_def.business_rules.requires_casefile`

---

## 👤 User ID Flow

### **1. Authentication Layer (API Entry)**

User authenticates → JWT issued with `user_id`

```python
# Example: OAuth2/JWT authentication
@app.post("/api/tools/execute")
async def execute_tool(
    request: ToolExecutionRequest,
    current_user: User = Depends(get_current_user)  # Extracts user_id from JWT
):
    user_id = current_user.id  # ← User ID extracted here
```

---

### **2. Context Creation (Service Layer)**

`user_id` is injected into `MDSContext`:

```python
from src.pydantic_ai_integration.dependencies import MDSContext

# Create context with user_id
ctx = MDSContext(
    user_id=current_user.id,           # ← User ID from auth
    session_id=session.session_id,      # From session store
    casefile_id=request.casefile_id     # From request (optional)
)
```

---

### **3. Permission Checking (Service Layer)**

Before tool execution, check permissions:

```python
# Get tool definition from registry
tool_def = get_tool_definition(tool_name)

# Check if user has required permissions
if not tool_def.check_permission(current_user.permissions):
    raise PermissionError(
        f"User {ctx.user_id} lacks permissions: {tool_def.business_rules.required_permissions}"
    )
```

**Implementation in `tool_definition.py`:**
```python
def check_permission(self, user_permissions: List[str]) -> bool:
    """Check if user has required permissions."""
    if not self.business_rules.required_permissions:
        return True  # No permissions required
    
    return all(
        perm in user_permissions
        for perm in self.business_rules.required_permissions
    )
```

---

### **4. Casefile Access Control**

If tool requires casefile, verify user owns it:

```python
# If casefile_id is provided, verify access
if ctx.casefile_id:
    casefile = await casefile_service.get_casefile(ctx.casefile_id)
    
    # Check if user owns this casefile
    if casefile.metadata.created_by != ctx.user_id:
        raise PermissionError(
            f"User {ctx.user_id} does not own casefile {ctx.casefile_id}"
        )
```

---

### **5. Tool Execution (User Context Available)**

Inside tool function, `user_id` is always accessible:

```python
@register_mds_tool(name="gmail_list_messages", ...)
async def gmail_list_messages(
    ctx: MDSContext,
    max_results: int = 10
) -> Dict[str, Any]:
    # ctx.user_id available throughout execution
    
    # Use user_id for API calls
    gmail_client = GmailClient(user_id=ctx.user_id)
    messages = await gmail_client.list_messages(max_results=max_results)
    
    # Store in user's casefile
    if ctx.casefile_id:
        await casefile_service.store_gmail_messages(
            casefile_id=ctx.casefile_id,
            messages=messages
        )
    
    # Audit trail includes user_id automatically
    ctx.register_event("gmail_list_messages", {"max_results": max_results})
    
    return {"messages": messages}
```

---

### **6. Audit Trail (Attribution)**

Every `ToolEvent` includes `user_id` via context:

```python
class ToolEvent(BaseModel):
    event_id: str
    event_type: str
    tool_name: str
    parameters: Dict[str, Any]
    timestamp: str
    # user_id is stored via session correlation
```

When stored:
```python
{
    "event_id": "evt_251002_abc123",
    "tool_name": "echo_tool",
    "session_id": "ts_251002_xyz789",  # ← Links to session
    "user_id": "user_demo",             # ← From session/casefile
    "timestamp": "2025-10-02T10:30:00Z",
    "parameters": {"message": "hello"},
    "result_summary": {"status": "success"}
}
```

---

## 🔄 Complete Flow Example: Gmail List Messages

### **Step 1: YAML Definition**

```yaml
# config/tools/gmail_list_messages.yaml
name: gmail_list_messages
business_rules:
  requires_auth: true
  required_permissions:
    - gmail:read
  requires_casefile: true

session_policies:
  requires_active_session: true
  log_request_payload: true

casefile_policies:
  requires_casefile: true
  enforce_access_control: true
  audit_casefile_changes: true

audit_events:
  success_event: gmail_messages_listed
  log_response_fields:
    - message_count
```

---

### **Step 2: Tool Registration**

Factory generates:
```python
@register_mds_tool(
    name="gmail_list_messages",
    requires_auth=True,
    required_permissions=["gmail:read"],
    requires_casefile=True,
    session_policies={
        "requires_active_session": True,
        "log_request_payload": True
    },
    casefile_policies={
        "requires_casefile": True,
        "enforce_access_control": True,
        "audit_casefile_changes": True
    },
    audit_config={
        "success_event": "gmail_messages_listed",
        "log_response_fields": ["message_count"]
    }
)
async def gmail_list_messages(ctx: MDSContext, max_results: int = 10):
    # Implementation...
```

---

### **Step 3: API Request**

```http
POST /api/tools/execute
Authorization: Bearer <JWT_TOKEN>
Content-Type: application/json

{
  "tool_name": "gmail_list_messages",
  "parameters": {
    "max_results": 20
  },
  "casefile_id": "cf_251002_abc123"
}
```

---

### **Step 4: Service Layer Enforcement**

```python
# 1. Extract user_id from JWT
current_user = verify_jwt(request.headers["Authorization"])
user_id = current_user.id  # "user_demo"

# 2. Get tool definition
tool_def = MANAGED_TOOLS["gmail_list_messages"]

# 3. Check enabled
if not tool_def.business_rules.enabled:
    raise ToolDisabledError()

# 4. Check authentication
if tool_def.business_rules.requires_auth and not current_user:
    raise AuthenticationError()

# 5. Check permissions
if not tool_def.check_permission(current_user.permissions):
    raise PermissionError(f"Missing: {tool_def.business_rules.required_permissions}")

# 6. Check session policy
if tool_def.session_policies.requires_active_session:
    session = await get_active_session(user_id)
    if not session:
        raise SessionRequiredError()

# 7. Check casefile policy
if tool_def.casefile_policies.requires_casefile:
    if not request.casefile_id:
        raise CasefileRequiredError()
    
    casefile = await get_casefile(request.casefile_id)
    
    # Enforce access control
    if tool_def.casefile_policies.enforce_access_control:
        if casefile.metadata.created_by != user_id:
            raise CasefileAccessDeniedError()

# 8. Create context
ctx = MDSContext(
    user_id=user_id,
    session_id=session.session_id,
    casefile_id=request.casefile_id
)

# 9. Execute tool
result = await gmail_list_messages(ctx, **request.parameters)
```

---

### **Step 5: Tool Execution**

```python
async def gmail_list_messages(ctx: MDSContext, max_results: int = 10):
    # user_id available
    print(f"Executing for user: {ctx.user_id}")  # "user_demo"
    
    # Use user-specific client
    client = GmailClient(user_id=ctx.user_id)
    messages = await client.list_messages(max_results=max_results)
    
    # Store in user's casefile
    await casefile_service.store_gmail_messages(
        casefile_id=ctx.casefile_id,
        messages=messages
    )
    
    # Register audit event
    ctx.register_event(
        "gmail_list_messages",
        {"max_results": max_results},
        result_summary={"message_count": len(messages)}
    )
    
    return {"messages": messages, "count": len(messages)}
```

---

### **Step 6: Audit Trail Storage**

```python
# ToolEvent created automatically
{
    "event_id": "evt_251002_xyz",
    "event_type": "gmail_messages_listed",  # From audit_config
    "tool_name": "gmail_list_messages",
    "session_id": "ts_251002_abc",
    "casefile_id": "cf_251002_def",
    "timestamp": "2025-10-02T10:30:00Z",
    "parameters": {"max_results": 20},
    "result_summary": {"message_count": 15},  # Only logged field
    "status": "success"
}

# Linked back to user via session/casefile
session.user_id = "user_demo"
casefile.metadata.created_by = "user_demo"
```

---

## 🔍 Key Enforcement Points

### **Service Layer Checklist (Before Execution)**

```python
# Pseudo-code for service layer enforcement
async def execute_tool_with_policies(
    tool_name: str,
    parameters: Dict[str, Any],
    current_user: User,
    casefile_id: Optional[str] = None
):
    # 1. Get tool definition
    tool_def = MANAGED_TOOLS[tool_name]
    
    # 2. Check business rules
    if not tool_def.business_rules.enabled:
        raise ToolDisabledError()
    
    if tool_def.business_rules.requires_auth and not current_user:
        raise AuthenticationError()
    
    if not tool_def.check_permission(current_user.permissions):
        raise PermissionError()
    
    # 3. Check session policies
    if tool_def.session_policies:
        if tool_def.session_policies.requires_active_session:
            session = await get_active_session(current_user.id)
            if not session and not tool_def.session_policies.allow_new_session:
                raise SessionRequiredError()
    
    # 4. Check casefile policies
    if tool_def.casefile_policies:
        if tool_def.casefile_policies.requires_casefile and not casefile_id:
            raise CasefileRequiredError()
        
        if casefile_id and tool_def.casefile_policies.enforce_access_control:
            casefile = await get_casefile(casefile_id)
            if casefile.metadata.created_by != current_user.id:
                raise AccessDeniedError()
    
    # 5. Create context with user_id
    ctx = MDSContext(
        user_id=current_user.id,
        session_id=session.session_id,
        casefile_id=casefile_id
    )
    
    # 6. Execute tool
    result = await tool_def.implementation(ctx, **parameters)
    
    # 7. Handle audit logging per audit_config
    if tool_def.audit_config:
        await log_audit_event(
            event_type=tool_def.audit_config.success_event,
            user_id=current_user.id,
            tool_name=tool_name,
            result=filter_fields(result, tool_def.audit_config.log_response_fields)
        )
    
    return result
```

---

## 📝 Summary

### **Policies:**
- **Declared** once in YAML or decorator
- **Stored** in `ManagedToolDefinition`
- **Enforced** by service layer before execution
- **Audited** through `ToolEvent` tracking

### **User ID:**
- **Extracted** from JWT at API boundary
- **Injected** into `MDSContext` 
- **Used** for permission checks, data access, audit trail
- **Tracked** through all layers (session → casefile → events)

### **Flow:**
```
User Auth → JWT → user_id → MDSContext → Policy Checks → Tool Execution → Audit Trail
```

### **Benefits:**
✅ **Declarative:** Policies defined in YAML, not code  
✅ **Centralized:** Single source of truth in `ManagedToolDefinition`  
✅ **Auditable:** Every action tracked with user attribution  
✅ **Secure:** Multi-layer enforcement (auth, permissions, casefile ACLs)  
✅ **Flexible:** Policies can be changed without code changes

---

## 📚 Related Documentation

- [Tool Engineering Foundation](./TOOLENGINEERING_FOUNDATION.md)
- [Tool Factory Architecture](../src/pydantic_ai_integration/tools/factory/README.md)
- [Security Validation Improvements](./SECURITY_VALIDATION_IMPROVEMENTS.md)

---

**Last Updated:** October 2, 2025  
**Maintained By:** Tool Engineering Team
