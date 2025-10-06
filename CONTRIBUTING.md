# Developer Guidelines - my-tiny-data-collider

## Setup

```powershell
# Clone
git clone https://github.com/MSD21091969/my-tiny-data-collider.git
cd my-tiny-data-collider

# Create venv
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Environment variables
cp .env.example .env
# Edit .env with your values

# Run tests
pytest

# Run server (if applicable)
python -m uvicorn src.main:app --reload
```

## Code Style

### Documents
- Facts only, no emojis, no verbose prose
- Code examples over explanations
- Direct, technical language

### Python
- Type hints required
- Pydantic models for all data structures
- Async/await for service methods
- Follow existing patterns

## Service Method Pattern

```python
async def method_name(self, request: Request) -> Response:
    start_time = datetime.now()
    
    # Extract
    user_id = request.user_id
    data = request.payload
    
    # Validate
    if not valid:
        return error_response()
    
    # Execute
    result = await self.repository.method(data)
    
    # Return
    execution_time_ms = int((datetime.now() - start_time).total_seconds() * 1000)
    return Response(
        request_id=request.request_id,
        status=RequestStatus.COMPLETED,
        payload=result,
        metadata={'execution_time_ms': execution_time_ms}
    )
```

## Model Pattern

```python
class Model(BaseModel):
    field: str = Field(..., description="Description")
    
    @computed_field
    @property
    def derived(self) -> int:
        return len(self.field)
    
    def business_logic(self) -> None:
        # Implementation
        pass
```

## Tool Pattern

```yaml
# config/tools/domain/subdomain/tool_name.yaml
name: tool_name
description: "What it does"
category: "domain"

classification:
  domain: workspace
  subdomain: casefile
  capability: create
  complexity: atomic
  maturity: stable
  integration_tier: internal

parameters:
  - name: param
    type: string
    required: true

implementation:
  type: api_call
  api_call:
    client_class: "Service"
    method_name: "method"
```

## Commit Messages

```
type(scope): Short description

- Bullet point details
- No paragraphs
- Facts only
```

Types: feat, fix, refactor, test, docs, chore

## File Organization

```
src/
├── pydantic_models/
│   ├── base/          # BaseRequest, BaseResponse, RequestStatus
│   ├── canonical/     # CasefileModel, ToolSession, UserModel
│   ├── operations/    # Request/Response pairs for services
│   ├── views/         # Summary models for API responses
│   └── workspace/     # Gmail, Drive, Sheets data types
├── casefileservice/
│   ├── service.py     # Business logic
│   └── repository.py  # Firestore persistence
├── tool_sessionservice/
├── communicationservice/
├── coreservice/
└── pydantic_ai_integration/
    ├── tool_decorator.py      # @register_mds_tool
    ├── tool_definition.py     # ManagedToolDefinition
    └── tools/factory/         # YAML → Python generator

config/
├── tool_schema_v2.yaml        # Schema definition
└── tools/                     # Tool YAML definitions

scripts/
└── phase2_*.py               # Implementation references

tests/
├── unit/
└── integration/
```

## Current Status

**Service Methods:**
- CasefileService: 11 methods
- ToolSessionService: 5 methods
- Phase 2 adds: +23 methods (in scripts/, not integrated)

**Models:**
- CasefileModel, ToolSession, ToolEvent: implemented
- UserModel: in phase2_03 (not integrated)

**Tools:**
- 3 example YAMLs in config/tools/
- Tool factory ready
- No production tools yet

## Phase 2 Integration TODO

See HANDOVER.md for integration steps.

1. Fix EmailStr in scripts/phase2_03_user_model.py
2. Enhance CasefileModel from phase2_01
3. Enhance ToolSession from phase2_02
4. Add UserModel from phase2_03
5. Add service methods from phase2_04, phase2_05, phase2_06
6. Add tests from phase2_07

## Testing

```bash
# All tests
pytest

# Specific
pytest tests/unit/
pytest tests/integration/
pytest -v -k test_name

# Coverage
pytest --cov=src
```

## Tool Generation

```bash
# Generate from YAML
python scripts/generate_tools.py tool_name

# Show registered tools
python scripts/show_tools.py
```

## Key Principles

1. One pattern for service methods (see above)
2. All data in Pydantic models
3. All operations return RequestStatus
4. All operations track execution_time_ms
5. All tools registered via @register_mds_tool
6. All tools defined in YAML first
7. Audit trail: User → Session → Request → Event → Casefile
8. Firestore for all persistence

## Debugging

```python
import logging
logger = logging.getLogger(__name__)
logger.info(f"Message: {var}")
logger.error(f"Error: {e}", exc_info=True)
```

## Questions

Check these first:
1. TOOL_ENGINEERING_ANALYSIS.md - Architecture overview
2. HANDOVER.md - Phase 2 integration guide
3. config/tool_schema_v2.yaml - Tool YAML schema
4. Existing code in src/ - Follow patterns
