# Testing Guide

## Overview

This project uses pytest with custom markers to categorize and selectively run tests.

## Test Markers

We use the following pytest markers (defined in `pytest.ini`):

| Marker | Description | Use Case |
|--------|-------------|----------|
| `@pytest.mark.unit` | Fast unit tests, no external dependencies | Testing pure functions, logic, models |
| `@pytest.mark.integration` | Integration tests, may use mocks | Testing service interactions |
| `@pytest.mark.firestore` | Requires Firestore connection | Testing persistence layer |
| `@pytest.mark.mock` | Uses mock backends | Testing without real services |
| `@pytest.mark.slow` | Tests taking >5 seconds | E2E workflows, heavy operations |

## Running Tests

### Run All Tests
```bash
pytest
```

### Run Specific Categories
```bash
# Run only unit tests (fast)
pytest -m unit

# Run only integration tests
pytest -m integration

# Run Firestore tests (requires connection)
pytest -m firestore

# Run tests using mocks
pytest -m mock

# Run slow tests
pytest -m slow
```

### Exclude Categories
```bash
# Skip slow tests (for quick validation)
pytest -m "not slow"

# Skip Firestore tests (when offline)
pytest -m "not firestore"

# Skip both Firestore and slow tests
pytest -m "not (firestore or slow)"
```

### Combine Markers
```bash
# Run unit OR integration tests
pytest -m "unit or integration"

# Run integration tests that use mocks
pytest -m "integration and mock"

# Run everything except Firestore and slow
pytest -m "not firestore and not slow"
```

### Verbose Output
```bash
# Show test names as they run
pytest -v

# Show extra details
pytest -vv

# Show print statements
pytest -s
```

## Test Organization

```
tests/
├── __init__.py
├── test_example_with_markers.py    # Example showing marker usage
├── fixtures/
│   └── common.py                    # Shared test fixtures
└── [future test files]
```

## Writing Tests

### Example: Unit Test
```python
import pytest

@pytest.mark.unit
def test_simple_function():
    """Fast test with no dependencies."""
    result = my_function(input_data)
    assert result == expected_output
```

### Example: Integration Test with Mock
```python
import pytest

@pytest.mark.integration
@pytest.mark.mock
async def test_service_with_mock():
    """Test service using mock repository."""
    service = MyService(use_mocks=True)
    result = await service.do_something()
    assert result.status == "success"
```

### Example: Firestore Test (Slow)
```python
import pytest

@pytest.mark.firestore
@pytest.mark.slow
async def test_firestore_operation():
    """Test real Firestore operation."""
    repo = FirestoreRepository()
    data = await repo.fetch_data()
    assert data is not None
```

### Example: Multiple Markers
```python
import pytest

@pytest.mark.integration
@pytest.mark.firestore
@pytest.mark.slow
async def test_end_to_end_workflow():
    """Full E2E test with real Firestore."""
    # Test complete workflow
    pass
```

## CI/CD Integration

### Fast Pipeline (Pull Requests)
```yaml
# Run only fast tests on every PR
pytest -m "unit and not slow"
```

### Full Pipeline (Merges to Main)
```yaml
# Run all tests including integration
pytest -m "not firestore"  # Skip if no Firestore in CI
```

### Nightly Pipeline
```yaml
# Run everything including slow tests
pytest
```

## Coverage Reports

### Generate Coverage Report
```bash
# Run tests with coverage
pytest --cov=src --cov-report=term-missing

# Generate HTML report
pytest --cov=src --cov-report=html

# Open HTML report (Windows)
start htmlcov/index.html
```

### Coverage with Markers
```bash
# Coverage for unit tests only
pytest -m unit --cov=src

# Coverage excluding slow tests
pytest -m "not slow" --cov=src
```

## Test Fixtures

Shared test fixtures are defined in `tests/fixtures/common.py`:

```python
import pytest
from tests.fixtures.common import sample_user, sample_casefile

@pytest.mark.unit
def test_with_fixture(sample_user):
    """Use shared fixture in test."""
    assert sample_user.id is not None
```

## Best Practices

### 1. **Always Use Markers**
Every test should have at least one marker:
```python
@pytest.mark.unit  # Good
def test_something():
    pass

def test_something():  # Bad - no marker
    pass
```

### 2. **Mark Slow Tests**
If a test takes >5 seconds, mark it as slow:
```python
@pytest.mark.slow
def test_heavy_operation():
    # Long-running test
    pass
```

### 3. **Use Multiple Markers When Appropriate**
Combine markers to describe test characteristics:
```python
@pytest.mark.integration
@pytest.mark.firestore
@pytest.mark.slow
async def test_complex_operation():
    pass
```

### 4. **Skip Tests Gracefully**
Use pytest.skip for tests requiring specific conditions:
```python
@pytest.mark.firestore
def test_firestore_feature():
    if not firestore_available():
        pytest.skip("Firestore not configured")
    # Test code
```

### 5. **Name Tests Descriptively**
Use clear, descriptive test names:
```python
@pytest.mark.unit
def test_user_creation_with_valid_email():  # Good
    pass

@pytest.mark.unit
def test_user():  # Bad - unclear
    pass
```

## Troubleshooting

### "Unknown marker" Warning
If you see warnings about unknown markers, ensure `pytest.ini` is in the project root.

### Tests Not Being Collected
- Check file names start with `test_`
- Check function names start with `test_`
- Ensure files are in `tests/` directory

### Markers Not Working
- Verify `pytest.ini` exists and has markers defined
- Run `pytest --markers` to see available markers
- Check marker spelling matches definition

## Quick Reference

```bash
# Fast development workflow
pytest -m "unit and not slow" -v

# Pre-commit checks
pytest -m "not (firestore or slow)"

# Full local validation
pytest -m "not firestore"

# Complete test suite
pytest
```

## Resources

- [pytest documentation](https://docs.pytest.org/)
- [pytest markers guide](https://docs.pytest.org/en/stable/example/markers.html)
- Project test examples: `tests/test_example_with_markers.py`
