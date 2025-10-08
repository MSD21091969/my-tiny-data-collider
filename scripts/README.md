# Scripts Directory

*Last updated: October 8, 2025 at 19:45*

Core scripts for maintaining the 6-layer architecture with parameter inheritance.

## 🎯 Core Workflow Scripts

These four scripts form the essential workflow for the feature/dto-inheritance architecture:

### 1. **validate_dto_alignment.py** ⭐⭐⭐⭐⭐
**Purpose**: Validates parameter alignment across 6 layers (DTO → Method → Tool)

**Use Cases**:
- Detect parameter drift between layers
- Ensure R-A-R pattern compliance (100% required)
- Validate tool → method references
- Check method → DTO model references

**When to Use**: Before every commit, after any model/method/tool changes

**Command**:
```bash
python scripts/validate_dto_alignment.py
```

**Output**: Lists validation issues by severity (ERROR, WARNING, INFO)

---

### 2. **generate_tools.py** ⭐⭐⭐⭐⭐
**Purpose**: Generates Python tool code from YAML definitions with auto-parameter inheritance

**Use Cases**:
- Create new tools from YAML
- Regenerate tools after method changes
- Validate YAML syntax

**When to Use**: After creating/updating tool YAMLs, after method signature changes

**Commands**:
```bash
python scripts/generate_tools.py              # Generate all tools
python scripts/generate_tools.py tool_name    # Generate specific tool
python scripts/generate_tools.py --validate-only  # Validate YAML only
```

**Output**: Generated Python files in `src/pydantic_ai_integration/tools/generated/`

---

### 3. **import_generated_tools.py** ⭐⭐⭐⭐
**Purpose**: Imports all generated tool modules into MANAGED_TOOLS registry

**Use Cases**:
- Refresh MANAGED_TOOLS registry
- Load newly generated tools
- Verify import success/failures

**When to Use**: After generate_tools.py, before runtime usage

**Command**:
```bash
python scripts/import_generated_tools.py
```

**Output**: Count of imported modules and any import errors

---

### 4. **show_tools.py** ⭐⭐⭐⭐
**Purpose**: Display registered tools in MANAGED_TOOLS registry

**Use Cases**:
- Check tool registration status
- Verify parameter inheritance worked correctly
- Debug tool visibility issues
- List all available tools

**When to Use**: After generate_tools.py, to verify registry state

**Command**:
```bash
python scripts/show_tools.py
```

**Output**: Formatted list of all registered tools with metadata

---

## 📋 Daily Development Workflow

```bash
# 1. Make changes to DTOs/Methods/Tools
# Edit files in src/pydantic_models/, config/methods_inventory_v1.yaml, config/toolsets/

# 2. Validate alignment
python scripts/validate_dto_alignment.py

# 3. Generate/regenerate tools
python scripts/generate_tools.py

# 4. Import tools into registry
python scripts/import_generated_tools.py

# 5. Verify registration
python scripts/show_tools.py
```

## 🔄 Before Committing

```bash
# Validate everything is aligned
python scripts/validate_dto_alignment.py

# Verify tool count and status
python scripts/show_tools.py
```

## 🧹 Major Tool Refactoring

```powershell
# 1. Clean up old files
.\scripts\cleanup_generated_files.ps1

# 2. Regenerate all tools
python scripts/generate_tools.py

# 3. Import and verify
python scripts/import_generated_tools.py
python scripts/show_tools.py
```

## 🛠️ Utility Scripts

### cleanup_generated_files.ps1
**Purpose**: Deletes generated tool files while preserving structure

**When to Use**: Before major tool regeneration, when cleaning up

**Command**:
```powershell
.\scripts\cleanup_generated_files.ps1
```

Preserves `__init__.py` files and folder structure while removing all generated `.py` files.

---

## 📦 Archive

The `archive/` directory contains scripts that are not part of the core daily workflow but may be useful for specific scenarios:

- **release_version.py** - Automated version release for methods registry
- **run_continuous_integration_tests.py** - CI/CD continuous test runner
- **yaml_test_executor.py** - YAML-driven test execution engine

These can be restored if needed for releases, CI/CD setup, or specialized testing.

---

## 🎯 Architecture Context

**6-Layer Model System**:
```
L0: Base Infrastructure (BaseRequest/BaseResponse)
L1: Payload Models (business data)
L2: Request/Response DTOs (execution envelopes)
L3: Method Definitions (MANAGED_METHODS)
L4: Tool Definitions (MANAGED_TOOLS)
L5: YAML Configuration (source of truth)
```

**Parameter Flow** (Single Source of Truth):
```
L1 Payload.field → L3 MethodParameterDef → L4 ToolParameterDef
```

**Key Principle**: Define parameters once in DTOs, auto-extract to methods, auto-inherit to tools.

---

## 📚 Related Documentation

- [HANDOVER Document](../HANDOVER.md) - Current development state
- [AI Framework](../AI/README.md) - AI collaboration guidelines
- [Copilot Instructions](../.github/copilot-instructions.md) - GitHub Copilot configuration
- [Method Registry](../config/methods_inventory_v1.yaml) - 26 method definitions
- [Model Registry](../config/models_inventory_v1.yaml) - 52 model definitions
- [Tool Schema](../config/tool_schema_v2.yaml) - Tool structure with inheritance

---

**Note**: These scripts are critical for maintaining the parameter inheritance system. Always run `validate_dto_alignment.py` before committing changes to ensure no parameter drift between layers.
