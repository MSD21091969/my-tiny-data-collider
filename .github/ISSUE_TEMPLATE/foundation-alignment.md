# Foundation Alignment - DTO Inheritance & R-A-R Pattern

**Branch**: `feature/dto-inheritance`  
**Priority**: Critical  
**Type**: Foundation Work

---

## Overview

Align model classification, DTO inheritance, and R-A-R pattern across all layers before proceeding with tool engineering.

**Reference**: `TOOL_ENGINEERING_ARCHITECTURE.md` and `ARCHITECTURE_CLARIFICATION.md`

---

## Chores

### 1. Fix R-A-R Pattern Violations

**File**: `src/pydantic_models/operations/tool_execution_ops.py`

**Issue**: `ChatRequest` uses `ChatMessagePayload` instead of `ChatRequestPayload`

**Tasks**:
- [ ] Rename `ChatMessagePayload` → `ChatRequestPayload`
- [ ] Ensure pattern: `ChatRequest(BaseRequest[ChatRequestPayload])`
- [ ] Update all references to renamed payload
- [ ] Verify tests pass

**Acceptance**: All DTOs follow `{Action}Request(BaseRequest[{Action}Payload])` pattern

---

### 2. Update methods_inventory_v1.yaml - Google Workspace Models

**File**: `config/methods_inventory_v1.yaml`

**Issue**: YAML references `GmailListMessagesRequest/Response` but actual implementation uses plain Pydantic models

**Tasks**:
- [ ] Review actual model implementations in `src/pydantic_ai_integration/integrations/google_workspace/models.py`
- [ ] Update YAML `models:` section to reflect actual model names
- [ ] Add note distinguishing external API data models from service operation models
- [ ] Validate all 6 Google Workspace methods have correct model references

**Acceptance**: methods_inventory_v1.yaml accurately reflects actual code

---

### 3. Implement DTO Inheritance in ToolFactory

**File**: `src/pydantic_ai_integration/tools/factory/__init__.py`

**Issue**: Tools duplicate parameters instead of inheriting from methods

**Tasks**:
- [ ] Add method resolution: `get_method(method_name)` from MANAGED_METHODS
- [ ] Extract parameters from `method.models.request_model_class.payload_class`
- [ ] Generate `ToolParameterDef` list from method parameters
- [ ] Update Jinja template to use inherited parameters
- [ ] Remove parameter definitions from tool YAML schema

**Acceptance**: Generated tools inherit all parameters from referenced method

---

### 4. Add Classification Inheritance

**File**: `src/pydantic_ai_integration/tools/factory/__init__.py`

**Issue**: Tool classification independent from method classification

**Tasks**:
- [ ] Extract classification from method: `method.get_classification()`
- [ ] Populate `ManagedToolDefinition.metadata` with method classification
- [ ] Remove classification from tool YAML (inherited automatically)
- [ ] Update tool_schema_v2.yaml to mark classification as optional (inherited by default)

**Acceptance**: Tools automatically inherit domain/subdomain/capability from method

---

### 5. Add ToolRequest → Method DTO Mapping

**File**: `src/pydantic_ai_integration/tools/generated/[tool_files].py`

**Issue**: No explicit type-safe mapping from `ToolRequest.payload.parameters` to method DTOs

**Tasks**:
- [ ] Update generated tool template
- [ ] Add: `method = get_method("method_name")`
- [ ] Add: `method_request = method.models.request_model_class(...)`
- [ ] Add: `payload = method.models.request_model_class.payload_class(**params)`
- [ ] Ensure type safety at parameter → payload boundary

**Acceptance**: Generated tools have type-safe parameter mapping

---

### 6. Validation & Drift Detection

**File**: `scripts/generate_tools.py`

**Issue**: No validation that tool YAML aligns with method definition

**Tasks**:
- [ ] Add validation: method exists in MANAGED_METHODS
- [ ] Add validation: tool parameters match method parameters
- [ ] Add validation: tool classification matches method classification (if specified)
- [ ] Emit warnings for parameter duplication in YAML
- [ ] Add drift detection in CI

**Acceptance**: Tool generation fails fast with clear errors on misalignment

---

### 7. Update Existing Tool YAMLs

**Files**: `config/toolsets/**/*.yaml`

**Issue**: Existing tools have redundant parameter definitions

**Tasks**:
- [ ] Remove `parameters:` section from all tool YAMLs
- [ ] Ensure `implementation.method_name` is correct
- [ ] Remove redundant `classification:` if it matches method
- [ ] Validate all tools still generate correctly

**Acceptance**: All tool YAMLs minimal (no duplication)

---

### 8. Documentation Updates

**Files**: `docs/methods/`, `docs/registry/`

**Tasks**:
- [ ] Document DTO inheritance pattern
- [ ] Document classification inheritance rules
- [ ] Update tool YAML examples
- [ ] Create migration guide for existing tools
- [ ] Update `docs/registry/reference.md` with new architecture

**Acceptance**: Complete documentation of new patterns

---

## Validation Checklist

Before marking complete:

- [ ] All DTOs follow R-A-R pattern
- [ ] methods_inventory_v1.yaml has correct model references
- [ ] ToolFactory resolves methods and inherits parameters
- [ ] Generated tools have type-safe DTO mapping
- [ ] Tool YAMLs minimal (no duplication)
- [ ] Validation catches misalignment
- [ ] All tests pass
- [ ] Documentation complete

---

## Dependencies

- MANAGED_METHODS registry loaded
- method_definition.py structure stable
- tool_definition.py structure stable

---

## Breaking Changes

- Tool YAML schema changes (parameters optional)
- Generated tool code structure changes
- Regeneration of all existing tools required

---

## Testing Strategy

1. **Unit Tests**: Parameter extraction, classification inheritance
2. **Integration Tests**: Full tool generation from YAML
3. **Validation Tests**: Drift detection, error cases
4. **Regression Tests**: All existing tools work after regeneration

---

## Estimated Effort

- Chores 1-2: 2-3 hours
- Chores 3-5: 5-7 hours
- Chores 6-7: 3-4 hours
- Chore 8: 2-3 hours

**Total**: 12-17 hours

---

## Success Criteria

✅ Single source of truth: methods define contracts  
✅ Zero duplication: tools inherit everything  
✅ Type safety: Dict[str, Any] → Typed DTOs  
✅ Validation: Fail fast on misalignment  
✅ Documentation: Complete migration guide
