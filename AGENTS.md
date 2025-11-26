# Repository Guidelines

## Project Structure & Module Organization
- Core code lives in `anyfile_to_ai/` with module-focused packages: `pdf_extractor`, `image_processor`, `audio_processor`, `text_summarizer`, plus shared helpers (`llm_client`, `progress_tracker`, `test_quality`).
- Tests sit in `tests/` with suites split into `unit/`, `integration/`, `contract/`, and the bash-based `human_review_quick_test`; sample fixtures are in `sample-data/`.
- Specs and supporting docs are in `specs/`, release artifacts in `dist/` and `build/`, and scripts/utilities such as `check_file_lengths.py` are at repo root.

## Build, Test, and Development Commands
- Install dev deps: `uv sync`.
- Run all tests with coverage: `uv run pytest` (adds `--cov` and enforces 80% threshold).
- Targeted suites: `uv run pytest tests/unit`, `uv run pytest tests/integration`, `uv run pytest tests/contract`, or mark-based `uv run pytest -m "not slow"`.
- Human sanity check: `./tests/human_review_quick_test` (uses `sample-data/` and writes logs to `./tmp`).
- Lint/format: `uv run ruff check .` and `uv run ruff format .`; file length check: `uv run python check_file_lengths.py`.
- Build distribution (optional): `uv run python -m build`.

## Coding Style & Naming Conventions
- Python 3.11+, spaces for indent, max line length 250; formatter prefers double quotes.
- Follow Ruff defaults with configured ignores; keep CLI-friendly prints allowed in entrypoints.
- Module names are lowercase with underscores; tests follow `test_*.py` and `Test*` classes.
- Prefer type hints for public functions; keep side effects confined to CLI entrypoints or explicit runners.

## Testing Guidelines
- Framework: `pytest` with reruns enabled; markers available: `slow`, `integration`, `contract`, `flaky`.
- Coverage: threshold enforced at 80% (`--cov-report=html` outputs to `htmlcov/`).
- Add tests alongside code changes in the matching suite; use `sample-data/` for fixtures and avoid network calls.
- Name tests descriptively (`test_<behavior>`) and keep setup lightweight; mark long/model-heavy cases as `slow`.

## Commit & Pull Request Guidelines
- Git history uses conventional prefixes (`feat:`, `fix:`, `chore:`) and concise subjects; follow that style (e.g., `feat: add streaming pdf extraction`).
- For PRs: include a short problem/solution summary, linked issue or task ID, notes on model/config requirements (env vars like `VISION_MODEL`, `LLM_PROVIDER`, `LLM_MODEL`), and test evidence (`uv run pytest`, `./tests/human_review_quick_test` when relevant).
- Keep diffs small and focused; mention coverage impacts and new sample data additions.

## Security & Configuration Tips
- Do not commit model binaries or credentials; keep provider tokens and model selections in environment variables.
- When adding new processors, document required env vars and default fallbacks in module READMEs and CLI help.
