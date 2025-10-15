# AI Instructions - Tiny Data Collider

## 1. What is "Tiny Data Collider"

**What:**
- FastAPI data integration platform with Pydantic validation
- Google Workspace integration (Gmail, Drive, Sheets)
- Casefile management, tool execution orchestration
- Phase 1 complete: 20+ custom types, 9 validators, 263 tests

**Ultimate Purpose:**
- **Tool Engineering Platform**: Build written/generated scripts for simple to advanced problem-solving
- **YAML-Driven Architecture**: Generate code/models/tools/parameters from Pydantic models
- **Agent Toolchain**: Premium agent tools + user tools for data workflows
- **Data Cycle**: Transfer → Transformation → Analysis → RAG → Tuning (iterative)
- **Session Management**: Structured chat sessions with context, goals, audit trail

**Key Documents:**
- `README.md` - Project overview, quick start
- `ROUNDTRIP_ANALYSIS.md` - Complete system state + action items ⭐ GO-TO FILE
- `docs/VALIDATION_PATTERNS.md` - Custom types & validators guide
- `scripts/generate_method_tools.py` - YAML tool generator (411 lines)

**Two-Repository Context:**
- **This repo (my-tiny-data-collider)**: Application code, models, services, tests
- **Toolset repo (my-tiny-toolset)**: Analysis tools + knowledge base (REFERENCE/, WORKSPACE/, CONFIGS/)
- **Toolset instructions**: `C:\Users\HP\my-tiny-toolset\.github\copilot-instructions.md` - Read for tool usage patterns
- **Integration**: Application uses toolset for code analysis, not vice versa
- **Knowledge Flow**: Patterns discovered here → Captured in toolset REFERENCE/ folders

---

## 2. Practices

**Communication:**
- Short, dry, no emojis (developers, not managers)
- Report during work, summarize at completion
- Update existing documents only (no new files without approval)

**Documentation:**
- Single source of truth: No duplicate information
- Update README.md for architectural changes
- Date stamp all major docs: `**Last Updated:** YYYY-MM-DD`

**Code Maintenance:**
- Use custom types from `src/pydantic_models/base/custom_types.py`
- Use validators from `src/pydantic_models/base/validators.py`
- Run validation: `python scripts/validate_registries.py --strict`
- Run tests: `python -m pytest tests/pydantic_models/ -v`

**Knowledge Capture:**
- Pattern discovery → Document in toolset `WORKSPACE/FIELDNOTES.md`
- Validate pattern → Test across use cases
- Move validated knowledge → Toolset `REFERENCE/SUBJECTS/<domain>/`
- Update folder README with date stamp

---

## 3. Validation Framework

### Custom Types (20+ types)

**Location:** `src/pydantic_models/base/custom_types.py`

```python
from src.pydantic_models.base.custom_types import (
    CasefileId, ShortString, IsoTimestamp, PositiveInt
)

class MyModel(BaseModel):
    id: CasefileId              # UUID validation + lowercase
    title: ShortString          # 1-200 characters
    created_at: IsoTimestamp    # ISO 8601 format
```

**Categories:** IDs, Strings, Numbers, Email/URL, Timestamps, Collections

### Reusable Validators (9 functions)

**Location:** `src/pydantic_models/base/validators.py`

```python
from src.pydantic_models.base.validators import validate_timestamp_order

@model_validator(mode='after')
def validate_model(self) -> 'MyModel':
    validate_timestamp_order(self, 'created_at', 'updated_at')
    return self
```

**Functions:** timestamp_order, at_least_one, mutually_exclusive, conditional_required, list_not_empty, list_unique, range, string_length, depends_on

**Full Guide:** `docs/VALIDATION_PATTERNS.md`

---

## 4. Toolset Usage

**Environment:** `$env:MY_TOOLSET = "C:\Users\HP\my-tiny-toolset\TOOLSET"`

| Tool | Purpose | Command |
|------|---------|---------|
| `code_analyzer.py` | Quick structure | `python $env:MY_TOOLSET\code_analyzer.py . --json` |
| `version_tracker.py` | Full analysis | `python $env:MY_TOOLSET\version_tracker.py . --version X` |
| `mapping_analyzer.py` | Relationships | `python $env:MY_TOOLSET\mapping_analyzer.py . --html` |

**Outputs:** `.tool-outputs/` (gitignored)

---

## 5. Testing & Validation

### Registry Validation
```powershell
# Full validation
python scripts/validate_registries.py --strict --verbose

# Parameter mapping only
python scripts/validate_parameter_mappings.py --verbose
```

### Test Suites
```powershell
# All tests (263)
python -m pytest tests/ -v

# Pydantic tests (116)
python -m pytest tests/pydantic_models/ -v

# Registry tests (43)
python -m pytest tests/registry/ -v

# Integration tests (104)
python -m pytest tests/integration/ -v
```

---

## 6. Tool Generation & YAML Workflow

### Generate Tool YAMLs
```powershell
# Generate all 34 tool YAMLs from methods inventory
python scripts/generate_method_tools.py

# Dry-run (show what would be generated)
python scripts/generate_method_tools.py --dry-run

# Verbose output
python scripts/generate_method_tools.py --verbose
```

**Pattern:** R-A-R (Request-Action-Response) - Parameters extracted from `payload` field  
**Output:** `config/methodtools_v1/*.yaml` (34 files)  
**Validation:** Type normalization, generic detection (list[str] → array)

### Test YAML Tools
```powershell
# Load and inspect tool
python -c "from pydantic_ai_integration.tool_decorator import register_tools_from_yaml, MANAGED_TOOLS; register_tools_from_yaml(); tool = MANAGED_TOOLS.get('create_casefile_tool'); print(f'Tool: {tool.name}, Method: {tool.method_name}')"
```

**Proven:** YAMLs work for actual CRUD (dry-run execution successful)  
**Runtime:** Requires Firestore/Redis infrastructure for live execution

---

## 7. Session Startup & Quick Reference

**Every new session:**

1. Set environment: `$env:MY_TOOLSET = "C:\Users\HP\my-tiny-toolset\TOOLSET"`
2. Check toolset context: `C:\Users\HP\my-tiny-toolset\.github\copilot-instructions.md`
3. Check branch: `git status`
4. Read context: `ROUNDTRIP_ANALYSIS.md` for current system state
5. Quick validation: `python scripts/validate_registries.py --strict`
6. Run tests: `python -m pytest tests/ -v --tb=short` (263 passing)

**Phase Status:**
- ✅ Phase 1 Complete: Custom types, validators, generator script, all tests passing
- 🚀 Ready for Phase 2: Google Workspace warnings (8) + Apply custom types (~60 models)

---

**Last Updated:** 2025-10-15
