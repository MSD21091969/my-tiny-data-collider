# Pydantic AI Integration

Tool execution framework with decorator-based tool registration, YAML-driven tool generation, and Google Workspace integrations.

## Structure

```
pydantic_ai_integration/
├── tool_decorator.py    # @mds_tool decorator, tool registry
├── tool_definition.py   # ManagedToolDefinition (single source of truth)
├── dependencies.py      # MDSContext for tool execution state
├── execution/
│   └── chain_executor.py    # Multi-tool execution chains
├── integrations/
│   └── google_workspace/
│       ├── clients.py       # Gmail, Drive, Sheets API clients
│       └── models.py        # External API request/response models
└── tools/
    ├── examples/
    │   └── unified_example_tools.py  # Example tool implementations
    ├── factory/
    │   └── templates/       # Jinja2 templates for code generation
    └── generated/           # YAML-generated tool implementations
        ├── echo_tool.py
        ├── gmail_*.py
        ├── drive_*.py
        └── sheets_*.py
```

## Three-Layer Architecture

**LAYER 1: Domain Models** (`../pydantic_models/`)
- Canonical entities, operations, views

**LAYER 2: Integration Models** (`integrations/google_workspace/models.py`)
- External API contracts (Gmail, Drive, Sheets)
- Request/response models for Google Workspace APIs

**LAYER 3: Generated Tool Parameters** (`tools/generated/*.py`)
- YAML-generated from `config/tools/*.yaml`
- Parameter validation models for tool execution

## Tool Registration

```python
from pydantic_ai_integration.tool_decorator import mds_tool

@mds_tool(
    name="echo_tool",
    description="Echoes input text",
    category="utilities"
)
def echo_tool(text: str, ctx: MDSContext) -> dict:
    return {"echo": text}
```

## Tool Definition

`ManagedToolDefinition` is the single source of truth:

```python
from pydantic_ai_integration.tool_definition import ManagedToolDefinition

tool = ManagedToolDefinition(
    name="echo_tool",
    description="Echoes input text",
    business_rules=["Input must be non-empty"],
    category="utilities",
    yaml_path="config/tools/echo_tool.yaml"
)
```

## YAML-Driven Generation

Tools defined in `config/tools/*.yaml` generate:
1. Parameter models (`tools/generated/*.py`)
2. Integration tests
3. API tests
4. Tool implementations (if template provided)

## MDSContext

Execution context passed to all tools:

```python
class MDSContext(BaseModel):
    casefile_id: Optional[str]
    session_id: Optional[str]
    user_id: str
    request_id: str
    events: List[ToolEvent]
    
    def log_event(self, tool_name: str, status: str):
        # Track tool execution events
```

## Google Workspace Integrations

**Clients** (`integrations/google_workspace/clients.py`):
- `GmailClient`, `DriveClient`, `SheetsClient`
- Handle API authentication and requests

**Models** (`integrations/google_workspace/models.py`):
- `GmailListMessagesRequest`, `GmailSendMessageRequest`
- `DriveListFilesRequest`
- `SheetsBatchGetRequest`

**Generated Tools** (`tools/generated/gmail_*.py`, etc.):
- Orchestrate client calls with validation
- Return structured responses
