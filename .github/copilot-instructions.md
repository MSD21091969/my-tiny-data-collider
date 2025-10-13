# AI Instructions - Tiny Data Collider

## 1. What is "Tiny Data Collider"

**What:**
- Application repository: FastAPI-based data integration and API orchestration platform
- Tech stack: FastAPI, Python 3.13+, Pydantic, Google Cloud (Firestore, Cloud Run)
- Analysis toolset: Uses my-tiny-toolset for code inspection and documentation

**Who:**
- Developed by: AI coding assistants (Copilot, agents) + human oversight
- Maintained by: MSD21091969
- Toolset: MSD21091969/my-tiny-toolset

**Where:**
- Repository: https://github.com/MSD21091969/my-tiny-data-collider.git
- Toolset: https://github.com/MSD21091969/my-tiny-toolset.git
- Outputs: `.tool-outputs/` (gitignored, local only)

**How:**
- AI assistants use toolset to analyze code structure before/after changes
- Tools run from this directory, outputs appear in `.tool-outputs/`
- Environment variable: `$env:MY_TOOLSET` points to toolset location

---

## 2. Practices

**Communication:**
- Chat responses: Short, dry, no emojis (developers, not managers)
- Report analysis results in chat when making significant changes
- Update existing documents, do not create new ones without approval

**Code Maintenance:**
- Run analysis before major changes (baseline)
- Re-run analysis after changes (verification)
- Include analysis summary in PR descriptions
- Maintain backward compatibility in API changes

**Documentation:**
- Keep README.md current with architectural changes
- Update API documentation when endpoints change
- Single source of truth: avoid duplicate information

---

## 3. Toolset Usage

**Available tools** via `$env:MY_TOOLSET`:

| Tool | Purpose | When to Use |
|------|---------|-------------|
| `version_tracker.py` | Full analysis + Git history | Before PR, after refactoring |
| `code_analyzer.py` | Quick structure check | During development |
| `mapping_analyzer.py` | Model relationships | When changing data models |
| `excel_exporter.py` | Stakeholder reports | For documentation/review |

**Common commands:**
```powershell
# Quick analysis
python $env:MY_TOOLSET\version_tracker.py . --version 1.0.0 --json

# Full report for PR
python $env:MY_TOOLSET\version_tracker.py . --version PR-123 --json --yaml --html

# Model relationships
python $env:MY_TOOLSET\mapping_analyzer.py . --html

# Excel report
python $env:MY_TOOLSET\excel_exporter.py . --output analysis.xlsx
```

---

## 4. AI Workflow

**Before coding:**
1. Run baseline analysis: `python $env:MY_TOOLSET\version_tracker.py . --version baseline --json`
2. Review current structure in `.tool-outputs/analysis/version_analysis.json`
3. Understand existing models, endpoints, relationships

**During coding:**
1. Make changes based on requirements
2. Quick checks: `python $env:MY_TOOLSET\code_analyzer.py .`
3. Verify changes don't break existing patterns

**After coding:**
1. Run full analysis: `python $env:MY_TOOLSET\version_tracker.py . --version current --json`
2. Compare with baseline
3. Generate mapping report: `python $env:MY_TOOLSET\mapping_analyzer.py . --html`
4. Review outputs in `.tool-outputs/`

**Before PR:**
1. Full analysis with all formats
2. Include summary in PR description
3. Highlight breaking changes if any

---

## 5. Output Structure

**`.tool-outputs/` contains:**
- `analysis/` - JSON/YAML analysis data (models, functions, endpoints)
- `mappings/` - Relationship diagrams (HTML dashboards)
- `docs/` - Generated documentation (HTML reports)
- `excel/` - Spreadsheet reports
- `README.md` - Explains contents (auto-generated)

**All gitignored** - copy what you need before cleanup.

---

## 6. Quick Reference

**When user asks "what models do we have?"** → Run code_analyzer, check `.tool-outputs/analysis/`  
**When user asks "how are things connected?"** → Run mapping_analyzer, open dashboard  
**When user asks "document this"** → Run version_tracker with --html  
**Before committing major changes** → Run full analysis, verify outputs  
**If unclear about structure** → Check existing analysis in `.tool-outputs/`
