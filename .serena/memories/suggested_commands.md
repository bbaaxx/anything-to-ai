# Development Commands

## Environment Setup

```bash
uv sync                    # Install dependencies
uv run pre-commit install  # Install pre-commit hooks
```

## Testing

```bash
# Full test suite
uv run pytest

# Fast test runner (no coverage)
./run_tests_fast.sh

# With coverage gate (80% required)
./run_coverage.sh

# Run specific test file
uv run pytest tests/unit/test_chunker.py

# Run specific test function
uv run pytest tests/unit/test_chunker.py::TestChunkText::test_empty_text_raises_value_error

# Run by marker
uv run pytest -k "timestamp and not integration"
uv run pytest -m integration
uv run pytest -m contract
uv run pytest -m slow
```

## Linting and Formatting

```bash
uv run ruff check .        # Lint
uv run ruff format .       # Format
uv run pre-commit run --all-files  # Run all pre-commit checks
```

## CLI Entrypoints

```bash
# PDF extraction
uv run pdf-extractor extract <file> [--format plain|json|csv|markdown] [--stream] [--progress]

# Image processing
uv run image-processor <files...> [--style brief|detailed|technical] [--format json|plain|markdown]

# Audio transcription
uv run audio-processor <files...> [--format plain|json|markdown] [--model tiny|base|small|medium|large|large-v3]

# Text summarization
uv run text-summarizer <file> [--format json|plain|markdown] [--stdin]

# Document conversion
uv run document-converter <path_or_url>
```

## Utility Commands (macOS/Darwin)

Standard Unix commands work: `git`, `ls`, `cd`, `grep`, `find`, `cat`