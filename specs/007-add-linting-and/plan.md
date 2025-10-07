# Implementation Plan: Automated Linting and Testing Infrastructure

**Branch**: `007-add-linting-and` | **Date**: 2025-09-29 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/007-add-linting-and/spec.md`

## Execution Flow (/plan command scope)

```
1. Load feature spec from Input path
   → If not found: ERROR "No feature spec at {path}"
2. Fill Technical Context (scan for NEEDS CLARIFICATION)
   → Detect Project Type from file system structure or context (web=frontend+backend, mobile=app+api)
   → Set Structure Decision based on project type
3. Fill the Constitution Check section based on the content of the constitution document.
4. Evaluate Constitution Check section below
   → If violations exist: Document in Complexity Tracking
   → If no justification possible: ERROR "Simplify approach first"
   → Update Progress Tracking: Initial Constitution Check
5. Execute Phase 0 → research.md
   → If NEEDS CLARIFICATION remain: ERROR "Resolve unknowns"
6. Execute Phase 1 → contracts, data-model.md, quickstart.md, CLAUDE.md
7. Re-evaluate Constitution Check section
   → If new violations: Refactor design, return to Phase 1
   → Update Progress Tracking: Post-Design Constitution Check
8. Plan Phase 2 → Describe task generation approach (DO NOT create tasks.md)
9. STOP - Ready for /tasks command
```

**IMPORTANT**: The /plan command STOPS at step 8. Phases 2-4 are executed by other commands:

- Phase 2: /tasks command creates tasks.md
- Phase 3-4: Implementation execution (manual or via tools)

## Summary

This feature adds automated linting and testing infrastructure to ensure code quality through pre-commit hooks. The system will enforce a 70% test coverage threshold, automatically fix simple style issues, and require manual fixes for complex violations. The infrastructure must work on macOS and Linux, prioritize completeness over speed, and integrate with the existing test structure (unit, integration, contract, performance).

## Technical Context

**Language/Version**: Python 3.13
**Primary Dependencies**: pre-commit (hook framework), ruff (linting/formatting), pytest (testing), pytest-cov (coverage measurement)
**Storage**: N/A (configuration files only)
**Testing**: pytest with coverage reporting, existing test structure (unit/integration/contract/performance)
**Target Platform**: macOS and Linux (developer workstations)
**Project Type**: single (multiple module packages in flat structure)
**Performance Goals**: No time limit - completeness over speed for pre-commit checks
**Constraints**:
- 70% minimum test coverage requirement
- 250-line maximum file length (constitution requirement)
- Must integrate with existing ruff and pytest configurations
- Pre-commit hooks only (no CI/CD integration)
**Scale/Scope**: 3 existing modules (pdf_extractor, image_processor, audio_processor) + tests directory

## Constitution Check

_GATE: Must pass before Phase 0 research. Re-check after Phase 1 design._

**Composition-First Check**:

- [x] All components are independently functional and testable (pre-commit hooks are standalone, configuration files are separate)
- [x] No monolithic structures proposed (hooks invoke separate tools: ruff, pytest)
- [x] Complexity emerges through composition, not component complexity (multiple tools orchestrated via pre-commit)

**250-Line Rule Check**:

- [x] No single file planned exceeds 250 lines (configuration files are minimal)
- [x] Large modules identified for modular breakdown (N/A - no implementation modules)
- [x] Clear refactoring strategy for size violations (N/A - only configuration)

**Minimal Dependencies Check**:

- [x] All dependencies justified with clear rationale:
  - pre-commit: Industry-standard hook framework, manages git hooks
  - ruff: Fast Python linter/formatter (already in project)
  - pytest: Already in project for testing
  - pytest-cov: Coverage measurement (lightweight plugin)
- [x] Standard library solutions preferred over external packages (git hooks use standard git mechanisms)
- [x] Dependency audit plan included (minimal new dependencies, all well-maintained)

**Experimental Mindset Check**:

- [x] Learning objectives documented (exploring pre-commit hook patterns, coverage enforcement)
- [x] Quick iteration approach planned (start with essential hooks, expand as needed)
- [x] Breaking changes acceptable for architectural improvements (can adjust hook configuration easily)

**Modular Architecture Check**:

- [x] Single responsibility per module:
  - pre-commit config: Hook orchestration
  - ruff config: Linting/formatting rules
  - pytest config: Test execution and coverage
- [x] Clear interface definitions between modules (standard CLI interfaces)
- [x] Modules designed for replaceability (can swap ruff for another linter, pytest for another test runner)

## Project Structure

### Documentation (this feature)

```
specs/007-add-linting-and/
├── plan.md              # This file (/plan command output)
├── research.md          # Phase 0 output (/plan command)
├── data-model.md        # Phase 1 output (/plan command)
├── quickstart.md        # Phase 1 output (/plan command)
├── contracts/           # Phase 1 output (/plan command)
└── tasks.md             # Phase 2 output (/tasks command - NOT created by /plan)
```

### Source Code (repository root)

```
# Single project structure
.pre-commit-config.yaml  # Pre-commit hook configuration (NEW)
pyproject.toml           # Extended with coverage and additional lint rules (MODIFIED)

pdf_extractor/          # Existing module
audio_processor/        # Existing module
image_processor/        # Existing module

tests/
├── contract/           # Existing
├── integration/        # Existing
├── unit/               # Existing
└── performance/        # Existing
```

**Structure Decision**: Single project with multiple module packages. The linting and testing infrastructure is repository-wide configuration, not a new module. This aligns with the existing flat structure where each processor is a top-level package.

## Phase 0: Outline & Research

**Research Topics**:

1. **pre-commit framework best practices**
   - How to configure pre-commit for Python projects
   - Hook execution order and dependencies
   - Performance optimization strategies (caching)
   - Cross-platform compatibility (macOS/Linux)

2. **pytest-cov configuration**
   - Setting minimum coverage thresholds
   - Excluding files from coverage (e.g., tests, __init__)
   - Coverage reporting formats (terminal, HTML)
   - Integration with pre-commit hooks

3. **ruff auto-fix capabilities**
   - Which rules support automatic fixing (simple issues)
   - Which rules require manual intervention (complex issues)
   - Configuration for hybrid auto-fix/manual approach
   - Format vs lint separation

4. **Hook bypass mechanisms**
   - Standard git --no-verify flag behavior
   - When bypass is appropriate
   - Warning/notification patterns

5. **Test execution optimization**
   - Running tests in pre-commit (all vs subset)
   - Handling long-running tests
   - Test discovery and selection strategies
   - Dealing with flaky tests

**Output**: research.md with decisions on tool configuration, hook composition, and testing strategy

## Phase 1: Design & Contracts

_Prerequisites: research.md complete_

### 1. Data Model (data-model.md)

**Configuration Entities**:

- **PreCommitConfig**: Defines hooks, their execution order, file patterns, and pass/fail criteria
  - Fields: repos (list), default_language_version, fail_fast
  - Relationships: Contains multiple Hook entries

- **Hook**: Individual quality check (linting, formatting, testing)
  - Fields: id, name, entry, language, types, stages, args
  - Validation: Must specify files to check, must have clear pass/fail criteria

- **LintRule**: Ruff linting rule configuration
  - Fields: rule_code, enabled, auto_fix_capable, severity
  - Categories: Simple (auto-fixable) vs Complex (manual fix required)

- **CoverageConfig**: Test coverage requirements
  - Fields: min_coverage, exclude_patterns, fail_under
  - Validation: min_coverage >= 70%

### 2. API Contracts (contracts/)

Since this is infrastructure/tooling, "API contracts" are CLI interface contracts:

- **pre-commit CLI contract**: Standard pre-commit commands (install, run, validate-config)
- **ruff CLI contract**: lint, format, check commands with expected exit codes
- **pytest CLI contract**: Test execution with --cov flags, exit code interpretation

Contract tests will verify:
- Configuration files are valid (yaml/toml parsing)
- Tools installed and callable
- Expected behavior on pass/fail scenarios

### 3. Contract Tests

Generate failing contract tests:
- `tests/contract/test_precommit_config.py`: Validates .pre-commit-config.yaml structure
- `tests/contract/test_coverage_enforcement.py`: Validates coverage threshold enforcement
- `tests/contract/test_ruff_autofix.py`: Validates ruff auto-fix behavior for simple vs complex issues
- `tests/contract/test_hook_bypass.py`: Validates --no-verify bypass mechanism

### 4. Integration Test Scenarios

From acceptance scenarios:
- Developer commits code with simple violations → auto-fixed
- Developer commits code with complex violations → blocked
- Developer commits code with failing tests → blocked
- Developer commits code with <70% coverage → blocked
- Developer bypasses hooks → warning shown

### 5. Update CLAUDE.md

Run update script to add new commands and configuration:
```bash
.specify/scripts/bash/update-agent-context.sh claude
```

**Output**: data-model.md, contracts/*.yaml, failing contract tests, quickstart.md, updated CLAUDE.md

## Phase 2: Task Planning Approach

_This section describes what the /tasks command will do - DO NOT execute during /plan_

**Task Generation Strategy**:

1. **Configuration Tasks**:
   - Create .pre-commit-config.yaml with hook definitions
   - Update pyproject.toml with pytest-cov configuration
   - Configure ruff rules for auto-fix vs manual

2. **Contract Test Tasks** (TDD - tests first):
   - Write contract test for valid pre-commit config [P]
   - Write contract test for coverage enforcement [P]
   - Write contract test for ruff auto-fix behavior [P]
   - Write contract test for hook bypass [P]

3. **Implementation Tasks**:
   - Install pre-commit hooks in local repo
   - Configure linting hook (ruff check + ruff format)
   - Configure testing hook (pytest with coverage)
   - Configure hook execution order and dependencies

4. **Integration Test Tasks**:
   - Test pre-commit with clean code (should pass)
   - Test pre-commit with simple violations (should auto-fix)
   - Test pre-commit with complex violations (should block)
   - Test pre-commit with failing tests (should block)
   - Test pre-commit with low coverage (should block)
   - Test bypass mechanism (should warn but allow)

5. **Documentation Tasks**:
   - Update README with pre-commit setup instructions
   - Document bypass scenarios in CLAUDE.md
   - Create quickstart guide for new developers

**Ordering Strategy**:

- Configuration first (required for all other tasks)
- Contract tests before implementation (TDD)
- Implementation to make tests pass
- Integration tests last (validate end-to-end behavior)
- Mark independent tasks with [P] for parallel execution

**Estimated Output**: 18-22 numbered, ordered tasks in tasks.md

**IMPORTANT**: This phase is executed by the /tasks command, NOT by /plan

## Phase 3+: Future Implementation

_These phases are beyond the scope of the /plan command_

**Phase 3**: Task execution (/tasks command creates tasks.md)
**Phase 4**: Implementation (execute tasks.md following constitutional principles)
**Phase 5**: Validation (run tests, execute quickstart.md, verify pre-commit hooks work)

## Complexity Tracking

_No constitutional violations - all checks passed_

| Violation | Why Needed | Simpler Alternative Rejected Because |
| --------- | ---------- | ------------------------------------ |
| None      | N/A        | N/A                                  |

## Progress Tracking

_This checklist is updated during execution flow_

**Phase Status**:

- [x] Phase 0: Research complete (/plan command)
- [x] Phase 1: Design complete (/plan command)
- [x] Phase 2: Task planning complete (/plan command - describe approach only)
- [x] Phase 3: Tasks generated (/tasks command)
- [ ] Phase 4: Implementation complete
- [ ] Phase 5: Validation passed

**Gate Status**:

- [x] Initial Constitution Check: PASS
- [ ] Post-Design Constitution Check: PASS
- [ ] All NEEDS CLARIFICATION resolved
- [x] Complexity deviations documented (none)

---

_Based on Constitution v1.0.0 - See `/memory/constitution.md`_
