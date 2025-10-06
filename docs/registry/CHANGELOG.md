# Methods Registry Changelog

All notable changes to the service methods registry will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Versioning Rules

### For Methods (`methods_inventory_v*.yaml`)
- **MAJOR** (v2.0.0): Breaking changes to method signatures (rename parameters, change required fields, modify return types)
- **MINOR** (v1.1.0): Non-breaking additions (new methods, new optional parameters, enhanced metadata)
- **PATCH** (v1.0.1): Non-breaking fixes (description updates, classification refinements, metadata corrections)

### For Method Registry Code (`method_definition.py`, `method_registry.py`, `method_decorator.py`)
- **MAJOR**: Breaking API changes (rename registry functions, change decorator signature, modify data structures)
- **MINOR**: New features (new discovery APIs, new validation rules, enhanced metadata)
- **PATCH**: Bug fixes (error handling, edge cases, documentation)

### Deprecation Policy
1. Methods marked `deprecated: true` in YAML will trigger warnings when called
2. Deprecated methods remain functional for at least **1 MAJOR version**
3. Migration path must be documented in deprecation notice
4. Deprecated methods removed in next MAJOR version

### Breaking Change Examples
- ❌ Renaming a method parameter
- ❌ Changing a parameter from optional to required
- ❌ Modifying response model structure (removing fields, changing types)
- ❌ Renaming a method
- ❌ Changing required permissions

### Non-Breaking Change Examples
- ✅ Adding new optional parameter with default value
- ✅ Adding new method
- ✅ Enhancing description or metadata
- ✅ Adding new permission (in addition to existing)
- ✅ Improving validation rules (stricter input checks)

---

## [1.0.0] - 2025-10-06

### Added
- **Initial baseline release** of methods registry system
- 26 methods across 6 services:
  - **CasefileService** (13 methods): CRUD operations, ACL management, Google Workspace integration
  - **ToolSessionService** (1 method): Tool execution tracking
  - **CommunicationService** (6 methods): Chat session and request processing
  - **GmailClient** (4 methods): Gmail operations (list, send, search, get messages)
  - **DriveClient** (1 method): Drive file listing
  - **SheetsClient** (1 method): Batch data retrieval
- Classification taxonomy with 6 fields: domain, subdomain, capability, complexity, maturity, integration_tier
- `MANAGED_METHODS` registry parallel to `MANAGED_TOOLS`
- `@register_service_method` decorator for runtime registration
- 13 discovery APIs: `get_registered_methods()`, `get_methods_by_domain()`, `get_methods_by_service()`, etc.
- Comprehensive documentation: 26 method pages + 6 service pages + 3 domain pages + 1 index (36 files total)
- `methods_inventory_v1.yaml` (757 lines) with complete method specifications

### Service Breakdown
#### CasefileService (13 methods)
- **Create**: `create_casefile`
- **Read**: `get_casefile`, `list_casefiles`, `check_permission`, `list_permissions`
- **Update**: `update_casefile`, `add_session_to_casefile`, `grant_permission`, `store_gmail_messages`, `store_drive_files`, `store_sheet_data`
- **Delete**: `delete_casefile`, `revoke_permission`

#### ToolSessionService (1 method)
- **Process**: `process_tool_request`

#### CommunicationService (6 methods)
- **Create**: `create_session`
- **Read**: `get_session`, `list_sessions`
- **Update**: `close_session`
- **Process**: `process_chat_request`, `_ensure_tool_session` (private)

#### GmailClient (4 methods)
- **Read**: `get_message`
- **Search**: `list_messages`, `search_messages`
- **Update**: `send_message`

#### DriveClient (1 method)
- **Search**: `list_files`

#### SheetsClient (1 method)
- **Read**: `batch_get`

### Classification Statistics
- **By Domain**: Workspace (15), Communication (10), Automation (1)
- **By Capability**: Read (8), Update (7), Create (3), Search (3), Process (3), Delete (2)
- **By Maturity**: Stable (17), Beta (9)
- **By Integration Tier**: Internal (15), Hybrid (5), External (6)

### Documentation
- Created `docs/methods/` with comprehensive API reference
- Generated markdown pages for all methods with:
  - Classification metadata
  - Request/Response schemas
  - Parameter tables
  - Business rules
  - Usage examples
  - Related methods
- Service-specific pages grouped by capability
- Domain overview pages with subdomain organization

---

## [Unreleased]

### Planned for v1.1.0
- [ ] Add `list_tool_sessions` method to ToolSessionService
- [ ] Add `update_session` method to CommunicationService
- [ ] Add batch operations: `batch_create_casefiles`, `batch_update_casefiles`
- [ ] Add `archive_casefile` method (soft delete)
- [ ] Add pagination metadata to list responses
- [ ] Add rate limiting metadata to external API methods

### Planned for v2.0.0
- [ ] Migrate to unified permission model (breaking: changes `required_permissions` format)
- [ ] Standardize error codes across all methods (breaking: changes response error structure)
- [ ] Consolidate Google Workspace methods into unified `WorkspaceService` (breaking: changes service_name)

---

## Migration Guides

### Upgrading from v0.x to v1.0.0
Not applicable - this is the initial baseline release.

### Future: v1.x to v2.0.0
Migration guide will be added when v2.0.0 is planned.

---

## Notes

- **Registry Location**: `src/pydantic_ai_integration/method_registry.py`
- **Inventory YAML**: `config/methods_inventory_v1.yaml`
- **Documentation**: `docs/methods/` (API reference), `docs/registry/` (system docs)
- **Versioning Guide**: [versioning-guide.md](./versioning-guide.md)
- **Release Process**: [release-process.md](./release-process.md)
- **Change Requests**: Submit via GitHub issues with label `method-registry`
