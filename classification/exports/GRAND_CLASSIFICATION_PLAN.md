# Grand Classification Plan
**Version:** 1.0.0  
**Created:** October 11, 2025  
**Status:** Planning Phase  
**Context:** Building on archived analytical toolset engineering docs

---

## Executive Summary

This plan outlines a systematic approach to classify and organize **toolsets, models, and methods** within the Tiny Data Collider system. The classification system serves as the analytical foundation for parameter mapping, orchestration, and meta-tooling capabilities described in the archived documentation.

**Core Objective:** Create a comprehensive, maintainable classification system that enables:
- Analytical parameter mapping between tools ↔ methods ↔ models
- Bidirectional data flow management (inputs/outputs)
- Orchestration parameter separation from method parameters
- Meta-tooling for "engineering tools for tools"
- Pattern recognition and standardization

---

## Part 1: Current State Analysis

### 1.1 Existing Infrastructure

**Registry System:**
- `MANAGED_TOOLS` - 36+ tools in `tool_decorator.py`
- `MANAGED_METHODS` - 34+ methods in `method_registry.py`
- `ModelRegistry` - 80+ models in `model_registry.py`

**Classification Metadata:**
```
Tools (12 fields):
├── Identity: name, description, version
├── Classification: category, tags
├── Method Link: method_name (for inheritance)
└── Execution: parameters, implementation, params_model

Methods (16 fields):
├── Identity: name, description, version
├── Classification: domain, subdomain, capability, complexity, maturity, integration_tier
├── Models: request_model_class, response_model_class
└── Execution: implementation_class, implementation_method

Models (8 metadata fields):
├── Identity: name, file
├── Classification: layer, domain, operation, type
└── Structure: fields[], description, api
```

**YAML Inventories:**
- `config/methods_inventory_v1.yaml` - Method definitions (34 methods)
- `config/methodtools_v1/*.yaml` - Tool definitions (36 YAML files)
- `config/models_inventory_v1.yaml` - Model catalog (80 models)
- `config/tool_schema_v2.yaml` - Tool schema specification

**Export Infrastructure:**
- `model_exports/` - 80 CSV files with model field data
- Auto-discovery system (ensures 100% coverage)
- Verification tooling (validates completeness)

### 1.2 Current Gaps

**Parameter Mapping:**
- ❌ No formal mapping between tool params → method params
- ❌ No transformation rules defined
- ❌ No validation of parameter compatibility
- ❌ No bidirectional mapping (input/output)

**Orchestration:**
- ❌ No distinction between method params vs orchestration params
- ❌ No standardized orchestration parameter catalog
- ❌ No execution control metadata

**Pattern Recognition:**
- ❌ No systematic analysis of parameter patterns
- ❌ No common transformation catalog
- ❌ No reusable mapping templates

**Meta-Tooling:**
- ❌ No tools for analyzing tool/method/model relationships
- ❌ No consistency validation tools
- ❌ No automated mapping generation

---

## Part 2: Classification Dimensions

### 2.1 Tool Classification

**Existing Dimensions:**
- `category` - Organization grouping (e.g., "casefiles", "communication")
- `tags` - Discovery/filtering (e.g., ["workspace", "create"])
- `version` - Tool version (semver)

**Proposed Extensions:**
```yaml
classification:
  # Existing
  category: string          # Organization grouping
  tags: list[string]        # Discovery keywords
  
  # NEW: Execution patterns
  execution_pattern: enum   # simple, composite, pipeline, orchestrator
  complexity_tier: enum     # basic, intermediate, advanced
  
  # NEW: Parameter handling
  parameter_strategy: enum  # direct_pass, transform, composite, orchestrated
  mapping_template: string  # Reference to reusable mapping pattern
  
  # NEW: Integration
  integration_type: enum    # internal, external, hybrid
  dependencies: list[string] # Other tools/methods required
```

### 2.2 Method Classification

**Existing Dimensions:**
- `domain` - workspace, communication, automation
- `subdomain` - casefile, gmail, tool_session, etc.
- `capability` - create, read, update, delete, process, search
- `complexity` - atomic, composite, pipeline
- `maturity` - stable, beta, alpha
- `integration_tier` - internal, external, hybrid

**Proposed Extensions:**
```yaml
classification:
  # Existing (keep all)
  domain: string
  subdomain: string
  capability: string
  complexity: string
  maturity: string
  integration_tier: string
  
  # NEW: Parameter characteristics
  parameter_profile:
    complexity: enum        # simple, moderate, complex
    nesting_depth: int      # Max depth of nested parameters
    transformation_required: bool
    
  # NEW: Data flow
  data_flow_pattern: enum  # request_response, streaming, async, batch
  side_effects: enum       # none, database, external_api, filesystem
```

### 2.3 Model Classification

**Existing Dimensions:**
- `layer` - layer_0_base, layer_1_payloads, layer_2_dtos, etc.
- `domain` - casefile_domain, tool_session_domain, etc.
- `operation` - create, read, update, delete, etc.
- `type` - request, response, payload, etc.

**Proposed Extensions:**
```yaml
classification:
  # Existing (keep all)
  layer: string
  domain: string
  operation: string
  type: string
  
  # NEW: Data characteristics
  data_profile:
    field_count: int
    has_nested_models: bool
    validation_complexity: enum  # simple, moderate, complex
    
  # NEW: Usage patterns
  usage_context: enum      # input_only, output_only, bidirectional
  reusability: enum        # specific, shared, common
```

---

## Part 3: Parameter Mapping System

### 3.1 Mapping Types

**1. Direct Mapping** - Parameter names/types match exactly
```yaml
mapping_type: direct
tool_param: title
method_param: title
transformation: none
```

**2. Transform Mapping** - Type conversion required
```yaml
mapping_type: transform
tool_param: created_date
method_param: created_at
transformation:
  type: string_to_datetime
  format: "%Y-%m-%d"
```

**3. Nested Mapping** - Extract from nested structures
```yaml
mapping_type: nested
tool_param: user.id
method_param: user_id
transformation:
  type: extract_nested
  path: ["user", "id"]
```

**4. Composite Mapping** - Combine multiple parameters
```yaml
mapping_type: composite
tool_params: [street, city, zip_code]
method_param: address
transformation:
  type: combine_fields
  template: "{street}, {city} {zip_code}"
```

**5. Orchestration Mapping** - Execution control (not passed to method)
```yaml
mapping_type: orchestration
tool_param: dry_run
method_param: null  # Not passed to method
usage: execution_control
applies_to: tool_execution_layer
```

### 3.2 Mapping Configuration Schema

```yaml
# config/parameter_mappings_v1/<ToolName>_<MethodName>_mapping.yaml

mapping_id: "create_casefile_tool_to_method"
version: "1.0.0"
tool: "create_casefile"
method: "CasefileService.create_casefile"

# Input mappings (tool → method)
input_mappings:
  - tool_param: "title"
    method_param: "title"
    mapping_type: "direct"
    required: true
    
  - tool_param: "description"
    method_param: "description"
    mapping_type: "direct"
    required: false
    
  - tool_param: "tags"
    method_param: "tags"
    mapping_type: "direct"
    transformation:
      type: "list_validation"
      rules: ["non_empty_strings"]
      
  - tool_param: "dry_run"
    method_param: null
    mapping_type: "orchestration"
    usage: "execution_preview"
    handler: "preview_executor"

# Output mappings (method → tool response)
output_mappings:
  - method_return: "casefile_id"
    tool_response: "id"
    mapping_type: "direct"
    
  - method_return: "created_timestamp"
    tool_response: "created_at"
    mapping_type: "transform"
    transformation:
      type: "datetime_to_iso_string"
      
  - method_return: "metadata"
    tool_response: "metadata"
    mapping_type: "enrich"
    enrichment:
      add_fields:
        - name: "tool_version"
          value: "from_tool_definition"
        - name: "execution_time"
          value: "from_execution_context"

# Validation rules
validation:
  input_validation:
    - check: "required_fields_present"
      fields: ["title"]
    - check: "type_compatibility"
      strict: true
      
  output_validation:
    - check: "response_schema_match"
      schema: "CreateCasefileResponse"
```

### 3.3 Transformation Catalog

**Standard Transformations:**
- `string_to_datetime` - Parse string to datetime
- `datetime_to_iso_string` - Format datetime as ISO
- `list_validation` - Validate list contents
- `extract_nested` - Extract from nested object
- `combine_fields` - Combine multiple fields
- `split_field` - Split single field into multiple
- `enum_validation` - Validate enum values
- `type_coercion` - Safe type conversion

**Custom Transformations:**
- Defined in `src/pydantic_ai_integration/transformations.py`
- Registered in transformation registry
- Reusable across mappings

---

## Part 4: Orchestration Parameter System

### 4.1 Standard Orchestration Parameters

**Execution Control:**
```yaml
orchestration_params:
  execution_control:
    - name: "dry_run"
      type: "boolean"
      description: "Preview execution without side effects"
      default: false
      handler: "preview_executor"
      
    - name: "execution_mode"
      type: "enum"
      values: ["sync", "async", "batch"]
      description: "Execution mode selection"
      default: "sync"
      handler: "execution_mode_selector"
```

**Retry and Timeout:**
```yaml
orchestration_params:
  reliability:
    - name: "timeout_seconds"
      type: "integer"
      description: "Execution timeout"
      default: 30
      min: 1
      max: 300
      handler: "timeout_enforcer"
      
    - name: "retry_policy"
      type: "object"
      description: "Retry configuration"
      default: {"max_attempts": 3, "backoff": "exponential"}
      handler: "retry_executor"
```

**Context and Session:**
```yaml
orchestration_params:
  context:
    - name: "session_id"
      type: "string"
      description: "Session context identifier"
      required: false
      handler: "session_context_manager"
      
    - name: "casefile_id"
      type: "string"
      description: "Casefile context identifier"
      required: false
      handler: "casefile_context_manager"
```

**Validation and Testing:**
```yaml
orchestration_params:
  validation:
    - name: "strict_validation"
      type: "boolean"
      description: "Enable strict validation mode"
      default: false
      handler: "validation_enforcer"
      
    - name: "validation_only"
      type: "boolean"
      description: "Validate parameters without execution"
      default: false
      handler: "validation_only_executor"
```

### 4.2 Orchestration Handler Registry

**Handler Interface:**
```python
# src/pydantic_ai_integration/orchestration_handlers.py

from abc import ABC, abstractmethod
from typing import Any, Dict

class OrchestrationHandler(ABC):
    """Base class for orchestration parameter handlers"""
    
    @abstractmethod
    async def handle(
        self,
        param_value: Any,
        tool_context: Dict[str, Any],
        execution_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Process orchestration parameter and modify execution context.
        
        Args:
            param_value: Value of orchestration parameter
            tool_context: Tool-level context
            execution_context: Current execution context
            
        Returns:
            Modified execution context
        """
        pass

# Example handlers
class DryRunHandler(OrchestrationHandler):
    async def handle(self, param_value, tool_context, execution_context):
        if param_value:
            execution_context["preview_mode"] = True
            execution_context["skip_side_effects"] = True
        return execution_context

class TimeoutHandler(OrchestrationHandler):
    async def handle(self, param_value, tool_context, execution_context):
        execution_context["timeout_seconds"] = param_value
        return execution_context
```

---

## Part 5: Implementation Phases

### Phase 1: Foundation (Week 1-2)

**Goal:** Establish classification infrastructure

**Tasks:**
1. **Extended Classification Schema**
   - Update `tool_definition.py` with new classification fields
   - Update `method_definition.py` with parameter profiles
   - Update `model_registry.py` with data profiles

2. **Mapping Schema Definition**
   - Create `parameter_mapping_schema_v1.yaml`
   - Define transformation catalog
   - Create mapping YAML template

3. **Orchestration Framework**
   - Create `orchestration_parameter_schema_v1.yaml`
   - Define standard orchestration parameters
   - Create handler base classes

**Deliverables:**
- [ ] Extended schema documentation
- [ ] Updated registry classes
- [ ] Schema validation scripts
- [ ] Template generators

### Phase 2: Analysis Tools (Week 3-4)

**Goal:** Build meta-tooling for classification

**Tasks:**
1. **Parameter Analysis Tool**
   ```bash
   python model_analysis_tools/analyze_parameter_relationships.py
   ```
   - Scan all tools and methods
   - Identify parameter patterns
   - Generate mapping templates
   - Detect potential issues

2. **Consistency Validator**
   ```bash
   python model_analysis_tools/validate_classification_consistency.py
   ```
   - Check classification completeness
   - Validate mapping definitions
   - Detect inconsistencies
   - Generate reports

3. **Mapping Generator**
   ```bash
   python model_analysis_tools/generate_parameter_mappings.py --tool "create_casefile"
   ```
   - Auto-generate mapping YAML from tool/method analysis
   - Suggest transformation types
   - Create validation rules

**Deliverables:**
- [ ] Parameter analysis tool
- [ ] Consistency validator
- [ ] Mapping generator
- [ ] Classification reports (CSV/HTML)

### Phase 3: Population (Week 5-6)

**Goal:** Populate classification system with existing tools/methods/models

**Tasks:**
1. **Classify Existing Tools**
   - Add extended classification to 36 tool YAMLs
   - Document execution patterns
   - Identify dependencies

2. **Classify Existing Methods**
   - Add parameter profiles to 34 methods
   - Document data flow patterns
   - Classify side effects

3. **Create Mappings**
   - Generate mapping YAMLs for all 36 tools
   - Validate input/output mappings
   - Define orchestration parameters

**Deliverables:**
- [ ] 36 updated tool YAMLs
- [ ] 34 updated method definitions
- [ ] 36 parameter mapping YAMLs
- [ ] Orchestration parameter catalog

### Phase 4: Integration (Week 7-8)

**Goal:** Integrate classification into runtime

**Tasks:**
1. **Mapping Executor**
   ```python
   # src/pydantic_ai_integration/mapping_executor.py
   class MappingExecutor:
       def apply_input_mappings(self, tool_params, mapping_def)
       def apply_output_mappings(self, method_result, mapping_def)
       def handle_orchestration_params(self, orch_params, handlers)
   ```

2. **Tool Decorator Enhancement**
   - Update `register_mds_tool` to use mappings
   - Add orchestration parameter handling
   - Integrate transformation engine

3. **Validation Enhancement**
   - Add mapping validation
   - Add transformation validation
   - Add orchestration validation

**Deliverables:**
- [ ] Mapping executor implementation
- [ ] Enhanced tool decorator
- [ ] Transformation engine
- [ ] Integration tests

### Phase 5: Verification (Week 9-10)

**Goal:** Validate complete system

**Tasks:**
1. **End-to-End Testing**
   - Test all 36 tools with new system
   - Validate parameter mappings
   - Test orchestration parameters
   - Performance testing

2. **Documentation**
   - Complete classification guide
   - Parameter mapping tutorial
   - Orchestration parameter reference
   - Migration guide

3. **Tooling Finalization**
   - Polish analysis tools
   - Add visualization tools
   - Create maintenance scripts

**Deliverables:**
- [ ] Complete test suite
- [ ] Full documentation
- [ ] Maintenance tooling
- [ ] Performance benchmarks

---

## Part 6: File Structure

### 6.1 Configuration Directory

```
config/
├── tool_schema_v2.yaml                    # Existing tool schema
├── methods_inventory_v1.yaml              # Existing methods inventory
├── models_inventory_v1.yaml               # Existing models inventory
│
├── classification_schemas/                 # NEW
│   ├── extended_tool_classification_v1.yaml
│   ├── extended_method_classification_v1.yaml
│   ├── extended_model_classification_v1.yaml
│   ├── parameter_mapping_schema_v1.yaml
│   └── orchestration_parameter_schema_v1.yaml
│
├── parameter_mappings_v1/                  # NEW
│   ├── CasefileService_create_casefile_mapping.yaml
│   ├── CasefileService_get_casefile_mapping.yaml
│   ├── ToolSessionService_create_session_mapping.yaml
│   └── ... (36 mapping files)
│
├── orchestration_catalog_v1/               # NEW
│   ├── execution_control_params.yaml
│   ├── reliability_params.yaml
│   ├── context_params.yaml
│   └── validation_params.yaml
│
└── methodtools_v1/                         # Existing (enhanced)
    ├── CasefileService_create_casefile_tool.yaml
    └── ... (36 tool files with extended classification)
```

### 6.2 Analysis Tools Directory

```
model_analysis_tools/
├── export_models_to_spreadsheet.py        # Existing
├── quick_model_viewer.py                  # Existing
├── verify_model_exports.py                # Existing
│
├── analyze_parameter_relationships.py     # NEW
├── validate_classification_consistency.py # NEW
├── generate_parameter_mappings.py         # NEW
├── visualize_tool_method_relationships.py # NEW
├── detect_mapping_patterns.py             # NEW
└── export_classification_reports.py       # NEW
```

### 6.3 Source Code Structure

```
src/pydantic_ai_integration/
├── tool_definition.py                     # Enhanced with extended classification
├── method_definition.py                   # Enhanced with parameter profiles
├── model_registry.py                      # Enhanced with data profiles
├── tool_decorator.py                      # Enhanced with mapping support
├── method_registry.py                     # Existing
│
├── mapping_executor.py                    # NEW - Execute parameter mappings
├── transformation_engine.py               # NEW - Apply transformations
├── orchestration_handlers.py              # NEW - Handle orchestration params
├── orchestration_registry.py              # NEW - Handler registry
└── classification_loader.py               # NEW - Load extended classification
```

---

## Part 7: Usage Examples

### 7.1 Defining a Tool with Full Classification

```yaml
# config/methodtools_v1/CasefileService_create_casefile_tool.yaml

name: "create_casefile"
description: "Create a new casefile with metadata"
version: "1.0.0"

# Extended classification
classification:
  category: "casefiles"
  tags: ["workspace", "create", "casefile"]
  execution_pattern: "simple"
  complexity_tier: "basic"
  parameter_strategy: "transform"
  mapping_template: "standard_create_operation"
  integration_type: "internal"
  dependencies: []

# Method reference
method_reference:
  service: "CasefileService"
  method: "create_casefile"

# Parameter mapping reference
parameter_mapping: "CasefileService_create_casefile_mapping.yaml"

# Tool-specific parameters (includes orchestration)
tool_params:
  # Method parameters (mapped)
  - name: "title"
    type: "string"
    description: "Casefile title"
    required: true
    min_length: 1
    max_length: 200
    
  - name: "description"
    type: "string"
    description: "Casefile description"
    required: false
    
  - name: "tags"
    type: "array"
    description: "Casefile tags"
    items: {"type": "string"}
    required: false
    
  # Orchestration parameters (not mapped to method)
  - name: "dry_run"
    type: "boolean"
    description: "Preview without creating"
    default: false
    orchestration: true
    handler: "dry_run_handler"
```

### 7.2 Defining a Parameter Mapping

```yaml
# config/parameter_mappings_v1/CasefileService_create_casefile_mapping.yaml

mapping_id: "create_casefile_tool_to_method"
version: "1.0.0"
tool: "create_casefile"
method: "CasefileService.create_casefile"

# Input mappings
input_mappings:
  - tool_param: "title"
    method_param: "title"
    mapping_type: "direct"
    required: true
    validation:
      - type: "string_length"
        min: 1
        max: 200
    
  - tool_param: "description"
    method_param: "description"
    mapping_type: "direct"
    required: false
    
  - tool_param: "tags"
    method_param: "tags"
    mapping_type: "direct"
    transformation:
      type: "list_validation"
      rules:
        - "non_empty_strings"
        - "max_length_per_item:50"
    
  # Orchestration (not passed to method)
  - tool_param: "dry_run"
    method_param: null
    mapping_type: "orchestration"
    usage: "execution_preview"

# Output mappings
output_mappings:
  - method_return: "casefile_id"
    tool_response: "id"
    mapping_type: "direct"
    
  - method_return: "created_at"
    tool_response: "created_at"
    mapping_type: "transform"
    transformation:
      type: "datetime_to_iso_string"
    
  - method_return: "metadata"
    tool_response: "metadata"
    mapping_type: "enrich"
    enrichment:
      add_fields:
        - name: "tool_version"
          source: "tool_definition.version"
        - name: "execution_timestamp"
          source: "execution_context.timestamp"

# Validation
validation:
  input_validation:
    - check: "required_fields_present"
      fields: ["title"]
    - check: "type_compatibility"
      strict: true
  output_validation:
    - check: "response_schema_match"
      schema: "CreateCasefileResponse"
```

### 7.3 Using Analysis Tools

```bash
# Analyze parameter relationships across all tools
python model_analysis_tools/analyze_parameter_relationships.py

# Output: parameter_analysis_report.csv with:
# - Tool name, method name
# - Parameter name, type, mapping type
# - Transformation required
# - Common patterns identified

# Validate classification consistency
python model_analysis_tools/validate_classification_consistency.py

# Output: consistency_report.txt with:
# - Missing classifications
# - Inconsistent naming
# - Incomplete mappings
# - Suggested fixes

# Generate mapping for new tool
python model_analysis_tools/generate_parameter_mappings.py \
  --tool "new_tool" \
  --method "ServiceName.method_name" \
  --output "config/parameter_mappings_v1/"

# Output: Auto-generated mapping YAML with:
# - Detected parameter relationships
# - Suggested transformation types
# - Validation rules
# - Orchestration parameter suggestions
```

---

## Part 8: Success Metrics

### 8.1 Completeness Metrics

- ✅ **100% Tool Classification** - All 36 tools have extended classification
- ✅ **100% Method Classification** - All 34 methods have parameter profiles
- ✅ **100% Model Classification** - All 80 models have data profiles
- ✅ **100% Mapping Coverage** - All 36 tools have parameter mappings
- ✅ **100% Orchestration Coverage** - Standard orchestration params cataloged

### 8.2 Quality Metrics

- **Consistency Score** - >95% consistent naming/structure
- **Validation Pass Rate** - 100% mappings pass validation
- **Documentation Coverage** - 100% classification fields documented
- **Test Coverage** - >90% code coverage for mapping system

### 8.3 Performance Metrics

- **Mapping Execution Time** - <10ms per tool invocation
- **Validation Time** - <5ms per parameter set
- **Registry Load Time** - <100ms for all registries
- **Analysis Tool Runtime** - <30s for complete analysis

### 8.4 Usability Metrics

- **Tool Development Time** - 50% reduction with auto-generation
- **Mapping Creation Time** - 70% reduction with templates
- **Error Detection Rate** - 90% issues caught before runtime
- **Developer Satisfaction** - >4.5/5 rating for tooling

---

## Part 9: Maintenance Strategy

### 9.1 Automated Validation

**Daily Checks:**
```bash
# Run comprehensive validation
python scripts/daily_classification_check.py

# Checks:
# - Registry consistency
# - Mapping completeness
# - Orchestration handler availability
# - Schema validation
```

**Pre-Commit Hooks:**
```bash
# .git/hooks/pre-commit
python model_analysis_tools/validate_classification_consistency.py --strict
python model_analysis_tools/validate_parameter_mappings.py --all
```

### 9.2 Version Control

**Classification Versioning:**
- Use semver for classification schemas
- Track schema migrations
- Maintain backward compatibility

**Change Management:**
- Document all classification changes
- Review mapping updates
- Validate impact analysis

### 9.3 Documentation Updates

**Auto-Generated Docs:**
- Parameter mapping reference
- Orchestration parameter catalog
- Classification field dictionary
- Pattern library

**Manual Docs:**
- Classification philosophy
- Best practices guide
- Migration guides
- Troubleshooting guide

---

## Part 10: Next Steps

### Immediate Actions (This Week)

1. **Review and Approve Plan**
   - Stakeholder review
   - Technical feasibility assessment
   - Timeline validation
   - Resource allocation

2. **Create Foundation**
   - Set up directory structure
   - Create schema templates
   - Initialize new configuration files
   - Set up version control

3. **Build First Tools**
   - Implement parameter analysis tool
   - Create mapping generator
   - Build consistency validator
   - Test with sample data

### Short-Term Goals (Weeks 1-4)

- Complete Phase 1 (Foundation)
- Complete Phase 2 (Analysis Tools)
- Start Phase 3 (Population)
- Create first 10 parameter mappings

### Long-Term Goals (Months 2-3)

- Complete all phases
- Full system integration
- Comprehensive documentation
- Performance optimization
- Community feedback integration

---

## Appendix A: Reference Architecture

### A.1 Data Flow

```
User Request
    ↓
Tool Layer (with orchestration params)
    ↓
Parameter Mapping Layer
    ├─→ Method Parameters (transformed)
    └─→ Orchestration Parameters (handled separately)
    ↓
Method Execution
    ↓
Response Mapping Layer
    ├─→ Method Results (transformed)
    └─→ Metadata Enrichment (added)
    ↓
Tool Response
    ↓
User
```

### A.2 Classification Hierarchy

```
System
├── Tools (36)
│   ├── Classification
│   │   ├── Category
│   │   ├── Tags
│   │   ├── Execution Pattern
│   │   └── Parameter Strategy
│   ├── Parameters
│   │   ├── Method Parameters (mapped)
│   │   └── Orchestration Parameters (handled)
│   └── Mapping Reference
│
├── Methods (34)
│   ├── Classification
│   │   ├── Domain/Subdomain
│   │   ├── Capability
│   │   ├── Complexity
│   │   └── Integration Tier
│   ├── Parameter Profile
│   │   ├── Complexity
│   │   └── Nesting Depth
│   └── Data Flow Pattern
│
└── Models (80)
    ├── Classification
    │   ├── Layer
    │   ├── Domain
    │   └── Operation
    ├── Data Profile
    │   ├── Field Count
    │   └── Validation Complexity
    └── Usage Context
```

### A.3 Technology Stack

**Configuration:**
- YAML for definitions
- JSON Schema for validation
- CSV for analysis exports

**Implementation:**
- Python 3.13+
- Pydantic for validation
- Type hints for safety

**Tooling:**
- AST parsing for analysis
- Template engines for generation
- Reporting libraries for visualization

---

## Appendix B: Related Documentation

### Archived Documents (Foundation)
- `docs/archive/ANALYTICAL_TOOLSET_ENGINEERING.md` - Classification philosophy
- `docs/archive/TOOL_DEVELOPMENT_WORKFLOW.md` - Development lifecycle
- `docs/archive/METHOD_PARAMETER_INTEGRATION.md` - Parameter mapping concepts
- `docs/archive/PARAMETER_MAPPING_ANALYSIS.md` - Bidirectional mapping & orchestration

### Configuration Files
- `config/tool_schema_v2.yaml` - Tool schema specification
- `config/methods_inventory_v1.yaml` - Method definitions
- `config/models_inventory_v1.yaml` - Model catalog

### Registry Documentation
- `src/pydantic_ai_integration/tool_definition.py` - Tool definition class
- `src/pydantic_ai_integration/method_definition.py` - Method definition class
- `src/pydantic_ai_integration/model_registry.py` - Model registry class

---

## Document Control

**Version History:**
- v1.0.0 (2025-10-11) - Initial plan created

**Approval:**
- [ ] Technical Lead
- [ ] Project Owner
- [ ] Architecture Review

**Next Review:** 2025-10-18

---

**End of Grand Classification Plan v1.0.0**
