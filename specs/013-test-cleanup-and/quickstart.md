# Quickstart: Test Cleanup and Quality Assurance

## Prerequisites

- Python 3.13 installed
- Project dependencies installed: `uv install`
- Existing test suite and ruff configuration

## Initial Assessment

1. **Run current test suite**:
   ```bash
   uv run pytest
   ```

2. **Check current quality status**:
   ```bash
   uv run ruff check .
   ```

3. **Measure current coverage**:
   ```bash
   uv run pytest --cov=anyfile_to_ai --cov-report=term-missing
   ```

## Test Cleanup Process

### Step 1: Identify Failing Tests
```bash
uv run pytest --tb=short -v
```

### Step 2: Fix Import Issues
- Fix missing module imports in test files
- Ensure all modules are properly importable
- Update import paths after module reorganization

### Step 3: Address Test Failures
- Fix assertion errors
- Update test expectations to match current behavior
- Ensure test isolation (no shared state between tests)

### Step 4: Handle Flaky Tests
```bash
# Identify flaky tests
uv run pytest --reruns 3 --reruns-delay 1

# Quarantine identified flaky tests
# Add @pytest.mark.flaky to test functions
# Run stable tests only
uv run pytest -m "not flaky"
```

## Quality Assurance Process

### Step 1: Run Quality Checks
```bash
uv run ruff check . --statistics
```

### Step 2: Fix Quality Violations
```bash
# Auto-fix simple issues
uv run ruff check . --fix

# Manually fix complex issues
# Focus on complexity and maintainability metrics
```

### Step 3: Validate Atomic Fixes
```bash
# After each fix, ensure no new issues introduced
uv run pytest
uv run ruff check .
```

## Coverage Improvement

### Step 1: Identify Uncovered Code
```bash
uv run pytest --cov=anyfile_to_ai --cov-report=html
# Open htmlcov/index.html to see detailed coverage
```

### Step 2: Add Missing Tests
- Focus on critical paths first
- Add tests for error handling
- Ensure edge cases are covered

### Step 3: Validate Coverage Target
```bash
uv run pytest --cov=anyfile_to_ai --cov-fail-under=80
```

## Continuous Validation

### Pre-commit Hooks
```bash
uv run pre-commit install
uv run pre-commit run --all-files
```

### CI/CD Pipeline
- Ensure all checks pass in CI
- Monitor coverage trends
- Track quality metrics over time

## Success Criteria

✅ All tests pass without failures
✅ No ruff quality violations
✅ Minimum 80% test coverage
✅ Flaky tests quarantined
✅ Atomic fixes validated

## Troubleshooting

**Import Errors**: Check module structure and PYTHONPATH
**Test Failures**: Review test isolation and mock usage
**Quality Violations**: Focus on complexity reduction
**Coverage Gaps**: Prioritize critical business logic
