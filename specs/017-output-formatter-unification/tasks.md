# Tasks: Shared Output Formatter Unification

**Input**: Design documents from `/specs/017-output-formatter-unification/`
**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `contracts/output-formatter.openapi.yaml`, `quickstart.md`

**Tests**: Tests are REQUIRED by spec and constitution; all stories include failing-first test tasks.

**Organization**: Tasks are grouped by user story to keep each story independently implementable and testable.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Initialize shared formatter workspace and baseline fixtures.

- [X] T001 Create shared formatter package skeleton in `anyfile_to_ai/output_formatter/__init__.py`, `anyfile_to_ai/output_formatter/interfaces.py`, `anyfile_to_ai/output_formatter/profiles.py`, `anyfile_to_ai/output_formatter/metadata.py`, `anyfile_to_ai/output_formatter/plain.py`, `anyfile_to_ai/output_formatter/markdown.py`, `anyfile_to_ai/output_formatter/json_formatter.py`, and `anyfile_to_ai/output_formatter/errors.py`
- [X] T002 [P] Add shared formatter fixture builders in `tests/helpers/output_formatter_fixtures.py`
- [X] T003 [P] Add unified contract test scaffold in `tests/contract/test_output_formatter_unified_contract.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Build core shared contracts and primitives needed by every story.

**⚠️ CRITICAL**: Complete this phase before starting user story work.

- [X] T004 Implement supported profile constants and validation in `anyfile_to_ai/output_formatter/profiles.py`
- [X] T005 Implement formatter-layer error classes and mapping helpers in `anyfile_to_ai/output_formatter/errors.py`
- [X] T006 Implement metadata normalization (`processing`, `configuration`, `source`, `extensions`) in `anyfile_to_ai/output_formatter/metadata.py`
- [X] T007 Implement deterministic JSON serialization helper in `anyfile_to_ai/output_formatter/json_formatter.py`
- [X] T008 Implement shared formatter interface entry points in `anyfile_to_ai/output_formatter/interfaces.py`
- [X] T009 Wire package exports for shared formatter public API in `anyfile_to_ai/output_formatter/__init__.py`
- [X] T010 Add failing foundational tests for metadata normalization and formatter errors in `tests/unit/test_shared_output_metadata_normalization.py` and `tests/unit/test_shared_output_formatter_errors.py`

**Checkpoint**: Shared formatter foundation is stable and ready for story implementation.

---

## Phase 3: User Story 1 - Approve a Single Formatter Architecture (Priority: P1) 🎯 MVP

**Goal**: Deliver canonical shared `plain`, `markdown`, and `json` formatter behavior backed by the accepted architecture.

**Independent Test**: Run shared unit + contract tests to verify canonical formatting, metadata inclusion rules, and explicit unsupported-format behavior.

### Tests for User Story 1 (REQUIRED) ⚠️

- [X] T011 [P] [US1] Add failing plain-format profile parity tests in `tests/unit/test_shared_output_formatter_plain.py`
- [X] T012 [P] [US1] Add failing markdown heading/ordering parity tests in `tests/unit/test_shared_output_formatter_markdown.py`
- [X] T013 [P] [US1] Add failing JSON required-field and include-metadata tests in `tests/unit/test_shared_output_formatter_json.py`
- [X] T014 [P] [US1] Add failing contract tests for `/format` and `unsupported_format` behavior in `tests/contract/test_output_formatter_unified_contract.py`
- [X] T015 [P] [US1] Add failing contract tests for `/format/plain`, `/format/markdown`, and `/format/json` in `tests/contract/test_output_formatter_unified_contract.py`

### Implementation for User Story 1

- [X] T016 [US1] Implement profile-aware plain rendering behavior in `anyfile_to_ai/output_formatter/plain.py`
- [X] T017 [US1] Implement profile-aware markdown rendering behavior in `anyfile_to_ai/output_formatter/markdown.py`
- [X] T018 [US1] Implement profile-aware JSON output object assembly in `anyfile_to_ai/output_formatter/json_formatter.py`
- [X] T019 [US1] Implement metadata include-flag enforcement in `anyfile_to_ai/output_formatter/interfaces.py`
- [X] T020 [US1] Implement audio timestamp formatting (`HH:MM:SS.CC`) and boundary validation in `anyfile_to_ai/output_formatter/markdown.py`
- [X] T021 [US1] Implement legacy audio markdown heading compatibility path in `anyfile_to_ai/output_formatter/markdown.py`
- [X] T022 [US1] Finalize orchestration wiring for `format_plain`, `format_markdown`, and `format_json` in `anyfile_to_ai/output_formatter/interfaces.py`

**Checkpoint**: US1 is complete and independently testable.

---

## Phase 4: User Story 2 - Migrate Incrementally Without Regressions (Priority: P2)

**Goal**: Migrate modules to shared formatter paths with per-module equivalence gates and rollback safety.

**Independent Test**: Execute each module's equivalence integration tests and contract suites after migration, validating module-local fallback behavior.

### Tests for User Story 2 (REQUIRED) ⚠️

- [X] T023 [P] [US2] Add failing text summarizer equivalence tests in `tests/integration/test_formatter_equivalence_text.py`
- [X] T024 [P] [US2] Add failing image processor equivalence tests in `tests/integration/test_formatter_equivalence_image.py`
- [X] T025 [P] [US2] Add failing PDF extractor equivalence tests in `tests/integration/test_formatter_equivalence_pdf.py`
- [X] T026 [P] [US2] Add failing audio processor equivalence tests in `tests/integration/test_formatter_equivalence_audio.py`
- [X] T027 [P] [US2] Add failing audio timestamp parity tests for shared profile in `tests/unit/test_timestamp_formatting.py`

### Implementation for User Story 2

- [X] T028 [US2] Migrate text summarizer formatter call path to shared shim in `anyfile_to_ai/text_summarizer/__main__.py`
- [X] T029 [US2] Migrate image processor formatter call path to shared shim in `anyfile_to_ai/image_processor/cli.py`
- [X] T030 [US2] Migrate PDF plain/json formatter call path to shared shim in `anyfile_to_ai/pdf_extractor/output_formatters.py`
- [X] T031 [US2] Migrate PDF markdown formatter call path to shared shim in `anyfile_to_ai/pdf_extractor/markdown_formatter.py`
- [X] T032 [US2] Migrate audio markdown formatter call path to shared shim in `anyfile_to_ai/audio_processor/markdown_formatter.py`
- [X] T033 [US2] Add document converter formatter adapter compatibility path in `anyfile_to_ai/document_converter/converter.py`
- [X] T034 [US2] Implement module-local rollback toggles in `anyfile_to_ai/text_summarizer/__main__.py`, `anyfile_to_ai/image_processor/cli.py`, `anyfile_to_ai/pdf_extractor/output_formatters.py`, and `anyfile_to_ai/audio_processor/markdown_formatter.py`
- [X] T035 [US2] Add deprecation warnings for duplicate internal formatters in `anyfile_to_ai/pdf_extractor/output_formatters.py`, `anyfile_to_ai/pdf_extractor/markdown_formatter.py`, and `anyfile_to_ai/audio_processor/markdown_formatter.py`

**Checkpoint**: US2 is complete and independently testable.

---

## Phase 5: User Story 3 - Implement With Test and Documentation Parity (Priority: P3)

**Goal**: Deliver full verification mapping and documentation parity for contributors/maintainers.

**Independent Test**: Confirm traceable test coverage and docs updates, then run full quality gates successfully.

### Tests for User Story 3 (REQUIRED) ⚠️

- [X] T036 [P] [US3] Extend unified contract tests for metadata consistency and error-path compatibility in `tests/contract/test_output_formatter_unified_contract.py`
- [X] T037 [P] [US3] Add failing CLI/API parity integration tests for migrated profiles in `tests/integration/test_formatter_cli_api_parity.py`
- [X] T038 [P] [US3] Add failing contract parity checks for existing module contracts in `tests/contract/test_cli_output.py`, `tests/contract/test_timestamp_contracts.py`, `tests/contract/test_pdf_metadata_contract.py`, and `tests/contract/test_image_metadata_contract.py`

### Implementation for User Story 3

- [X] T039 [US3] Update shared formatter architecture and compatibility policy in `README.md`
- [X] T040 [US3] Update PDF formatter contract docs in `anyfile_to_ai/pdf_extractor/README.md`
- [X] T041 [US3] Update image formatter contract docs in `anyfile_to_ai/image_processor/README.md`
- [X] T042 [US3] Update audio formatter contract docs in `anyfile_to_ai/audio_processor/README.md`
- [X] T043 [US3] Update text summarizer formatter contract docs in `anyfile_to_ai/text_summarizer/README.md`
- [X] T044 [US3] Update CLI help text for output and metadata flags in `anyfile_to_ai/text_summarizer/__main__.py` and `anyfile_to_ai/image_processor/cli.py`
- [X] T045 [US3] Add maintainer migration guide in `docs/output_formatter_migration.md`

**Checkpoint**: US3 is complete and independently testable.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final cleanup and cross-story verification.

- [X] T046 [P] Record quickstart verification command outcomes in `specs/017-output-formatter-unification/quickstart.md`
- [X] T047 Remove retired duplicate formatter internals after Phase C gates in `anyfile_to_ai/pdf_extractor/output_formatters.py`, `anyfile_to_ai/pdf_extractor/markdown_formatter.py`, and `anyfile_to_ai/audio_processor/markdown_formatter.py`
- [X] T048 [P] Refresh shared formatter fixture coverage for long-term regressions in `tests/helpers/output_formatter_fixtures.py`
- [X] T049 [P] Update implementation notes and traceability summary in `specs/017-output-formatter-unification/plan.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies.
- **Phase 2 (Foundational)**: Depends on Phase 1 and blocks all user stories.
- **Phase 3 (US1)**: Depends on Phase 2 and delivers MVP behavior.
- **Phase 4 (US2)**: Depends on US1 shared formatter implementation.
- **Phase 5 (US3)**: Depends on US1 and US2 outputs for final parity/documentation.
- **Phase 6 (Polish)**: Depends on all user stories.

### User Story Dependency Graph

- **US1 (P1) -> US2 (P2) -> US3 (P3)**

### Within Each User Story

- Write failing tests first.
- Implement behavior changes after failing tests are in place.
- Re-run story-specific suites before progressing.

---

## Parallel Execution Examples

### User Story 1

```bash
Task: "T011 [US1] in tests/unit/test_shared_output_formatter_plain.py"
Task: "T012 [US1] in tests/unit/test_shared_output_formatter_markdown.py"
Task: "T013 [US1] in tests/unit/test_shared_output_formatter_json.py"
Task: "T014 [US1] in tests/contract/test_output_formatter_unified_contract.py"
```

### User Story 2

```bash
Task: "T023 [US2] in tests/integration/test_formatter_equivalence_text.py"
Task: "T024 [US2] in tests/integration/test_formatter_equivalence_image.py"
Task: "T025 [US2] in tests/integration/test_formatter_equivalence_pdf.py"
Task: "T026 [US2] in tests/integration/test_formatter_equivalence_audio.py"
```

### User Story 3

```bash
Task: "T040 [US3] in anyfile_to_ai/pdf_extractor/README.md"
Task: "T041 [US3] in anyfile_to_ai/image_processor/README.md"
Task: "T042 [US3] in anyfile_to_ai/audio_processor/README.md"
Task: "T043 [US3] in anyfile_to_ai/text_summarizer/README.md"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phases 1-2.
2. Complete Phase 3 (US1).
3. Validate US1 independently before migration rollout.

### Incremental Delivery

1. Deliver US1 shared formatter contracts.
2. Deliver US2 module-by-module migrations with rollback.
3. Deliver US3 full parity docs/tests and final gate compliance.

### Parallel Team Strategy

1. Complete setup/foundation together.
2. In parallel, one stream implements US1 core while another prepares US2 equivalence tests.
3. After US2, run US3 docs and cross-contract parity work in parallel.

---

## Notes

- `[P]` marks tasks that can run concurrently in different files.
- `[US1]`, `[US2]`, `[US3]` map tasks directly to spec user stories.
- Keep stdout/stderr/exit-code behavior unchanged unless a separately approved contract change exists.
