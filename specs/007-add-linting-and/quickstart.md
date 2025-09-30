# Pre-commit Hooks Quickstart Guide

Quick guide for developers setting up and using pre-commit hooks in this project.

## Prerequisites

- Python 3.13+
- UV package manager installed
- Git repository cloned

## Setup (One-Time)

```bash
# 1. Install development dependencies
uv sync --group dev

# 2. Install pre-commit hooks
uv run pre-commit install

# 3. Verify installation
uv run pre-commit --version
```

## Usage

### Automatic Execution

Pre-commit hooks run automatically when you commit:

```bash
# Make changes to your code
vim my_module.py

# Stage and commit (hooks run automatically)
git add my_module.py
git commit -m "Add new feature"
```

**Expected output:**
```
ruff-lint-fix............................Passed
ruff-format..............................Passed
trailing-whitespace......................Passed
end-of-file-fixer........................Passed
check-yaml...............................Passed
[branch-name abc1234] Add new feature
 1 file changed, 10 insertions(+)
```

### Manual Execution

Run hooks manually on all files:

```bash
# Run all hooks on all files
uv run pre-commit run --all-files

# Run specific hook
uv run pre-commit run ruff --all-files
```

## Troubleshooting

### Hooks Fail with Auto-Fixable Issues

If hooks fail but fix the issues automatically:

```bash
# Re-stage the fixed files
git add .

# Try committing again
git commit -m "Your message"
```

### Hooks Fail with Manual Fixes Required

Example: High complexity (C901) or undefined names (F821)

```bash
# View the error details
# Fix the issues in your editor
vim my_module.py

# Re-stage and commit
git add my_module.py
git commit -m "Your message"
```

### When to Bypass Hooks

Use `--no-verify` only for:
- Emergency hotfixes
- Tool malfunction
- WIP commits during experimentation

```bash
git commit --no-verify -m "Emergency fix"
```

### Bypass Specific Hook

Use the `SKIP` environment variable:

```bash
# Skip ruff check only
SKIP=ruff git commit -m "Your message"
```

## Coverage Testing

Coverage is NOT run in pre-commit hooks (performance). Run manually:

```bash
# Run tests with coverage
uv run pytest

# Generate HTML coverage report
uv run pytest --cov-report=html
open htmlcov/index.html
```

## Common Issues

### "Hook not found" error

```bash
# Reinstall hooks
uv run pre-commit install
```

### Hooks take too long

```bash
# Pre-commit caches hook environments
# First run is slow, subsequent runs are fast
# Wait for cache to build (2-3 minutes first time)
```

### Python version mismatch

Ensure you're using Python 3.13:

```bash
python --version  # Should be 3.13.x
```

## Additional Resources

- Full configuration: `.pre-commit-config.yaml`
- Research decisions: `specs/007-add-linting-and/research.md`
- Bypass guidelines: `README.md` (Development Workflow section)