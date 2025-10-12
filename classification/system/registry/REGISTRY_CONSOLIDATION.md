# Registry Consolidation Guide

**Tags:** `registry` `validation` `yaml` `ci-cd` `maintenance`

## Overview

The Registry Consolidation project unifies method and tool registration into a cohesive, validated, and maintainable system. This guide covers the architecture, usage patterns, validation modes, troubleshooting, and maintenance workflows.

## Table of Contents

- [Architecture](#architecture)
- [Quick Start](#quick-start)
- [Validation Modes](#validation-modes)
- [Environment Variables](#environment-variables)
- [CI/CD Integration](#cicd-integration)
- [Adding New Methods/Tools](#adding-new-methodstools)
- [Troubleshooting](#troubleshooting)
- [Maintenance](#maintenance)

---

## Architecture

### Component Overview

```text
src/pydantic_ai_integration/registry/
  __init__.py       # Public API exports
  types.py          # Shared types, enums, reports, results
  loader.py         # RegistryLoader - unified loading orchestration
  validators.py     # Coverage, consistency, and drift validators
```

### Key Concepts

| Component | Purpose | Responsibilities |
|-----------|---------|------------------|
| **RegistryLoader** | Unified entry point for loading methods and tools | Orchestrates loading, validation, error handling |
| **ValidationMode** | Controls validation behavior | `STRICT` (fail on errors), `WARNING` (log only), `OFF` (skip validation) |
| **Validators** | Ensure registry integrity | Coverage checks, consistency validation, drift detection |
| **Reports** | Structured validation results | `CoverageReport`, `ConsistencyReport`, `DriftReport` |
| **RegistryLoadResult** | Complete loading outcome | Success status, counts, validation reports, errors |

### Data Flow

```
1. initialize_registries() called
   ↓
2. RegistryLoader.load_all_registries()
   ↓
3. Load methods from YAML → method_registry.MANAGED_METHODS
   ↓
4. Load tools from YAML → tool decorator registrations
   ↓
5. Run validators (coverage, consistency, drift detection)
   ↓
6. Return RegistryLoadResult with reports
   ↓
7. Handle errors based on ValidationMode
```

---

## Quick Start

### Basic Usage

```python
from pydantic_ai_integration import initialize_registries

# Initialize with defaults (STRICT mode, drift detection enabled)
result = initialize_registries()

if result.success:
    print(f"✓ Loaded {result.methods_loaded} methods, {result.tools_loaded} tools")
else:
    print(f"✗ Validation failed: {len(result.errors)} errors")
```

### Custom Configuration

```python
from pydantic_ai_integration.registry import RegistryLoader, ValidationMode

# Create custom loader
loader = RegistryLoader(
    validation_mode=ValidationMode.WARNING,  # Log errors but don't fail
    enable_drift_detection=False             # Skip drift detection
)

# Load registries
result = loader.load_all_registries()

# Access validation reports
coverage = result.coverage_report
consistency = result.consistency_report
drift = result.drift_report
```

### Accessing Loaded Registries

```python
from pydantic_ai_integration.method_registry import MANAGED_METHODS

# Lookup method by name
method_def = MANAGED_METHODS.get("CasefileService.create_casefile")

if method_def:
    print(f"Method: {method_def.full_name}")
    print(f"Service: {method_def.service_name}")
    print(f"Classification: {method_def.classification}")
```

---

## Validation Modes

### STRICT Mode (Default)

**Behavior:** Validation errors cause initialization to fail.

**Use Cases:**
- Production environments
- CI/CD pipelines
- Pre-deployment checks

**Example:**
```python
loader = RegistryLoader(validation_mode=ValidationMode.STRICT)
result = loader.load_all_registries()

if not result.success:
    # Application should not start
    raise RuntimeError(f"Registry validation failed: {result.errors}")
```

**Environment Variable:**
```bash
export REGISTRY_STRICT_VALIDATION=true
```

---

### WARNING Mode

**Behavior:** Validation errors are logged but don't fail initialization.

**Use Cases:**
- Development environments
- Debugging registry issues
- Gradual migration to strict validation

**Example:**
```python
loader = RegistryLoader(validation_mode=ValidationMode.WARNING)
result = loader.load_all_registries()

# Always succeeds, check reports for issues
if result.coverage_report.missing_methods:
    print(f"⚠ Missing methods: {result.coverage_report.missing_methods}")
```

**Environment Variable:**
```bash
export REGISTRY_STRICT_VALIDATION=false
```

---

### OFF Mode

**Behavior:** Validation is completely skipped.

**Use Cases:**
- Emergency deployments
- Temporary workarounds
- Performance-critical scenarios

**Example:**
```python
loader = RegistryLoader(validation_mode=ValidationMode.OFF)
result = loader.load_all_registries()

# No validation performed, check only success/failure
assert result.success
```

**Not recommended for production use.**

---

## Environment Variables

### Configuration Options

| Variable | Values | Default | Purpose |
|----------|--------|---------|---------|
| `REGISTRY_STRICT_VALIDATION` | `true`, `false` | `true` | Controls validation mode (STRICT vs WARNING) |
| `SKIP_DRIFT_DETECTION` | `true`, `false` | `false` | Disables drift detection when `true` |
| `SKIP_AUTO_INIT` | `true`, `false` | `false` | Prevents auto-initialization on module import |

### Priority Order

Configuration sources are evaluated in this order (highest to lowest priority):

1. **Explicit constructor arguments**
   ```python
   RegistryLoader(validation_mode=ValidationMode.WARNING)
   ```

2. **Environment variables**
   ```bash
   export REGISTRY_STRICT_VALIDATION=false
   ```

3. **Default values**
   - ValidationMode: `STRICT`
   - enable_drift_detection: `True`

### Examples

**Development Setup (.env file):**
```bash
# Relaxed validation for local development
REGISTRY_STRICT_VALIDATION=false
SKIP_DRIFT_DETECTION=true
```

**Production Setup:**
```bash
# Strict validation in production
REGISTRY_STRICT_VALIDATION=true
SKIP_DRIFT_DETECTION=false
```

**CI/CD Setup:**
```bash
# Fail builds on validation errors
REGISTRY_STRICT_VALIDATION=true
SKIP_DRIFT_DETECTION=false
SKIP_AUTO_INIT=false
```

---

## CI/CD Integration

### GitHub Actions Workflow

The repository includes a comprehensive CI/CD workflow at `.github/workflows/registry-validation.yml`.

**Workflow Jobs:**

1. **validate-registries**: Runs validation script in STRICT mode
2. **test-registries**: Executes full test suite with coverage reporting

**Triggers:**
- Push to `main`, `develop`, `feature/*` branches
- Pull requests to `main`, `develop`
- Manual workflow dispatch

### Validation Script

**Location:** `scripts/validate_registries.py`

**Usage:**

```bash
# Run with default STRICT mode
python scripts/validate_registries.py

# Run in WARNING mode
python scripts/validate_registries.py --warning

# Skip drift detection
python scripts/validate_registries.py --no-drift

# Verbose output
python scripts/validate_registries.py -v

# Quiet mode (errors only)
python scripts/validate_registries.py -q
```

**Exit Codes:**
- `0`: Validation successful
- `1`: Validation errors found
- `2`: Script execution error

### Local Pre-Commit Validation

Add to your workflow before committing:

```bash
# Validate registries
python scripts/validate_registries.py

# Run registry tests
pytest tests/registry/ -v

# Check for drift
python scripts/validate_registries.py --strict
```

### Blocking PR Checks

The GitHub Actions workflow is configured to block PRs when:
- Validation script exits with non-zero code
- Any registry tests fail
- Coverage drops below threshold

---

## Adding New Methods/Tools

### Step 1: Define Method in Service

```python
# src/casefileservice/service.py
from pydantic_ai_integration.method_decorator import register_service_method

@register_service_method(
    classification="workspace.management",
    description="Archive old casefiles",
    requires_auth=True,
    request_model=ArchiveCasefileRequest,
    response_model=ArchiveCasefileResponse,
)
async def archive_casefile(self, casefile_id: str) -> Casefile:
    """Archive a casefile."""
    # Implementation...
```

### Step 2: Add to YAML Inventory

**File:** `config/methods_inventory_v1.yaml`

```yaml
- method_name: "CasefileService.archive_casefile"
  service_name: "CasefileService"
  classification: "workspace.management"
  description: "Archive old casefiles"
  requires_auth: true
  payload_model: "ArchiveCasefilePayload"
  response_model: "ArchiveCasefileResponse"
```

### Step 3: Create Tool Definition

**File:** `config/methodtools_v1/CasefileService_archive_casefile_tool.yaml`

```yaml
tool_name: "archive_casefile_tool"
schema_version: "2.0"
metadata:
  version: "1.0.0"
  tags: ["casefile", "archive", "workspace"]

method:
  method_name: "CasefileService.archive_casefile"
  service_name: "CasefileService"

parameters:
  casefile_id:
    type: "string"
    description: "ID of casefile to archive"
    required: true
    source: "method"
```

### Step 4: Validate

```bash
# Run validation script
python scripts/validate_registries.py --strict

# Run tests
pytest tests/registry/ -v
```

### Step 5: Verify Coverage

```python
# Check method is loaded
from pydantic_ai_integration.method_registry import MANAGED_METHODS

method = MANAGED_METHODS.get("CasefileService.archive_casefile")
assert method is not None
assert method.classification == "workspace.management"
```

---

## Troubleshooting

### Common Issues

#### 1. Missing Methods

**Symptom:**
```
ValidationError: Missing methods not in YAML inventory: ['CasefileService.new_method']
```

**Cause:** Method decorated with `@register_service_method` but not in YAML inventory.

**Fix:**
1. Add method to `config/methods_inventory_v1.yaml`
2. Or remove the decorator if method should not be managed

---

#### 2. Missing Tools

**Symptom:**
```
ValidationError: Missing tool definitions: ['CasefileService.new_method']
```

**Cause:** Method in YAML inventory but no corresponding tool YAML file.

**Fix:**
1. Create tool definition in `config/methodtools_v1/`
2. Use naming convention: `{ServiceName}_{method_name}_tool.yaml`
3. Run validation to verify

---

#### 3. Parameter Drift

**Symptom:**
```
DriftError: Parameter mismatch for CasefileService.update_casefile
Expected: ['casefile_id', 'title', 'description']
Found: ['casefile_id', 'title']
```

**Cause:** Method signature changed but YAML not updated.

**Fix:**
1. Update method definition in `config/methods_inventory_v1.yaml`
2. Update tool definition in `config/methodtools_v1/`
3. Ensure parameters match service method signature

---

#### 4. Validation Mode Conflicts

**Symptom:**
```
Environment variable REGISTRY_STRICT_VALIDATION=true but code uses WARNING mode
```

**Cause:** Conflicting configuration sources.

**Fix:**
Check priority order:
1. Constructor arguments override environment variables
2. Use consistent configuration across application
3. Document validation mode choices

---

#### 5. Auto-Initialization Disabled

**Symptom:**
```
AttributeError: MANAGED_METHODS is empty
```

**Cause:** `SKIP_AUTO_INIT=true` prevents automatic loading.

**Fix:**
1. Explicitly call `initialize_registries()` at application startup
2. Or remove `SKIP_AUTO_INIT` environment variable

```python
from pydantic_ai_integration import initialize_registries

# Explicit initialization
result = initialize_registries()
if not result.success:
    raise RuntimeError("Registry initialization failed")
```

---

### Debugging Tips

#### Enable Verbose Logging

```python
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("pydantic_ai_integration.registry")
logger.setLevel(logging.DEBUG)
```

#### Inspect Validation Reports

```python
result = initialize_registries()

# Check coverage
print(f"Methods loaded: {len(result.coverage_report.methods_loaded)}")
print(f"Tools loaded: {len(result.coverage_report.tools_loaded)}")
print(f"Missing: {result.coverage_report.missing_methods}")

# Check consistency
print(f"Orphaned tools: {result.consistency_report.orphaned_tools}")
print(f"Duplicate methods: {result.consistency_report.duplicate_methods}")

# Check drift
if result.drift_report:
    print(f"Drift detected: {result.drift_report.has_drift}")
    for issue in result.drift_report.issues:
        print(f"  - {issue}")
```

#### Run Tests with Verbose Output

```bash
pytest tests/registry/ -vv --tb=short
```

---

## Maintenance

### Monthly Tasks

- [ ] Review validation reports for warnings
- [ ] Update YAML inventories for new methods
- [ ] Check CI/CD workflow execution times
- [ ] Verify coverage remains at 100%

### Quarterly Tasks

- [ ] Review and update documentation
- [ ] Audit drift detection accuracy
- [ ] Evaluate validation mode effectiveness
- [ ] Plan schema version upgrades

### Annual Tasks

- [ ] Comprehensive registry audit
- [ ] Performance optimization review
- [ ] Schema version migration planning
- [ ] Tool retirement analysis

### Health Checks

**Weekly:**
```bash
# Verify registries load successfully
python scripts/validate_registries.py --strict

# Run full test suite
pytest tests/registry/ tests/test_integration_init.py -v
```

**Monthly:**
```bash
# Generate coverage report
pytest tests/registry/ --cov=src/pydantic_ai_integration/registry --cov-report=html

# Review drift detection results
python scripts/validate_registries.py --strict -v | grep "drift"
```

---

## Best Practices

### DO ✅

- Use STRICT mode in production
- Keep YAML inventories synchronized with code
- Run validation before committing
- Document new methods/tools thoroughly
- Monitor validation reports in CI/CD
- Use semantic versioning for schema changes
- Test validation modes in non-production environments

### DON'T ❌

- Skip validation in production
- Use OFF mode without justification
- Ignore WARNING mode messages
- Commit without running validation
- Mix validation modes across environments
- Modify registries at runtime
- Bypass CI/CD checks

---

## References

- [CI/CD Workflow Documentation](.github/workflows/README.md)
- [Pydantic AI Integration Overview](./PYDANTIC_AI_INTEGRATION_OVERVIEW.md)
- [Branch Development Plan](../BRANCH_DEVELOPMENT_PLAN.md)
- [Validation Script](../scripts/validate_registries.py)

---

## Support

For issues or questions:

1. Check this documentation
2. Review troubleshooting section
3. Inspect validation reports
4. Check GitHub Actions logs
5. Open an issue with reproduction steps

---

**Last Updated:** October 11, 2025
**Status:** Phase 6 Complete (Documentation)
