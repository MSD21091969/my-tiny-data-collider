# ADR-001: Parameter Inheritance System

**Title:** ADR-001: Implement Parameter Inheritance from DTOs to Tools  
**Date:** 2025-10-09  
**Status:** Accepted  
**Deciders:** Development Team, AI Assistant

---

## Context

The project had parameter definitions duplicated across three layers:
1. **L1-L2:** Pydantic models (DTOs)
2. **L3:** Method registry (`methods_inventory_v1.yaml`)
3. **L4-L5:** Tool definitions (`toolsets/*.yaml`)

This caused:
- **Maintenance burden:** Changes required updates in 3 places
- **Drift errors:** Parameters fell out of sync
- **Validation issues:** No automated way to detect mismatches
- **Cognitive load:** Developers had to remember to update all layers

---

## Decision

**Implement single source of truth with automatic parameter inheritance:**

```
L1-L2 DTOs (define) → L3 Methods (extract) → L4 Tools (inherit)
```

**Key Mechanisms:**
1. DTOs define parameters with Pydantic Field annotations
2. Method registry extracts parameters from DTO via introspection
3. Tools reference methods and inherit parameters automatically
4. Code generation creates tool wrappers with inherited signatures

---

## Rationale

### Why This Approach?

**1. Single Source of Truth**
- DTOs are the authoritative definition
- Pydantic ensures type safety at the source
- Changes propagate automatically

**2. Zero Duplication**
- Parameters defined once in DTO
- Extracted on-demand via Pydantic introspection
- No manual copying required

**3. Validation Built-In**
- `validate_dto_alignment.py` detects drift
- Fails fast if layers out of sync
- Prevents runtime errors

**4. Developer Experience**
- Less to remember
- Fewer places to update
- Automated code generation

### Considered Alternatives

**Alternative 1: Manual Parameter Definitions**
- Pros: Simple, explicit
- Cons: High maintenance, drift-prone, error-prone
- **Why rejected:** Caused the original problem

**Alternative 2: JSON Schema Generation**
- Pros: Standard format, tool support
- Cons: Extra conversion layer, runtime overhead
- **Why rejected:** Unnecessary complexity, Pydantic already provides schema

**Alternative 3: Shared YAML Definitions**
- Pros: Central definitions
- Cons: YAML becomes source of truth (not code), no type safety
- **Why rejected:** Loses Pydantic validation benefits

---

## Consequences

### Positive
- **Reduced maintenance:** Update DTOs only
- **Fewer errors:** Automatic validation catches drift
- **Better DX:** Less cognitive load
- **Type safety:** Pydantic ensures correctness
- **Scalable:** Easy to add new operations

### Negative
- **Code generation required:** Tools must be regenerated after DTO changes
- **Learning curve:** Developers must understand the flow
- **Debugging complexity:** Errors span multiple layers

### Neutral
- **Build step added:** `python scripts/generate_tools.py` required
- **Validation step added:** `python scripts/validate_dto_alignment.py` recommended

---

## Implementation

### Completed
- [x] Create method registry with parameter extraction
- [x] Update tool schema to support `method_name` references
- [x] Implement code generation with parameter inheritance
- [x] Create `validate_dto_alignment.py` script
- [x] Migrate 3 example tools to new pattern
- [x] Document workflow in HANDOVER.md

### Pending
- [ ] Migrate all existing tools to use inheritance
- [ ] Add pre-commit hook for validation
- [ ] Create CI/CD pipeline check for drift
- [ ] Add IDE support (type hints in generated tools)

---

## References

- **Related ADRs:** ADR-002 (R-A-R Pattern)
- **Files:**
  - `config/methods_inventory_v1.yaml` - Method registry
  - `config/tool_schema_v2.yaml` - Tool schema with inheritance
  - `scripts/generate_tools.py` - Code generator
  - `scripts/validate_dto_alignment.py` - Validation script
- **Discussions:** HANDOVER.md Phase 2 notes

---

## Maintenance Notes

**When to update this ADR:**
- Major changes to parameter inheritance mechanism
- New validation strategies
- Alternative approaches proven better

**Related patterns:**
- R-A-R Pattern (ADR-002)
- Tool Generation Workflow (ADR-003)
- RequestHub Orchestration (ADR-004)
