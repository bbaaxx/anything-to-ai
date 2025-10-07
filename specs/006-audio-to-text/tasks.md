# Tasks: Audio-to-Text Transcription Module

**Input**: Design documents from `/specs/006-audio-to-text/`
**Prerequisites**: spec.md, research.md, data-model.md, quickstart.md

## Execution Flow (main)

```
1. Load spec.md from feature directory
   → Feature: Audio transcription module with MLX-optimized Whisper
   → Extract: 23 functional requirements, 4 key entities
2. Load design documents:
   → research.md: lightning-whisper-mlx, module patterns from image_processor
   → data-model.md: AudioDocument, TranscriptionResult, TranscriptionConfig, ProcessingResult
   → quickstart.md: 15 test scenarios covering all FRs
3. Generate tasks by category:
   → Setup: project structure, dependencies, linting
   → Tests: contract tests (API, exceptions, CLI), integration tests
   → Core: data models, processor, model loader
   → Features: CLI, streaming, progress callbacks
   → Polish: validation tests, performance tests
4. Apply task rules:
   → Different files = mark [P] for parallel
   → Same file = sequential (no [P])
   → Tests before implementation (TDD)
5. Number tasks sequentially (T001-T031)
6. Dependencies mapped from module patterns
7. Return: SUCCESS (tasks ready for execution)
```

## Format: `[ID] [P?] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- Include exact file paths in descriptions

## Path Conventions

- Module path: `audio_processor/`
- Tests path: `tests/contract/`, `tests/integration/`, `tests/unit/`
- Sample data: `sample-data/audio/`

## Phase 3.1: Setup

- [X] T001 Create audio_processor module structure (9 files: models.py, exceptions.py, processor.py, cli.py, __init__.py, __main__.py, progress.py, streaming.py, model_loader.py) following image_processor pattern
- [X] T002 Add lightning-whisper-mlx dependency via `uv add lightning-whisper-mlx`
- [X] T003 Create sample audio test data directory at sample-data/audio/ with README

## Phase 3.2: Tests First (TDD) ⚠️ MUST COMPLETE BEFORE 3.3

**CRITICAL: These tests MUST be written and MUST FAIL before ANY implementation**

### Contract Tests (API surface)
- [X] T004 [P] Contract test for module API functions (process_audio, process_audio_batch, validate_audio, create_config, get_supported_formats, get_audio_info) in tests/contract/test_audio_module_api.py (FR-019, FR-020)
- [X] T005 [P] Contract test for exception hierarchy (AudioProcessingError base, AudioNotFoundError, UnsupportedFormatError, CorruptedAudioError, TranscriptionError, NoSpeechDetectedError, DurationExceededError, ValidationError, ModelLoadError, ProcessingTimeoutError, ProcessingInterruptedError) in tests/contract/test_audio_exceptions.py (FR-010)
- [X] T006 [P] Contract test for CLI parser arguments (positional audio files, --format, --model, --quantization, --language, --batch-size, --output, --verbose, --quiet) in tests/contract/test_audio_cli_parser.py (FR-015, FR-016, FR-017, FR-018)
- [X] T007 [P] Contract test for data model classes (AudioDocument, TranscriptionResult, TranscriptionConfig, ProcessingResult) in tests/contract/test_audio_models.py (FR-001, FR-003, FR-012)

### Integration Tests (user scenarios)
- [X] T008 [P] Integration test for single audio transcription with defaults (medium model, 4bit quantization, auto language detection) in tests/integration/test_single_audio.py (FR-003, FR-012, Quickstart #1)
- [X] T009 [P] Integration test for batch processing multiple audio files with progress in tests/integration/test_batch_audio_processing.py (FR-008, FR-009, Quickstart #5)
- [X] T010 [P] Integration test for error workflows (no speech detected, unsupported format, file not found, duration exceeded) in tests/integration/test_audio_error_workflows.py (FR-010, FR-023, Quickstart #6-9)
- [X] T011 [P] Integration test for language detection and hints in tests/integration/test_language_detection.py (FR-022, Quickstart #4)
- [X] T012 [P] Integration test for output formats (plain text, JSON) in tests/integration/test_output_formats.py (FR-004, FR-015, Quickstart #2)

## Phase 3.3: Core Implementation (ONLY after tests are failing)

### Data Models
- [X] T013 [P] Create AudioDocument dataclass with validation (file_path, format, duration, sample_rate, file_size, channels) in audio_processor/models.py (FR-001, FR-002, FR-014)
- [X] T014 [P] Create TranscriptionResult dataclass (audio_path, text, confidence_score, processing_time, model_used, quantization, detected_language, success, error_message) in audio_processor/models.py (FR-003, FR-005, FR-006)
- [X] T015 [P] Create TranscriptionConfig dataclass with defaults (model="medium", quantization="4bit", batch_size=12, language=None, output_format="plain", timeout_seconds=600, progress_callback=None, verbose=False, max_duration_seconds=7200) in audio_processor/models.py (FR-012)
- [X] T016 [P] Create ProcessingResult dataclass (success, results, total_files, successful_count, failed_count, total_processing_time, average_processing_time, error_summary) in audio_processor/models.py (FR-008)

### Exceptions
- [X] T017 [P] Create exception hierarchy with AudioProcessingError base and 10 derived classes in audio_processor/exceptions.py (FR-010)

### Configuration Factory
- [X] T018 [P] Create create_config factory function with parameter validation (models, quantization, batch_size, language, output_format) in audio_processor/config.py (FR-020)

### Model Loading
- [X] T019 [P] Create Whisper model loader with caching and lazy loading (LightningWhisperMLX integration) in audio_processor/model_loader.py (FR-013, Research: lightning-whisper-mlx)

### Audio Validation
- [X] T020 Audio validation function (file existence, format check, metadata extraction, duration limit enforcement) in audio_processor/processor.py (FR-001, FR-002, FR-011, FR-014, FR-023)

### Core Processing
- [X] T021 Single audio transcription function with Whisper model, confidence scoring, and language detection in audio_processor/processor.py (FR-003, FR-005, FR-022)
- [X] T022 No speech detection logic and error handling in audio_processor/processor.py (FR-010)
- [X] T023 Model configuration handling (model selection, quantization, batch_size) in audio_processor/processor.py (FR-012, FR-016)

### Progress and Streaming
- [X] T024 [P] Progress callback wrapper and helper functions in audio_processor/progress.py (FR-009, FR-018)
- [X] T025 Batch processing with progress callbacks and error accumulation in audio_processor/streaming.py (FR-008, FR-009)

### CLI Interface
- [X] T026 CLI argument parser with all required flags in audio_processor/cli.py (FR-015, FR-016, FR-017, FR-018)
- [X] T027 CLI main function with output formatting (plain/JSON), file writing, and verbose/quiet modes in audio_processor/cli.py (FR-004, FR-015, FR-017, FR-018)

### Module API
- [X] T028 Public API exports (process_audio, process_audio_batch, validate_audio, create_config, get_supported_formats, get_audio_info) in audio_processor/__init__.py (FR-019)
- [X] T029 CLI entry point in audio_processor/__main__.py

## Phase 3.4: Integration

- [X] T030 Add utility function get_audio_info for metadata extraction without processing in audio_processor/processor.py (FR-014)
- [X] T031 Add utility function get_supported_formats returning ['m4a', 'mp3', 'wav'] in audio_processor/processor.py (FR-002)

## Phase 3.5: Polish

- [ ] T032 [P] Unit tests for configuration validation edge cases in tests/unit/test_audio_config_validation.py (FR-012, FR-020, Quickstart #15) - SKIPPED: Contract tests cover this
- [ ] T033 [P] Unit tests for audio metadata extraction accuracy in tests/unit/test_audio_metadata.py (FR-014, Quickstart #11) - SKIPPED: Integration tests cover this
- [ ] T034 Performance validation for Apple Silicon optimization (compare MLX vs CPU processing speed) in tests/unit/test_audio_performance.py (FR-013) - DEFERRED: Requires real audio files
- [ ] T035 Create sample audio test files (speech.mp3, silence.wav, spanish.m4a, long.mp3) in sample-data/audio/ per quickstart requirements - DEFERRED: User will add audio files for testing
- [ ] T036 Run full quickstart validation (15 test scenarios) and verify all acceptance criteria - DEFERRED: Requires real audio files
- [X] T037 Update CLAUDE.md with audio_processor commands and patterns

## Dependencies

**Critical Path**:
- Setup (T001-T003) blocks everything
- Contract tests (T004-T007) before implementation (T013-T029)
- Integration tests (T008-T012) before implementation
- Data models (T013-T016) block processor implementation
- Exception hierarchy (T017) blocks error handling in processor
- Config factory (T018) blocks CLI and processor
- Model loader (T019) blocks processor implementation
- Processor core (T020-T023) blocks streaming and CLI
- Progress helpers (T024) block streaming (T025)
- Processor and streaming (T020-T025) block CLI implementation (T026-T027)
- CLI blocks module API exports (T028-T029)
- Everything blocks polish (T032-T037)

**Parallel Opportunities**:
- T004-T007: All contract tests (different files)
- T008-T012: All integration tests (different files)
- T013-T016: All data model classes (same file, but can be batched edits)
- T017, T018, T019: Exceptions, config, model_loader (different files)
- T024: Progress helpers (independent from processor)
- T032-T034: All unit tests (different files)

## Parallel Execution Examples

### Contract Tests (Phase 3.2)
```bash
# Launch T004-T007 together:
# 1. Open 4 parallel agents
# 2. Each writes one contract test file
# 3. All should fail initially (TDD)
```

### Integration Tests (Phase 3.2)
```bash
# Launch T008-T012 together:
# Similar to contract tests, 5 parallel agents
```

### Support Modules (Phase 3.3)
```bash
# Launch T017-T019 together:
# Exceptions, config factory, model loader (independent files)
```

### Unit Tests (Phase 3.5)
```bash
# Launch T032-T034 together:
# All unit test files independent
```

## Notes

- **Module Pattern**: Follow image_processor structure exactly (9 files, clear separation)
- **File Size**: All files MUST stay under 250 lines per constitutional requirement
- **Dependencies**: lightning-whisper-mlx is the only external dependency (justified for MLX optimization)
- **Test Data**: Need real audio samples for integration tests (see T035)
- **Apple Silicon**: MLX optimization is critical for performance (FR-013)
- **TDD**: Tests MUST fail before implementation starts
- **Commit Strategy**: Commit after each task completion
- **Avoid**: Creating files prematurely, bypassing test-first approach

## Task Generation Rules Applied

1. **From Spec Requirements**:
   - FR-001 to FR-023 → 31 implementation tasks
   - Each FR mapped to specific tasks with file paths

2. **From Data Model**:
   - 4 entities (AudioDocument, TranscriptionResult, TranscriptionConfig, ProcessingResult) → T013-T016
   - All in same file (models.py), sequential or batched edits

3. **From Research**:
   - lightning-whisper-mlx integration → T019 (model_loader.py)
   - Module patterns from image_processor → T001 (structure)

4. **From Quickstart**:
   - 15 test scenarios → T008-T012 (integration tests)
   - Test data requirements → T003, T035

5. **Ordering Logic**:
   - Setup → Contract/Integration Tests → Data Models → Exceptions/Config → Core Processor → Streaming/CLI → API Exports → Polish
   - Dependencies enforced through task numbering

## Validation Checklist

- [x] All entities from data-model.md have model tasks (T013-T016)
- [x] All API functions have contract tests (T004)
- [x] All exception types have contract tests (T005)
- [x] CLI arguments have contract tests (T006)
- [x] All user scenarios from quickstart have integration tests (T008-T012)
- [x] Tests come before implementation (T004-T012 before T013-T029)
- [x] Parallel tasks are truly independent (different files)
- [x] Each task specifies exact file path
- [x] No [P] tasks modify same file
- [x] All files designed to stay under 250 lines (9 small files)
- [x] Modular composition enforced (separate files for models, processor, CLI, etc.)
- [x] Minimal dependencies (only lightning-whisper-mlx, justified for MLX)
- [x] All 23 functional requirements mapped to tasks
- [x] Test data requirements identified (T003, T035)
- [x] Performance validation included (T034)
- [x] Documentation updates included (T037)

---

**Status**: Ready for execution. All 37 tasks defined with clear dependencies and parallel opportunities.
