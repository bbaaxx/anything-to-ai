# Task Completion Checklist

## Before Handoff

1. **All tests must pass**:
   ```bash
   uv run pytest
   ```
   Or for coverage gate:
   ```bash
   ./run_coverage.sh
   ```

2. **Code must be lint-clean**:
   ```bash
   uv run ruff check .
   uv run ruff format .
   ```

3. **File length compliance** (if applicable):
   ```bash
   uv run python check_file_lengths.py
   ```

## Pre-commit

Pre-commit hooks run automatically on commit. They:
- Fix simple issues automatically (imports, whitespace, formatting)
- Report complex issues requiring manual fixes

Bypass with `git commit --no-verify` ONLY for:
- Emergency hotfixes
- Tool malfunction
- WIP commits during local experimentation

## Best Practices

- Write/update tests before implementation
- Keep module boundaries tight
- Preserve CLI and Python API parity
- Output contracts: stdout for results, stderr for diagnostics
- Non-zero exit codes on failures
- Never commit secrets - use env vars/flags
- Update README.md for user-visible changes