# Tiny Data Collider

**Last Updated:** 2025-10-14

A FastAPI-based data integration and API orchestration platform with comprehensive Pydantic validation, featuring Google Workspace integration (Gmail, Drive, Sheets), casefile management, and tool execution orchestration.

---

## 🎯 Quick Start

### For Developers
1. **Read**: [`docs/VALIDATION_PATTERNS.md`](docs/VALIDATION_PATTERNS.md) - Learn custom types and validators
2. **Install**: `pip install -r requirements.txt`
3. **Validate**: `python scripts/validate_registries.py --strict`
4. **Test**: `python -m pytest tests/pydantic_models/ -v`

### For AI Assistants
1. **Session Startup**: Check `ROUNDTRIP_ANALYSIS.md` for current system state
2. **Check Branch**: `git status` - Confirm you're on correct branch
3. **Run Analysis**: Use VS Code task "Quick Analysis" or `python $env:MY_TOOLSET\code_analyzer.py .`
4. **Review Context**: `.tool-outputs/analysis/` for baseline understanding

### For Reviewers
- **Start**: [`docs/PHASE1_COMPLETION_SUMMARY.md`](docs/PHASE1_COMPLETION_SUMMARY.md) - What was accomplished
- **Details**: [`docs/DEVELOPMENT_PROGRESS.md`](docs/DEVELOPMENT_PROGRESS.md) - 27/32 hours (84% complete)
- **Issues**: [`docs/PARAMETER_MAPPING_RESULTS.md`](docs/PARAMETER_MAPPING_RESULTS.md) - 40 mismatches to fix

---

## 📋 System Overview

### Core Services
- **AuthService**: JWT authentication, user/service tokens, session management
- **CasefileService**: Document/case management, ACL permissions, data source storage
- **CommunicationService**: Tool session lifecycle, Gmail/Drive/Sheets client wrappers
- **CoreService**: Request orchestration, autonomous execution, session coordination
- **ToolSessionService**: Tool execution, parameter validation, audit trail

### Pydantic Enhancement (Phase 1 Complete)
- **Custom Types**: 20+ reusable Annotated types (CasefileId, ShortString, IsoTimestamp, etc.)
- **Validators**: 9 reusable validation functions (timestamp_order, at_least_one, etc.)
- **Enhanced Models**: 13 files (8 canonical, 4 operation, 1 workspace)
- **Parameter Mapping**: Validator system with CI/CD integration
- **Test Suite**: 159 tests passing (116 pydantic + 43 registry)

### Current Status
- **Branch**: `feature/develop` (post-PR #34 merge)
- **Phase 1**: 84% complete (27/32 hours)
- **Tests**: 159/159 passing (100%)
- **Known Issues**: 40 tool-method parameter mismatches (HIGH PRIORITY to fix)
- **Code Quality**: 62% validation code reduction, DRY principles enforced

---

## 🔧 Pydantic Validation Framework

### Custom Types Library (20+ types)

**Location:** `src/pydantic_models/base/custom_types.py`

Reusable Annotated types eliminate duplicate validation code:

```python
from src.pydantic_models.base.custom_types import (
    CasefileId, ShortString, IsoTimestamp, PositiveInt, TagList
)

class CasefileMetadata(BaseModel):
    casefile_id: CasefileId      # Auto-validates UUID + lowercase
    title: ShortString           # 1-200 characters
    priority: PositiveInt        # Must be > 0
    created_at: IsoTimestamp     # ISO 8601 format
    tags: TagList                # List of non-empty strings
```

**Available Types:**

| Category | Types | Purpose |
|----------|-------|---------|
| **IDs** | CasefileId, ToolSessionId, ChatSessionId, SessionId | UUID validation + normalization |
| **Strings** | NonEmptyString, ShortString, MediumString, LongString | Length constraints (1-200, 1-1000, 1-10000) |
| **Numbers** | PositiveInt, NonNegativeInt, PositiveFloat, Percentage, FileSizeBytes | Numeric constraints |
| **Email/URL** | EmailAddress, UrlString | Format validation |
| **Time** | IsoTimestamp | ISO 8601 validation |
| **Collections** | TagList, EmailList | Typed lists with validation |

### Reusable Validators (9 functions)

**Location:** `src/pydantic_models/base/validators.py`

Cross-field validation patterns for `@model_validator` usage:

```python
from src.pydantic_models.base.validators import (
    validate_timestamp_order, validate_at_least_one, validate_mutually_exclusive
)

@model_validator(mode='after')
def validate_model(self) -> 'MyModel':
    # Ensure created_at <= updated_at
    validate_timestamp_order(self, 'created_at', 'updated_at')
    
    # At least one data source required
    validate_at_least_one(self, ['gmail_data', 'drive_data', 'sheets_data'])
    
    # Only one primary key allowed
    validate_mutually_exclusive(self, ['id', 'external_id', 'reference_id'])
    
    return self
```

**Available Validators:**

| Validator | Purpose | Example |
|-----------|---------|---------|
| `validate_timestamp_order` | Ensure timestamp ordering | created_at ≤ updated_at |
| `validate_at_least_one` | At least one field required | Email OR phone OR address |
| `validate_mutually_exclusive` | Only one field allowed | Credit card XOR PayPal |
| `validate_conditional_required` | Conditional requirements | If type="email", email field required |
| `validate_list_not_empty` | Non-empty lists | Tags must have at least one item |
| `validate_list_unique` | Unique list items | No duplicate tags |
| `validate_range` | Numeric bounds | 0 ≤ percentage ≤ 100 |
| `validate_string_length` | String constraints | Custom length validation |
| `validate_depends_on` | Field dependencies | Field B requires Field A |

### Code Reduction Impact

**Before (40 lines):**
```python
class CasefileMetadata(BaseModel):
    casefile_id: str
    title: str
    created_at: str
    
    @field_validator('casefile_id')
    @classmethod
    def validate_casefile_id(cls, v: str) -> str:
        try:
            UUID(v)
        except ValueError:
            raise ValueError("Invalid casefile_id format...")
        return v.lower()
    
    @field_validator('title')
    @classmethod
    def validate_title(cls, v: str) -> str:
        if not v or len(v) > 200:
            raise ValueError("Title must be between 1 and 200 characters")
        return v
    
    # ... 15+ more lines of timestamp validation
```

**After (15 lines - 62% reduction):**
```python
from src.pydantic_models.base.custom_types import CasefileId, ShortString, IsoTimestamp
from src.pydantic_models.base.validators import validate_timestamp_order

class CasefileMetadata(BaseModel):
    casefile_id: CasefileId
    title: ShortString
    created_at: IsoTimestamp
    updated_at: IsoTimestamp
    
    @model_validator(mode='after')
    def validate_timestamps(self) -> 'CasefileMetadata':
        validate_timestamp_order(self, 'created_at', 'updated_at')
        return self
```

**See [`docs/VALIDATION_PATTERNS.md`](docs/VALIDATION_PATTERNS.md) for complete usage guide and migration examples.**

---

## 📚 Documentation

### Primary References
- **[Documentation Index](docs/README.md)** - Master navigation hub ⭐
- **[Validation Patterns](docs/VALIDATION_PATTERNS.md)** - Custom types & validators guide (769 lines) ⭐
- **[Round-Trip Analysis](ROUNDTRIP_ANALYSIS.md)** - Complete system state analysis ⭐

### Development Tracking
- **[Phase 1 Summary](docs/PHASE1_COMPLETION_SUMMARY.md)** - Achievements overview (305 lines)
- **[Development Progress](docs/DEVELOPMENT_PROGRESS.md)** - Detailed tracking (474 lines, 27/32 hours)

### Issue Management
- **[Parameter Mapping Results](docs/PARAMETER_MAPPING_RESULTS.md)** - 40 mismatches to fix (175 lines) ⚠️ ACTION ITEMS
- **[Pytest Import Issue](docs/PYTEST_IMPORT_ISSUE.md)** - 9 test files workarounds (280 lines)
- **[Parameter Mapping Test Issues](docs/PARAMETER_MAPPING_TEST_ISSUES.md)** - Test challenges (310 lines)

### Historical Reference
- **[Pydantic Enhancement Longlist](docs/PYDANTIC_ENHANCEMENT_LONGLIST.md)** - Original 32-hour plan (1135 lines)

**Quick Links by Audience:**
- **New Developers** → Start with `docs/VALIDATION_PATTERNS.md`
- **PR Reviewers** → Read `docs/PHASE1_COMPLETION_SUMMARY.md`
- **Maintainers** → Check `docs/PARAMETER_MAPPING_RESULTS.md` for action items
- **Planners** → Review `ROUNDTRIP_ANALYSIS.md` for comprehensive state

---

## 🧪 Testing & Validation

### Registry Validation (CI/CD Integration)

```bash
# Full validation (coverage, consistency, drift, parameter mapping)
python scripts/validate_registries.py --strict --verbose

# Skip parameter mapping (faster checks)
python scripts/validate_registries.py --no-param-mapping

# Detailed parameter mapping report
python scripts/validate_parameter_mappings.py --verbose
```

**Validation Coverage:**
- **Coverage**: Ensures all tools reference valid methods
- **Consistency**: Checks method/tool configuration alignment
- **Drift Detection**: Compares YAML definitions with code implementation
- **Parameter Mapping**: Validates tool-to-method parameter compatibility ⚠️ 40 issues found

### Test Suites

```bash
# Run all tests (159 total)
python -m pytest tests/ -v

# Pydantic models (116 tests)
python -m pytest tests/pydantic_models/ -v

# Registry system (43 tests)
python -m pytest tests/registry/ -v

# Standalone validator tests (workaround for import issue)
python tests/pydantic_models/test_validators_standalone.py
```

**Test Coverage:**
- **Custom Types**: 26 tests (100% coverage)
- **Canonical Models**: 27 tests (95%+ coverage)
- **Canonical Validation**: 20 tests (business rules)
- **Validators Standalone**: 65+ test cases
- **Registry System**: 43 tests (existing functionality preserved)

**Known Issue:** 9/167 test files (5.4%) have pytest import path issues - workarounds documented in `docs/PYTEST_IMPORT_ISSUE.md`

### VS Code Tasks

Available via `Ctrl+Shift+P` → Tasks: Run Task:

| Task | Purpose | When to Use |
|------|---------|-------------|
| **Quick Analysis** | Fast code structure check | During development |
| **Full Analysis** | Comprehensive analysis + mappings | Before PR, after refactoring |
| **Validate Registries** | Run CI/CD validation | Before commit |
| **Run Tests** | Execute test suite | After changes |
| **Pre-commit Checks** | Full validation pipeline | Before PR creation |

---

## 🚀 Development Workflow

### Branch Strategy

- **`main`**: Production-ready code (protected, requires PR + approval)
- **`feature/develop`**: Active development branch (protected, requires PR)
- **`feature/*`**: Feature branches (CI/CD validation required)

### Contribution Requirements

✅ **Before PR:**
1. Run validation: `python scripts/validate_registries.py --strict`
2. Run tests: `python -m pytest tests/ -v`
3. Update documentation if architectural changes made
4. Add/update test coverage for new functionality

✅ **PR Requirements:**
- All CI/CD checks passing
- Code review and approval from maintainer
- Documentation updates (if applicable)
- No breaking changes to existing APIs (without migration plan)

### Analysis Tools (my-tiny-toolset)

**Environment Variable:** `$env:MY_TOOLSET = "C:\Users\HP\my-tiny-toolset\TOOLSET"`

| Tool | Purpose | Usage |
|------|---------|-------|
| `code_analyzer.py` | Fast structure analysis | `python $env:MY_TOOLSET\code_analyzer.py . --json` |
| `version_tracker.py` | Full analysis + Git history | `python $env:MY_TOOLSET\version_tracker.py . --version 1.0.0` |
| `mapping_analyzer.py` | Model relationships | `python $env:MY_TOOLSET\mapping_analyzer.py . --html` |
| `excel_exporter.py` | Spreadsheet reports | `python $env:MY_TOOLSET\excel_exporter.py . --output report.xlsx` |

**Outputs:** `.tool-outputs/` (gitignored, local only)

---

## ⚠️ Current Action Items (Post-PR #34)

### HIGH PRIORITY: Fix 40 Parameter Mapping Issues

**Status:** 32 errors + 8 warnings discovered by parameter mapping validator  
**Location:** `config/methodtools_v1/*.yaml` files need updates  
**Details:** See [`docs/PARAMETER_MAPPING_RESULTS.md`](docs/PARAMETER_MAPPING_RESULTS.md)

**Action Plan:**
1. Update tool YAML files to include all required method parameters
2. Start with CasefileService tools (11 errors - highest impact)
3. Validate after each fix: `python scripts/validate_parameter_mappings.py --strict`
4. Target: 40 → 0 mismatches

**Examples of Missing Parameters:**
- `create_casefile_tool`: Missing `title` (required)
- `add_session_to_casefile_tool`: Missing `casefile_id`, `session_id`, `session_type`
- `grant_permission_tool`: Missing `casefile_id`, `permission`, `target_user_id`
- `close_session_tool`: Missing `session_id`
- `process_chat_request_tool`: Missing `message`, `session_id`

### MEDIUM PRIORITY: Investigate Parameter Extraction Warnings

**Status:** 8 tools report parameters but methods show zero  
**Issue:** `extract_parameters_from_request_model()` may not handle certain patterns  
**Affected:** Gmail/Drive/Sheets client methods

### LOW PRIORITY: Pytest Import Issue

**Status:** 9/167 test files (5.4%) fail pytest collection  
**Impact:** Core functionality 100% working, workarounds available  
**Details:** [`docs/PYTEST_IMPORT_ISSUE.md`](docs/PYTEST_IMPORT_ISSUE.md)  
**Solution:** Consider editable install or pytest_configure hook in Phase 2

---

## 📊 Project Metrics

### Code Statistics
- **Models**: 294 (13 enhanced with custom types in Phase 1)
- **Functions**: 825+
- **Request/Response Mappings**: 122+
- **Custom Types**: 20+ reusable Annotated types
- **Validators**: 9 reusable validation functions
- **Test Coverage**: 159 tests (116 pydantic + 43 registry, 100% passing)

### Phase 1 Achievements
- **Hours**: 27/32 (84% complete)
- **Code Reduction**: 62% less validation code in models
- **False Positives**: 83% reduction (188 → 40 real issues)
- **Files Created**: 10 (custom_types.py, validators.py, parameter_mapping.py, tests, docs)
- **Files Modified**: 16 (13 model files, 2 scripts, 1 README)
- **Documentation**: 8 files, 1,900+ lines
- **Git Commits**: 12 commits in feature/pydantic-enhancement

### Known Issues Summary
| Issue | Files Affected | Priority | Status |
|-------|----------------|----------|--------|
| Parameter mapping errors | 32 tool YAMLs | HIGH | Action required ⚠️ |
| Parameter extraction warnings | 8 tools | MEDIUM | Investigation needed |
| Pytest import paths | 9 test files (5.4%) | LOW | Workarounds available ✅ |

---

## 🏗️ Architecture Reference

### Service Layer
```
RequestHub (CoreService)
    ↓
ToolSessionService → CommunicationService → Google Workspace Clients
    ↓                                            ↓
CasefileService ← Data Storage              Gmail/Drive/Sheets
    ↓
AuthService → JWT Tokens → Firestore
```

### Data Flow
1. **Request** → RequestHub validates and routes
2. **Authentication** → AuthService issues JWT with user_id + casefile_id
3. **Tool Execution** → ToolSessionService manages execution with audit trail
4. **Data Storage** → CasefileService stores results with ACL permissions
5. **Communication** → CommunicationService wraps Google Workspace APIs

### Registry System
- **Models Registry**: `config/models_inventory_v1.yaml` - Pydantic model definitions
- **Methods Registry**: `config/methods_inventory_v1.yaml` - Service method inventory
- **Tools Registry**: `config/methodtools_v1/` - Tool-to-method mappings (YAML per tool)
- **Validation**: CI/CD integration ensures registry consistency

---

## 🎯 MVP User Journeys (Implementation Status)

### Journey 1: Workspace Setup ✅
- User authentication → JWT token with user_id/username
- Create casefile with title, description → casefile_id returned
- Token extended with casefile_id for request routing
- Casefile persisted to Firestore, retrievable by ID

### Journey 2: Tool Execution in Context ⚠️
- Create tool session → session_id, linked to casefile (audit trail)
- Submit tool request with parameters → Tool executes, results returned
- Session lifecycle: active → executing → completed/failed
- **Issue**: 32 tool YAML mismatches (HIGH PRIORITY to fix)

### Journey 3: Permission Management ✅
- Grant "read" permission to collaborator (casefile ACL)
- Permission check passes → collaborator retrieves data
- ACL list visible showing all permissions
- Revoke permission → access denied after revocation

### Journey 4: Service Automation ✅
- Service token with client_id (no session_request_id)
- Service creates tool session, executes tools
- Audit trail shows service_token as actor
- Background processing without user interaction

### Journey 5: Session Lifecycle ✅
- Create session → status "active"
- Execute multiple tools in same session context
- All requests logged under session_id hierarchy
- Close session → status "closed", no new requests accepted

---

## 🔄 Migration Guide

### Updating Existing Models

**Step 1: Import Custom Types**
```python
from src.pydantic_models.base.custom_types import (
    CasefileId, ShortString, IsoTimestamp, PositiveInt
)
```

**Step 2: Replace Field Validators**
```python
# Before (10+ lines)
@field_validator('casefile_id')
@classmethod
def validate_casefile_id(cls, v: str) -> str:
    try:
        UUID(v)
    except ValueError:
        raise ValueError("Invalid casefile_id format...")
    return v.lower()

# After (1 line)
casefile_id: CasefileId
```

**Step 3: Replace Model Validators**
```python
# Before (15+ lines of timestamp validation)
@model_validator(mode='after')
def validate_timestamps(self) -> 'MyModel':
    # ... complex validation logic
    return self

# After (3 lines)
from src.pydantic_models.base.validators import validate_timestamp_order

@model_validator(mode='after')
def validate_timestamps(self) -> 'MyModel':
    validate_timestamp_order(self, 'created_at', 'updated_at')
    return self
```

**Complete migration guide:** [`docs/VALIDATION_PATTERNS.md`](docs/VALIDATION_PATTERNS.md)

---

## 🤖 AI Assistant Integration

### Session Startup Protocol

**Every new session, AI should:**
1. Set environment: `$env:MY_TOOLSET = "C:\Users\HP\my-tiny-toolset\TOOLSET"`
2. Check branch: `git status` - Confirm correct branch
3. Quick analysis: Run VS Code task "Quick Analysis" or `python $env:MY_TOOLSET\code_analyzer.py . --json`
4. Review outputs: Check `.tool-outputs/analysis/` for baseline context
5. Report status: Branch, model count, known issues

### Natural Language Commands

**Analysis:**
- "analyze the codebase" → Run code_analyzer
- "what models exist?" → Check analysis outputs
- "show relationships" → Run mapping_analyzer

**Validation:**
- "check for errors" → Run validate_registries.py
- "validate parameter mappings" → Run validate_parameter_mappings.py
- "run tests" → Execute pytest

**Development:**
- "create new model" → Use custom types from base/custom_types.py
- "add validation" → Use validators from base/validators.py
- "fix parameter mapping" → Update tool YAML in config/methodtools_v1/

### Context Files
- **System State**: `ROUNDTRIP_ANALYSIS.md` - Current state, action items
- **AI Instructions**: `.github/copilot-instructions.md` - Session startup, practices
- **Documentation Hub**: `docs/README.md` - Navigation to all docs

---

## 📞 Support & Resources

### Internal Documentation
- **Primary Guide**: [`docs/VALIDATION_PATTERNS.md`](docs/VALIDATION_PATTERNS.md) - Custom types & validators
- **Current State**: `ROUNDTRIP_ANALYSIS.md` - System analysis + action items
- **Issue Tracking**: [`docs/PARAMETER_MAPPING_RESULTS.md`](docs/PARAMETER_MAPPING_RESULTS.md) - 40 mismatches

### External Resources
- **Pydantic V2**: https://docs.pydantic.dev/
- **FastAPI**: https://fastapi.tiangolo.com/
- **Pytest**: https://docs.pytest.org/

### Getting Help
1. Check `docs/VALIDATION_PATTERNS.md` troubleshooting section
2. Review `ROUNDTRIP_ANALYSIS.md` for current issues and solutions
3. See test files in `tests/pydantic_models/` for usage examples
4. Consult source code: `src/pydantic_models/base/` for implementations

---

## 📝 Changelog

### Phase 1 Complete (2025-10-14)
- ✅ Added 20+ custom types (CasefileId, ShortString, IsoTimestamp, etc.)
- ✅ Added 9 reusable validators (timestamp_order, at_least_one, etc.)
- ✅ Enhanced 13 model files (8 canonical, 4 operation, 1 workspace)
- ✅ Created parameter mapping validator with CI/CD integration
- ✅ Added 116 pydantic tests + 43 registry tests (159 total, 100% passing)
- ✅ Comprehensive documentation (8 files, 1,900+ lines)
- ✅ 62% validation code reduction, DRY principles enforced
- ⚠️ Discovered 40 tool-method parameter mismatches (action required)
- ⚠️ 9 test files with pytest import issue (workarounds available)

### Next Steps
- Fix 32 parameter mapping errors in tool YAMLs (HIGH PRIORITY)
- Investigate 8 parameter extraction warnings (MEDIUM PRIORITY)
- Consider pytest import issue resolution (LOW PRIORITY)
- Optional: Property-based testing with Hypothesis (Phase 2)

---

**Repository:** https://github.com/MSD21091969/my-tiny-data-collider.git  
**Toolset:** https://github.com/MSD21091969/my-tiny-toolset.git  
**License:** [Add license information]  
**Maintainer:** MSD21091969

---

**Last Updated:** 2025-10-14  
**Phase:** Post-PR #34 merge, Parameter mapping fixes in progress  
**Status:** 159/159 tests passing, 40 YAML updates required