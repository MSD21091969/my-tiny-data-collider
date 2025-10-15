# AI Instructions - Tiny Data Collider

**Last Updated:** 2025-10-14

## 0. Session Startup Protocol

**Every new session:**

1. **Set environment:** `$env:MY_TOOLSET = "C:\Users\HP\my-tiny-toolset\TOOLSET"`
2. **Read toolset context:** Check `C:\Users\HP\my-tiny-toolset\.github\copilot-instructions.md` for toolset usage patterns
3. **Check branch:** `git status` - Confirm correct branch
4. **Quick validation:** `python scripts/validate_registries.py --strict` (expect ~34 drift/mapping issues - NORMAL)
5. **Run tests:** `python -m pytest tests/ -v --tb=short` - Verify 263 passing (116 pydantic + 43 registry + 104 integration tests)
6. **Verify test outputs:** Check test artifacts exist:
   - `tests/reports/` - Excel report (1 file: `test_validation_report.xlsx`)
   - `tests/reports/` - JSON files (2 files: `test_results.json`, `test_validation_summary.json`)
   - `tests/reports/` - CSV files (4 files: `models.csv`, `methods.csv`, `tools.csv`, `validation_errors.csv`)
7. **Review context:** Read `ROUNDTRIP_ANALYSIS.md` for current system state
8. **Report status:** Branch, validation issues, tests passing, artifacts present

**Standard opening:**
```
Branch: <branch-name>
Validation: ~34 issues (drift + mapping - expected)
Tests: 263/263 passing ✓
Artifacts: Excel (1), JSON (2), CSV (4) ✓
Action Items: [From ROUNDTRIP_ANALYSIS.md]
Ready. What are we working on?
```

**Note:** Validation script is faster than full test run for quick checks. Use tests for comprehensive verification. Current test suite includes additional integration tests beyond original 159 target.

---

## 1. What is "Tiny Data Collider"

**What:**
- FastAPI data integration platform with Pydantic validation
- Google Workspace integration (Gmail, Drive, Sheets)
- Casefile management, tool execution orchestration
- Phase 1 complete: 20+ custom types, 9 validators, 234 tests

**Ultimate Purpose:**
- **Tool Engineering Platform**: Build written/generated scripts for simple to advanced problem-solving
- **YAML-Driven Architecture**: Generate code/models/tools/parameters from Pydantic models
- **Agent Toolchain**: Premium agent tools + user tools for data workflows
- **Data Cycle**: Transfer → Transformation → Analysis → RAG → Tuning (iterative)
- **Session Management**: Structured chat sessions with context, goals, audit trail

**Current State:**
- Branch: `feature/develop` (post-PR #34 merge)
- Phase 1: 84% complete (27/32 hours)
- MVP Goal: First working iteration of tool engineering framework
- Tests: 235/235 passing (116 pydantic + 43 registry + additional integration tests)
- Action Items: 40 tool YAML mismatches (HIGH PRIORITY)

**Key Documents:**
- `README.md` - Project overview, quick start (558 lines)
- `ROUNDTRIP_ANALYSIS.md` - Complete system state + action items ⭐ GO-TO FILE
- `docs/VALIDATION_PATTERNS.md` - Custom types & validators guide (769 lines)
- `docs/PARAMETER_MAPPING_RESULTS.md` - 40 mismatches to fix

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

**Code Maintenance:**
- Use custom types from `src/pydantic_models/base/custom_types.py`
- Use validators from `src/pydantic_models/base/validators.py`
- Run validation: `python scripts/validate_registries.py --strict`
- Run tests: `python -m pytest tests/pydantic_models/ -v`

**Documentation:**
- Single source of truth: No duplicate information
- Update README.md for architectural changes
- Date stamp all major docs: `**Last Updated:** YYYY-MM-DD`

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

## 4. Testing & Validation

### Registry Validation
```powershell
# Full validation
python scripts/validate_registries.py --strict --verbose

# Parameter mapping only
python scripts/validate_parameter_mappings.py --verbose
```

### Test Suites
```powershell
# All tests (234)
python -m pytest tests/ -v

# Pydantic tests (116)
python -m pytest tests/pydantic_models/ -v

# Registry tests (43)
python -m pytest tests/registry/ -v
```

### VS Code Tasks
- **Quick Analysis** - Fast code structure check
- **Full Analysis** - Comprehensive analysis + mappings
- **Validate Registries** - CI/CD validation
- **Run Tests** - Execute test suite
- **Pre-commit Checks** - Full validation pipeline

---

## 5. Toolset Usage

**Environment:** `$env:MY_TOOLSET = "C:\Users\HP\my-tiny-toolset\TOOLSET"`

| Tool | Purpose | Command |
|------|---------|---------|
| `code_analyzer.py` | Quick structure | `python $env:MY_TOOLSET\code_analyzer.py . --json` |
| `version_tracker.py` | Full analysis | `python $env:MY_TOOLSET\version_tracker.py . --version X` |
| `mapping_analyzer.py` | Relationships | `python $env:MY_TOOLSET\mapping_analyzer.py . --html` |

**Outputs:** `.tool-outputs/` (gitignored)

---

## 6. Quick Reference

**Session startup** → Run tests, verify artifacts (Excel 1, JSON 2, CSV 4), skip mapping  
**User asks about validation** → Point to `docs/VALIDATION_PATTERNS.md`  
**User asks about action items** → Check `ROUNDTRIP_ANALYSIS.md` Part 10  
**User wants to fix YAMLs** → Start with `docs/PARAMETER_MAPPING_RESULTS.md`  
**User asks about tests** → 234/234 passing, artifacts in `tests/reports/`  
**Before major changes** → Read `ROUNDTRIP_ANALYSIS.md` for full context  
**Creating new models** → Use custom types from `base/custom_types.py`  
**Verify outputs** → Excel (1 .xlsx), JSON (2 .json), CSV (4 .csv) in tests/reports/

---

## 7. Session Management & Knowledge Capture

### Chat Session Best Practices

**Structured Sessions:**
1. Start with clear goal (from ROUNDTRIP_ANALYSIS.md or Git issue)
2. Break into subtasks
3. Validate after each subtask
4. Document decisions in WORKSPACE/FIELDNOTES.md
5. Update formal docs when pattern validated

**Effective Context:**
- Always reference ROUNDTRIP_ANALYSIS.md for current state
- Check Git status before starting work
- Run tests to establish baseline
- Verify artifacts exist (Excel, JSON, CSV)

**Continuity Between Sessions:**
- Git commits preserve code state
- ROUNDTRIP_ANALYSIS.md preserves system state
- WORKSPACE/FIELDNOTES.md preserves decisions/discoveries
- Git issues provide formal tracking

### Session Goals Hierarchy

**1. Branch Goals** (feature/develop in this case)
- Read: `ROUNDTRIP_ANALYSIS.md` - Current system state, action items
- Track: Git issues linked to current branch
- Update: Progress in ROUNDTRIP_ANALYSIS.md as work completes

**2. Immediate Goals** (current work)
- Fix 40 tool YAML parameter mappings (HIGH PRIORITY)
- Validate after each fix: `python scripts/validate_parameter_mappings.py --strict`
- Track progress: 40 → 0 mismatches

**3. Session Context** (multi-session continuity)
- Chat sessions structured around specific goals
- Context preserved in WORKSPACE/FIELDNOTES.md (toolset repo)
- Git issues provide formal tracking
- Folder workspace field notes capture informal progress

### Tool Engineering Focus

**YAML-Driven Development:**
- Models defined in Pydantic → Exported to YAML
- Tools defined in YAML → Validated against methods
- Parameters mapped automatically → Type-checked
- Changes in code → Registry drift detection

**Custom Tool Functions:**
- Build reusable validators (9 functions so far)
- Create custom types (20+ types so far)
- Generic helpers for audit, session management
- All validated with comprehensive tests

**Problem-Solving Workflow:**
1. Define problem (Git issue or ROUNDTRIP_ANALYSIS.md action item)
2. Check existing solutions (REFERENCE/SUBJECTS/)
3. Implement solution using custom types/validators
4. Validate with tests (159 tests framework)
5. Document pattern if reusable (WORKSPACE/ → REFERENCE/)
6. Update tool YAMLs if new parameters added

### Knowledge Capture Protocol

**When to update toolset REFERENCE/ folders:**

1. **Discover a pattern** → Document in `WORKSPACE/FIELDNOTES.md` first
2. **Validate pattern** → Test across multiple use cases
3. **Extract to REFERENCE/** → Move validated knowledge to proper subject folder
4. **Update folder README** → Date stamp + add to curated index

**What goes where in toolset:**

| Discovery | Capture Location | Final Destination |
|-----------|------------------|-------------------|
| Quick note, command, link | `WORKSPACE/FIELDNOTES.md` | Stay there (ephemeral) |
| Validated solution | `WORKSPACE/FIELDNOTES.md` | `REFERENCE/SUBJECTS/<domain>/` |
| Best practice | Test in application | `REFERENCE/SUBJECTS/<domain>/` |
| Architecture pattern | `REFERENCE/SYSTEM/architecture/` | Update existing docs |
| Configuration example | Test first | `CONFIGS/<type>/` |
| Useful prompt | `WORKSPACE/FIELDNOTES.md` | `PROMPTS/` (if reusable) |

**Knowledge Flow:**
```
Application Work → Pattern Discovery → WORKSPACE/FIELDNOTES.md
                                            ↓
                                    Validation & Testing
                                            ↓
                                    REFERENCE/SUBJECTS/<domain>/
                                            ↓
                                    Update folder README.md (dated)
```

### AI Alignment Principles

**Code Base Understanding:**
1. **Go-to file**: `ROUNDTRIP_ANALYSIS.md` - Complete system state
2. **Related docs**: `/docs` folder - Domain-specific knowledge
3. **Toolset knowledge**: `C:\Users\HP\my-tiny-toolset\REFERENCE/` - Best practices, solutions

**Identify Best Practices:**
- During work, note patterns that work well
- Check if pattern already exists in REFERENCE/SUBJECTS/
- If new pattern, document in WORKSPACE/FIELDNOTES.md
- After validation, propose moving to REFERENCE/

**Update Knowledge Base:**
- **REFERENCE/SUBJECTS/**: Domain expertise (data-engineering, mlops, api-design)
- **REFERENCE/SYSTEM/**: Architecture, guides, specifications
- **WORKSPACE/**: Research notes, experiments, drafts
- **CONFIGS/**: Configuration templates
- **PROMPTS/**: Reusable prompt patterns

**Relevant Sources at Any Time:**
- Check toolset README files for curated indexes
- Cross-reference REFERENCE/INDEX.md for navigation
- External sources documented in WORKSPACE/FIELDNOTES.md
- Always date stamp when updating capital folders

### Data Workflow Cycle (RAG/Tuning)

**Transfer:**
- Gmail/Drive/Sheets → Casefile storage
- Structured data models (GmailMessage, DriveFile, SheetData)
- Audit trail: session_id → casefile_id hierarchy

**Transformation:**
- Pydantic validation ensures data quality
- Custom types enforce constraints
- Validators check business rules

**Analysis:**
- Code analysis tools from toolset
- Parameter mapping validation
- Registry drift detection

**RAG Integration:**
- Casefile as context storage
- Session management for conversation continuity
- Tool execution history for learning

**Tuning Cycle:**
- Validation errors → Improve models
- Parameter mismatches → Update tool YAMLs
- Test failures → Refine validation logic
- Repeat cycle iteratively
