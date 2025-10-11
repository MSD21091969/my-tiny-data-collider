# Registry Validation CI/CD

This directory contains GitHub Actions workflows for automated registry validation.

## Workflows

### Registry Validation (`registry-validation.yml`)

Automatically validates method and tool registries on every push and pull request.

**Jobs:**

1. **validate-registries**: Runs the validation script in STRICT mode
   - Checks method-tool coverage
   - Validates registry consistency  
   - Detects YAML-code drift
   - Fails the build if errors are found

2. **test-registries**: Runs comprehensive test suite
   - Executes 52 registry and integration tests
   - Generates coverage reports
   - Uploads coverage artifacts

**Triggers:**
- Push to `main`, `develop`, or `feature/*` branches
- Pull requests to `main` or `develop`
- Manual workflow dispatch

**Configuration:**
- Python 3.12
- STRICT validation mode
- Full drift detection enabled
- Coverage reporting with artifacts

## Local Validation

Run the same checks locally before pushing:

```bash
# Run validation script
python scripts/validate_registries.py --strict --verbose

# Run registry tests
python -m pytest tests/registry/ tests/test_integration_init.py -v

# Run with coverage
python -m pytest tests/registry/ tests/test_integration_init.py --cov=src/pydantic_ai_integration/registry --cov-report=html
```

## Validation Script Usage

The `scripts/validate_registries.py` script provides flexible validation options:

```bash
# Default (STRICT mode with drift detection)
python scripts/validate_registries.py

# WARNING mode (log errors but don't fail)
python scripts/validate_registries.py --warning

# Skip drift detection
python scripts/validate_registries.py --no-drift

# Verbose output
python scripts/validate_registries.py --verbose

# Quiet mode (errors only)
python scripts/validate_registries.py --quiet
```

**Environment Variables:**
- `REGISTRY_STRICT_VALIDATION`: Set to `'true'` for STRICT mode (default)
- `SKIP_DRIFT_DETECTION`: Set to `'true'` to skip drift detection

**Exit Codes:**
- `0`: All validations passed
- `1`: Validation errors found (in STRICT mode)
- `2`: Script execution error

## Integration with PRs

The workflow automatically runs on all pull requests and provides:

✅ **Passing checks**: PR can be merged  
❌ **Failing checks**: Blocking - must be fixed before merge  
⚠️  **Warnings**: Non-blocking information

## Coverage Reports

Coverage reports are automatically generated and uploaded as artifacts:

1. Go to Actions tab in GitHub
2. Select a workflow run
3. Download "coverage-report" artifact
4. Open `htmlcov/index.html` in browser

## Troubleshooting

### Validation Failures

If validation fails, check the workflow logs for:
- **Coverage errors**: Missing tools or orphaned tools
- **Consistency errors**: Duplicate names, missing fields
- **Drift errors**: Methods in code but not YAML, or vice versa

### Local Testing

To replicate CI environment locally:

```bash
# Set up virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -e .[dev]

# Run validation
python scripts/validate_registries.py --strict
```

### Debug Mode

For detailed debugging:

```bash
# Enable verbose logging
python scripts/validate_registries.py --verbose

# Check specific validation steps
python -c "from src.pydantic_ai_integration.registry import RegistryLoader; loader = RegistryLoader(); result = loader.load_all_registries(); print(result)"
```

## Maintenance

### Updating Workflows

When modifying workflows:

1. Test changes locally with `act` (GitHub Actions local runner)
2. Create PR with workflow changes
3. Verify workflow runs successfully on PR
4. Merge only after successful validation

### Adding New Validations

To add new validation checks:

1. Add validator function in `src/pydantic_ai_integration/registry/validators.py`
2. Integrate into `RegistryLoader.load_all_registries()`
3. Add tests in `tests/registry/test_validators.py`
4. Update documentation

### Caching

The workflow uses pip caching for faster runs. To clear cache:

1. Go to Actions → Caches
2. Delete old caches
3. Next run will rebuild cache

## Best Practices

✅ **DO:**
- Run validation locally before pushing
- Fix errors immediately when detected
- Keep registries in sync with code changes
- Review validation reports in PR checks

❌ **DON'T:**
- Disable validation checks without approval
- Merge PRs with failing validation
- Ignore drift warnings
- Skip writing tests for new validators

## Support

For issues or questions:
1. Check existing GitHub issues
2. Review validation logs in Actions tab
3. Contact maintainers for help
4. Refer to `docs/` directory for detailed documentation
