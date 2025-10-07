# Development Workflow

*Created: October 8, 2025*

## Current Focus

**Branch**: `feature/dto-inheritance`

**Objective**: Foundation alignment and classification
- DTO inheritance from MANAGED_METHODS
- Full classification of models, methods, YAMLs, and tools
- R-A-R pattern alignment across all layers
- ToolRequest payload relationship to internal req/resp models

**Scope**: Combined Priority 1 + Priority 3 work

---

## Branch Strategy

### Active Branch
- **feature/dto-inheritance** - Foundation work (Priority 1 + 3 combined)

### Stopped Branches
- ~~feature/enhanced-schema~~ (Priority 2) - Stopped, strategy TBD after foundation complete
- ~~feature/rar-alignment~~ (Priority 3) - Merged into dto-inheritance branch

---

## Development Principles

1. **Foundation First**: Align classification before tool engineering strategy
2. **Factual Documentation**: Short, clear, no verbose documentation
3. **Single Source of Truth**: Methods define contracts, tools inherit
4. **R-A-R Pattern**: Request-Action-Response across all layers

---

## Architecture Layers

See [ARCHITECTURE_CLARIFICATION.md](../ARCHITECTURE_CLARIFICATION.md) for detailed layer separation:

1. **Tool Request Layer**: System envelope (ToolRequest/ToolResponse)
2. **Method DTO Layer**: Business logic (CreateCasefileRequest/Response)
3. **Service Layer**: Business operations
4. **Repository Layer**: Data persistence

**Key**: ToolRequest.payload.parameters → transforms to → Method Request DTOs

---

## Workflow

1. **Work on foundation branch**: `feature/dto-inheritance`
2. **Commit frequently**: Clear, factual commit messages
3. **Test continuously**: Verify classification and alignment
4. **Decide strategy**: Tool engineering approach based on results

---

*Keep it simple. Focus on foundation and classification.*
