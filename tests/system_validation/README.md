# System Validation Tests

**Rigorous automated testing framework for system-wide code validation**

## Overview

This test suite validates fundamental code integrity after refactoring:
- ✅ **Code Integrity**: Syntax, imports, module structure
- ✅ **Type Validation**: Pydantic models, type hints, DTO structure
- ✅ **YAML Validation**: Schema compliance, data integrity, classification

## Quick Start

### Run All Validation Tests
```bash
# From project root
python tests/system_validation/run_all_validation.py
```

### Run Individual Test Suites
```bash
# Code integrity (syntax, imports, modules)
python -m pytest tests/system_validation/test_code_integrity.py -v -s

# Type validation (Pydantic models, type hints)
python -m pytest tests/system_validation/test_type_validation.py -v -s

# YAML validation (schema, data integrity)
python -m pytest tests/system_validation/test_yaml_validation.py -v -s
```

## Test Suites

### 1. Code Integrity Tests (`test_code_integrity.py`)

**What it validates**:
- All Python files have valid syntax
- Critical modules are importable
- Service classes exist and are accessible
- No broken imports across codebase

**Output**:
```
CODE INTEGRITY REPORT - Syntax Validation
================================================================================
Total Files: 47
Passed: 47
Failed: 0
Success Rate: 100.00%

CRITICAL MODULE IMPORT TEST
================================================================================
  ✅ pydantic_ai_integration.method_definition
  ✅ pydantic_ai_integration.method_registry
  ✅ pydantic_ai_integration.method_decorator
  [...]

Result: 6/6 modules importable
```

**Tests**:
- `test_all_python_files_valid_syntax` - Validates syntax of all .py files
- `test_critical_modules_importable` - Tests registry and model imports
- `test_service_classes_exist` - Verifies all 6 service classes accessible

---

### 2. Type Validation Tests (`test_type_validation.py`)

**What it validates**:
- BaseRequest/BaseResponse envelope structure
- All Pydantic models are valid
- Method definition models can be instantiated
- Operation model files are importable
- Registry API functions have type hints

**Output**:
```
BASE ENVELOPE STRUCTURE TEST
================================================================================
  ✅ BaseRequest structure valid
  ✅ BaseResponse structure valid

METHOD DEFINITION MODELS TEST
================================================================================
  ✅ MethodParameterDef (5 fields)
  ✅ MethodMetadata (4 fields)
  ✅ MethodBusinessRules (8 fields)
  ✅ MethodModels (2 fields)
  ✅ ManagedMethodDefinition (4 fields)

Result: 5/5 models valid
```

**Tests**:
- `test_base_envelope_structure` - Validates BaseRequest/BaseResponse
- `test_method_definition_models` - Tests all method definition Pydantic models
- `test_method_definition_instantiation` - Creates valid instances with test data
- `test_operation_models_exist` - Verifies 6 operation model files importable
- `test_registry_api_type_hints` - Checks 10+ registry API functions

---

### 3. YAML Validation Tests (`test_yaml_validation.py`)

**What it validates**:
- `methods_inventory_v1.yaml` is parseable
- Header structure (version, schema_version, description)
- All methods have required fields
- Classification values are valid
- No duplicate method names
- Business rules are complete
- Model references properly formatted

**Output**:
```
YAML FILE EXISTENCE TEST
================================================================================
  ✅ File exists: config/methods_inventory_v1.yaml
  ✅ File is parseable YAML

METHOD SCHEMA VALIDATION TEST
================================================================================
  ✅ workspace.casefile.create_casefile
  ✅ workspace.casefile.get_casefile
  [...]
  ✅ automation.tool_execution.process_tool_request

Result: 26/26 methods valid
Success Rate: 100.00%

📊 Model Coverage:
  - Methods with models: 25/26
  - Missing models: 1
```

**Tests**:
- `test_yaml_file_exists_and_parseable` - Basic YAML validity
- `test_yaml_header_structure` - Validates metadata fields
- `test_all_methods_have_required_fields` - Checks 8 required fields per method
- `test_no_duplicate_method_names` - Ensures unique method names
- `test_classification_values_valid` - Validates against allowed values
- `test_model_references_format` - Checks request/response model references
- `test_method_naming_convention` - Verifies {domain}.{subdomain}.{capability}_{name}
- `test_business_rules_completeness` - Checks 4 required business rule fields

---

## Reports

All test runs generate detailed reports in `test_reports/`:

### JSON Report (for analysis)
```json
{
  "timestamp": "2025-10-06T15:30:00",
  "project_root": "/path/to/my-tiny-data-collider",
  "suites": [
    {
      "name": "Code Integrity",
      "file": "test_code_integrity.py",
      "exit_code": 0,
      "status": "PASSED"
    },
    ...
  ]
}
```

### Text Summary (for debugging)
```
================================================================================
SYSTEM VALIDATION SUMMARY REPORT
================================================================================
Timestamp: 2025-10-06T15:30:00
Project: my-tiny-data-collider

Total Test Suites: 3
Passed: 3
Failed: 0
Success Rate: 100.00%

--------------------------------------------------------------------------------
SUITE DETAILS
--------------------------------------------------------------------------------
✅ Code Integrity                PASSED
✅ Type Validation               PASSED
✅ YAML Validation               PASSED

================================================================================
🎉 ALL VALIDATION TESTS PASSED!
System is ready for commit and deployment.
================================================================================
```

---

## What Gets Validated

### Code Integrity ✅
- [x] All 47 Python files have valid syntax
- [x] 6 critical modules importable (method_definition, method_registry, etc.)
- [x] 6 service classes accessible (CasefileService, GmailClient, etc.)
- [x] No broken imports or circular dependencies

### Type Validation ✅
- [x] BaseRequest[T] and BaseResponse[T] structure intact
- [x] 5 method definition Pydantic models valid
- [x] ManagedMethodDefinition can be instantiated
- [x] 6 operation model files importable (casefile_ops, gmail_ops, etc.)
- [x] 10+ registry API functions have type hints

### YAML Validation ✅
- [x] methods_inventory_v1.yaml is parseable
- [x] 26 methods have complete schema (8 required fields each)
- [x] No duplicate method names
- [x] Classification values match allowed values (domain, capability, etc.)
- [x] 25/26 methods have model references (83% coverage)
- [x] Business rules complete for all methods
- [x] Method naming convention followed

---

## When to Run

**Always run before**:
- Committing refactoring changes
- Merging to main/develop branch
- Creating release tags
- Deploying to production

**Run after**:
- Adding new methods to YAML
- Modifying Pydantic models
- Changing service class structures
- Updating method registry code
- Large-scale refactoring

---

## Integration with CI/CD

Add to `.github/workflows/validation.yml`:
```yaml
name: System Validation

on: [push, pull_request]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt
      - run: python tests/system_validation/run_all_validation.py
```

---

## Troubleshooting

### Import Errors
If you see import errors:
```bash
# Verify Python path
export PYTHONPATH="${PYTHONPATH}:${PWD}/src"

# Or use absolute imports
python -m pytest tests/system_validation/test_code_integrity.py
```

### YAML Not Found
```bash
# Verify you're in project root
pwd  # Should show /path/to/my-tiny-data-collider

# Check file exists
ls -la config/methods_inventory_v1.yaml
```

### Pydantic Version Issues
```bash
# Check Pydantic version (requires v2.x)
pip show pydantic

# Upgrade if needed
pip install --upgrade pydantic
```

---

## Exit Codes

- `0` - All tests passed ✅
- `1` - One or more test suites failed ❌

Use in CI/CD to block merges on failure:
```bash
python tests/system_validation/run_all_validation.py || exit 1
```

---

## Future Enhancements

**Planned additions**:
- [ ] Performance benchmarks (method execution time)
- [ ] Security validation (permission checks)
- [ ] Database schema validation
- [ ] API contract testing (request/response matching)
- [ ] Documentation completeness check
- [ ] Deprecation warning detection
- [ ] Model coverage gap analysis
- [ ] Integration test coverage metrics

---

## Files

```
tests/system_validation/
├── README.md                      [This file]
├── run_all_validation.py          [Test runner + report generator]
├── test_code_integrity.py         [Syntax, imports, modules]
├── test_type_validation.py        [Pydantic models, type hints]
└── test_yaml_validation.py        [YAML schema, data integrity]
```

---

**Created**: 2025-10-06  
**Phase**: 13 (Method Registry Infrastructure)  
**Purpose**: System-wide validation before commit/deployment
