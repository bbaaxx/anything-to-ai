# Tasks: Text Summarizer Module

**Feature**: Text Summarizer Module
**Branch**: `009-summarizer-module-this`
**Design docs**: `<project_root>/specs/009-summarizer-module-this/`

## Execution Flow

```
1. Setup project structure for text_summarizer module
2. Write contract tests (TDD - tests must fail first)
3. Implement core components (models, exceptions, chunker, processor)
4. Implement CLI interface
5. Polish with unit tests and performance validation
```

## Format: `[ID] [P?] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- Tasks ordered by dependencies

---

## Phase 3.1: Setup

- [x] **T001** Create text_summarizer/ module structure

  - `text_summarizer/__init__.py`
  - `text_summarizer/models.py`
  - `text_summarizer/exceptions.py`
  - `text_summarizer/chunker.py`
  - `text_summarizer/processor.py`
  - `text_summarizer/__main__.py`
  - Keep each file under 250 lines per constitution

- [x] **T002** [P] Create test directory structure
  - `tests/contract/test_summarizer_api.py`
  - `tests/integration/test_summarizer_workflow.py`
  - `tests/unit/test_chunker.py`
  - `tests/unit/test_models.py`

---

## Phase 3.2: Tests First (TDD) ⚠️ MUST COMPLETE BEFORE 3.3

**CRITICAL: These tests MUST be written and MUST FAIL before ANY implementation**

- [x] **T003** [P] Contract test for `summarize_text` in tests/contract/test_summarizer_api.py

  - Test valid input returns SummaryResult
  - Test result has non-empty summary
  - Test result has ≥3 tags
  - Test metadata included/excluded based on flag
  - Test raises InvalidInputError for empty text
  - Test raises InvalidInputError for whitespace-only
  - Test handles small text (<1k words)
  - Test handles medium text (1k-10k words)
  - Test handles large text (>10k words, chunking)
  - Test handles non-English text (multilingual)

- [x] **T004** [P] Contract test for `create_summarizer` in tests/contract/test_summarizer_api.py

  - Test creates with default client
  - Test creates with custom client
  - Test sets custom chunk_size and chunk_overlap
  - Test raises ValueError if chunk_size < chunk_overlap
  - Test raises ValueError for invalid parameters

- [x] **T005** [P] Contract test for `chunk_text` in tests/contract/test_summarizer_api.py

  - Test returns single chunk for small text
  - Test returns multiple chunks for large text
  - Test chunks have sequential indices
  - Test chunks have correct word ranges
  - Test chunks overlap by specified amount
  - Test raises ValueError for empty text

- [x] **T006** [P] Contract test for CLI interface in tests/contract/test_summarizer_cli.py

  - Test reads from file path argument
  - Test reads from stdin with --stdin
  - Test outputs JSON by default
  - Test outputs plain text with --format plain
  - Test writes to stdout by default
  - Test writes to file with --output
  - Test shows help with --help
  - Test exit code 1 for invalid input
  - Test exit code 2 for LLM errors
  - Test exit code 3 for validation errors

- [x] **T007** [P] Integration test for basic summarization workflow in tests/integration/test_summarizer_workflow.py

  - Test scenario 1: Summarize simple text (from quickstart)
  - Test scenario 2: Plain text output format
  - Test scenario 3: Read from stdin
  - Test scenario 5: Non-English text (multilingual)
  - Test scenario 6: Output to file

- [x] **T008** [P] Integration test for large text chunking in tests/integration/test_summarizer_workflow.py

  - Test scenario 4: Large text with chunking (>10k words)
  - Verify metadata.chunked = true
  - Verify metadata.chunk_count > 1
  - Verify coherent summary despite chunking

- [x] **T009** [P] Integration test for module piping in tests/integration/test_summarizer_workflow.py

  - Test scenario 7: PDF → Summarizer pipeline
  - Test scenario 8: Audio → Summarizer pipeline
  - Test scenario 9: Image → Summarizer pipeline

- [x] **T010** [P] Integration test for error handling in tests/integration/test_summarizer_workflow.py
  - Test scenario 10: Empty input
  - Test scenario 11: Invalid UTF-8
  - Test scenario 12: File not found

---

## Phase 3.3: Core Implementation (ONLY after tests are failing)

- [x] **T011** [P] Implement exceptions in text_summarizer/exceptions.py

  - SummarizerError (base)
  - InvalidInputError
  - LLMError
  - ValidationError
  - Keep file under 50 lines

- [x] **T012** [P] Implement data models in text_summarizer/models.py

  - SummaryRequest (with field validators)
  - SummaryResult (with field validators)
  - SummaryMetadata
  - TextChunk (with field validators)
  - Follow data-model.md specifications
  - Keep file under 200 lines

- [x] **T013** [P] Implement chunker in text_summarizer/chunker.py

  - chunk_text function (sliding window with overlap)
  - Helper functions if needed (keep under 50 lines each)
  - Follow research.md chunking strategy
  - Keep file under 150 lines

- [x] **T014** Implement processor core in text_summarizer/processor.py

  - TextSummarizer class
  - create_summarizer factory function
  - LLM prompt builder (from research.md)
  - Response parser
  - Hierarchical summarization for chunked text
  - Keep file under 250 lines (may need composition)

- [x] **T015** Implement summarize_text in text_summarizer/processor.py

  - Main API function
  - Integrates with LLM client
  - Handles small and large texts
  - Error handling and validation
  - Must work with T014 (same file, sequential)

- [x] **T016** [P] Implement CLI interface in text_summarizer/**main**.py

  - Argument parsing (argparse)
  - File/stdin reading
  - Output formatting (JSON and plain)
  - File/stdout writing
  - Exit codes (0, 1, 2, 3)
  - Verbose logging
  - Keep file under 200 lines

- [x] **T017** Implement module exports in text_summarizer/**init**.py
  - Import and re-export all public APIs
  - Define **all**
  - Follow module_api.md contract
  - Keep file under 50 lines

---

## Phase 3.4: Integration

- [x] **T018** Integrate with llm_client module

  - Verify llm_client import works
  - Test with actual LLM calls (small text)
  - Verify prompt engineering works
  - May require updates to processor.py (T014/T015)

- [x] **T019** Test piping with existing modules
  - pdf_extractor → text_summarizer
  - audio_processor → text_summarizer
  - image_processor → text_summarizer
  - Verify output format compatibility

---

## Phase 3.5: Polish

- [x] **T020** [P] Unit tests for chunker in tests/unit/test_chunker.py

  - Test edge cases (empty, single word, exact boundaries)
  - Test overlap calculation
  - Test word range accuracy

- [x] **T021** [P] Unit tests for models in tests/unit/test_models.py

  - Test Pydantic validation rules
  - Test field validators
  - Test error messages

- [ ] **T022** [P] Performance tests in tests/performance/test_summarizer_perf.py

  - Small text: < 5 seconds
  - Medium text: < 30 seconds
  - Large text: < 5 minutes
  - Memory usage: < 200MB

- [x] **T023** Update CLAUDE.md

  - Add text_summarizer CLI usage
  - Add summarization commands
  - Update tech stack
  - Update recent changes

- [x] **T024** Manual testing from quickstart.md
  - Run all 14 quickstart scenarios manually
  - Verify all validation checks pass
  - Document any deviations

---

## Dependencies

```
T001 (setup) → blocks all other tasks
T002 (test structure) → blocks T003-T010

Tests (T003-T010) → MUST COMPLETE before implementation (T011-T017)

T011 (exceptions) → blocks T012, T014, T015, T016
T012 (models) → blocks T014, T015
T013 (chunker) → blocks T014, T015
T014 (processor core) → blocks T015, T018
T015 (summarize_text) → blocks T018
T016 (CLI) → no blockers

T018 (LLM integration) → blocks T019, T022, T024
T019 (piping) → blocks T024

Polish tasks (T020-T024) → only start after T018 complete
```

---

## Parallel Execution Examples

### Setup Phase (Run Together)

```bash
# After T001 complete, create test structure:
# Can run as single task (directory creation is fast)
```

### Test Phase (Run T003-T006 in Parallel)

```python
# Launch 4 agents in parallel to write contract tests:
Task("Contract test for summarize_text in tests/contract/test_summarizer_api.py")
Task("Contract test for create_summarizer in tests/contract/test_summarizer_api.py")
Task("Contract test for chunk_text in tests/contract/test_summarizer_api.py")
Task("Contract test for CLI in tests/contract/test_summarizer_cli.py")
```

### Test Phase (Run T007-T010 in Parallel)

```python
# Launch 4 agents in parallel to write integration tests:
Task("Integration test for basic workflow in tests/integration/test_summarizer_workflow.py")
Task("Integration test for large text in tests/integration/test_summarizer_workflow.py")
Task("Integration test for module piping in tests/integration/test_summarizer_workflow.py")
Task("Integration test for error handling in tests/integration/test_summarizer_workflow.py")
```

**NOTE**: T007-T009 write to same file - may conflict. Better to run sequentially or coordinate.

### Implementation Phase (Run T011-T013, T016 in Parallel)

```python
# Launch 4 agents in parallel (different files):
Task("Implement exceptions in text_summarizer/exceptions.py")
Task("Implement models in text_summarizer/models.py")
Task("Implement chunker in text_summarizer/chunker.py")
Task("Implement CLI in text_summarizer/__main__.py")
# Note: T014-T015 cannot be parallel (same file), run after T011-T013
```

### Polish Phase (Run T020-T022 in Parallel)

```python
# Launch 3 agents in parallel (different files):
Task("Unit tests for chunker in tests/unit/test_chunker.py")
Task("Unit tests for models in tests/unit/test_models.py")
Task("Performance tests in tests/performance/test_summarizer_perf.py")
```

---

## Validation Checklist

_GATE: Verify before marking feature complete_

- [ ] All contract tests (T003-T006) pass
- [ ] All integration tests (T007-T010) pass
- [ ] All unit tests (T020-T021) pass
- [ ] Performance tests (T022) meet benchmarks
- [ ] Manual testing (T024) completes successfully
- [ ] All files are under 250 lines
- [ ] Module exports match module_api.md contract
- [ ] CLI follows existing module patterns
- [ ] Integration with llm_client works
- [ ] Piping with other modules works
- [ ] Error handling is comprehensive
- [ ] CLAUDE.md is updated
- [ ] No linting errors (ruff check passes)

---

## Notes

- **TDD is mandatory**: All tests must be written and failing before implementation
- **File size limit**: 250 lines per file (constitution requirement)
- **Minimal dependencies**: Only llm_client + standard library
- **Consistency**: Follow patterns from image_processor and audio_processor
- **Composition**: If processor.py exceeds 250 lines, split into separate files
- **Contract compliance**: All APIs must match module_api.md exactly
- **Test coverage**: Aim for >90% coverage

---

**Generated**: 2025-10-01
**Status**: Ready for execution
**Estimated effort**: 8-12 hours for experienced developer
