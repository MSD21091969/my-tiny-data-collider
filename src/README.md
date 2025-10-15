# Source Code Structure

**Last updated:** 2025-10-15

Application source code organized by domain.

## Phase 10 Architecture (Oct 15, 2025)

**Method Registration:** Decorator-based auto-registration via `@register_service_method`
- Service methods decorated in source files
- Auto-register at import (triggered by `src/__init__.py`)
- No manual YAML editing required
- YAML (`config/methods_inventory_v1.yaml`) is documentation-only

**Startup Flow:**
1. Import `src` package
2. Service modules imported (`casefileservice`, `tool_sessionservice`, `communicationservice`, etc.)
3. Decorators execute, populating MANAGED_METHODS registry
4. Application ready with 34 registered methods

## Services

### casefileservice/
Casefile CRUD operations, ACL management, workspace sync.
- **Methods:** 13 (create, read, update, delete, list, permissions, workspace sync)
- **Registration:** All methods decorated with `@register_service_method`

### tool_sessionservice/
Tool session lifecycle and execution orchestration.
- **Methods:** 6 (session CRUD, tool execution)
- **Registration:** All methods decorated with `@register_service_method`

### communicationservice/
Chat session management and LLM interaction.
- **Methods:** 6 (chat session CRUD, chat processing)
- **Registration:** All methods decorated with `@register_service_method`

### coreservice/
Core infrastructure services.
- **request_hub.py:** 3 methods (casefile execution, composite workflows)
- **Registration:** Module-level functions decorated

### pydantic_ai_integration/
PydanticAI integration layer and tool management.
- **method_decorator.py:** `@register_service_method` decorator implementation
- **registry/:** Method and tool registry management
- **integrations/google_workspace/clients.py:** 6 methods (Gmail, Drive, Sheets clients)

### pydantic_models/
Pydantic model definitions for requests, responses, domain entities.
- **base/:** Custom types (20+), validators (9), envelopes
- **operations/:** Operation-specific request/response models
- **canonical/:** Domain entity models
- **workspace/:** Google Workspace data models

### persistence/
Data persistence layer (Firestore, Redis).

### authservice/
Authentication and authorization (planned).

## Usage

Import services to trigger method registration:
```python
from src import casefileservice, tool_sessionservice, communicationservice
# All 34 methods now registered in MANAGED_METHODS
```

Add new methods with decorator:
```python
@register_service_method(
    name="my_method",
    description="What it does",
    service_name="MyService",
    service_module="src.myservice.service",
    classification={
        "domain": "workspace",
        "subdomain": "specific_area",
        "capability": "create",
        "complexity": "atomic",
        "maturity": "stable",
        "integration_tier": "internal"
    },
    required_permissions=["permission:action"],
    requires_casefile=False,
    enabled=True,
    requires_auth=True,
    timeout_seconds=30,
    version="1.0.0"
)
async def my_method(self, request: MyRequest) -> MyResponse:
    # Implementation
```
