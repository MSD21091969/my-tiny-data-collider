# Classification Library

**Version:** 1.0.0  
**Created:** October 11, 2025  
**Branch:** feature/develop  
**Status:** Active Development

---

## Overview

This directory contains the **Grand Classification System** for the Tiny Data Collider project - a comprehensive framework for analyzing, organizing, and managing relationships between **toolsets, models, and methods**.

The classification system provides:
- 📊 **Analytical Framework** - Systematic analysis of tool/method/model relationships
- 🔗 **Parameter Mapping** - Bridge between tool parameters and method parameters
- ⚡ **Orchestration System** - Execution control separate from business logic
- 🛠️ **Meta-Tooling** - Tools for engineering tools
- 📈 **Pattern Recognition** - Identify and standardize common patterns

---

## Directory Structure

```
classification/
├── README.md                          # This file
│
├── docs/                              # Documentation
│   ├── GRAND_CLASSIFICATION_PLAN.md  # Master plan and architecture
│   ├── ANALYTICAL_TOOLSET_ENGINEERING.md
│   ├── TOOL_DEVELOPMENT_WORKFLOW.md
│   ├── METHOD_PARAMETER_INTEGRATION.md
│   └── PARAMETER_MAPPING_ANALYSIS.md
│
├── tools/                             # Analysis and generation tools
│   ├── analyze_parameter_relationships.py
│   ├── validate_classification_consistency.py
│   ├── generate_parameter_mappings.py
│   ├── export_classification_reports.py
│   └── README.md
│
├── exports/                           # Generated reports and data
│   ├── model_exports/                # Model field exports (CSV)
│   ├── tool_analysis/                # Tool analysis reports
│   ├── method_analysis/              # Method analysis reports
│   └── mapping_reports/              # Parameter mapping reports
│
└── schemas/                           # Classification schemas
    ├── extended_tool_classification_v1.yaml
    ├── extended_method_classification_v1.yaml
    ├── extended_model_classification_v1.yaml
    ├── parameter_mapping_schema_v1.yaml
    └── orchestration_parameter_schema_v1.yaml
```

---

## Quick Start

### View the Master Plan
```bash
# Read the comprehensive classification plan
cat classification/docs/GRAND_CLASSIFICATION_PLAN.md
```

### Run Analysis Tools
```bash
# Analyze parameter relationships across all tools
python classification/tools/analyze_parameter_relationships.py

# Validate classification consistency
python classification/tools/validate_classification_consistency.py

# Generate parameter mappings for a tool
python classification/tools/generate_parameter_mappings.py --tool "create_casefile"
```

### View Exports
```bash
# View model exports
cd classification/exports/model_exports
ls *.csv

# View analysis reports
cd classification/exports/tool_analysis
```

---

## Core Concepts

### 1. Three-Tier Classification

**Tools (36+)**
- Execution metadata and orchestration
- Reference methods for parameter inheritance
- Define user-facing interface

**Methods (34+)**
- Business logic implementation
- Service layer operations
- Define request/response contracts

**Models (80+)**
- Data structures and validation
- Layered architecture (0-5)
- Type safety and constraints

### 2. Parameter Mapping

**Five Mapping Types:**
1. **Direct** - Parameter names/types match exactly
2. **Transform** - Type conversion required (e.g., string → datetime)
3. **Nested** - Extract from nested structures
4. **Composite** - Combine multiple parameters
5. **Orchestration** - Execution control (not passed to method)

### 3. Orchestration Parameters

**Standard Categories:**
- **Execution Control** - dry_run, execution_mode
- **Reliability** - timeout_seconds, retry_policy
- **Context** - session_id, casefile_id
- **Validation** - strict_validation, validation_only

### 4. Bidirectional Flow

**Input Mapping:** Tool parameters → Method parameters  
**Output Mapping:** Method results → Tool responses  
**Enrichment:** Add execution metadata to responses

---

## Key Features

### Analytical Framework
- Pattern recognition across 36+ tools
- Relationship analysis (tools ↔ methods ↔ models)
- Consistency validation
- Gap detection

### Parameter Mapping System
- Formal mapping definitions (YAML)
- Transformation catalog
- Validation rules
- Auto-generation templates

### Meta-Tooling
- Analysis tools for tool engineers
- Mapping generators
- Consistency validators
- Report generators

### Orchestration System
- Standardized execution parameters
- Handler registry
- Context management
- Preview/dry-run modes

---

## Integration Points

### With Existing System

**Registries:**
- `src/pydantic_ai_integration/tool_decorator.py` - MANAGED_TOOLS registry
- `src/pydantic_ai_integration/method_registry.py` - MANAGED_METHODS registry
- `src/pydantic_ai_integration/model_registry.py` - Model registry

**Configuration:**
- `config/methodtools_v1/` - Tool YAML definitions (36 files)
- `config/methods_inventory_v1.yaml` - Method definitions (34 methods)
- `config/models_inventory_v1.yaml` - Model catalog (80 models)

**Analysis Tools:**
- `model_analysis_tools/` - Existing model analysis tools
- Auto-discovery and verification infrastructure

---

## Implementation Status

### ✅ Completed (Phase 0)

- [x] Directory structure created
- [x] Master plan documented (GRAND_CLASSIFICATION_PLAN.md)
- [x] Foundation docs compiled (4 archived docs)
- [x] Model export infrastructure (80 CSV files)
- [x] Verification tooling (100% coverage validation)

### 🚧 In Progress

- [ ] Extended classification schemas
- [ ] Parameter mapping definitions
- [ ] Analysis tools implementation
- [ ] Orchestration handler registry
- [ ] Transformation engine

### 📋 Planned (Phases 1-5)

**Phase 1: Foundation (Weeks 1-2)**
- Extended classification schemas
- Mapping schema definition
- Orchestration framework

**Phase 2: Analysis Tools (Weeks 3-4)**
- Parameter relationship analyzer
- Consistency validator
- Mapping generator

**Phase 3: Population (Weeks 5-6)**
- Classify 36 tools
- Classify 34 methods
- Create 36 mappings

**Phase 4: Integration (Weeks 7-8)**
- Mapping executor
- Enhanced tool decorator
- Validation system

**Phase 5: Verification (Weeks 9-10)**
- End-to-end testing
- Complete documentation
- Performance optimization

---

## Usage Examples

### Analyze Tool-Method Relationships

```bash
# Generate comprehensive analysis report
python classification/tools/analyze_parameter_relationships.py

# Output: classification/exports/parameter_analysis_report.csv
# Contains: tool name, method name, parameter mappings, transformations
```

### Validate Classification

```bash
# Check all classifications for consistency
python classification/tools/validate_classification_consistency.py

# Output: classification/exports/consistency_report.txt
# Shows: missing classifications, inconsistencies, suggestions
```

### Generate Parameter Mapping

```bash
# Auto-generate mapping YAML for a tool
python classification/tools/generate_parameter_mappings.py \
  --tool "create_casefile" \
  --method "CasefileService.create_casefile" \
  --output "config/parameter_mappings_v1/"

# Output: Auto-generated mapping with:
# - Detected parameter relationships
# - Suggested transformation types
# - Validation rules
```

---

## Documentation

### Master Plan
- **GRAND_CLASSIFICATION_PLAN.md** - Complete architecture and implementation plan
  - 10 parts covering foundation → implementation → maintenance
  - Schemas, examples, timelines, metrics
  - Integration with existing system

### Foundation Documents
- **ANALYTICAL_TOOLSET_ENGINEERING.md** - Classification philosophy
- **TOOL_DEVELOPMENT_WORKFLOW.md** - Development lifecycle
- **METHOD_PARAMETER_INTEGRATION.md** - Parameter mapping concepts
- **PARAMETER_MAPPING_ANALYSIS.md** - Bidirectional mapping & orchestration

### Schema Documentation
- Tool classification schema
- Method classification schema
- Model classification schema
- Parameter mapping schema
- Orchestration parameter schema

---

## Contributing

### Adding New Classifications

1. **For New Tools:**
   - Add extended classification in tool YAML
   - Create parameter mapping file
   - Run consistency validator

2. **For New Methods:**
   - Add parameter profile to method definition
   - Document data flow pattern
   - Update method registry

3. **For New Models:**
   - Add data profile to model inventory
   - Document usage context
   - Export to CSV

### Running Validation

```bash
# Before committing
python classification/tools/validate_classification_consistency.py --strict

# Check specific area
python classification/tools/validate_classification_consistency.py --focus tools
```

---

## Metrics

### Current Coverage

- **Tools:** 36 registered in MANAGED_TOOLS
- **Methods:** 34 registered in MANAGED_METHODS
- **Models:** 80 cataloged in model registry
- **Tool YAMLs:** 36 in config/methodtools_v1/
- **Model Exports:** 80 CSV files with field data

### Target Metrics (Post-Implementation)

- **Classification Coverage:** 100% (all tools/methods/models)
- **Mapping Coverage:** 100% (all tools have mappings)
- **Consistency Score:** >95%
- **Validation Pass Rate:** 100%
- **Test Coverage:** >90%

---

## Related Systems

### Branch Structure

**feature/develop** (current)
- Classification library lives here
- Stable, permanent infrastructure
- Ready for merge to main

**feature/ai-method-integration** (branch 1)
- Will consume classification system
- Implements actual method calling
- Uses mappings for parameter routing

### Config Integration

```
config/
├── methodtools_v1/              # Tool YAMLs (existing)
├── methods_inventory_v1.yaml    # Method definitions (existing)
├── models_inventory_v1.yaml     # Model catalog (existing)
│
└── parameter_mappings_v1/       # NEW: Parameter mappings
    └── [36 mapping files]
```

### Source Integration

```
src/pydantic_ai_integration/
├── tool_decorator.py            # Enhanced with mapping support
├── method_registry.py           # Existing registry
├── model_registry.py            # Existing registry
│
├── mapping_executor.py          # NEW: Execute mappings
├── transformation_engine.py     # NEW: Apply transformations
└── orchestration_handlers.py    # NEW: Handle orchestration
```

---

## Maintenance

### Daily Checks
```bash
# Run comprehensive validation
python scripts/daily_classification_check.py
```

### Pre-Commit Hooks
```bash
# Add to .git/hooks/pre-commit
python classification/tools/validate_classification_consistency.py --strict
```

### Version Control
- Classification schemas use semver
- Document all changes in CHANGELOG.md
- Maintain backward compatibility

---

## Support

### Documentation
- See `classification/docs/` for detailed guides
- See `config/` for YAML examples
- See `src/pydantic_ai_integration/` for implementation

### Tools
- See `classification/tools/README.md` for tool documentation
- See `model_analysis_tools/README.md` for existing analysis tools

### Issues
- File issues with `[classification]` prefix
- Reference specific components (tool/method/model)
- Include relevant YAML snippets

---

## Roadmap

### Q4 2025
- ✅ Foundation complete
- 🚧 Phase 1: Extended schemas
- 📋 Phase 2: Analysis tools
- 📋 Phase 3: Population

### Q1 2026
- 📋 Phase 4: Integration
- 📋 Phase 5: Verification
- 📋 Full system deployment

### Future
- Advanced pattern recognition
- ML-assisted mapping generation
- Visual relationship explorer
- Real-time consistency monitoring

---

## License

Same as parent project (my-tiny-data-collider)

---

## Version History

- **v1.0.0** (2025-10-11) - Initial classification library structure
  - Directory structure created
  - Master plan documented
  - Foundation docs compiled
  - Ready for phase 1 implementation

---

**End of Classification Library README**
