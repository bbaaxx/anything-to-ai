# Tasks: Image VLM Text Description Module

**Input**: Design documents from `/specs/002-implement-a-module/`
**Prerequisites**: plan.md (required), research.md, data-model.md, contracts/

## Execution Flow (main)

```
1. Load plan.md from feature directory
   → Extract: Python 3.13, mlx-vlm, PIL/Pillow, single project structure
2. Load design documents:
   → data-model.md: 4 entities → model tasks
   → contracts/: 3 files → 12+ contract test tasks
   → quickstart.md: 6 scenarios → integration test tasks
3. Generate tasks by category:
   → Setup: project init, dependencies, linting
   → Tests: contract tests, integration tests
   → Core: models, processors, CLI commands
   → Integration: error handling, progress tracking
   → Polish: unit tests, performance, docs
4. Apply task rules:
   → Different files = mark [P] for parallel
   → Same file = sequential (no [P])
   → Tests before implementation (TDD)
5. Number tasks sequentially (T001, T002...)
6. Generate dependency graph
7. Create parallel execution examples
```

## Format: `[ID] [P?] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- Include exact file paths in descriptions

## Path Conventions

Single project structure at repository root:

- **Source**: `image_processor/` (new module following pdf_extractor pattern)
- **Tests**: `tests/contract/`, `tests/integration/`, `tests/unit/`

## Phase 3.1: Setup

- [ ] T001 Create image_processor module structure (image_processor/**init**.py, models.py, processor.py, streaming.py, exceptions.py, progress.py, cli.py)
- [ ] T002 Initialize Python 3.13 project with MLX dependencies (uv add mlx-vlm pillow)
- [ ] T003 [P] Configure linting and 250-line limit enforcement for image_processor module

## Phase 3.2: Contract Tests (TDD) ⚠️ MUST COMPLETE BEFORE 3.3

**CRITICAL: These tests MUST be written and MUST FAIL before ANY implementation**

### API Contract Tests

- [ ] T004 [P] Contract test process_image() in tests/contract/test_api_process_image.py
- [ ] T005 [P] Contract test process_images() in tests/contract/test_api_process_images.py
- [ ] T006 [P] Contract test validate_image() in tests/contract/test_api_validate_image.py
- [ ] T007 [P] Contract test get_supported_formats() in tests/contract/test_api_formats.py
- [ ] T008 [P] Contract test process_images_streaming() in tests/contract/test_api_streaming.py
- [ ] T009 [P] Contract test create_config() in tests/contract/test_api_config.py
- [ ] T010 [P] Contract test get_image_info() in tests/contract/test_api_info.py

### Exception Contract Tests

- [ ] T011 [P] Contract test exception hierarchy in tests/contract/test_exceptions.py
- [ ] T012 [P] Contract test error message formatting in tests/contract/test_error_messages.py

### CLI Contract Tests

- [ ] T013 [P] Contract test create_cli_parser() in tests/contract/test_cli_parser.py
- [ ] T014 [P] Contract test CLI main() function in tests/contract/test_cli_main.py
- [ ] T015 [P] Contract test output formatting in tests/contract/test_cli_output.py

## Phase 3.3: Integration Tests (User Scenarios)

- [ ] T016 [P] Integration test single image processing in tests/integration/test_single_image.py
- [ ] T017 [P] Integration test batch processing in tests/integration/test_batch_processing.py
- [ ] T018 [P] Integration test streaming with progress in tests/integration/test_streaming_progress.py
- [ ] T019 [P] Integration test CLI usage scenarios in tests/integration/test_cli_scenarios.py
- [ ] T020 [P] Integration test error handling workflows in tests/integration/test_error_workflows.py
- [ ] T021 [P] Integration test PDF processor integration in tests/integration/test_pdf_integration.py

## Phase 3.4: Core Implementation (ONLY after tests are failing)

### Data Models

- [ ] T022 [P] ImageDocument model in image_processor/models.py
- [ ] T023 [P] DescriptionResult model in image_processor/models.py
- [ ] T024 [P] ProcessingResult model in image_processor/models.py
- [ ] T025 [P] ProcessingConfig model in image_processor/models.py

### Exception Hierarchy

- [ ] T026 Exception hierarchy implementation in image_processor/exceptions.py

### Core Processing

- [ ] T027 VLM model loading and management in image_processor/processor.py
- [ ] T028 Image validation and preprocessing in image_processor/processor.py
- [ ] T029 Single image VLM processing in image_processor/processor.py

### Batch Processing and Progress

- [ ] T030 Batch processing engine in image_processor/streaming.py
- [ ] T031 Progress tracking system in image_processor/progress.py

### API Implementation

- [ ] T032 Core API functions (process_image, process_images) in image_processor/**init**.py
- [ ] T033 Validation API functions in image_processor/**init**.py
- [ ] T034 Configuration API functions in image_processor/**init**.py

### CLI Implementation

- [ ] T035 CLI argument parsing and validation in image_processor/cli.py
- [ ] T036 CLI output formatting (plain, JSON, CSV) in image_processor/cli.py
- [ ] T037 CLI path expansion and main entry point in image_processor/cli.py

## Phase 3.5: Integration

- [ ] T038 Error handling integration across all modules
- [ ] T039 Progress callback integration with streaming processing
- [ ] T040 Memory management and cleanup for large images
- [ ] T041 Performance optimization and resource monitoring

## Phase 3.6: Polish

- [ ] T042 [P] Unit tests for model validation in tests/unit/test_models.py
- [ ] T043 [P] Unit tests for utility functions in tests/unit/test_utils.py
- [ ] T044 [P] Performance validation (<2s per image) in tests/unit/test_performance.py
- [ ] T045 [P] Constitution compliance check (250-line limit) across all files
- [ ] T046 [P] Module integration with existing pdf_extractor patterns

## Dependencies

- Setup (T001-T003) before everything
- Contract tests (T004-T015) before implementation (T022-T041)
- Integration tests (T016-T021) before implementation
- Models (T022-T025) before core processing (T027-T029)
- Core processing (T027-T029) before batch processing (T030-T031)
- API implementation (T032-T034) after core components
- CLI (T035-T037) after API implementation
- Integration (T038-T041) after core implementation
- Polish (T042-T046) after everything

## Parallel Example

```
# Launch contract tests together (T004-T015):
Task: "Contract test process_image() in tests/contract/test_api_process_image.py"
Task: "Contract test process_images() in tests/contract/test_api_process_images.py"
Task: "Contract test validate_image() in tests/contract/test_api_validate_image.py"
Task: "Contract test exception hierarchy in tests/contract/test_exceptions.py"

# Launch model implementations together (T022-T025):
Task: "ImageDocument model in image_processor/models.py"
Task: "DescriptionResult model in image_processor/models.py"
Task: "ProcessingResult model in image_processor/models.py"
Task: "ProcessingConfig model in image_processor/models.py"
```

## Notes

- [P] tasks = different files, no dependencies
- Verify tests fail before implementing
- Each file must stay under 250 lines per constitution
- Follow existing pdf_extractor architectural patterns
- Use uv for dependency management with Python 3.13

## Task Generation Rules

_Applied during main() execution_

1. **From Contracts**:

   - contracts/api.py → 7 contract test tasks [P]
   - contracts/exceptions.py → 2 exception test tasks [P]
   - contracts/cli.py → 3 CLI test tasks [P]

2. **From Data Model**:

   - 4 entities → 4 model creation tasks [P]
   - Validation rules → utility function tasks

3. **From User Stories (quickstart.md)**:

   - 6 scenarios → 6 integration test tasks [P]

4. **Ordering**:
   - Setup → Contract Tests → Integration Tests → Models → Processing → CLI → Integration → Polish
   - Dependencies block parallel execution

## Validation Checklist

_GATE: Checked before execution_

- [x] All contracts have corresponding tests (12 contract tests for 3 contract files)
- [x] All entities have model tasks (4 models for 4 entities)
- [x] All tests come before implementation (TDD approach)
- [x] Parallel tasks truly independent (different files marked [P])
- [x] Each task specifies exact file path
- [x] No task modifies same file as another [P] task
- [x] All files designed to stay under 250 lines
- [x] Modular composition enforced in task structure
- [x] Dependencies are minimal and justified (mlx-vlm, pillow only)
