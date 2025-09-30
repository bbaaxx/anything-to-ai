# Tasks: Enhanced PDF Extraction with Image Description

**Input**: Design documents from `/specs/005-augment-pdf-extraction/`
**Prerequisites**: plan.md (✓), research.md (✓), data-model.md (✓), contracts/ (✓), quickstart.md (✓)

## Execution Flow (main)

```
1. Load plan.md from feature directory ✓
   → Extract: Python 3.13, pdfplumber, mlx-vlm, PIL/Pillow, modular structure
2. Load design documents ✓
   → data-model.md: Extract entities → model tasks
   → contracts/: Each file → contract test task
   → research.md: Extract decisions → setup tasks
3. Generate tasks by category:
   → Setup: project init, dependencies, linting
   → Tests: contract tests, integration tests
   → Core: models, services, CLI commands
   → Integration: PDF-image processing, streaming
   → Polish: unit tests, performance, docs
4. Apply task rules:
   → Different files = mark [P] for parallel
   → Same file = sequential (no [P])
   → Tests before implementation (TDD)
5. Number tasks sequentially (T001, T002...)
6. Generate dependency graph
7. Create parallel execution examples
8. Validate task completeness ✓
```

## Format: `[ID] [P?] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- Include exact file paths in descriptions

## Phase 3.1: Setup

- [X] T001 Create enhanced PDF extraction project structure with image integration modules
- [X] T002 Initialize Python 3.13 project with pdfplumber, mlx-vlm, PIL dependencies (reuse existing)
- [X] T003 [P] Configure linting and 250-line limit enforcement for new modules

## Phase 3.2: Tests First (TDD) ⚠️ MUST COMPLETE BEFORE 3.3

**CRITICAL: These tests MUST be written and MUST FAIL before ANY implementation**

- [X] T004 [P] Contract test for enhanced_api.py interfaces in tests/contract/test_enhanced_api.py
- [X] T005 [P] Contract test for CLI interface in tests/contract/test_cli_interface.py
- [X] T006 [P] Contract test for exception hierarchy in tests/contract/test_exceptions.py
- [X] T007 [P] Integration test basic PDF with images extraction in tests/integration/test_pdf_with_images.py
- [X] T008 [P] Integration test backward compatibility in tests/integration/test_backward_compatibility.py
- [X] T009 [P] Integration test error scenarios in tests/integration/test_error_workflows.py
- [X] T010 [P] Integration test streaming with progress in tests/integration/test_streaming_progress.py

## Phase 3.3: Core Implementation (ONLY after tests are failing)

- [ ] T011 [P] EnhancedExtractionConfig model in pdf_extractor/enhanced_models.py
- [ ] T012 [P] ImageContext model in pdf_extractor/enhanced_models.py
- [ ] T013 [P] EnhancedPageResult model in pdf_extractor/enhanced_models.py
- [ ] T014 [P] EnhancedExtractionResult model in pdf_extractor/enhanced_models.py
- [ ] T015 [P] VLMCircuitBreaker class in pdf_extractor/image_integration.py
- [ ] T016 PDF image extraction service in pdf_extractor/image_integration.py
- [ ] T017 PDFImageProcessor orchestration class in pdf_extractor/image_integration.py
- [ ] T018 Enhanced CLI argument parser in pdf_extractor/cli.py
- [ ] T019 Enhanced output formatters in pdf_extractor/cli.py
- [ ] T020 Progress reporting enhancements in pdf_extractor/cli.py
- [ ] T021 Configuration validation logic in pdf_extractor/enhanced_models.py
- [ ] T022 Error handling integration in pdf_extractor/exceptions.py

## Phase 3.4: Integration

- [ ] T023 Integrate ImageProcessor adapter with PDFImageProcessor
- [ ] T024 Streaming enhancement for image processing pipeline
- [ ] T025 Position-aware text insertion with image descriptions
- [ ] T026 Memory-aware batch processing implementation
- [ ] T027 Circuit breaker integration with VLM service
- [ ] T028 Enhanced CLI main module integration

## Phase 3.5: Polish

- [ ] T029 [P] Unit tests for configuration validation in tests/unit/test_enhanced_models.py
- [ ] T030 [P] Unit tests for VLM circuit breaker in tests/unit/test_circuit_breaker.py
- [ ] T031 [P] Unit tests for image integration logic in tests/unit/test_image_integration.py
- [ ] T032 Performance tests for image processing batch sizes in tests/performance/test_batch_performance.py
- [ ] T033 [P] Update CLAUDE.md with enhanced extraction commands
- [ ] T034 File length validation (ensure all files ≤250 lines)
- [ ] T035 Execute quickstart.md validation scenarios
- [ ] T036 Final integration test with sample data

## Dependencies

- Setup (T001-T003) before everything
- Tests (T004-T010) before implementation (T011-T028)
- Models (T011-T014) before services (T015-T017)
- Models before CLI enhancements (T018-T022)
- Core implementation (T011-T022) before integration (T023-T028)
- Integration before polish (T029-T036)

## Parallel Example

```bash
# Launch T004-T006 together (contract tests):
Task: "Contract test for enhanced_api.py interfaces in tests/contract/test_enhanced_api.py"
Task: "Contract test for CLI interface in tests/contract/test_cli_interface.py"
Task: "Contract test for exception hierarchy in tests/contract/test_exceptions.py"

# Launch T007-T010 together (integration tests):
Task: "Integration test basic PDF with images extraction in tests/integration/test_pdf_with_images.py"
Task: "Integration test backward compatibility in tests/integration/test_backward_compatibility.py"
Task: "Integration test error scenarios in tests/integration/test_error_workflows.py"
Task: "Integration test streaming with progress in tests/integration/test_streaming_progress.py"

# Launch T011-T015 together (model implementations):
Task: "EnhancedExtractionConfig model in pdf_extractor/enhanced_models.py"
Task: "ImageContext model in pdf_extractor/enhanced_models.py"
Task: "EnhancedPageResult model in pdf_extractor/enhanced_models.py"
Task: "EnhancedExtractionResult model in pdf_extractor/enhanced_models.py"
Task: "VLMCircuitBreaker class in pdf_extractor/image_integration.py"

# Launch T029-T031, T033 together (unit tests and docs):
Task: "Unit tests for configuration validation in tests/unit/test_enhanced_models.py"
Task: "Unit tests for VLM circuit breaker in tests/unit/test_circuit_breaker.py"
Task: "Unit tests for image integration logic in tests/unit/test_image_integration.py"
Task: "Update CLAUDE.md with enhanced extraction commands"
```

## Notes

- [P] tasks = different files, no dependencies
- Verify tests fail before implementing
- Commit after each task completion
- All new files must stay under 250 lines (constitutional requirement)
- Maintain backward compatibility (existing PDF extraction unchanged)
- Progressive enhancement pattern (text first, images optional)

## Task Generation Rules

_Applied during task creation based on design documents_

1. **From Contracts**:
   - enhanced_api.py → T004 contract test task [P]
   - cli_interface.py → T005 contract test task [P]
   - exceptions.py → T006 contract test task [P]

2. **From Data Model**:
   - EnhancedExtractionConfig → T011 model task [P]
   - ImageContext → T012 model task [P]
   - EnhancedPageResult → T013 model task [P]
   - EnhancedExtractionResult → T014 model task [P]
   - VLMCircuitBreaker → T015 model task [P]

3. **From User Stories (quickstart.md)**:
   - Basic usage scenario → T007 integration test [P]
   - Backward compatibility → T008 integration test [P]
   - Error scenarios → T009 integration test [P]
   - Streaming processing → T010 integration test [P]

4. **Ordering Applied**:
   - Setup → Tests → Models → Services → CLI → Integration → Polish
   - Constitutional compliance: Each file ≤250 lines enforced in T034
   - TDD approach: All failing tests (T004-T010) before implementation (T011+)

## Validation Checklist

_Validated during task creation_

- [x] All contracts have corresponding tests (T004-T006)
- [x] All entities have model tasks (T011-T014)
- [x] All tests come before implementation (T004-T010 before T011+)
- [x] Parallel tasks truly independent (different files within phases)
- [x] Each task specifies exact file path
- [x] No task modifies same file as another [P] task
- [x] All files designed to stay under 250 lines (enforced in T034)
- [x] Modular composition enforced in task structure
- [x] Dependencies are minimal and justified (reuse existing modules)
- [x] Backward compatibility preserved (T008 validates this)
- [x] Progressive enhancement pattern maintained (optional image processing)