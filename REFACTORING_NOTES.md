# Architecture Refactoring Notes

## Move: tool_definition.py Location Change

**Date**: October 3, 2025  
**Commit**: 0af7614  
**Type**: Architecture improvement (non-breaking)

### What Changed

Moved `tool_definition.py` from incorrect location to proper location:

```
src/pydantic_models/tool_session/tool_definition.py
    ↓
src/pydantic_ai_integration/tool_definition.py
```

### Why This Change Was Needed

#### Problem
`tool_definition.py` was located in `pydantic_models/` but contained:
- **Business logic methods**: `validate_params()`, `check_permission()`, `check_enabled()`
- **Executable references**: `implementation` (function), `params_model` (class)
- **Active behavior**: Not just data structures, but tool management logic

#### Solution
Moved to `pydantic_ai_integration/` because:
- This folder owns tool **registration** (`tool_decorator.py`)
- This folder owns tool **execution** (calls implementation)
- This folder owns tool **validation** (uses params_model)
- `ManagedToolDefinition` is part of the tool infrastructure, not a passive data model

### New Architecture

```
src/
├── pydantic_models/          # PASSIVE: Pure data structures
│   └── tool_session/
│       ├── models.py         # ToolRequest, ToolResponse, ToolEvent
│       └── session_models.py # Session CRUD request/response models
│
└── pydantic_ai_integration/  # ACTIVE: Tool management infrastructure
    ├── tool_definition.py    # ✅ ManagedToolDefinition (moved here)
    ├── tool_decorator.py     # @register_mds_tool, MANAGED_TOOLS registry
    ├── dependencies.py       # MDSContext
    └── tools/                # Tool implementations
```

### Changes Made

1. **File moved**: `tool_definition.py` → `pydantic_ai_integration/`
2. **Import updated**: `tool_decorator.py` now uses relative import:
   ```python
   # OLD
   from src.pydantic_models.tool_session.tool_definition import (...)
   
   # NEW
   from .tool_definition import (...)
   ```
3. **No functional changes**: All code works identically
4. **No API changes**: External interfaces unchanged

### Benefits

1. ✅ **Logical grouping**: Tool infrastructure lives together
2. ✅ **Clear separation**: Data models vs business logic
3. ✅ **Better maintainability**: Related code is co-located
4. ✅ **Prevents confusion**: Name implies relationship (tool_definition.py + tool_decorator.py)
5. ✅ **Cleaner imports**: Relative imports within same package

### Verification

- ✅ No lint errors
- ✅ No type errors
- ✅ Imports successful
- ✅ Service layer unaffected (uses `get_tool_definition()` from decorator)
- ✅ API layer unaffected (uses `get_tool_definition()` from decorator)

### Related Cleanup (Also in Commit)

- Removed `resume_models.py` (obsolete, resume is implicit)
- Removed `/resume` endpoint from router
- Removed `resume_session()` method from service
- Session resume now happens implicitly via `session_id` parameter

---

## Separation of Concerns Principles

### pydantic_models/ - WHAT
**Purpose**: Define data structures for serialization/deserialization  
**Contents**: Pure Pydantic models (no business logic)  
**Examples**: Request/Response envelopes, Events, DTOs

### pydantic_ai_integration/ - HOW
**Purpose**: Tool registration, validation, and execution infrastructure  
**Contents**: Active logic, decorators, registries, validators  
**Examples**: Tool definitions, decorators, execution context

### services/ - WHEN/WHERE
**Purpose**: Business logic orchestration  
**Contents**: Service methods, repositories, domain logic  
**Examples**: ToolSessionService, CommunicationService

### routers/ - WHO/WHAT
**Purpose**: API endpoints and routing  
**Contents**: HTTP handlers, auth checks, request validation  
**Examples**: Tool session router, chat router

---

## Future Improvements

1. Consider adding `tool_definition.py` to `__init__.py` exports if needed externally
2. Could create separate `tool_infrastructure/` package if this grows larger
3. May want to add type stubs for better IDE support

---

*This refactoring improves code organization without changing functionality.*
