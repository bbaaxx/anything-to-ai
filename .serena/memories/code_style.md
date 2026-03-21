# Code Style and Conventions

## Formatting

- **Line length**: 250 characters
- **Quotes**: Double quotes
- **Indent**: Spaces (2 spaces via Ruff)
- **Tool**: Ruff for both linting and formatting

## Imports

- Group as: stdlib → third-party → local
- Use absolute imports for cross-module references (`anyfile_to_ai...`)
- Use relative imports within a module when it improves clarity
- Remove unused imports

## Types

- Type hints for public functions/methods and important internal helpers
- Prefer modern syntax: `list[str]`, `dict[str, Any]`, `X | None`
- Keep return types explicit
- Avoid broad `Any` when concrete types are available

## Naming

- **Files/modules**: `snake_case.py`
- **Functions/variables**: `snake_case`
- **Classes/exceptions**: `PascalCase`
- **Constants**: `UPPER_SNAKE_CASE`
- **Tests**: `test_*.py` files, `Test*` classes, `test_*` functions

## Error Handling

- Raise explicit exceptions with clear, actionable messages
- Library layers: exception-based (no process exits)
- CLI entry points: map failures to stable exit codes
- Maintain backward-compatible error contracts
- Never silently swallow exceptions

## Docstrings

- NO COMMENTS unless explicitly requested
- Docstrings are acceptable for public APIs

## Ruff Ignore Rules

Key allowed patterns:
- `E501`: Line too long (handled by formatter)
- `T201`: Print statements (intentional in CLI)
- `ARG001/002/005`: Unused arguments (false positives in mocks)
- `F401`: Unused imports (for type checking)
- `PTH*`: os.path usage (compatibility preserved)