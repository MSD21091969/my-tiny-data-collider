# Archived Test Infrastructure

*Last updated: October 8, 2025*

YAML-driven test infrastructure that was previously part of the main test suite.

## 📦 Archived Components

### helpers/
Comprehensive test utilities for YAML-driven testing:

#### tool_test_helper.py
**Purpose**: Helper class for testing MDS tools with reduced boilerplate
**Features**:
- Create test casefiles
- Create test tool sessions
- Automatic cleanup after tests
- Async context managers for test setup/teardown

#### test_environments.py
**Purpose**: Test environment fixtures and configurations
**Features**:
- Valid/invalid user sessions
- Permission configurations
- Authentication states

#### test_scenario_runner.py
**Purpose**: Execute YAML-defined test scenarios
**Features**:
- Parse YAML test scenarios
- Execute test cases
- Collect results
- Handle async execution

#### test_report_generator.py
**Purpose**: Generate test reports in multiple formats
**Features**:
- HTML reports
- JSON reports
- Text reports
- Summary statistics

#### test_runner.py
**Purpose**: Main entry point for YAML test execution
**Features**:
- CLI for running YAML tests
- Glob pattern support
- Environment overrides
- Verbose output options

**Example Usage**:
```bash
python -m tests.helpers.test_runner config/toolsets/**/*.yaml
```

## 🔄 Why Archived?

This test infrastructure was archived on October 8, 2025 because:

1. **Overlap with Archived Scripts**: Works in conjunction with `scripts/archive/yaml_test_executor.py` which was also archived
2. **Import Errors**: Has dependencies on model structures that may have changed
3. **Complexity**: Overly complex for current testing needs
4. **Maintenance**: Not aligned with simplified test approach focusing on core validation

## 💡 Current Testing Approach

The current test approach uses:
- Simple pytest tests in `test_imports.py`
- Validation scripts (`validate_dto_alignment.py`) for parameter alignment
- Standard pytest fixtures in `conftest.py`
- Focus on business logic and integration testing

## 🔄 Restoration

If YAML-driven testing is needed in the future:

1. **Fix Imports**: Update import statements to match current codebase structure
2. **Update Dependencies**: Ensure all required models and services exist
3. **Test Infrastructure**: Verify helpers work with current architecture
4. **Move Back**: Copy helpers back to main tests directory

```powershell
# Restore helpers
Copy-Item -Path "tests\archive\helpers" -Destination "tests\helpers" -Recurse
```

## 📚 Related

- Main [Tests README](../README.md)
- [Scripts Archive](../../scripts/archive/README.md) - Related archived scripts
- [YAML Test Executor](../../scripts/archive/yaml_test_executor.py) - Complementary archived script
