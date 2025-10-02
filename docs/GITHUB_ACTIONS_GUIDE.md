# GitHub Actions CI/CD Guide

**My Tiny Data Collider** - Automated Testing, Validation, and Deployment

---

## 🎯 Overview

This project uses **GitHub Actions** for continuous integration and deployment. Three workflows automate testing, tool validation, and branch management across all Week 2 feature branches.

---

## 📋 Workflows

### **1. CI - Test Suite** (`.github/workflows/ci.yml`)

**Triggers:**
- Push to `main`, `develop`, or any `feature/**` branch
- Pull requests to `main` or `develop`

**What It Does:**
- ✅ Runs unit tests (tool layer) on Python 3.12 & 3.13
- ✅ Runs integration tests (service layer)
- ✅ Runs API tests (HTTP layer)
- ✅ Enforces 90% code coverage
- ✅ Lints code with ruff, black, isort, mypy
- ✅ Scans for security vulnerabilities (safety, bandit)
- ✅ Validates YAML tool definitions
- ✅ Uploads coverage to Codecov
- ✅ Creates test summary in PR

**Key Jobs:**
```yaml
- test (Python 3.12, 3.13)
- lint (ruff, black, isort, mypy)
- security (safety, bandit)
- validate-yaml (YAML syntax + schema)
- summary (aggregate results)
```

**Requirements for Passing:**
- All unit tests pass (9/9 for echo_tool)
- Code coverage ≥ 90%
- No critical security vulnerabilities
- YAML definitions valid

---

### **2. Tool Generation Validator** (`.github/workflows/tool-generation.yml`)

**Triggers:**
- Pull requests that modify:
  - `config/tools/**/*.yaml`
  - `templates/**/*.jinja2`
  - `scripts/main.py` or `scripts/generate_tools.py`

**What It Does:**
- ✅ Detects changed YAML files
- ✅ Regenerates tools from YAML
- ✅ Checks if generated files match YAML definitions
- ✅ Runs tests on newly generated tools
- ✅ Validates against tool schema
- ✅ Comments on PR with results

**Key Jobs:**
```yaml
- validate-tool-generation (regenerate + test)
- test-all-tools (comprehensive tool testing)
- schema-validation (ensure YAML compliance)
```

**Failure Scenarios:**
- Generated `.py` files don't match YAML
- Tool tests fail
- YAML missing required fields

**Fix:**
```bash
# Regenerate tools locally
python -m scripts.main config/tools/*.yaml

# Commit regenerated files
git add src/pydantic_ai_integration/tools/generated/
git add tests/generated/
git commit -m "chore: regenerate tools from YAML"
```

---

### **3. Week 2 Feature Branch Monitor** (`.github/workflows/feature-branch-monitor.yml`)

**Triggers:**
- Push to any `feature/**` branch
- Pull requests to `develop`

**What It Does:**
- ✅ Identifies feature branch type (Gmail, Drive, Sheets, etc.)
- ✅ Runs branch-specific tests
- ✅ Checks PR readiness (tests, coverage, docs)
- ✅ Verifies documentation exists for feature
- ✅ Checks for merge conflicts with `develop`
- ✅ Creates PR readiness summary

**Key Jobs:**
```yaml
- identify-branch (detect feature type)
- test-feature (run targeted tests)
- pr-ready-check (comprehensive validation)
- merge-preview (dry-run merge to develop)
```

**Branch-Specific Tests:**

| Branch | Tests Run |
|--------|-----------|
| `feature/integration-test-templates` | `tests/integration/` |
| `feature/api-test-templates` | `tests/api/` |
| `feature/google-workspace-gmail` | Gmail tool tests |
| `feature/google-workspace-drive` | Drive tool tests |
| `feature/google-workspace-sheets` | Sheets tool tests |
| `feature/tool-composition` | Composition tests |

**PR Requirements:**
- [ ] All tests passing
- [ ] Coverage ≥ 90%
- [ ] Feature-specific documentation exists
- [ ] CHANGELOG.md updated (recommended)
- [ ] No merge conflicts with `develop`

---

## 🚀 Developer Workflow

### **Working on a Feature Branch**

```bash
# 1. Create/checkout your feature branch
git checkout feature/your-feature-name

# 2. Make changes (add tools, write code)
# Edit config/tools/my_tool.yaml

# 3. Generate tool locally
python -m scripts.main config/tools/my_tool.yaml

# 4. Run tests locally
python -m pytest tests/generated/test_my_tool.py -v

# 5. Commit and push
git add .
git commit -m "feat: add my_tool with X functionality"
git push origin feature/your-feature-name
```

### **What Happens Next (Automatic)**

1. **CI Workflow runs** (`.github/workflows/ci.yml`)
   - Tests execute on Python 3.12 & 3.13
   - Coverage calculated
   - Lint checks run
   - Security scan performed

2. **Tool Generation Validator runs** (if YAML changed)
   - Validates your YAML syntax
   - Checks generated files are up-to-date
   - Runs tool-specific tests

3. **Feature Branch Monitor runs**
   - Identifies your branch type
   - Runs targeted tests
   - Checks documentation

**Check Results:**
- Go to GitHub Actions tab
- See green ✅ or red ❌ status
- Click for detailed logs

---

### **Creating a Pull Request**

```bash
# 1. Push your branch
git push origin feature/your-feature-name

# 2. On GitHub, create PR
# Base: develop
# Head: feature/your-feature-name

# 3. Workflows run automatically
# - CI tests
# - Tool validation
# - PR readiness check
# - Merge conflict detection

# 4. Review bot comments
# - Test summary
# - Coverage report
# - Documentation checklist

# 5. Address any failures
# - Fix code
# - Regenerate tools if needed
# - Update docs
# - Push changes (workflows re-run)

# 6. Get approval and merge
```

---

## 📊 Monitoring Test Results

### **GitHub Actions Tab**

1. Go to repository → Actions tab
2. See all workflow runs
3. Filter by workflow name or branch
4. Click run for detailed logs

### **PR Comments**

Workflows automatically comment on PRs with:
- Test results summary
- Coverage percentage
- Tool generation status
- Documentation checklist
- Merge conflict warnings

### **Badges** (Optional)

Add to README:
```markdown
[![CI](https://github.com/MSD21091969/my-tiny-data-collider/workflows/CI%20-%20Test%20Suite/badge.svg)](https://github.com/MSD21091969/my-tiny-data-collider/actions)
[![Coverage](https://codecov.io/gh/MSD21091969/my-tiny-data-collider/branch/develop/graph/badge.svg)](https://codecov.io/gh/MSD21091969/my-tiny-data-collider)
```

---

## 🔧 Troubleshooting

### **"Tests Failed" ❌**

**Check:**
1. Click workflow run → see failed job
2. Read error message
3. Fix locally:
   ```bash
   python -m pytest tests/ -v --tb=short
   ```
4. Push fix

### **"Generated Files Out of Sync" ❌**

**Fix:**
```bash
# Regenerate all tools
python -m scripts.main config/tools/*.yaml

# Commit
git add src/pydantic_ai_integration/tools/generated/
git add tests/generated/
git commit -m "chore: regenerate tools from YAML"
git push
```

### **"Coverage Below 90%" ❌**

**Fix:**
```bash
# Check coverage locally
python -m pytest tests/ --cov=src --cov-report=term-missing

# Add tests for uncovered lines
# Commit and push
```

### **"Documentation Missing" ⚠️**

**Fix:**
```bash
# Create required docs
touch docs/YOUR_FEATURE.md

# Follow template from other docs
# Commit and push
```

### **"Merge Conflicts" ❌**

**Fix:**
```bash
# Update your branch with develop
git checkout feature/your-branch
git fetch origin
git rebase origin/develop

# Resolve conflicts
# git add <resolved files>
# git rebase --continue

# Force push (rebase changes history)
git push --force-with-lease
```

---

## 🎯 Best Practices

### **Before Pushing**

✅ Run tests locally first
```bash
python -m pytest tests/ -v
```

✅ Check coverage
```bash
python -m pytest tests/ --cov=src --cov-report=term-missing
```

✅ Validate YAML
```bash
python -m scripts.main config/tools/my_tool.yaml
```

✅ Check for uncommitted changes
```bash
git status
```

### **Commit Messages**

Follow conventional commits:
```bash
feat: add Gmail list messages tool
fix: correct parameter validation in echo_tool
docs: update GitHub Actions guide
test: add integration tests for service layer
chore: regenerate tools from updated YAML
```

### **PR Descriptions**

Include:
- What feature/fix this PR adds
- Which tools were added/modified
- Test results (all passing)
- Documentation updated
- Related issues (if any)

---

## 🛡️ Security

### **Secrets Management**

**Never commit:**
- API keys
- OAuth tokens
- Firestore credentials
- `.env` files

**Use GitHub Secrets:**
1. Repository Settings → Secrets and variables → Actions
2. Add secrets (e.g., `FIREBASE_CREDENTIALS`)
3. Reference in workflows:
   ```yaml
   env:
     FIREBASE_CREDENTIALS: ${{ secrets.FIREBASE_CREDENTIALS }}
   ```

### **Dependency Scanning**

CI workflow runs:
- **safety**: Checks for known vulnerabilities in dependencies
- **bandit**: Scans Python code for security issues

**If vulnerabilities found:**
1. Check Actions tab for details
2. Update affected packages
3. Rerun tests

---

## 📚 Additional Resources

### **GitHub Actions Documentation**
- [Workflow Syntax](https://docs.github.com/en/actions/reference/workflow-syntax-for-github-actions)
- [GitHub Actions Marketplace](https://github.com/marketplace?type=actions)
- [Secrets](https://docs.github.com/en/actions/security-guides/encrypted-secrets)

### **Project Documentation**
- [README.md](../README.md) - Project overview
- [QUICK_REFERENCE.md](../QUICK_REFERENCE.md) - Daily commands
- [FEATURE_BRANCH_STRATEGY.md](FEATURE_BRANCH_STRATEGY.md) - Branching workflow

### **Testing Guides**
- [LAYERED_ARCHITECTURE_FLOW.md](LAYERED_ARCHITECTURE_FLOW.md) - Testing at each layer

---

## 🎓 Week 2 Feature Branch Checklist

### **For Each Feature Branch:**

- [ ] Branch created from `feature/tool-factory-week1`
- [ ] Development environment setup
- [ ] Tests running locally (9/9 for echo_tool)
- [ ] Feature implemented
- [ ] YAML tools defined (if applicable)
- [ ] Tests written (unit + integration + API)
- [ ] Coverage ≥ 90%
- [ ] Documentation created (`docs/YOUR_FEATURE.md`)
- [ ] CHANGELOG.md updated
- [ ] All CI checks passing ✅
- [ ] PR created to `develop`
- [ ] PR review completed
- [ ] Merged to `develop`

---

## 🚀 Integration to Main

After all Week 2 features merged to `develop`:

```bash
# 1. Verify develop is stable
git checkout develop
git pull origin develop
python -m pytest tests/ -v --cov=src --cov-fail-under=90

# 2. Create PR from develop → main
# On GitHub: develop → main

# 3. Full regression testing runs (all workflows)

# 4. After approval, merge to main

# 5. Tag release
git checkout main
git pull origin main
git tag -a v0.2.0 -m "Week 2: Google Workspace tools + testing infrastructure"
git push origin v0.2.0
```

---

**Last Updated:** October 2, 2025  
**Version:** 0.1.0 (Week 2 CI/CD Setup)

---

**Questions?** See project README or open an issue on GitHub.
