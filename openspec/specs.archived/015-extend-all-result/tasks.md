# Tasks: Metadata Dictionary for Result Models

**Input**: Design documents from `/specs/015-extend-all-result/`
**Prerequisites**: plan.md, research.md, data-model.md, contracts/, quickstart.md


## ⚡ IMPLEMENTATION STATUS: 54/54 tasks complete (100%)

**Last Updated**: 2025-10-25
**Status**: 🎉 COMPLETE - All Tests Passing

**Completed**:
- ✅ Setup (2 tasks)
- ✅ Contract Tests (5 tasks)
- ✅ Model Extensions (4 tasks)
- ✅ Metadata Extractors (4 tasks)
- ✅ Processor Integration (4 tasks)
- ✅ CLI Updates (3 tasks)
- ✅ Formatter Updates (16 tasks - some N/A as formats don't exist)
- ✅ Unit Tests (8 tasks)
- ✅ Integration Tests (8 tasks)

**See**: `IMPLEMENTATION_STATUS.md` for detailed status and next steps
**See**: `QUICK_REFERENCE.md` for fast onboarding

---
## Execution Flow (main)

```
1. Load plan.md from feature directory
   → Extract: Python 3.11+, pdfplumber, mlx-vlm, Pillow, lightning-whisper-mlx, pydantic, httpx
   → Structure: Single project with modular processing packages
2. Load design documents:
   → data-model.md: ProcessingMetadata, ConfigurationMetadata, SourceMetadata (4 type-specific extensions)
   → contracts/: 5 files (metadata-schema.json + 4 module API contracts)
   → research.md: ISO 8601 timestamps, EXIF extraction, metadata schema patterns
   → quickstart.md: 10 integration test scenarios
3. Generate tasks by category:
   → Contract tests: 5 tasks (1 schema + 4 module contracts)
   → Model extensions: 4 tasks (PDF, Image, Audio, Text)
   → Metadata extractors: 4 tasks (1 per module)
   → Processor integration: 4 tasks (1 per module)
   → CLI updates: 3 tasks (PDF, Image, Audio only)
   → Formatter updates: 16 tasks (4 formats × 4 modules)
   → Unit tests: 8 tasks (extractors + utilities)
   → Integration tests: 10 tasks (from quickstart scenarios)
4. Apply task rules:
   → Contract tests = [P] (different files)
   → Model extensions = [P] (different files)
   → Metadata extractors = [P] (different files)
   → Processor/CLI/formatter updates = sequential per module
   → Tests = [P] where independent
5. Number tasks sequentially (T001-T054)
6. Total: 54 tasks across 9 phases
```

## Format: `[ID] [P?] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- Include exact file paths in descriptions

## Path Conventions

- Single project: `anyfile_to_ai/`, `tests/` at repository root
- Metadata extractors: `anyfile_to_ai/<module>/metadata.py`
- Models: `anyfile_to_ai/<module>/models.py`
- Tests: `tests/contract/`, `tests/unit/`, `tests/integration/`

---

## Phase 3.1: Setup

- [X] T001 Verify project structure and dependencies (Python 3.11+, existing deps: pdfplumber, mlx-vlm, Pillow, lightning-whisper-mlx, pydantic, httpx)
- [X] T002 Confirm linting configuration (ruff) enforces file length limits and style

---

## Phase 3.2: Contract Tests First (TDD) ⚠️ MUST COMPLETE BEFORE 3.3

**CRITICAL: These tests MUST be written and MUST FAIL before ANY implementation**

- [X] T003 [P] Contract test metadata JSON schema validation in tests/contract/test_metadata_schema.py (MUST include test: result.metadata is None when --include-metadata flag omitted)
- [X] T004 [P] Contract test PDF ExtractionResult metadata structure in tests/contract/test_pdf_metadata_contract.py
- [X] T005 [P] Contract test Image DescriptionResult metadata structure in tests/contract/test_image_metadata_contract.py
- [X] T006 [P] Contract test Audio TranscriptionResult metadata structure in tests/contract/test_audio_metadata_contract.py
- [X] T007 [P] Contract test Text SummaryMetadata extension in tests/contract/test_text_metadata_contract.py

---

## Phase 3.3: Core Implementation - Model Extensions (ONLY after tests are failing)

- [X] T008 [P] Extend ExtractionResult with metadata field in anyfile_to_ai/pdf_extractor/models.py
- [X] T009 [P] Extend DescriptionResult with metadata field in anyfile_to_ai/image_processor/models.py
- [X] T010 [P] Extend TranscriptionResult with metadata field in anyfile_to_ai/audio_processor/models.py
- [X] T011 [P] Extend SummaryMetadata with universal fields in anyfile_to_ai/text_summarizer/models.py

---

## Phase 3.4: Metadata Extractors

- [X] T012 [P] Create PDF metadata extractor in anyfile_to_ai/pdf_extractor/metadata.py
- [X] T013 [P] Create Image metadata extractor with EXIF handling in anyfile_to_ai/image_processor/metadata.py
- [X] T014 [P] Create Audio metadata extractor in anyfile_to_ai/audio_processor/metadata.py
- [X] T015 [P] Create Text metadata extractor in anyfile_to_ai/text_summarizer/metadata.py

---

## Phase 3.5: Processor Integration

- [X] T016 Integrate PDF metadata extraction in anyfile_to_ai/pdf_extractor/reader.py (Updated extract_text function)
- [X] T017 Integrate Image metadata extraction in anyfile_to_ai/image_processor/processor.py
- [X] T018 Integrate Audio metadata extraction in anyfile_to_ai/audio_processor/processor.py
- [X] T019 Integrate Text metadata extraction in anyfile_to_ai/text_summarizer/processor.py

---

## Phase 3.6: CLI Updates

- [X] T020 [P] Add --include-metadata flag to PDF CLI in anyfile_to_ai/pdf_extractor/cli.py
- [X] T021 [P] Add --include-metadata flag to Image CLI in anyfile_to_ai/image_processor/cli.py
- [X] T022 [P] Add --include-metadata flag to Audio CLI in anyfile_to_ai/audio_processor/cli.py

---

## Phase 3.7: Formatter Updates - PDF Module

- [X] T023 Update PDF JSON formatter to include metadata in anyfile_to_ai/pdf_extractor/output_formatters.py
- [X] T024 Update PDF markdown formatter with metadata frontmatter/section in anyfile_to_ai/pdf_extractor/markdown_formatter.py
- [X] T025 Update PDF CSV formatter to flatten metadata columns in anyfile_to_ai/pdf_extractor/output_formatters.py
- [X] T026 Update PDF plain formatter (exclude metadata) in anyfile_to_ai/pdf_extractor/output_formatters.py

---

## Phase 3.8: Formatter Updates - Image Module

- [X] T027 Update Image JSON formatter to include metadata in anyfile_to_ai/image_processor/cli.py (ALREADY DONE in T021)
- [X] T028 Update Image markdown formatter with EXIF metadata section in anyfile_to_ai/image_processor/markdown_formatter.py
- [X] T029 Update Image CSV formatter to flatten metadata columns in anyfile_to_ai/image_processor/cli.py
- [X] T030 Update Image plain formatter (exclude metadata) in anyfile_to_ai/image_processor/cli.py (plain format already excludes metadata)

---

## Phase 3.9: Formatter Updates - Audio Module

- [X] T031 Update Audio JSON formatter to include metadata in anyfile_to_ai/audio_processor/cli.py (ALREADY DONE in T022)
- [X] T032 Update Audio markdown formatter with metadata section in anyfile_to_ai/audio_processor/markdown_formatter.py
- [X] T033 Update Audio CSV formatter to flatten metadata columns (N/A - CSV format not supported by audio_processor)
- [X] T034 Update Audio plain formatter (exclude metadata) in anyfile_to_ai/audio_processor/cli.py (plain format already excludes metadata)

---

## Phase 3.10: Formatter Updates - Text Module

- [X] T035 Update Text JSON formatter to include metadata in anyfile_to_ai/text_summarizer/__main__.py (ALREADY DONE - existing implementation)
- [X] T036 Update Text markdown formatter with metadata section in anyfile_to_ai/text_summarizer/__main__.py (ALREADY DONE - existing implementation)
- [X] T037 Update Text CSV formatter to flatten metadata columns (N/A - CSV format not supported by text_summarizer)
- [X] T038 Update Text plain formatter (exclude metadata) in anyfile_to_ai/text_summarizer/__main__.py (metadata inclusion controlled by --no-metadata flag)

---

## Phase 3.11: Unit Tests

- [X] T039 [P] Unit tests for PDF metadata extraction in tests/unit/test_pdf_metadata.py
- [X] T040 [P] Unit tests for Image EXIF extraction in tests/unit/test_image_metadata.py
- [X] T041 [P] Unit tests for Audio metadata extraction in tests/unit/test_audio_metadata.py
- [X] T042 [P] Unit tests for Text metadata extraction in tests/unit/test_text_metadata.py
- [X] T043 [P] Unit tests for ISO 8601 timestamp formatting in tests/unit/test_timestamp_utils.py
- [X] T044 [P] Unit tests for configuration metadata in tests/unit/test_config_metadata.py
- [X] T045 [P] Unit tests for unavailable field handling in tests/unit/test_unavailable_fields.py
- [X] T046 [P] Unit tests for metadata serialization in tests/unit/test_metadata_serialization.py

---

## Phase 3.12: Integration Tests

- [X] T047 Integration test PDF extraction with full metadata in tests/integration/test_pdf_metadata_integration.py
- [X] T048 Integration test Image EXIF extraction workflow in tests/integration/test_image_metadata_integration.py
- [X] T049 Integration test Audio language confidence workflow in tests/integration/test_audio_metadata_integration.py
- [X] T050 Integration test Text summarizer backward compatibility in tests/integration/test_text_metadata_integration.py
- [X] T051 Integration test PDF→summarizer pipeline with metadata in tests/integration/test_pdf_summary_pipeline.py
- [X] T052 Integration test Audio→summarizer pipeline with metadata in tests/integration/test_audio_summary_pipeline.py
- [X] T053 Integration test metadata disabled (backward compatibility) in tests/integration/test_backward_compat_metadata.py
- [X] T054 Integration test unavailable fields handling in tests/integration/test_unavailable_metadata.py

---

## Dependencies

### Critical Path
```
Setup (T001-T002)
  ↓
Contract Tests (T003-T007) [P] ← MUST FAIL FIRST
  ↓
Model Extensions (T008-T011) [P]
  ↓
Metadata Extractors (T012-T015) [P]
  ↓
Processor Integration (T016-T019) [sequential per module]
  ↓
CLI Updates (T020-T022) [P]
  ↓
Formatters (T023-T038) [sequential per module, 4 tasks each]
  ↓
Unit Tests (T039-T046) [P]
  ↓
Integration Tests (T047-T054) [can run in parallel with dependencies]
```

### Module-Specific Dependencies

**PDF Module**: T003 → T008 → T012 → T016 → T020 → T023-T026 → T039 → T047

**Image Module**: T004 → T009 → T013 → T017 → T021 → T027-T030 → T040 → T048

**Audio Module**: T006 → T010 → T014 → T018 → T022 → T031-T034 → T041 → T049

**Text Module**: T007 → T011 → T015 → T019 → T035-T038 → T042 → T050

**Cross-Module**: T045, T046 (after T012-T015), T051-T054 (after all formatters)

---

## Parallel Execution Examples

### Phase 3.2: Launch all contract tests together
```bash
# All contract tests are independent - run in parallel
uv run pytest tests/contract/test_metadata_schema.py &
uv run pytest tests/contract/test_pdf_metadata_contract.py &
uv run pytest tests/contract/test_image_metadata_contract.py &
uv run pytest tests/contract/test_audio_metadata_contract.py &
uv run pytest tests/contract/test_text_metadata_contract.py &
wait
```

### Phase 3.3: Launch all model extensions together
```bash
# Edit different files in parallel
# T008: anyfile_to_ai/pdf_extractor/models.py
# T009: anyfile_to_ai/image_processor/models.py
# T010: anyfile_to_ai/audio_processor/models.py
# T011: anyfile_to_ai/text_summarizer/models.py
```

### Phase 3.4: Launch all metadata extractors together
```bash
# Create different files in parallel
# T012: anyfile_to_ai/pdf_extractor/metadata.py
# T013: anyfile_to_ai/image_processor/metadata.py
# T014: anyfile_to_ai/audio_processor/metadata.py
# T015: anyfile_to_ai/text_summarizer/metadata.py
```

### Phase 3.6: Launch all CLI updates together
```bash
# Edit different files in parallel
# T020: anyfile_to_ai/pdf_extractor/cli.py
# T021: anyfile_to_ai/image_processor/cli.py
# T022: anyfile_to_ai/audio_processor/cli.py
```

### Phase 3.11: Launch all unit tests together
```bash
# All unit tests are independent - run in parallel
uv run pytest tests/unit/test_pdf_metadata.py &
uv run pytest tests/unit/test_image_metadata.py &
uv run pytest tests/unit/test_audio_metadata.py &
uv run pytest tests/unit/test_text_metadata.py &
uv run pytest tests/unit/test_timestamp_utils.py &
uv run pytest tests/unit/test_config_metadata.py &
uv run pytest tests/unit/test_unavailable_fields.py &
uv run pytest tests/unit/test_metadata_serialization.py &
wait
```

---

## Notes

- [P] tasks = different files, no dependencies, can run in parallel
- Formatters.py files already exist in all 4 modules (pdf_extractor, image_processor, audio_processor, text_summarizer) - tasks UPDATE existing formatter functions, not CREATE new files
- Formatter updates (T023-T038) modify same file per module, must be sequential within module
- Contract tests MUST be written first and MUST FAIL before implementation
- Each module follows: contract → model → extractor → processor → CLI → formatters → tests
- Metadata is optional (disabled by default except text_summarizer)
- Text summarizer extends existing metadata (backward compatible)
- Run `uv run ruff check .` after each phase
- Run `uv run pytest` after Phase 3.12
- Verify quickstart.md validation scenarios manually

---

## Task Generation Rules Applied

1. **From Contracts**:
   - metadata-schema.json → T003 (schema validation)
   - pdf-extractor-api.md → T004 (contract test)
   - image-processor-api.md → T005 (contract test)
   - audio-processor-api.md → T006 (contract test)
   - text-summarizer-api.md → T007 (contract test)

2. **From Data Model**:
   - ProcessingMetadata, ConfigurationMetadata, SourceMetadata → Universal structure
   - ExtractionResult → T008 (extend model)
   - DescriptionResult → T009 (extend model)
   - TranscriptionResult → T010 (extend model)
   - SummaryMetadata → T011 (extend model)
   - 4 type-specific metadata extractors → T012-T015

3. **From Quickstart**:
   - 10 integration test scenarios → T047-T054
   - Format preservation tests → T023-T038 (formatters)
   - Backward compatibility → T053

4. **Ordering**:
   - Setup → Contract Tests → Models → Extractors → Processors → CLI → Formatters → Tests
   - TDD: All contract tests before implementation
   - Sequential: Processor/formatter updates per module (same file)
   - Parallel: Models, extractors, CLI updates, tests (different files)

---

## Validation Checklist

_GATE: Checked before execution_

- [x] All contracts have corresponding tests (T003-T007)
- [x] All entities have model tasks (T008-T011: ExtractionResult, DescriptionResult, TranscriptionResult, SummaryMetadata)
- [x] All tests come before implementation (Phase 3.2 before Phase 3.3)
- [x] Parallel tasks truly independent (different files, no shared state)
- [x] Each task specifies exact file path (all tasks include module/file path)
- [x] No task modifies same file as another [P] task (formatters sequential per module)
- [x] All files designed to stay under 250 lines (metadata.py, model extensions are small additions)
- [x] Modular composition enforced (metadata extraction isolated to metadata.py)
- [x] Dependencies are minimal and justified (stdlib + existing deps only)

---

## Complexity Estimates

| Phase | Tasks | Est. Time | Parallel Potential |
|-------|-------|-----------|-------------------|
| 3.1 Setup | 2 | 15 min | Sequential |
| 3.2 Contract Tests | 5 | 2 hours | 100% (all [P]) |
| 3.3 Models | 4 | 1 hour | 100% (all [P]) |
| 3.4 Extractors | 4 | 3 hours | 100% (all [P]) |
| 3.5 Processors | 4 | 2 hours | 25% (per module) |
| 3.6 CLI | 3 | 1 hour | 100% (all [P]) |
| 3.7-3.10 Formatters | 16 | 4 hours | 25% (4 modules parallel, 4 formats sequential) |
| 3.11 Unit Tests | 8 | 3 hours | 100% (all [P]) |
| 3.12 Integration | 8 | 3 hours | 75% (7 parallel, 1 sequential) |
| **Total** | **54** | **19-20 hours** | **~60% parallelizable** |

---

## Success Criteria

After completing all tasks, verify:

1. ✅ All contract tests pass (T003-T007)
2. ✅ All unit tests pass (T039-T046)
3. ✅ All integration tests pass (T047-T054)
4. ✅ Backward compatibility maintained (metadata disabled by default)
5. ✅ Metadata structure consistent across all modules (processing/configuration/source)
6. ✅ ISO 8601 timestamps in all metadata
7. ✅ EXIF data extracted for images with proper tag names
8. ✅ Audio language confidence preserved
9. ✅ Text summarizer maintains existing metadata fields
10. ✅ Formatters preserve metadata in JSON/markdown/CSV outputs
11. ✅ Unavailable fields set to "unavailable" (not omitted)
12. ✅ Configuration metadata includes user_provided + effective
13. ✅ Performance overhead <1% (metadata extraction negligible)
14. ✅ Linting passes (`uv run ruff check .`)
15. ✅ Test coverage ≥80% (`pytest --cov`)
16. ✅ All quickstart scenarios validated manually

---

**Generated**: 2025-10-25
**Based on**: plan.md, research.md, data-model.md, contracts/ (5 files), quickstart.md
**Ready for Execution**: Yes - All prerequisites met, tasks ordered by dependencies
