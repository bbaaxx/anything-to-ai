# Testing Conventions

## Test Structure

```
tests/
├── unit/           # Fast, isolated unit tests
├── integration/    # Integration tests with external dependencies
├── contract/       # CLI/API contract tests
└── helpers/        # Test utilities
```

## Test Markers

- `@pytest.mark.flaky` - Quarantined flaky tests
- `@pytest.mark.slow` - Long-running tests
- `@pytest.mark.integration` - Integration tests
- `@pytest.mark.contract` - Contract tests

## Naming Conventions

- Test files: `test_*.py`
- Test classes: `Test*`
- Test functions: `test_*`

## Coverage

- Minimum coverage: 80%
- Run with: `./run_coverage.sh` or `uv run pytest --cov=anyfile_to_ai --cov-fail-under=80`

## Test Execution

```bash
# Single test file
uv run pytest tests/unit/test_chunker.py

# Single test function
uv run pytest tests/unit/test_chunker.py::TestChunkText::test_empty_text

# By expression
uv run pytest -k "timestamp and not integration"

# By marker
uv run pytest -m "not slow"
```

## Writing Tests

- Every behavior change requires tests
- Start with unit tests; add integration/contract when interfaces change
- For CLI/API contract changes: include contract tests
- Keep tests deterministic and isolated