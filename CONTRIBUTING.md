# Contributing to my-tiny-data-collider

## Setup

```powershell
git clone https://github.com/MSD21091969/my-tiny-data-collider.git
cd my-tiny-data-collider
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
cp .env.example .env  # Edit with your values
pytest  # Verify setup
```

## Code Standards

**Documentation**: Facts only, code examples over prose, no emojis, DRY principle

**Python**:
- Type hints required (`async def method(req: Request) -> Response`)
- Pydantic models for all data (inherit BaseRequest/BaseResponse)
- Async/await for service methods
- Follow existing patterns in `/src/{service}/`

## Patterns

### Service Method
```python
async def method_name(self, request: Request) -> Response:
    start_time = datetime.now()
    # Extract → Validate → Execute → Return with execution_time_ms
    result = await self.repository.method(request.payload)
    return Response(
        request_id=request.request_id,
        status=RequestStatus.COMPLETED,
        payload=result,
        metadata={'execution_time_ms': int((datetime.now() - start_time).total_seconds() * 1000)}
    )
```

### Pydantic Model
```python
class OperationPayload(BaseModel):
    field: str = Field(..., description="What it does")
    optional: Optional[int] = Field(None, ge=0)

class OperationRequest(BaseRequest[OperationPayload]):
    operation: Literal["operation_name"] = "operation_name"

class OperationResultPayload(BaseModel):
    result: str

class OperationResponse(BaseResponse[OperationResultPayload]):
    pass
```

### Tool YAML
```yaml
# config/tools/{domain}/{subdomain}/{tool_name}.yaml
name: tool_name
description: "Action description"
category: "domain"

classification:
  domain: workspace                # [workspace, communication, automation, utilities]
  subdomain: casefile              # Specific area
  capability: create               # [create, read, update, delete, process, search]
  complexity: atomic               # [atomic, composite, pipeline]
  maturity: stable                 # [experimental, beta, stable, deprecated]
  integration_tier: internal       # [internal, external, hybrid]

parameters:
  - name: param
    type: string
    required: true
    description: "Param purpose"

implementation:
  type: api_call                   # [api_call, simple, data_transform, composite]
  api_call:
    client_module: "src.service.service"
    client_class: "ServiceClass"
    method_name: "method_name"

examples:
  - description: "Usage example"
    parameters: {param: "value"}
    expected_outcome: {status: "success"}
```

**See**: `docs/yaml_classification_schema.md` for full field reference

## Commits

```
type(scope): Short description

- Bullet points
- Facts only
```

Types: `feat`, `fix`, `refactor`, `test`, `docs`, `chore`

## Architecture

### Registries
**MANAGED_TOOLS** (`tool_decorator.py`): Global registry of all tools with metadata, classification, validation  
**MANAGED_METHODS** (Phase 7): Parallel registry for service methods

**Discovery API** (11 methods):
```python
get_registered_tools() -> Dict[str, ManagedToolDefinition]
get_tools_by_domain(domain) -> List[ManagedToolDefinition]
get_tools_by_capability(capability) -> List[ManagedToolDefinition]
get_hierarchical_tool_path(name) -> str  # "workspace.casefile.create"
get_classification_summary() -> Dict  # Stats
# + 6 more (complexity, maturity, tier, subdomain, exists, definition)
```

### Data Flow
```
YAML → ToolFactory.load_tool_config() → validate → Jinja2 → generated tool
     → @register_mds_tool → MANAGED_TOOLS → ToolSessionService.process_tool_request
```

### Classification System
**6 fields** (domain, subdomain, capability, complexity, maturity, integration_tier)  
**See**: `docs/yaml_classification_schema.md`

### File Structure
```
src/
├── pydantic_models/
│   ├── base/           # BaseRequest[T], BaseResponse[T], RequestStatus
│   ├── canonical/      # CasefileModel, ToolSession, UserModel
│   ├── operations/     # Request/Response pairs (casefile_ops, tool_session_ops, etc.)
│   └── workspace/      # Gmail, Drive, Sheets types
├── casefileservice/    # 13 methods (CRUD, ACL, workspace sync)
├── tool_sessionservice/    # 5 methods (session lifecycle, tool execution)
├── communicationservice/   # 6 methods (chat sessions, processing)
└── pydantic_ai_integration/
    ├── tool_decorator.py       # @register_mds_tool, MANAGED_TOOLS
    └── tools/factory/          # YAML → Python generator

config/
├── tool_schema_v2.yaml         # Classification schema
└── tools/{domain}/{subdomain}/ # Tool YAMLs

docs/
├── methods_inventory_v1.0.0.md           # 30 methods catalog
├── request_response_model_mapping.md     # Pydantic models (83% coverage)
├── yaml_classification_schema.md         # 6-field taxonomy
└── tool_engineering_foundation.md        # Registry + ToolFactory reference
```

## Current System

**Methods**: 30 across 6 services
- CasefileService: 13 (CRUD:5, ACL:4, workspace sync:3, session:1)
- ToolSessionService: 5 (lifecycle:4, execution:1)
- CommunicationService: 6 (lifecycle:4, processing:2)
- GmailClient: 4, DriveClient: 1, SheetsClient: 1

**Models**: 100 Pydantic models (25 req/resp pairs, 83% coverage)
- Missing: 5 pairs (list_permissions, check_permission, store_gmail_messages, store_drive_files, store_sheet_data)

**Tools**: YAML-based generation system ready
- 3 example YAMLs in config/tools/
- ToolFactory operational
- @register_mds_tool decorator + MANAGED_TOOLS registry

**See**: `docs/methods_inventory_v1.0.0.md` for full catalog

## Workflow

**Testing**:
```bash
pytest                          # All tests
pytest tests/unit/              # Unit only
pytest -v -k test_create        # Pattern match
pytest --cov=src                # Coverage
```

**Tool Generation**:
```bash
python scripts/generate_tools.py                    # All YAMLs
python scripts/generate_tools.py tool_name          # Specific tool
python scripts/generate_tools.py --validate-only    # Check YAMLs
python scripts/show_tools.py                        # List registered
```

**Discovery**:
```python
from src.pydantic_ai_integration.tool_decorator import get_tools_by_domain
tools = get_tools_by_domain("workspace")  # Query registry
```

## Principles

1. **Service methods**: BaseRequest[T] → BaseResponse[T] pattern with execution_time_ms
2. **Tools**: YAML-first, @register_mds_tool decorator, MANAGED_TOOLS registry
3. **Classification**: 6 fields (domain/subdomain/capability/complexity/maturity/tier)
4. **Models**: All data in Pydantic, Field() with descriptions
5. **Status tracking**: RequestStatus enum (PENDING, IN_PROGRESS, COMPLETED, FAILED)
6. **Audit trail**: User → Session → Request → Event → Casefile
7. **Persistence**: Firestore for all data
8. **Type safety**: Type hints required everywhere

## Method Registry (Phases 7-13)

**Future work**: MANAGED_METHODS parallel to MANAGED_TOOLS
- Phase 7: Registry structure (MethodDefinition class)
- Phase 8: Generate 5 missing Pydantic models
- Phase 9: YAML artifact (methods_inventory_v1.yaml)
- Phase 10: @register_service_method decorator
- Phase 11: ToolFactory integration (validate api_call.method_name)
- Phase 12-13: Documentation + versioning

## References

**Docs**:
- `docs/methods_inventory_v1.0.0.md` - 30 methods catalog with signatures
- `docs/request_response_model_mapping.md` - Pydantic model coverage
- `docs/yaml_classification_schema.md` - 6-field taxonomy reference
- `docs/tool_engineering_foundation.md` - Registry + ToolFactory

**Code**:
- `src/pydantic_ai_integration/tool_decorator.py` - MANAGED_TOOLS registry
- `src/pydantic_ai_integration/tools/factory/` - YAML generator
- `config/tool_schema_v2.yaml` - Classification schema
- `src/pydantic_models/operations/` - Request/Response models
