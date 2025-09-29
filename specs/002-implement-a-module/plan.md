# Implementation Plan: Image VLM Text Description Module

**Branch**: `002-implement-a-module` | **Date**: 2025-09-28 | **Spec**: spec.md
**Input**: Feature specification from `/specs/002-implement-a-module/spec.md`

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

Implement a modular image processing system that takes image files and generates descriptive text using Vision Language Models (VLM) via the mlx-vlm library. The module must follow the same quality, modularity, and architectural patterns as the existing PDF extraction feature, including structured results, progress tracking, error handling, and batch processing capabilities.

## Technical Context

**Language/Version**: Python 3.13 (per project requirements)
**Primary Dependencies**: mlx-vlm (VLM processing), PIL/Pillow (image handling)
**Storage**: File system (image files), no persistent storage required
**Testing**: pytest (following existing project pattern)
**Target Platform**: macOS (MLX framework requirement)
**Project Type**: single - Python module following existing pdf_extractor pattern
**Performance Goals**: Process images efficiently with progress tracking for large files
**Constraints**: <250 lines per file (constitution), minimal dependencies, composition-first architecture
**Scale/Scope**: Single/batch image processing, modular design for podcast content pipeline integration

## Constitution Check

_GATE: Must pass before Phase 0 research. Re-check after Phase 1 design._

**Composition-First Check**:

- [x] All components are independently functional and testable
- [x] No monolithic structures proposed
- [x] Complexity emerges through composition, not component complexity

**250-Line Rule Check**:

- [x] No single file planned exceeds 250 lines (including comments/whitespace)
- [x] Large modules identified for modular breakdown
- [x] Clear refactoring strategy for size violations

**Minimal Dependencies Check**:

- [x] All dependencies justified with clear rationale (mlx-vlm for VLM, PIL for image handling)
- [x] Standard library solutions preferred over external packages
- [x] Dependency audit plan included

**Experimental Mindset Check**:

- [x] Learning objectives documented (VLM integration patterns, MLX framework usage)
- [x] Quick iteration approach planned
- [x] Breaking changes acceptable for architectural improvements

**Modular Architecture Check**:

- [x] Single responsibility per module
- [x] Clear interface definitions between modules
- [x] Modules designed for replaceability

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

<!--
  ACTION REQUIRED: Replace the placeholder tree below with the concrete layout
  for this feature. Delete unused options and expand the chosen structure with
  real paths (e.g., apps/admin, packages/something). The delivered plan must
  not include Option labels.
-->

```
image_processor/           # New module following pdf_extractor pattern
├── __init__.py           # Public API exports
├── models.py             # Data models (ImageDocument, DescriptionResult, etc.)
├── processor.py          # Core VLM processing functionality
├── streaming.py          # Streaming/batch processing
├── exceptions.py         # Custom exception types
├── progress.py          # Progress tracking utilities
└── cli.py               # Command line interface

tests/
├── contract/            # API contract tests
│   └── test_api.py
├── integration/         # End-to-end workflow tests
│   └── test_workflows.py
└── unit/               # Individual component tests
    ├── test_models.py
    ├── test_processor.py
    ├── test_streaming.py
    ├── test_exceptions.py
    └── test_progress.py
```

**Structure Decision**: Single project structure following existing pdf_extractor module pattern. New image_processor module will be added alongside pdf_extractor with identical architectural patterns for consistency and maintainability.

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

- Load `.specify/templates/tasks-template.md` as base
- Generate tasks from Phase 1 design docs (contracts, data model, quickstart)
- Each entity in data-model.md → model creation task [P]
- Each contract function → contract test task [P]
- Each CLI command → CLI test task
- Implementation tasks following TDD pattern to make tests pass
- Integration tasks based on user scenarios from spec

**Ordering Strategy**:

- TDD order: Contract tests → Models → Core processors → Streaming → CLI → Integration tests
- Dependency order:
  1. Models and exceptions (independent) [P]
  2. Core processor (depends on models)
  3. Streaming processor (depends on core)
  4. Progress tracking (depends on streaming)
  5. CLI interface (depends on all core components)
  6. Integration tests (validates complete workflows)
- Mark [P] for parallel execution (independent files under 250 lines each)

**Specific Task Categories**:

- **Models**: ImageDocument, DescriptionResult, ProcessingResult, ProcessingConfig (4 tasks) [P]
- **Exceptions**: Custom exception hierarchy with proper inheritance (1 task)
- **Core Processing**: MLX-VLM integration, image validation, single image processing (3 tasks)
- **Batch Processing**: Streaming interface, progress tracking, memory management (3 tasks)
- **CLI Interface**: Argument parsing, output formatting, file path expansion (3 tasks)
- **Testing**: Contract tests for all public APIs (6 tasks)
- **Integration**: End-to-end workflow tests matching user scenarios (4 tasks)

**Constitution Compliance Strategy**:

- Each file limited to 250 lines maximum
- Modular components with single responsibilities
- Clear interfaces between all modules
- Minimal external dependencies (mlx-vlm, PIL only)

**Estimated Output**: 24-26 numbered, ordered tasks in tasks.md

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
- [x] Complexity deviations documented

---

_Based on Constitution v1.0.0 - See `/memory/constitution.md`_
