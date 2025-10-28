# Implementation Plan: Metadata Dictionary for Result Models

**Branch**: `015-extend-all-result` | **Date**: 2025-10-25 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/015-extend-all-result/spec.md`

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

Add optional metadata dictionary to all result models (PDF, image, audio, text) to preserve source document information and processing context. For PDFs: page count, file size, creation date. For images: EXIF data, dimensions, camera info. For audio: duration, sample rate, language confidence. For all: processing timestamps, model versions, configuration used. Controlled via `--include-metadata` flag (default: disabled for backward compatibility). Metadata structure is consistent across modules with universal fields (timestamps, model versions, config) and type-specific fields (EXIF, file metadata, quality metrics).

## Technical Context

**Language/Version**: Python 3.11+ (project requires >=3.11)
**Primary Dependencies**: pdfplumber (PDF), mlx-vlm (VLM), Pillow (images), lightning-whisper-mlx (audio), pydantic (text_summarizer validation), httpx (LLM client)
**Storage**: N/A (in-memory processing only, no persistent storage)
**Testing**: pytest (unit, integration, contract tests), pytest-cov (80% coverage minimum)
**Target Platform**: macOS (MLX-optimized models), Linux (compatible)
**Project Type**: single (CLI-based processing modules with dataclasses/pydantic models)
**Performance Goals**: Metadata extraction negligible overhead (<1% processing time increase), ISO 8601 timestamp formatting
**Constraints**: Must maintain backward compatibility (metadata disabled by default), preserve existing output formats (JSON, plain, markdown, CSV)
**Scale/Scope**: 4 processing modules (pdf_extractor, image_processor, audio_processor, text_summarizer), extend existing result models (ExtractionResult, ProcessingResult, DescriptionResult, TranscriptionResult, SummaryResult)

## Constitution Check

_GATE: Must pass before Phase 0 research. Re-check after Phase 1 design._

**Composition-First Check**:

- [x] All components are independently functional and testable - Metadata extraction is isolated to dedicated functions/methods within each module
- [x] No monolithic structures proposed - Each module handles its own metadata extraction logic, composed into result models
- [x] Complexity emerges through composition, not component complexity - Metadata dictionary is a simple dict/dataclass with clear field definitions

**250-Line Rule Check**:

- [x] No single file planned exceeds 250 lines (including comments/whitespace) - Current model files are under 100 lines; adding metadata fields and extraction logic will keep them under 200 lines
- [x] Large modules identified for modular breakdown - Metadata extraction can be split into separate metadata.py files per module if needed
- [x] Clear refactoring strategy for size violations - If models.py exceeds 200 lines, extract metadata logic to metadata.py or metadata_extractor.py

**Minimal Dependencies Check**:

- [x] All dependencies justified with clear rationale - Using stdlib datetime for ISO 8601 timestamps, PIL/Pillow EXIF (already used for images), os.stat for file metadata
- [x] Standard library solutions preferred over external packages - datetime, os, pathlib for metadata extraction; no new external dependencies required
- [x] Dependency audit plan included - No new dependencies; verify existing dependencies (Pillow for EXIF) remain minimal

**Experimental Mindset Check**:

- [x] Learning objectives documented - Explore comprehensive metadata preservation patterns similar to MarkItDown, learn EXIF handling best practices
- [x] Quick iteration approach planned - Start with universal metadata (timestamps, model versions), then add type-specific fields incrementally
- [x] Breaking changes acceptable for architectural improvements - Feature is additive (optional metadata), no breaking changes to existing API

**Modular Architecture Check**:

- [x] Single responsibility per module - Each processing module owns its metadata extraction logic
- [x] Clear interface definitions between modules - Metadata schema defined in contracts with universal fields + type-specific extensions
- [x] Modules designed for replaceability - Metadata extraction logic can be swapped without affecting core processing functionality

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
anyfile_to_ai/
├── pdf_extractor/
│   ├── models.py          # Extend ExtractionResult with metadata
│   ├── metadata.py        # New: PDF metadata extraction logic
│   ├── processor.py       # Update to collect metadata
│   └── cli.py             # Add --include-metadata flag
├── image_processor/
│   ├── models.py          # Extend DescriptionResult/ProcessingResult with metadata
│   ├── metadata.py        # New: Image/EXIF metadata extraction
│   ├── processor.py       # Update to collect metadata
│   └── cli.py             # Add --include-metadata flag
├── audio_processor/
│   ├── models.py          # Extend TranscriptionResult/ProcessingResult with metadata
│   ├── metadata.py        # New: Audio metadata extraction
│   ├── processor.py       # Update to collect metadata
│   └── cli.py             # Add --include-metadata flag
└── text_summarizer/
    ├── models.py          # Extend SummaryResult with metadata
    ├── metadata.py        # New: Text processing metadata
    ├── processor.py       # Update to collect metadata
    └── cli.py             # Add --include-metadata flag

tests/
├── contract/
│   ├── test_metadata_schema.py           # New: JSON schema validation
│   ├── test_pdf_metadata_contract.py     # New: PDF metadata contract tests
│   ├── test_image_metadata_contract.py   # New: Image metadata contract tests
│   ├── test_audio_metadata_contract.py   # New: Audio metadata contract tests
│   └── test_text_metadata_contract.py    # New: Text metadata contract tests
├── integration/
│   ├── test_pdf_metadata_integration.py
│   ├── test_image_metadata_integration.py
│   ├── test_audio_metadata_integration.py
│   └── test_text_metadata_integration.py
└── unit/
    ├── test_pdf_metadata.py
    ├── test_image_metadata.py
    ├── test_audio_metadata.py
    └── test_text_metadata.py
```

**Structure Decision**: Single project structure with modular processing packages. Each module (pdf_extractor, image_processor, audio_processor, text_summarizer) gets its own metadata.py for metadata extraction logic. Models.py files extended with optional metadata fields. CLI modules updated with --include-metadata flag. Test structure follows existing convention (contract/integration/unit separation).

## Phase 0: Outline & Research

1. **Extract unknowns from Technical Context** above:
   - No NEEDS CLARIFICATION markers in Technical Context (all resolved via clarifications session)
   - Research needed for: ISO 8601 timestamp format implementation, EXIF data extraction best practices, metadata schema design patterns, backward compatibility strategies

2. **Research Tasks**:
   - ISO 8601 timestamp formatting in Python (datetime.isoformat() vs strftime)
   - EXIF data extraction with Pillow (PIL.Image.getexif() API)
   - Metadata schema patterns (universal fields + type-specific extensions)
   - CLI flag implementation patterns for optional features
   - Metadata preservation through format conversions (JSON/markdown/CSV)

3. **Consolidate findings** in `research.md`:
   - Timestamp formatting: datetime.isoformat() for ISO 8601 with timezone
   - EXIF extraction: PIL.Image.getexif() with .get_ifd() for comprehensive tags
   - Schema design: TypedDict or dataclass for metadata structure
   - CLI flags: argparse --include-metadata (store_true action)
   - Format preservation: Include metadata in JSON as nested object, in markdown as YAML frontmatter or metadata section

**Output**: research.md with all research findings documented

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

The /tasks command will generate implementation tasks following TDD principles:

1. **Contract Test Tasks** (from contracts/):
   - metadata-schema.json → JSON schema validation test [P]
   - Each API contract (pdf, image, audio, text) → contract test file [P]
   - Total: 5 contract test tasks (parallel)

2. **Model Extension Tasks** (from data-model.md):
   - Extend ExtractionResult (PDF) with metadata field [P]
   - Extend DescriptionResult/ProcessingResult (Image) with metadata [P]
   - Extend TranscriptionResult (Audio) with metadata [P]
   - Extend SummaryMetadata (Text) with universal fields [P]
   - Total: 4 model extension tasks (parallel)

3. **Metadata Extraction Tasks** (per module):
   - Create pdf_extractor/metadata.py with extraction functions
   - Create image_processor/metadata.py with EXIF extraction
   - Create audio_processor/metadata.py with audio metadata extraction
   - Create text_summarizer/metadata.py with text metadata extraction
   - Total: 4 metadata extractor tasks (parallel)

4. **Processor Integration Tasks** (per module):
   - Update pdf_extractor/processor.py to collect metadata
   - Update image_processor/processor.py to collect metadata
   - Update audio_processor/processor.py to collect metadata
   - Update text_summarizer/processor.py to extend SummaryMetadata
   - Total: 4 processor update tasks (sequential after metadata extractors)

5. **CLI Update Tasks** (per module):
   - Add --include-metadata flag to pdf_extractor/cli.py
   - Add --include-metadata flag to image_processor/cli.py
   - Add --include-metadata flag to audio_processor/cli.py
   - No change for text_summarizer (already has --no-metadata)
   - Total: 3 CLI update tasks (parallel)

6. **Formatter Update Tasks** (per module):
   - Update JSON formatter to include metadata
   - Update markdown formatter to include metadata (frontmatter/section)
   - Update CSV formatter to flatten metadata
   - Update plain text formatter (exclude metadata)
   - Total: 4 formatter tasks per module (sequential after processor integration)

7. **Integration Test Tasks** (from quickstart.md):
   - PDF metadata integration test (full workflow)
   - Image EXIF extraction integration test
   - Audio language confidence integration test
   - Text summarizer backward compatibility test
   - Pipeline tests (PDF→summarizer, audio→summarizer)
   - Total: 6 integration test tasks

8. **Unit Test Tasks**:
   - PDF metadata extraction unit tests
   - Image EXIF extraction unit tests
   - Audio metadata extraction unit tests
   - Text metadata extraction unit tests
   - Timestamp formatting unit tests
   - Configuration metadata unit tests
   - Total: 6 unit test tasks (parallel)

**Ordering Strategy**:

```
Phase 1 (Parallel): Contract tests [1-5]
Phase 2 (Parallel): Model extensions [6-9]
Phase 3 (Parallel): Metadata extractors [10-13]
Phase 4 (Sequential): Processor integrations [14-17]
Phase 5 (Parallel): CLI updates [18-20]
Phase 6 (Sequential): Formatter updates [21-24]
Phase 7 (Parallel): Unit tests [25-30]
Phase 8 (Sequential): Integration tests [31-36]
Phase 9 (Sequential): Linting, coverage, validation
```

**Task Breakdown by Module**:

Each processing module (PDF, Image, Audio, Text) follows the same pattern:
1. Contract test (failing)
2. Extend model with metadata field
3. Create metadata.py extractor
4. Update processor.py to call extractor
5. Update cli.py with flag (if needed)
6. Update formatters to include metadata
7. Unit tests for metadata extraction
8. Integration test for end-to-end workflow

**Actual Output**: 54 numbered, ordered tasks in tasks.md (actual task count post-generation)

**Parallelization**:
- Tasks marked [P] can be executed in parallel (independent files)
- Model extensions and metadata extractors are fully parallel
- Processor/formatter updates are sequential per module (depend on extractors)
- Tests can be written in parallel with implementation

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

- [x] Phase 0: Research complete (/plan command) - ✅ research.md generated
- [x] Phase 1: Design complete (/plan command) - ✅ data-model.md, contracts/, quickstart.md generated
- [x] Phase 2: Task planning complete (/plan command - describe approach only) - ✅ Task generation strategy documented
- [ ] Phase 3: Tasks generated (/tasks command)
- [ ] Phase 4: Implementation complete
- [ ] Phase 5: Validation passed

**Gate Status**:

- [x] Initial Constitution Check: PASS - All checks passed, no violations
- [x] Post-Design Constitution Check: PASS - Design maintains constitutional compliance
- [x] All NEEDS CLARIFICATION resolved - Clarifications session completed in spec
- [x] Complexity deviations documented - No deviations required

---

_Based on Constitution v1.0.0 - See `/memory/constitution.md`_
