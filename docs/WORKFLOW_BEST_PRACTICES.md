# Workflow Architecture & Best Practices

**My Tiny Data Collider** - CI/CD Workflow Maintenance Guide

---

## 🏗️ Architecture Overview

### **Workflow Hierarchy**

```
┌─────────────────────────────────────────────────────────────┐
│  Reusable Workflow (Base)                                   │
│  reusable-setup.yml - Python setup, deps install            │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  Core CI Pipeline                                            │
│  ci.yml - Main test suite (unit, integration, API)          │
│  - Runs on all branches                                      │
│  - Enforces 90% coverage                                     │
│  - Linting, security, YAML validation                        │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  Specialized Workflows                                       │
│  ├─ tool-generation.yml (YAML change validation)            │
│  ├─ feature-branch-monitor.yml (Week 2 branch tracking)     │
│  ├─ auto-docs.yml (Documentation generation)                │
│  └─ parallel-branch-tests.yml (Scheduled multi-branch tests)│
└─────────────────────────────────────────────────────────────┘
```

---

## 📋 Workflow Inventory

### **1. Reusable Setup** (`reusable-setup.yml`)
**Purpose:** Shared Python environment setup  
**Called By:** Other workflows (future enhancement)  
**Key Features:**
- Parameterized Python version
- Pip caching
- Dev dependency options

**Usage Example:**
```yaml
jobs:
  test:
    uses: ./.github/workflows/reusable-setup.yml
    with:
      python-version: '3.12'
      install-dev-deps: true
```

---

### **2. Main CI Pipeline** (`ci.yml`)
**Triggers:**
- Push to `main`, `develop`, `feature/**`
- Pull requests to `main`, `develop`

**Jobs:**
1. **test** - Multi-version Python testing (3.12, 3.13)
2. **lint** - Code quality + YAML validation
3. **security** - Vulnerability scanning
4. **validate-yaml** - Tool spec validation
5. **summary** - Aggregate results

**Key Metrics:**
- ✅ 90% coverage required
- ✅ Zero critical security vulnerabilities
- ✅ All YAML specs valid
- ✅ All tests passing

**Artifacts:**
- Test results (JUnit XML)
- Coverage reports (HTML, XML)
- Security scan reports

---

### **3. Tool Generation Validator** (`tool-generation.yml`)
**Triggers:**
- Changes to `config/tools/**/*.yaml`
- Changes to `templates/**/*.jinja2`
- Changes to generation scripts

**Jobs:**
1. **validate-tool-generation** - Regenerate + verify
2. **test-all-tools** - Individual tool tests
3. **schema-validation** - YAML compliance

**Key Features:**
- Detects YAML changes
- Regenerates tools
- Compares with committed files
- Posts PR comment with detailed results + links

**PR Comment Includes:**
- Test results summary
- Changed files list
- Direct links to artifacts
- Review checklist

---

### **4. Feature Branch Monitor** (`feature-branch-monitor.yml`)
**Triggers:**
- Push to `feature/**` branches
- Pull requests to `develop`

**Jobs:**
1. **identify-branch** - Detect feature type (Gmail, Drive, etc.)
2. **test-feature** - Branch-specific tests
3. **pr-ready-check** - Merge requirements
4. **merge-preview** - Dry-run merge

**Branch Detection:**
```yaml
feature/integration-test-templates → integration-tests
feature/api-test-templates → api-tests
feature/google-workspace-gmail → gmail-tools
feature/google-workspace-drive → drive-tools
feature/google-workspace-sheets → sheets-tools
feature/tool-composition → composition
```

**PR Requirements Enforced:**
- All tests passing
- Coverage ≥ 90%
- Documentation exists
- No merge conflicts
- CHANGELOG updated (warning)

---

### **5. Auto Documentation** (`auto-docs.yml`)
**Triggers:**
- Push to `develop`/`main` with YAML changes
- Pull requests with YAML changes

**Jobs:**
1. **generate-tool-catalog** - Auto-generate `docs/TOOL_CATALOG.md`
2. **validate-tool-docs** - Check feature docs exist

**Key Features:**
- Generates comprehensive tool catalog from YAML
- Auto-commits to `develop` on push
- Posts PR preview in comments
- Validates Gmail/Drive/Sheets docs exist

**Generated Catalog Includes:**
- Tool parameters with constraints
- Policy configurations
- Usage examples
- YAML source references

---

### **6. Parallel Branch Tests** (`parallel-branch-tests.yml`)
**Triggers:**
- Scheduled: Every 6 hours
- Manual: `workflow_dispatch`

**Jobs:**
1. **discover-branches** - Find all `feature/**` branches
2. **test-branches** - Matrix test all branches
3. **summarize** - Aggregate report + create issue if failures

**Key Features:**
- Tests all feature branches in parallel
- Uploads per-branch test results + coverage
- Creates GitHub Issue if failures detected
- Step summary with branch status table

**Manual Trigger:**
```bash
gh workflow run parallel-branch-tests.yml -f branches="feature/gmail,feature/drive"
```

---

## 🎯 Design Principles

### **1. Fail Fast, Fail Loudly**
- Tests run in parallel jobs
- Critical failures block merge
- Warnings don't fail builds (use `continue-on-error`)

### **2. Artifact Everything**
- Test results (JUnit XML)
- Coverage reports (XML, HTML)
- Security scan outputs
- Generated documentation

### **3. Developer-Friendly Feedback**
- Rich PR comments with links
- Direct links to artifacts
- Review checklists
- Clear failure messages

### **4. Separation of Concerns**
- Core CI (`ci.yml`) - always runs
- Specialized workflows - context-specific
- Reusable components - shared setup

### **5. Idempotency**
- Workflows can be re-run safely
- Auto-commit uses `[skip ci]` to prevent loops
- Matrix tests are independent

---

## 🔧 Maintenance Guidelines

### **Adding a New Workflow**

1. **Create workflow file**
   ```bash
   touch .github/workflows/my-new-workflow.yml
   ```

2. **Follow naming convention**
   - Use kebab-case: `my-workflow-name.yml`
   - Descriptive names: `test-google-apis.yml`

3. **Include metadata**
   ```yaml
   name: Human-Readable Name
   
   # Clear trigger descriptions
   on:
     push:
       branches: [main, develop]
   ```

4. **Use reusable setup (if applicable)**
   ```yaml
   jobs:
     setup:
       uses: ./.github/workflows/reusable-setup.yml
   ```

5. **Add documentation**
   - Update this file
   - Add to `docs/GITHUB_ACTIONS_GUIDE.md`

---

### **Updating Existing Workflows**

**Before Modifying:**
- [ ] Read current workflow thoroughly
- [ ] Understand all jobs and dependencies
- [ ] Check for downstream impacts
- [ ] Test in feature branch first

**Checklist:**
- [ ] Update `name` if behavior changes
- [ ] Add comments for complex logic
- [ ] Test with `workflow_dispatch` if possible
- [ ] Update documentation
- [ ] Verify no breaking changes

**Testing Strategy:**
```bash
# 1. Create test branch
git checkout -b test/workflow-update

# 2. Modify workflow
# Edit .github/workflows/ci.yml

# 3. Push and verify
git push origin test/workflow-update

# 4. Check Actions tab for results

# 5. Merge if passing
```

---

### **Debugging Workflow Failures**

**Step 1: Identify Failed Job**
- Go to Actions tab
- Click failed run
- Expand failed job
- Read error message

**Step 2: Reproduce Locally**
```bash
# For test failures
python -m pytest tests/ -v --tb=short

# For linting
ruff check src/
black --check src/
isort --check-only src/

# For YAML validation
yamllint config/tools/
```

**Step 3: Common Issues**

| Issue | Symptom | Fix |
|-------|---------|-----|
| **Missing dependency** | `ModuleNotFoundError` | Add to `requirements.txt` |
| **Tests failing** | Red X on test job | Fix tests locally first |
| **Coverage drop** | Coverage < 90% | Add tests for uncovered code |
| **YAML lint error** | yamllint failure | Fix YAML formatting |
| **Generated files out of sync** | Tool validation fails | Regenerate: `python -m scripts.main config/tools/*.yaml` |
| **Merge conflict** | Merge preview fails | Rebase on target branch |

**Step 4: Re-run Workflow**
- Click "Re-run all jobs" button
- Or push another commit

---

## 📊 Monitoring & Observability

### **Key Metrics to Track**

1. **Build Success Rate**
   - Target: >95%
   - Alert if <90%

2. **Average Build Time**
   - Target: <5 minutes
   - Monitor for degradation

3. **Test Coverage**
   - Target: ≥90%
   - Enforce in CI

4. **Deployment Frequency**
   - Track merges to `main`
   - Aim for regular cadence

### **Setting Up Alerts**

**GitHub Issues:**
- Parallel branch tests create issues on failure
- Consider adding to other critical workflows

**Branch Protection:**
```yaml
# In repository settings
Branches → Branch protection rules

For develop:
  ✅ Require status checks:
    - CI - Test Suite
    - Tool Generation Validator
  ✅ Require conversation resolution
  ✅ Include administrators (optional)
```

### **Workflow Analytics**

Access via:
- Repository → Insights → Actions
- See: run duration, success rate, most used workflows

---

## 🚀 Optimization Strategies

### **1. Cache Aggressively**

**Current Caching:**
- Pip packages (`actions/setup-python` with `cache: 'pip'`)
- Python packages (`actions/cache@v4`)

**Consider Adding:**
```yaml
- name: Cache pytest results
  uses: actions/cache@v4
  with:
    path: .pytest_cache
    key: pytest-${{ hashFiles('tests/**') }}
```

### **2. Parallel Job Execution**

**Current:**
- Test job runs 2 Python versions in parallel
- Lint, security, validate-yaml run in parallel

**Optimization:**
- Split tests by layer (unit, integration, API) into separate jobs
- Use matrix for multiple OS (Ubuntu, Windows, macOS)

### **3. Conditional Job Execution**

**Already Implemented:**
- Integration/API tests use `continue-on-error` during Week 2
- Tool generation only runs on YAML changes

**Best Practice:**
```yaml
jobs:
  expensive-job:
    if: |
      github.event_name == 'push' &&
      contains(github.event.head_commit.message, '[full-test]')
```

### **4. Artifact Retention**

**Current:** Default (90 days)

**Consider:**
```yaml
- uses: actions/upload-artifact@v4
  with:
    name: test-results
    path: test-results.xml
    retention-days: 30  # Reduce storage costs
```

---

## 🛡️ Security Best Practices

### **1. Secrets Management**

**Use GitHub Secrets:**
```yaml
env:
  FIREBASE_CREDENTIALS: ${{ secrets.FIREBASE_CREDENTIALS }}
  GOOGLE_CLIENT_SECRET: ${{ secrets.GOOGLE_CLIENT_SECRET }}
```

**Never:**
- Commit secrets to repository
- Echo secrets in logs
- Use secrets in pull requests from forks

### **2. Permissions**

**Principle of Least Privilege:**
```yaml
permissions:
  contents: read        # Read code
  issues: write         # Create issues (parallel-branch-tests)
  pull-requests: write  # Comment on PRs
```

### **3. Dependency Pinning**

**Current:**
```yaml
uses: actions/checkout@v4        # Good: major version
uses: actions/setup-python@v5    # Good: major version
```

**Consider:**
```yaml
uses: actions/checkout@v4.1.1    # Better: pinned version
# But requires more maintenance
```

### **4. Vulnerability Scanning**

**Already Implemented:**
- `safety` checks Python dependencies
- `bandit` scans Python code

**Monitor:**
- Review security job failures
- Update vulnerable dependencies promptly

---

## 📚 Resources

### **GitHub Actions Documentation**
- [Workflow Syntax](https://docs.github.com/en/actions/reference/workflow-syntax-for-github-actions)
- [Contexts](https://docs.github.com/en/actions/reference/context-and-expression-syntax-for-github-actions)
- [Workflow Commands](https://docs.github.com/en/actions/reference/workflow-commands-for-github-actions)

### **Best Practices Guides**
- [GitHub Actions Best Practices](https://docs.github.com/en/actions/guides/best-practices-for-workflows)
- [Security Hardening](https://docs.github.com/en/actions/security-guides/security-hardening-for-github-actions)

### **Project Documentation**
- [GitHub Actions Guide](GITHUB_ACTIONS_GUIDE.md) - User-facing guide
- [Feature Branch Strategy](FEATURE_BRANCH_STRATEGY.md) - Branching workflow
- [README.md](../README.md) - Project overview

---

## 🎓 Workflow Evolution Plan

### **Phase 1: Current (Week 2)** ✅
- Core CI pipeline
- Tool generation validation
- Feature branch monitoring
- Auto-documentation
- Parallel branch testing

### **Phase 2: Enhancement (Week 3-4)**
- [ ] Deployment workflows (staging → production)
- [ ] Performance benchmarking
- [ ] Visual regression testing
- [ ] E2E API testing with real services
- [ ] Slack/Discord notifications

### **Phase 3: Advanced (Month 2+)**
- [ ] Multi-region deployment
- [ ] Canary releases
- [ ] Rollback automation
- [ ] Custom GitHub Actions
- [ ] Self-hosted runners (if needed)

---

## 📝 Change Log Template

When modifying workflows, document changes:

```markdown
## Workflow Updates - YYYY-MM-DD

### Changed: `ci.yml`
- Added YAML linting step
- Enhanced PR comment with direct links
- Increased coverage threshold to 90%

**Impact:** All PRs now require passing linting
**Migration:** Developers should run `yamllint config/tools/` locally

### Added: `parallel-branch-tests.yml`
- Scheduled testing of all feature branches
- Auto-creates issues on failure

**Impact:** Better visibility into branch health
**Migration:** None required
```

---

**Last Updated:** October 2, 2025  
**Maintainers:** Tool Engineering Team  
**Contact:** See project README

---

**Related Documentation:**
- [GitHub Actions Guide](GITHUB_ACTIONS_GUIDE.md) - Developer guide
- [CI/CD Setup Complete](.github/CICD_SETUP_COMPLETE.md) - Setup instructions
