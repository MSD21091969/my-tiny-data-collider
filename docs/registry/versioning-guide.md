# Methods Registry Versioning Guide

**Version:** 1.0.0  
**Last Updated:** 2025-10-06

## Overview

This guide defines the versioning strategy for the service methods registry system, including:
- Version numbering rules (Semantic Versioning)
- Breaking vs. non-breaking changes
- Deprecation workflow
- Migration path requirements

## Semantic Versioning

The methods registry follows [Semantic Versioning 2.0.0](https://semver.org/):

```
MAJOR.MINOR.PATCH
```

### Version Components

#### MAJOR (e.g., 1.x.x → 2.x.x)
**Breaking changes that require code updates**

Examples:
- Renaming a method parameter
- Changing parameter type (string → int)
- Making optional parameter required
- Removing a method
- Changing response model structure
- Modifying required permissions
- Renaming a method

**Action Required:** Users must update calling code

#### MINOR (e.g., 1.1.x → 1.2.x)
**Backward-compatible additions**

Examples:
- Adding new method
- Adding optional parameter with default value
- Adding new classification field
- Adding new discovery API
- Enhancing metadata (description, examples)
- Adding new permission (non-required)

**Action Required:** None (users can adopt new features optionally)

#### PATCH (e.g., 1.1.1 → 1.1.2)
**Backward-compatible fixes**

Examples:
- Fixing typos in descriptions
- Correcting classification metadata
- Fixing documentation errors
- Improving validation error messages
- Bug fixes that don't change signatures

**Action Required:** None (transparent improvements)

---

## Change Classification Matrix

| Change Type | Method Signature | Request Model | Response Model | Classification | Version Impact |
|-------------|------------------|---------------|----------------|----------------|----------------|
| Add new method | N/A | N/A | N/A | N/A | MINOR |
| Remove method | ✓ | ✓ | ✓ | ✓ | MAJOR |
| Rename method | ✓ | - | - | - | MAJOR |
| Rename parameter | ✓ | ✓ | - | - | MAJOR |
| Add required param | ✓ | ✓ | - | - | MAJOR |
| Add optional param | ✓ | ✓ | - | - | MINOR |
| Change param type | ✓ | ✓ | - | - | MAJOR |
| Add response field | - | - | ✓ | - | MINOR |
| Remove response field | - | - | ✓ | - | MAJOR |
| Change response type | - | - | ✓ | - | MAJOR |
| Add required permission | - | - | - | - | MAJOR |
| Add optional permission | - | - | - | - | MINOR |
| Update description | - | - | - | - | PATCH |
| Update classification | - | - | - | ✓ | PATCH |
| Fix validation | - | ✓ | - | - | MINOR/PATCH* |

*PATCH if fixing incorrect validation, MINOR if adding new validation rules

---

## Deprecation Policy

### Step 1: Mark as Deprecated
Add to YAML:
```yaml
methods:
  - name: old_method_name
    deprecated: true
    deprecated_since: "1.5.0"
    deprecated_reason: "Replaced by new_method_name for better performance"
    replacement: "new_method_name"
    removal_version: "2.0.0"
```

### Step 2: Runtime Warning
The `@register_service_method` decorator automatically logs warnings:
```
DeprecationWarning: Method 'old_method_name' is deprecated since v1.5.0. 
Use 'new_method_name' instead. Will be removed in v2.0.0.
```

### Step 3: Documentation Update
Add to `METHODS_CHANGELOG.md`:
```markdown
### Deprecated
- `old_method_name`: Use `new_method_name` instead. Will be removed in v2.0.0.
```

### Step 4: Migration Period
- Deprecated methods remain functional for **at least 1 MAJOR version**
- Example: Deprecated in v1.5.0 → Removed in v2.0.0 (not v1.6.0)

### Step 5: Removal
Remove from `methods_inventory_v2.yaml` and update:
```markdown
### Removed
- `old_method_name`: Removed as planned. Use `new_method_name`.
```

---

## Version Workflow

### Making a Change

#### 1. Identify Change Type
Ask:
- Does this break existing code? → **MAJOR**
- Does this add new functionality? → **MINOR**
- Does this fix a bug/typo? → **PATCH**

#### 2. Update YAML
For **MAJOR/MINOR**:
```bash
# Copy current version
cp config/methods_inventory_v1.yaml config/methods_inventory_v2.yaml

# Update header
version: "2.0.0"
last_updated: "2025-10-15"
```

For **PATCH**:
```bash
# Edit in place
version: "1.0.1"
last_updated: "2025-10-15"
```

#### 3. Update CHANGELOG
Add to `docs/METHODS_CHANGELOG.md`:
```markdown
## [2.0.0] - 2025-10-15

### Changed
- **[BREAKING]** Renamed parameter `casefile_id` to `id` in all methods for consistency

### Migration Guide
Update all calls:
```python
# Before (v1.x)
response = service.get_casefile(casefile_id="123")

# After (v2.x)
response = service.get_casefile(id="123")
```
```

#### 4. Update Documentation
```bash
# Regenerate docs
python scripts/generate_method_docs.py
```

#### 5. Tag Release
```bash
# For MAJOR/MINOR
git tag -a v2.0.0 -m "Release v2.0.0: Unified parameter naming"
git push origin v2.0.0

# For PATCH (optional)
git tag -a v1.0.1 -m "Release v1.0.1: Fix description typos"
```

---

## YAML Version Header

Every `methods_inventory_vX.yaml` must include:

```yaml
version: "1.0.0"
last_updated: "2025-10-06"
description: "Service methods inventory with classification and metadata"
schema_version: "1.0"  # YAML structure version (separate from content version)
changelog: "docs/METHODS_CHANGELOG.md"

# Versioning metadata
compatibility:
  minimum_registry_version: "1.0.0"  # Min version of method_registry.py
  minimum_decorator_version: "1.0.0"  # Min version of method_decorator.py

# Deprecation notices (if any)
deprecations: []
# - method_name: "old_method"
#   deprecated_since: "1.5.0"
#   removal_version: "2.0.0"
#   replacement: "new_method"

services:
  - name: CasefileService
    # ... methods
```

---

## Migration Path Template

For MAJOR version upgrades, include this section in `METHODS_CHANGELOG.md`:

```markdown
## Migration Guide: v1.x → v2.0

### Breaking Changes Summary
1. **Unified Parameter Naming**
   - All `casefile_id` parameters renamed to `id`
   - Affects: 13 CasefileService methods

2. **Permission Model Update**
   - `required_permissions` now uses format `domain:resource:action`
   - Old: `["casefiles:read"]`
   - New: `["workspace:casefile:read"]`

### Step-by-Step Migration

#### Step 1: Update Method Calls
```python
# Before (v1.x)
service.get_casefile(casefile_id="123")
service.grant_permission(casefile_id="123", user_id="456", permission="read")

# After (v2.0)
service.get_casefile(id="123")
service.grant_permission(id="123", user_id="456", permission="read")
```

#### Step 2: Update Permission Checks
```python
# Before (v1.x)
required_permissions = ["casefiles:read", "casefiles:write"]

# After (v2.0)
required_permissions = ["workspace:casefile:read", "workspace:casefile:write"]
```

#### Step 3: Update Tests
- Run test suite against v2.0
- Update assertions for new parameter names
- Update mock data for new permission format

#### Step 4: Update Documentation
- Review API docs for parameter changes
- Update integration examples
- Update client SDKs (if any)

### Compatibility Notes
- v1.x and v2.0 cannot coexist in same codebase
- Recommend upgrading all services simultaneously
- Estimated migration time: 2-4 hours for typical codebase
```

---

## Discovery API Versioning

The registry discovery APIs follow the same versioning:

| API Function | v1.0.0 | v2.0.0 Notes |
|--------------|--------|--------------|
| `get_registered_methods()` | ✓ | Stable |
| `get_methods_by_domain()` | ✓ | Stable |
| `get_methods_by_service()` | ✓ | Stable |
| `get_methods_by_capability()` | ✓ | Stable |
| `get_method()` | ✓ | Stable |
| `get_classification_summary()` | ✓ | May add fields |
| `validate_method_call()` | - | New in v2.0 |

---

## Best Practices

### For Method Owners
1. **Think twice before breaking changes** - Can you make it backward-compatible?
2. **Document migrations thoroughly** - Include code examples
3. **Announce in advance** - Deprecate → Wait → Remove
4. **Version YAML files** - Keep `v1.yaml`, `v2.yaml` separate for MAJOR changes
5. **Test migrations** - Verify upgrade path works

### For Method Users
1. **Pin versions** - Specify which YAML version you're using
2. **Monitor deprecations** - Watch for warnings in logs
3. **Test before upgrading** - Run test suite against new version
4. **Review changelogs** - Read before upgrading MAJOR versions
5. **Plan migration windows** - Don't upgrade MAJOR versions without testing

---

## Tooling Support

### Check Current Version
```python
from pydantic_ai_integration.method_decorator import get_registry_version

version = get_registry_version()  # Returns "1.0.0"
```

### Validate Compatibility
```python
from pydantic_ai_integration.method_registry import validate_yaml_compatibility

# Check if YAML is compatible with current registry code
is_compatible = validate_yaml_compatibility("config/methods_inventory_v2.yaml")
```

### List Deprecated Methods
```python
from pydantic_ai_integration.method_registry import get_deprecated_methods

deprecated = get_deprecated_methods()
# Returns: [{"name": "old_method", "replacement": "new_method", "removal_version": "2.0.0"}]
```

---

## Rollback Strategy

If a release has critical issues:

### PATCH/MINOR Issues
1. Create hotfix with PATCH version (v1.1.1)
2. Update CHANGELOG with `[Fixed]` section
3. Tag and release immediately

### MAJOR Issues
1. **Do not rollback MAJOR versions** - breaks compatibility
2. Instead: Create v2.0.1 with fixes
3. If critical: Create v2.1.0 with backward-compatibility layer
4. Document workarounds in CHANGELOG

---

## Questions?

- **Registry Code**: `src/pydantic_ai_integration/method_registry.py`
- **Changelog**: [CHANGELOG.md](./CHANGELOG.md)
- **Release Process**: [release-process.md](./release-process.md)
- **Issues**: GitHub issues with label `method-registry`
- **Discussions**: GitHub Discussions for versioning proposals
