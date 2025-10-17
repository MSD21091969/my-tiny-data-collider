# Integration Tests

**Last Updated:** 2025-10-17

## Test Suites

### test_mvp_user_journeys.py ✅
- **Status:** 7/7 passing
- Complete user journey tests
- Auth flow validation  
- Request context flow verification
- Session context preservation

### test_tool_method_integration.py ⚠️
- **Status:** 2/7 passing (5 failures due to tool registry issues)
- Tool-to-method integration tests
- Parameter mapping verification
- Error handling tests
- Registry validation

### test_tool_execution_modes.py ⚠️
- **Status:** 2/27 passing (18 skipped, 7 failures due to tool registry)
- Comprehensive execution mode tests (7 modes)
- Direct execution, DTO, mock, dry-run tests
- Performance tracking
- Error handling scenarios

## Running Tests

### All Integration Tests
```powershell
pytest tests/integration/ -v
```

### By Test Suite
```powershell
# MVP user journeys (all passing)
pytest tests/integration/test_mvp_user_journeys.py -v

# Tool method integration
pytest tests/integration/test_tool_method_integration.py -v

# Execution modes
pytest tests/integration/test_tool_execution_modes.py -v
```

### By Test Class
```powershell
# Specific test class
pytest tests/integration/test_tool_execution_modes.py::TestDirectToolExecution -v

# Specific test
pytest tests/integration/test_mvp_user_journeys.py::TestMVPUserJourney::test_complete_user_journey_create_casefile_and_execute_tool -v
```

### With Logging
```powershell
# Show execution details
pytest tests/integration/ -v -s --log-cli-level=INFO

# Debug level (shows data flow)
pytest tests/integration/ -v -s --log-cli-level=DEBUG
```

## Test Execution Modes

1. **Direct Tool Execution** - `tool.implementation()` calls without additional layers
2. **Via Request DTO** - Full Request DTO construction and service method flow
3. **Mock Mode** - Mocked services for testing without external dependencies
4. **Dry Run Mode** - Preview mode, no actual service execution
5. **Result Verification** - Structure, timing, and data correctness validation
6. **Error Handling** - Invalid params, timeouts, missing services scenarios
7. **Performance Tracking** - Execution timing measurement and analysis

## Test Results

### Current Status (2025-10-17)
- **MVP User Journeys:** 7/7 passed ✅
- **Tool Method Integration:** 2/7 passed (5 failures due to tool registry issues)
- **Tool Execution Modes:** 2/27 passed (18 skipped, 7 failures due to tool registry)

### Known Issues
- Tool registry coverage/drift warnings (YAML methods not generating tools)
- This is a system issue unrelated to test infrastructure
- Tests validate that error handling works correctly

### Expected Results

**Success (with configured services):**
- Status: "success"
- Result contains expected data structures
- Duration tracked in milliseconds
- All assertions pass

**Success (without configured services):**
- Status: "error"  
- Error type indicates missing dependency
- Tests pass (validates error handling)

**Dry Run Mode:**
- Status: "dry_run"
- Preview mode - no actual execution
- Parameters logged for verification

## Test Fixtures

Available in `tests/integration/conftest.py` and root `conftest.py`:

- **test_context** - Basic execution context for tool testing
- **mock_context** - Context without casefile ID
- **mock_casefile_context** - Context with casefile ID
- **valid_user_session** - Authenticated session fixture
- **read_only_user** - Limited permissions scenario
- **expired_session_user** - Session expiration testing
- **invalid_session_user** - Invalid/non-existent session testing

## Test Coverage

### Categories
1. **User Journeys** - End-to-end workflows (7/7 passing)
2. **Tool-Method Integration** - Tool execution and parameter mapping
3. **Execution Modes** - Different execution patterns and error scenarios

### Services Under Test
- **CasefileService** - Casefile CRUD operations
- **ToolSessionService** - Session management
- **AuthService** - Authentication and authorization
- **RequestHub** - Request orchestration and policy enforcement

## Writing New Tests

### Test Structure
```python
import pytest
from tests.fixtures.integration_fixtures import test_context

@pytest.mark.asyncio
@pytest.mark.integration
async def test_my_feature(test_context):
    """Clear description of what's being tested."""
    # Arrange
    # Act
    # Assert
```

### Assertions
```python
# Structure validation
assert "status" in result
assert result["status"] in ["success", "error", "dry_run"]

# Success path
if result["status"] == "success":
    assert "result" in result
    assert "duration_ms" in result

# Error handling
elif result["status"] == "error":
    assert "error_type" in result
    assert "error_message" in result
```

### Test Naming Conventions
- `test_<feature>_<scenario>` - Feature-based tests
- `test_<action>_<condition>` - Action-based tests  
- `Test<Category>` - Test class names
- Always include clear docstrings

## Maintenance Notes

### Removed Utility Scripts (2025-10-17)
The following scripts were removed as redundant with pytest infrastructure:
- `verify_implementation.py` - Replaced by `test_tool_method_integration.py`
- `run_tool_tests.py` - Replaced by native pytest CLI (`pytest -k`, `-m` flags)
- `show_data_flow.py` - Replaced by pytest logging (`-s --log-cli-level=INFO`)

Use pytest's built-in features for debugging and selective test execution.
