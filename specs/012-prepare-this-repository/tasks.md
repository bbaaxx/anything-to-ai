# Tasks: Prepare Repository for Python Packaging

**Input**: Design documents from `/specs/012-prepare-this-repository/`
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

- **Single project**: Repository root with `anyfile_to_ai/` package
- **Configuration**: `pyproject.toml` at repository root
- **Tests**: `tests/` directory structure maintained
- **Paths shown below assume repository root structure

## Phase 3.1: Setup

- [x] T001 Create anyfile_to_ai package directory structure at repository root
- [x] T002 Backup existing pyproject.toml and create new packaging configuration
- [x] T003 [P] Configure build system with setuptools and wheel in pyproject.toml

## Phase 3.2: Tests First (TDD) ⚠️ MUST COMPLETE BEFORE 3.3

**CRITICAL: These tests MUST be written and MUST FAIL before ANY implementation**

- [x] T004 [P] Contract test package metadata schema in tests/contract/test_package_metadata.py
- [x] T005 [P] Contract test entry points schema in tests/contract/test_entry_points.py
- [x] T006 [P] Contract test optional dependencies schema in tests/contract/test_optional_dependencies.py
- [x] T007 [P] Integration test package installation in tests/integration/test_installation.py
- [x] T008 [P] Integration test CLI functionality after installation in tests/integration/test_cli_installation.py

## Phase 3.3: Core Implementation (ONLY after tests are failing)

- [x] T009 [P] Package metadata configuration in pyproject.toml
- [x] T010 [P] Optional dependencies configuration in pyproject.toml
- [x] T011 [P] CLI entry points configuration in pyproject.toml
- [x] T012 Move existing modules to anyfile_to_ai/ package structure
- [x] T013 Update module imports for new package structure
- [x] T014 Create anyfile_to_ai/__init__.py with package metadata
- [x] T015 Update README.md for PyPI distribution

## Phase 3.4: Integration

- [x] T016 Configure build system and dependencies
- [x] T017 Test local package build with python -m build
- [x] T018 Test package installation in clean environment
- [x] T019 Validate CLI entry points after installation
- [x] T020 Test optional extras installation scenarios

## Phase 3.5: Polish

- [x] T021 [P] Unit tests for package configuration in tests/unit/test_package_config.py
- [x] T022 [P] Unit tests for import structure in tests/unit/test_imports.py
- [x] T023 Performance test package build time (<5 minutes)
- [x] T024 [P] Update documentation for installation procedures
- [x] T025 Validate package with twine check
- [x] T026 Remove temporary files and clean up structure

## Dependencies

- Tests (T004-T008) before implementation (T009-T015)
- T009 blocks T010, T011
- T012 blocks T013, T014
- Implementation before integration (T016-T020)
- Integration before polish (T021-T026)

## Parallel Example

```
# Launch T004-T008 together:
Task: "Contract test package metadata schema in tests/contract/test_package_metadata.py"
Task: "Contract test entry points schema in tests/contract/test_entry_points.py"
Task: "Contract test optional dependencies schema in tests/contract/test_optional_dependencies.py"
Task: "Integration test package installation in tests/integration/test_installation.py"
Task: "Integration test CLI functionality after installation in tests/integration/test_cli_installation.py"

# Launch T009-T011 together:
Task: "Package metadata configuration in pyproject.toml"
Task: "Optional dependencies configuration in pyproject.toml"
Task: "CLI entry points configuration in pyproject.toml"

# Launch T021-T022 together:
Task: "Unit tests for package configuration in tests/unit/test_package_config.py"
Task: "Unit tests for import structure in tests/unit/test_imports.py"
```

## Notes

- [P] tasks = different files, no dependencies
- Verify tests fail before implementing
- Commit after each task
- Avoid: vague tasks, same file conflicts

## Task Generation Rules

_Applied during main() execution_

1. **From Contracts**:
   - package-metadata.json → contract test task T004 [P]
   - entry-points.json → contract test task T005 [P]
   - optional-dependencies.json → contract test task T006 [P]
2. **From Data Model**:
   - Package Metadata Entity → configuration task T009 [P]
   - Optional Dependencies Entity → configuration task T010 [P]
   - CLI Entry Points Entity → configuration task T011 [P]
3. **From User Stories**:
   - Package installation → integration test T007 [P]
   - CLI functionality → integration test T008 [P]
   - Quickstart scenarios → validation tasks T017-T020

4. **Ordering**:
   - Setup → Tests → Configuration → Implementation → Integration → Polish
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