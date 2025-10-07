# Test Infrastructure

**Last Updated:** October 7, 2025

This directory contains the unified test infrastructure for the my-tiny-data-collider project. The testing approach has been simplified to use YAML-driven test scenarios embedded directly in tool configurations, eliminating overlapping validation layers.

## Directory Structure

```
tests/
├── README.md              # This documentation
├── conftest.py            # Pytest configuration and shared fixtures
├── test_imports.py        # Basic import validation tests
├── helpers/               # Consolidated test utilities
│   ├── __init__.py
│   ├── tool_test_helper.py    # Core test utilities
│   ├── test_environments.py   # Test environment fixtures
│   ├── test_scenario_runner.py # Scenario execution engine
│   ├── test_report_generator.py # Report generation
│   └── test_runner.py         # Main test execution script
├── reports/               # Generated test reports (auto-created)
└── data/                  # Test data files (auto-created)
```

## Testing Approach

### YAML-Driven Testing

Test scenarios are now embedded directly in tool YAML configurations under the `test_scenarios` section. This approach:

- **Eliminates redundancy**: Single source of truth for tool behavior and testing
- **Simplifies maintenance**: Tests evolve with tool configurations
- **Enables automation**: CI/CD can run tests directly from tool definitions
- **Provides consistency**: Standardized test environments and scenarios

### Test Scenario Structure

Each tool YAML can include a `test_scenarios` section:

```yaml
tool_name: my_tool
# ... tool configuration ...

test_scenarios:
  happy_paths:
    - name: "basic_create"
      description: "Create casefile with minimal valid inputs"
      environment: "valid_user_session"
      input:
        title: "Test Casefile"
      expected:
        status: "COMPLETED"
        has_casefile_id: true

  unhappy_paths:
    - name: "missing_title"
      description: "Fail when required title is missing"
      environment: "valid_user_session"
      input: {}  # Empty input
      expected:
        status: "FAILED"
        error_type: "ValidationError"
```

## Test Environments

Predefined test environments provide consistent user sessions and permissions:

- `valid_user_session`: Full permissions, valid session
- `read_only_user`: Read-only permissions
- `expired_session_user`: Expired session/token
- `invalid_session_user`: Non-existent session
- `admin_user`: Administrator with all permissions
- `unauthenticated_user`: No authentication

## Running Tests

### Command Line Execution

Use the main test runner script:

```bash
# Run tests for a specific tool
python -m tests.helpers.test_runner config/toolsets/core/casefile_management/create_casefile_inherited.yaml

# Run tests for all tools in a directory
python -m tests.helpers.test_runner "config/toolsets/**/*.yaml"

# Run with verbose output
python -m tests.helpers.test_runner -v config/toolsets/**/*.yaml

# Generate custom report name
python -m tests.helpers.test_runner -r my_custom_report config/toolsets/**/*.yaml
```

### Pytest Integration

Basic validation tests still use pytest:

```bash
# Run import validation tests
pytest tests/test_imports.py -v

# Run with coverage
pytest --cov=src tests/test_imports.py
```

## Report Generation

Tests generate multiple report formats in `tests/reports/`:

- **HTML Report**: Interactive web view with detailed results
- **JSON Report**: Machine-readable structured data
- **Summary Report**: Concise text summary

## Migration from Legacy Tests

The following legacy test files have been removed:

- `test_factory_integration.py` → Functionality moved to YAML scenarios
- `test_method_decorator.py` → Validation now in tool generation
- `test_test_helpers.py` → Consolidated into `tool_test_helper.py`
- `system_validation/` → Redundant with YAML-driven approach
- `api/` and `integration/` → Empty directories removed

### Migration Steps Completed

1. ✅ **Created new clean structure** with consolidated helpers
2. ✅ **Implemented YAML-driven test scenarios** in tool configurations
3. ✅ **Removed redundant/overlapping test files** and directories
4. ✅ **Updated CI/CD scripts** to use new test runner
5. ✅ **Cleaned up directory structure** and documentation

## Continuous Integration

Update your CI/CD pipeline to use the new test runner:

```yaml
# Example GitHub Actions step
- name: Run Tool Tests
  run: python -m tests.helpers.test_runner "config/toolsets/**/*.yaml" -v

- name: Upload Test Reports
  uses: actions/upload-artifact@v3
  with:
    name: test-reports
    path: tests/reports/
```

## Benefits

- **Single Source of Truth**: Tests defined in YAML alongside tools
- **No Overlapping Layers**: Eliminated redundant validation
- **Simplified Structure**: Clear, organized directory structure
- **Environment-Aware**: Happy/unhappy scenarios with different contexts
- **Unified Execution**: Single command for comprehensive testing