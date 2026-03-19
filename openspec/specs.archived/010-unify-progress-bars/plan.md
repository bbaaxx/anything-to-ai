# Implementation Plan: Unified Progress Tracking System

**Branch**: `010-unify-progress-bars` | **Date**: 2025-10-02 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/010-unify-progress-bars/spec.md`

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
6. Execute Phase 1 → contracts, data-model.md, quickstart.md, agent-specific template file (e.g., `CLAUDE.md` for Claude Code, `.github/copilot-instructions.md` for GitHub Copilot, `GEMINI.md` for Gemini CLI, `QWEN.md` for Qwen Code or `AGENTS.md` for opencode).
7. Re-evaluate Constitution Check section
   → If new violations: Refactor design, return to Phase 1
   → Update Progress Tracking: Post-Design Constitution Check
8. Plan Phase 2 → Describe task generation approach (DO NOT create tasks.md)
9. STOP - Ready for /tasks command
```

**IMPORTANT**: The /plan command STOPS at step 7. Phases 2-4 are executed by other commands:

- Phase 2: /tasks command creates tasks.md
- Phase 3-4: Implementation execution (manual or via tools)

## Summary

This feature unifies progress tracking across all processing modules (pdf_extractor, image_processor, audio_processor, text_summarizer) with a composable async-first design. The implementation will create a shared progress reporting mechanism that serves both CLI (via alive-progress library) and programmatic consumers, eliminating code duplication while supporting hierarchical progress, dynamic totals, and indeterminate states.

## Technical Context

**Language/Version**: Python 3.13
**Primary Dependencies**: alive-progress (CLI rendering), asyncio (async support), dataclasses (models)
**Storage**: N/A (in-memory state only)
**Testing**: pytest with async support (pytest-asyncio)
**Target Platform**: macOS/Linux CLI, importable Python modules
**Project Type**: single (modular Python packages)
**Performance Goals**: Minimal overhead (<1% processing time), throttled updates (max 10 Hz), async/await native support
**Constraints**: Must not block processing, exception-safe callbacks, stderr output for CLI (preserve stdout for piping)
**Scale/Scope**: 4 existing modules to unify, support for nested/hierarchical progress (2-3 levels), handle 1-100k items per operation

**Current State Analysis**:
- pdf_extractor: Uses ProgressInfo dataclass with detailed fields (pages, percentage, estimated time)
- image_processor & audio_processor: Use ProgressTracker class with simple callback(current, total) signature
- text_summarizer & llm_client: No built-in progress tracking
- Inconsistent callback signatures and state models across modules

## Constitution Check

_GATE: Must pass before Phase 0 research. Re-check after Phase 1 design._

**Composition-First Check**:

- [x] All components are independently functional and testable
  - Core: ProgressState (data), ProgressEmitter (state management), ProgressConsumer (abstract interface)
  - Consumers: CLIProgressConsumer, CallbackProgressConsumer, LoggingProgressConsumer
  - Each component has single purpose and can be tested in isolation
- [x] No monolithic structures proposed
  - No single "ProgressManager" god object - functionality distributed across focused components
- [x] Complexity emerges through composition, not component complexity
  - Hierarchical progress = ProgressEmitter containing child ProgressEmitters
  - CLI rendering = CLIProgressConsumer wrapping alive-progress library

**250-Line Rule Check**:

- [x] No single file planned exceeds 250 lines (including comments/whitespace)
  - models.py: ~80 lines (ProgressState, ProgressUpdate dataclasses)
  - emitter.py: ~120 lines (ProgressEmitter with async/sync support)
  - consumers.py: ~180 lines (3 consumer implementations @ ~60 lines each)
  - cli_renderer.py: ~100 lines (alive-progress integration)
- [x] Large modules identified for modular breakdown
  - Existing progress.py files in each module (~30-60 lines) will be replaced with imports from shared module
- [x] Clear refactoring strategy for size violations
  - If consumers.py approaches limit, split into separate files per consumer type

**Minimal Dependencies Check**:

- [x] All dependencies justified with clear rationale
  - alive-progress: Required for rich CLI progress bars (spec mandates this library)
  - asyncio: Standard library, needed for async/await support
  - dataclasses: Standard library, used for type-safe state models
  - typing: Standard library, used for protocol definitions
- [x] Standard library solutions preferred over external packages
  - Only external dep is alive-progress (user-specified requirement)
- [x] Dependency audit plan included
  - alive-progress is actively maintained, well-documented, pure Python

**Experimental Mindset Check**:

- [x] Learning objectives documented
  - Explore async generators for progress streaming
  - Test composability patterns for hierarchical progress
  - Validate DRY approach with real-world module integration
- [x] Quick iteration approach planned
  - Phase 0: Research async patterns and alive-progress API
  - Phase 1: Build core abstractions, defer full module integration
  - Phase 2+: Iterative refactoring of existing modules
- [x] Breaking changes acceptable for architectural improvements
  - Will replace existing ProgressTracker/ProgressInfo classes
  - Module APIs may change to accept new progress callbacks

**Modular Architecture Check**:

- [x] Single responsibility per module
  - models: Data structures only
  - emitter: State management and update emission
  - consumers: Display/handling logic (no state management)
  - cli_renderer: alive-progress integration (no progress logic)
- [x] Clear interface definitions between modules
  - ProgressConsumer protocol defines consumer contract
  - ProgressEmitter provides producer interface
  - AsyncIterator[ProgressUpdate] for streaming updates
- [x] Modules designed for replaceability
  - Can swap CLIProgressConsumer for TUIProgressConsumer without changing emitter
  - Can add new consumers (WebSocketProgressConsumer) without modifying existing code

## Project Structure

### Documentation (this feature)

```
specs/[###-feature]/
├── plan.md              # This file (/plan command output)
├── research.md          # Phase 0 output (/plan command)
├── data-model.md        # Phase 1 output (/plan command)
├── quickstart.md        # Phase 1 output (/plan command)
├── contracts/           # Phase 1 output (/plan command)
└── tasks.md             # Phase 2 output (/tasks command - NOT created by /plan)
```

### Source Code (repository root)

```
progress_tracker/                  # New shared module
├── __init__.py                    # Public API exports
├── models.py                      # ProgressState, ProgressUpdate dataclasses
├── emitter.py                     # ProgressEmitter (core state management)
├── consumers.py                   # Consumer implementations
├── cli_renderer.py                # alive-progress CLI integration
└── README.md                      # Module documentation

pdf_extractor/
├── progress.py                    # DEPRECATED → import from progress_tracker
└── ...

image_processor/
├── progress.py                    # DEPRECATED → import from progress_tracker
└── ...

audio_processor/
├── progress.py                    # DEPRECATED → import from progress_tracker
└── ...

text_summarizer/
└── ...                            # Add progress support

llm_client/
└── ...                            # Add progress support

tests/
├── contract/
│   └── test_progress_protocol.py # ProgressConsumer protocol tests
├── integration/
│   ├── test_cli_progress.py      # End-to-end CLI rendering
│   ├── test_hierarchical.py      # Nested progress scenarios
│   └── test_module_integration.py # Existing modules with new progress
└── unit/
    ├── test_models.py             # ProgressState/ProgressUpdate tests
    ├── test_emitter.py            # ProgressEmitter logic tests
    └── test_consumers.py          # Consumer implementation tests
```

**Structure Decision**: Single project (modular Python packages). New `progress_tracker/` module contains all shared progress functionality. Existing modules will refactor their progress.py files to import from the shared module, maintaining backward compatibility where feasible.

## Phase 0: Outline & Research

1. **Extract unknowns from Technical Context** above:

   - For each NEEDS CLARIFICATION → research task
   - For each dependency → best practices task
   - For each integration → patterns task

2. **Generate and dispatch research agents**:

   ```
   For each unknown in Technical Context:
     Task: "Research {unknown} for {feature context}"
   For each technology choice:
     Task: "Find best practices for {tech} in {domain}"
   ```

3. **Consolidate findings** in `research.md` using format:
   - Decision: [what was chosen]
   - Rationale: [why chosen]
   - Alternatives considered: [what else evaluated]

**Output**: research.md with all NEEDS CLARIFICATION resolved

## Phase 1: Design & Contracts

_Prerequisites: research.md complete_

1. **Extract entities from feature spec** → `data-model.md`:

   - Entity name, fields, relationships
   - Validation rules from requirements
   - State transitions if applicable

2. **Generate API contracts** from functional requirements:

   - For each user action → endpoint
   - Use standard REST/GraphQL patterns
   - Output OpenAPI/GraphQL schema to `/contracts/`

3. **Generate contract tests** from contracts:

   - One test file per endpoint
   - Assert request/response schemas
   - Tests must fail (no implementation yet)

4. **Extract test scenarios** from user stories:

   - Each story → integration test scenario
   - Quickstart test = story validation steps

5. **Update agent file incrementally** (O(1) operation):
   - Run `.specify/scripts/bash/update-agent-context.sh claude`
     **IMPORTANT**: Execute it exactly as specified above. Do not add or remove any arguments.
   - If exists: Add only NEW tech from current plan
   - Preserve manual additions between markers
   - Update recent changes (keep last 3)
   - Keep under 150 lines for token efficiency
   - Output to repository root

**Output**: data-model.md, /contracts/\*, failing tests, quickstart.md, agent-specific file

## Phase 2: Task Planning Approach

_This section describes what the /tasks command will do - DO NOT execute during /plan_

**Task Generation Strategy**:

The /tasks command will generate a comprehensive task list following TDD and constitutional principles:

1. **Contract Test Tasks** (from contracts/test_progress_protocol.py):
   - Task for each protocol validation test
   - Task for each dataclass contract test
   - Task for each API method contract test
   - All contract tests MUST fail initially (no implementation yet)

2. **Core Model Tasks** (from data-model.md):
   - Task: Implement ProgressState dataclass with validation
   - Task: Implement UpdateType enum
   - Task: Implement ProgressUpdate dataclass
   - Task: Verify all contract tests for models pass

3. **Consumer Protocol Tasks** (from data-model.md + contracts/api.md):
   - Task: Define ProgressConsumer Protocol
   - Task: Verify protocol contract tests pass

4. **ProgressEmitter Implementation** (from data-model.md + contracts/api.md):
   - Task: Implement basic ProgressEmitter (update, set_current, properties)
   - Task: Implement consumer management (add/remove consumers)
   - Task: Implement throttling mechanism
   - Task: Implement complete() with validation
   - Task: Implement update_total() for dynamic totals
   - Task: Implement exception-safe consumer notifications
   - Task: Verify emitter contract tests pass

5. **Consumer Implementations** (from contracts/api.md):
   - Task: Implement CallbackProgressConsumer [P]
   - Task: Implement LoggingProgressConsumer [P]
   - Task: Implement CLIProgressConsumer (alive-progress integration)
   - Task: Verify consumer contract tests pass

6. **Hierarchical Progress** (from data-model.md):
   - Task: Implement create_child() method
   - Task: Implement parent-child update propagation
   - Task: Implement weighted average calculation
   - Task: Integration test for hierarchical progress

7. **Async Streaming** (from contracts/api.md):
   - Task: Implement async stream() generator
   - Task: Integration test for async iteration

8. **Module Integration** (from quickstart.md):
   - Task: Refactor pdf_extractor to use ProgressEmitter [P]
   - Task: Refactor image_processor to use ProgressEmitter [P]
   - Task: Refactor audio_processor to use ProgressEmitter [P]
   - Task: Add progress support to text_summarizer [P]
   - Task: Integration test for each module

9. **CLI Integration** (from quickstart.md):
   - Task: Update CLI entry points to use CLIProgressConsumer
   - Task: Add --quiet flag support
   - Task: Integration test for CLI progress display

10. **Documentation & Cleanup**:
    - Task: Add deprecation warnings to old progress.py files
    - Task: Update module READMEs with progress examples
    - Task: Verify all quickstart examples work

**Ordering Strategy**:

- **Phase 1**: Contract tests (all failing initially)
- **Phase 2**: Core models (ProgressState, UpdateType, ProgressUpdate)
- **Phase 3**: Consumer protocol + ProgressEmitter core
- **Phase 4**: Consumer implementations (parallelizable)
- **Phase 5**: Advanced features (hierarchical, async streaming)
- **Phase 6**: Module integration (parallelizable)
- **Phase 7**: CLI integration
- **Phase 8**: Documentation & cleanup

**Parallelization Markers**:
- [P] indicates tasks that can run in parallel (independent files/modules)
- Consumer implementations are fully independent
- Module integrations are independent after core is complete

**Constitutional Compliance**:
- All files constrained to <250 lines (enforced by ruff)
- Each component is independently testable
- Composition-first: Consumers compose with emitters, children compose with parents
- Minimal dependencies: Only alive-progress external dep

**Estimated Output**: 35-40 numbered, ordered tasks in tasks.md

**Validation Checkpoints**:
- After Phase 2: All model contract tests pass
- After Phase 4: All consumer contract tests pass
- After Phase 6: All module integration tests pass
- After Phase 7: All CLI integration tests pass

**IMPORTANT**: This phase is executed by the /tasks command, NOT by /plan

## Phase 3+: Future Implementation

_These phases are beyond the scope of the /plan command_

**Phase 3**: Task execution (/tasks command creates tasks.md)
**Phase 4**: Implementation (execute tasks.md following constitutional principles)
**Phase 5**: Validation (run tests, execute quickstart.md, performance validation)

## Complexity Tracking

_Fill ONLY if Constitution Check has violations that must be justified_

| Violation                  | Why Needed         | Simpler Alternative Rejected Because |
| -------------------------- | ------------------ | ------------------------------------ |
| [e.g., 4th project]        | [current need]     | [why 3 projects insufficient]        |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient]  |

## Progress Tracking

_This checklist is updated during execution flow_

**Phase Status**:

- [x] Phase 0: Research complete (/plan command)
- [x] Phase 1: Design complete (/plan command)
- [x] Phase 2: Task planning complete (/plan command - describe approach only)
- [ ] Phase 3: Tasks generated (/tasks command)
- [ ] Phase 4: Implementation complete
- [ ] Phase 5: Validation passed

**Gate Status**:

- [x] Initial Constitution Check: PASS
- [x] Post-Design Constitution Check: PASS
- [x] All NEEDS CLARIFICATION resolved
- [x] Complexity deviations documented (None - full constitutional compliance)

**Artifacts Generated**:

- [x] research.md: Technical decisions and research findings
- [x] data-model.md: Entity definitions and relationships
- [x] contracts/api.md: Public API contract documentation
- [x] contracts/test_progress_protocol.py: Contract test stubs (134 tests)
- [x] quickstart.md: Developer integration guide
- [x] CLAUDE.md: Updated with new technologies

**Next Command**: Run `/tasks` to generate tasks.md from design artifacts

---

_Based on Constitution v1.0.0 - See `/memory/constitution.md`_
