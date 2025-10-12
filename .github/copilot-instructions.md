# Tiny Data Collider - AI Agent Instructions

## AI Chat Practices

### Core Principles
- Ship answers in developer voice—concise, direct, and code-first.
- Stay DRY: avoid repeating established facts or restating plan items.
- Base every response on repository evidence, tool output, or executable code.
- Skip fluff, emojis, and management speak; maintain engineering cadence.
- Work autonomously when the task is clear and the user has delegated ownership.

### Response Guidelines
- Unblock the user's immediate question; reference `BRANCH_DEVELOPMENT_PLAN.md` when it anchors context.
- Reach for MCP tools, repo utilities, or test runs whenever they yield authoritative answers for CI/CD or workspace state.
- Prefer file paths, diffs, or command output over prose when they communicate faster.
- Keep responses tight; produce layered summaries only when the user requests them explicitly.
- Call out follow-up actions only when they exist and align with the current plan.

### Conversation Flow
- Reply in sequence and log new decisions or discoveries in the branch plan as they surface.
- Investigate with tools first, then report back with citations to files or commands.
- Treat living documents (`BRANCH_DEVELOPMENT_PLAN.md`, subsystem overviews) as the shared ledger for ongoing work.
- Advance without transition fluff; no restating prior agreements or conclusions.

### Documentation
- Document code and systems factually, using the established overview structure as the template.
- Update living documents in place instead of creating parallel summaries.
- Add inline code comments sparingly, only where logic is non-obvious.
- Avoid recap reports or management-style summaries that repeat existing content.

## Development Toolset

### Toolset Location
Tools are installed globally at: `C:\Users\HP\my-tiny-toolset\`

### Available Tools
- **code_analyzer.py**: Analyzes Python code for models, functions, and API patterns
- **version_tracker.py**: Tracks version history and changes across the codebase
- **mapping_analyzer.py**: Analyzes model mappings and transformations
- **excel_exporter.py**: Exports analysis results to Excel format

### VS Code Integration
Tools are accessible via VS Code tasks. Use Command Palette (Ctrl+Shift+P) → "Tasks: Run Task" → Select tool.

### Tool Usage
All tools accept `${workspaceFolder}` as the target directory and output results to their respective directories with appropriate flags (--csv, --json, --yaml, --quiet).

## Architecture Overview
This is a FastAPI-based microservices architecture for AI tool management and execution. Key components:

- **pydantic_api**: Main FastAPI app with middleware stack (auth, rate limiting, metrics, CORS)
- **Services**: Domain-specific services (auth, casefile, communication, tool_session) following repository-service pattern
- **pydantic_ai_integration**: Tool and method registration system with decorators and YAML inventory
- **Persistence**: Firestore for data, Redis for caching, async connection pools
- **Models**: Pydantic-based request/response models in `pydantic_models/` (base, canonical, operations, views)

## Core Patterns

### Service-Repository Pattern
Each domain has:
- `repository.py`: Async data access (Firestore)
- `service.py`: Business logic and orchestration

Example: `tool_sessionservice/service.py` uses `ToolSessionRepository` for persistence.

### Request-Action-Response (R-A-R)
Workflows orchestrated in `coreservice/request_hub.py` with pre/post hooks:
```python
# Example from request_hub.py
async def execute_request(self, request: BaseRequest) -> BaseResponse:
    await self._run_pre_hooks(request)
    response = await self._execute_action(request)
    await self._run_post_hooks(request, response)
    return response
```

### Tool Registration
Tools registered via `@register_mds_tool` decorator or YAML inventory:
- Decorators in `pydantic_ai_integration/tool_decorator.py`
- YAML config in `config/methods_inventory_v1.yaml`
- Loaded at startup in `pydantic_ai_integration/__init__.py`

### Dependency Injection
Use `MDSContext` from `pydantic_ai_integration/dependencies.py` for shared state:
```python
from pydantic_ai_integration.dependencies import MDSContext

async def some_function(ctx: MDSContext) -> None:
    session_id = ctx.session_id
    user_id = ctx.user_id
```

## Development Workflows

### Setting Up the Environment
```bash
# Install dependencies (including dev dependencies)
pip install -e .[dev]

# Or install only runtime dependencies
pip install -e .
```

### Running the Application
```bash
# Development with auto-reload
uvicorn src.pydantic_api.app:app --reload --host 0.0.0.0 --port 8000

# Production
uvicorn src.pydantic_api.app:app --host 0.0.0.0 --port 8000
```

### Testing
```bash
# All tests
pytest

# Specific markers
pytest -m "unit"          # Fast unit tests
pytest -m "integration"   # Integration tests
pytest -m "firestore"     # Firestore-dependent tests
pytest -m "mock"          # Mock-based tests
pytest -m "slow"          # Slow tests (>5s)
```

### Code Quality
```bash
# Format code
black .

# Lint
ruff check . --fix

# Type check
mypy src/
```

## Key Conventions

### Async Everywhere
All repositories, services, and API endpoints are async. Use `await` consistently.

### Model Structure
- **Base**: Common types, envelopes (`BaseRequest`, `BaseResponse`)
- **Canonical**: Core business entities (`ToolSession`, `Casefile`)
- **Operations**: Request/response DTOs (`CreateSessionRequest`)
- **Views**: API response projections (`SessionSummary`)

### Error Handling
Use middleware stack for cross-cutting concerns. Services raise specific exceptions caught by `ErrorHandlingMiddleware`.

### Configuration
- Environment variables in `.env` (see `.env.example`)
- YAML configs in `config/` for tools/methods
- Firestore database: `mds-objects`
- Redis: `redis://localhost:6379/0`

### Logging
Use structured logging with context:
```python
logger = logging.getLogger(__name__)
logger.info("Operation completed", extra={"session_id": session_id, "user_id": user_id})
```

## Integration Points

### External Dependencies
- **Google Cloud Firestore**: Primary persistence
- **Redis**: Caching layer
- **Pydantic AI**: Tool execution framework
- **JWT**: Authentication via `authservice`

### Cross-Service Communication
Services communicate via shared models and repositories. No direct HTTP calls between services.

### Health Checks
`/health` endpoint checks Firestore pool and Redis connectivity.

## Common Patterns

### Creating New Operations
1. Define request/response models in `pydantic_models/operations/`
2. Add to `request_hub.py` orchestration
3. Implement in appropriate service
4. Add router endpoint in `pydantic_api/routers/`

### Adding Tools
1. Register in YAML `config/methods_inventory_v1.yaml`
2. Or use `@register_mds_tool` decorator
3. Implement execution logic in service

### Database Operations
Always use repositories for data access. Example:
```python
# In service
session = await self.repository.get_by_id(session_id)
await self.repository.update(session)
```

Reference files: `src/tool_sessionservice/repository.py`, `src/casefileservice/repository.py`</content>
<parameter name="filePath">c:\Users\HP\Documents\Python\251008\.github\copilot-instructions.md