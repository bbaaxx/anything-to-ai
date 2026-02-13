# Tasks: MarkItDown Bridge Contract Stabilization

**Input**: Design documents from `/specs/016-markitdown-bridge/`
**Prerequisites**: `plan.md` (required), `spec.md` (required), `research.md`, `data-model.md`, `contracts/document-converter.openapi.yaml`, `quickstart.md`

**Tests**: Tests are REQUIRED. Include failing-first test tasks for each user story and affected suites.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: User story label (`[US1]`, `[US2]`, `[US3]`)
- Include exact file paths in every task description.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Prepare required test and traceability scaffolds used by all stories.

- [ ] T001 Create unit error test scaffold in `tests/unit/test_document_converter_errors.py`
- [ ] T002 Create integration routing test scaffold in `tests/integration/test_document_converter_routing.py`
- [ ] T003 Create contract API test scaffold in `tests/contract/test_document_converter_contracts.py`
- [ ] T004 Create contract CLI test scaffold in `tests/contract/test_document_converter_cli_contracts.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Add shared helpers and baseline contract traceability required before user story work.

**CRITICAL**: Complete this phase before implementing any user story.

- [ ] T005 [P] Add shared fake backend result builders in `tests/helpers/document_converter_fakes.py`
- [ ] T006 [P] Add shared source matrix fixtures in `tests/helpers/document_converter_sources.py`
- [ ] T007 Wire helper exports for reuse in `tests/helpers/__init__.py`
- [ ] T008 Establish baseline converter behavior snapshot tests in `tests/unit/test_document_converter.py`
- [ ] T009 Capture pre-implementation test-gap matrix for FR-026 in `specs/016-markitdown-bridge/spec.md`
- [ ] T010 Align quickstart scope notes with in-scope CLI contract behavior in `specs/016-markitdown-bridge/quickstart.md`

**Checkpoint**: Foundation ready - story phases can begin.

---

## Phase 3: User Story 1 - Deterministic Routing Contract (Priority: P1) 🎯 MVP

**Goal**: Guarantee deterministic routing matrix and precedence handling for local and URL inputs.

**Independent Test**: Run routing-focused unit and integration tests verifying matrix mappings, precedence order, unknown-extension fallback, non-HTTP scheme handling, and no network-bound behavior for local sources.

### Tests for User Story 1 (REQUIRED) ⚠️

- [ ] T011 [US1] Add failing unit tests for URL precedence, unknown-extension fallback, and whitespace rejection in `tests/unit/test_document_converter.py`
- [ ] T012 [P] [US1] Add failing integration routing-matrix tests with lightweight doubles in `tests/integration/test_document_converter_routing.py`
- [ ] T013 [US1] Add failing unit test for non-HTTP/HTTPS scheme handling (for example `ftp://`) in `tests/unit/test_document_converter.py`
- [ ] T014 [US1] Add failing unit test asserting local-path routing/dispatch does not invoke URL or network-dependent handlers in `tests/unit/test_document_converter.py`
- [ ] T015 [P] [US1] Add failing integration assertion that local routed fixtures do not trigger network-bound code paths in `tests/integration/test_document_converter_routing.py`

### Implementation for User Story 1

- [ ] T016 [US1] Implement deterministic precedence and validation updates in `anyfile_to_ai/document_converter/routing.py`
- [ ] T017 [US1] Align converter route dispatch with updated routing expectations in `anyfile_to_ai/document_converter/converter.py`
- [ ] T018 [US1] Align route/result model typing with routing contract in `anyfile_to_ai/document_converter/models.py`
- [ ] T019 [US1] Validate US1 commands and expected outputs in `specs/016-markitdown-bridge/quickstart.md`

**Checkpoint**: User Story 1 is independently functional and testable.

---

## Phase 4: User Story 2 - Stable API and Error Semantics (Priority: P2)

**Goal**: Enforce typed error boundaries and API/CLI parity for conversion behavior.

**Independent Test**: Run unit and contract tests for wrapping/no-rewrap behavior, dependency guidance strings, lazy imports, and CLI stdout/stderr/exit-code parity.

### Tests for User Story 2 (REQUIRED) ⚠️

- [ ] T020 [US2] Add failing unit tests for exception wrapping and no-rewrap behavior in `tests/unit/test_document_converter.py`
- [ ] T021 [P] [US2] Add failing unit tests for dependency guidance fragments (`install`, package name, `markitdown[all]`) and lazy imports in `tests/unit/test_document_converter_errors.py`
- [ ] T022 [P] [US2] Add failing contract tests for `/convert` error and response semantics in `tests/contract/test_document_converter_contracts.py`
- [ ] T023 [P] [US2] Add failing CLI parity contract tests in `tests/contract/test_document_converter_cli_contracts.py`

### Implementation for User Story 2

- [ ] T024 [US2] Implement error wrapping boundaries and typed pass-through logic in `anyfile_to_ai/document_converter/converter.py`
- [ ] T025 [US2] Align typed exception classes and guidance text semantics in `anyfile_to_ai/document_converter/exceptions.py`
- [ ] T026 [US2] Ensure public API exports reflect contracted surface in `anyfile_to_ai/document_converter/__init__.py`
- [ ] T027 [US2] Add minimal CLI entry point for document conversion in `anyfile_to_ai/document_converter/__main__.py`
- [ ] T028 [US2] Register document converter CLI script entry in `pyproject.toml`
- [ ] T029 [US2] Validate US2 commands and expected outputs in `specs/016-markitdown-bridge/quickstart.md`

**Checkpoint**: User Stories 1 and 2 both pass independently.

---

## Phase 5: User Story 3 - Explicitly Deferred Formatter Unification (Priority: P3)

**Goal**: Lock output-compatibility guardrails while preserving formatter deferral.

**Independent Test**: Run contract and integration tests validating stable required fields and allowed backend-specific variance for metadata and raw output.

### Tests for User Story 3 (REQUIRED) ⚠️

- [ ] T030 [P] [US3] Add failing contract tests for stable required fields and best-effort variance fields in `tests/contract/test_document_converter_contracts.py`
- [ ] T031 [P] [US3] Add failing integration tests for MarkItDown best-effort metadata behavior in `tests/integration/test_document_converter_routing.py`

### Implementation for User Story 3

- [ ] T032 [US3] Implement output guardrail handling for metadata and `raw_result` variance in `anyfile_to_ai/document_converter/converter.py`
- [ ] T033 [US3] Update deferred follow-up statuses for formatter unification in `DEFERRED_ACTIONS.md`
- [ ] T034 [US3] Validate US3 commands and expected outputs in `specs/016-markitdown-bridge/quickstart.md`

**Checkpoint**: All user stories are independently functional and testable.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final quality gates, release documentation, and traceability closure.

- [ ] T035 [P] Run focused lint/format/test command set documented in `specs/016-markitdown-bridge/quickstart.md`
- [ ] T036 [P] Run full-suite validation command documented in `specs/016-markitdown-bridge/quickstart.md`
- [ ] T037 Update release notes for bridge routing/error/output contract changes in `docs/release-notes.md`
- [ ] T038 Capture and verify targeted converter unit runtime budget evidence in `specs/016-markitdown-bridge/quickstart.md`
- [ ] T039 Verify and update post-implementation test-gap traceability matrix in `specs/016-markitdown-bridge/spec.md`
- [ ] T040 Update CLI usage examples and behavior notes for document converter in `README.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- Setup (Phase 1): no dependencies
- Foundational (Phase 2): depends on Setup completion; blocks all stories
- User Stories (Phases 3-5): depend on Foundational completion
- Polish (Phase 6): depends on completion of desired user stories

### User Story Dependencies

- **US1 (P1)**: Starts after Phase 2; no dependency on US2/US3
- **US2 (P2)**: Starts after Phase 2; depends on US1 route-context behavior for parity assertions
- **US3 (P3)**: Starts after Phase 2; depends on US1 and US2 for final guardrail compatibility checks

### Dependency Graph

```text
Phase 1 -> Phase 2 -> US1 -> US2 -> US3 -> Phase 6
```

### Within Each User Story

- Add failing tests first
- Implement minimal code to satisfy tests
- Re-run story-specific tests before moving to next phase

---

## Parallel Execution Examples

### User Story 1

```bash
Task T012: tests/integration/test_document_converter_routing.py
Task T015: tests/integration/test_document_converter_routing.py
```

### User Story 2

```bash
Task T021: tests/unit/test_document_converter_errors.py
Task T023: tests/contract/test_document_converter_cli_contracts.py
```

### User Story 3

```bash
Task T030: tests/contract/test_document_converter_contracts.py
Task T031: tests/integration/test_document_converter_routing.py
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 and Phase 2
2. Complete Phase 3 (US1)
3. Validate US1 independently as MVP

### Incremental Delivery

1. Deliver US1 deterministic routing
2. Deliver US2 error and CLI/API parity
3. Deliver US3 output compatibility guardrails and deferral alignment
4. Complete polish and release documentation tasks

### Parallel Team Strategy

1. Contributor A: converter code in `anyfile_to_ai/document_converter/`
2. Contributor B: unit and integration tests in `tests/unit` and `tests/integration`
3. Contributor C: contract and docs artifacts in `tests/contract`, `specs/016-markitdown-bridge/`, and `docs/release-notes.md`

---

## Notes

- `[P]` tasks indicate parallel-safe work across different files with no dependency on incomplete tasks
- Story labels maintain traceability for independently testable increments
- Formatter unification remains deferred and tracked in `DEFERRED_ACTIONS.md`
