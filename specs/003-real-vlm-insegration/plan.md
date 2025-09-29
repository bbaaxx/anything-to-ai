# Implementation Plan: Real VLM Integration

**Branch**: `003-real-vlm-insegration` | **Date**: 2025-09-28 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/003-real-vlm-insegration/spec.md`

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

Complete the implementation of a VLM model to complement the previous mock implementation. Replace placeholder text with real AI-powered image analysis using configurable VLM models (initially google/gemma-3-4b for testing). Preserve existing technical metadata alongside new VLM descriptions.

## Technical Context

**Language/Version**: Python 3.13 (per project requirements)
**Primary Dependencies**: mlx-vlm (VLM processing), PIL/Pillow (image handling), existing image_processor module
**Storage**: File system (image files), no persistent storage required
**Testing**: pytest with existing test structure (unit, integration, contract)
**Target Platform**: macOS/Linux development environment
**Project Type**: single - CLI tool with module API
**Performance Goals**: Model loading within reasonable time, configurable timeout for VLM processing
**Constraints**: Memory cleanup after batch processing, 250-line file limit per constitution
**Scale/Scope**: Single image and batch processing, maintain existing API compatibility

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

- [x] All dependencies justified with clear rationale (mlx-vlm for VLM processing)
- [x] Standard library solutions preferred over external packages
- [x] Dependency audit plan included

**Experimental Mindset Check**:

- [x] Learning objectives documented (real VLM integration)
- [x] Quick iteration approach planned
- [x] Breaking changes acceptable for architectural improvements

**Modular Architecture Check**:

- [x] Single responsibility per module (vlm_integration.py for VLM logic)
- [x] Clear interface definitions between modules
- [x] Modules designed for replaceability

## Project Structure

### Documentation (this feature)

```
specs/003-real-vlm-insegration/
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
image_processor/
├── __main__.py
├── cli.py
├── models.py
├── processor.py
├── exceptions.py
├── progress.py
├── streaming.py
└── vlm_integration.py  # New VLM module

tests/
├── contract/
├── integration/
└── unit/
```

**Structure Decision**: Single project structure with existing image_processor module. New VLM integration will be added as vlm_integration.py module within src/image_processor/ to maintain existing API compatibility while adding real VLM functionality.

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
- Generate VLM-specific contract tests from contracts/ directory [P]
- Create enhanced data model implementations from data-model.md [P]
- Implement VLM integration module (vlm_integration.py)
- Extend existing processor.py with VLM capability while preserving compatibility
- Update CLI and models to support enhanced results
- Integration tests from quickstart.md scenarios

**Ordering Strategy**:

- Contract tests first (TDD approach)
- VLM integration module (independent) [P]
- Enhanced data models [P]
- Processor enhancement (depends on VLM module)
- CLI updates (depends on processor)
- Integration tests (depends on all components)

**Estimated Output**: 18-22 numbered, ordered tasks focusing on VLM integration while maintaining existing functionality

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
