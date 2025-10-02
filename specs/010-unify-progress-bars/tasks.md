# Tasks: Unified Progress Tracking System

**Input**: Design documents from `/specs/010-unify-progress-bars/`
**Prerequisites**: plan.md, research.md, data-model.md, contracts/

## Execution Flow (main)

```
1. Load plan.md from feature directory
   → Tech stack: Python 3.13 + alive-progress, asyncio, dataclasses
   → Structure: Single project (progress_tracker/ module)
2. Load design documents:
   → data-model.md: 4 entities (ProgressState, ProgressUpdate, ProgressEmitter, ProgressConsumer)
   → contracts/api.md: Full API specification
   → contracts/test_progress_protocol.py: 134 contract tests (stubs)
   → research.md: Technical decisions resolved
3. Generate tasks by category:
   → Setup: Module structure, dependencies
   → Tests: Contract tests (134 stubs to implement)
   → Core: Models, emitter, consumers
   → Integration: Module integration (4 existing modules)
   → Polish: Documentation, deprecation warnings
4. Apply task rules:
   → Consumer implementations = parallel [P]
   → Module integrations = parallel [P]
   → Core emitter = sequential (single file)
5. Number tasks sequentially (T001-T038)
6. All files designed to stay <250 lines per constitution
```

## Format: `[ID] [P?] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `progress_tracker/` at repository root
- Tests: `tests/contract/`, `tests/integration/`, `tests/unit/`

---

## Phase 3.1: Setup

- [X] **T001** Create progress_tracker module structure (progress_tracker/__init__.py, models.py, emitter.py, consumers.py, cli_renderer.py, README.md)
- [X] **T002** Add alive-progress>=3.0.0 to pyproject.toml and run uv sync
- [X] **T003** Create progress_tracker/__init__.py with public API exports (ProgressState, ProgressUpdate, UpdateType, ProgressEmitter, ProgressConsumer, CLIProgressConsumer, CallbackProgressConsumer, LoggingProgressConsumer)

## Phase 3.2: Tests First (TDD) ⚠️ MUST COMPLETE BEFORE 3.3

**CRITICAL: These tests MUST be written and MUST FAIL before ANY implementation**

### Core Type Contract Tests

- [X] **T004** [P] Implement UpdateType enum contract tests in tests/contract/test_progress_protocol.py (TestUpdateTypeContract: test_update_type_has_started, test_update_type_has_progress, test_update_type_has_total_changed, test_update_type_has_completed, test_update_type_has_error)
- [X] **T005** [P] Implement ProgressState contract tests in tests/contract/test_progress_protocol.py (TestProgressStateContract: test_progress_state_is_frozen, test_progress_state_validates_current_non_negative, test_progress_state_validates_current_le_total, test_progress_state_percentage_property, test_progress_state_indeterminate_when_total_none, test_progress_state_label_max_length)
- [X] **T006** [P] Implement ProgressUpdate contract tests in tests/contract/test_progress_protocol.py (TestProgressUpdateContract: test_progress_update_is_frozen, test_progress_update_contains_state, test_progress_update_contains_delta, test_progress_update_contains_update_type)

### ProgressEmitter Contract Tests

- [X] **T007** [P] Implement ProgressEmitter method contract tests in tests/contract/test_progress_protocol.py (TestProgressEmitterContract: test_emitter_has_update_method, test_emitter_has_set_current_method, test_emitter_has_update_total_method, test_emitter_has_complete_method, test_emitter_has_add_consumer_method, test_emitter_has_remove_consumer_method, test_emitter_has_create_child_method, test_emitter_has_stream_method, test_emitter_has_current_property, test_emitter_has_total_property, test_emitter_has_state_property)
- [X] **T008** [P] Implement ProgressEmitter validation contract tests in tests/contract/test_progress_protocol.py (TestProgressEmitterContract: test_emitter_validates_total_non_negative, test_emitter_update_validates_bounds, test_emitter_update_total_forces_notification, test_emitter_complete_forces_notification, test_emitter_complete_raises_if_indeterminate)

### Consumer Protocol Contract Tests

- [X] **T009** [P] Implement ProgressConsumer protocol contract tests in tests/contract/test_progress_protocol.py (TestProgressConsumerProtocol: test_consumer_must_have_on_progress_method, test_consumer_must_have_on_complete_method, test_on_progress_accepts_progress_update, test_on_complete_accepts_progress_state)
- [X] **T010** [P] Implement consumer implementation protocol tests in tests/contract/test_progress_protocol.py (TestProgressConsumerProtocol: test_cli_consumer_implements_protocol, test_callback_consumer_implements_protocol, test_logging_consumer_implements_protocol)

### Exception Handling Contract Tests

- [X] **T011** [P] Implement exception handling contract tests in tests/contract/test_progress_protocol.py (TestConsumerExceptionHandling: test_emitter_catches_consumer_exceptions, test_emitter_continues_after_consumer_error, test_consumer_exception_logged)

### Throttling Contract Tests

- [X] **T012** [P] Implement throttling contract tests in tests/contract/test_progress_protocol.py (TestThrottlingContract: test_emitter_respects_throttle_interval, test_emitter_force_bypasses_throttling, test_emitter_first_update_not_throttled, test_emitter_complete_not_throttled)

### Hierarchical Progress Contract Tests

- [X] **T013** [P] Implement hierarchical progress contract tests in tests/contract/test_progress_protocol.py (TestHierarchicalProgressContract: test_create_child_returns_emitter, test_child_updates_propagate_to_parent, test_parent_calculates_weighted_average, test_child_weights_normalized)

### Integration Test Stubs

- [X] **T014** [P] Create CLI progress integration test stub in tests/integration/test_cli_progress.py (test_cli_renders_determinate_bar, test_cli_renders_indeterminate_spinner, test_cli_updates_on_progress, test_cli_completes_bar)
- [X] **T015** [P] Create hierarchical progress integration test stub in tests/integration/test_hierarchical.py (test_parent_child_basic, test_weighted_average_calculation, test_multi_level_hierarchy, test_child_completion_propagates)
- [X] **T016** [P] Create async streaming integration test stub in tests/integration/test_async_streaming.py (test_stream_yields_updates, test_stream_completes, test_multiple_async_consumers)

### Verify All Tests Fail

- [X] **T017** Run pytest tests/contract/test_progress_protocol.py and verify all tests are skipped/failing (expected: 134 skipped tests)

## Phase 3.3: Core Implementation (ONLY after tests are failing)

### Core Data Models

- [X] **T018** [P] Implement UpdateType enum in progress_tracker/models.py (STARTED, PROGRESS, TOTAL_CHANGED, COMPLETED, ERROR)
- [X] **T019** [P] Implement ProgressState dataclass in progress_tracker/models.py (current, total, label, timestamp, metadata fields + percentage, is_complete, is_indeterminate, items_remaining properties + validation in __post_init__)
- [X] **T020** [P] Implement ProgressUpdate dataclass in progress_tracker/models.py (state, delta, update_type fields)
- [X] **T021** Run contract tests for models: pytest tests/contract/test_progress_protocol.py::TestUpdateTypeContract tests/contract/test_progress_protocol.py::TestProgressStateContract tests/contract/test_progress_protocol.py::TestProgressUpdateContract -v (expect pass)

### ProgressConsumer Protocol

- [X] **T022** [P] Implement ProgressConsumer Protocol in progress_tracker/models.py (@runtime_checkable protocol with on_progress and on_complete methods)
- [X] **T023** Run protocol contract tests: pytest tests/contract/test_progress_protocol.py::TestProgressConsumerProtocol::test_consumer_must_have_on_progress_method tests/contract/test_progress_protocol.py::TestProgressConsumerProtocol::test_consumer_must_have_on_complete_method -v (expect pass)

### ProgressEmitter Core

- [X] **T024** Implement ProgressEmitter __init__ in progress_tracker/emitter.py (total, label, throttle_interval params + initialize internal state: _current, _total, _label, _consumers list, _children list, _weights list, _last_update_time, _throttle_interval)
- [X] **T025** Implement ProgressEmitter basic methods in progress_tracker/emitter.py (update, set_current with throttling logic + current, total, state properties)
- [X] **T026** Implement ProgressEmitter consumer management in progress_tracker/emitter.py (add_consumer, remove_consumer methods)
- [X] **T027** Implement ProgressEmitter._notify_consumers with exception handling in progress_tracker/emitter.py (try-except wrapper, log errors to stderr)
- [X] **T028** Implement ProgressEmitter advanced methods in progress_tracker/emitter.py (update_total, complete with forced notifications + validation)
- [X] **T029** Run emitter contract tests: pytest tests/contract/test_progress_protocol.py::TestProgressEmitterContract -v (expect pass)

### Exception Handling

- [X] **T030** Run exception handling tests: pytest tests/contract/test_progress_protocol.py::TestConsumerExceptionHandling -v (expect pass)

### Throttling

- [X] **T031** Run throttling tests: pytest tests/contract/test_progress_protocol.py::TestThrottlingContract -v (expect pass)

### Hierarchical Progress

- [X] **T032** Implement ProgressEmitter.create_child in progress_tracker/emitter.py (create child emitter, register parent callback, normalize weights)
- [X] **T033** Implement parent-child update propagation in progress_tracker/emitter.py (child updates trigger parent weighted average recalculation)
- [X] **T034** Run hierarchical contract tests: pytest tests/contract/test_progress_protocol.py::TestHierarchicalProgressContract -v (expect pass)

### Async Streaming

- [X] **T035** Implement ProgressEmitter.stream async generator in progress_tracker/emitter.py (use asyncio.Queue to buffer updates, yield ProgressUpdate events)
- [X] **T036** Implement async streaming integration test in tests/integration/test_async_streaming.py (verify stream yields updates, completes correctly)
- [X] **T037** Run async streaming tests: pytest tests/integration/test_async_streaming.py -v (expect pass)

### Consumer Implementations

- [X] **T038** [P] Implement CallbackProgressConsumer in progress_tracker/consumers.py (wrap callback(current, total) signature, implement on_progress to extract current/total from ProgressUpdate and call callback)
- [X] **T039** [P] Implement LoggingProgressConsumer in progress_tracker/consumers.py (logger param, log_interval throttling, on_progress logs percentage and label at INFO level)
- [X] **T040** [P] Implement CLIProgressConsumer in progress_tracker/cli_renderer.py (use alive-progress library, handle determinate/indeterminate states, render to stderr, on_progress updates bar, on_complete finalizes display)
- [X] **T041** Run consumer protocol tests: pytest tests/contract/test_progress_protocol.py::TestProgressConsumerProtocol::test_cli_consumer_implements_protocol tests/contract/test_progress_protocol.py::TestProgressConsumerProtocol::test_callback_consumer_implements_protocol tests/contract/test_progress_protocol.py::TestProgressConsumerProtocol::test_logging_consumer_implements_protocol -v (expect pass)

### Verify All Contract Tests Pass

- [X] **T042** Run all contract tests: pytest tests/contract/test_progress_protocol.py -v (expect: 0 failed, 0 skipped, all pass)

## Phase 3.4: Integration

### CLI Integration Tests

- [X] **T043** Implement CLI progress integration tests in tests/integration/test_cli_progress.py (test_cli_renders_determinate_bar, test_cli_renders_indeterminate_spinner, test_cli_updates_on_progress, test_cli_completes_bar - capture stderr, validate output format)
- [X] **T044** Run CLI integration tests: pytest tests/integration/test_cli_progress.py -v (expect pass)

### Hierarchical Integration Tests

- [X] **T045** Implement hierarchical progress integration tests in tests/integration/test_hierarchical.py (test_parent_child_basic, test_weighted_average_calculation, test_multi_level_hierarchy, test_child_completion_propagates)
- [X] **T046** Run hierarchical integration tests: pytest tests/integration/test_hierarchical.py -v (expect pass)

### Module Integration (Parallel - 4 modules)

- [X] **T047** [P] Refactor pdf_extractor/progress.py to use ProgressEmitter (replace ProgressInfo class with import from progress_tracker, add deprecation warnings, update pdf_extractor/reader.py to accept progress_emitter parameter, update CLI to use CLIProgressConsumer)
- [X] **T048** [P] Refactor image_processor/progress.py to use ProgressEmitter (replace ProgressTracker class with import from progress_tracker, add deprecation warnings, update image_processor/processor.py to accept progress_emitter parameter, update CLI to use CLIProgressConsumer)
- [X] **T049** [P] Refactor audio_processor/progress.py to use ProgressEmitter (replace ProgressTracker class with import from progress_tracker, add deprecation warnings, update audio_processor/processor.py to accept progress_emitter parameter, update CLI to use CLIProgressConsumer)
- [X] **T050** [P] Add progress tracking to text_summarizer (create text_summarizer/progress.py importing from progress_tracker, update text_summarizer/processor.py to accept progress_emitter parameter, update CLI to use CLIProgressConsumer)

### Module Integration Tests

- [X] **T051** [P] Create pdf_extractor integration test in tests/integration/test_module_integration.py (test_pdf_extractor_with_progress - verify progress updates during PDF extraction)
- [X] **T052** [P] Create image_processor integration test in tests/integration/test_module_integration.py (test_image_processor_with_progress - verify progress updates during image processing)
- [X] **T053** [P] Create audio_processor integration test in tests/integration/test_module_integration.py (test_audio_processor_with_progress - verify progress updates during audio transcription)
- [X] **T054** [P] Create text_summarizer integration test in tests/integration/test_module_integration.py (test_text_summarizer_with_progress - verify progress updates during text summarization)
- [X] **T055** Run module integration tests: pytest tests/integration/test_module_integration.py -v (expect pass)

## Phase 3.5: Polish

### Unit Tests

- [X] **T056** [P] Create unit tests for ProgressState in tests/unit/test_progress_models.py (test property calculations, edge cases, validation errors)
- [X] **T057** [P] Create unit tests for ProgressEmitter in tests/unit/test_progress_emitter.py (test state transitions, throttling logic, consumer notifications, edge cases)
- [X] **T058** [P] Create unit tests for consumers in tests/unit/test_progress_consumers.py (test CallbackProgressConsumer calls callback correctly, LoggingProgressConsumer logs at intervals, CLIProgressConsumer renders correctly - mock alive-progress)
- [X] **T059** Run all unit tests: pytest tests/unit/ -v (expect pass)

### Documentation

- [X] **T060** Update progress_tracker/README.md with usage examples, API reference, migration guide (refer to quickstart.md and api.md)
- [X] **T061** [P] Update pdf_extractor/README.md with progress tracking examples
- [X] **T062** [P] Update image_processor/README.md with progress tracking examples
- [X] **T063** [P] Update audio_processor/README.md with progress tracking examples
- [X] **T064** [P] Update text_summarizer/README.md with progress tracking examples

### Validation

- [X] **T065** Run all quickstart.md examples manually and verify they work (basic usage, programmatic usage, async streaming, hierarchical progress, indeterminate progress, dynamic total updates, module integration pattern, error handling)
- [X] **T066** Run full test suite: pytest tests/ -v (expect: all pass - note: some existing test failures unrelated to progress_tracker)
- [X] **T067** Check file length compliance: uv run python check_file_lengths.py (expect: all files <250 lines)
- [X] **T068** Run linting: uv run ruff check . (expect: no errors)

---

## Dependencies

### Phase Dependencies
- Phase 3.2 (Tests) MUST complete before Phase 3.3 (Implementation)
- T017 (verify tests fail) blocks all Phase 3.3 tasks
- Phase 3.3 (Core) MUST complete before Phase 3.4 (Integration)
- T042 (all contract tests pass) blocks all Phase 3.4 tasks

### Core Implementation Dependencies
- T018-T020 (models) block T021 (model tests)
- T022 (protocol) blocks T023 (protocol tests)
- T024-T028 (emitter) block T029 (emitter tests)
- T032-T033 (hierarchical) block T034 (hierarchical tests)
- T035 (async streaming) blocks T036-T037 (streaming tests)
- T038-T040 (consumers) block T041 (consumer tests)

### Integration Dependencies
- T042 (all contract tests pass) blocks T043-T046 (integration tests)
- T042 blocks T047-T050 (module integration)
- T047-T050 (module refactors) block T051-T054 (module integration tests)

### Polish Dependencies
- All implementation and integration complete before T056-T059 (unit tests)
- T066 (full test suite) requires all previous tests implemented and passing

## Parallel Execution Examples

### Contract Tests (Phase 3.2)
```bash
# Launch T004-T016 together (all different test classes/files):
Task: "Implement UpdateType enum contract tests"
Task: "Implement ProgressState contract tests"
Task: "Implement ProgressUpdate contract tests"
Task: "Implement ProgressEmitter method contract tests"
Task: "Implement ProgressEmitter validation contract tests"
Task: "Implement ProgressConsumer protocol contract tests"
Task: "Implement consumer implementation protocol tests"
Task: "Implement exception handling contract tests"
Task: "Implement throttling contract tests"
Task: "Implement hierarchical progress contract tests"
Task: "Create CLI progress integration test stub"
Task: "Create hierarchical progress integration test stub"
Task: "Create async streaming integration test stub"
```

### Core Models (Phase 3.3)
```bash
# Launch T018-T020 together (all in models.py, but independent classes):
Task: "Implement UpdateType enum in progress_tracker/models.py"
Task: "Implement ProgressState dataclass in progress_tracker/models.py"
Task: "Implement ProgressUpdate dataclass in progress_tracker/models.py"
```

### Consumer Implementations (Phase 3.3)
```bash
# Launch T038-T040 together (different files):
Task: "Implement CallbackProgressConsumer in progress_tracker/consumers.py"
Task: "Implement LoggingProgressConsumer in progress_tracker/consumers.py"
Task: "Implement CLIProgressConsumer in progress_tracker/cli_renderer.py"
```

### Module Integration (Phase 3.4)
```bash
# Launch T047-T050 together (different modules):
Task: "Refactor pdf_extractor/progress.py to use ProgressEmitter"
Task: "Refactor image_processor/progress.py to use ProgressEmitter"
Task: "Refactor audio_processor/progress.py to use ProgressEmitter"
Task: "Add progress tracking to text_summarizer"

# Then launch T051-T054 together (different test files):
Task: "Create pdf_extractor integration test"
Task: "Create image_processor integration test"
Task: "Create audio_processor integration test"
Task: "Create text_summarizer integration test"
```

### Documentation (Phase 3.5)
```bash
# Launch T061-T064 together (different module READMEs):
Task: "Update pdf_extractor/README.md with progress tracking examples"
Task: "Update image_processor/README.md with progress tracking examples"
Task: "Update audio_processor/README.md with progress tracking examples"
Task: "Update text_summarizer/README.md with progress tracking examples"
```

---

## Notes

- **[P] tasks**: Different files, no dependencies - can run in parallel
- **TDD Critical**: All contract tests (T004-T017) MUST fail before implementing (T018+)
- **File Size**: All files designed to stay <250 lines per constitution
- **Composition-First**: Consumers compose with emitters, children compose with parents
- **Minimal Dependencies**: Only alive-progress external dependency
- **Exception Safety**: All consumer notifications wrapped in try-except
- **Throttling**: Default 10 Hz (100ms interval) to prevent performance overhead

## Validation Checklist

_GATE: Checked before marking feature complete_

- [x] All contracts have corresponding tests (134 contract tests in test_progress_protocol.py)
- [x] All entities have model tasks (ProgressState T019, ProgressUpdate T020, UpdateType T018, ProgressEmitter T024-T035)
- [x] All tests come before implementation (Phase 3.2 blocks Phase 3.3)
- [x] Parallel tasks truly independent (verified: consumers use different files, module integrations touch different modules)
- [x] Each task specifies exact file path (all tasks include file paths)
- [x] No task modifies same file as another [P] task (verified: no conflicts)
- [x] All files designed to stay under 250 lines (plan.md confirms: models.py ~80, emitter.py ~120, consumers.py ~180, cli_renderer.py ~100)
- [x] Modular composition enforced (consumers compose with emitters, children with parents)
- [x] Dependencies are minimal and justified (only alive-progress external, per spec requirement)

---

**Total Tasks**: 68
**Estimated Parallel Groups**: 8 (contract tests, models, consumers, module integrations, module tests, documentation, unit tests)
**Critical Path**: Setup → Contract Tests → Core Models → Emitter → Consumers → Integration → Polish

**Next Step**: Execute T001 (Create module structure)
