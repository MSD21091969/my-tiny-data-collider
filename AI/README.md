# AI Collaboration Framework

Last updated: October 8, 2025

## Structure

```
AI/
├── practices/        # Conversation standards, collaboration guidelines
├── workflows/        # Development processes, quality assurance
├── prompts/          # Reusable prompt templates
└── examples/         # Real repository examples
```

## Quick Start

**Contributors:** Read practices/conversation-practices.md, prompts/README.md  
**AI Assistants:** Check ../.github/copilot-instructions.md, workflows/quality-assurance.md

## Principles

**Communication:** Precise, unambiguous, factual. No emojis, DRY prose.  
**Documentation:** Update README.md and HANDOVER.md only. Report progress in chat.  
**Code Quality:** Type hints required, async/await patterns, 85% test coverage.  
**Review:** All AI-generated code requires human validation.

## Repository Context

**Name:** my-tiny-data-collider  
**Stack:** Python 3.11+, FastAPI, Pydantic, Firebase  
**Architecture:** Service-Repository pattern, tool-based AI integration  
**Primary Branch:** develop

### Core Directories
- `src/pydantic_models/` - Data models (100% DTO coverage)
- `src/casefileservice/` - Casefile CRUD operations
- `src/communicationservice/` - Chat session management
- `src/tool_sessionservice/` - Tool execution lifecycle
- `src/pydantic_ai_integration/` - AI tool system
- `config/` - YAML configurations (methods_inventory_v1.yaml, tool_schema_v2.yaml)
- `docs/` - Documentation (ai-collaboration/, methods/, registry/)
- `scripts/` - Automation (generate_tools.py, validate_dto_alignment.py)

### Key Files
- `HANDOVER.md` - Current development state
- `docs/ai-collaboration/practices/conversation-practices.md` - Communication standards
- `docs/registry/reference.md` - System architecture (26 methods, 52 models)

## Development Standards

### Code Pattern
```python
async def method_name(self, request: RequestModel) -> ResponseModel:
    """Docstring with Args, Returns, Raises."""
    result = await self.repository.operation(request.payload)
    return ResponseModel(
        request_id=request.request_id,
        status=RequestStatus.COMPLETED,
        payload=result
    )
```

### Architecture
- **6-Layer Model System:** L0 (Base) → L1 (Payloads) → L2 (DTOs) → L3 (Methods) → L4 (Tools) → L5 (YAML)
- **Parameter Flow:** Define once in DTO, auto-extract to Method, auto-inherit to Tool
- **R-A-R Pattern:** Request-Action-Response for all operations
- **Tool Registration:** `@register_mds_tool` decorator

### Tool Engineering
```bash
# Generate tools from YAML
python scripts/generate_tools.py

# Validate DTO alignment
python scripts/validate_dto_alignment.py
```

Tool YAML structure:
```yaml
name: tool_name
implementation:
  type: api_call
  method_name: workspace.casefile.create_casefile
# Parameters auto-inherited from method
```

## Testing

```bash
pytest                              # All tests
pytest --cov=src --cov-report=html # With coverage
pytest tests/integration/          # Integration only
```

**Requirements:** 85% coverage minimum, comprehensive assertions, proper mocking.

## Quality Gates

**Prohibited AI Uses:** Security-sensitive authentication, production configs, legal docs, financial logic  
**Required:** Type hints everywhere, async/await, error handling, docstrings  
**Standards:** Pylint >8.0, API response <200ms, input validation

## Commit Format

```
type(scope): Short description

- Factual bullet points
- No emojis, code over prose
```

Types: feat, fix, refactor, test, docs, chore

## Documentation References

| Topic | Location |
|-------|----------|
| API Reference | ../docs/methods/README.md |
| System Architecture | ../docs/registry/reference.md |
| Conversation Standards | practices/conversation-practices.md |
| Quality Assurance | workflows/quality-assurance.md |
| Tool Generation | ../TOOL_GENERATION_WORKFLOW.md |