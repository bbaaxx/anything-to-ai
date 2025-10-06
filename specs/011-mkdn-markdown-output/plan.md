# Implementation Plan: Markdown Output Format Support

**Branch**: `011-mkdn-markdown-output` | **Date**: 2025-10-02 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/011-mkdn-markdown-output/spec.md`

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

**IMPORTANT**: The /plan command STOPS at step 8. Phases 2-4 are executed by other commands:

- Phase 2: /tasks command creates tasks.md
- Phase 3-4: Implementation execution (manual or via tools)

## Summary

Add markdown output format (`--format markdown`) to all existing processing modules (pdf_extractor, image_processor, audio_processor, text_summarizer) to enable LLM-compatible, human-readable structured output. This enhancement preserves document structure in PDFs, formats images with VLM-generated captions, displays audio transcriptions with speaker labels and timestamps, and outputs text summaries with proper heading hierarchy. The feature enables seamless integration with LLM consumption workflows while maintaining backward compatibility with existing output formats.

**Key Clarifications (2025-10-02)**:
- No character escaping (rely on markdown processors)
- PDF structure fallback: plain paragraphs when detection fails
- VLM failure: generic fallback with "Description unavailable"
- Audio speaker fallback: plain paragraphs when speakers/timestamps missing
- Format conflict resolution: last specified format wins

## Technical Context

**Language/Version**: Python 3.13
**Primary Dependencies**: pdfplumber (PDF), mlx-vlm (VLM), Pillow (images), lightning-whisper-mlx (audio), alive-progress (CLI), httpx (LLM client)
**Storage**: File system only (no persistent storage)
**Testing**: pytest with 70% coverage requirement, contract tests, integration tests
**Target Platform**: macOS/Linux (MLX optimized for Apple Silicon)
**Project Type**: single (modular Python project with independent modules)
**Performance Goals**: Maintain current processing speeds, no degradation with markdown formatting
**Constraints**: 250-line rule per file (constitution), modular composition-first architecture, no new dependencies
**Scale/Scope**: 4 modules to modify (pdf_extractor, image_processor, audio_processor, text_summarizer), add optional shared markdown utilities

## Constitution Check

_GATE: Must pass before Phase 0 research. Re-check after Phase 1 design._

**Composition-First Check**:

- [x] All components are independently functional and testable
  - Markdown formatters will be separate, composable functions
  - Each module maintains independence, only formatter layer changes
- [x] No monolithic structures proposed
  - Shared formatter utilities (if needed) extracted to reusable module
  - Each module's formatter integration is independent
- [x] Complexity emerges through composition, not component complexity
  - Markdown rendering composed from simple text transformation functions
  - Format selection composes existing formatters with new markdown formatter

**250-Line Rule Check**:

- [x] No single file planned exceeds 250 lines (including comments/whitespace)
  - Current output_formatters.py is 137 lines
  - Markdown formatter functions: ~40-60 lines per module (simplified without escaping)
  - Shared utilities module (if created): <100 lines
- [x] Large modules identified for modular breakdown
  - No large modules anticipated, formatters are small and focused
- [x] Clear refactoring strategy for size violations
  - If any formatter exceeds 200 lines, split by content type (PDF structure vs image vs audio vs text)

**Minimal Dependencies Check**:

- [x] All dependencies justified with clear rationale
  - No new external dependencies required
  - Markdown generation uses standard string formatting
  - No escaping library needed (clarification decision)
- [x] Standard library solutions preferred over external packages
  - Using standard library only for markdown generation
  - No markdown rendering library needed (generating text output)
- [x] Dependency audit plan included
  - No dependency changes for this feature

**Experimental Mindset Check**:

- [x] Learning objectives documented
  - Explore markdown structure preservation from different source formats
  - Test LLM consumption of generated markdown
  - Validate no-escaping approach in practice
- [x] Quick iteration approach planned
  - Start with simplest markdown formatter (text_summarizer)
  - Iterate to more complex formatters (PDF structure, image captions, audio timestamps)
- [x] Breaking changes acceptable for architectural improvements
  - No breaking changes expected, only additive feature

**Modular Architecture Check**:

- [x] Single responsibility per module
  - Markdown formatters: pure formatting functions
  - Module CLIs: coordinate formatting selection
  - Shared utilities: reusable markdown helpers (optional)
- [x] Clear interface definitions between modules
  - Formatter interface: `format_markdown(result) -> str`
  - All modules use consistent format parameter
- [x] Modules designed for replaceability
  - Markdown formatters are optional, modules work without them
  - Easy to swap or enhance formatting logic independently

## Project Structure

### Documentation (this feature)

```
specs/011-mkdn-markdown-output/
├── plan.md              # This file (/plan command output)
├── research.md          # Phase 0 output (/plan command) ✓
├── data-model.md        # Phase 1 output (/plan command) ✓
├── quickstart.md        # Phase 1 output (/plan command) ✓
├── contracts/           # Phase 1 output (/plan command) ✓
│   ├── pdf_markdown.yaml
│   ├── image_markdown.yaml
│   ├── audio_markdown.yaml
│   └── text_markdown.yaml
└── tasks.md             # Phase 2 output (/tasks command - NOT created by /plan)
```

### Source Code (repository root)

```
# Single project structure
pdf_extractor/
├── __init__.py
├── __main__.py
├── cli.py
├── output_formatters.py     # Extend with markdown support
├── markdown_formatter.py    # NEW: PDF-specific markdown formatting
├── models.py
├── reader.py
└── ...existing files...

image_processor/
├── __init__.py
├── __main__.py
├── cli.py
├── markdown_formatter.py    # NEW: Image markdown with captions
├── models.py
└── ...existing files...

audio_processor/
├── __init__.py
├── __main__.py
├── markdown_formatter.py    # NEW: Audio transcript markdown with timestamps
├── models.py
└── ...existing files...

text_summarizer/
├── __init__.py
├── __main__.py
├── markdown_formatter.py    # NEW: Summary markdown with hierarchy
├── models.py
└── ...existing files...

markdown_utils/              # OPTIONAL: Shared markdown utilities
├── __init__.py
├── structure.py             # Heading hierarchy helpers (no escaping needed)
└── README.md

tests/
├── contract/
│   ├── test_pdf_markdown.py        # NEW: PDF markdown contract
│   ├── test_image_markdown.py      # NEW: Image markdown contract
│   ├── test_audio_markdown.py      # NEW: Audio markdown contract
│   └── test_text_markdown.py       # NEW: Text markdown contract
├── integration/
│   ├── test_pdf_markdown_integration.py   # NEW
│   ├── test_image_markdown_integration.py # NEW
│   ├── test_audio_markdown_integration.py # NEW
│   └── test_text_markdown_integration.py  # NEW
└── unit/
    └── test_markdown_utils.py       # NEW: Shared utilities tests (if needed)
```

**Structure Decision**: Single project structure maintained. All processing modules exist as independent top-level directories. `markdown_utils/` module is optional - may not be needed given simplified no-escaping approach. Each processor module gets its own `markdown_formatter.py` file for domain-specific markdown generation while keeping under 250-line limit.

## Phase 0: Outline & Research

✅ **Completed** - See `research.md`

Key decisions documented:
- CommonMark/GFM markdown syntax
- No character escaping (clarified 2025-10-02)
- Conservative PDF structure detection with plain paragraph fallback
- LLM-optimized markdown structure
- Consistent module patterns with error handling
- No new dependencies required

**Output**: research.md ✓

## Phase 1: Design & Contracts

✅ **Completed** - See artifacts below

### Artifacts Generated

1. **data-model.md** ✓
   - MarkdownContent (shared model)
   - DocumentStructure (PDF-specific)
   - MarkdownImageReference (image-specific)
   - TranscriptSegment (audio-specific)
   - SummaryHierarchy (text-specific)

2. **contracts/** ✓
   - `pdf_markdown.yaml` - PDF structure preservation with fallback
   - `image_markdown.yaml` - Image references with VLM captions, fallback handling
   - `audio_markdown.yaml` - Transcripts with timestamps, speaker fallback
   - `text_markdown.yaml` - Summaries with hierarchy

3. **quickstart.md** ✓
   - Test sequences for all 4 modules
   - Pipeline integration tests
   - Edge case validation
   - Success criteria checklist

4. **CLAUDE.md** ✓
   - Updated with markdown format commands

**Output**: All Phase 1 artifacts generated ✓

## Phase 2: Task Planning Approach

_This section describes what the /tasks command will do - DO NOT execute during /plan_

**Task Generation Strategy**:

1. **Optional Shared Infrastructure** (evaluate if needed):
   - Determine if `markdown_utils/` module is necessary
   - If created: implement structure helpers (heading levels, lists)
   - Write unit tests for utilities

2. **Per-Module Tasks** (repeat for each: pdf_extractor, image_processor, audio_processor, text_summarizer):
   - Create contract test for markdown format [P]
   - Create `{module}/markdown_formatter.py` [P]
   - Implement markdown formatting function (no escaping, simpler)
   - Integrate markdown option into CLI argument parser
   - Connect formatter to output logic
   - Implement fallback behaviors (clarified edge cases)
   - Create integration tests [P]
   - Test manual execution with sample files

3. **Integration Tasks**:
   - Test all modules with markdown format
   - Verify LLM consumption (pipe to text_summarizer)
   - Test error conditions (VLM failures, structure detection failures)
   - Validate format conflict resolution (last wins)

4. **Documentation Tasks**:
   - Update each module's README with markdown examples
   - Update CLAUDE.md with markdown format commands (done)
   - Verify quickstart.md accuracy

**Ordering Strategy**:

- Phase 1: Evaluate shared utilities need (may skip if unnecessary)
- Phase 2: Contract tests (TDD, all modules parallel [P])
- Phase 3: Formatter implementation (per module, parallel [P])
- Phase 4: CLI integration (per module, parallel [P])
- Phase 5: Integration testing
- Phase 6: Documentation

**Estimated Output**: 30-35 numbered, ordered tasks in tasks.md (reduced from original estimate due to no escaping)

**IMPORTANT**: This phase is executed by the /tasks command, NOT by /plan

## Phase 3+: Future Implementation

_These phases are beyond the scope of the /plan command_

**Phase 3**: Task execution (/tasks command creates tasks.md)
**Phase 4**: Implementation (execute tasks.md following constitutional principles)
**Phase 5**: Validation (run tests, execute quickstart.md, performance validation)

## Complexity Tracking

_Fill ONLY if Constitution Check has violations that must be justified_

No constitutional violations identified. All checks pass:
- Composition-first: Formatters are simple, composable functions
- 250-line rule: All files under limit with clear refactoring plan (simplified by no escaping)
- Minimal dependencies: No new dependencies
- Experimental mindset: Iterative approach, learning objectives documented
- Modular architecture: Clear separation, single responsibility

**Impact of Clarifications**:
- No escaping decision significantly simplifies implementation
- Reduces complexity and file lengths
- Aligns with "minimal dependencies" principle
- May result in optional/minimal shared utilities module

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
- [x] All NEEDS CLARIFICATION resolved (via /clarify session 2025-10-02)
- [x] Complexity deviations documented (none required)

**Clarifications Applied**:
- [x] Updated research.md with no-escaping decision
- [x] Updated research.md with edge case resolutions
- [x] Verified contracts align with clarifications
- [x] Verified data-model aligns with clarifications

---

_Based on Constitution v1.0.0 - See `/memory/constitution.md`_
_Clarifications from /clarify session 2025-10-02 integrated_
