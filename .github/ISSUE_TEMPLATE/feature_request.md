---
name: Feature Request
about: Propose a new feature
title: '[FEATURE] '
labels: enhancement
assignees: ''
---

## Feature Description
A clear and concise description of the feature.

## Problem Statement
What problem does this solve?

## Proposed Solution
How should this be implemented?

## Architecture Impact
Which layers does this affect?
- [ ] L0: Base Infrastructure (BaseRequest/BaseResponse)
- [ ] L1: Payload Models (business data)
- [ ] L2: Request/Response DTOs
- [ ] L3: Method Definitions (MANAGED_METHODS)
- [ ] L4: Tool Definitions (MANAGED_TOOLS)
- [ ] L5: YAML Configuration

## Implementation Checklist
- [ ] Create/update models in `src/pydantic_models/`
- [ ] Add method to `config/methods_inventory_v1.yaml`
- [ ] Create tool YAML in `config/toolsets/`
- [ ] Generate tool: `python scripts/generate_tools.py`
- [ ] Implement service logic in `src/{service}/`
- [ ] Add tests in `tests/`
- [ ] Update documentation (HANDOVER.md, CODE-MAP.md)
- [ ] Validate alignment: `python scripts/validate_dto_alignment.py`

## API Example
```python
# Show expected usage
```

## Alternatives Considered
What other approaches were considered?

## Additional Context
Links to related issues, documentation, or discussions.
