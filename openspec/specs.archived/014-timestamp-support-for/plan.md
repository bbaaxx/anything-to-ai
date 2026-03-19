# Implementation Plan: Timestamp Support for Audio Transcription

**Branch**: `014-timestamp-support-for` | **Date**: 2025-10-06 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/014-timestamp-support-for/spec.md`

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

Enhance the audio_processor module to support optional segment-level timestamps in transcriptions. Users can enable timestamps via a `--timestamps` CLI flag to get temporal markers at centisecond precision (HH:MM:SS.CC format) for each transcribed segment. Supports markdown output with human-readable timestamps (e.g., `[00:01:23.45] text`) and JSON output with structured arrays containing start/end times and text. When timestamp data is unavailable, the system warns the user but continues processing without timestamps, ensuring graceful degradation.

## Technical Context

**Language/Version**: Python 3.13 (per project requirements)
**Primary Dependencies**: lightning-whisper-mlx (audio transcription with MLX optimization), existing audio_processor modules (models, processor, cli, formatters)
**Storage**: N/A (in-memory processing, no persistent storage)
**Testing**: pytest (unit, integration, contract tests following existing patterns)
**Target Platform**: macOS (MLX-optimized for Apple Silicon)
**Project Type**: single (CLI application with modular architecture)
**Performance Goals**: Timestamp extraction should not significantly impact transcription performance (maintain existing transcription speed)
**Constraints**: Segment-level granularity only, centisecond precision, 250-line file limit per constitution, minimal dependency additions
**Scale/Scope**: Single audio file and batch processing support, all existing audio formats (mp3, wav, m4a), backward compatible with non-timestamp usage

## Constitution Check

_GATE: Must pass before Phase 0 research. Re-check after Phase 1 design._

**Composition-First Check**:

- [x] All components are independently functional and testable (timestamp models, formatters, CLI flag handling are separate concerns)
- [x] No monolithic structures proposed (extending existing modular audio_processor architecture)
- [x] Complexity emerges through composition, not component complexity (timestamp data added to existing TranscriptionResult model, formatter functions handle display)

**250-Line Rule Check**:

- [x] No single file planned exceeds 250 lines (including comments/whitespace)
- [x] Large modules identified for modular breakdown (existing files already under 250 lines: models.py=83, processor.py=203, cli.py=240)
- [x] Clear refactoring strategy for size violations (timestamp formatting separated into dedicated formatter module, similar to existing markdown_formatter.py)

**Minimal Dependencies Check**:

- [x] All dependencies justified with clear rationale (lightning-whisper-mlx already in use, provides timestamp data natively)
- [x] Standard library solutions preferred over external packages (using standard library datetime/time for timestamp formatting)
- [x] Dependency audit plan included (no new external dependencies required)

**Experimental Mindset Check**:

- [x] Learning objectives documented (exploring Whisper segment-level timestamp extraction capabilities)
- [x] Quick iteration approach planned (add optional field to existing model, extend formatters)
- [x] Breaking changes acceptable for architectural improvements (backward compatible, additive change only)

**Modular Architecture Check**:

- [x] Single responsibility per module (models handle data, formatters handle display, processor handles logic, CLI handles arguments)
- [x] Clear interface definitions between modules (TranscriptionResult model extended with optional timestamps field)
- [x] Modules designed for replaceability (timestamp formatting can be swapped without affecting transcription logic)

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
anyfile_to_ai/
├── audio_processor/
│   ├── __init__.py
│   ├── __main__.py
│   ├── models.py              # [MODIFY] Add timestamp fields to TranscriptionResult
│   ├── processor.py           # [MODIFY] Extract and attach timestamp data from Whisper
│   ├── cli.py                 # [MODIFY] Add --timestamps flag
│   ├── config.py              # [MODIFY] Add timestamps config option
│   ├── markdown_formatter.py  # [MODIFY] Add timestamp formatting for markdown
│   ├── streaming.py           # [EXISTING] No changes
│   ├── model_loader.py        # [EXISTING] No changes
│   ├── progress.py            # [EXISTING] No changes
│   └── exceptions.py          # [EXISTING] No changes
└── [other modules unchanged]

tests/
├── contract/
│   └── test_timestamp_contracts.py  # [NEW] Contract tests for timestamp API
├── integration/
│   └── test_timestamp_integration.py  # [NEW] End-to-end timestamp tests
└── unit/
    └── test_timestamp_formatting.py   # [NEW] Unit tests for timestamp formatters
```

**Structure Decision**: Single project structure (Option 1). This feature extends the existing `anyfile_to_ai/audio_processor/` module by adding timestamp support. Changes are localized to the audio_processor package, maintaining the existing modular architecture. No new top-level modules required.

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

The /tasks command will generate tasks based on Phase 1 artifacts:

1. **Model Tasks** (from data-model.md):
   - Add TranscriptionSegment dataclass to models.py
   - Extend TranscriptionResult with optional segments field
   - Extend TranscriptionConfig with timestamps field

2. **Contract Test Tasks** (from contracts/):
   - test_timestamp_contracts.py: TranscriptionSegment structure validation
   - test_timestamp_contracts.py: TranscriptionResult.segments field validation
   - test_timestamp_contracts.py: CLI --timestamps flag parsing
   - test_timestamp_contracts.py: process_audio with timestamps contract

3. **Processor Implementation Tasks**:
   - Extract segments from Whisper result in processor.py
   - Convert seek positions to seconds
   - Create TranscriptionSegment instances
   - Handle missing timestamp data with warning

4. **Formatter Implementation Tasks**:
   - Add format_timestamp() to markdown_formatter.py
   - Add format_segments_markdown() to markdown_formatter.py
   - Extend format_output() to handle timestamps in markdown
   - Extend JSON formatter to include segments
   - Extend CSV formatter to output timestamp rows

5. **CLI Tasks**:
   - Add --timestamps argument to CLI parser
   - Pass timestamps config to processor

6. **Integration Test Tasks** (from quickstart.md scenarios):
   - test_timestamp_integration.py: Single file with timestamps
   - test_timestamp_integration.py: Batch processing with timestamps
   - test_timestamp_integration.py: Graceful degradation when unavailable
   - test_timestamp_integration.py: All output formats work correctly

7. **Unit Test Tasks**:
   - test_timestamp_formatting.py: format_timestamp() edge cases
   - test_timestamp_formatting.py: Markdown formatting
   - test_timestamp_formatting.py: CSV formatting
   - test_timestamp_formatting.py: JSON serialization

**Ordering Strategy**:

1. **Phase A - Models & Config** [P]:
   - Task 1: Add TranscriptionSegment model [P]
   - Task 2: Extend TranscriptionResult model [P]
   - Task 3: Extend TranscriptionConfig model [P]

2. **Phase B - Contract Tests** (after models):
   - Task 4: Write model contract tests
   - Task 5: Write processor contract tests
   - Task 6: Write CLI contract tests
   - Task 7: Write formatter contract tests

3. **Phase C - Implementation** (TDD: tests before code) [some parallel]:
   - Task 8: Implement format_timestamp() [P]
   - Task 9: Implement segment extraction in processor
   - Task 10: Implement format_segments_markdown() [P]
   - Task 11: Add --timestamps CLI flag
   - Task 12: Extend JSON formatter
   - Task 13: Extend CSV formatter

4. **Phase D - Integration Tests & Validation**:
   - Task 14: Write integration tests
   - Task 15: Write unit tests for formatters
   - Task 16: Run full test suite
   - Task 17: Manual testing with quickstart scenarios

**Estimated Output**: ~17-20 tasks in dependency order

**Parallelization**: Tasks marked [P] can run in parallel (touch independent files)

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
- [x] Complexity deviations documented (none - all checks pass)

---

_Based on Constitution v1.0.0 - See `/memory/constitution.md`_
