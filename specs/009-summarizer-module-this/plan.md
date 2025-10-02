# Implementation Plan: Text Summarizer Module

**Branch**: `009-summarizer-module-this` | **Date**: 2025-10-01 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/009-summarizer-module-this/spec.md`

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

The summarizer module accepts text input (from PDFs, images, audio transcriptions, or direct input) and uses the existing LLM client module to generate intelligent summaries with categorization tags. The LLM determines appropriate summary length based on content density and complexity. For texts exceeding 10,000 words, the system uses sharded/chunked analysis. The module auto-detects input language and always outputs summaries and tags in English, supporting both JSON (default) and plain text output formats.

## Technical Context

**Language/Version**: Python 3.13
**Primary Dependencies**: llm_client module (OpenAI-compatible client), standard library (json, argparse, sys)
**Storage**: N/A (in-memory processing)
**Testing**: pytest, pytest-cov
**Target Platform**: macOS/Linux CLI (Python 3.13+)
**Project Type**: single (CLI utility module)
**Performance Goals**: Process 10k words in <30 seconds, 100k words with sharding in <5 minutes
**Constraints**: UTF-8 encoding only, 10k word threshold for sharding, minimum 3 tags per summary
**Scale/Scope**: Single module with CLI interface, ~200 lines max per file (250-line constitutional limit)

## Constitution Check

_GATE: Must pass before Phase 0 research. Re-check after Phase 1 design._

**Composition-First Check**:

- [x] All components are independently functional and testable (text processor, LLM client wrapper, output formatter, CLI parser)
- [x] No monolithic structures proposed (separate concerns: input → processing → output)
- [x] Complexity emerges through composition, not component complexity (sharding is composition of single-text processing)

**250-Line Rule Check**:

- [x] No single file planned exceeds 250 lines (4 main files: models ~50, processor ~100, formatter ~50, CLI ~50)
- [x] Large modules identified for modular breakdown (text processor may need chunking logic separated)
- [x] Clear refactoring strategy for size violations (split by concern: chunker, summarizer, validator)

**Minimal Dependencies Check**:

- [x] All dependencies justified with clear rationale (llm_client for LLM calls, standard library for everything else)
- [x] Standard library solutions preferred over external packages (json, argparse, sys, typing)
- [x] Dependency audit plan included (only llm_client required, already exists in project)

**Experimental Mindset Check**:

- [x] Learning objectives documented (explore LLM-based summarization patterns, multi-language handling)
- [x] Quick iteration approach planned (start with basic summarization, add sharding if needed)
- [x] Breaking changes acceptable for architectural improvements (output format may evolve)

**Modular Architecture Check**:

- [x] Single responsibility per module (models=data, processor=logic, formatter=output, CLI=interface)
- [x] Clear interface definitions between modules (typed data classes, function signatures)
- [x] Modules designed for replaceability (can swap LLM client, output formatters independently)

## Project Structure

### Documentation (this feature)

```
specs/009-summarizer-module-this/
├── plan.md              # This file (/plan command output)
├── research.md          # Phase 0 output (/plan command)
├── data-model.md        # Phase 1 output (/plan command)
├── quickstart.md        # Phase 1 output (/plan command)
├── contracts/           # Phase 1 output (/plan command)
└── tasks.md             # Phase 2 output (/tasks command - NOT created by /plan)
```

### Source Code (repository root)

```
text_summarizer/                    # New module for this feature
├── __init__.py                     # Module exports
├── __main__.py                     # CLI entry point
├── models.py                       # Data models (SummaryRequest, SummaryResult)
├── processor.py                    # Core summarization logic
├── chunker.py                      # Text chunking for large inputs (>10k words)
├── formatter.py                    # Output formatting (JSON, plain text)
└── cli.py                          # CLI argument parsing

tests/
├── contract/
│   └── test_summarizer_api.py     # Contract tests for module API
├── integration/
│   ├── test_single_text.py        # End-to-end summarization tests
│   ├── test_large_text.py         # Sharding/chunking tests
│   └── test_multilingual.py       # Language detection tests
└── unit/
    ├── test_models.py              # Data model tests
    ├── test_processor.py           # Processor unit tests
    ├── test_chunker.py             # Chunking logic tests
    └── test_formatter.py           # Formatter tests
```

**Structure Decision**: Single project (direct module structure). Following the existing pattern of `audio_processor/`, `image_processor/`, `pdf_extractor/`, and `llm_client/`, the new `text_summarizer/` module will be a standalone directory at the repository root. This maintains consistency with the current architecture where each processing module is independently organized.

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

The /tasks command will:
1. Load `.specify/templates/tasks-template.md` as base
2. Generate tasks from Phase 1 artifacts:
   - data-model.md → Data model implementation tasks
   - contracts/module_api.md → Contract test tasks
   - quickstart.md → Integration test scenarios
3. Group by type:
   - Contract tests (one per API function) [P]
   - Data models (Pydantic classes) [P]
   - Core implementation (processor, chunker, formatter)
   - CLI implementation
   - Integration tests (from quickstart scenarios)
   - Documentation updates

**Ordering Strategy**:

Following TDD and dependency order:
1. **Foundation** [P]: Data models (models.py), exceptions
2. **Contract Tests** [P]: test_summarizer_api.py (all tests failing initially)
3. **Core Logic**:
   - chunker.py (text splitting logic)
   - processor.py (LLM integration, summarization)
   - formatter.py (JSON/plain text output)
4. **CLI Layer**: cli.py, __main__.py
5. **Integration Tests**: Based on quickstart.md scenarios
6. **Validation**: Run quickstart.md as final validation

**Parallel Execution Opportunities** [P]:
- All data model files
- All contract test files
- Chunker and formatter (independent of each other)
- Unit tests for each module

**File Size Monitoring**:
Each task will include a note to check file length against 250-line limit:
- models.py: ~80 lines (4 classes)
- processor.py: ~150 lines (main logic)
- chunker.py: ~70 lines (splitting logic)
- formatter.py: ~60 lines (2 formatters)
- cli.py: ~100 lines (argument parsing, main)
- __main__.py: ~20 lines (entry point)

Total: ~480 lines across 6 files (well within limits)

**Estimated Output**: 28-32 numbered, ordered tasks in tasks.md

**Task Categories**:
- Setup & Models: 4 tasks
- Contract Tests: 3 tasks
- Core Implementation: 8-10 tasks
- CLI & Integration: 5-6 tasks
- Testing & Validation: 6-8 tasks
- Documentation: 2 tasks

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
- [x] Post-Design Constitution Check: PASS (no violations introduced during design)
- [x] All NEEDS CLARIFICATION resolved
- [x] Complexity deviations documented (none required)

---

_Based on Constitution v1.0.0 - See `/memory/constitution.md`_
