# Tasks: PDF Text Extraction Module

**Input**: Design documents from `/specs/001-a-simple-python/`
**Prerequisites**: plan.md (required), research.md, data-model.md, contracts/

## Format: `[ID] [P?] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `pdf_extractor/`, `tests/` at repository root

## Phase 3.1: Setup

- [x] T001 Create project structure per implementation plan (ensure <250 line files)
- [x] T002 Initialize Python project with pdfplumber dependency and pytest
- [x] T003 [P] Configure linting and 250-line limit enforcement

## Phase 3.2: Tests First (TDD) ⚠️ MUST COMPLETE BEFORE 3.3

**CRITICAL: These tests MUST be written and MUST FAIL before ANY implementation**

- [x] T004 [P] Contract test extract_text() function in tests/contract/test_api.py
- [x] T005 [P] Contract test extract_text_streaming() function in tests/contract/test_api.py
- [x] T006 [P] Contract test get_pdf_info() function in tests/contract/test_api.py
- [x] T007 [P] Contract test CLI extract command in tests/integration/test_cli.py
- [x] T008 [P] Contract test CLI info command in tests/integration/test_cli.py
- [x] T009 [P] Integration test small PDF processing workflow in tests/integration/test_workflows.py
- [x] T010 [P] Integration test large PDF streaming workflow in tests/integration/test_workflows.py
- [x] T011 [P] Integration test CLI extract command in tests/integration/test_cli.py
- [x] T012 [P] Integration test error handling scenarios in tests/integration/test_workflows.py

## Phase 3.3: Core Implementation (ONLY after tests are failing)

- [x] T013 [P] Custom exception classes in pdf_extractor/exceptions.py
- [x] T014 [P] PDFDocument model class in pdf_extractor/reader.py
- [x] T015 [P] TextContent and PageResult models in pdf_extractor/reader.py
- [x] T016 [P] ProgressInfo model in pdf_extractor/progress.py
- [x] T017 [P] ExtractionConfig model in pdf_extractor/reader.py
- [x] T018 Core PDF text extraction function extract_text() in pdf_extractor/reader.py
- [x] T019 [P] Progress tracking functionality in pdf_extractor/progress.py
- [x] T020 Streaming extraction function extract_text_streaming() in pdf_extractor/streaming.py
- [x] T021 PDF info function get_pdf_info() in pdf_extractor/reader.py
- [x] T022 [P] CLI argument parsing and command dispatch in pdf_extractor/cli.py
- [x] T023 CLI extract command implementation in pdf_extractor/cli.py
- [x] T024 CLI info command implementation in pdf_extractor/cli.py
- [x] T025 Module interface and exports in pdf_extractor/**init**.py
- [x] T026 CLI entry point python -m support in pdf_extractor/**main**.py

## Phase 3.4: Integration

- [x] T027 Connect streaming to progress tracking
- [x] T028 Error handling integration across all modules
- [x] T029 CLI output formatting (plain text and JSON)
- [x] T030 Memory optimization for large file processing

## Phase 3.5: Polish

- [x] T031 [P] Unit tests for exception handling in tests/unit/test_exceptions.py
- [x] T032 [P] Unit tests for PDF reader core logic in tests/unit/test_reader.py
- [x] T033 [P] Unit tests for streaming functionality in tests/unit/test_streaming.py
- [x] T034 [P] Unit tests for progress tracking in tests/unit/test_progress.py
- [x] T035 Performance tests for large files (<reasonable processing time)
- [x] T036 Memory usage validation tests
- [x] T037 [P] Code review for 250-line rule compliance
- [x] T038 Run quickstart.md validation scenarios

## Dependencies

- Setup tasks (T001-T003) before all others
- Tests (T004-T012) before implementation (T013-T026)
- T013 (exceptions) blocks T014-T026 (all other implementation)
- T014-T017 (models) before T018-T026 (functions using models)
- T018-T021 (core functions) before T022-T026 (CLI and integration)
- T025-T026 (module interface) depends on all implementation (T013-T024)
- Implementation (T013-T026) before integration (T027-T030)
- Integration (T027-T030) before polish (T031-T038)

## Parallel Example: Phase 3.2 Tests

```bash
# Launch T004-T012 together (all different files or sections):
Task: "Contract test extract_text() function in tests/contract/test_api.py"
Task: "Contract test CLI extract command in tests/contract/test_cli.py"
Task: "Integration test small PDF workflow in tests/integration/test_workflows.py"
Task: "Integration test CLI extract command in tests/integration/test_cli.py"
```

## Parallel Example: Phase 3.3 Models

```bash
# Launch T013-T017 together (different files):
Task: "Custom exception classes in pdf_extractor/exceptions.py"
Task: "ProgressInfo model in pdf_extractor/progress.py"
Task: "CLI argument parsing in pdf_extractor/cli.py"
```

## Notes

- [P] tasks = different files, no dependencies
- Verify tests fail before implementing
- Commit after each task
- Each module must stay under 250 lines (constitutional requirement)
- Focus on modular, composable design

## Constitutional Compliance

- **250-Line Rule**: Each file (T013-T026) designed to stay under 250 lines
- **Composition-First**: Models (T014-T017) compose into functions (T018-T021)
- **Minimal Dependencies**: Only pdfplumber and pytest required
- **Modular Architecture**: Each module has single responsibility

## Task Generation Rules Applied

1. **From Contracts**:

   - api.py → T004-T006 (API contract tests)
   - cli.py → T007-T008 (CLI contract tests)
   - exceptions.py → T013 (exception implementation)

2. **From Data Model**:

   - PDFDocument → T014
   - TextContent/PageResult → T015
   - ProgressInfo → T016
   - ExtractionConfig → T017

3. **From Quickstart Scenarios**:
   - Small PDF → T009
   - Large PDF streaming → T010
   - CLI usage → T011
   - Error handling → T012

## Validation Checklist

- [x] All contracts have corresponding tests (T004-T008)
- [x] All entities have model tasks (T014-T017)
- [x] All tests come before implementation (T004-T012 → T013-T026)
- [x] Parallel tasks truly independent (different files)
- [x] Each task specifies exact file path
- [x] No task modifies same file as another [P] task
- [x] All files designed to stay under 250 lines
- [x] Modular composition enforced in task structure
- [x] Dependencies are minimal and justified (pdfplumber only)
