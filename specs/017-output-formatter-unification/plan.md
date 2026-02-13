# Implementation Plan: Shared Output Formatter Unification

**Branch**: `017-output-formatter-unification` | **Date**: 2026-02-13 | **Spec**: `specs/017-output-formatter-unification/spec.md`
**Input**: Feature specification from `specs/017-output-formatter-unification/spec.md`

## Summary

Create a shared `anyfile_to_ai/output_formatter/` package with profile-based `plain`, `markdown`, and `json` rendering, then migrate module formatter paths incrementally through compatibility shims. Keep existing CLI/Python contracts stable via failing-first tests, equivalence gates, and module-local rollback before duplicate formatter retirement.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: Python standard library (`json`, `typing`, `dataclasses`/typed models), existing module formatter inputs from `pdf_extractor`, `image_processor`, `audio_processor`, `text_summarizer`, `document_converter`
**Storage**: N/A (in-memory formatting transforms)
**Testing**: `pytest` across `tests/unit`, `tests/integration`, `tests/contract`; quality checks with `ruff`
**Target Platform**: Local CLI and Python API usage on macOS/Linux CI
**Project Type**: Single Python package (`anyfile_to_ai`)
**Performance Goals**: Maintain output equivalence and deterministic JSON serialization with no migration-time formatter regressions
**Constraints**: Preserve stdout/stderr/exit-code contracts, preserve module-specific wording/order, keep optional dependencies lazy, avoid unnecessary cross-module coupling
**Scale/Scope**: Five module profiles (`pdf`, `image`, `audio`, `text`, `document_converter`) migrated in Phases A/B/C with per-module rollback

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Pre-Research Gate

- **Module boundaries**: PASS - shared logic is scoped to `anyfile_to_ai/output_formatter/`; module-local adapters preserve boundaries.
- **Contract stability**: PASS - spec requires stable CLI/Python behavior and explicit error/output parity.
- **Test-first evidence**: PASS - unit/integration/contract failing-first tests are defined per phase and per module.
- **Secure configuration**: PASS - no new secrets/provider config channels introduced.
- **Docs and observability**: PASS - README/module README/CLI help updates are required with stable diagnostics behavior.

## Phase 0: Research Output

Research decisions are captured in `specs/017-output-formatter-unification/research.md` and resolve architecture approach, deterministic metadata/JSON policy, and phased migration/rollback strategy.

## Phase 1: Design & Contracts Output

- Data model defined in `specs/017-output-formatter-unification/data-model.md`
- API contract defined in `specs/017-output-formatter-unification/contracts/output-formatter.openapi.yaml`
- Implementation/test quickstart defined in `specs/017-output-formatter-unification/quickstart.md`

## Project Structure

### Documentation (this feature)

```text
specs/017-output-formatter-unification/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── output-formatter.openapi.yaml
└── tasks.md
```

### Source Code (repository root)
```text
anyfile_to_ai/
├── output_formatter/
│   ├── __init__.py
│   ├── interfaces.py
│   ├── profiles.py
│   ├── metadata.py
│   ├── plain.py
│   ├── markdown.py
│   ├── json_formatter.py
│   └── errors.py
├── pdf_extractor/
├── image_processor/
├── audio_processor/
├── text_summarizer/
└── document_converter/

tests/
├── helpers/
├── contract/
├── integration/
└── unit/
```

**Structure Decision**: Use the existing single-package module-first structure and add one shared formatter package while keeping module-local shim integration points.

## Phase 2 Preview (for `/speckit.tasks`)

1. Add failing unit tests for shared plain/markdown/json formatting, metadata normalization, and formatter errors.
2. Add failing integration equivalence tests per migration order (`text`, `image`, `pdf`, `audio`).
3. Add failing cross-module contract tests for required fields, metadata consistency, and error compatibility.
4. Implement shared formatter interfaces and adapters (Phase A), then migrate module call paths with module-local rollback (Phase B).
5. Retire duplicate formatter internals only after parity gates and deprecation window requirements (Phase C).
6. Run `uv run ruff check .`, `uv run ruff format .`, and `uv run pytest`; update docs in same scope.

## Post-Design Constitution Re-Check

- **Module boundaries**: PASS - responsibilities split cleanly between shared formatter package and module-owned payload generation.
- **Contract stability**: PASS - design retains existing CLI/Python signatures and explicit output/error compatibility behavior.
- **Test-first evidence**: PASS - quickstart and plan enforce failing-first tests across unit/integration/contract suites.
- **Secure configuration**: PASS - no new secret-bearing config; optional dependency behavior remains lazy/deterministic.
- **Docs and observability**: PASS - required README/module README/CLI help updates and stable diagnostics are defined.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No constitution violations identified; no exception tracking required.

## Implementation Notes (2026-02-13)

- Added shared package `anyfile_to_ai/output_formatter/` with profile validation, formatter interfaces, metadata normalization, deterministic JSON serialization, and stable formatter-layer errors.
- Added unit/contract/integration coverage for shared formatter behavior, unsupported format/profile handling, metadata include-flag enforcement, and migration equivalence checks.
- Migrated formatter call paths in `text_summarizer`, `image_processor`, and `pdf_extractor` to shared shims with module-local environment rollback toggles.
- Added opt-in shared markdown path for `audio_processor` (`ANYFILE_OUTPUT_FORMATTER_AUDIO_SHARED=1`) to preserve existing default markdown contract behavior while enabling phased migration.
- Added migration and compatibility documentation updates (`README.md`, module READMEs, `docs/output_formatter_migration.md`, quickstart verification outcomes).
