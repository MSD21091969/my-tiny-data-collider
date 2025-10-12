# GitHub Actions Workflows# GitHub Actions Workflows# Registry Validation CI/CD



This directory contains automated CI/CD workflows for the my-tiny-data-collider project.



## 🔄 Active WorkflowsThis directory contains automated CI/CD workflows for the my-tiny-data-collider project.This directory contains GitHub Actions workflows for automated registry validation.



### 1. Registry Validation (`registry-validation.yml`)



**Purpose**: Validates method and tool registries on every code change.## 🔄 Active Workflows## Workflows



**Triggers:**

- Push to `main`, `develop`, or `feature/*` branches

- Pull requests to `main` or `develop`### 1. Registry Validation (`registry-validation.yml`)### Registry Validation (`registry-validation.yml`)

- Manual workflow dispatch



**Jobs:**

- **validate-registries**: STRICT mode validation**Purpose**: Validates method and tool registries on every code change.Automatically validates method and tool registries on every push and pull request.

  - Method-tool coverage checks

  - Registry consistency validation

  - YAML-code drift detection

- **test-registries**: Comprehensive test suite**Triggers:****Jobs:**

  - 52+ registry and integration tests

  - Coverage reports with artifacts- Push to `main`, `develop`, or `feature/*` branches



### 2. PR Automation (`pr-automation.yml`)- Pull requests to `main` or `develop`1. **validate-registries**: Runs the validation script in STRICT mode



**Purpose**: Automates pull request lifecycle management.- Manual workflow dispatch   - Checks method-tool coverage



**Triggers:**   - Validates registry consistency  

- PR opened, synchronized, reopened

- PR reviews submitted**Jobs:**   - Detects YAML-code drift



**Jobs:**- **validate-registries**: STRICT mode validation   - Fails the build if errors are found

- **auto-assign-reviewers**: Auto-assign team members

- **auto-label-pr**: Label based on files changed and size  - Method-tool coverage checks

- **auto-merge-check**: Enable auto-merge for approved PRs

- **pr-size-check**: Warn about large PRs (>500 lines)  - Registry consistency validation2. **test-registries**: Runs comprehensive test suite



**Features:**  - YAML-code drift detection   - Executes 52 registry and integration tests

- ✅ Auto-reviewer assignment

- 🏷️ Smart labeling (tests, docs, registry, ci/cd, size)- **test-registries**: Comprehensive test suite   - Generates coverage reports

- 🤖 Auto-merge eligible PRs after approval

- 📏 Size warnings for maintainability  - 52+ registry and integration tests   - Uploads coverage artifacts



## 🎯 Workflow Integration  - Coverage reports with artifacts



### Development Lifecycle**Triggers:**

```

Create Feature Branch → Make Changes → Push to GitHub### 2. PR Automation (`pr-automation.yml`)- Push to `main`, `develop`, or `feature/*` branches

    ↓

Registry Validation + PR Auto-Actions Run- Pull requests to `main` or `develop`

    ↓

Validation Pass? → No → Fix Issues → Push Again**Purpose**: Automates pull request lifecycle management.- Manual workflow dispatch

    ↓ Yes

Tests Run → Pass? → No → Fix Issues → Push Again  

    ↓ Yes

Ready for Review → Code Review → Approved?**Triggers:****Configuration:**

    ↓ Yes

Auto-merge Enabled → Merged to Develop- PR opened, synchronized, reopened- Python 3.12

```

- PR reviews submitted- STRICT validation mode

### Quality Gates

1. **Registry Validation** - Ensures code-registry consistency- Full drift detection enabled

2. **Test Suite** - 52+ tests covering registry functionality

3. **Code Review** - Human approval required**Jobs:**- Coverage reporting with artifacts

4. **Branch Protection** - Enforced via GitHub settings

- **auto-assign-reviewers**: Auto-assign team members

## 🚦 Status Indicators

- **auto-label-pr**: Label based on files changed and size## Local Validation

### Workflow Status

- ✅ **Green**: All checks passed- **auto-merge-check**: Enable auto-merge for approved PRs

- ❌ **Red**: Failed - blocks merge

- 🟡 **Yellow**: In progress- **pr-size-check**: Warn about large PRs (>500 lines)Run the same checks locally before pushing:

- ⚪ **Gray**: Skipped/not required



### Required Checks

Both workflows must pass before PR can be merged:**Features:**```bash

- `Registry Validation / Validate Method & Tool Registries`

- `Registry Validation / Run Registry Tests`- ✅ Auto-reviewer assignment# Run validation script



## 📊 Monitoring & Reports- 🏷️ Smart labeling (tests, docs, registry, ci/cd, size)python scripts/validate_registries.py --strict --verbose



### GitHub Actions Tab- 🤖 Auto-merge eligible PRs after approval

- View all workflow runs and their status

- Access detailed logs for debugging- 📏 Size warnings for maintainability# Run registry tests

- Download coverage report artifacts

python -m pytest tests/registry/ tests/test_integration_init.py -v

### PR Integration

- Status checks visible on PR pages## 🎯 Workflow Integration

- Auto-generated comments for size warnings

- Auto-merge notifications# Run with coverage



### Coverage Reports### Development Lifecyclepython -m pytest tests/registry/ tests/test_integration_init.py --cov=src/pydantic_ai_integration/registry --cov-report=html

1. Navigate to Actions tab

2. Click on any registry validation run``````

3. Download "coverage-report" artifact

4. Open `htmlcov/index.html` for detailed coverageCreate Feature Branch → Make Changes → Push to GitHub



## 🔧 Local Development    ↓## Validation Script Usage



### Pre-commit ValidationRegistry Validation + PR Auto-Actions Run

```bash

# Run same checks as CI    ↓The `scripts/validate_registries.py` script provides flexible validation options:

python scripts/validate_registries.py --strict --verbose

python -m pytest tests/registry/ tests/test_integration_init.py -vValidation Pass? → No → Fix Issues → Push Again

```

    ↓ Yes```bash

### VS Code Tasks

Use Command Palette → Tasks: Run Task:Tests Run → Pass? → No → Fix Issues → Push Again  # Default (STRICT mode with drift detection)

- `Validate Before PR` - Run registry validation

- `Run All Tests` - Execute full test suite    ↓ Yespython scripts/validate_registries.py

- `Pre-commit Checks` - Both validation + tests

- `Full PR Workflow` - Complete end-to-end flowReady for Review → Code Review → Approved?



## 🛠️ Troubleshooting    ↓ Yes# WARNING mode (log errors but don't fail)



### Registry Validation FailuresAuto-merge Enabled → Merged to Developpython scripts/validate_registries.py --warning

- Check specific error in workflow logs

- Run validation locally: `python scripts/validate_registries.py --strict````

- Common issues: method-tool coverage, YAML syntax, drift

# Skip drift detection

### PR Automation Failures

- Review GitHub API permissions### Quality Gatespython scripts/validate_registries.py --no-drift

- Check workflow syntax

- Verify GitHub token permissions1. **Registry Validation** - Ensures code-registry consistency



### Test Failures2. **Test Suite** - 52+ tests covering registry functionality# Verbose output

- Review test logs in Actions tab

- Run tests locally: `pytest tests/registry/ -v`3. **Code Review** - Human approval requiredpython scripts/validate_registries.py --verbose

- Check for environment differences

4. **Branch Protection** - Enforced via GitHub settings

## 📋 Best Practices

# Quiet mode (errors only)

### ✅ DO

- Run validation locally before pushing## 🚦 Status Indicatorspython scripts/validate_registries.py --quiet

- Keep PRs focused and reasonably sized

- Fill out PR templates completely```

- Review workflow logs when failures occur

- Update documentation when adding workflows### Workflow Status



### ❌ DON'T- ✅ **Green**: All checks passed**Environment Variables:**

- Bypass required status checks

- Ignore workflow failures- ❌ **Red**: Failed - blocks merge- `REGISTRY_STRICT_VALIDATION`: Set to `'true'` for STRICT mode (default)

- Create excessively large PRs (>1000 lines)

- Modify workflows without testing- 🟡 **Yellow**: In progress- `SKIP_DRIFT_DETECTION`: Set to `'true'` to skip drift detection

- Skip local validation

- ⚪ **Gray**: Skipped/not required

## 🔗 Resources

**Exit Codes:**

- [GitHub Actions Documentation](https://docs.github.com/actions)

- [Development Workflow Guide](../docs/DEVELOPMENT_WORKFLOW.md)### Required Checks- `0`: All validations passed

- [Branch Protection Setup](../BRANCH_PROTECTION.md)
Both workflows must pass before PR can be merged:- `1`: Validation errors found (in STRICT mode)

- `Registry Validation / Validate Method & Tool Registries`- `2`: Script execution error

- `Registry Validation / Run Registry Tests`

## Integration with PRs

## 📊 Monitoring & Reports

The workflow automatically runs on all pull requests and provides:

### GitHub Actions Tab

- View all workflow runs and their status✅ **Passing checks**: PR can be merged  

- Access detailed logs for debugging❌ **Failing checks**: Blocking - must be fixed before merge  

- Download coverage report artifacts⚠️  **Warnings**: Non-blocking information



### PR Integration## Coverage Reports

- Status checks visible on PR pages

- Auto-generated comments for size warningsCoverage reports are automatically generated and uploaded as artifacts:

- Auto-merge notifications

1. Go to Actions tab in GitHub

### Coverage Reports2. Select a workflow run

1. Navigate to Actions tab3. Download "coverage-report" artifact

2. Click on any registry validation run4. Open `htmlcov/index.html` in browser

3. Download "coverage-report" artifact

4. Open `htmlcov/index.html` for detailed coverage## Troubleshooting



## 🔧 Local Development### Validation Failures



### Pre-commit ValidationIf validation fails, check the workflow logs for:

```bash- **Coverage errors**: Missing tools or orphaned tools

# Run same checks as CI- **Consistency errors**: Duplicate names, missing fields

python scripts/validate_registries.py --strict --verbose- **Drift errors**: Methods in code but not YAML, or vice versa

python -m pytest tests/registry/ tests/test_integration_init.py -v

```### Local Testing



### VS Code TasksTo replicate CI environment locally:

Use Command Palette → Tasks: Run Task:

- `Validate Before PR` - Run registry validation```bash

- `Run All Tests` - Execute full test suite# Set up virtual environment

- `Pre-commit Checks` - Both validation + testspython -m venv venv

- `Full PR Workflow` - Complete end-to-end flowsource venv/bin/activate  # On Windows: venv\Scripts\activate



## 🔄 Workflow Configuration# Install dependencies

pip install -e .[dev]

### Environment Variables

- `REGISTRY_STRICT_VALIDATION`: Set to `'true'` for STRICT mode# Run validation

- `SKIP_DRIFT_DETECTION`: Set to `'true'` to skip drift detectionpython scripts/validate_registries.py --strict

```

### Branch Protection Requirements

Configure in GitHub Settings → Branches:### Debug Mode

- **main**: Require 1 approval + status checks + linear history

- **develop**: Require 1 approval + status checksFor detailed debugging:

- Auto-merge enabled for qualifying PRs

```bash

## 🛠️ Maintenance# Enable verbose logging

python scripts/validate_registries.py --verbose

### Adding New Workflows

1. Create `.yml` file in `.github/workflows/`# Check specific validation steps

2. Test locally with `act` (GitHub Actions runner)python -c "from src.pydantic_ai_integration.registry import RegistryLoader; loader = RegistryLoader(); result = loader.load_all_registries(); print(result)"

3. Create PR to test in CI environment```

4. Update this documentation

## Maintenance

### Modifying Existing Workflows

1. Edit workflow file### Updating Workflows

2. Test changes on feature branch

3. Verify workflow runs successfullyWhen modifying workflows:

4. Update documentation if needed

1. Test changes locally with `act` (GitHub Actions local runner)

### Troubleshooting Failed Workflows2. Create PR with workflow changes

3. Verify workflow runs successfully on PR

#### Registry Validation Failures4. Merge only after successful validation

- Check specific error in workflow logs

- Run validation locally: `python scripts/validate_registries.py --strict`### Adding New Validations

- Common issues: method-tool coverage, YAML syntax, drift

To add new validation checks:

#### PR Automation Failures

- Review GitHub API permissions1. Add validator function in `src/pydantic_ai_integration/registry/validators.py`

- Check workflow syntax2. Integrate into `RegistryLoader.load_all_registries()`

- Verify GitHub token permissions3. Add tests in `tests/registry/test_validators.py`

4. Update documentation

#### Test Failures

- Review test logs in Actions tab### Caching

- Run tests locally: `pytest tests/registry/ -v`

- Check for environment differencesThe workflow uses pip caching for faster runs. To clear cache:



## 📋 Best Practices1. Go to Actions → Caches

2. Delete old caches

### ✅ DO3. Next run will rebuild cache

- Run validation locally before pushing

- Keep PRs focused and reasonably sized## Best Practices

- Fill out PR templates completely

- Review workflow logs when failures occur✅ **DO:**

- Update documentation when adding workflows- Run validation locally before pushing

- Fix errors immediately when detected

### ❌ DON'T- Keep registries in sync with code changes

- Bypass required status checks- Review validation reports in PR checks

- Ignore workflow failures

- Create excessively large PRs (>1000 lines)❌ **DON'T:**

- Modify workflows without testing- Disable validation checks without approval

- Skip local validation- Merge PRs with failing validation

- Ignore drift warnings

## 🔗 Resources- Skip writing tests for new validators



- **GitHub Actions Documentation**: [docs.github.com/actions](https://docs.github.com/actions)## Support

- **Workflow Syntax**: [GitHub Workflow Syntax](https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions)

- **Local Testing**: [nektos/act](https://github.com/nektos/act)For issues or questions:

- **Development Workflow**: `../docs/DEVELOPMENT_WORKFLOW.md`1. Check existing GitHub issues

2. Review validation logs in Actions tab

## 📈 Metrics & Analytics3. Contact maintainers for help

4. Refer to `docs/` directory for detailed documentation

Track workflow performance:
- **Success Rate**: Percentage of passing runs
- **Build Time**: Average workflow duration
- **Coverage**: Test coverage trends
- **PR Throughput**: Time from creation to merge

Regular monitoring ensures efficient development process and early issue detection.