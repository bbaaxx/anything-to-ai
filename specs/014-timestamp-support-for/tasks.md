# Tasks: Timestamp Support for Audio Transcription

**Feature**: 014-timestamp-support-for
**Input**: Design documents from `/specs/014-timestamp-support-for/`
**Prerequisites**: research.md ✓, data-model.md ✓, contracts/ ✓, quickstart.md ✓

## Execution Flow

```
1. Setup: Ensure dependencies installed
2. Tests First (TDD): Write ALL contract/integration tests BEFORE implementation
3. Core Implementation: Add timestamp models, extraction, formatting
4. Integration: Connect CLI → processor → formatters
5. Polish: Unit tests, performance validation, documentation
```

## Path Conventions

- **Project**: Single Python package at repository root
- **Source**: `anyfile_to_ai/audio_processor/`
- **Tests**: `tests/contract/`, `tests/integration/`, `tests/unit/`

## Phase 3.1: Setup

- [x] T001 Verify Python 3.13+ and lightning-whisper-mlx installed (no new dependencies needed)
- [x] T002 [P] Run existing linting to establish baseline: `uv run ruff check .`

## Phase 3.2: Tests First (TDD) ⚠️ MUST COMPLETE BEFORE 3.3

**CRITICAL: These tests MUST be written and MUST FAIL before ANY implementation**

- [x] T003 [P] Contract test for TranscriptionSegment model in `tests/contract/test_timestamp_contracts.py::test_transcription_segment_model`
- [x] T004 [P] Contract test for TranscriptionResult.segments field in `tests/contract/test_timestamp_contracts.py::test_transcription_result_segments`
- [x] T005 [P] Contract test for process_audio() with timestamps in `tests/contract/test_timestamp_contracts.py::test_process_audio_with_timestamps`
- [x] T006 [P] Contract test for CLI --timestamps flag parsing in `tests/contract/test_timestamp_contracts.py::test_cli_timestamps_flag`
- [x] T007 [P] Contract test for format_timestamp() function in `tests/contract/test_timestamp_contracts.py::test_format_timestamp_contract`
- [x] T008 [P] Integration test single audio with timestamps in `tests/integration/test_timestamp_integration.py::test_single_audio_with_timestamps`
- [x] T009 [P] Integration test batch processing with timestamps in `tests/integration/test_timestamp_integration.py::test_batch_with_timestamps`
- [x] T010 [P] Integration test graceful degradation (unavailable timestamps) in `tests/integration/test_timestamp_integration.py::test_graceful_degradation`

**Verify tests fail**: Run `uv run pytest tests/contract/test_timestamp_contracts.py tests/integration/test_timestamp_integration.py -v` → All should FAIL

## Phase 3.3: Core Implementation (ONLY after tests are failing)

- [x] T011 Add TranscriptionSegment dataclass to `anyfile_to_ai/audio_processor/models.py`
- [x] T012 Add segments field to TranscriptionResult in `anyfile_to_ai/audio_processor/models.py`
- [x] T013 Add timestamps field to TranscriptionConfig in `anyfile_to_ai/audio_processor/config.py`
- [x] T014 Extract and convert segments in `anyfile_to_ai/audio_processor/processor.py` (process_audio function)
- [x] T015 [P] Add format_timestamp() function to `anyfile_to_ai/audio_processor/markdown_formatter.py`
- [x] T016 [P] Add format_segments_markdown() function to `anyfile_to_ai/audio_processor/markdown_formatter.py`
- [x] T017 Modify format_output() to handle timestamps in `anyfile_to_ai/audio_processor/markdown_formatter.py`
- [x] T018 Add --timestamps CLI flag in `anyfile_to_ai/audio_processor/cli.py`

**Verify tests pass**: Run `uv run pytest tests/contract/test_timestamp_contracts.py tests/integration/test_timestamp_integration.py -v` → All should PASS

## Phase 3.4: Integration

- [x] T019 Test markdown output with timestamps (manual): `uv run python -m audio_processor sample-data/audio/test.mp3 --timestamps --format markdown`
- [x] T020 Test JSON output with timestamps (manual): `uv run python -m audio_processor sample-data/audio/test.mp3 --timestamps --format json`
- [x] T021 Test CSV output with timestamps (manual): `uv run python -m audio_processor sample-data/audio/test.mp3 --timestamps --format csv`
- [x] T022 Verify backward compatibility (no --timestamps): `uv run python -m audio_processor sample-data/audio/test.mp3 --format json` (should not have segments key)

## Phase 3.5: Polish

- [ ] T023 [P] Unit test for timestamp formatting edge cases in `tests/unit/test_timestamp_formatting.py::test_format_timestamp_edge_cases`
- [ ] T024 [P] Unit test for markdown segment formatting in `tests/unit/test_timestamp_formatting.py::test_format_segments_markdown`
- [ ] T025 [P] Unit test for CSV timestamp formatting in `tests/unit/test_timestamp_formatting.py::test_format_csv_with_timestamps`
- [ ] T026 Performance test: Verify no overhead when timestamps disabled in `tests/unit/test_performance.py::test_timestamp_disabled_performance`
- [ ] T027 Run full test suite to ensure no regressions: `uv run pytest tests/ -v`
- [ ] T028 Update CLAUDE.md with timestamp CLI examples (if not auto-updated)

## Dependencies

```
Setup (T001-T002)
  → Tests (T003-T010) MUST FAIL
    → Models (T011-T013)
      → Processor (T014)
        → Formatters (T015-T017)
          → CLI (T018)
            → Integration (T019-T022)
              → Polish (T023-T028)
```

**Parallel constraints**:
- T003-T010: All parallel (different test files/functions)
- T011-T012: Sequential (same file `models.py`)
- T015-T016: Parallel (different functions, no shared state)
- T023-T025: All parallel (different test files/functions)

## Parallel Execution Examples

### Phase 3.2: Write all contract tests in parallel
```bash
# All these tests can be written simultaneously (different test files/functions):
Task: "Contract test for TranscriptionSegment model in tests/contract/test_timestamp_contracts.py::test_transcription_segment_model"
Task: "Contract test for TranscriptionResult.segments field in tests/contract/test_timestamp_contracts.py::test_transcription_result_segments"
Task: "Contract test for process_audio() with timestamps in tests/contract/test_timestamp_contracts.py::test_process_audio_with_timestamps"
Task: "Contract test for CLI --timestamps flag in tests/contract/test_timestamp_contracts.py::test_cli_timestamps_flag"
Task: "Contract test for format_timestamp() in tests/contract/test_timestamp_contracts.py::test_format_timestamp_contract"
Task: "Integration test single audio with timestamps in tests/integration/test_timestamp_integration.py::test_single_audio_with_timestamps"
Task: "Integration test batch processing in tests/integration/test_timestamp_integration.py::test_batch_with_timestamps"
Task: "Integration test graceful degradation in tests/integration/test_timestamp_integration.py::test_graceful_degradation"
```

### Phase 3.3: Formatter functions in parallel
```bash
# These formatting functions are independent:
Task: "Add format_timestamp() function to anyfile_to_ai/audio_processor/markdown_formatter.py"
Task: "Add format_segments_markdown() function to anyfile_to_ai/audio_processor/markdown_formatter.py"
```

### Phase 3.5: Unit tests in parallel
```bash
# All unit tests are independent:
Task: "Unit test for timestamp formatting edge cases in tests/unit/test_timestamp_formatting.py::test_format_timestamp_edge_cases"
Task: "Unit test for markdown segment formatting in tests/unit/test_timestamp_formatting.py::test_format_segments_markdown"
Task: "Unit test for CSV timestamp formatting in tests/unit/test_timestamp_formatting.py::test_format_csv_with_timestamps"
```

## Notes

- **[P] tasks**: Different files or functions, no dependencies, safe to parallelize
- **Sequential tasks**: Same file modifications (models.py, processor.py, cli.py)
- **TDD requirement**: Tests T003-T010 MUST fail before implementing T011-T018
- **File size**: All modified files stay well under 250 lines (largest is processor.py at ~215 lines after changes)
- **Zero new dependencies**: Uses existing lightning-whisper-mlx and standard library only

## Task Generation Rules Applied

1. **From Contracts**:
   - processor-api.md → T005 (process_audio contract test)
   - cli-api.md → T006 (CLI flag contract test)
   - formatter-api.md → T007, T015-T017 (formatter contracts and implementation)

2. **From Data Model**:
   - TranscriptionSegment entity → T003, T011 (contract test + model)
   - TranscriptionResult modification → T004, T012 (contract test + field addition)
   - TranscriptionConfig modification → T013 (config field)

3. **From Quickstart**:
   - Basic timestamp usage → T008 (integration test)
   - Batch processing → T009 (integration test)
   - Graceful degradation → T010 (integration test)
   - Manual validation → T019-T022 (manual testing)

4. **Ordering**:
   - Setup → Tests (TDD) → Models → Processor → Formatters → CLI → Integration → Polish
   - Dependencies strictly enforced (tests fail before implementation)

## Validation Checklist

- [x] All contracts have corresponding tests (T003-T007)
- [x] All entities have model tasks (T011-T013)
- [x] All tests come before implementation (T003-T010 before T011-T018)
- [x] Parallel tasks truly independent (different files/functions)
- [x] Each task specifies exact file path ✓
- [x] No task modifies same file as another [P] task ✓
- [x] All files designed to stay under 250 lines ✓
- [x] Modular composition enforced ✓
- [x] Dependencies minimal and justified (zero new deps) ✓
