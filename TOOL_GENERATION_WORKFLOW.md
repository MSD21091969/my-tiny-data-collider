# Tool Generation Workflow

This document outlines the standardized workflow for tool generation in the my-tiny-data-collider repository.

## Overview

The tool generation system uses a factory pattern to create Python tools from declarative YAML configurations. Tools are generated into the `src/pydantic_ai_integration/tools/generated/` directory with proper package structure.

## Architecture

### Components

1. **YAML Configurations** (`config/tools/`)
   - Declarative tool definitions following `tool_schema_v2.yaml`
   - Organized by domain/subdomain (e.g., `workspace/casefile/`)
   - Support for CRUD operations, business rules, and audit policies

2. **Jinja Templates** (`src/pydantic_ai_integration/tools/factory/templates/`)
   - `tool_template.py.jinja2`: Generates tool implementation with Pydantic models and decorators

3. **Tool Factory** (`src/pydantic_ai_integration/tools/factory/__init__.py`)
   - Processes YAML configurations
   - Generates Python code with proper imports and validation
   - Handles directory structure and `__init__.py` creation

4. **Generated Output** (`src/pydantic_ai_integration/tools/generated/`)
   - Auto-generated tools with `@register_mds_tool` decorator
   - Pydantic parameter models with validation
   - Proper package structure mirroring YAML organization

## Workflow Commands

### Generate All Tools
```bash
python scripts/generate_tools.py
```

### Generate Specific Tool
```bash
python scripts/generate_tools.py tool_name
```
- Searches recursively in `config/tools/` for `tool_name.yaml`
- Supports tools in subdirectories (e.g., `workspace/casefile/create_casefile_tool`)

### Validate YAML Configurations
```bash
python scripts/generate_tools.py --validate-only
```

### Clean Generated Files
```powershell
.\scripts\cleanup_generated_files.ps1
```
- Removes all `.py` files from generated directories
- Preserves `__init__.py` and folder structure

### Import Generated Tools
```bash
python scripts/import_generated_tools.py
```
- Imports all generated tool modules to register them
- Useful for ensuring tools are loaded in the runtime

### Show Registered Tools
```bash
python scripts/show_tools.py
```
- Displays all registered tools with metadata
- Shows parameters, permissions, and policies

## YAML Configuration Schema

Tools are defined using the schema in `config/tool_schema_v2.yaml`. Key sections:

### Required Fields
- `name`: Snake_case tool identifier
- `description`: Human-readable description
- `category`: Tool category (workspace, communication, etc.)
- `parameters`: List of input parameters with types and validation

### Classification
- `domain`: High-level category (workspace, communication, automation, utilities)
- `subdomain`: Specific area within domain
- `capability`: Operation type (create, read, update, delete, process)
- `complexity`: Implementation complexity (atomic, composite, pipeline)
- `maturity`: Development stage (experimental, beta, stable, deprecated)

### Business Rules
- `requires_auth`: Whether authentication is required
- `required_permissions`: List of permissions needed
- `timeout_seconds`: Maximum execution time

### Implementation Types
- `simple`: Inline Python logic
- `api_call`: Calls registered MANAGED_METHODS
- `data_transform`: Transforms data structures
- `composite`: Orchestrates multiple tools

## Directory Structure

```
config/tools/
├── workspace/
│   └── casefile/
│       ├── create_casefile_tool.yaml
│       ├── get_casefile_tool.yaml
│       └── update_casefile_tool.yaml

src/pydantic_ai_integration/tools/generated/
├── __init__.py
└── workspace/
    └── casefile/
        ├── __init__.py
        ├── create_casefile_tool.py
        ├── get_casefile_tool.py
        └── update_casefile_tool.py
```

## Best Practices

### YAML Organization
- Use domain/subdomain structure for logical grouping
- Follow consistent naming: `{action}_{resource}_tool.yaml`
- Include comprehensive examples and error scenarios
- Document business rules and audit requirements

### Toolset Storage
**Store YAML files in organized toolsets for session persistence:**

```bash
config/
├── toolsets/                    # Organized tool collections
│   ├── core/                    # Core business logic
│   │   └── casefile_management/ # Casefile CRUD operations
│   ├── helpers/                 # Utility tools
│   ├── prototypes/              # Experimental tools
│   └── workflows/               # Multi-step compositions
└── tools/                       # Legacy flat structure (deprecated)
```

**Toolset Categories:**
- **Core**: Essential business functionality, primary use cases
- **Helpers**: Supporting utilities, data transformations, common operations
- **Prototypes**: Experimental tools, new patterns, testing variants
- **Workflows**: Complex multi-step operations, business processes

**Benefits:**
- ✅ **Logical Grouping**: Tools organized by purpose and implementation
- ✅ **Session Persistence**: Keep tool configurations between sessions
- ✅ **Version Control**: Toolsets can be versioned independently
- ✅ **Testing Boundaries**: Natural scopes for testing and monitoring
- ✅ **Maintenance**: Easier to manage related tools together

**Example Organization:**
```
config/toolsets/core/casefile_management/
├── create_casefile_tool.yaml
├── get_casefile_tool.yaml
├── update_casefile_tool.yaml
├── delete_casefile_tool.yaml
├── list_casefiles_tool.yaml
└── README.md                    # Toolset documentation
```

### Tool Development
- Validate YAML before generation: `python scripts/generate_tools.py --validate-only`
- Test generated tools: `python scripts/import_generated_tools.py`
- Clean before regeneration: `.\scripts\cleanup_generated_files.ps1`

### Code Generation
- Never manually edit generated files (marked with warnings)
- Regenerate after YAML changes
- Use version control to track configuration changes

## Current Status

### Active Features
- ✅ YAML-based tool definition with validation
- ✅ Recursive directory structure support
- ✅ Pydantic model generation with constraints
- ✅ Tool registration with MANAGED_TOOLS
- ✅ CLI support for single and batch generation
- ✅ Directory structure mirroring

### Known Limitations
- ⚠️ Test generation templates not implemented (disabled)
- ⚠️ Composite tool orchestration not implemented
- ⚠️ Advanced data transformation patterns limited

### Maintenance Notes
- ToolFactory CLI fixed to support recursive YAML search
- Test generation code removed to avoid confusion (templates missing)
- Scripts are documented and integrated into workflow
- Cleanup preserves package structure

## Troubleshooting

### Common Issues

**Tool not found during generation:**
- Ensure YAML file exists in `config/tools/` (recursive search supported)
- Check filename matches tool name exactly

**Import errors after generation:**
- Run `python scripts/import_generated_tools.py` to load tools
- Check for syntax errors in generated code

**Validation failures:**
- Review `tool_schema_v2.yaml` for required fields
- Check parameter definitions and constraints
- Verify method references in MANAGED_METHODS registry

**Directory structure issues:**
- Clean generated files: `.\scripts\cleanup_generated_files.ps1`
- Regenerate to recreate proper structure

## Future Enhancements

- Implement test template generation
- Add composite tool orchestration
- Support for advanced data transformations
- Integration with CI/CD pipelines
- Tool versioning and migration support