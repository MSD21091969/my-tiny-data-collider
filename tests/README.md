# Test Suite

**Last Updated:** 2025-10-17

## Current Status

✅ **Unit Tests:** 179 passed, 0 warnings, 0 failures (2.76s)  
⚠️ **Integration Tests:** 11 passed, 18 skipped, 5 failed (tool registry issues - expected)

## Directory Structure

```
tests/
├── conftest.py              # Root pytest configuration
├── unit/                    # Unit tests (179 tests)
│   ├── casefileservice/     # Repository tests
│   ├── coreservice/         # Core service tests
│   ├── pydantic_models/     # Model validation tests
│   └── registry/            # Registry loader/validator tests
├── integration/             # Integration tests (34 tests)
│   ├── conftest.py          # Integration fixtures
│   ├── test_mvp_user_journeys.py
│   ├── test_tool_method_integration.py
│   └── test_tool_execution_modes.py
├── fixtures/                # Test data and mocks
└── reports/                 # Test coverage reports
```

## Running Tests

### All Tests
```powershell
pytest
```

### By Category
```powershell
pytest tests/unit/           # Unit tests only
pytest tests/integration/    # Integration tests only
```

### With Options
```powershell
pytest -v                    # Verbose output
pytest -q                    # Quiet output
pytest -s                    # Show print statements
pytest --tb=short            # Short traceback format
pytest -k "test_name"        # Run specific test by name
```

### With Coverage
```powershell
pytest --cov=src --cov-report=html
```

## Test Organization

### Unit Tests (`unit/`)
Test individual components in isolation:
- **Pydantic Models:** Custom types, validators, canonical models
- **Services:** Repository CRUD, service methods, autonomous execution
- **Registry:** Tool registration, validation, drift detection

### Integration Tests (`integration/`)
Test cross-service interactions:
- **MVP User Journeys:** End-to-end workflows (7/7 passing)
- **Tool-Method Integration:** Tool execution and parameter mapping
- **Execution Modes:** Direct, DTO, mock, dry-run patterns

## Important Notes

### Test Directory Structure Rules
⚠️ **CRITICAL:** Test directories must NOT have `__init__.py` files!

With `package-dir = {"": "src"}` in `pyproject.toml`, pytest adds `src/` to `sys.path`. If test directories have `__init__.py`, pytest treats them as packages matching source code structure, causing namespace confusion.

**Solution:** Tests are NOT packages - they import from the installed package.

### Import Pattern
```python
# ✅ Correct
from casefileservice.repository import CasefileRepository
from pydantic_models.base.types import RequestStatus

# ❌ Wrong (circular import)
from src.casefileservice.repository import CasefileRepository
```

## Test Naming Conventions

- Test files: `test_*.py`
- Test functions: `test_*`
- Test classes: `Test*`
- Use descriptive names: `test_feature_scenario_expected_result`

## Writing New Tests

```python
import pytest

@pytest.mark.asyncio  # For async tests
async def test_my_feature():
    """Clear description of what's being tested."""
    # Arrange
    # Act
    # Assert
    pass
```

## Fixtures

Shared fixtures in `conftest.py`:
- `test_context` - Basic execution context
- `mock_services` - Mocked service dependencies
- Additional integration fixtures in `tests/integration/conftest.py`