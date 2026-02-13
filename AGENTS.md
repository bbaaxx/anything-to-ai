# Repository Guidelines For Coding Agents

This guide is for autonomous coding agents working in this repository.

## Agent Quickstart Checklist

- Read `.specify/memory/constitution.md` before planning changes.
- Identify affected module(s) under `anyfile_to_ai/` and keep boundaries tight.
- Write or update failing tests first (unit/integration/contract as needed).
- Implement the smallest safe change that satisfies tests and contracts.
- Run `uv run ruff check .`, `uv run ruff format .`, and targeted pytest runs.
- Run `uv run pytest` (or `./run_coverage.sh` for explicit coverage gate) before handoff.
- Update `README.md` / module README / CLI help for user-visible changes.

## Rule Priority

1. `.specify/memory/constitution.md` (authoritative)
2. `AGENTS.md` (agent execution rules)
3. `CLAUDE.md` (tooling and project command reference)
4. Module docs in `anyfile_to_ai/*/README.md`

## Repository Snapshot

- Python: 3.11+
- Package root: `anyfile_to_ai/`
- Main modules: `pdf_extractor`, `image_processor`, `audio_processor`,
  `text_summarizer`, `llm_client`, `progress_tracker`, `document_converter`
- Tests: `tests/unit`, `tests/integration`, `tests/contract`
- Tooling: `uv`, `pytest`, `ruff`, `pre-commit`
- Coverage gate: 80%

## Constitution-Aligned Delivery Rules

- Keep features module-first; avoid unnecessary cross-module coupling.
- Preserve CLI and Python API parity for user-facing features.
- Implement tests first (or update failing tests before implementation).
- Keep output contracts stable: stdout for results, stderr for diagnostics,
  non-zero exit codes on failures.
- Never commit secrets; use env vars/flags for provider/model settings.
- Update docs for user-visible behavior/config changes in the same PR.

## Setup And Common Commands

### Environment Setup

```bash
uv sync
uv run pre-commit install
```

### Lint / Format

```bash
uv run ruff check .
uv run ruff format .
uv run pre-commit run --all-files
```

### Full Test Runs

```bash
uv run pytest
./run_tests_fast.sh
./run_coverage.sh
```

## Single-Test Execution (Use Often)

Run one file:

```bash
uv run pytest tests/unit/test_chunker.py
./run_tests_fast.sh tests/unit/test_chunker.py
```

Run one test function:

```bash
uv run pytest tests/unit/test_chunker.py::TestChunkText::test_empty_text_raises_value_error
./run_tests_fast.sh tests/unit/test_chunker.py::TestChunkText::test_empty_text_raises_value_error
```

Run by expression/marker:

```bash
uv run pytest -k "timestamp and not integration"
uv run pytest -m "integration"
uv run pytest -m "contract"
uv run pytest -m "slow"
```

Run a suite directory:

```bash
uv run pytest tests/unit
uv run pytest tests/integration
uv run pytest tests/contract
```

## Code Style Standards

## Formatting And Linting

- Use Ruff for both lint and format.
- Line length: 250.
- Prefer double quotes.
- Do not add new lint ignores unless unavoidable and justified.

## Imports

- Group imports as: stdlib, third-party, local.
- Prefer absolute imports for cross-module references (`anyfile_to_ai...`).
- Use relative imports within a module package when it improves clarity.
- Remove unused imports unless intentionally used for public API/type-checking.

## Types And Interfaces

- Add type hints for public functions/methods and important internal helpers.
- Prefer modern syntax (`list[str]`, `dict[str, Any]`, `X | None`).
- Keep return types explicit.
- Avoid broad `Any` when a concrete protocol/type is available.

## Naming

- Files/modules: `snake_case.py`
- Functions/variables: `snake_case`
- Classes/exceptions: `PascalCase`
- Constants: `UPPER_SNAKE_CASE`
- Tests: files `test_*.py`, classes `Test*`, functions `test_*`

## Error Handling

- Raise explicit exceptions with clear, actionable messages.
- Keep library layers exception-based; avoid process exits in non-CLI code.
- In CLI entry points, map failures to stable exit codes.
- Maintain backward-compatible error and output contracts where feasible.
- Do not silently swallow exceptions.

## Testing Standards

- Every behavior change requires tests.
- Start with unit tests; add integration/contract tests when interfaces change.
- For CLI/API contract changes, include contract tests.
- Mark slow or external-dependency tests (`slow`, `integration`, `contract`,
  `flaky`) appropriately.
- Keep tests deterministic and isolated.

## Security And Configuration

- Never commit credentials or tokens.
- Configure providers/models via env vars or flags (for example
  `PROVIDER`, `BASE_URL`, `TEXT_MODEL`, `VISION_MODEL`).
- Document new config keys/defaults in the affected module README.

## Documentation Update Rules

When behavior changes, update as needed in the same change:

- `README.md` (project-level user impact)
- `anyfile_to_ai/*/README.md` (module usage and options)
- CLI help text and examples

## Cursor / Copilot Rules Check

- No Cursor rules found: `.cursor/rules/` and `.cursorrules` are absent.
- No Copilot instructions found: `.github/copilot-instructions.md` is absent.

If these files are added later, merge their requirements into this guide.

## Active Technologies
- Python 3.11+ + standard library (`pathlib`, `urllib.parse`), `markitdown[all]` (optional route dependency), existing backend modules (`pdf_extractor`, `image_processor`, `audio_processor`) (016-markitdown-bridge)
- N/A (stateless conversion routing/normalization) (016-markitdown-bridge)
- Python 3.11+ + Python standard library (`json`, `typing`, `dataclasses`/typed models), existing module formatter inputs from `pdf_extractor`, `image_processor`, `audio_processor`, `text_summarizer`, `document_converter` (017-output-formatter-unification)
- N/A (in-memory formatting transforms) (017-output-formatter-unification)

## Recent Changes
- 016-markitdown-bridge: Added Python 3.11+ + standard library (`pathlib`, `urllib.parse`), `markitdown[all]` (optional route dependency), existing backend modules (`pdf_extractor`, `image_processor`, `audio_processor`)
