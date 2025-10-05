# Tool Definition Catalogue

All tools are defined as YAML files in this directory. The YAML is the **single source of truth** for generation, execution policies, and documentation (see the project-wide guidance in `INSTALL.md`, `README.md`, and `DEVELOPER_GUIDE.md`). Generated Python and test files can be safely regenerated at any time with `generate-tools`.

> **New to the repo?** Run through the clean-slate workflow in the root `README.md`/`INSTALL.md` first (clone → `pip install -e ".[dev]"` → `python scripts/generate_tools.py` → `python scripts/import_generated_tools.py`) so the generated packages exist before you edit YAML.

## Directory Layout (domain/subdomain)

```
tools/
├── automation/
│   └── pipelines/
│       ├── gmail_to_drive_pipeline.yaml
│       └── multi_echo_pipeline.yaml
├── communication/
│   └── email/
│       ├── gmail_get_message.yaml
│       ├── gmail_list_messages.yaml
│       ├── gmail_search_messages.yaml
│       └── gmail_send_message.yaml
├── utilities/
│   └── debugging/
│       ├── echo_chain_demo.yaml
│       └── echo_tool.yaml
└── workspace/
        └── google/
                ├── drive_list_files.yaml
                └── sheets_batch_get.yaml
```

- **Domain** controls the first folder level (communication, workspace, automation, utilities).
- **Subdomain** controls the second folder level (email, google, pipelines, debugging).
- File names use `{integration}_{action}_{subject}.yaml` so the generated code/tests follow the same hierarchy.

## YAML Contract

Each tool definition shares the same high-level shape:

```yaml
name: gmail_send_message
classification:
    domain: communication
    subdomain: email
    capability: create        # CRUD/verb
    complexity: atomic        # atomic | composite | pipeline
    maturity: stable          # experimental | beta | stable | deprecated
    integration_tier: external
parameters:                 # Strongly typed parameters → Pydantic model
business_rules:             # Enabled/auth/permission/timeouts
session_policies:           # Session lifecycle controls
casefile_policies:          # Casefile enforcement/audit
implementation:             # Simple/api_call/data_transform/composite
returns:                    # Response schema for documentation
audit_events:               # Success/failure + redaction policy
examples: []                # Happy-path test vectors
error_scenarios: []         # Validation + failure tests
test_scenarios: []          # Structured integration scenarios
metadata: {}                # Optional annotations surfaced in discovery APIs
documentation: {}           # Optional summary + changelog entries
```

Key sections map directly to runtime behaviour:

| Section | Purpose |
| --- | --- |
| `classification` | Drives folder naming, discovery filters, and tool registry metadata. |
| `parameters` | Generates the Pydantic params model and request validation. |
| `business_rules` | Enables/disables the tool, enforces auth and permission requirements, and sets execution timeouts. |
| `session_policies` & `casefile_policies` | Control when sessions/casefiles are required and how audit data is emitted. |
| `implementation` | Chooses the generator template (`api_call`, `data_transform`, `composite`, `simple`) and wires clients like `GmailClient`. |
| `returns` | Describes the response payload that populates the generated `ToolResponse`. |
| `audit_events`, `examples`, `error_scenarios`, `test_scenarios` | Feed generated unit/integration/API tests and audit configuration. |
| `metadata`, `documentation` | Surface human-friendly annotations in discovery responses and generated docs. |

## Workflow Recap

1. **Define or edit YAML** under the correct domain/subdomain.
2. **Regenerate** artefacts (`generate-tools`) — see `INSTALL.md` for command options and environment setup.
3. **Run tests** (`pytest` suites outlined in `INSTALL.md`) to validate the generated unit/integration/API scaffolding.
4. **Commit the YAML** plus any generated files that changed (per `DEVELOPER_GUIDE.md`).

Remember: YAML drives everything — never hand-edit `src/pydantic_ai_integration/tools/generated/**` or the generated tests; regenerate instead. The generator also refreshes compatibility shims and package `__init__` exports so manual edits can be dropped safely.