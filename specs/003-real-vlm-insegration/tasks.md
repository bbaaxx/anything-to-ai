# Tasks: Real VLM Integration

**Input**: Design documents from `/specs/003-real-vlm-insegration/`
**Prerequisites**: plan.md (required), research.md, data-model.md, contracts/

## Execution Flow (main)

```
1. Load plan.md from feature directory
   → Extract: Python 3.13, mlx-vlm, PIL/Pillow, existing image_processor
2. Load design documents:
   → data-model.md: 5 entities → model tasks
   → contracts/: 3 files → contract test tasks
   → research.md: Environment config, MLX patterns
   → quickstart.md: 7 test scenarios
3. Generate tasks by category:
   → Setup: mlx-vlm dependency, environment validation
   → Tests: contract tests, integration tests (TDD)
   → Core: VLM models, processor, configuration
   → Integration: Replace mock, enhance CLI
   → Polish: unit tests, performance, validation
4. Apply task rules:
   → Different files = mark [P] for parallel
   → Same file = sequential (no [P])
   → Tests before implementation (TDD)
5. Number tasks sequentially (T001-T027)
6. Generate dependency graph
7. Create parallel execution examples
8. Validate: All contracts tested, all entities implemented
9. Return: SUCCESS (tasks ready for execution)
```

## Format: `[ID] [P?] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- Include exact file paths in descriptions

## Phase 3.1: Setup

- [X] T001 Add mlx-vlm dependency to project with uv add mlx-vlm
- [X] T002 [P] Create environment validation script for VISION_MODEL in image_processor/config.py
- [X] T003 [P] Configure linting to enforce <100 line files for new VLM modules

## Phase 3.2: Tests First (TDD) ⚠️ MUST COMPLETE BEFORE 3.3

**CRITICAL: These tests MUST be written and MUST FAIL before ANY implementation**

### Contract Tests
- [X] T004 [P] Contract test module API functions in tests/contract/test_module_api.py
- [X] T005 [P] Contract test CLI interface behavior in tests/contract/test_cli_interface.py
- [X] T006 [P] Contract test VLM integration protocols in tests/contract/test_vlm_integration.py

### Integration Tests (from quickstart.md scenarios)
- [X] T007 [P] Integration test basic VLM processing in tests/integration/test_basic_vlm.py
- [X] T008 [P] Integration test model configuration validation in tests/integration/test_model_config.py
- [X] T009 [P] Integration test invalid model handling in tests/integration/test_invalid_model.py
- [X] T010 [P] Integration test timeout behavior in tests/integration/test_timeout_behavior.py
- [X] T011 [P] Integration test batch processing cleanup in tests/integration/test_batch_cleanup.py
- [X] T012 [P] Integration test backward compatibility in tests/integration/test_backward_compat.py
- [X] T013 [P] Integration test module API compatibility in tests/integration/test_module_api_compat.py

## Phase 3.3: Core Implementation (ONLY after tests are failing)

### Data Models and Exceptions
- [X] T014 [P] VLM-specific exception types in image_processor/vlm_exceptions.py
- [X] T015 [P] ModelConfiguration entity in image_processor/vlm_models.py
- [X] T016 [P] LoadedModel and ModelRegistry in image_processor/model_registry.py
- [X] T017 [P] EnhancedResult with VLM + technical metadata in image_processor/enhanced_result.py

### VLM Core Components
- [X] T018 VLM configuration loader from environment in image_processor/vlm_config.py
- [X] T019 VLMModel protocol implementation with MLX in image_processor/vlm_model_impl.py
- [X] T020 VLMProcessor for single/batch processing in image_processor/vlm_processor.py
- [X] T021 Model validation and loading logic in image_processor/model_loader.py

## Phase 3.4: Integration

### Replace Mock Implementation
- [X] T022 Update ProcessingConfig to use VISION_MODEL environment variable in image_processor/models.py
- [X] T023 Replace mock VLM processing with real implementation in image_processor/processor.py
- [X] T024 Integrate VLM processor with existing streaming pipeline in image_processor/streaming.py
- [X] T025 Update CLI to support VLM environment configuration in image_processor/cli.py

## Phase 3.5: Polish

### Testing and Validation
- [ ] T026 [P] Unit tests for VLM configuration in tests/unit/test_vlm_config.py
- [ ] T027 [P] Unit tests for model registry in tests/unit/test_model_registry.py
- [ ] T028 [P] Unit tests for VLM processor in tests/unit/test_vlm_processor.py
- [ ] T029 Performance tests for VLM processing (<5s per image) in tests/performance/test_vlm_performance.py
- [ ] T030 Error handling robustness tests in tests/integration/test_error_handling.py

### Documentation and Final Validation
- [X] T031 [P] Update module docstrings to reflect real VLM integration in image_processor/__init__.py
- [ ] T032 End-to-end validation with real model using quickstart scenarios

## Dependencies

- Setup (T001-T003) before everything
- Contract tests (T004-T006) before implementation (T014-T025)
- Integration tests (T007-T013) before implementation (T014-T025)
- T014 (exceptions) blocks T018-T021 (VLM components need exceptions)
- T015-T017 (data models) before T018-T021 (VLM components need models)
- T018 (config) blocks T019-T021 (components need configuration)
- T019 (VLM model) blocks T020 (processor needs model implementation)
- T022-T025 (integration) after T014-T021 (need core components)
- Polish (T026-T032) after integration complete

## Parallel Example

### Launch contract tests together:
```bash
Task: "Contract test module API functions in tests/contract/test_module_api.py"
Task: "Contract test CLI interface behavior in tests/contract/test_cli_interface.py"
Task: "Contract test VLM integration protocols in tests/contract/test_vlm_integration.py"
```

### Launch integration tests together:
```bash
Task: "Integration test basic VLM processing in tests/integration/test_basic_vlm.py"
Task: "Integration test model configuration validation in tests/integration/test_model_config.py"
Task: "Integration test invalid model handling in tests/integration/test_invalid_model.py"
Task: "Integration test timeout behavior in tests/integration/test_timeout_behavior.py"
Task: "Integration test batch processing cleanup in tests/integration/test_batch_cleanup.py"
Task: "Integration test backward compatibility in tests/integration/test_backward_compat.py"
Task: "Integration test module API compatibility in tests/integration/test_module_api_compat.py"
```

### Launch data model creation together:
```bash
Task: "VLM-specific exception types in image_processor/vlm_exceptions.py"
Task: "ModelConfiguration entity in image_processor/vlm_models.py"
Task: "LoadedModel and ModelRegistry in image_processor/model_registry.py"
Task: "EnhancedResult with VLM + technical metadata in image_processor/enhanced_result.py"
```

## Notes

- [P] tasks = different files, no dependencies
- Verify tests fail before implementing
- Environment variable VISION_MODEL required for VLM processing
- Maintain exact backward compatibility (no API breaking changes)
- Model lifecycle: validate → load → process → cleanup
- Real MLX-VLM integration replaces mock implementation

## Task Generation Rules

_Applied during main() execution_

1. **From Contracts (3 files)**:
   - contracts/module_api.py → T004 contract test [P]
   - contracts/cli_interface.py → T005 contract test [P]
   - contracts/vlm_integration.py → T006 contract test [P]

2. **From Data Model (5 entities)**:
   - ModelConfiguration → T015 model creation [P]
   - LoadedModel → T016 model creation [P]
   - ModelRegistry → T016 model creation [P]
   - EnhancedResult → T017 model creation [P]
   - TechnicalMetadata → existing (preserved)

3. **From Quickstart (7 scenarios)**:
   - Basic VLM processing → T007 integration test [P]
   - Model configuration validation → T008 integration test [P]
   - Invalid model handling → T009 integration test [P]
   - Timeout behavior → T010 integration test [P]
   - Batch processing cleanup → T011 integration test [P]
   - Backward compatibility → T012 integration test [P]
   - Module API compatibility → T013 integration test [P]

4. **Ordering**:
   - Setup → Tests → Models → VLM Core → Integration → Polish
   - Exception types before components using them
   - Configuration before processing components

## Validation Checklist

_GATE: Checked by main() before returning_

- [x] All 3 contracts have corresponding tests (T004-T006)
- [x] All 5 entities have model tasks (T014-T017)
- [x] All 7 quickstart scenarios have tests (T007-T013)
- [x] All tests come before implementation (T004-T013 before T014-T025)
- [x] Parallel tasks truly independent (different files marked [P])
- [x] Each task specifies exact file path
- [x] No task modifies same file as another [P] task
- [x] All files designed to stay under 100 lines per new modules
- [x] Modular composition enforced (separate files for config, models, processor)
- [x] Dependencies are minimal and justified (MLX-VLM only new dependency)
- [x] TDD approach enforced (tests fail before implementation)
- [x] Backward compatibility preserved (enhanced but compatible API)

## Success Criteria

1. ✅ **Real VLM Integration**: MLX-VLM replaces mock implementation
2. ✅ **Environment Configuration**: VISION_MODEL drives model selection
3. ✅ **Enhanced Results**: VLM descriptions + technical metadata
4. ✅ **Model Management**: Validation, loading, lifecycle, cleanup
5. ✅ **Error Handling**: VLM-specific exceptions with clear messages
6. ✅ **Backward Compatibility**: All existing APIs preserved exactly
7. ✅ **Performance**: Reasonable processing times with memory cleanup
8. ✅ **Testing**: Comprehensive test coverage including contract and integration tests

## Implementation Notes

- **Environment Variables**: VISION_MODEL (required), VLM_TIMEOUT_BEHAVIOR (optional), VLM_AUTO_DOWNLOAD (optional)
- **Model Registry**: Singleton pattern with lazy loading and cleanup hooks
- **Memory Management**: MLX cache clearing after batch processing
- **Error Strategy**: Fail fast on configuration issues, graceful handling during processing
- **CLI Compatibility**: All existing arguments preserved, environment-based model selection
- **Output Enhancement**: JSON/CSV/plain formats enhanced with VLM data while preserving structure
