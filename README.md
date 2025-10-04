# My Tiny Data Collider

Declarative tool engineering stack that transforms YAML specs into Pydantic-validated tools, FastAPI routes, and supporting tests.

---

## Snapshot — 5 Oct 2025

- **YAML is authoritative.** All generated modules/tests were purged during cleanup and should be rebuilt from the YAML definitions when needed.
- **Runtime infrastructure lives on.** Decorator, registry, generator templates, Firestore stub, and service layers remain under `src/`.
- **Agents still receive context.** `src/persistence/firestore/context_persistence.py` continues to hydrate `MDSContext` for tool execution.
- **Async pytest support restored.** `pytest-asyncio` is installed, so async tests execute instead of being skipped.

---

## Regenerate on demand

1. Edit YAML in `config/tools/**`.
2. Generate artefacts:
	```powershell
	python scripts/generate_tools.py
	```
	- Tools land in `src/pydantic_ai_integration/tools/generated/...`.
	- Tests appear in `tests/unit|integration|api/...`.
3. Run suites:
	```powershell
	pytest tests/unit -q
	pytest tests/integration -q
	pytest tests/api -q
	```
4. Commit both YAML and regenerated outputs.

Until step 2 runs, the generated directories will be empty by design.

---

## Key components

| Location | Purpose |
| --- | --- |
| `config/tools/**` | Declarative tool definitions (single source of truth) |
| `src/pydantic_ai_integration/tool_decorator.py` | `@register_mds_tool`, MANAGED_TOOLS registry |
| `src/pydantic_ai_integration/tools/factory/` | ToolFactory and Jinja templates |
| `src/pydantic_ai_integration/execution/firebase_stub.py` | Local Firestore shim used by generated tools |
| `src/tool_sessionservice/service.py` | Service orchestrating tool execution and audit trail |
| `src/persistence/firestore/context_persistence.py` | Persists session context used to build `MDSContext` |
| `tests/integration/test_tool_response_wrapping.py` | Hand-authored regression that guards the ToolResponse envelope |

---

## Developer quick start

```powershell
pip install -e ".[dev]"
python scripts/generate_tools.py
pytest tests/integration/test_tool_response_wrapping.py -q
```

See [`INSTALL.md`](INSTALL.md) for complete setup instructions and [`HANDOVER.md`](HANDOVER.md) for the latest project summary.
