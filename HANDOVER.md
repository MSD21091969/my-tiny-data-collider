# Dev Branch Handover — Workflow Focus

## Snapshot
- Branch: `develop`
- Date: 5 Oct 2025
- Scope: Align the repository around the regenerated-tool workflow, document required test runs, and tighten YAML/tooling governance.

---

## 1. End-to-End Workflow (clean slate → green tests)

1. **Bootstrap environment**
   ```powershell
   git clone -b develop https://github.com/MSD21091969/my-tiny-data-collider.git
   cd my-tiny-data-collider
   python -m venv venv
   .\venv\Scripts\activate
   pip install -e ".[dev]"
   ```
2. **Regenerate artefacts from YAML**
   ```powershell
   python scripts/generate_tools.py
   ```
3. **Register generated modules for the current shell**
   ```powershell
   python scripts/import_generated_tools.py
   python scripts/show_tools.py   # Optional: inspect registry + params
   ```
4. **Verify core suites**
   ```powershell
   pytest tests/integration/test_tool_response_wrapping.py -q
   pytest tests/unit -q
   pytest tests/api -q
   ```
5. **Iterate on YAML → regenerate → re-run tests** (repeat as specs change).

Keep these commands in sync with `INSTALL.md` and the root `README.md`; they are the canonical workflow for every collaborator.

---

## 2. Repository Hygiene & Regeneration Rules

- Generated folders (`src/pydantic_ai_integration/tools/generated/**` and `tests/{unit,integration,api}/**`) are **disposable**. Never hand-edit them—update YAML, regenerate, and commit the artefacts alongside their source YAML.
- `scripts/import_generated_tools.py` should be run in any shell that needs live tool definitions (CI, local scripts, notebooks). It surfaces syntax/import issues quickly—treat failures as blockers before running longer suites.
- `scripts/show_tools.py` offers a quick audit of tool metadata/parameters; run it before handoff to ensure registry parity with YAML expectations.
- Keep the repo lean: delete orphaned generated modules when YAML definitions are removed or renamed, then regenerate. Empty directories are acceptable; the generator recreates them deterministically.

---

## 3. YAML Governance & Versioning

- **Single source of truth:** Every behavioural change originates in `config/tools/**`. Do not diverge from this contract.
- **Version identifiers:** Populate `version`, `maturity`, and `integration_tier` in each YAML file. Bump `version` when behaviour or contract changes (including parameter schema tweaks).
- **Metadata fields:** Ensure `yaml_relative_path` and `generated_module_import` remain accurate when moving files; update them manually if git renames do not trigger generation.
- **Changelog discipline:** Use the `documentation` block (summary/changelog) inside YAML for auditability. Regeneration propagates these notes into generated docstrings and discovery payloads.
- **Storage:** Commit YAML alongside regenerated artefacts in the same changeset. If YAML is moved, delete the old generated outputs prior to regeneration to prevent zombie modules.

---

## 4. Classification System Health Check

- Domains currently shipping: `automation`, `communication`, `utilities`, `workspace`. Subdomains must remain two levels deep (`domain/subdomain`).
- Run `python scripts/generate_tools.py --validate-only` (flag available via ToolFactory CLI) before committing reclassified tools; this catches mismatched folders or typos.
- When introducing a new domain/subdomain, update:
  - `config/tools/README.md` directory map.
  - Downstream documentation (`src/pydantic_ai_integration/README.md`, `INSTALL.md`) if the classification affects onboarding.
  - Any discovery filters in services/routes relying on enumerated domains.
- For composites/pipelines, confirm the `implementation.type` (`composite`) aligns with the chain executor’s capabilities and that referenced step tools exist in the registry post-regeneration.

---

## 5. Testing & Validation Sources

| Command | Purpose | Notes |
| --- | --- | --- |
| `python scripts/import_generated_tools.py` | Syntax/import smoke test | Fails fast on generator regressions; run before pytest. |
| `python scripts/show_tools.py` | Inspect registered tools | Confirms MANAGED_TOOLS metadata matches YAML. |
| `pytest tests/integration/test_tool_response_wrapping.py -q` | Regression on async execution/audit wrapping | Should pass on every change; guards decorator/service contract. |
| `pytest tests/unit -q` | Generated unit tests per tool | Requires regenerated outputs; watch for skipped tests if YAML missing `examples`. |
| `pytest tests/api -q` | FastAPI surface sanity | Validates router contracts vs. generated payloads. |

Record test output (at least the integration regression) in PR descriptions or release notes so consumers know the environment is stable.

---

## 6. Workflow Improvements in Progress / To Do

1. **Generator + template versioning**
   - Tag template releases or embed a `generator_version` field in YAML to detect mismatches between local scripts and generated code.
   - Add a `--lock` mode in `generate_tools.py` to write the generator/template commit hash for reproducibility.

2. **Classification validation tooling**
   - Provide a CLI utility that lists domains/subdomains with counts and highlights orphaned generated modules.
   - Integrate validation into CI (failing if classifications drift from documented directories).

3. **YAML linting**
   - Adopt a schema-based validator (e.g., `pykwalify` or `jsonschema`) to enforce required fields, version increments, and description presence before regeneration.

4. **Test matrix automation**
   - Extend CI to run `python scripts/import_generated_tools.py` and `python scripts/show_tools.py` before pytest to capture registry drift early.

---

## 7. Next Steps for Maintainers

1. Enforce the clean-slate workflow for all contributors (consider pre-commit hooks or project templates).
2. Implement YAML schema validation + generator version stamping to prevent silent drift.
3. Schedule regular audits of classifications and prune legacy YAML definitions to keep generated outputs minimal.
4. Expand the testing table above into a CI pipeline (GitHub Actions/Azure DevOps) with cached virtualenv to keep runtimes acceptable.
5. Document upgrade paths for external integrations (Google Workspace API changes) directly in the relevant YAML `documentation` blocks and README sections.

---

## Appendix: Key Artefacts & Ownership

| Area | Primary File(s) | Notes |
| --- | --- | --- |
| Workflow docs | `README.md`, `INSTALL.md`, `WORKFLOW_GUIDE.md` | Stay synchronized; update together. |
| Tool source of truth | `config/tools/**.yaml` | Version bump and classification tracked here. |
| Tool generation | `scripts/generate_tools.py`, `src/pydantic_ai_integration/tools/factory/**` | Keep templates pinned; document changes. |
| Registry helpers | `scripts/import_generated_tools.py`, `scripts/show_tools.py` | Lightweight diagnostics; extend as workflow evolves. |
| Testing harness | `pytest.ini`, `tests/**` | Generated tests depend on YAML `examples`/`test_scenarios`. |

This handover should equip maintainers to reproduce the system from scratch, keep YAML governance tight, and sustain confidence via consistent testing.
