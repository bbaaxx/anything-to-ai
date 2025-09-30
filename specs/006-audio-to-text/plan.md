# Implementation Plan: Audio-to-Text Transcription Module

**Branch**: `006-audio-to-text` | **Date**: 2025-09-29 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/006-audio-to-text/spec.md`

## Execution Flow (/plan command scope)

```
1. Load feature spec from Input path
   → ✅ Loaded from /specs/006-audio-to-text/spec.md
2. Fill Technical Context (scan for NEEDS CLARIFICATION)
   → ✅ No NEEDS CLARIFICATION markers found (all resolved in clarifications)
   → ✅ Project Type: single (Python module)
3. Fill the Constitution Check section
   → ✅ Completed initial constitutional review
4. Evaluate Constitution Check section
   → ✅ PASS - No violations identified
   → ✅ Update Progress Tracking: Initial Constitution Check
5. Execute Phase 0 → research.md
   → ✅ Created research.md with technology decisions
6. Execute Phase 1 → contracts, data-model.md, quickstart.md, CLAUDE.md
   → ✅ Created data-model.md with 4 core entities
   → ✅ Created contracts/module-api.yaml
   → ✅ Created contracts/cli-interface.yaml
   → ✅ Created quickstart.md with 15 validation scenarios
   → ✅ Updated CLAUDE.md via update-agent-context.sh
7. Re-evaluate Constitution Check section
   → ✅ PASS - Design maintains constitutional compliance
   → ✅ Update Progress Tracking: Post-Design Constitution Check
8. Plan Phase 2 → Describe task generation approach
   → ✅ Documented in Phase 2 section below
9. STOP - Ready for /tasks command
   → ✅ Plan complete
```

**IMPORTANT**: The /plan command STOPS here. Phases 2-4 are executed by other commands:

- Phase 2: /tasks command creates tasks.md
- Phase 3-4: Implementation execution (manual or via tools)

## Summary

Implement an audio-to-text transcription module that processes audio files (mp3, wav, m4a) and generates text transcriptions using the lightning-whisper-mlx library. The module follows established patterns from `image_processor` and `pdf_extractor` modules, providing both CLI and programmatic interfaces. Key features include configurable Whisper models (tiny to large-v3), quantization options (none/4bit/8bit), multilingual support with auto-detection, batch processing with progress callbacks, and comprehensive error handling. The implementation leverages MLX framework for Apple Silicon optimization, achieving 10x speed improvement over standard Whisper implementations.

## Technical Context

**Language/Version**: Python 3.13 (per project requirements)
**Primary Dependencies**: lightning-whisper-mlx (Whisper transcription), pydub or mutagen (audio metadata extraction)
**Storage**: File system (audio files), no persistent storage required
**Testing**: pytest (unit, integration, contract tests)
**Target Platform**: Apple Silicon (macOS with MLX framework)
**Project Type**: single (Python module following existing module patterns)
**Performance Goals**: 10x faster than Whisper CPP, 4x faster than standard MLX Whisper, support up to 2-hour audio files
**Constraints**: ≤250 lines per file (constitutional), ≤2 hours audio duration, Apple Silicon required for MLX
**Scale/Scope**: Single audio file and batch processing, configurable models (11 variants), 3 audio formats, 3 output formats

## Constitution Check

_GATE: Must pass before Phase 0 research. Re-check after Phase 1 design._

**Composition-First Check**:

- [x] All components are independently functional and testable
  - Validator, model_loader, transcriber, streaming_processor can work independently
- [x] No monolithic structures proposed
  - Module broken into 9 focused files following image_processor pattern
- [x] Complexity emerges through composition, not component complexity
  - Streaming processor composes validator + transcriber + progress handler

**250-Line Rule Check**:

- [x] No single file planned exceeds 250 lines (including comments/whitespace)
  - Estimated file sizes: models.py (~80), exceptions.py (~150), processor.py (~200), cli.py (~220), others <150
- [x] Large modules identified for modular breakdown
  - Core processing split: validation → transcription → formatting
- [x] Clear refactoring strategy for size violations
  - If cli.py approaches limit, extract formatters to output_formatters.py

**Minimal Dependencies Check**:

- [x] All dependencies justified with clear rationale
  - lightning-whisper-mlx: Required for MLX-optimized Whisper (no alternative)
  - pydub/mutagen: Lightweight audio metadata extraction (evaluate lightest option)
- [x] Standard library solutions preferred over external packages
  - argparse, dataclasses, pathlib, json all from stdlib
- [x] Dependency audit plan included
  - Compare pydub vs mutagen for minimal footprint

**Experimental Mindset Check**:

- [x] Learning objectives documented
  - MLX optimization techniques, Whisper model performance characteristics
- [x] Quick iteration approach planned
  - Start with basic transcription, incrementally add features (quantization, multilingual, batch)
- [x] Breaking changes acceptable for architectural improvements
  - API follows established patterns but can evolve based on learnings

**Modular Architecture Check**:

- [x] Single responsibility per module
  - models: data structures only, processor: transcription only, cli: interface only
- [x] Clear interface definitions between modules
  - Public API: process_audio(), process_audio_batch(), validate_audio(), create_config()
- [x] Modules designed for replaceability
  - Whisper model can be replaced, audio metadata library can be swapped

## Project Structure

### Documentation (this feature)

```
specs/006-audio-to-text/
├── plan.md              # This file (/plan command output)
├── research.md          # Phase 0 output (/plan command) ✅
├── data-model.md        # Phase 1 output (/plan command) ✅
├── quickstart.md        # Phase 1 output (/plan command) ✅
├── contracts/           # Phase 1 output (/plan command) ✅
│   ├── module-api.yaml
│   └── cli-interface.yaml
└── tasks.md             # Phase 2 output (/tasks command - NOT created yet)
```

### Source Code (repository root)

```
audio_processor/              # New module (follows image_processor pattern)
├── __init__.py              # Public API exports (~80 lines)
├── __main__.py              # CLI entry point (~10 lines)
├── models.py                # Data structures (~80 lines)
├── exceptions.py            # Exception hierarchy (~150 lines)
├── processor.py             # Core transcription logic (~200 lines)
├── cli.py                   # CLI interface (~220 lines)
├── progress.py              # Progress callbacks (~50 lines)
├── streaming.py             # Batch processing (~120 lines)
└── model_loader.py          # Whisper model loading (~100 lines)

tests/
├── contract/
│   ├── test_module_api.py           # API contract tests (~150 lines)
│   ├── test_exceptions.py           # Exception hierarchy tests (~80 lines)
│   └── test_cli_parser.py           # CLI parser tests (~100 lines)
├── integration/
│   ├── test_single_audio.py         # Single file transcription (~150 lines)
│   ├── test_batch_processing.py     # Batch processing (~150 lines)
│   └── test_error_workflows.py      # Error handling scenarios (~180 lines)
└── unit/
    ├── test_models.py               # Model validation (~100 lines)
    └── test_audio_validation.py     # Audio validation logic (~120 lines)

sample-data/
└── audio/                   # Test audio files
    ├── speech.mp3           # Normal speech sample
    ├── silence.wav          # Silent audio
    ├── spanish.m4a          # Spanish speech
    └── long.mp3             # Longer audio sample
```

**Structure Decision**: Single project structure selected. The repository follows a modular architecture with separate directories for each feature module (pdf_extractor, image_processor, audio_processor). This matches the existing project pattern where each module is self-contained and follows identical organizational principles. Tests are organized by type (contract, integration, unit) at the repository level to maintain consistency across all modules.

## Phase 0: Outline & Research

**Status**: ✅ Complete

1. **Extracted unknowns from Technical Context**:
   - All clarified in spec Session 2025-09-29 (9 questions answered)
   - No remaining NEEDS CLARIFICATION markers

2. **Research completed** (see research.md):
   - lightning-whisper-mlx library capabilities and API
   - Model variants and quantization options
   - Audio format support and metadata extraction
   - Module patterns from image_processor
   - API design patterns and exception hierarchy
   - Performance characteristics and optimization strategies

3. **Key decisions documented**:
   - Core library: lightning-whisper-mlx (10x performance gain)
   - Models: All 11 variants supported, default medium + 4bit
   - Audio formats: mp3, wav, m4a
   - Metadata library: pydub or mutagen (evaluate lightest)
   - Module structure: 9 files following image_processor pattern

**Output**: ✅ research.md created with all decisions, rationales, and alternatives

## Phase 1: Design & Contracts

**Status**: ✅ Complete

1. **Extracted entities from feature spec** → `data-model.md`: ✅
   - AudioDocument (6 fields)
   - TranscriptionResult (9 fields)
   - TranscriptionConfig (9 fields)
   - ProcessingResult (7 fields)
   - Validation rules and state transitions documented

2. **Generated API contracts** from functional requirements: ✅
   - contracts/module-api.yaml: 6 functions, 4 models, 10 exceptions
   - contracts/cli-interface.yaml: CLI arguments, output formats, error messages
   - Contracts map directly to functional requirements (FR-001 through FR-023)

3. **Contract tests planned** (not yet implemented):
   - tests/contract/test_module_api.py: Function signatures, return types, exceptions
   - tests/contract/test_exceptions.py: Exception hierarchy and fields
   - tests/contract/test_cli_parser.py: Argument parsing and validation

4. **Test scenarios extracted** from user stories → `quickstart.md`: ✅
   - 15 validation scenarios covering all functional requirements
   - Acceptance criteria from spec mapped to quickstart tests
   - Integration test scenarios for error workflows
   - Performance validation steps

5. **Updated agent file**: ✅
   - Executed `.specify/scripts/bash/update-agent-context.sh claude`
   - CLAUDE.md updated with new feature technologies
   - Manual additions preserved

**Output**: ✅ data-model.md, contracts/*.yaml, quickstart.md, updated CLAUDE.md

## Phase 2: Task Planning Approach

_This section describes what the /tasks command will do - DO NOT execute during /plan_

**Task Generation Strategy**:

1. Load `.specify/templates/tasks-template.md` as base template
2. Generate tasks from Phase 1 design artifacts:
   - contracts/module-api.yaml → contract test tasks
   - data-model.md → model creation tasks
   - quickstart.md → integration test tasks
   - research.md → implementation guidance

3. Task categories:
   - **Contract Tests** (5 tasks): Test files that assert API contracts [P]
   - **Data Models** (4 tasks): Create dataclasses for core entities [P]
   - **Exception Hierarchy** (1 task): Implement all exception types [P]
   - **Audio Validation** (2 tasks): File validation and metadata extraction
   - **Model Loading** (2 tasks): Whisper model loading and caching
   - **Core Processing** (3 tasks): Transcription logic, config handling, error handling
   - **Batch Processing** (2 tasks): Streaming processor, progress callbacks
   - **CLI Interface** (3 tasks): Argument parser, formatters, main entry point
   - **Integration Tests** (5 tasks): Single audio, batch, error workflows
   - **Documentation** (2 tasks): __init__.py exports, module docstrings

4. Dependency ordering:
   - Layer 0 [P]: Contract tests (fail fast, define interface)
   - Layer 1 [P]: Models, Exceptions (no dependencies)
   - Layer 2: Validation, Model Loading (depends on models/exceptions)
   - Layer 3: Core Processing (depends on validation, models)
   - Layer 4: Batch Processing, CLI (depends on core processing)
   - Layer 5: Integration Tests (depends on all implementation)
   - Layer 6: Documentation (final polish)

**Ordering Strategy**:

- TDD approach: Contract tests first to define expectations
- Bottom-up implementation: Models → Validation → Processing → CLI
- Parallel tasks marked [P] for independent file creation
- Sequential tasks enforce dependencies (validation before processing)

**Estimated Output**: 30-35 numbered, ordered tasks in tasks.md

**Task Format Example**:
```
1. [P] Create contract test for module API (test_module_api.py)
   - Test function signatures for process_audio, process_audio_batch, etc.
   - Assert exception types raised
   - Verify return types match contracts

2. [P] Create contract test for exception hierarchy (test_exceptions.py)
   - Test all exception types exist
   - Verify inheritance chain
   - Assert exception fields
```

**IMPORTANT**: This phase is executed by the /tasks command, NOT by /plan

## Phase 3+: Future Implementation

_These phases are beyond the scope of the /plan command_

**Phase 3**: Task execution (/tasks command creates tasks.md)
**Phase 4**: Implementation (execute tasks.md following constitutional principles)
**Phase 5**: Validation (run tests, execute quickstart.md, performance validation)

## Complexity Tracking

_Fill ONLY if Constitution Check has violations that must be justified_

No constitutional violations identified. All checks pass.

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
- [x] Complexity deviations documented (none)

**Artifacts Generated**:

- [x] research.md (2,982 words)
- [x] data-model.md (1,845 words)
- [x] contracts/module-api.yaml (6 functions, 4 models, 10 exceptions)
- [x] contracts/cli-interface.yaml (CLI specification)
- [x] quickstart.md (15 validation scenarios)
- [x] CLAUDE.md updated

---

**Plan Status**: ✅ COMPLETE - Ready for /tasks command

_Based on Constitution v1.0.0 - See `.specify/memory/constitution.md`_