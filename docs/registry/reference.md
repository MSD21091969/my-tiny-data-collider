# Methods Registry Reference

**Version**: 1.0.0 | **Date**: 2025-10-06

Quick reference for classification schema, model coverage, and method statistics.

---

## Classification Schema

6-field taxonomy for method metadata:

```yaml
classification:
  domain:           [workspace, communication, automation]
  subdomain:        casefile | gmail | tool_session | chat_session | google_drive | google_sheets | casefile_acl | google_workspace | chat_processing | tool_execution
  capability:       [create, read, update, delete, process, search]
  complexity:       [atomic, composite, pipeline]
  maturity:         [stable, beta, experimental, deprecated]
  integration_tier: [internal, external, hybrid]
```

### Field Definitions

**domain**: High-level functional area
- `workspace` - Casefiles, Google Drive/Sheets (15 methods)
- `communication` - Gmail, chat, messaging (11 methods)
- `automation` - Tool execution, workflows (4 methods)

**subdomain**: Specific area within domain
- Examples: `casefile`, `gmail`, `tool_session`, `chat_session`, `google_drive`, `google_sheets`, `casefile_acl`

**capability**: Operation type
- `create` - Creates resources (5 methods)
- `read` - Retrieves data (11 methods)
- `update` - Modifies existing (9 methods)
- `delete` - Removes resources (2 methods)
- `process` - Transforms/analyzes (3 methods)
- `search` - Queries/filters (4 methods)

**complexity**: Composition pattern
- `atomic` - Single operation (24 methods)
- `composite` - Multiple operations (5 methods)
- `pipeline` - Multi-step workflow (2 methods)

**maturity**: Lifecycle stage
- `stable` - Production ready (23 methods)
- `beta` - Testing, may change (7 methods)
- `experimental` - Early dev, API unstable
- `deprecated` - Being removed (use `deprecated_since` field)

**integration_tier**: External dependencies
- `internal` - Internal services only (18 methods)
- `external` - Requires external APIs (6 methods)
- `hybrid` - Internal + external (6 methods)

---

## Method Statistics

```
Total Methods:    30
├─ Domain:        workspace(15) | communication(11) | automation(4)
├─ Capability:    read(11) | update(9) | create(5) | search(4) | process(3) | delete(2)
├─ Complexity:    atomic(24) | composite(5) | pipeline(2)
├─ Integration:   internal(18) | external(6) | hybrid(6)
├─ Maturity:      stable(23) | beta(7)
└─ Model Coverage: 83% (25/30)
```

### Service Breakdown

| Service | Method Count | Domains |
|---------|--------------|---------|
| CasefileService | 13 | workspace (casefile, casefile_acl, google_workspace) |
| ToolSessionService | 1 | automation (tool_execution) |
| CommunicationService | 6 | communication (chat_session, chat_processing) |
| GmailClient | 4 | communication (gmail) |
| DriveClient | 1 | workspace (google_drive) |
| SheetsClient | 1 | workspace (google_sheets) |

---

## Model Coverage

**83% coverage** (25/30 methods). All models inherit from `BaseRequest[T]` / `BaseResponse[T]`.

### Coverage by File

| File | Methods | Coverage | Missing |
|------|---------|----------|---------|
| casefile_ops.py | 13 | 8/13 (62%) | list_permissions, check_permission, store_gmail_messages, store_drive_files, store_sheet_data |
| tool_session_ops.py | 5 | 5/5 (100%) | - |
| chat_session_ops.py | 4 | 4/4 (100%) | - |
| gmail_ops.py | 4 | 4/4 (100%) | - |
| drive_ops.py | 1 | 1/1 (100%) | - |
| sheets_ops.py | 1 | 1/1 (100%) | - |
| tool_execution_ops.py | 1 | 1/1 (100%) | - |

### Missing Models (5)

**CasefileService ACL (2)**:
- `list_permissions` - Get all permissions for casefile
- `check_permission` - Verify user permission

**CasefileService Workspace Sync (3)**:
- `store_gmail_messages` - Sync Gmail to casefile (beta/hybrid)
- `store_drive_files` - Sync Drive files to casefile (beta/hybrid)
- `store_sheet_data` - Sync Sheets data to casefile (beta/hybrid)

---

## Naming Conventions

**Method Names**: `{domain}.{subdomain}.{capability}_{descriptive_name}`

Examples:
- `workspace.casefile.create_casefile`
- `communication.gmail.send_email`
- `automation.tool_execution.process_tool_request`

**Model Names**: `{Operation}{Entity}Request/Response`

Examples:
- `CreateCasefileRequest` / `CreateCasefileResponse`
- `SendEmailRequest` / `SendEmailResponse`
- `ToolRequest` / `ToolResponse`

---

## Quick Links

**Full API Documentation**: See [../methods/README.md](../methods/README.md)

**Registry System**:
- [CHANGELOG.md](./CHANGELOG.md) - Version history
- [versioning-guide.md](./versioning-guide.md) - Semver rules
- [release-process.md](./release-process.md) - Release workflows

**Source Files**:
- `config/methods_inventory_v1.yaml` - Method metadata (YAML)
- `src/pydantic_ai_integration/method_definition.py` - Data structures
- `src/pydantic_ai_integration/method_registry.py` - MANAGED_METHODS registry
- `src/pydantic_ai_integration/method_decorator.py` - @register_service_method
