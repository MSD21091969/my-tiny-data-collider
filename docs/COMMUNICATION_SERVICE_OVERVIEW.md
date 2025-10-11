# communicationservice Overview

**Tags:** `chat` `requesthub`

## Directory Snapshot

```text
src/communicationservice/
  repository.py   # Firestore repository for chat sessions/messages
  service.py      # ContextAwareService subclass for chat workflows (chat-only scope)
```

## Role in R-A-R Flow

- RequestHub maps chat-related operations (`create_chat_session`, `process_chat_request`, `close_chat_session`, etc.) to this service.
- Service inherits `ContextAwareService`, so hooks capture chat metadata and audit trails.
- Currently scoped to chat session lifecycle and message processing; no direct tool execution orchestration yet.

## Key Components

| Component | Purpose | Notes |
| --- | --- | --- |
| `CommunicationService` | Handles chat session lifecycle and chat request processing | Exposes methods mirrored in chat tool YAML templates |
| `ChatSessionRepository` | Firestore persistence for chat sessions and messages | Injected via `ServiceContainer`; supports request tracing |

## Open Questions / Next Actions

1. Build route-level tests simulating chat requests through FastAPI → RequestHub → CommunicationService to validate context propagation.
2. Ensure chat request metadata (session IDs, hook outputs) aligns with audit requirements.
3. Evaluate optional integrations (Pub/Sub, logging, execution engine) while keeping chat scope clear and layered via configuration.

## Navigation

- [[CORE_SERVICE_OVERVIEW.md|coreservice overview]]
- [[TOOL_SESSION_SERVICE_OVERVIEW.md|tool_sessionservice overview]]
- [[BRANCH_DEVELOPMENT_PLAN.md|branch development plan]]
