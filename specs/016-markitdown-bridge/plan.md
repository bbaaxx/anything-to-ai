# Implementation Plan: MarkItDown Bridge Contract Stabilization

**Branch**: `016-markitdown-bridge` | **Date**: 2026-02-12 | **Spec**: `specs/016-markitdown-bridge/spec.md`
**Input**: Feature specification from `specs/016-markitdown-bridge/spec.md`

## Summary

Formalize and harden the existing `document_converter` bridge contract without expanding scope into formatter unification. The plan centers on deterministic routing guarantees, typed error boundaries, a minimal CLI parity contract surface, normalized output compatibility guardrails, and targeted test coverage expansion (unit/integration/contract) to prevent contract drift.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: standard library (`pathlib`, `urllib.parse`), `markitdown[all]` (optional route dependency), existing backend modules (`pdf_extractor`, `image_processor`, `audio_processor`)
**Storage**: N/A (stateless conversion routing/normalization)
**Testing**: `pytest` with suites in `tests/unit`, `tests/integration`, `tests/contract`
**Target Platform**: Local CLI/automation environments on macOS/Linux CI with optional dependency variability
**Project Type**: Single Python package (`anyfile_to_ai`)
**Performance Goals**: Deterministic route classification with no additional network calls for local routed inputs; targeted converter unit suite completes in <=30 seconds in CI baseline runs
**Constraints**: Preserve backward compatibility for existing specialized routes; include minimal `document_converter` CLI parity surface; formatter unification explicitly out of scope
**Scale/Scope**: Contract hardening for one module (`anyfile_to_ai/document_converter`) plus related tests and spec artifacts

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Pre-Research Gate

- **Module boundaries**: PASS - work remains within `anyfile_to_ai/document_converter` plus tests and spec docs; no new cross-module formatter abstraction.
- **Contract stability**: PASS - Python API and minimal CLI parity are both explicitly contracted for source input, metadata behavior, and failure semantics.
- **Test-first evidence**: PASS - plan requires failing-first additions across unit/integration/contract suites before implementation edits.
- **Secure configuration**: PASS - no new secrets/config channels; optional dependency errors provide install guidance.
- **Docs and observability**: PASS - spec + planning artifacts updated; user-facing docs only if runtime behavior changes.

## Phase 0: Research Output

Research decisions are captured in `specs/016-markitdown-bridge/research.md` and resolve routing precedence, error taxonomy boundaries, and deterministic test isolation strategy.

## Phase 1: Design & Contracts Output

- Data model defined in `specs/016-markitdown-bridge/data-model.md`
- API contract artifact defined in `specs/016-markitdown-bridge/contracts/document-converter.openapi.yaml`
- Implementation/test quickstart defined in `specs/016-markitdown-bridge/quickstart.md`

## Project Structure

### Documentation (this feature)

```text
specs/016-markitdown-bridge/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── document-converter.openapi.yaml
└── tasks.md
```

### Source Code (repository root)

```text
anyfile_to_ai/
├── document_converter/
│   ├── __init__.py
│   ├── __main__.py
│   ├── converter.py
│   ├── exceptions.py
│   ├── models.py
│   └── routing.py
├── pdf_extractor/
├── image_processor/
└── audio_processor/

tests/
├── helpers/
│   ├── __init__.py
│   ├── document_converter_fakes.py
│   └── document_converter_sources.py
├── unit/
│   ├── test_document_converter.py
│   └── test_document_converter_errors.py
├── integration/
│   └── test_document_converter_routing.py
└── contract/
    ├── test_document_converter_contracts.py
    └── test_document_converter_cli_contracts.py
```

**Structure Decision**: Keep a module-first single-package structure. Limit code changes to `document_converter` and test suites; do not introduce new top-level packages or shared formatter modules in this phase.

## Phase 2 Preview (for `/speckit.tasks`)

1. Add failing unit tests for precedence and error-boundary gaps (including non-HTTP/HTTPS scheme handling).
2. Add failing integration and contract tests for route/output guarantees and CLI parity behavior.
3. Implement minimal code adjustments required to satisfy added tests, including minimal CLI entry point and script registration.
4. Validate with `uv run ruff check .`, `uv run ruff format .`, and targeted/full pytest runs.
5. Update docs and release notes for user-visible contract behavior changes.

## Post-Design Constitution Re-Check

- **Module boundaries**: PASS - design artifacts preserve module-local implementation and do not couple formatter internals.
- **Contract stability**: PASS - stable required output fields, typed error semantics, and minimal CLI parity behavior are explicitly contracted.
- **Test-first evidence**: PASS - explicit failing-first test sequence captured in quickstart and phase preview.
- **Secure configuration**: PASS - optional dependency handling remains lazy; no secret-bearing configuration added.
- **Docs and observability**: PASS - contract documentation artifacts created; no unresolved observability regressions introduced.

## Complexity Tracking

No constitution violations identified; no exception tracking required.
