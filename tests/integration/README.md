# Integration Tests - feature/ai-method-integration

## Test Files

### Core Test Suites

**test_tool_method_integration.py**
- Original integration tests
- End-to-end tool execution validation
- Parameter mapping verification
- Error handling tests

**test_tool_execution_modes.py**
- Comprehensive test suite with 7 execution modes
- 13 test cases covering direct, DTO, mock, dry-run, verification, error, and performance modes
- Tests all 5 casefile tools

### Test Scripts

**verify_implementation.py**
- Quick verification script
- Demonstrates 3 test scenarios: dry run, execution, parameter mapping
- Run: `python tests/integration/verify_implementation.py`

**run_tool_tests.py**
- Test runner with mode filtering
- CLI: `python tests/integration/run_tool_tests.py --mode [direct|dto|mock|dryrun|verify|error|performance]`

**show_data_flow.py**
- Enhanced logging demonstration
- Shows all data at each execution step
- Requires valid Firestore configuration

## Running Tests

### All Integration Tests
```powershell
pytest tests/integration/ -v
```

### Specific Test Suites
```powershell
# Original integration tests
pytest tests/integration/test_tool_method_integration.py -v

# Execution modes suite
pytest tests/integration/test_tool_execution_modes.py -v

# Dry run mode only
pytest tests/integration/test_tool_execution_modes.py::TestDryRunMode -v

# Direct execution tests
pytest tests/integration/test_tool_execution_modes.py::TestDirectToolExecution -v
```

### With Logging
```powershell
# Show all logs
pytest tests/integration/test_tool_execution_modes.py -v -s --log-cli-level=INFO

# Debug level logging
pytest tests/integration/test_tool_execution_modes.py -v -s --log-cli-level=DEBUG
```

### Single Test
```powershell
pytest tests/integration/test_tool_execution_modes.py::TestDirectToolExecution::test_create_casefile_direct -v -s
```

## Test Modes

### 1. Direct Tool Execution
Tests `tool.implementation()` calls directly without additional layers.

### 2. Via Request DTO
Tests full Request DTO construction and service method flow.

### 3. Mock Mode
Uses mocked services to test logic without Firestore dependency.

### 4. Dry Run Mode
Tests preview mode where no actual service methods execute.

### 5. Result Verification
Validates result structure, timing, and data correctness per tool.

### 6. Error Handling
Tests error scenarios: invalid params, timeouts, missing services.

### 7. Performance Tracking
Measures and logs execution timing for performance analysis.

## Test Output

### Output Directory
`tests/integration/output/` contains:
- `data_flow_output.txt` - Full execution logs with data flow
- `test_output.txt` - Test run results
- Additional test artifacts as generated

### Expected Results

**Success (with Firestore):**
- Status: "success"
- Result contains casefile_id (e.g., cf_251010_abc123)
- Duration tracked in milliseconds
- All test assertions pass

**Success (without Firestore):**
- Status: "error"
- Error type: ServiceInstantiationError or ToolExecutionError
- Tests pass (infrastructure working, external dependency missing)

**Dry Run:**
- Status: "dry_run"
- Message indicates preview mode
- No service calls made
- All parameters logged

## Fixtures

Located in `tests/conftest.py`:

**mock_context()** - Basic execution context without casefile
**mock_casefile_context()** - Context with casefile ID
**valid_user_session()** - Valid authenticated session
**read_only_user()** - User with read-only permissions
**expired_session_user()** - Expired session scenario
**invalid_session_user()** - Invalid/non-existent session

## Test Coverage

**Tested Tools:** 5 of 64
- create_casefile_tool
- get_casefile_tool
- list_casefiles_tool
- update_casefile_tool
- delete_casefile_tool

**Remaining:** 59 tools require testing

## Known Issues

1. UUID not JSON serializable in some contexts (logged, not blocking)
2. Firestore credentials required for live service tests
3. Some error types return generic ToolExecutionError (can be more specific)

## Development

### Adding New Tests

1. Create test class inheriting from appropriate base
2. Use `@pytest.mark.asyncio` for async tests
3. Use `@pytest.mark.integration` for integration tests
4. Parameterize tests where applicable

### Test Naming Convention

- `test_<tool_name>_<mode>` for mode-specific tests
- `test_<functionality>` for feature tests
- Descriptive docstrings required

### Assertions

Check result structure:
```python
assert "status" in result
assert "tool_name" in result
assert result["status"] in ["success", "error", "dry_run"]
```

Check execution:
```python
if result["status"] == "success":
    assert "result" in result
    assert "duration_ms" in result
```

Check errors:
```python
elif result["status"] == "error":
    assert "error_type" in result
    assert "error_message" in result
```
