# Implementation Plan: Enhanced PDF Extraction with Image Description

**Branch**: `005-augment-pdf-extraction` | **Date**: 2025-09-29 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/005-augment-pdf-extraction/spec.md`

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

Enhance the existing PDF extraction capability by adding optional image description processing. When enabled, the system will extract images from PDFs, analyze them using a vision model, and include AI-generated descriptions inline with the extracted text. This provides a complete textual representation of document content including visual information.

## Technical Context

**Language/Version**: Python 3.13 (per project requirements)
**Primary Dependencies**: pdfplumber (PDF parsing), mlx-vlm (VLM processing), PIL/Pillow (image handling), existing pdf_extractor and image_processor modules
**Storage**: File system (PDF and image files), no persistent storage required
**Testing**: pytest with comprehensive test structure (contract, integration, unit)
**Target Platform**: Development environment with MLX support (Apple Silicon optimized)
**Project Type**: single - CLI tool with modular architecture
**Performance Goals**: Process PDFs with images efficiently, maintain existing streaming performance
**Constraints**: 250-line file limit per constitution, minimal dependencies, modular composition-first design
**Scale/Scope**: Single-user CLI tool, handle PDFs with multiple images, maintain backward compatibility

## Constitution Check

_GATE: Must pass before Phase 0 research. Re-check after Phase 1 design._

**Composition-First Check**:

- [x] All components are independently functional and testable (leveraging existing pdf_extractor and image_processor modules)
- [x] No monolithic structures proposed (feature will compose existing modules)
- [x] Complexity emerges through composition, not component complexity (integration layer between existing modules)

**250-Line Rule Check**:

- [x] No single file planned exceeds 250 lines (existing modules already comply, new integration files will be small)
- [x] Large modules identified for modular breakdown (will create focused integration modules)
- [x] Clear refactoring strategy for size violations (split into separate concerns: configuration, extraction, integration)

**Minimal Dependencies Check**:

- [x] All dependencies justified with clear rationale (reusing existing pdfplumber and mlx-vlm dependencies)
- [x] Standard library solutions preferred over external packages (no new external dependencies required)
- [x] Dependency audit plan included (leveraging existing project dependencies)

**Experimental Mindset Check**:

- [x] Learning objectives documented (explore PDF-image integration patterns)
- [x] Quick iteration approach planned (extend existing working modules)
- [x] Breaking changes acceptable for architectural improvements (backward compatible extension)

**Modular Architecture Check**:

- [x] Single responsibility per module (separate concerns: PDF extraction, image processing, integration)
- [x] Clear interface definitions between modules (using existing module APIs)
- [x] Modules designed for replaceability (existing modules already follow this pattern)

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
├── __init__.py
├── reader.py
├── models.py
├── cli.py
├── streaming.py
├── progress.py
└── exceptions.py

image_processor/
├── __init__.py
├── processor.py
├── vlm_processor.py
├── models.py
├── cli.py
├── streaming.py
├── config.py
├── model_loader.py
└── exceptions.py

# New integration modules (this feature)
pdf_extractor/
├── image_integration.py    # NEW: PDF-image integration logic
└── enhanced_models.py      # NEW: Extended models with image support

tests/
├── contract/              # Interface contract tests
├── integration/           # Cross-module integration tests
└── unit/                  # Unit tests for individual components
```

**Structure Decision**: Single project architecture with existing modular structure. This feature extends the pdf_extractor module with image processing capabilities by composing with the existing image_processor module. New files will be minimal and focused, maintaining the 250-line constitutional limit.

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
- Each contract interface → contract test task [P]
- Enhanced models → model implementation task [P]
- Image extraction → image integration service task
- CLI enhancements → CLI extension task
- Integration scenarios → integration test tasks

**Specific Task Categories**:

1. **Contract Tests (Parallel)**:
   - `enhanced_api.py` → contract test for API interfaces
   - `cli_interface.py` → contract test for CLI arguments and behavior
   - `exceptions.py` → contract test for exception hierarchy

2. **Model Implementation (Parallel)**:
   - Enhanced extraction config model
   - Image context model
   - Enhanced page/extraction result models

3. **Core Services (Sequential)**:
   - Image extraction service (depends on models)
   - VLM circuit breaker (depends on models)
   - PDF-image integration orchestrator (depends on all above)

4. **CLI Extension (Sequential)**:
   - Argument parser extension (depends on models)
   - Output formatter updates (depends on enhanced models)
   - Progress reporter enhancements (depends on services)

5. **Integration Tests (Final)**:
   - Backward compatibility validation
   - Error scenario testing
   - Performance baseline validation
   - Quickstart scenario validation

**Ordering Strategy**:

- TDD order: Contract tests → models → services → CLI → integration
- Constitutional compliance: Each file ≤250 lines, composition-first
- Dependency order: Independent components first, then composition
- Mark [P] for parallel execution (independent files within same phase)

**Estimated Output**: 18-22 numbered, ordered tasks in tasks.md

**Constitutional Validation Tasks**:
- File length validation after each implementation task
- Composition-first validation during integration phases
- Dependency audit validation before completion

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
- [x] Complexity deviations documented (none required)

---

_Based on Constitution v1.0.0 - See `/memory/constitution.md`_
