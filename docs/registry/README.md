# Methods Registry Documentation

*Last updated: October 7, 2025*

**Central documentation for the MANAGED_METHODS registry system**

## Quick Links

| Document | Purpose |
|----------|---------|
| [reference.md](./reference.md) | Complete reference: classification schema, versioning, release process, stats, model coverage |
| [CHANGELOG.md](./CHANGELOG.md) | Detailed version history, release notes, and migration guides |

## Structure Overview

```
docs/
├── registry/                           [Registry system documentation]
│   ├── README.md                       [This file]
│   ├── reference.md                    [Classification schema, stats, model coverage]
│   ├── CHANGELOG.md                    [Version history]
│   ├── versioning-guide.md             [Semver rules]
│   └── release-process.md              [Release workflows]
│
├── methods/                            [API reference (generated)]
│   ├── README.md                       [Method API index]
│   ├── workspace/                      [15 method pages]
│   ├── communication/                  [10 method pages]
│   ├── automation/                     [1 method page]
│   └── services/                       [6 service pages]
│
├── audits/                             [Historical analysis docs]
└── tool_engineering_foundation.md      [MANAGED_TOOLS documentation]
```

## For Developers

**Creating a new method:**
1. Add to `config/methods_inventory_v1.yaml`
2. Create Pydantic request/response models
3. Implement method with `@register_service_method` decorator
4. Run `python scripts/generate_method_docs.py`

**Making changes:**
- **PATCH** (typos, metadata): Edit YAML, bump version to x.y.z+1
- **MINOR** (new methods): Add to YAML, bump version to x.y+1.0
- **MAJOR** (breaking): Copy YAML to v2.yaml, write migration guide

**Releasing:**
```bash
# Automated
python scripts/release_version.py --type minor --changelog "Add archive method"

# Manual
# 1. Update YAML version
# 2. Add CHANGELOG entry
# 3. Regenerate docs
# 4. Commit + tag
```

See [release-process.md](./release-process.md) for detailed workflows.

## For Users

**Browse API:**
- Start at [../methods/README.md](../methods/README.md)
- Browse by domain: [workspace](../methods/workspace/), [communication](../methods/communication/), [automation](../methods/automation/)
- Browse by service: [CasefileService](../methods/services/CasefileService.md), [GmailClient](../methods/services/GmailClient.md), etc.

**Check compatibility:**
```python
from pydantic_ai_integration.method_registry import validate_yaml_compatibility

result = validate_yaml_compatibility("config/methods_inventory_v2.yaml")
if not result["compatible"]:
    print(f"Issues: {result['issues']}")
```

**Monitor deprecations:**
```python
from pydantic_ai_integration.method_registry import get_deprecated_methods

deprecated = get_deprecated_methods()
for method in deprecated:
    print(f"{method['name']}: Use {method['replacement']} instead")
```

## Registry Components

### Code
- `src/pydantic_ai_integration/method_definition.py` - Data structures
- `src/pydantic_ai_integration/method_registry.py` - Global registry + 15 discovery APIs
- `src/pydantic_ai_integration/method_decorator.py` - `@register_service_method` decorator

### Configuration
- `config/methods_inventory_v1.yaml` - Method definitions (757 lines, 26 methods)

### Scripts
- `scripts/generate_method_docs.py` - Generate markdown API reference
- `scripts/release_version.py` - Automated versioning workflow

### Tests
- `tests/test_method_decorator.py` - Decorator registration tests
- `tests/test_factory_integration.py` - ToolFactory integration tests

## Version History

- **v1.0.0** (2025-10-06): Initial baseline release
  - 26 methods across 6 services
  - Complete classification taxonomy
  - Comprehensive documentation
  - Versioning infrastructure

See [CHANGELOG.md](./CHANGELOG.md) for detailed history.

---

**Questions?** Check [versioning-guide.md](./versioning-guide.md) or file an issue.
