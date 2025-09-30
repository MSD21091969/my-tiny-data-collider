# Copilot instructions for MDS Objects API

## Quick map
- `main.py` bootstraps the FastAPI server via `src/pydantic_api/app.py`; the app wires auth, casefile, tool-session, and optional chat routers.
- Service layers live under `src/*service/` and wrap persistence repositories plus domain logic; API routes only compose these services.
- Data contracts are defined in `src/pydantic_models/**` and carry computed fields used across services, so prefer reusing them over ad-hoc dicts.

## Environment & config
- Defaults assume `ENVIRONMENT=development`; production flips feature flags in `src/coreservice/config.py`.
- Set `USE_MOCKS=true` (default in non-production) to run everything in-memory; setting it to false expects Firestore credentials (`GOOGLE_APPLICATION_CREDENTIALS`, `FIRESTORE_DATABASE`, `GOOGLE_CLOUD_PROJECT`).
- `.env` is loaded automatically in `main.py`; keep new config keys there and expose via helper functions in `coreservice.config`.

## Persistence patterns
- Repositories (`casefileservice.repository`, `tool_sessionservice.repository`, `communicationservice.repository`) mirror the same API for mock vs Firestore backends. Always call `model_dump(mode="json")` before writing to Firestore to serialize UUIDs.
- When adding new collections, follow the existing pattern: initialize in `*_init_firestore`, gracefully fall back to mocks if `firebase_admin` import fails, and keep string IDs in Firestore documents.
- `persistence/firestore/context_persistence.py` chunks oversized fields; reuse `_split_large_context` logic rather than bypassing it.

## Pydantic + agent workflow
- Request models extend `BaseRequest`; set both `user_id` and `operation` explicitly when constructing them in tests or services.
- `ToolSessionService.process_tool_request` re-validates input with `model_dump(mode="json", exclude={...})` to strip computed fields—mirror this pattern when you add new services that persist `BaseModel` instances.
- Agent tools register via `@default_agent.tool` (see `pydantic_ai_integration/tools/enhanced_example_tools.py`) and expect an `MDSContext` as the first argument. Use `context.register_event(...)` to keep the audit trail consistent and update `last_event.result_summary` before returning.
- New tools should also be registered in `pydantic_ai_integration/agents/base.py` if they need a specific agent binding.

## Casefiles, sessions & chat
- Casefiles use string IDs from `generate_casefile_id()` (`yymmdd_random`) and store session UUIDs; never coerce IDs to UUIDs when writing to Firestore.
- `ToolSessionService.create_session` links sessions to casefiles through `CasefileService.add_session_to_casefile`; preserve this flow to keep metadata in sync.
- Session payloads track `session_request_id` to correlate requests/responses—always forward any client-supplied ID.
- `communicationservice.service` bridges chat messages to tool executions by embedding tool session IDs in `session.metadata`; reuse that contract if you introduce new message types.

## Developer workflows
- Run the API locally with `python scripts/main.py`; it enables Uvicorn reload automatically when `ENVIRONMENT=development`.
- `pytest` respects `pytest.ini` (`pythonpath=.` and `asyncio_mode=auto`). Without Firestore access, export `USE_MOCKS=true` or filter out Firestore-heavy scripts (`pytest -k "not firestore"`).
- Use `python scripts/debug_startup.py` to sanity-check imports and JWT creation without launching the server.

## Copilot chore cadence
- File recurring maintenance work using the issue template at `.github/ISSUE_TEMPLATE/copilot-chore-checklist.md`; it auto-assigns the `github-copilot` user with `chore` + `automation` labels.
- Ensure each run captures `pytest` output, FastAPI startup confirmation, and findings from ID prefix/manual smoke tests in the "Observations & follow-ups" section.
- Open follow-up issues for dependency bumps or regressions instead of packing them into the chore ticket.

## Implementation tips
- When extending repositories or services, accept an optional `use_mocks` flag so tests can force the backend.
- Prefer storing timestamps via `datetime.now().isoformat()` to match existing documents and computed fields.
- Keep logging consistent with existing modules (module-level logger + `logging.basicConfig` in entrypoints).
- Before persisting new context fields, ensure they’re JSON-serializable (follow helpers in `MDSContext._ensure_serializable_dict`).
