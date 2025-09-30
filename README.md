# MDS Objects API

FastAPI-powered service for managing casefiles, tool sessions, and chat workflows with consistent, prefixed identifiers. The project centralizes ID generation, supports mock or Firestore persistence, and offers integration points for agent-driven tool execution.

## Features

- **Centralized ID service** that issues prefixed IDs (`cf_`, `ts_`, `sr_`, `te_`, `cs_`) for casefiles, tool sessions, session requests, tool events, and chat sessions.
- **Service and repository layer** covering casefile, tool session, communication, and auth workflows.
- **Mock and Firestore backends** with seamless switching via environment configuration.
- **Agent integration** through Pydantic-driven tool definitions and context tracking.
- **Comprehensive tests** validating ID prefixes across services.

## Getting Started

### Prerequisites

- Python 3.11+
- (Optional) Google Cloud credentials if running against Firestore.

### Installation

```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

### Configuration

Configuration is driven by environment variables (defaults favor development):

- `ENVIRONMENT`: defaults to `development`.
- `USE_MOCKS`: set to `true` (default) to run fully in-memory; set to `false` to use Firestore.
- `GOOGLE_APPLICATION_CREDENTIALS`, `FIRESTORE_DATABASE`, `GOOGLE_CLOUD_PROJECT`: required when `USE_MOCKS=false`.

Create a `.env` file to store local overrides; it is automatically loaded at startup.

### Running the API

```powershell
.\.venv\Scripts\activate
python scripts/main.py
```

The app starts a FastAPI server with automatic reload in development.

### Running Tests

```powershell
.\.venv\Scripts\activate
pytest
```

Tests default to the mock persistence layer and include coverage of ID prefix enforcement.

## Repository Tasks

- `src/coreservice/id_service.py`: central ID generation logic.
- `src/casefileservice`, `src/tool_sessionservice`, `src/communicationservice`: service and repository layers.
- `tests/test_id_prefixes.py`: end-to-end validation of ID prefix rules.

## Deploying with Firestore

1. Set `USE_MOCKS=false`.
2. Provide Google credentials via `GOOGLE_APPLICATION_CREDENTIALS` and set `FIRESTORE_DATABASE`/`GOOGLE_CLOUD_PROJECT`.
3. Start the API; repositories automatically initialize Firestore collections and subcollections.

## Development Notes

- Runtime helpers now live under `scripts/` (`scripts/main.py`, `scripts/debug_startup.py`, `scripts/get_token.py`).
- JWT helpers live in `src/authservice/token.py` and now use timezone-aware timestamps.
- `.gitignore` excludes virtual environments, cache directories, and environment files.
- `pytest.ini` configures asyncio fixtures with function scope to keep event loops isolated.
