# 📤 Workflow Outputs & Inputs Guide

**Date:** October 2, 2025  
**Purpose:** Understanding what workflows produce and what they need

---

## 🎯 Quick Answer

**Q: "What usable output do workflows produce?"**  
**A:** Test results, coverage reports, artifacts, and status badges!

**Q: "Do workflows need input/parameters?"**  
**A:** Some do! Manual workflows need inputs, automated ones use git context.

---

## 📤 Workflow Outputs (Usable Artifacts)

### 1. **ci.yml** - Main CI/CD Pipeline

#### Outputs You Can Download:
- **Test Results** (JUnit XML)
  - `test-results-3.12.xml` - Python 3.12 test results
  - `test-results-3.13.xml` - Python 3.13 test results
  - Location: Actions → Workflow run → Artifacts
  
- **Coverage Report** (XML + HTML)
  - `coverage.xml` - Machine-readable coverage data
  - `htmlcov/` - Human-readable HTML report
  - Uploaded to Codecov automatically
  
- **Linting Reports**
  - ruff violations
  - black formatting issues
  - isort import order problems
  - mypy type errors
  - yamllint YAML issues
  
**How to access:**
```bash
# Via GitHub CLI
gh run download <run-id> --name test-results-3.12

# Via Web UI
Actions → Click workflow run → Scroll to Artifacts section → Download
```

#### Status Outputs (For Other Workflows):
```yaml
outputs:
  test_status: ${{ steps.test.outcome }}
  coverage: ${{ steps.coverage.outputs.coverage_percent }}
```

### 2. **tool-generation.yml** - Tool Factory Validation

#### Outputs You Can Download:
- **Generated Tool Files**
  - Regenerated Python tools from YAML
  - Diff showing changes (if any)
  - Location: PR comments + Artifacts
  
- **Validation Report**
  - Tool consistency check
  - Schema compliance report
  - Missing/extra files report

**How to access:**
```bash
# Artifacts
gh run download <run-id> --name generated-tools

# PR Comments (automatic)
# Appears directly in PR conversation
```

#### PR Comment Example:
```markdown
## 🛠️ Tool Generation Report

### Changed YAML Files
- config/tools/gmail_send.yaml

### Regenerated Tools
✅ src/pydantic_ai_integration/tools/generated/gmail_send.py
✅ tests/generated/test_gmail_send.py

### Validation
✅ All tools consistent with YAML specs
✅ No schema violations

[Download artifacts](link-to-artifacts)
```

### 3. **auto-docs.yml** - Documentation Generation

#### Outputs:
- **TOOL_CATALOG.md**
  - Auto-generated from all YAML tool specs
  - Lists all available tools
  - Shows parameters, descriptions, examples
  - Automatically committed to develop branch

**How to access:**
```bash
# File is auto-committed, just pull
git pull origin develop

# Or view on GitHub
https://github.com/MSD21091969/my-tiny-data-collider/blob/develop/TOOL_CATALOG.md
```

### 4. **parallel-branch-tests.yml** - Multi-Branch Testing

#### Outputs:
- **Consolidated Test Report**
  - Test status for all 6 feature branches
  - Pass/fail summary matrix
  - Detailed logs for failures
  
- **GitHub Issue** (if failures detected)
  - Automatically created with title: "🚨 Branch Test Failures Detected"
  - Lists failing branches
  - Links to failure logs
  - Assigns to maintainers

**Example Issue:**
```markdown
## 🚨 Branch Test Failures Detected

**Run ID:** 123456789
**Date:** October 2, 2025

### Failed Branches
- ❌ feature/google-workspace-gmail
  - Test: test_gmail_send_message FAILED
  - Log: [View details](link)

### Passing Branches
- ✅ feature/integration-test-templates
- ✅ feature/api-test-templates
- ✅ feature/google-workspace-drive
- ✅ feature/google-workspace-sheets
- ✅ feature/tool-composition

### Action Required
Review and fix failing tests on gmail branch.
```

### 5. **dev-session-readiness.yml** - Team Kickoff Check

#### Outputs:
- **Readiness Report** (JSON)
  ```json
  {
    "develop_health": "healthy",
    "feature_branches": {
      "integration-test-templates": "ready",
      "api-test-templates": "ready",
      "google-workspace-gmail": "ready",
      "google-workspace-drive": "ready",
      "google-workspace-sheets": "ready",
      "tool-composition": "ready"
    },
    "issues_status": {
      "total": 6,
      "open": 6,
      "closed": 0
    },
    "recommendations": [
      "All systems operational",
      "Ready for Week 2 kickoff"
    ]
  }
  ```

- **Team Kickoff Checklist** (Markdown)
  - Emailed/posted to team channel
  - Lists action items
  - Shows branch assignments

### 6. **feature-branch-monitor.yml** - Branch Health

#### Outputs:
- **Branch Health Dashboard** (Markdown)
  ```markdown
  # Branch Health Report
  
  ## Active Branches
  - feature/integration-test-templates (2 days old) ✅
  - feature/api-test-templates (2 days old) ✅
  
  ## Stale Branches (>7 days)
  - feature/old-experiment (15 days old) ⚠️
  
  ## Recommendations
  - Merge or close stale branches
  ```

---

## 📥 Workflow Inputs (Parameters)

### Automatic Workflows (No Input Required)

These run automatically based on git events:

#### 1. **ci.yml**
**Triggers:** Push or PR to any branch  
**Inputs:** None (uses git context)  
**Auto-detected:**
- Branch name
- Commit SHA
- Changed files
- PR number (if applicable)

#### 2. **tool-generation.yml**
**Triggers:** Push or PR to any branch  
**Inputs:** None  
**Auto-detected:**
- Changed YAML files
- Base branch for comparison
- PR metadata

#### 3. **auto-docs.yml**
**Triggers:** Push to develop/main with tool changes  
**Inputs:** None  
**Auto-detected:**
- Changed tool YAML files
- Commit message
- Author

---

### Manual Workflows (Input Required)

These need user input to run:

#### 1. **dev-session-readiness.yml**

**How to run:**
```bash
# Via GitHub CLI
gh workflow run dev-session-readiness.yml \
  --field check_type=team-kickoff \
  --field notify_team=true

# Via GitHub Web UI
Actions → dev-session-readiness.yml → Run workflow → Fill form
```

**Input Parameters:**
```yaml
check_type:
  type: choice
  options:
    - quick-health      # Fast health check only
    - full-validation   # Complete validation suite
    - team-kickoff      # Full report for team meeting
  required: true

notify_team:
  type: boolean
  default: false
  description: Send notification to team channel
```

**Example Usage:**
```bash
# Quick check before starting work
gh workflow run dev-session-readiness.yml --field check_type=quick-health

# Full validation before release
gh workflow run dev-session-readiness.yml --field check_type=full-validation

# Team kickoff with notifications
gh workflow run dev-session-readiness.yml \
  --field check_type=team-kickoff \
  --field notify_team=true
```

#### 2. **parallel-branch-tests.yml**

**How to run manually:**
```bash
# Via GitHub CLI
gh workflow run parallel-branch-tests.yml

# Via GitHub Web UI
Actions → parallel-branch-tests.yml → Run workflow
```

**Input Parameters:**
```yaml
# No inputs required for manual run
# Uses default: test all feature branches
```

**Note:** Also runs automatically every 6 hours via schedule.

---

## 🎯 Practical Examples

### Example 1: Download Test Results After Failure

```bash
# 1. Find the failed run
gh run list --workflow=ci.yml --limit 5

# 2. Download test results
gh run download 123456789 --name test-results-3.12

# 3. View locally
cat test-results-3.12.xml | grep "FAILED"
```

### Example 2: Check Coverage Report

```bash
# 1. Run workflow (if not already run)
git push origin feature/my-branch

# 2. Wait for completion, then visit Codecov
# https://codecov.io/gh/MSD21091969/my-tiny-data-collider

# 3. Or download coverage.xml artifact
gh run download <run-id> --name coverage
```

### Example 3: Trigger Team Kickoff Check

```bash
# Full team kickoff validation
gh workflow run dev-session-readiness.yml \
  --field check_type=team-kickoff \
  --field notify_team=false

# Wait for completion
gh run watch

# View output
gh run view --log
```

### Example 4: View Auto-Generated Tool Catalog

```bash
# After pushing new tool YAML
git push origin develop

# auto-docs.yml runs automatically
# Wait ~2 minutes, then pull
git pull origin develop

# View the catalog
cat TOOL_CATALOG.md
```

---

## 📊 Status Badges (Visual Outputs)

### Add to README.md

```markdown
![CI Status](https://github.com/MSD21091969/my-tiny-data-collider/actions/workflows/ci.yml/badge.svg)
![Tool Generation](https://github.com/MSD21091969/my-tiny-data-collider/actions/workflows/tool-generation.yml/badge.svg)
![Coverage](https://codecov.io/gh/MSD21091969/my-tiny-data-collider/branch/develop/graph/badge.svg)
```

**Visual Output:**
- 🟢 Green badge = passing
- 🔴 Red badge = failing
- 🟡 Yellow badge = in progress

---

## 🔍 Understanding "No YAML changes" Output

**Question:** *"Expected outcome: GREEN ✅ Reason: No YAML changes in last commits - so??"*

**Answer:**

The `tool-generation.yml` workflow:

1. **Detects changed YAML files** in `config/tools/`
2. **If no YAML changes detected:**
   - Workflow still runs (for validation)
   - But skips regeneration step
   - Reports: "No tools to regenerate"
   - Exits with GREEN ✅ (success)
   
3. **If YAML changes detected:**
   - Regenerates Python from YAML
   - Compares with committed files
   - Reports differences (if any)
   - Comments on PR with changes

**Current Status:**
```
Last commits: "ci: Trigger workflows" (only added BRANCH_INFO.txt)
Tool YAMLs: No changes
Result: Workflow runs validation, reports "No YAML changes", exits GREEN ✅
```

**This is GOOD!** ✅ It means:
- Tool Factory is working
- No inconsistencies between YAML and Python
- All tools are in sync
- Safe to develop

---

## 💡 Key Takeaways

### Outputs You Should Care About:
1. ✅ **Test results** - Download if tests fail
2. ✅ **Coverage reports** - Check on Codecov
3. ✅ **TOOL_CATALOG.md** - Auto-updated documentation
4. ✅ **GitHub Issues** - Auto-created for failures
5. ✅ **Status badges** - Visual health indicators

### Inputs You May Need:
1. 🎯 **dev-session-readiness.yml** - Manual trigger for kickoff
2. 🎯 **check_type parameter** - Choose validation level
3. 🎯 **notify_team parameter** - Send team notifications

### Automatic = No Input Needed:
- ci.yml ✅
- tool-generation.yml ✅
- auto-docs.yml ✅
- Scheduled workflows ✅

---

## 🚀 Next Steps

1. **Monitor current runs** - All should be GREEN ✅
2. **Download artifacts** if you want detailed reports
3. **Trigger manual workflow** when ready for team kickoff
4. **Start development** - CI/CD handles the rest!

---

**Questions Answered!** ✅  
Workflows produce usable outputs AND run mostly automatically.
