# Version Release Process

**Guide for creating new releases of the methods registry**

## Quick Reference

| Release Type | Version Change | When to Use | Tag Required |
|--------------|----------------|-------------|--------------|
| PATCH | 1.0.0 → 1.0.1 | Bug fixes, typos, metadata corrections | Optional |
| MINOR | 1.0.0 → 1.1.0 | New methods, optional parameters, enhancements | Recommended |
| MAJOR | 1.0.0 → 2.0.0 | Breaking changes, signature modifications | **Required** |

---

## Release Checklist

### PATCH Release (1.0.x → 1.0.y)

**What qualifies:**
- ✅ Fix typos in descriptions
- ✅ Correct classification metadata
- ✅ Update documentation
- ✅ Fix validation error messages
- ✅ Improve code comments

**Steps:**
1. [ ] Make fixes in `config/methods_inventory_v1.yaml`
2. [ ] Update version: `version: "1.0.1"`
3. [ ] Update `updated_at` field
4. [ ] Add entry to `docs/METHODS_CHANGELOG.md` under `[1.0.1]`
5. [ ] Regenerate docs: `python scripts/generate_method_docs.py`
6. [ ] Commit changes
7. [ ] (Optional) Tag: `git tag v1.0.1`

**Estimated time:** 15 minutes

---

### MINOR Release (1.x.0 → 1.y.0)

**What qualifies:**
- ✅ Add new method
- ✅ Add optional parameter to existing method
- ✅ Add new classification field
- ✅ Add new discovery API
- ✅ Enhance metadata (non-breaking)

**Steps:**
1. [ ] Copy YAML: `cp config/methods_inventory_v1.yaml config/methods_inventory_v1.1.yaml`
2. [ ] Update version in new file: `version: "1.1.0"`
3. [ ] Make changes (add methods, parameters, etc.)
4. [ ] Update `updated_at` field
5. [ ] Add entry to `docs/METHODS_CHANGELOG.md` under `[1.1.0]`:
   ```markdown
   ## [1.1.0] - YYYY-MM-DD
   
   ### Added
   - New method: `archive_casefile` for soft delete operations
   - Optional parameter `include_archived` in `list_casefiles` method
   ```
6. [ ] Regenerate docs: `python scripts/generate_method_docs.py`
7. [ ] Run tests: `pytest tests/test_method_registry.py`
8. [ ] Commit changes
9. [ ] Tag release: `git tag -a v1.1.0 -m "Release v1.1.0: Add archive functionality"`
10. [ ] Push tag: `git push origin v1.1.0`

**Estimated time:** 1-2 hours

---

### MAJOR Release (x.0.0 → y.0.0)

**What qualifies:**
- ❌ Rename method
- ❌ Rename parameter
- ❌ Change parameter type
- ❌ Make optional parameter required
- ❌ Remove method
- ❌ Change response structure
- ❌ Modify required permissions

**Steps:**
1. [ ] **Plan migration path** - Document how users will upgrade
2. [ ] Copy YAML: `cp config/methods_inventory_v1.yaml config/methods_inventory_v2.yaml`
3. [ ] Update version in new file: `version: "2.0.0"`
4. [ ] Update `schema_version` if structure changed: `schema_version: "2.0"`
5. [ ] Make breaking changes
6. [ ] Update `updated_at` field
7. [ ] Add detailed entry to `docs/METHODS_CHANGELOG.md` under `[2.0.0]`:
   ```markdown
   ## [2.0.0] - YYYY-MM-DD
   
   ### Changed
   - **[BREAKING]** Renamed parameter `casefile_id` to `id` in all CasefileService methods
   - **[BREAKING]** Changed permission format from `service:action` to `domain:resource:action`
   
   ### Removed
   - **[BREAKING]** Removed deprecated method `old_create_casefile` (use `create_casefile` instead)
   
   ### Migration Guide
   See section below for step-by-step upgrade instructions.
   ```
8. [ ] Write migration guide in CHANGELOG
9. [ ] Update registry code if needed (`method_definition.py`, `method_registry.py`)
10. [ ] Regenerate docs: `python scripts/generate_method_docs.py`
11. [ ] Run full test suite: `pytest`
12. [ ] Create migration test: `tests/test_v1_to_v2_migration.py`
13. [ ] Commit changes
14. [ ] **Tag release with annotation**: `git tag -a v2.0.0 -m "Release v2.0.0: Unified parameter naming"`
15. [ ] Push tag: `git push origin v2.0.0`
16. [ ] Create GitHub release with migration guide

**Estimated time:** 4-8 hours (includes testing and documentation)

---

## Deprecation Workflow

### Step 1: Mark Method as Deprecated (MINOR release)

In `methods_inventory_v1.5.yaml`:
```yaml
methods:
  - name: old_create_casefile
    description: "Create casefile (DEPRECATED: Use create_casefile instead)"
    deprecated: true
    deprecated_since: "1.5.0"
    deprecated_reason: "Replaced by create_casefile with improved validation"
    replacement: "create_casefile"
    removal_version: "2.0.0"
```

Add to CHANGELOG:
```markdown
## [1.5.0] - 2025-11-01

### Deprecated
- `old_create_casefile`: Use `create_casefile` instead. Will be removed in v2.0.0.
  - **Reason**: Improved validation and error handling
  - **Migration**: Replace all calls to `old_create_casefile` with `create_casefile`
```

### Step 2: Wait Period (at least 1 MAJOR version)

- Keep deprecated method functional in v1.x
- Log warnings when method is called
- Update documentation to show deprecation notice
- Communicate to users via:
  - Release notes
  - In-code warnings
  - Documentation banners

### Step 3: Remove Method (MAJOR release)

In `methods_inventory_v2.0.yaml`:
```yaml
# Remove old_create_casefile method entirely
```

Add to CHANGELOG:
```markdown
## [2.0.0] - 2025-12-01

### Removed
- **[BREAKING]** `old_create_casefile`: Removed as planned. Use `create_casefile`.
  - Deprecated since: v1.5.0
  - Migration guide: See v1.5.0 release notes
```

---

## Git Tagging Commands

### List existing tags
```bash
git tag -l "v*"
```

### Create annotated tag (RECOMMENDED)
```bash
# MINOR/MAJOR releases
git tag -a v1.1.0 -m "Release v1.1.0: Add archive functionality"

# PATCH releases
git tag -a v1.0.1 -m "Fix: Correct classification metadata"
```

### Create lightweight tag (NOT RECOMMENDED)
```bash
git tag v1.0.1
```

### Push tag to remote
```bash
# Single tag
git push origin v1.1.0

# All tags
git push origin --tags
```

### View tag details
```bash
git show v1.1.0
```

### Delete tag (if mistake)
```bash
# Delete local
git tag -d v1.0.1

# Delete remote
git push origin :refs/tags/v1.0.1
```

---

## Automated Release Script

See `scripts/release_version.py` for automated workflow:

```bash
# PATCH release
python scripts/release_version.py --type patch

# MINOR release
python scripts/release_version.py --type minor --changelog "Add archive functionality"

# MAJOR release (requires manual migration guide)
python scripts/release_version.py --type major --changelog "Unified parameter naming"
```

Script will:
1. Validate current state (no uncommitted changes)
2. Update version in YAML
3. Update CHANGELOG template
4. Regenerate documentation
5. Commit changes
6. Create git tag
7. Print next steps (push to remote, create GitHub release)

---

## GitHub Release Creation

After pushing tag:

1. Go to: `https://github.com/MSD21091969/my-tiny-data-collider/releases/new`
2. Select tag: `v1.1.0`
3. Title: `v1.1.0: Add archive functionality`
4. Description: Copy from CHANGELOG
5. Attach files (optional): None needed
6. Mark as pre-release: Only for alpha/beta
7. Click "Publish release"

---

## Version Compatibility Matrix

| YAML Version | Registry Code Version | Compatible | Notes |
|--------------|----------------------|------------|-------|
| v1.0.0 | v1.0.0 | ✅ | Baseline |
| v1.1.0 | v1.0.0 | ✅ | Backward compatible |
| v1.0.0 | v1.1.0 | ✅ | Forward compatible |
| v2.0.0 | v1.0.0 | ❌ | Breaking changes |
| v1.0.0 | v2.0.0 | ⚠️ | May work with warnings |

**Check compatibility:**
```python
from pydantic_ai_integration.method_registry import validate_yaml_compatibility

result = validate_yaml_compatibility("config/methods_inventory_v2.yaml")
print(result)
# {
#   "compatible": True,
#   "issues": [],
#   "yaml_version": "2.0.0",
#   "registry_version": "2.0.0"
# }
```

---

## Rollback Strategy

### If PATCH/MINOR release has issues:
```bash
# Revert commit
git revert HEAD

# Or delete tag and re-release
git tag -d v1.1.0
git push origin :refs/tags/v1.1.0

# Make fixes
# Create new tag with PATCH bump
git tag -a v1.1.1 -m "Fix: Correct version 1.1.0 issues"
```

### If MAJOR release has issues:
**DO NOT ROLLBACK** - this breaks compatibility for users who upgraded.

Instead:
1. Create hotfix in v2.0.1
2. Or add backward compatibility layer in v2.1.0
3. Document workarounds in CHANGELOG
4. Communicate to all users

---

## Communication Checklist

After release:

- [ ] Push tag to GitHub
- [ ] Create GitHub release with notes
- [ ] Update main README.md if needed
- [ ] Post in team chat/Slack
- [ ] Update project documentation
- [ ] Send email to stakeholders (MAJOR only)
- [ ] Update API documentation site (if exists)

---

## Questions?

- **Process issues**: See [versioning-guide.md](./versioning-guide.md)
- **Technical issues**: Check `src/pydantic_ai_integration/method_registry.py`
- **Changelog format**: See [CHANGELOG.md](./CHANGELOG.md)
