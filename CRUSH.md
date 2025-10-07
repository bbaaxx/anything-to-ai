# Development Commands
uv run pytest                    # Run all tests
uv run pytest tests/unit/test_*.py  # Run unit tests only
uv run pytest tests/contract/test_*.py  # Run contract tests only
uv run pytest -k "test_name"     # Run specific test by name
uv run ruff check .              # Lint code
uv run ruff format .             # Format code
uv run python check_file_lengths.py  # Check file lengths

# Code Style
- Python 3.13+ required
- Use dataclasses for data models
- Type hints required for all function signatures
- Custom exception hierarchy with specific error types
- Double quotes for strings, 4-space indentation
- Max line length: 250 characters
- Max file length: 250 lines (enforced)
- Use descriptive variable names (snake_case)
- Classes use PascalCase, constants use UPPER_SNAKE_CASE
- Always include docstrings for public functions and classes
