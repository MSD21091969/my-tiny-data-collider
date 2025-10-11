# Scripts

Development and maintenance scripts organized by function.

## Categories

### analysis/
Model and tool analysis utilities.
- `analyze_model_transformations.py` - Analyze model conversion patterns
- `document_field_mappings.py` - Document field mappings between models
- `generate_model_docs.py` - Generate model documentation
- `generate_tool_coverage.py` - Generate tool coverage reports

### generators/
Code generation tools.
- `generate_mapper.py` - Generate mapper classes
- `generate_method_tools.py` - Generate tool definitions from service methods
- `generate_tools.py` - Generate tool YAML definitions

### utilities/
General utility scripts.
- `import_generated_tools.py` - Import generated tool definitions
- `scan_models.py` - Scan and catalog Pydantic models
- `show_tools.py` - Display registered tools

### validators/
Validation and verification scripts.
- `validate_dto_alignment.py` - Validate DTO alignment
- `validate_tool_definitions.py` - Validate tool YAML definitions

### visualization/
Data flow and structure visualization.
- `visualize_rar_flow.py` - Visualize Request-Action-Response flow

### workflows/
Development workflow automation.
- `tool_development_workflow.py` - End-to-end tool development workflow

## Usage

Run from project root:
```
python scripts/<category>/<script>.py
```

Example:
```
python scripts/generators/generate_method_tools.py
python scripts/validators/validate_tool_definitions.py
```
