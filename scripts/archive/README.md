# Archived Scripts

*Last updated: October 8, 2025*

Scripts that are not part of the core daily workflow but may be useful for specific scenarios.

## 📦 Archived Scripts

### release_version.py
**Purpose**: Automated version release for methods registry
**Use Case**: Releasing new versions with changelog generation and git tagging
**Status**: Available for future releases

**Usage**:
```bash
python scripts/archive/release_version.py --type patch
python scripts/archive/release_version.py --type minor --changelog "Add archive functionality"
python scripts/archive/release_version.py --type major --changelog "Unified parameter naming"
```

---

### run_continuous_integration_tests.py
**Purpose**: Continuous integration test runner
**Use Case**: Running integration tests continuously with comprehensive logging
**Status**: Available for CI/CD pipeline integration

**Usage**:
```bash
python scripts/archive/run_continuous_integration_tests.py
```

---

### yaml_test_executor.py
**Purpose**: YAML-driven test execution engine
**Use Case**: Executing test scenarios defined in tool YAML configurations
**Status**: Available for specialized testing scenarios

**Usage**:
```bash
python scripts/archive/yaml_test_executor.py
```

---

## 🔄 Restoring Scripts

If you need to use any of these scripts, simply move them back to the main scripts directory:

```powershell
Move-Item -Path "scripts\archive\script_name.py" -Destination "scripts\script_name.py"
```

Or run them directly from the archive:

```bash
python scripts/archive/script_name.py
```

---

## 📋 Why Archived?

These scripts were moved to the archive to keep the main scripts directory focused on the core workflow for the 6-layer architecture with parameter inheritance:

1. **validate_dto_alignment.py** - Parameter drift detection
2. **generate_tools.py** - Tool generation with inheritance
3. **import_generated_tools.py** - Registry population
4. **show_tools.py** - Verification

The archived scripts remain available for specialized use cases like releases, CI/CD automation, and advanced testing.
