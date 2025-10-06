# Implementation Plan: Prepare Repository for Python Packaging

**Branch**: `012-prepare-this-repository` | **Date**: 2025-10-06 | **Spec**: /specs/012-prepare-this-repository/spec.md
**Input**: Feature specification from `/specs/012-prepare-this-repository/spec.md`

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

Prepare the anyfile-to-ai repository for Python packaging and PyPI distribution. The approach involves creating a unified `anyfile_to_ai` package with optional extras for modular installation, maintaining existing CLI entry points while providing proper package metadata and build configuration. The solution excludes ML model dependencies from the package to reduce size and allow user choice, following Python packaging standards and constitutional principles.

## Technical Context

**Language/Version**: Python 3.11+ (per clarifications)  
**Primary Dependencies**: setuptools, wheel, build (packaging tools); existing module dependencies (pdfplumber, mlx-vlm, lightning-whisper-mlx, etc.)  
**Storage**: File system only (package distribution files)  
**Testing**: pytest (existing test framework)  
**Target Platform**: PyPI distribution for cross-platform Python installation  
**Project Type**: Single Python package with optional extras  
**Performance Goals**: Package build time <5 minutes, install time <2 minutes  
**Constraints**: Must comply with PyPI packaging standards, support modular installation  
**Scale/Scope**: 4 modules (pdf, image, audio, text) with optional extras

## Constitution Check

_GATE: Must pass before Phase 0 research. Re-check after Phase 1 design._

**Composition-First Check**:

- [x] All components are independently functional and testable (existing modules)
- [x] No monolithic structures proposed (modular package design)
- [x] Complexity emerges through composition, not component complexity (optional extras)

**250-Line Rule Check**:

- [x] No single file planned exceeds 250 lines (configuration files only)
- [x] Large modules identified for modular breakdown (existing modules already compliant)
- [x] Clear refactoring strategy for size violations (existing check_file_lengths.py)

**Minimal Dependencies Check**:

- [x] All dependencies justified with clear rationale (packaging tools + existing deps)
- [x] Standard library solutions preferred over external packages (setuptools, wheel)
- [x] Dependency audit plan included (existing pyproject.toml structure)

**Experimental Mindset Check**:

- [x] Learning objectives documented (Python packaging exploration)
- [x] Quick iteration approach planned (modular release strategy)
- [x] Breaking changes acceptable for architectural improvements (package name change)

**Modular Architecture Check**:

- [x] Single responsibility per module (each processing module has clear purpose)
- [x] Clear interface definitions between modules (CLI entry points, Python APIs)
- [x] Modules designed for replaceability (optional extras installation)

## Project Structure

### Documentation (this feature)

```
specs/012-prepare-this-repository/
├── plan.md              # This file (/plan command output)
├── research.md          # Phase 0 output (/plan command)
├── data-model.md        # Phase 1 output (/plan command)
├── quickstart.md        # Phase 1 output (/plan command)
├── contracts/           # Phase 1 output (/plan command)
└── tasks.md             # Phase 2 output (/tasks command - NOT created by /plan)
```

### Source Code (repository root)

```
anyfile_to_ai/              # Main package directory
├── __init__.py            # Package initialization
├── pdf_extractor/         # PDF processing module
├── image_processor/       # Image processing module
├── audio_processor/       # Audio processing module
├── text_summarizer/       # Text summarization module
└── llm_client/           # LLM client module

tests/
├── contract/             # Contract tests
├── integration/          # Integration tests
└── unit/                 # Unit tests

pyproject.toml            # Package configuration and metadata
README.md                 # PyPI package documentation
LICENSE                   # Package license
```

**Structure Decision**: Single Python package with modular subpackages, maintaining existing module structure while providing unified package metadata and distribution.

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
- Package metadata configuration task
- Directory structure reorganization task
- CLI entry point configuration task
- Optional dependencies setup task
- Build system configuration task
- Contract validation tasks for each schema
- Integration test tasks for installation scenarios
- Documentation update tasks

**Ordering Strategy**:

- Configuration before implementation
- Structure changes before code changes
- Build setup before testing
- Local testing before distribution
- Mark [P] for parallel execution (independent configuration files)

**Estimated Output**: 15-20 numbered, ordered tasks in tasks.md

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
