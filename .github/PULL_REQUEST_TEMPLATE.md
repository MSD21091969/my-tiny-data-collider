# Pull Request

## Description
Brief description of changes.

## Type of Change
- [ ] Bug fix (non-breaking change)
- [ ] New feature (non-breaking change)
- [ ] Breaking change (requires version bump)
- [ ] Refactoring (no functional changes)
- [ ] Documentation update
- [ ] Tool generation update

## Related Issues
Closes #

## Changes Made

### Models (L1-L2)
- [ ] Created/updated payload models in `src/pydantic_models/workspace/`
- [ ] Created/updated DTOs in `src/pydantic_models/operations/`
- [ ] Updated `config/models_inventory_v1.yaml`

### Methods (L3)
- [ ] Added/updated method in `config/methods_inventory_v1.yaml`
- [ ] Updated method registry

### Tools (L4-L5)
- [ ] Created/updated YAML in `config/toolsets/`
- [ ] Regenerated tools: `python scripts/generate_tools.py`
- [ ] Validated alignment: `python scripts/validate_dto_alignment.py`

### Services
- [ ] Implemented/updated service logic in `src/{service}/`
- [ ] Updated RequestHub routing if needed

### Tests
- [ ] Added unit tests
- [ ] Added integration tests
- [ ] All tests pass: `pytest -v`
- [ ] Coverage maintained >80%

### Documentation
- [ ] Updated ARCHITECTURE.md with session notes
- [ ] Updated documentation if structure changed
- [ ] Updated relevant AI prompts in `AI/prompts/`

## Testing Checklist
```bash
# Run these commands to verify
pytest tests/ -v --cov=src
python scripts/validate_dto_alignment.py
python scripts/show_tools.py
```

## Pre-Merge Validation
- [ ] All tests pass
- [ ] No parameter drift detected
- [ ] Type checking passes: `mypy src/`
- [ ] Linting passes: `pylint src/`
- [ ] Documentation updated
- [ ] No merge conflicts with develop

## Breaking Changes
List any breaking changes and migration steps needed.

## Screenshots/Examples
If applicable, add examples of the feature or output.

## AI Assistant Notes
<!-- AI assistants can add implementation notes here -->

---

**For Reviewers:**
- Check alignment with R-A-R pattern
- Verify parameter inheritance (no duplication)
- Confirm test coverage >80%
- Validate documentation updates
