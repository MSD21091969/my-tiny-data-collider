# Pydantic Models

Organized by purpose: base infrastructure, canonical entities, operations, views, and workspace data.

## Structure

```
pydantic_models/
├── base/          # Infrastructure (BaseRequest, BaseResponse, RequestStatus)
├── canonical/     # Domain entities with business logic
├── operations/    # Request/response DTOs for API operations
├── views/         # Lightweight projections for list operations
└── workspace/     # External workspace data (Gmail, Drive, Sheets)
```

## Import Patterns

```python
# Infrastructure
from pydantic_models.base.envelopes import BaseRequest, BaseResponse
from pydantic_models.base.types import RequestStatus

# Canonical entities
from pydantic_models.canonical.casefile import CasefileModel
from pydantic_models.canonical.tool_session import ToolSession
from pydantic_models.canonical.chat_session import ChatSession

# Operations
from pydantic_models.operations.casefile_ops import CreateCasefileRequest
from pydantic_models.operations.tool_execution_ops import ToolRequest

# Views
from pydantic_models.views.casefile_views import CasefileSummary

# Workspace
from pydantic_models.workspace.gmail import GmailMessage
```

## Design

- **Canonical models** contain business logic and validation rules
- **Operations** are data transfer objects (DTOs) only
- **Views** are optimized projections for list operations
- All operations use `BaseRequest[PayloadT]` / `BaseResponse[PayloadT]` envelope pattern

## Migration

Reorganized from domain-based structure (casefile/, tool_session/, communication/) to purpose-based structure. See `PYDANTIC_MIGRATION.md` for details.
