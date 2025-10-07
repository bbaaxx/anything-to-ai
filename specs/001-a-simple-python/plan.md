# Implementation Plan: PDF Text Extraction Module

**Branch**: `001-a-simple-python` | **Date**: 2025-09-28 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-a-simple-python/spec.md`

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

A Python module for extracting text content from PDF files with streaming support for large files, progress tracking, and both programmatic API and command-line interfaces. The module handles files of varying sizes efficiently, with special handling for large files (>20 pages) via streaming and provides clear error handling for edge cases.

## Technical Context

**Language/Version**: Python 3.8+ (for compatibility with standard library features)
**Primary Dependencies**: PyPDF2 or pdfplumber for PDF parsing (minimal external dependencies per constitution)
**Storage**: File system input only (PDF files)
**Testing**: pytest for unit and integration testing
**Target Platform**: Cross-platform (Linux, macOS, Windows)
**Project Type**: single - Python module with CLI interface
**Performance Goals**: Stream processing for files >20 pages, memory-efficient page-by-page processing
**Constraints**: <250 lines per file (constitution), minimal dependencies, handle files up to memory limits via streaming
**Scale/Scope**: Internal API consumption, CLI testing interface, handle various PDF sizes and formats

## Constitution Check

_GATE: Must pass before Phase 0 research. Re-check after Phase 1 design._

**Composition-First Check**:

- [x] All components are independently functional and testable (PDF reader, progress tracker, CLI interface as separate modules)
- [x] No monolithic structures proposed (modular design with clear separation)
- [x] Complexity emerges through composition, not component complexity (simple modules combined for complete functionality)

**250-Line Rule Check**:

- [x] No single file planned exceeds 250 lines (each module <250 lines: reader, progress, CLI, exceptions)
- [x] Large modules identified for modular breakdown (PDF processing split into core reader + streaming handler)
- [x] Clear refactoring strategy for size violations (split by responsibility: reading, streaming, progress, CLI)

**Minimal Dependencies Check**:

- [x] All dependencies justified with clear rationale (PyPDF2/pdfplumber for PDF parsing - no standard library alternative)
- [x] Standard library solutions preferred over external packages (using argparse, json, sys from stdlib)
- [x] Dependency audit plan included (single PDF parsing dependency evaluation)

**Experimental Mindset Check**:

- [x] Learning objectives documented (explore PDF processing patterns, streaming architectures, CLI design)
- [x] Quick iteration approach planned (start with basic reader, add streaming, then CLI)
- [x] Breaking changes acceptable for architectural improvements (experimental project allows refactoring)

**Modular Architecture Check**:

- [x] Single responsibility per module (reader, progress tracker, CLI, error handling separate)
- [x] Clear interface definitions between modules (defined APIs for each component)
- [x] Modules designed for replaceability (progress tracking can be swapped, PDF library can be changed)

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
pdf_extractor/
├── __init__.py          # Module interface
├── __main__.py          # CLI entry point (python -m pdf_extractor)
├── reader.py            # Core PDF text extraction
├── streaming.py         # Streaming/pagination for large files
├── progress.py          # Progress tracking functionality
├── cli.py               # Command line interface logic
└── exceptions.py        # Custom exception classes

tests/
├── contract/
│   └── test_api.py      # Contract tests for module interface
├── integration/
│   ├── test_cli.py      # CLI integration tests
│   └── test_workflows.py # End-to-end processing tests
└── unit/
    ├── test_reader.py   # PDF reading unit tests
    ├── test_streaming.py # Streaming logic tests
    ├── test_progress.py # Progress tracking tests
    └── test_exceptions.py # Exception handling tests
```

**Structure Decision**: Single Python module structure chosen. The `pdf_extractor/` directory contains all core functionality split into focused modules (each <250 lines per constitution). CLI interface accessible via `python -m pdf_extractor`. Tests organized by type (contract, integration, unit) following TDD approach.

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
- Each contract API function → contract test task [P]
- Each entity (PDFDocument, TextContent, etc.) → model creation task [P]
- Each CLI command → integration test task
- Each exception type → error handling test task [P]
- Implementation tasks ordered by dependency
- Constitution compliance verification tasks

**Ordering Strategy**:

- TDD order: Contract tests → Entity tests → Implementation → Integration tests
- Dependency order: Exceptions → Models → Core logic → Streaming → CLI
- Mark [P] for parallel execution (independent modules per constitution)
- Group by constitutional file size limits (<250 lines each)

**Estimated Output**: 18-22 numbered, ordered tasks in tasks.md focusing on modular, testable components

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
- [x] Post-Design Constitution Check: PASS (all modules <250 lines, composition-first design, minimal dependencies)
- [x] All NEEDS CLARIFICATION resolved
- [x] Complexity deviations documented (none required)

---

_Based on Constitution v1.0.0 - See `/memory/constitution.md`_
