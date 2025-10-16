# AI Instructions - Tiny Data Collider

**Last Updated:** 2025-10-16

---

## 1. Repository Overview

**This is the APPLICATION repository** for a FastAPI data integration platform:  
- Pydantic validation, Google Workspace integration, casefile management, and tool execution orchestration.

**Code Assistant Role (Updated):**
- Focus on tool engineering, research, and implementing or documenting fixes/action items found in referenced MD files, especially `ROUNDTRIP_ANALYSIS.md`.
- Know all tools and codebase details; suggest improvements, research, or code/documentation changes
- Reference actionable items, plans, or fixes from `ROUNDTRIP_ANALYSIS.md`, `docs/VALIDATION_PATTERNS.md`, and other key documentation.
- Use meta-tools from the toolset repository for code analysis/documentation only, not for app logic.

**Two-repository architecture:**
- **my-tiny-data-collider**: Application code, models, services, tests.
- **my-tiny-toolset**: Meta-tools for analysis, engineering, knowledge base (see its own instructions).

**Key documents:**
- `ROUNDTRIP_ANALYSIS.md` - System state, action plan, progress tracking (PRIMARY REFERENCE)
- `docs/VALIDATION_PATTERNS.md` - Custom types, validators
- `README.md` - Overview, quick start guide

---

## 2. Practices

**Communication:**
- Short, dry, no emojis (developers, not managers)
- Report during work, summarize at completion
- Update existing documents only (no new files without approval)

**Documentation:**
- Single source of truth: No duplicate information
- Update README.md for architectural changes
- Date stamp all major docs: `**Last Updated:** YYYY-MM-DD`

**Code Maintenance:**
- Use custom types from `src/pydantic_models/base/custom_types.py`
- Use validators from `src/pydantic_models/base/validators.py`
- Focus on code, documentation, and research tasks—not test or script execution.

**Method Registration:**
- Use `@register_service_method` for new service methods (auto-registers)
- YAML (`config/methods_inventory_v1.yaml`) is for documentation only

**Knowledge Capture:**
- Discover patterns here, document in toolset repo as needed

---

## 3. Validation Framework

- See `docs/VALIDATION_PATTERNS.md` for custom types and validators
- Reference actionable items from `ROUNDTRIP_ANALYSIS.md` for engineering/research focus

---

## 4. Toolset Usage

- Use `$env:MY_TOOLSET` to reference toolset repo for analysis/documentation
- Only use toolset meta-tools for analysis (never for application code execution)

---

## 5. Session Startup Checklist

- Read system state in `ROUNDTRIP_ANALYSIS.md` for current progress/action plan
- Review engineering/research tasks in referenced docs

---

## 6. Guidance for AI Assistant

- Do NOT suggest, run, or maintain test/scripting tasks.
- Focus on engineering, documentation, and research based on actionable items in MDs.
- Always reference the latest state and plans from `ROUNDTRIP_ANALYSIS.md` and supporting docs.

---