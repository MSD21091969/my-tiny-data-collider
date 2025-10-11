# Model Analysis Tools

## Purpose

Tools for analyzing Pydantic models. Uses systematic auto-discovery to ensure completeness.

## Scripts

### export_models_to_spreadsheet.py

Exports all Pydantic models to CSV files. Uses systematic auto-discovery of directories.

Usage:
```
python model_analysis_tools/export_models_to_spreadsheet.py
```

Features:
- Auto-discovers all subdirectories in src/pydantic_models/
- No hardcoded category lists
- Automatically finds new model directories you add

Output: Creates model_exports/ directory with 80+ CSV files organized by category.

### quick_model_viewer.py

View model structure without importing dependencies.

Usage:
```
python model_analysis_tools/quick_model_viewer.py
python model_analysis_tools/quick_model_viewer.py src/pydantic_models/canonical/casefile.py
```

Output: Displays model fields, types, and requirements in terminal.

### verify_model_exports.py

Verifies all models are exported. Compares source code against exported CSVs.

Usage:
```
python model_analysis_tools/verify_model_exports.py
```

Output: Shows model counts by category, identifies missing exports.

## Systematic Approach

The export script uses auto-discovery instead of hardcoded categories:
- Scans src/pydantic_models/ for all subdirectories
- Processes any directory containing Python files
- Automatically includes new directories you add
- No manual configuration needed

This ensures you never miss models from new directories.

## Systematic Update Workflow

To ensure reliable output after code changes:

1. Make changes to your Pydantic models
2. Run export: `python model_analysis_tools/export_models_to_spreadsheet.py`
3. Verify completeness: `python model_analysis_tools/verify_model_exports.py`
4. Check output shows "Status: OK - All models exported"

The verification tool compares source code against exported CSVs to catch missing models.

## Output Location

All generated files are in: model_exports/
