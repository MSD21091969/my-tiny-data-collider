# GitHub Copilot Chore List

**Project:** MDS Objects API  
**Date Created:** October 1, 2025  
**Status:** Ready for automated execution  
**Focus:** Code quality checks, documentation gaps, test prep, environment validation

---

## Overview

This document contains **tactical preparation chores** for GitHub Copilot to execute autonomously. These are NOT feature implementations - they are checks, audits, documentation gaps, test scaffolding, and environment validation tasks that prepare for strategic work.

**Related Documents:**
- `docs/SOLID_INTEGRATION_PLAN.md` - Strategy context (not implemented here)
- `docs/pydantic toolengineering.txt` - Vision context (not implemented here)
- `.github/copilot-instructions.md` - Project guidelines

---

## Chore Progress Tracker

| # | Title | Type | Effort | Status | Branch | PR | Completed |
|---|-------|------|--------|--------|--------|----|-----------| 
| 1 | Audit all imports for unused/circular deps | Check | 30m | ⏳ | - | - | - |
| 2 | Validate all Pydantic models have examples | Check | 1h | ⏳ | - | - | - |
| 3 | Check test coverage gaps | Check | 30m | ⏳ | - | - | - |
| 4 | Verify environment variable documentation | Check | 30m | ⏳ | - | - | - |
| 5 | Create test fixtures for common scenarios | Prep | 1h | ⏳ | - | - | - |
| 6 | Document API error response formats | Doc | 1h | ⏳ | - | - | - |
| 7 | Verify Firestore indexes are documented | Check | 30m | ⏳ | - | - | - |
| 8 | Create pytest markers for test categories | Prep | 30m | ⏳ | - | - | - |
| 9 | Audit logging consistency across services | Check | 1h | ⏳ | - | - | - |
| 10 | Verify all routes have proper docstrings | Check | 1h | ⏳ | - | - | - |

**Status Legend:** ⏳ Not Started | 🚧 In Progress | ✅ Completed | ❌ Blocked  
**Type Legend:** Check (audit/validation) | Prep (scaffolding) | Doc (documentation)

---

## Chore #1: Audit All Imports for Unused/Circular Dependencies

**Type:** Check  
**Effort:** 30 minutes  
**Files to Inspect:** `src/**/*.py`

### Description
Scan all Python files in `src/` to identify:
1. Unused imports (imported but never referenced)
2. Circular import patterns (A imports B, B imports A)
3. Duplicate imports (same module imported multiple times)
4. Wildcard imports (`from x import *`)

### Requirements
- Use `pylint --disable=all --enable=unused-import,cyclic-import` or similar
- Generate a report listing violations by file
- Do NOT fix issues - just report them
- Output format: Markdown table with file path, line number, issue type, description

### Acceptance Criteria
- [ ] Report generated in `docs/IMPORT_AUDIT_REPORT.md`
- [ ] All `src/**/*.py` files scanned
- [ ] Table includes: File | Line | Type | Description
- [ ] Summary counts by issue type at top
- [ ] No false positives (manual spot-check 5 random findings)

### Test Script
```bash
# Run audit
pylint --disable=all --enable=unused-import,cyclic-import src/ > audit.txt

# Verify report exists
test -f docs/IMPORT_AUDIT_REPORT.md

# Check report has content
grep -q "| File | Line | Type |" docs/IMPORT_AUDIT_REPORT.md
```

### Dependencies
- None (first chore)

---

## Chore #2: Validate All Pydantic Models Have Examples

**Type:** Check  
**Effort:** 1 hour  
**Files to Inspect:** `src/pydantic_models/**/*.py`

### Description
Check every Pydantic model class to ensure it has a `model_config` with example data for API documentation. OpenAPI/FastAPI uses these for interactive docs.

### Requirements
- Find all classes inheriting from `BaseModel`
- Check for `model_config = ConfigDict(json_schema_extra={"example": {...}})`
- Generate report of models missing examples
- Do NOT add examples - just report missing ones

### Acceptance Criteria
- [ ] Report generated in `docs/PYDANTIC_EXAMPLES_AUDIT.md`
- [ ] All models in `src/pydantic_models/` checked
- [ ] Table includes: File | Class Name | Has Example | Fields Count
- [ ] Summary: X models with examples, Y without
- [ ] No false positives (check 3 "missing" cases manually)

### Test Script
```bash
# Run check
python scripts/audit_pydantic_examples.py

# Verify report
test -f docs/PYDANTIC_EXAMPLES_AUDIT.md

# Check format
grep -q "| File | Class Name | Has Example |" docs/PYDANTIC_EXAMPLES_AUDIT.md
```

### Example Script Stub
```python
# scripts/audit_pydantic_examples.py
import ast
from pathlib import Path

def find_models_without_examples():
    models_dir = Path("src/pydantic_models")
    results = []
    
    for py_file in models_dir.rglob("*.py"):
        # Parse AST, find BaseModel classes, check for model_config
        # Append to results
        pass
    
    return results

if __name__ == "__main__":
    results = find_models_without_examples()
    # Write to docs/PYDANTIC_EXAMPLES_AUDIT.md
```

### Dependencies
- None

---

## Chore #3: Check Test Coverage Gaps

**Type:** Check  
**Effort:** 30 minutes  
**Files to Inspect:** `tests/**/*.py` vs `src/**/*.py`

### Description
Generate pytest coverage report and identify modules/functions with <80% coverage. Do NOT write tests - just report gaps.

### Requirements
- Run `pytest --cov=src --cov-report=term-missing`
- Extract modules with <80% coverage
- List specific uncovered line ranges
- Generate report in Markdown

### Acceptance Criteria
- [ ] Report generated in `docs/TEST_COVERAGE_GAPS.md`
- [ ] Coverage report run successfully
- [ ] Table includes: Module | Coverage % | Uncovered Lines | Priority
- [ ] Priority assigned: HIGH (<50%), MEDIUM (50-79%), LOW (80%+)
- [ ] Summary: X modules need attention

### Test Script
```bash
# Run coverage
pytest --cov=src --cov-report=term-missing --cov-report=json

# Verify report exists
test -f docs/TEST_COVERAGE_GAPS.md

# Check has priority column
grep -q "Priority" docs/TEST_COVERAGE_GAPS.md
```

### Dependencies
- Requires `pytest-cov` installed

---

## Chore #4: Verify Environment Variable Documentation

**Type:** Check  
**Effort:** 30 minutes  
**Files to Inspect:** `src/**/*.py`, `docs/**/*.md`, `.env.example`

### Description
Find all environment variables used in code (`os.getenv()`, `os.environ[]`) and check if they're documented in `.env.example` or README. Report undocumented variables.

### Requirements
- Scan for `os.getenv`, `os.environ`, `config.get()`
- Extract variable names
- Check if listed in `.env.example` or `docs/` files
- Generate report of undocumented vars

### Acceptance Criteria
- [ ] Report generated in `docs/ENV_VAR_AUDIT.md`
- [ ] All environment variables found in code
- [ ] Table includes: Variable | File | Line | Documented? | Has Default?
- [ ] List of undocumented vars at top
- [ ] Suggestions for `.env.example` additions

### Test Script
```bash
# Run audit
python scripts/audit_env_vars.py

# Verify report
test -f docs/ENV_VAR_AUDIT.md

# Check has undocumented section
grep -q "Undocumented Variables" docs/ENV_VAR_AUDIT.md
```

### Dependencies
- None

---

## Chore #5: Create Test Fixtures for Common Scenarios

**Type:** Prep  
**Effort:** 1 hour  
**Files to Create:** `tests/fixtures/common.py`

### Description
Create pytest fixtures for frequently used test data: sample users, casefiles, tool sessions, contexts. This reduces boilerplate in tests.

### Requirements
- Create `tests/fixtures/common.py`
- Define fixtures: `sample_user`, `sample_casefile`, `sample_tool_session`, `sample_mds_context`
- Use Pydantic models from `src/pydantic_models/`
- Add docstrings explaining each fixture
- Follow existing pytest fixture patterns

### Acceptance Criteria
- [ ] File created: `tests/fixtures/common.py`
- [ ] At least 5 fixtures defined
- [ ] Each fixture has docstring
- [ ] Fixtures use proper Pydantic models
- [ ] Example test file uses fixtures successfully
- [ ] Run `pytest tests/fixtures/test_common_fixtures.py` passes

### Test Script
```bash
# Verify file exists
test -f tests/fixtures/common.py

# Check fixtures are importable
python -c "from tests.fixtures.common import sample_user, sample_casefile"

# Run example test
pytest tests/fixtures/test_common_fixtures.py -v
```

### Example Code
```python
# tests/fixtures/common.py
import pytest
from src.pydantic_models.casefile.models import Casefile

@pytest.fixture
def sample_casefile() -> Casefile:
    """Provides a sample casefile for testing."""
    return Casefile(
        id="251001_ABC123",
        user_id="test_user_123",
        title="Sample Investigation",
        description="Test casefile for unit tests",
        created_at="2025-10-01T10:00:00",
        sessions=[]
    )

# ... more fixtures
```

### Dependencies
- None

---

## Chore #6: Document API Error Response Formats

**Type:** Doc  
**Effort:** 1 hour  
**Files to Create:** `docs/API_ERROR_RESPONSES.md`

### Description
Document the standard error response format for all API endpoints. Check current error handling in routers and document the actual structure returned.

### Requirements
- Inspect error handling in `src/pydantic_api/routers/*.py`
- Document HTTP status codes used
- Document error response JSON structure
- Provide examples for each error type
- Include validation error format

### Acceptance Criteria
- [ ] File created: `docs/API_ERROR_RESPONSES.md`
- [ ] Documents HTTP status codes (400, 401, 404, 500, etc.)
- [ ] Shows JSON structure for each error type
- [ ] Includes 3+ real examples
- [ ] Documents validation error format (Pydantic errors)
- [ ] Table of status codes with descriptions

### Test Script
```bash
# Verify file exists
test -f docs/API_ERROR_RESPONSES.md

# Check has status codes
grep -q "400" docs/API_ERROR_RESPONSES.md
grep -q "404" docs/API_ERROR_RESPONSES.md
grep -q "500" docs/API_ERROR_RESPONSES.md

# Check has JSON examples
grep -q '```json' docs/API_ERROR_RESPONSES.md
```

### Example Content
```markdown
# API Error Response Formats

## Standard Error Structure

```json
{
  "detail": "Human-readable error message",
  "error_code": "ERROR_TYPE",
  "timestamp": "2025-10-01T10:00:00Z"
}
```

## Status Codes

| Code | Meaning | When Used |
|------|---------|-----------|
| 400 | Bad Request | Invalid parameters |
| 401 | Unauthorized | Missing/invalid JWT |
| 404 | Not Found | Resource doesn't exist |
| 500 | Internal Error | Server-side failure |
```

### Dependencies
- None

---

## Chore #7: Verify Firestore Indexes Are Documented

**Type:** Check  
**Effort:** 30 minutes  
**Files to Inspect:** `src/persistence/firestore/*.py`, `docs/**/*.md`

### Description
Find all Firestore queries that use multiple fields (compound queries) and verify indexes are documented. Firestore requires composite indexes for multi-field queries.

### Requirements
- Scan for `.where()` chained queries
- Identify compound queries (2+ fields)
- Check if indexes documented in `docs/` or code comments
- Generate report of undocumented index needs

### Acceptance Criteria
- [ ] Report generated in `docs/FIRESTORE_INDEXES_AUDIT.md`
- [ ] All compound queries identified
- [ ] Table includes: Collection | Fields | Query File | Line | Documented?
- [ ] Suggested `firestore.indexes.json` snippet for undocumented indexes
- [ ] Summary count of required indexes

### Test Script
```bash
# Run audit
python scripts/audit_firestore_indexes.py

# Verify report
test -f docs/FIRESTORE_INDEXES_AUDIT.md

# Check has suggested indexes
grep -q "firestore.indexes.json" docs/FIRESTORE_INDEXES_AUDIT.md
```

### Dependencies
- None

---

## Chore #8: Create Pytest Markers for Test Categories

**Type:** Prep  
**Effort:** 30 minutes  
**Files to Modify:** `pytest.ini`, `tests/**/*.py`

### Description
Define pytest markers to categorize tests (unit, integration, firestore, mock, slow). This allows selective test runs like `pytest -m "not slow"`.

### Requirements
- Add markers to `pytest.ini`
- Document each marker's purpose
- Add example marker usage to 3 test files
- Update README with marker usage examples

### Acceptance Criteria
- [ ] Markers defined in `pytest.ini`: unit, integration, firestore, mock, slow
- [ ] Each marker has description in `pytest.ini`
- [ ] At least 3 test files use markers with `@pytest.mark.X`
- [ ] README updated with `pytest -m` examples
- [ ] Run `pytest -m unit` executes only unit tests
- [ ] Run `pytest -m "not firestore"` skips Firestore tests

### Test Script
```bash
# Check markers defined
grep -q "markers =" pytest.ini

# Verify marker works
pytest -m unit --collect-only | grep -q "test_"

# Check README updated
grep -q "pytest -m" README.md
```

### Example Code
```ini
# pytest.ini additions
[pytest]
markers =
    unit: Unit tests (fast, no external deps)
    integration: Integration tests (slower, may use mocks)
    firestore: Tests requiring Firestore connection
    mock: Tests using mock backends
    slow: Tests that take >5 seconds
```

```python
# tests/test_example.py
import pytest

@pytest.mark.unit
def test_fast_function():
    assert 1 + 1 == 2

@pytest.mark.firestore
@pytest.mark.slow
def test_firestore_query():
    # ... slow Firestore test
    pass
```

### Dependencies
- None

---

## Chore #9: Audit Logging Consistency Across Services

**Type:** Check  
**Effort:** 1 hour  
**Files to Inspect:** `src/*service/*.py`, `src/pydantic_api/*.py`

### Description
Check all service and API files for logging usage. Ensure consistent patterns: proper log levels, structured data, no sensitive info logged.

### Requirements
- Scan for `logger.info()`, `logger.error()`, etc.
- Check if loggers named consistently (`__name__`)
- Identify logs that might leak sensitive data (tokens, passwords)
- Check for missing error logs in exception handlers
- Generate report of inconsistencies

### Acceptance Criteria
- [ ] Report generated in `docs/LOGGING_AUDIT.md`
- [ ] All service files checked
- [ ] Table includes: File | Issue Type | Line | Current Code | Suggestion
- [ ] Issue types: inconsistent level, missing context, sensitive data, missing error log
- [ ] Summary: X issues by type
- [ ] Suggested logging standards section

### Test Script
```bash
# Run audit
python scripts/audit_logging.py

# Verify report
test -f docs/LOGGING_AUDIT.md

# Check has issue types
grep -q "Issue Type" docs/LOGGING_AUDIT.md

# Check has standards section
grep -q "Logging Standards" docs/LOGGING_AUDIT.md
```

### Dependencies
- None

---

## Chore #10: Verify All Routes Have Proper Docstrings

**Type:** Check  
**Effort:** 1 hour  
**Files to Inspect:** `src/pydantic_api/routers/*.py`

### Description
Check all FastAPI route functions for proper docstrings. FastAPI uses these for OpenAPI docs, so they should describe the endpoint, parameters, and responses.

### Requirements
- Find all `@router.get`, `@router.post`, etc. decorated functions
- Check if docstring exists and is non-empty
- Check if docstring mentions parameters and return value
- Generate report of routes missing proper docs

### Acceptance Criteria
- [ ] Report generated in `docs/ROUTE_DOCSTRINGS_AUDIT.md`
- [ ] All routes in `src/pydantic_api/routers/` checked
- [ ] Table includes: File | Route | HTTP Method | Has Docstring | Quality Score
- [ ] Quality Score: 3 (good), 2 (partial), 1 (missing/poor)
- [ ] Example good docstring provided in report
- [ ] Summary: X routes need improvement

### Test Script
```bash
# Run audit
python scripts/audit_route_docstrings.py

# Verify report
test -f docs/ROUTE_DOCSTRINGS_AUDIT.md

# Check has quality scores
grep -q "Quality Score" docs/ROUTE_DOCSTRINGS_AUDIT.md

# Check has example
grep -q "Example Good Docstring" docs/ROUTE_DOCSTRINGS_AUDIT.md
```

### Example Good Docstring
```python
@router.post("/casefiles", response_model=CreateCasefileResponse)
async def create_casefile(request: CreateCasefileRequest):
    """
    Create a new casefile for investigation tracking.
    
    Args:
        request: Casefile creation details including title and description
        
    Returns:
        CreateCasefileResponse with the new casefile ID and metadata
        
    Raises:
        400: Invalid request parameters
        401: Unauthorized (missing/invalid JWT)
        500: Server error during creation
    """
    # ... implementation
```

### Dependencies
- None

---

## Execution Guidelines for GitHub Copilot

### Workflow
1. Pick a chore (start with #1, proceed sequentially)
2. Create branch: `git checkout -b chore/N-short-description`
3. Execute the chore (follow requirements exactly)
4. Run test script to verify acceptance criteria
5. Commit: `git commit -m "chore: [Title from chore]"`
6. Push: `git push origin chore/N-short-description`
7. Update this file: mark status as ✅, add branch name, date
8. Create PR linking to this file

### Commit Message Format
```
chore: [Title from chore table]

- [Acceptance criteria 1]
- [Acceptance criteria 2]
- [Acceptance criteria 3]

Refs: .github/COPILOT_CHORES.md#chore-N
```

### Important Notes
- **DO NOT** implement features - only prep/check/doc tasks
- **DO NOT** fix issues found - just report them
- **DO** follow project patterns in `.github/copilot-instructions.md`
- **DO** run test scripts before committing
- **DO** update the progress tracker table in this file

---

## Success Metrics

After all chores complete:
- [ ] 10 audit reports generated in `docs/`
- [ ] Test infrastructure improved (fixtures, markers)
- [ ] Documentation gaps filled
- [ ] Code quality baseline established
- [ ] Ready for strategic feature work
- [ ] All chores marked ✅ in tracker

---

**Last Updated:** October 1, 2025  
**Next Review:** After 5 chores completed
