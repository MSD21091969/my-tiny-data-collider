# Tiny Data Collider

**Last Updated:** 2025-10-16  
**Status:** 100% Complete (MVP + Optional Enhancements)

FastAPI data integration platform with Pydantic validation, Google Workspace integration, casefile management, and YAML-driven tool orchestration.

---

## Quick Start

**Install:** `pip install -r requirements.txt`  
**Test:** `python -m pytest tests/ -v --ignore=tests/integration/test_tool_execution_modes.py --ignore=tests/integration/test_tool_method_integration.py`  
**Status:** `ROUNDTRIP_ANALYSIS.md` → 236/236 Pydantic tests passing

---

## Current Status

**Phase 1-5:** Complete (74.5h actual vs 95.5h estimated, 22% efficiency gain)
- **30 custom types** (10 IDs + 7 strings + 5 numbers + 5 timestamps + 3 URLs/emails)
- **12 validators** (zero duplication pattern)
- **16 model files enhanced** (95+ fields)
- **236/236 tests passing**
- **34 methods** auto-registered with `@register_service_method`

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
python -m pytest tests/pydantic_models/ -v              # 236 Pydantic tests
python scripts/validate_registries.py --strict          # Registry validation
```

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
