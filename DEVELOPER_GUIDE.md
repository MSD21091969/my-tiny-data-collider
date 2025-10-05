# Developer Guide — My Tiny Data Collider

Unified guidance for developers working on the `develop` branch. Start with the quick-start checklist, then dip into the deep-dive sections as needed.

## Quick Start

### 1. Environment setup
```powershell
python -m venv venv
.\venv\Scripts\activate
pip install -e ".[dev]"
```

### 2. Daily loop
1. Edit or add YAML under `config/tools/{domain}/{subdomain}/`.
2. Regenerate artefacts:
   ```powershell
   python scripts/generate_tools.py
   python scripts/import_generated_tools.py
   python scripts/show_tools.py   # optional registry audit
   ```
3. Run fast tests:
   ```powershell
   pytest tests/integration/test_tool_response_wrapping.py -q
   pytest tests/unit -q
   pytest tests/api -q
   ```
4. Repeat: YAML → regenerate → rerun relevant suites.

### 3. Branch & PR flow
| Branch | Purpose |
| --- | --- |
| `main` | Production-ready artefacts |
| `develop` | Integration branch for completed work |
| `feature/*` | Scoped work or experiments based on `develop` |
| `hotfix/*` | Emergency fixes branched from `main` |

Workflow: branch from `develop` → make focused commits → open PR back to `develop` → ensure tests pass → merge → promote `develop` to `main` when release-ready.

### 4. Pre-PR checklist
- [ ] Clean history with descriptive commit messages (`feat:`, `fix:`, etc.).
- [ ] `pip install -e ".[dev]"` run if the environment may have drifted.
- [ ] `python scripts/generate_tools.py` rerun after any YAML or classification change.
- [ ] Relevant pytest suites executed locally with captured output.
- [ ] Documentation (`README.md`, `HANDOVER.md`, this guide) updated for behaviour or workflow changes.

## Deep Dive

### Repository architecture
- **Source of truth:** YAML specs live under `config/tools/{domain}/{subdomain}/`. Schema details sit in `config/tool_schema_v2.yaml` with reusable policy templates in `config/policies/**`.
- **Generated artefacts:** `python scripts/generate_tools.py` emits modules in `src/pydantic_ai_integration/tools/generated/**` plus mirrored tests in `tests/{unit|integration|api}/**`. Never hand-edit these outputs.
- **Runtime execution:** `src/pydantic_ai_integration/tool_decorator.py` registers tools into `MANAGED_TOOLS`. Requests run through `tool_sessionservice/service.py`, and public APIs live under `src/pydantic_api/routers/**`.
- **Persistence layer:** Firestore repositories and `src/persistence/firestore/context_persistence.py` capture casefiles, sessions, and audit logs. Dev mode defaults to mocked Google clients toggled in `coreservice.config`.

### Coding standards & reviews
- Follow PEP 8 with type hints; keep public docstrings concise and factual.
- Import order: stdlib → third-party → `src/...`.
- Services return typed envelopes from `src/pydantic_models/operations/**`; avoid raw dicts at service boundaries.
- Keep diffs surgical—limit formatting churn to the touched regions.
- Update documentation alongside behaviour changes to keep the narrative aligned.

### Tool engineering patterns
- Populate `classification`, `business_rules`, and policy sections in each YAML file so generated metadata stays consistent.
- `examples`, `error_scenarios`, and `test_scenarios` drive generated unit, integration, and API suites—maintain them to prevent skipped coverage.
- Composite tooling leans on `MDSContext` helpers (`plan_tool_chain`, `register_event`, `complete_chain`) and the chain executor under `src/pydantic_ai_integration/execution/`.

### Testing & quality assurance
| Command | Purpose | Notes |
| --- | --- | --- |
| `pytest tests/integration/test_tool_response_wrapping.py -q` | Regression guard for async execution & audit wrapping | Run before every PR |
| `pytest tests/unit -q` | Generated params/validation coverage | Requires regenerated artefacts |
| `pytest tests/integration -q` | Service-layer coverage with async context | Uses mock Google clients by default |
| `pytest tests/api -q` | FastAPI contract checks | Validates routers against the registry |

`pytest.ini` already configures asyncio defaults; reuse fixtures under `tests/fixtures/**` when authoring new tests.

### Environment & integration notes
- Firestore access outside GCP requires `GOOGLE_APPLICATION_CREDENTIALS`. Local mock toggles live in `ENABLE_MOCK_GMAIL` / `ENABLE_MOCK_DRIVE`.
- Solid Pod scripts under `scripts/` depend on `SOLID_*` env vars when `SOLID_ENABLED=true`.
- `MDSContext` can auto-persist; large collections are chunked transparently by `context_persistence.py` when a handler is registered.

## CI & infrastructure notes
- No automated pipeline is committed yet; when wiring one, run the same sequence used locally: `pip install -e ".[dev]"`, `python scripts/generate_tools.py`, `python scripts/import_generated_tools.py`, targeted pytest suites, then any deployment packaging.
- Cache the virtualenv or pip download directory to speed up CI—generation touches many files, so ensure artefacts are either regenerated in the pipeline or committed beforehand.
- Surface registry drift early by adding `python scripts/show_tools.py` (with `--validate-only` once added) before lengthy test jobs.
- Centralize environment variables in CI secrets (`GOOGLE_APPLICATION_CREDENTIALS`, `GOOGLE_CLOUD_PROJECT`, `SOLID_*`) and fail fast if required values are missing.

## Working with AI assistants
- Treat assistants as pair programmers: gather context, outline TODOs, then execute immediately after describing the plan.
- Prefer precise diffs (e.g., `apply_patch`) and avoid sweeping formatting changes.
- After YAML edits, regenerate artefacts, run at least one relevant suite, and report actual PASS/FAIL output.
- Keep responses concise and technical; flag blockers with proposed next steps rather than guessing outcomes.

## Reference documents
- `README.md` — system overview and onboarding.
- `HANDOVER.md` — end-to-end workflow checklist and governance notes.
- `config/tools/README.md` — tool catalogue layout and YAML contract.
- `src/pydantic_ai_integration/README.md` — runtime architecture deep dive.

Questions or updates? Open an issue or start a thread in your feature branch before diverging from these patterns.
