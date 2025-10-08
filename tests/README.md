# Tests Directory

*Last updated: October 8, 2025 at 19:50*

Simplified test infrastructure focused on essential validation for the 6-layer architecture.

## 📁 Directory Structure

```
tests/
├── README.md              # This documentation
├── conftest.py            # Pytest configuration and fixtures
├── test_imports.py        # Basic import validation tests
├── reports/               # Generated test reports (auto-created, not committed)
│   └── .gitkeep
└── archive/               # Archived test infrastructure
    ├── README.md
    └── helpers/           # YAML-driven test helpers (archived)
```

## 🎯 Current Test Approach

### Core Tests

#### test_imports.py
**Purpose**: Validate basic package structure and imports
**Tests**:
- `test_casefile_service_import()` - Verify CasefileService imports
- `test_tool_session_service_import()` - Verify ToolSessionService imports  
- `test_pydantic_models_import()` - Verify Pydantic models import

**Run**:
```bash
pytest tests/test_imports.py -v
```

### Pytest Configuration (conftest.py)

Provides shared fixtures for all tests:
- `project_root` - Project root directory
- `src_path` - Source directory path
- `config_path` - Configuration directory path
- `tools_config_path` - Tools configuration path
- `methods_yaml_path` - Methods inventory path
- `add_src_to_path` - Auto-adds src to Python path

## 🧪 Running Tests

### All Tests
```bash
# Run all tests
pytest

# With verbose output
pytest -v

# With coverage
pytest --cov=src --cov-report=html

# Specific test file
pytest tests/test_imports.py
```

### Coverage Reports
```bash
# Generate HTML coverage report
pytest --cov=src --cov-report=html

# View report
# Open htmlcov/index.html in browser
```

### Test Reports
Generated reports are stored in `tests/reports/` but should not be committed to version control.

## 📝 Writing New Tests

### Test Structure
```python
def test_something():
    """Test description following AAA pattern."""
    # Arrange
    test_data = create_test_data()
    
    # Act
    result = function_under_test(test_data)
    
    # Assert
    assert result.status == expected_status
    assert result.payload is not None
```

### Using Fixtures
```python
def test_with_config(config_path):
    """Test using config path fixture."""
    methods_file = config_path / "methods_inventory_v1.yaml"
    assert methods_file.exists()
```

### Async Tests
```python
import pytest

@pytest.mark.asyncio
async def test_async_operation():
    """Test async service method."""
    service = MyService()
    result = await service.async_method()
    assert result is not None
```

## 🎯 Focus Areas for Testing

Given the 6-layer architecture with parameter inheritance:

### 1. Model Validation
- Test R-A-R pattern compliance
- Validate payload models
- Test request/response DTOs

### 2. Parameter Alignment
- Verify parameter extraction from DTOs
- Validate method parameter definitions
- Check tool parameter inheritance

### 3. Service Logic
- Test service method implementations
- Validate business logic
- Check error handling

### 4. Tool Registration
- Verify tools are registered in MANAGED_TOOLS
- Validate tool metadata
- Check parameter mappings

## 📦 Archived Test Infrastructure

The `archive/` directory contains YAML-driven test infrastructure that was previously used:

- **helpers/** - Comprehensive test utilities for YAML-driven testing
  - `tool_test_helper.py` - Tool testing utilities
  - `test_environments.py` - Test environment fixtures
  - `test_scenario_runner.py` - Scenario execution engine
  - `test_report_generator.py` - Report generation
  - `test_runner.py` - Main test execution script

This infrastructure was designed to work with YAML test scenarios embedded in tool configurations. It has been archived because:
1. Overlaps with archived `scripts/yaml_test_executor.py`
2. Has import errors with current codebase structure
3. Complex infrastructure for the current testing needs

Can be restored if YAML-driven testing approach is adopted in the future.

## 🔄 Testing Workflow

### Before Committing
```bash
# 1. Run validation scripts
python scripts/validate_dto_alignment.py

# 2. Run tests
pytest -v

# 3. Check coverage
pytest --cov=src --cov-report=term-missing
```

### CI/CD Integration
```yaml
# Example GitHub Actions workflow
- name: Run Tests
  run: |
    pytest --cov=src --cov-fail-under=80
    
- name: Validate DTO Alignment
  run: |
    python scripts/validate_dto_alignment.py
```

## 📊 Test Coverage Goals

- **Overall**: 80% minimum
- **AI-Generated Code**: 85% minimum
- **Core Services**: 90% target
- **Models**: 100% (Pydantic validation)

## 🔗 Related Documentation

- [Scripts README](../scripts/README.md) - Validation scripts
- [HANDOVER Document](../HANDOVER.md) - Current development state
- [AI Framework](../AI/README.md) - AI collaboration guidelines
- [Quality Assurance](../AI/workflows/quality-assurance.md) - QA processes

---

**Note**: Keep tests simple and focused. The core workflow relies on validation scripts (`validate_dto_alignment.py`) for parameter alignment checks. Tests should focus on business logic and integration validation.
