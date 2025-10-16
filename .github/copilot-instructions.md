# AI Instructions - Tiny Data Collider

**Last Updated:** 2025-10-16

---

## 1. Repository Overview

**This is the APPLICATION repository** - FastAPI data integration platform with Pydantic validation, Google Workspace integration (Gmail/Drive/Sheets), casefile management, and tool execution orchestration using YAML-driven architecture.

**Your role as Code Assistant:**
1. Build and enhance FastAPI application code in this repository
2. Use meta-tools from separate toolset repository for analysis (not vice versa)
3. Follow validation framework (custom types + validators) in all Pydantic models
4. Execute tasks defined in `.vscode/tasks.json` (validation, tests, analysis)
5. Consult `ROUNDTRIP_ANALYSIS.md` for current system state and action plan

**Two-repository architecture:**
- **my-tiny-data-collider** (THIS REPO): Application code, models, services, tests, 34 service methods, 37 Pydantic models
- **my-tiny-toolset** (SEPARATE): 17 meta-tools for code analysis + knowledge base → See `C:\Users\HP\my-tiny-toolset\.github\copilot-instructions.md`

**Key documents in THIS repo:**
- `ROUNDTRIP_ANALYSIS.md` - Complete system state, action plan, progress tracking ⭐ PRIMARY REFERENCE
- `docs/VALIDATION_PATTERNS.md` - Custom types & validators reference
- `README.md` - Project overview, quick start guide
- `.vscode/tasks.json` - Executable tasks for validation, testing, analysis

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

**Method Registration (Phase 10):**
- Add `@register_service_method` decorator to new service methods
- Methods auto-register at import (no YAML edits needed)
- YAML (`config/methods_inventory_v1.yaml`) is documentation-only
- Decorator extracts classification from decorator parameters, models from signature

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

**Full Guide:** `docs/VALIDATION_PATTERNS.md` (Phase 1 reference)

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

## 7. Session Startup Checklist

**Every new session, execute in order:**

1. **Set toolset environment** → `$env:MY_TOOLSET = "C:\Users\HP\my-tiny-toolset\TOOLSET"`
2. **Check Git branch** → `git status` (should be on `feature/develop`)
3. **Read system state** → Open `ROUNDTRIP_ANALYSIS.md` for current progress and action plan
4. **Validate registries** → Run task "Validate Registries" OR `python scripts/validate_registries.py --strict`
5. **Run test suite** → Run task "Run Tests" OR `python -m pytest tests/ -v --tb=short` (expect 263/263 passing)
6. **Review tasks** → Check `.vscode/tasks.json` for available executable tasks

**Available tasks** (use VS Code Task Runner or `run_task` tool):
- `Validate Registries` - Full registry + parameter validation
- `Run Tests` - Complete test suite (263 tests)
- `Quick Analysis` - Run code_analyzer.py on current codebase
- `Full Analysis` - Run version_tracker.py + mapping_analyzer.py
- `Pre-commit Checks` - Sequential validation + tests before commit

**Current system status:**
- ✅ **263/263 tests passing** (116 pydantic + 43 registry + 104 integration)
- ✅ **34 service methods registered** with `@register_service_method` decorator
- ✅ **37 Pydantic models validated** (100% schema valid, 9 files enhanced with custom types)
- ✅ **Phase 1-2 complete** (52h): Validation foundation + decorator registration
- 📋 **Remaining work**: See ROUNDTRIP_ANALYSIS.md Actions 13, 16-18, 21-22 (24.5h estimated)

**Toolset integration:**
- Toolset repo has separate `.github/copilot-instructions.md` with 17 meta-tool documentation
- Use toolset tools FOR analysis, not IN the application code
- Knowledge flow: Discover patterns here → Capture in toolset `REFERENCE/` folders

---
