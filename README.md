# Tiny Data Collider

**Last Updated:** 2025-10-17  
**Status:** 100% Complete (MVP + Optional Enhancements + Test Suite Validated)

FastAPI data integration platform with Pydantic validation, Google Workspace integration, casefile management, and YAML-driven tool orchestration.

---

## Quick Start

**Install:** `pip install -r requirements.txt`  
**Test:** `pytest tests/unit/ -q` (179 passing, 0 warnings)  
**Status:** `ROUNDTRIP_ANALYSIS.md` → All phases complete, test suite validated

---

## Current Status

**Phase 1-7:** Complete (80.5h actual vs 95.5h estimated, 16% efficiency gain)
- **30 custom types** (10 IDs + 7 strings + 5 numbers + 5 timestamps + 3 URLs/emails)
- **12 validators** (zero duplication pattern)
- **16 model files enhanced** (95+ fields)
- **179 unit tests passing** (0 warnings, 0 failures)
- **11 integration tests passing** (MVP user journeys validated)
- **28 methods** auto-registered with `@register_service_method`
- **Test suite architecture validated** - pytest 8.x compatibility, import patterns fixed

---

## Documentation

**Primary:**
- `ROUNDTRIP_ANALYSIS.md` - Complete system state
- `docs/VALIDATION_PATTERNS.md` - 30 types + 12 validators guide (870 lines)
- `.github/copilot-instructions.md` - AI session startup

**Cross-project:** Validation patterns also in `my-tiny-toolset/REFERENCE/SUBJECTS/shared-patterns/`

---

## Testing

```bash
# Quick test (summary only)
pytest tests/unit/ -q

# Verbose unit tests
pytest tests/unit/ -v

# Integration tests
pytest tests/integration/ -v

# With coverage
pytest --cov=src --cov-report=html

# Registry validation
python scripts/validate_registries.py --strict
```

**Current Results:**
- Unit Tests: 179 passed, 0 warnings, 0 failures (2.76s)
- Integration Tests: 11 passed, 18 skipped, 5 failed (tool registry issues - expected)

---

## Validation Framework

### Custom Types (30 total)
```python
from src.pydantic_models.base.custom_types import (
    CasefileId, ShortString, IsoTimestamp, UserId, GmailMessageId
)
```

### Validators (12 total)
```python
from src.pydantic_models.base.validators import validate_timestamp_order

@model_validator(mode='after')
def validate_timestamps(self) -> 'Model':
    validate_timestamp_order(self.created_at, self.updated_at, 'created_at', 'updated_at')
    return self
```

**Full guide:** `docs/VALIDATION_PATTERNS.md`

---

**Repository:** https://github.com/MSD21091969/my-tiny-data-collider.git  
**Toolset:** https://github.com/MSD21091969/my-tiny-toolset.git
