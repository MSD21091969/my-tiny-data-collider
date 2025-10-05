# My Tiny Data Collider

Declarative tool platform that turns YAML specifications into Pydantic-validated async tools, FastAPI routes, and aligned test suites.

---

## System Overview

- **Source of truth:** YAML definitions in `config/tools/{domain}/{subdomain}/`.
- **Generation target:** Python implementations under `src/pydantic_ai_integration/tools/generated/` plus mirrored unit, integration, and API tests.
- **Runtime core:** `src/pydantic_ai_integration/tool_decorator.py`, `tool_sessionservice/service.py`, and `src/persistence/firestore/context_persistence.py`.

---

## Daily Workflow

1. Update or add a YAML tool spec.
2. Regenerate artefacts.
3. Import generated modules to populate the registry.
4. Execute focused tests.

```powershell
python scripts/generate_tools.py
python scripts/import_generated_tools.py
python scripts/show_tools.py
pytest tests/integration/test_tool_response_wrapping.py -q
```

---

## Key Paths

| Path | Notes |
| --- | --- |
| `config/tools/**` | Tool metadata, classification, business rules. |
| `src/pydantic_ai_integration/tools/factory/` | Jinja templates + generator utilities. |
| `src/tool_sessionservice/` | Enforcement and execution orchestration. |
| `tests/**` | Generated parity tests; keep them in sync with YAML. |

---

## Testing Matrix

- `tests/unit/` — Validation and parameter models.
- `tests/integration/` — Service-layer execution with async context.
- `tests/api/` — FastAPI contract coverage.
- Manual regression guard: `tests/integration/test_tool_response_wrapping.py`.

---

## Reference

- [`DEVELOPER_GUIDE.md`](DEVELOPER_GUIDE.md) — End-to-end workflow, coding standards, testing matrix, and assistant expectations.
- [`HANDOVER.md`](HANDOVER.md) — Current architecture, governance, and process checklist.
