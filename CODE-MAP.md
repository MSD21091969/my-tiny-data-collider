# CODE MAP

**Updated:** October 9, 2025 at 18:20

---

## Root Structure

### [[src/.foam-note.md|src/]]
- [[src/authservice/.foam-note.md|authservice/]] - Authentication, JWT tokens
- [[src/casefileservice/.foam-note.md|casefileservice/]] - Casefile CRUD
- [[src/communicationservice/.foam-note.md|communicationservice/]] - Gmail integration
- [[src/coreservice/.foam-note.md|coreservice/]] - RequestHub orchestrator
- [[src/tool_sessionservice/.foam-note.md|tool_sessionservice/]] - Session lifecycle
- [[src/persistence/.foam-note.md|persistence/]] - Database adapters
- [[src/pydantic_ai_integration/.foam-note.md|pydantic_ai_integration/]] - Tool generation
  - [[src/pydantic_ai_integration/tools/.foam-note.md|tools/]] - Generated code
- [[src/pydantic_api/.foam-note.md|pydantic_api/]] - FastAPI app
  - [[src/pydantic_api/routers/.foam-note.md|routers/]] - HTTP endpoints
- [[src/pydantic_models/.foam-note.md|pydantic_models/]] - 6-layer models
  - [[src/pydantic_models/base/.foam-note.md|base/]] - L0: BaseRequest/BaseResponse
  - [[src/pydantic_models/workspace/.foam-note.md|workspace/]] - L1: Business payloads
  - [[src/pydantic_models/operations/.foam-note.md|operations/]] - L2: Request/Response DTOs
  - [[src/pydantic_models/canonical/.foam-note.md|canonical/]] - External API models
  - [[src/pydantic_models/views/.foam-note.md|views/]] - UI views

### [[config/.foam-note.md|config/]]
- `methods_inventory_v1.yaml` - 26 methods
- `models_inventory_v1.yaml` - 124 models
- `tool_schema_v2.yaml` - Tool schema
- [[config/toolsets/.foam-note.md|toolsets/]] - YAML tool definitions

---

## Flow Diagrams

### Request Flow
```
HTTP → pydantic_api/ → coreservice/ (RequestHub) → Services
```

### Tool Generation
```
toolsets/*.yaml → generate_tools.py → tools/generated/*.py
```

### Model Layers
```
base/ → workspace/ → operations/
```

---

## Key Files

- `src/coreservice/request_hub.py` - Central orchestrator
- `config/methods_inventory_v1.yaml` - 26 methods
- `config/models_inventory_v1.yaml` - 124 models
- `tests/integration/test_request_hub_fastapi.py` - 8/8 tests passing


---

## Core Architecture

### [[src/coreservice]] - Central Orchestration
**Tags:** #service #core #orchestration  
**Type:**  Service Directory  
**Purpose:** Request orchestration, hooks, policy patterns

**Key Files:**
- [[src/coreservice/request_hub.py]]  #core-service - Central dispatcher for all R-A-R requests
  - Validates auth, session, permissions
  - Enriches context (MDSContext, ToolSession, Casefile)
  - Executes hooks (metrics, audit)
  - Delegates to service methods
- [[src/coreservice/policy_patterns.py]]  #config - Policy templates for request validation
- [[src/coreservice/id_service.py]]  #utility - ID generation utilities
- [[src/coreservice/config.py]]  #config - Core configuration

**Relationships:**
- Uses: [[src/casefileservice]] #service, [[src/tool_sessionservice]] #service, [[src/communicationservice]] #service
- Consumed by: [[src/pydantic_api]] #api
- Orchestrates: All R-A-R operations

---

### [[src/casefileservice]] - Casefile Management
**Tags:** #service #business-logic #casefile  
**Type:**  Service Directory  
**Purpose:** Business logic for casefile CRUD operations

**Key Files:**
- [[src/casefileservice/service.py]]  #service-implementation - CasefileService with create/read/update/delete methods
- [[src/casefileservice/repository.py]]  #repository - Data persistence abstraction (Firestore/Memory)

**Relationships:**
- Uses: [[src/pydantic_models/workspace]] #models, [[src/persistence]] #persistence
- Called by: [[src/coreservice/request_hub.py]] #core-service
- Models: [[src/pydantic_models/operations]] #dtos (CreateCasefileRequest/Response)

---

### [[src/tool_sessionservice]] - Tool Session Management
**Tags:** #service #session-management #tools  
**Type:**  Service Directory  
**Purpose:** Manage tool execution sessions and state

**Key Files:**
- [[src/tool_sessionservice/service.py]]  #service-implementation - ToolSessionService for session lifecycle
- [[src/tool_sessionservice/repository.py]]  #repository - Session persistence

**Relationships:**
- Uses: [[src/pydantic_models/tool_session.py]] #models
- Called by: [[src/coreservice/request_hub.py]] #core-service
- Integrates: [[src/pydantic_ai_integration]] #tool-engineering

---

### [[src/communicationservice]] - External Communications
**Tags:** #service #external-api #communication  
**Type:**  Service Directory  
**Purpose:** Handle Gmail, notifications, external messaging

**Key Files:**
- [[src/communicationservice/service.py]]  #service-implementation - CommunicationService (Gmail integration)
- [[src/communicationservice/repository.py]]  #repository - Message persistence

**Relationships:**
- Uses: [[src/pydantic_models/canonical]] #external-models (external API models)
- Called by: [[src/coreservice/request_hub.py]] #core-service
- External: Google Workspace APIs

---

### [[src/authservice]] - Authentication & Authorization
**Tags:** #service #security #authentication  
**Type:**  Service Directory  
**Purpose:** User authentication and token management

**Key Files:**
- [[src/authservice/routes.py]]  #api-routes - Auth endpoints
- [[src/authservice/token.py]]  #security - JWT token handling

**Relationships:**
- Used by: [[src/pydantic_api]] #api middleware
- Validates: All requests via [[src/coreservice/request_hub.py]] #core-service

---

### [[src/persistence]] - Data Persistence Layer
**Tags:** #persistence #database #storage  
**Type:**  Infrastructure Directory  
**Purpose:** Database abstraction and storage

**Key Files:**
- [[src/persistence/firestore]]  #database - Google Firestore implementation

**Relationships:**
- Used by: All service repositories #repository
- Provides: Data storage for casefiles, sessions, messages

---

### [[src/solidservice]] - Solid Pod Integration
**Tags:** #service #external-api #decentralized  
**Type:**  Service Directory  
**Purpose:** Decentralized data storage integration

**Key Files:**
- [[src/solidservice/client.py]]  #external-client - Solid Pod client

**Relationships:**
- Alternative storage: Can replace [[src/persistence/firestore]] #database
- Status: Optional integration

---

## Model System

### [[src/pydantic_models]] - 6-Layer Model Hierarchy
**Tags:** #models #data-structures #pydantic  
**Type:**  Models Directory  
**Purpose:** Single source of truth for all data structures

**Layer 0: Base Infrastructure**
- [[src/pydantic_models/base]]  #base-models - BaseRequest, BaseResponse, BasePayload
- Core abstractions for R-A-R pattern

**Layer 1: Payload Models**
- [[src/pydantic_models/workspace]]  #business-models - Business data (Casefile, Document, etc.)
- Pure business logic, no execution metadata

**Layer 2: Request/Response DTOs**
- [[src/pydantic_models/operations]]  #dtos - Execution envelopes
- CreateCasefileRequest, CreateCasefileResponse
- Contains operation, payload, user_id, session_id, hooks

**Layer 3: Method Definitions**
- [[config/methods_inventory_v1.yaml]]  #yaml #registry - 26 registered methods
- Loaded into [[src/pydantic_ai_integration/method_registry.py]]  #registry
- MANAGED_METHODS registry

**Layer 4: Tool Definitions**
- [[src/pydantic_ai_integration/tools]]  #generated-code - Generated tool code
- MANAGED_TOOLS registry
- Created by [[scripts/generate_tools.py]]  #script

**Layer 5: YAML Configuration**
- [[config/toolsets]]  #yaml #config - Source of truth for tool definitions
- [[config/tool_schema_v2.yaml]]  #yaml #schema - Tool schema

**Relationships:**
```
YAML → generates → Tools → create → Request DTOs → 
  RequestHub validates → Service executes → Response DTOs
```

**Special Models:**
- [[src/pydantic_models/canonical]]  #external-models - External API models (Gmail, Google Workspace)
- [[src/pydantic_models/views]]  #view-models - UI/API views
- [[src/pydantic_models/tool_session.py]]  #models - Tool session state

**Model Inventory:**
- Total: 124 models documented
- Registry: [[config/models_inventory_v1.yaml]]  #yaml #registry

---

## Tool Engineering

### [[src/pydantic_ai_integration]] - Tool Generation & Registry
**Tags:** #tool-engineering #code-generation #registry  
**Type:**  Tool Engineering Directory  
**Purpose:** Generate executable tools from YAML definitions

**Key Components:**

**Method Registry:**
- [[src/pydantic_ai_integration/method_registry.py]]  #registry - MANAGED_METHODS (26 methods)
- [[src/pydantic_ai_integration/method_definition.py]]  #models - ManagedMethodDefinition (16 fields)
- Loads from [[config/methods_inventory_v1.yaml]]  #yaml

**Tool Registry:**
- [[src/pydantic_ai_integration/tool_decorator.py]]  #decorator - @register_mds_tool decorator
- [[src/pydantic_ai_integration/tool_definition.py]]  #models - ManagedToolDefinition (12 fields)
- [[src/pydantic_ai_integration/tool_utils.py]]  #utility - Tool utilities

**Model Registry:**
- [[src/pydantic_ai_integration/model_registry.py]]  #registry - 52 models across 6 layers
- Discovery APIs for model inspection

**Tool Factory:**
- [[scripts/generate_tools.py]]  #script #code-generator - Generates Python code from YAML
- Uses Jinja2 templates
- Parameter inheritance: DTO → Method → Tool

**Generated Tools:**
- [[src/pydantic_ai_integration/tools/generated]]  #generated-code - Auto-generated tool code
  - workflows/request_hub/ - RequestHub workflow tools
  - core/casefile_management/ - Casefile tools
  - helpers/ - Utility tools

**Relationships:**
```
config/toolsets/*.yaml → generate_tools.py → 
  tools/generated/*.py → MANAGED_TOOLS registry →
  tool execution → RequestHub dispatch
```

**Key Scripts:**
- [[scripts/generate_tools.py]]  #script - Generate tools from YAML
- [[scripts/import_generated_tools.py]]  #script - Load tools into registry
- [[scripts/validate_dto_alignment.py]]  #script - Validate parameter alignment
- [[scripts/show_tools.py]]  #script - List registered tools

---

## API Layer

### [[src/pydantic_api]] - FastAPI Application
**Tags:** #api #fastapi #http  
**Type:**  API Directory  
**Purpose:** HTTP REST API for all operations

**Key Files:**
- [[src/pydantic_api/app.py]]  #api-main - FastAPI application instance
- [[src/pydantic_api/dependencies.py]]  #dependency-injection - Dependency injection (RequestHub, services)

**Routers:**
- [[src/pydantic_api/routers]]  #api-routes - API endpoints
  - casefile routes → [[src/casefileservice]] #service
  - tool_session routes → [[src/tool_sessionservice]] #service
  - communication routes → [[src/communicationservice]] #service
  - auth routes → [[src/authservice]] #service

**Request Flow:**
```
HTTP Request → FastAPI Router → 
  RequestHub.dispatch() → Service Method → 
  Response + Hook Metadata → HTTP Response
```

**Integration Pattern:**
- Uses [[src/coreservice/request_hub.py]] #core-service for all operations
- Dependency injection: `hub: RequestHub = Depends(get_request_hub)`
- Example: [[tests/integration/test_request_hub_fastapi.py]]  #test

---

## Configuration

### [[config]] - System Configuration
**Tags:** #config #yaml #inventory  
**Type:**  Configuration Directory  
**Purpose:** YAML-based configuration for methods, models, and tools

**Key Files:**

**Method Inventory:**
- [[config/methods_inventory_v1.yaml]]  #yaml #registry - 26 method definitions
  - Classification: domain, subdomain, capability, complexity
  - Execution: request_model, response_model, implementation_class
  - Loaded at startup via [[src/__init__.py]]  #bootstrap

**Model Inventory:**
- [[config/models_inventory_v1.yaml]]  #yaml #registry - 124 models documented
  - 6-layer taxonomy (L0-L5)
  - Field definitions, inheritance chains
  - Generated by [[scripts/scan_models.py]]  #script

**Tool Schema:**
- [[config/tool_schema_v2.yaml]]  #yaml #schema - Tool definition schema
  - Supports method_name references (parameter inheritance)
  - Classification taxonomy
  - Composite tool patterns

**Tool Definitions:**
- [[config/toolsets/core]]  #yaml #tools - Core functionality tools
- [[config/toolsets/workflows]]  #yaml #tools - Multi-step workflow tools
- [[config/toolsets/helpers]]  #yaml #tools - Utility tools
- [[config/toolsets/prototypes]]  #yaml #tools - Experimental tools

**Synchronization:**
- Methods loaded: Startup via `register_methods_from_yaml()`
- Models scanned: `python scripts/scan_models.py`
- Tools generated: `python scripts/generate_tools.py`

---

## Testing

### [[tests]] - Test Suite
**Tags:** #testing #pytest #quality-assurance  
**Type:**  Test Directory  
**Purpose:** Comprehensive testing (85% coverage minimum)

**Structure:**

**Unit Tests:**
- [[tests/coreservice]]  #unit-tests - RequestHub unit tests (2 tests)
  - test_request_hub.py - Simple and composite workflows
- [[tests/casefileservice]]  #unit-tests - Service unit tests
  - test_memory_repository.py - Repository tests
- [[tests/tool_sessionservice]]  #unit-tests - Session service tests
- [[tests/communicationservice]]  #unit-tests - Communication service tests

**Integration Tests:**
- [[tests/integration/test_request_hub_fastapi.py]]  #integration-test - End-to-end tests (6 tests)
  - HTTP → RequestHub → Service flow
  - Hook execution validation
  - Context enrichment validation
  - Error handling validation

**Test Results:**
- Total: 8/8 passing (100%)
- Coverage: Request flow, hooks, policies, error handling

**Test Configuration:**
- [[pytest.ini]]  #config - pytest configuration
- [[tests/conftest.py]]  #test-fixtures - Test fixtures

---

## AI Assistance

### [[AI/prompts]] - Code Generation Templates
**Tags:** #ai #templates #code-generation  
**Type:**  AI Templates Directory  
**Purpose:** Systematic prompts for AI-assisted development

**Templates:**
- [[AI/prompts/tool-yaml.md]]  #template - YAML tool definitions (30 lines)
- [[AI/prompts/dto-pattern.md]]  #template - R-A-R DTO patterns (35 lines)
- [[AI/prompts/fix-bug.md]]  #template - Bug fixing workflow (25 lines)
- [[AI/prompts/refactor.md]]  #template - Code refactoring workflow (32 lines)

**Format:** Variables → Constraints → Template → Command/Rule

**Usage:** Reference in AI conversations for consistent code generation

---

## Scripts & Utilities

### [[scripts]] - Development Scripts
**Tags:** #scripts #automation #devtools  
**Type:**  Scripts Directory  
**Purpose:** Code generation, validation, testing

**Key Scripts:**

**Tool Generation:**
- [[scripts/generate_tools.py]]  #script #code-generator - Generate Python code from YAML
- [[scripts/import_generated_tools.py]]  #script - Load tools into MANAGED_TOOLS
- [[scripts/cleanup_generated_files.ps1]]  #powershell - Clean generated tool code

**Validation:**
- [[scripts/validate_dto_alignment.py]]  #script #validation - Validate tool ↔ method parameter alignment
- [[scripts/show_tools.py]]  #script - List all registered tools

**Model Management:**
- [[scripts/scan_models.py]]  #script - Generate models_inventory_v1.yaml

**Workflow:**
```powershell
# Full regeneration workflow
.\scripts\cleanup_generated_files.ps1
python scripts/generate_tools.py
python scripts/import_generated_tools.py
python scripts/validate_dto_alignment.py
pytest tests/ -v
```

---

## Key Concepts

### R-A-R Pattern (Request-Action-Response)
**Tags:** #pattern #architecture #design-pattern  
**Definition:** Request envelope → Business logic → Response envelope

**Structure:**
```python
Request (operation + payload + metadata) →
  RequestHub validates/enriches →
  Service executes →
  Response (result + status + metadata)
```

**Benefits:** Clean separation, validation centralized, hooks injectable

### Parameter Inheritance
**Tags:** #pattern #dry #code-generation  
**Definition:** Parameters defined once in DTOs, auto-inherited by methods and tools

**Flow:**
```
DTO.field → MethodParameterDef → ToolParameterDef
```

**Mechanism:** Pydantic introspection extracts fields on-demand

### RequestHub Orchestration
**Tags:** #pattern #orchestration #core  
**Definition:** Central dispatcher for all R-A-R operations

**Responsibilities:**
1. Validate auth/session/permissions
2. Enrich context (MDSContext, ToolSession)
3. Apply policy patterns
4. Execute service methods
5. Trigger hooks (metrics, audit)

**Integration:** All routes use `RequestHub.dispatch()`

### Hooks Framework
**Tags:** #pattern #cross-cutting #observability  
**Definition:** Pre/post execution callbacks for cross-cutting concerns

**Types:**
- Metrics: Performance tracking (stage, operation, timestamp)
- Audit: Compliance logging (user, session, status)

**Registry:** Dynamic hook registration in RequestHub

### Tool Factory
**Tags:** #pattern #code-generation #metaprogramming  
**Definition:** Code generator creating Python tools from YAML definitions

**Input:** [[config/toolsets]]/*.yaml #yaml  
**Output:** [[src/pydantic_ai_integration/tools/generated]]/*.py #generated-code  
**Mechanism:** Jinja2 templates + parameter inheritance

---

## Dependency Graph

```
YAML Configs (L5) #yaml #config
    ↓
Tool Factory (generate_tools.py) #script
    ↓
Generated Tools (L4) #generated-code → MANAGED_TOOLS Registry #registry
    ↓
Method Definitions (L3) #models → MANAGED_METHODS Registry #registry
    ↓
Request DTOs (L2) #dtos → Validation
    ↓
RequestHub #core-service → Orchestration
    ↓
Services #service → Business Logic
    ↓
Repositories #repository → Persistence #database
    ↓
Response DTOs (L2) #dtos
```

---

## Legend

**Tags Reference:**
- `#service` - Service layer components
- `#models` - Data models and DTOs
- `#api` - API/HTTP layer
- `#config` - Configuration files
- `#yaml` - YAML files
- `#registry` - Registry patterns
- `#repository` - Data access layer
- `#testing` - Test files
- `#script` - Automation scripts
- `#generated-code` - Auto-generated files
- `#pattern` - Architecture patterns
- `#core` - Core/central components

---

## Related Documentation

- [[HANDOVER.md]]  #documentation - Project status and implementation roadmap
- [[config/toolsets/README.md]]  #documentation - Tool definition guidelines
- [[src/pydantic_ai_integration/README.md]]  #documentation - Tool integration architecture

---

## Quick Reference

**Start Development:**
1. Review [[HANDOVER.md]] #documentation for current status
2. Check [[CODE-MAP.md]] #documentation (this file) for structure
3. Use [[AI/prompts]] #templates for code generation
4. Run synchronization workflow from [[scripts]] #scripts

**Add New Feature:**
1. Define DTOs in [[src/pydantic_models/operations]] #dtos
2. Add method to [[config/methods_inventory_v1.yaml]] #yaml
3. Create service method in [[src/*service]] #service
4. Generate tools: `python scripts/generate_tools.py`
5. Wire into [[src/pydantic_api/routers]] #api-routes
6. Add tests to [[tests/integration]] #testing

**Debug Issues:**
1. Check [[tests/integration/test_request_hub_fastapi.py]] #testing for examples
2. Validate with [[scripts/validate_dto_alignment.py]] #script
3. Review [[src/coreservice/request_hub.py]] #core-service for orchestration logic
4. Use [[AI/prompts/fix-bug.md]] #template

---

### [[src/casefileservice]] - Casefile Management
**Purpose:** Business logic for casefile CRUD operations

**Key Files:**
- [[src/casefileservice/service.py]] - CasefileService with create/read/update/delete methods
- [[src/casefileservice/repository.py]] - Data persistence abstraction (Firestore/Memory)

**Relationships:**
- Uses: [[src/pydantic_models/workspace]], [[src/persistence]]
- Called by: [[src/coreservice/request_hub.py]]
- Models: [[src/pydantic_models/operations]] (CreateCasefileRequest/Response)

---

### [[src/tool_sessionservice]] - Tool Session Management
**Purpose:** Manage tool execution sessions and state

**Key Files:**
- [[src/tool_sessionservice/service.py]] - ToolSessionService for session lifecycle
- [[src/tool_sessionservice/repository.py]] - Session persistence

**Relationships:**
- Uses: [[src/pydantic_models/tool_session.py]]
- Called by: [[src/coreservice/request_hub.py]]
- Integrates: [[src/pydantic_ai_integration]]

---

### [[src/communicationservice]] - External Communications
**Purpose:** Handle Gmail, notifications, external messaging

**Key Files:**
- [[src/communicationservice/service.py]] - CommunicationService (Gmail integration)
- [[src/communicationservice/repository.py]] - Message persistence

**Relationships:**
- Uses: [[src/pydantic_models/canonical]] (external API models)
- Called by: [[src/coreservice/request_hub.py]]
- External: Google Workspace APIs

---

### [[src/authservice]] - Authentication & Authorization
**Purpose:** User authentication and token management

**Key Files:**
- [[src/authservice/routes.py]] - Auth endpoints
- [[src/authservice/token.py]] - JWT token handling

**Relationships:**
- Used by: [[src/pydantic_api]] middleware
- Validates: All requests via [[src/coreservice/request_hub.py]]

---

### [[src/persistence]] - Data Persistence Layer
**Purpose:** Database abstraction and storage

**Key Files:**
- [[src/persistence/firestore]] - Google Firestore implementation

**Relationships:**
- Used by: All service repositories
- Provides: Data storage for casefiles, sessions, messages

---

### [[src/solidservice]] - Solid Pod Integration
**Purpose:** Decentralized data storage integration

**Key Files:**
- [[src/solidservice/client.py]] - Solid Pod client

**Relationships:**
- Alternative storage: Can replace [[src/persistence/firestore]]
- Status: Optional integration

---

## Model System

### [[src/pydantic_models]] - 6-Layer Model Hierarchy
**Purpose:** Single source of truth for all data structures

**Layer 0: Base Infrastructure**
- [[src/pydantic_models/base]] - BaseRequest, BaseResponse, BasePayload
- Core abstractions for R-A-R pattern

**Layer 1: Payload Models**
- [[src/pydantic_models/workspace]] - Business data (Casefile, Document, etc.)
- Pure business logic, no execution metadata

**Layer 2: Request/Response DTOs**
- [[src/pydantic_models/operations]] - Execution envelopes
- CreateCasefileRequest, CreateCasefileResponse
- Contains operation, payload, user_id, session_id, hooks

**Layer 3: Method Definitions**
- [[config/methods_inventory_v1.yaml]] - 26 registered methods
- Loaded into [[src/pydantic_ai_integration/method_registry.py]]
- MANAGED_METHODS registry

**Layer 4: Tool Definitions**
- [[src/pydantic_ai_integration/tools]] - Generated tool code
- MANAGED_TOOLS registry
- Created by [[scripts/generate_tools.py]]

**Layer 5: YAML Configuration**
- [[config/toolsets]] - Source of truth for tool definitions
- [[config/tool_schema_v2.yaml]] - Tool schema

**Relationships:**
```
YAML → generates → Tools → create → Request DTOs → 
  RequestHub validates → Service executes → Response DTOs
```

**Special Models:**
- [[src/pydantic_models/canonical]] - External API models (Gmail, Google Workspace)
- [[src/pydantic_models/views]] - UI/API views
- [[src/pydantic_models/tool_session.py]] - Tool session state

**Model Inventory:**
- Total: 124 models documented
- Registry: [[config/models_inventory_v1.yaml]]

---

## Tool Engineering

### [[src/pydantic_ai_integration]] - Tool Generation & Registry
**Purpose:** Generate executable tools from YAML definitions

**Key Components:**

**Method Registry:**
- [[src/pydantic_ai_integration/method_registry.py]] - MANAGED_METHODS (26 methods)
- [[src/pydantic_ai_integration/method_definition.py]] - ManagedMethodDefinition (16 fields)
- Loads from [[config/methods_inventory_v1.yaml]]

**Tool Registry:**
- [[src/pydantic_ai_integration/tool_decorator.py]] - @register_mds_tool decorator
- [[src/pydantic_ai_integration/tool_definition.py]] - ManagedToolDefinition (12 fields)
- [[src/pydantic_ai_integration/tool_utils.py]] - Tool utilities

**Model Registry:**
- [[src/pydantic_ai_integration/model_registry.py]] - 52 models across 6 layers
- Discovery APIs for model inspection

**Tool Factory:**
- [[scripts/generate_tools.py]] - Generates Python code from YAML
- Uses Jinja2 templates
- Parameter inheritance: DTO → Method → Tool

**Generated Tools:**
- [[src/pydantic_ai_integration/tools/generated]] - Auto-generated tool code
  - workflows/request_hub/ - RequestHub workflow tools
  - core/casefile_management/ - Casefile tools
  - helpers/ - Utility tools

**Relationships:**
```
config/toolsets/*.yaml → generate_tools.py → 
  tools/generated/*.py → MANAGED_TOOLS registry →
  tool execution → RequestHub dispatch
```

**Key Scripts:**
- [[scripts/generate_tools.py]] - Generate tools from YAML
- [[scripts/import_generated_tools.py]] - Load tools into registry
- [[scripts/validate_dto_alignment.py]] - Validate parameter alignment
- [[scripts/show_tools.py]] - List registered tools

---

## API Layer

### [[src/pydantic_api]] - FastAPI Application
**Purpose:** HTTP REST API for all operations

**Key Files:**
- [[src/pydantic_api/app.py]] - FastAPI application instance
- [[src/pydantic_api/dependencies.py]] - Dependency injection (RequestHub, services)

**Routers:**
- [[src/pydantic_api/routers]] - API endpoints
  - casefile routes → [[src/casefileservice]]
  - tool_session routes → [[src/tool_sessionservice]]
  - communication routes → [[src/communicationservice]]
  - auth routes → [[src/authservice]]

**Request Flow:**
```
HTTP Request → FastAPI Router → 
  RequestHub.dispatch() → Service Method → 
  Response + Hook Metadata → HTTP Response
```

**Integration Pattern:**
- Uses [[src/coreservice/request_hub.py]] for all operations
- Dependency injection: `hub: RequestHub = Depends(get_request_hub)`
- Example: [[tests/integration/test_request_hub_fastapi.py]]

---

## Configuration

### [[config]] - System Configuration
**Purpose:** YAML-based configuration for methods, models, and tools

**Key Files:**

**Method Inventory:**
- [[config/methods_inventory_v1.yaml]] - 26 method definitions
  - Classification: domain, subdomain, capability, complexity
  - Execution: request_model, response_model, implementation_class
  - Loaded at startup via [[src/__init__.py]]

**Model Inventory:**
- [[config/models_inventory_v1.yaml]] - 124 models documented
  - 6-layer taxonomy (L0-L5)
  - Field definitions, inheritance chains
  - Generated by [[scripts/scan_models.py]]

**Tool Schema:**
- [[config/tool_schema_v2.yaml]] - Tool definition schema
  - Supports method_name references (parameter inheritance)
  - Classification taxonomy
  - Composite tool patterns

**Tool Definitions:**
- [[config/toolsets/core]] - Core functionality tools
- [[config/toolsets/workflows]] - Multi-step workflow tools
- [[config/toolsets/helpers]] - Utility tools
- [[config/toolsets/prototypes]] - Experimental tools

**Synchronization:**
- Methods loaded: Startup via `register_methods_from_yaml()`
- Models scanned: `python scripts/scan_models.py`
- Tools generated: `python scripts/generate_tools.py`

---

## Testing

### [[tests]] - Test Suite
**Purpose:** Comprehensive testing (85% coverage minimum)

**Structure:**

**Unit Tests:**
- [[tests/coreservice]] - RequestHub unit tests (2 tests)
  - test_request_hub.py - Simple and composite workflows
- [[tests/casefileservice]] - Service unit tests
  - test_memory_repository.py - Repository tests
- [[tests/tool_sessionservice]] - Session service tests
- [[tests/communicationservice]] - Communication service tests

**Integration Tests:**
- [[tests/integration/test_request_hub_fastapi.py]] - End-to-end tests (6 tests)
  - HTTP → RequestHub → Service flow
  - Hook execution validation
  - Context enrichment validation
  - Error handling validation

**Test Results:**
- Total: 8/8 passing (100%)
- Coverage: Request flow, hooks, policies, error handling

**Test Configuration:**
- [[pytest.ini]] - pytest configuration
- [[tests/conftest.py]] - Test fixtures

---

## AI Assistance

### [[AI/prompts]] - Code Generation Templates
**Purpose:** Systematic prompts for AI-assisted development

**Templates:**
- [[AI/prompts/tool-yaml.md]] - YAML tool definitions (30 lines)
- [[AI/prompts/dto-pattern.md]] - R-A-R DTO patterns (35 lines)
- [[AI/prompts/fix-bug.md]] - Bug fixing workflow (25 lines)
- [[AI/prompts/refactor.md]] - Code refactoring workflow (32 lines)

**Format:** Variables → Constraints → Template → Command/Rule

**Usage:** Reference in AI conversations for consistent code generation

---

## Scripts & Utilities

### [[scripts]] - Development Scripts
**Purpose:** Code generation, validation, testing

**Key Scripts:**

**Tool Generation:**
- [[scripts/generate_tools.py]] - Generate Python code from YAML
- [[scripts/import_generated_tools.py]] - Load tools into MANAGED_TOOLS
- [[scripts/cleanup_generated_files.ps1]] - Clean generated tool code

**Validation:**
- [[scripts/validate_dto_alignment.py]] - Validate tool ↔ method parameter alignment
- [[scripts/show_tools.py]] - List all registered tools

**Model Management:**
- [[scripts/scan_models.py]] - Generate models_inventory_v1.yaml

**Workflow:**
```powershell
# Full regeneration workflow
.\scripts\cleanup_generated_files.ps1
python scripts/generate_tools.py
python scripts/import_generated_tools.py
python scripts/validate_dto_alignment.py
pytest tests/ -v
```

---

## Key Concepts

### R-A-R Pattern (Request-Action-Response)
**Definition:** Request envelope → Business logic → Response envelope

**Structure:**
```python
Request (operation + payload + metadata) →
  RequestHub validates/enriches →
  Service executes →
  Response (result + status + metadata)
```

**Benefits:** Clean separation, validation centralized, hooks injectable

### Parameter Inheritance
**Definition:** Parameters defined once in DTOs, auto-inherited by methods and tools

**Flow:**
```
DTO.field → MethodParameterDef → ToolParameterDef
```

**Mechanism:** Pydantic introspection extracts fields on-demand

### RequestHub Orchestration
**Definition:** Central dispatcher for all R-A-R operations

**Responsibilities:**
1. Validate auth/session/permissions
2. Enrich context (MDSContext, ToolSession)
3. Apply policy patterns
4. Execute service methods
5. Trigger hooks (metrics, audit)

**Integration:** All routes use `RequestHub.dispatch()`

### Hooks Framework
**Definition:** Pre/post execution callbacks for cross-cutting concerns

**Types:**
- Metrics: Performance tracking (stage, operation, timestamp)
- Audit: Compliance logging (user, session, status)

**Registry:** Dynamic hook registration in RequestHub

### Tool Factory
**Definition:** Code generator creating Python tools from YAML definitions

**Input:** [[config/toolsets]]/*.yaml  
**Output:** [[src/pydantic_ai_integration/tools/generated]]/*.py  
**Mechanism:** Jinja2 templates + parameter inheritance

---

## Dependency Graph

```
YAML Configs (L5)
    ↓
Tool Factory (generate_tools.py)
    ↓
Generated Tools (L4) → MANAGED_TOOLS Registry
    ↓
Method Definitions (L3) → MANAGED_METHODS Registry
    ↓
Request DTOs (L2) → Validation
    ↓
RequestHub → Orchestration
    ↓
Services → Business Logic
    ↓
Repositories → Persistence
    ↓
Response DTOs (L2)
```

---

## Related Documentation

- [[HANDOVER.md]] - Project status and implementation roadmap
- [[config/toolsets/README.md]] - Tool definition guidelines
- [[src/pydantic_ai_integration/README.md]] - Tool integration architecture

---

## Quick Reference

**Start Development:**
1. Review [[HANDOVER.md]] for current status
2. Check [[CODE-MAP.md]] (this file) for structure
3. Use [[AI/prompts]] templates for code generation
4. Run synchronization workflow from [[scripts]]

**Add New Feature:**
1. Define DTOs in [[src/pydantic_models/operations]]
2. Add method to [[config/methods_inventory_v1.yaml]]
3. Create service method in [[src/*service]]
4. Generate tools: `python scripts/generate_tools.py`
5. Wire into [[src/pydantic_api/routers]]
6. Add tests to [[tests/integration]]

**Debug Issues:**
1. Check [[tests/integration/test_request_hub_fastapi.py]] for examples
2. Validate with [[scripts/validate_dto_alignment.py]]
3. Review [[src/coreservice/request_hub.py]] for orchestration logic
4. Use [[AI/prompts/fix-bug.md]] template

