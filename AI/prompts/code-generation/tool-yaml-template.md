# Tool YAML Definition Template

*Last updated: October 8, 2025*  
*Sync status: ✅ UP TO DATE (October 8, 2025 - Foundation Sync)*

Template for creating YAML tool definitions with parameter inheritance from methods.

## Context

**Repository**: my-tiny-data-collider  
**Architecture**: 6-Layer Model System with parameter inheritance  
**Pattern**: DTO → Method → Tool (single source of truth)  
**Location**: `config/toolsets/`

## Task Definition

Create a YAML tool definition that:
- References an existing method from MANAGED_METHODS registry
- Automatically inherits parameters from the method's DTO
- Follows tool_schema_v2.yaml structure
- Includes proper classification and metadata

## Template Structure

```yaml
# Tool name follows convention: {domain}.{subdomain}.{action}
name: workspace.casefile.create_casefile

# Clear, concise description of what the tool does
description: "Creates a new casefile with metadata and initial status"

# Category for grouping (workspace, communication, tool_session, etc.)
category: "workspace"

# Classification following standard taxonomy
classification:
  domain: workspace              # workspace, communication, tool_session
  subdomain: casefile            # casefile, chat_session, tool_execution
  capability: create             # create, read, update, delete, list, search
  complexity: atomic             # atomic, composite
  maturity: stable               # prototype, development, stable, deprecated
  integration_tier: internal     # internal, external, hybrid

# Implementation details - references method for parameter inheritance
implementation:
  type: api_call                 # api_call or composite
  api_call:
    # Method name from MANAGED_METHODS registry
    method_name: workspace.casefile.create_casefile
    
# Parameters section - OPTIONAL for 1:1 tools
# Parameters are AUTO-INHERITED from method DTO
# Only include this section if you need to:
# - Transform parameters for UI presentation
# - Add additional parameters not in the method
# - Override descriptions for tool-specific context

# parameters:
#   - name: title
#     type: string
#     required: true
#     description: "Casefile title"
#   - name: description
#     type: string
#     required: false
#     description: "Optional casefile description"

# Return value description
returns:
  type: object
  description: "CreateCasefileResponse with created casefile details"
  properties:
    casefile_id:
      type: string
      description: "Unique identifier for the created casefile"
    status:
      type: string
      description: "Request execution status"

# Example usage for documentation
examples:
  - description: "Create a new casefile"
    input:
      title: "Investigation Case 001"
      description: "Initial fraud investigation"
    output:
      casefile_id: "cf_12345"
      status: "completed"

# Metadata
metadata:
  version: "1.0.0"
  tags: ["casefile", "create", "workspace"]
  requires_auth: true
  rate_limit: 100  # requests per minute
```

## Guidelines

### 1:1 Tool Pattern (Most Common)
**When to use**: Tool directly maps to a single method

```yaml
name: workspace.casefile.create_casefile
implementation:
  type: api_call
  api_call:
    method_name: workspace.casefile.create_casefile
# NO parameters section - auto-inherited from method
```

### Composite Tool Pattern
**When to use**: Tool orchestrates multiple methods

```yaml
name: workspace.casefile.create_with_initial_chat
implementation:
  type: composite
  composite:
    steps:
      - method_name: workspace.casefile.create_casefile
        output_mapping: casefile_id
      - method_name: communication.chat_session.create_chat_session
        input_mapping:
          casefile_id: $previous.casefile_id
# Parameters merged from all referenced methods
```

### Parameter Override Pattern
**When to use**: Need to transform or add parameters

```yaml
implementation:
  type: api_call
  api_call:
    method_name: workspace.casefile.create_casefile
    
parameters:
  # Inherited parameters with custom descriptions
  - name: title
    type: string
    required: true
    description: "Custom tool-specific description for UI"
    
  # Additional parameter not in method
  - name: ui_preset
    type: string
    required: false
    description: "UI preset configuration (tool-specific)"
```

## Validation Checklist

- [ ] Tool name follows convention: {domain}.{subdomain}.{action}
- [ ] Description is clear and concise
- [ ] Method reference exists in MANAGED_METHODS
- [ ] Classification fields are valid values
- [ ] Parameters only included if necessary (overrides/additions)
- [ ] Returns section describes output structure
- [ ] Examples demonstrate typical usage
- [ ] Metadata includes version and tags

## Generation Command

```bash
# Generate tool from YAML
python scripts/generate_tools.py tool_name

# Validate without generating
python scripts/generate_tools.py --validate-only

# Validate alignment with method DTOs
python scripts/validate_dto_alignment.py
```

## Quality Standards

### Required Elements
- Clear, actionable description
- Valid method reference
- Proper classification
- Accurate return type

### Optional Elements
- Parameters (only if overriding/adding)
- Examples (recommended for complex tools)
- Extended metadata

### Anti-patterns
- ❌ Duplicating all method parameters manually
- ❌ Inconsistent naming conventions
- ❌ Missing method references
- ❌ Invalid classification values
- ❌ Overly complex composite tools

## Related Resources

- [Tool Schema v2](../../../config/tool_schema_v2.yaml)
- [Method Registry](../../../config/methods_inventory_v1.yaml)
- [Tool Generation Script](../../../scripts/generate_tools.py)
- [Validation Script](../../../scripts/validate_dto_alignment.py)
- [HANDOVER Document](../../../HANDOVER.md)

---

**Note**: This template reflects the parameter inheritance system implemented in feature/dto-inheritance branch. Tools automatically inherit parameters from their referenced methods, eliminating parameter duplication.
