# Cleanup Script for Orphaned Files

**Date:** October 2, 2025  
**Purpose:** Remove duplicate/orphaned files from old tool factory iterations

---

## 🗑️ Files to Remove

### **1. Orphaned `generated/` Folder (Root Level)**

**Location:** `C:\Users\Geurt\Documents\VScode\my-tiny-data-collider\generated\`

**Why Remove:**
- This is an OLD output directory from early tool factory versions
- The OFFICIAL location is: `src/pydantic_ai_integration/tools/generated/`
- Tests are in: `tests/generated/`
- This root-level folder is a duplicate and not used

**Contents:**
```
generated/
├── tools/
│   ├── echo_tool.py         # Duplicate of src/.../tools/generated/echo_tool.py
│   └── __init__.py
├── tests/
│   ├── test_echo_tool.py    # Duplicate of tests/generated/test_echo_tool.py
│   └── __init__.py
└── __pycache__/
```

**Command to Remove:**
```powershell
Remove-Item -Recurse -Force "generated"
```

---

### **2. Schema File (Informational Only)**

**Location:** `config/tool_schema_v2.yaml`

**Status:** ✅ Keep (useful reference)

**Why Keep:**
- Documents the complete YAML schema for tool definitions
- Useful for developers creating new tools
- Not a generated file, it's documentation

---

## 🧹 Cleanup Commands

### **Option 1: Remove via PowerShell**

```powershell
# Navigate to project root
cd C:\Users\Geurt\Documents\VScode\my-tiny-data-collider

# Remove orphaned generated/ folder
Remove-Item -Recurse -Force "generated"

# Remove Python cache files globally (optional)
Get-ChildItem -Path . -Include __pycache__ -Recurse -Force | Remove-Item -Recurse -Force
```

### **Option 2: Remove via Git**

```bash
# Stage deletion
git rm -r generated/

# Commit
git commit -m "cleanup: remove orphaned generated/ folder from old tool factory"
```

---

## ✅ Verification After Cleanup

### **Check No Orphaned Files Remain**

```powershell
# Should only show config, src, tests, templates
Get-ChildItem -Directory | Select-Object Name
```

**Expected Directories:**
- `.github/`
- `.venv/`
- `config/`
- `docs/`
- `scripts/`
- `solid-config/`
- `solid-data/`
- `src/`
- `templates/`
- `tests/`

**Should NOT contain:**
- ~~`generated/`~~ ← Should be removed

### **Verify Official Generated Files Still Exist**

```powershell
# Check tool location (OFFICIAL)
Get-Item "src\pydantic_ai_integration\tools\generated\echo_tool.py"

# Check test location (OFFICIAL)
Get-Item "tests\generated\test_echo_tool.py"
```

Both should exist ✅

---

## 📂 Correct File Locations (Reference)

### **Generated Tools**
```
src/pydantic_ai_integration/tools/generated/
├── echo_tool.py           # ✅ OFFICIAL location
└── __init__.py
```

### **Generated Tests**
```
tests/generated/
├── test_echo_tool.py      # ✅ OFFICIAL location
└── __init__.py
```

### **Templates**
```
templates/
├── tool_template.py.jinja2    # ✅ Tool code template
└── test_template.py.jinja2    # ✅ Test code template
```

### **Tool Definitions**
```
config/tools/
├── echo_tool.yaml         # ✅ Tool definition
└── tool_schema_v2.yaml    # ✅ Schema reference (keep)
```

---

## 🔍 How This Happened

### **Evolution of Tool Factory Output**

1. **Early Version (Week 0):**
   - Output to root `generated/` folder
   - Simple flat structure

2. **Refactored (Week 1):**
   - Tools → `src/pydantic_ai_integration/tools/generated/`
   - Tests → `tests/generated/`
   - Better integration with project structure

3. **Result:**
   - Old `generated/` folder left behind
   - Now cleaned up ✅

---

## 📝 .gitignore Update (Recommended)

To prevent this in the future, ensure `.gitignore` excludes orphaned folders:

```gitignore
# Python cache
__pycache__/
*.py[cod]
*$py.class
*.so

# Virtual environment
.venv/
venv/
ENV/

# Generated files (if using old structure)
/generated/

# Keep official generated locations (NOT ignored)
# src/pydantic_ai_integration/tools/generated/
# tests/generated/
```

---

## ✅ Cleanup Checklist

- [ ] Remove root-level `generated/` folder
- [ ] Verify official locations still exist
- [ ] Clear Python cache files (optional)
- [ ] Update `.gitignore` (optional)
- [ ] Run tests to ensure nothing broke
- [ ] Commit cleanup changes

---

## 🎯 Expected Outcome

**Before Cleanup:**
```
my-tiny-data-collider/
├── generated/              ❌ OLD (remove)
│   ├── tools/
│   └── tests/
├── src/.../generated/      ✅ OFFICIAL
└── tests/generated/        ✅ OFFICIAL
```

**After Cleanup:**
```
my-tiny-data-collider/
├── src/.../generated/      ✅ OFFICIAL (only location)
└── tests/generated/        ✅ OFFICIAL (only location)
```

---

**Run This Next:**

```powershell
# Remove orphaned folder
Remove-Item -Recurse -Force "generated"

# Verify tests still pass
python -m pytest tests/generated/test_echo_tool.py -v

# Expected: 9 passed ✅
```

---

**Last Updated:** October 2, 2025
