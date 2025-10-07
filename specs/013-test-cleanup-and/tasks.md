# Tasks: Test Cleanup and Quality Assurance

**Input**: Design documents from `/specs/013-test-cleanup-and/`
**Prerequisites**: plan.md (required), research.md, data-model.md, contracts/

## Execution Flow (main)

```
1. Load plan.md from feature directory
   → If not found: ERROR "No implementation plan found"
   → Extract: tech stack, libraries, structure
2. Load optional design documents:
   → data-model.md: Extract entities → model tasks
   → contracts/: Each file → contract test task
   → research.md: Extract decisions → setup tasks
3. Generate tasks by category:
   → Setup: project init, dependencies, linting
   → Tests: contract tests, integration tests
   → Core: models, services, CLI commands
   → Integration: DB, middleware, logging
   → Polish: unit tests, performance, docs
4. Apply task rules:
   → Different files = mark [P] for parallel
   → Same file = sequential (no [P])
   → Tests before implementation (TDD)
5. Number tasks sequentially (T001, T002...)
6. Generate dependency graph
7. Create parallel execution examples
8. Validate task completeness:
   → All contracts have tests?
   → All entities have models?
   → All endpoints implemented?
9. Return: SUCCESS (tasks ready for execution)
```

## Format: `[ID] [P?] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `anyfile_to_ai/`, `tests/` at repository root
- Paths shown below reflect actual project structure from plan.md

## Phase 3.1: Setup

- [ ] T001 Create test quality infrastructure directory structure
- [ ] T002 Configure pytest with coverage plugin and flaky test detection
- [ ] T003 [P] Configure ruff for complexity and maintainability metrics
- [ ] T004 [P] Setup pre-commit hooks for test and quality validation

## Phase 3.2: Tests First (TDD) ⚠️ MUST COMPLETE BEFORE 3.3

**CRITICAL: These tests MUST be written and MUST FAIL before ANY implementation**

- [ ] T005 [P] Contract test GET /api/test/suites in tests/contract/test_test_suites_get.py
- [ ] T006 [P] Contract test POST /api/test/suites/{suite_id}/run in tests/contract/test_test_suites_run.py
- [ ] T007 [P] Contract test POST /api/test/suites/{suite_id}/quarantine in tests/contract/test_test_suites_quarantine.py
- [ ] T008 [P] Contract test GET /api/quality/reports in tests/contract/test_quality_reports_get.py
- [ ] T009 [P] Contract test POST /api/quality/check in tests/contract/test_quality_check.py
- [ ] T010 [P] Contract test POST /api/quality/fix in tests/contract/test_quality_fix.py
- [ ] T011 [P] Contract test GET /api/coverage/modules in tests/contract/test_coverage_modules_get.py
- [ ] T012 [P] Contract test POST /api/coverage/measure in tests/contract/test_coverage_measure.py
- [ ] T013 [P] Integration test test cleanup workflow in tests/integration/test_cleanup_workflow.py
- [ ] T014 [P] Integration test quality enforcement workflow in tests/integration/test_quality_workflow.py
- [ ] T015 [P] Integration test coverage improvement workflow in tests/integration/test_coverage_workflow.py

## Phase 3.3: Core Implementation (ONLY after tests are failing)

- [ ] T016 [P] TestSuite model in anyfile_to_ai/test_quality/models/test_suite.py
- [ ] T017 [P] QualityReport model in anyfile_to_ai/test_quality/models/quality_report.py
- [ ] T018 [P] QualityViolation model in anyfile_to_ai/test_quality/models/quality_violation.py
- [ ] T019 [P] TestResult model in anyfile_to_ai/test_quality/models/test_result.py
- [ ] T020 [P] CoverageData model in anyfile_to_ai/test_quality/models/coverage_data.py
- [ ] T021 [P] TestSuiteService in anyfile_to_ai/test_quality/services/test_suite_service.py
- [ ] T022 [P] QualityCheckService in anyfile_to_ai/test_quality/services/quality_check_service.py
- [ ] T023 [P] CoverageService in anyfile_to_ai/test_quality/services/coverage_service.py
- [ ] T024 GET /api/test/suites endpoint implementation
- [ ] T025 POST /api/test/suites/{suite_id}/run endpoint implementation
- [ ] T026 POST /api/test/suites/{suite_id}/quarantine endpoint implementation
- [ ] T027 GET /api/quality/reports endpoint implementation
- [ ] T028 POST /api/quality/check endpoint implementation
- [ ] T029 POST /api/quality/fix endpoint implementation
- [ ] T030 GET /api/coverage/modules endpoint implementation
- [ ] T031 POST /api/coverage/measure endpoint implementation

## Phase 3.4: Integration & Fix Implementation

- [ ] T032 Fix import issues in tests/unit/test_package_config.py
- [ ] T033 Fix import issues in tests/unit/test_imports.py
- [ ] T034 Fix import issues in tests/unit/test_utils.py
- [ ] T035 Fix import issues in tests/unit/test_models.py
- [ ] T036 Fix import issues in tests/unit/test_performance.py
- [ ] T037 Fix import issues in tests/integration/test_ollama_integration.py
- [ ] T038 Fix import issues in tests/contract/test_adapter_interface.py
- [ ] T039 Fix import issues in tests/contract/test_audio_module_api.py
- [ ] T040 Fix import issues in tests/contract/test_cli_interface_enhanced.py
- [ ] T041 Fix type annotation issues in anyfile_to_ai/image_processor/__init__.py
- [ ] T042 Fix type annotation issues in anyfile_to_ai/llm_client/adapters/mlx_adapter.py
- [ ] T043 Fix type annotation issues in anyfile_to_ai/pdf_extractor/image_adapter.py
- [ ] T044 Fix type annotation issues in anyfile_to_ai/audio_processor/__init__.py
- [ ] T045 Fix type annotation issues in specs/005-augment-pdf-extraction/contracts/cli_interface.py
- [ ] T046 Implement flaky test detection and quarantine system
- [ ] T047 Implement atomic fix validation system
- [ ] T048 Configure ruff rules for complexity and maintainability
- [ ] T049 Setup coverage measurement and reporting
- [ ] T050 Integrate test quality services with existing test runners

## Phase 3.5: Validation & Polish

- [ ] T051 [P] Unit tests for TestSuite model in tests/unit/test_models/test_test_suite.py
- [ ] T052 [P] Unit tests for QualityReport model in tests/unit/test_models/test_quality_report.py
- [ ] T053 [P] Unit tests for QualityViolation model in tests/unit/test_models/test_quality_violation.py
- [ ] T054 [P] Unit tests for TestResult model in tests/unit/test_models/test_test_result.py
- [ ] T055 [P] Unit tests for CoverageData model in tests/unit/test_models/test_coverage_data.py
- [ ] T056 [P] Unit tests for TestSuiteService in tests/unit/test_services/test_test_suite_service.py
- [ ] T057 [P] Unit tests for QualityCheckService in tests/unit/test_services/test_quality_check_service.py
- [ ] T058 [P] Unit tests for CoverageService in tests/unit/test_services/test_coverage_service.py
- [ ] T059 Performance validation: test suite execution under 5 minutes
- [ ] T060 Performance validation: quality checks under 2 minutes
- [ ] T061 Validate 80% coverage target achievement
- [ ] T062 Validate complexity metrics within acceptable range
- [ ] T063 [P] Update documentation for test quality processes
- [ ] T064 [P] Create troubleshooting guide for common issues
- [ ] T065 Final integration test: complete workflow validation

## Dependencies

- Setup (T001-T004) before everything
- Contract tests (T005-T012) before implementation (T016-T031)
- Integration tests (T013-T015) before implementation (T016-T031)
- Models (T016-T020) before services (T021-T023)
- Services (T021-T023) before endpoints (T024-T031)
- Import fixes (T032-T045) before integration (T046-T050)
- Core implementation before polish (T051-T065)

## Parallel Example

```
# Launch T005-T012 together (contract tests):
Task: "Contract test GET /api/test/suites in tests/contract/test_test_suites_get.py"
Task: "Contract test POST /api/test/suites/{suite_id}/run in tests/contract/test_test_suites_run.py"
Task: "Contract test POST /api/test/suites/{suite_id}/quarantine in tests/contract/test_test_suites_quarantine.py"
Task: "Contract test GET /api/quality/reports in tests/contract/test_quality_reports_get.py"
Task: "Contract test POST /api/quality/check in tests/contract/test_quality_check.py"
Task: "Contract test POST /api/quality/fix in tests/contract/test_quality_fix.py"
Task: "Contract test GET /api/coverage/modules in tests/contract/test_coverage_modules_get.py"
Task: "Contract test POST /api/coverage/measure in tests/contract/test_coverage_measure.py"

# Launch T016-T020 together (model creation):
Task: "TestSuite model in anyfile_to_ai/test_quality/models/test_suite.py"
Task: "QualityReport model in anyfile_to_ai/test_quality/models/quality_report.py"
Task: "QualityViolation model in anyfile_to_ai/test_quality/models/quality_violation.py"
Task: "TestResult model in anyfile_to_ai/test_quality/models/test_result.py"
Task: "CoverageData model in anyfile_to_ai/test_quality/models/coverage_data.py"

# Launch T032-T045 together (import fixes):
Task: "Fix import issues in tests/unit/test_package_config.py"
Task: "Fix import issues in tests/unit/test_imports.py"
Task: "Fix import issues in tests/unit/test_utils.py"
Task: "Fix import issues in tests/unit/test_models.py"
Task: "Fix import issues in tests/unit/test_performance.py"
Task: "Fix import issues in tests/integration/test_ollama_integration.py"
Task: "Fix import issues in tests/contract/test_adapter_interface.py"
Task: "Fix import issues in tests/contract/test_audio_module_api.py"
Task: "Fix import issues in tests/contract/test_cli_interface_enhanced.py"
Task: "Fix import issues in anyfile_to_ai/image_processor/__init__.py"
Task: "Fix import issues in anyfile_to_ai/llm_client/adapters/mlx_adapter.py"
Task: "Fix import issues in anyfile_to_ai/pdf_extractor/image_adapter.py"
Task: "Fix import issues in anyfile_to_ai/audio_processor/__init__.py"
Task: "Fix import issues in specs/005-augment-pdf-extraction/contracts/cli_interface.py"
```

## Notes

- [P] tasks = different files, no dependencies
- Verify tests fail before implementing
- Commit after each task
- Focus on existing codebase cleanup, not new features
- All fixes must be atomic (no new issues introduced)
- Target 80% test coverage minimum
- Enforce complexity and maintainability metrics

## Task Generation Rules

_Applied during main() execution_

1. **From Contracts**:
   - Each contract file → contract test task [P]
   - Each endpoint → implementation task
2. **From Data Model**:
   - Each entity → model creation task [P]
   - Relationships → service layer tasks
3. **From User Stories**:
   - Each story → integration test [P]
   - Quickstart scenarios → validation tasks

4. **Ordering**:
   - Setup → Tests → Models → Services → Endpoints → Polish
   - Dependencies block parallel execution

## Validation Checklist

_GATE: Checked by main() before returning_

- [x] All contracts have corresponding tests
- [x] All entities have model tasks
- [x] All tests come before implementation
- [x] Parallel tasks truly independent
- [x] Each task specifies exact file path
- [x] No task modifies same file as another [P] task
- [x] All files designed to stay under 250 lines
- [x] Modular composition enforced in task structure
- [x] Dependencies are minimal and justified
