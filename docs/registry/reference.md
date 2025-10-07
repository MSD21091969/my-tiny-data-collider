# Methods Registry Reference

**Version**: 1.0.0 | **Date**: 2025-10-07

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

## Versioning & Release Process

### Semantic Versioning

**MAJOR.MINOR.PATCH** - Breaking.Non-breaking.Fixes

#### When to Increment
- **MAJOR** (2.0.0): Breaking changes (rename parameters, change types, remove methods)
- **MINOR** (1.1.0): Non-breaking additions (new methods, optional parameters)
- **PATCH** (1.0.1): Non-breaking fixes (typos, metadata corrections)

#### Breaking Change Examples
- ❌ Rename method parameter
- ❌ Change parameter type (string → int)
- ❌ Make optional parameter required
- ❌ Remove method or response field
- ❌ Change required permissions

#### Non-Breaking Examples
- ✅ Add new optional parameter
- ✅ Add new method
- ✅ Fix description typos
- ✅ Update classification metadata
- ✅ Add new permission (non-required)

### Release Workflow

#### PATCH Release (15 min)
```bash
# Edit config/methods_inventory_v1.yaml
# Update version: "1.0.1"
# Add CHANGELOG entry
python scripts/generate_method_docs.py
git commit -m "Release v1.0.1: Fix description typos"
git tag v1.0.1  # Optional
```

#### MINOR Release (1-2 hrs)
```bash
# Copy config/methods_inventory_v1.yaml → v1.1.yaml
# Add new methods/parameters
# Update version: "1.1.0"
# Add detailed CHANGELOG entry
python scripts/generate_method_docs.py
pytest tests/test_method_registry.py
git commit -m "Release v1.1.0: Add archive functionality"
git tag -a v1.1.0 -m "Release v1.1.0: Add archive functionality"
git push origin v1.1.0
```

#### MAJOR Release (4-8 hrs)
```bash
# Copy config/methods_inventory_v1.yaml → v2.0.yaml
# Make breaking changes with migration guide
# Update version: "2.0.0"
# Add comprehensive CHANGELOG with migration guide
python scripts/generate_method_docs.py
pytest  # Full test suite
git commit -m "Release v2.0.0: Unified parameter naming"
git tag -a v2.0.0 -m "Release v2.0.0: Unified parameter naming"
git push origin v2.0.0
# Create GitHub release with migration guide
```

### Deprecation Policy

1. **Mark deprecated** in YAML: `deprecated: true`, `deprecated_since`, `replacement`
2. **Maintain compatibility** for minimum 1 MAJOR version
3. **Runtime warnings** when deprecated methods called
4. **Remove in next MAJOR** version with migration guide

### Automated Release Script

```bash
# Use automated script for standard releases
python scripts/release_version.py --type minor --changelog "Add archive functionality"
```

---

## Method Statistics

```
Total Methods:    26
├─ Domain:        workspace(15) | communication(10) | automation(1)
├─ Capability:    read(10) | update(8) | create(5) | search(2) | delete(2) | process(1)
├─ Complexity:    atomic(24) | composite(2)
├─ Integration:   internal(14) | external(6) | hybrid(6)
├─ Maturity:      stable(23) | beta(3)
└─ Model Coverage: 100% (26/26) ✓
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

**100% coverage** (26/26 methods) ✓ All models inherit from `BaseRequest[T]` / `BaseResponse[T]`.

### Coverage by File

| File | Methods | Coverage | Notes |
|------|---------|----------|-------|
| casefile_ops.py | 13 | 13/13 (100%) | All CRUD, ACL, and workspace sync DTOs present |
| tool_session_ops.py | 5 | 5/5 (100%) | - |
| chat_session_ops.py | 4 | 4/4 (100%) | - |
| gmail_ops.py | 4 | 4/4 (100%) | - |
| drive_ops.py | 1 | 1/1 (100%) | - |
| sheets_ops.py | 1 | 1/1 (100%) | - |

**Verified**: 2025-10-06 - All 26 methods have complete Request/Response DTO pairs.

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
- [CHANGELOG.md](./CHANGELOG.md) - Version history, releases, and migration guides

**Source Files**:
- `config/methods_inventory_v1.yaml` - Method metadata (YAML)
- `src/pydantic_ai_integration/method_definition.py` - Data structures
- `src/pydantic_ai_integration/method_registry.py` - MANAGED_METHODS registry
- `src/pydantic_ai_integration/method_decorator.py` - @register_service_method
