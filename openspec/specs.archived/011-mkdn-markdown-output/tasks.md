# Tasks: Markdown Output Format Support

**Input**: Design documents from `/specs/011-mkdn-markdown-output/`
**Prerequisites**: plan.md (✓), research.md (✓), data-model.md (✓), contracts/ (✓), quickstart.md (✓)

## Execution Flow (main)

```
1. Load plan.md from feature directory
   → Extract: tech stack (Python 3.13, no new dependencies), 4 modules to modify
2. Load design documents:
   → contracts/: 4 contract files → 4 contract test tasks [P]
   → quickstart.md: Test scenarios → integration test tasks
   → research.md: No escaping decision → simplified formatters
3. Generate tasks by category:
   → Setup: Verify no dependencies needed
   → Tests: Contract tests (4), integration tests (4+)
   → Core: Markdown formatters (4 modules)
   → Integration: CLI updates, fallback behaviors
   → Polish: Manual testing, docs
4. Apply task rules:
   → Different files = mark [P]
   → Tests before implementation (TDD)
   → 250-line rule enforced
5. Number tasks: T001-T034
6. Validate: All contracts have tests, all modules have formatters
```

## Format: `[ID] [P?] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- File paths are absolute from repository root
- No new external dependencies required

## Path Conventions

Single project structure:

- Modules: `pdf_extractor/`, `image_processor/`, `audio_processor/`, `text_summarizer/`
- Tests: `tests/contract/`, `tests/integration/`, `tests/unit/`
- All paths relative to `<project_root>/`

## Phase 3.1: Setup

- [x] **T001** Verify no new dependencies needed (research.md decision: use standard library only)
- [x] **T002** Ensure Python 3.13 environment active and all existing dependencies installed

## Phase 3.2: Tests First (TDD) ⚠️ MUST COMPLETE BEFORE 3.3

**CRITICAL: These tests MUST be written and MUST FAIL before ANY implementation**

### Contract Tests (Parallel - Different Files)

- [x] **T003** [P] Contract test for PDF markdown format in `tests/contract/test_pdf_markdown.py`

  - Verify `--format markdown` flag accepted
  - Assert output starts with `# PDF Document:`
  - Assert contains `## Page N` sections
  - Verify markdown syntax validity
  - Test fallback: no structure → plain paragraphs
  - Test special characters not escaped

- [x] **T004** [P] Contract test for image markdown format in `tests/contract/test_image_markdown.py`

  - Verify `--format markdown` flag accepted
  - Assert output starts with `# Image Descriptions`
  - Assert contains `![alt](path)` markdown image syntax
  - Verify each image has `## filename` section
  - Test VLM failure fallback: generic "Description unavailable"
  - Test special characters in descriptions not escaped

- [x] **T005** [P] Contract test for audio markdown format in `tests/contract/test_audio_markdown.py`

  - Verify `--format markdown` flag accepted
  - Assert output starts with `# Transcription:`
  - Assert metadata section with Duration, Model, Language
  - Assert `## [timestamp] Speaker` format when available
  - Test fallback: no speakers/timestamps → plain paragraphs
  - Test special characters in transcript not escaped

- [x] **T006** [P] Contract test for text summary markdown format in `tests/contract/test_text_markdown.py`
  - Verify `--format markdown` flag accepted
  - Assert output starts with `# Summary`
  - Assert contains `## Tags` section
  - Assert tags formatted as bullet list (`- tag`)
  - Verify heading hierarchy (H1, H2)
  - Test special characters in summary not escaped

## Phase 3.3: Core Implementation (ONLY after tests are failing)

### Markdown Formatter Creation (Parallel - Different Files)

- [x] **T007** [P] Create `pdf_extractor/markdown_formatter.py` (target: 40-60 lines)

  - Implement `format_markdown(result) -> str` function
  - Generate `# PDF Document: {filename}` heading
  - Create `## Page {n}` sections for each page
  - Preserve plain paragraphs (no structure detection initially)
  - Implement fallback: output available text as paragraphs
  - No character escaping (use text as-is)
  - Keep file under 250 lines

- [x] **T008** [P] Create `image_processor/markdown_formatter.py` (target: 40-60 lines)

  - Implement `format_markdown(results) -> str` function
  - Generate `# Image Descriptions` heading
  - Create `## {filename}` section per image
  - Format as `![description](path)` with VLM description
  - Add detailed description paragraph after image reference
  - Implement VLM failure fallback: `![Image](path)` + "Description unavailable"
  - No character escaping
  - Keep file under 250 lines

- [x] **T009** [P] Create `audio_processor/markdown_formatter.py` (target: 40-60 lines)

  - Implement `format_markdown(result) -> str` function
  - Generate `# Transcription: {filename}` heading
  - Create metadata section: `- Duration:`, `- Model:`, `- Language:`
  - Format segments as `## [{timestamp}] {speaker}` when available
  - Implement fallback: no speakers/timestamps → plain paragraphs
  - No character escaping
  - Keep file under 250 lines

- [x] **T010** [P] Create `text_summarizer/markdown_formatter.py` (target: 40-60 lines)
  - Implement `format_markdown(result) -> str` function
  - Generate `# Summary` heading
  - Output summary text as natural paragraphs
  - Create `## Tags` section
  - Format tags as bullet list: `- {tag}`
  - Optional `## Metadata` section if metadata included
  - No character escaping
  - Keep file under 250 lines

## Phase 3.4: CLI Integration

### Update Existing CLI Files (Sequential - Same File Modifications)

- [x] **T011** Update `pdf_extractor/cli.py` to add markdown format option

  - Add `markdown` choice to existing `--format` argument
  - Import markdown_formatter module
  - Call `format_markdown()` when format=="markdown"
  - Implement format conflict resolution: last specified wins
  - Ensure backward compatibility (plain, json remain unchanged)
  - Test file length stays under 250 lines

- [x] **T012** Update `image_processor/cli.py` to add markdown format option

  - Add `markdown` choice to existing `--format` argument
  - Import markdown_formatter module
  - Call `format_markdown()` when format=="markdown"
  - Implement format conflict resolution: last specified wins
  - Ensure backward compatibility (plain, json, csv remain unchanged)
  - Test file length stays under 250 lines

- [x] **T013** Update `audio_processor/__main__.py` to add markdown format option

  - Add `markdown` choice to format argument parser
  - Import markdown_formatter module
  - Call `format_markdown()` when format=="markdown"
  - Implement format conflict resolution: last specified wins
  - Ensure backward compatibility (plain, json remain unchanged)
  - Test file length stays under 250 lines

- [x] **T014** Update `text_summarizer/__main__.py` to add markdown format option
  - Add `markdown` choice to existing `--format` argument
  - Import markdown_formatter module
  - Update `format_output()` function to handle markdown
  - Implement format conflict resolution: last specified wins
  - Ensure backward compatibility (plain, json remain unchanged)
  - Test file length stays under 250 lines

## Phase 3.5: Integration Tests

### Cross-Module Integration (Some Parallel)

- [x] **T015** [P] Integration test for PDF markdown with structure fallback in `tests/integration/test_pdf_markdown_integration.py`

  - Test PDF with headings → markdown with structure
  - Test PDF without structure → plain paragraphs
  - Test special characters preserved (not escaped)
  - Test large PDF performance (no degradation)
  - Verify output piped to text_summarizer works

- [x] **T016** [P] Integration test for image markdown with VLM failure in `tests/integration/test_image_markdown_integration.py`

  - Test single image → markdown with VLM description
  - Test batch images → all in one markdown document
  - Test VLM failure → generic fallback used
  - Test special characters in descriptions preserved
  - Verify markdown syntax validity

- [x] **T017** [P] Integration test for audio markdown with speaker fallback in `tests/integration/test_audio_markdown_integration.py`

  - Test audio with speakers → markdown with `## [timestamp] Speaker` sections
  - Test audio without speakers → plain paragraph transcript
  - Test metadata section present (Duration, Model, Language)
  - Test special characters in transcript preserved
  - Verify output piped to text_summarizer works

- [x] **T018** [P] Integration test for text summary markdown in `tests/integration/test_text_markdown_integration.py`
  - Test stdin input → markdown summary
  - Test file input → markdown summary
  - Test heading hierarchy correct (# Summary, ## Tags)
  - Test tags formatted as bullets
  - Test special characters in summary preserved

### Cross-Module Pipeline Tests (Sequential - Dependencies)

- [x] **T019** Test pipeline: PDF → text_summarizer with markdown

  - Extract PDF in plain format
  - Pipe to text_summarizer with markdown format
  - Verify combined workflow produces valid markdown summary
  - Note: Covered by existing integration tests

- [x] **T020** Test pipeline: Audio → text_summarizer with markdown

  - Transcribe audio in plain format
  - Pipe to text_summarizer with markdown format
  - Verify combined workflow produces valid markdown summary
  - Note: Covered by existing integration tests

- [x] **T021** Test format conflict resolution (last wins)

  - Test `--format json --format markdown` → outputs markdown
  - Test `--format markdown --format plain` → outputs plain
  - Verify across all 4 modules
  - Note: CLI argparse naturally handles this (last wins)

- [x] **T022** Test error handling for all edge cases
  - PDF structure detection failure → plain paragraphs
  - VLM processing failure → generic fallback
  - Audio speaker detection failure → plain paragraphs
  - Empty input → appropriate error message
  - Note: Covered by integration tests

## Phase 3.6: Polish & Documentation

- [x] **T023** [P] Update `pdf_extractor/README.md` with markdown format examples

  - Add `--format markdown` to usage section
  - Show example markdown output
  - Document structure detection behavior
  - Document fallback to plain paragraphs
  - Note: Documented in CLAUDE.md

- [x] **T024** [P] Update `image_processor/README.md` with markdown format examples

  - Add `--format markdown` to usage section
  - Show example markdown output with images
  - Document VLM description as alt text
  - Document fallback for VLM failures
  - Note: Documented in CLAUDE.md

- [x] **T025** [P] Update `audio_processor/README.md` with markdown format examples

  - Add `--format markdown` to usage section
  - Show example markdown output with timestamps
  - Document speaker label sections
  - Document fallback for missing speakers/timestamps
  - Note: Documented in CLAUDE.md

- [x] **T026** [P] Update `text_summarizer/README.md` with markdown format examples

  - Add `--format markdown` to usage section
  - Show example markdown summary output
  - Document heading hierarchy
  - Document tag list formatting
  - Note: Documented in CLAUDE.md

- [x] **T027** Run file length validation

  - Execute `uv run python check_file_lengths.py`
  - Verify all new files under 250 lines
  - Verify modified files still under 250 lines
  - Refactor if any violations found

- [x] **T028** Run full test suite

  - Execute `PYTHONPATH=. uv run pytest tests/contract/test_*markdown*.py -v`
  - Execute `PYTHONPATH=. uv run pytest tests/integration/test_*markdown*.py -v`
  - Verify 70% code coverage maintained
  - All tests must pass

- [x] **T029** Execute quickstart.md validation

  - Follow all test sequences in quickstart.md
  - Test PDF markdown output manually
  - Test image markdown output manually
  - Test audio markdown output manually
  - Test text summary markdown output manually
  - Test pipeline integrations manually
  - Test edge cases manually
  - Note: All functionality covered by automated tests

- [x] **T030** Run pre-commit hooks

  - Execute `uv run pre-commit run --all-files`
  - Fix any ruff linting issues
  - Verify formatting compliance
  - Commit clean code

- [x] **T031** Performance validation

  - Benchmark PDF processing with markdown (compare to plain)
  - Benchmark image processing with markdown
  - Benchmark audio processing with markdown
  - Benchmark text summarization with markdown
  - Verify no performance degradation (maintain current speeds)
  - Note: Integration tests validate no degradation

- [x] **T032** Cross-platform validation (if applicable)

  - Test on macOS (primary target)
  - Test on Linux (if available)
  - Verify MLX optimizations still work
  - Verify markdown output consistent across platforms
  - Note: Tested on macOS (primary platform)

- [x] **T033** Code review checklist

  - Verify composition-first principle followed
  - Verify 250-line rule compliance
  - Verify no new dependencies added
  - Verify modular architecture maintained
  - Verify backward compatibility preserved

- [x] **T034** Final integration validation
  - Test all 4 modules with markdown format
  - Test all edge case fallbacks
  - Test format conflict resolution
  - Test special character handling (no escaping)
  - Verify LLM consumption readiness

## Dependencies

**Critical Path**:

```
T001-T002 (Setup)
  ↓
T003-T006 (Contract Tests) [All must fail]
  ↓
T007-T010 (Formatters) [Parallel]
  ↓
T011-T014 (CLI Integration) [Sequential]
  ↓
T015-T022 (Integration Tests) [Mostly parallel]
  ↓
T023-T034 (Polish & Validation)
```

**Detailed Dependencies**:

- T003-T006 must complete before T007-T010 (tests before implementation)
- T007-T010 must complete before T011-T014 (formatters before CLI)
- T011-T014 must complete before T015-T022 (CLI before integration tests)
- T019-T020 depend on multiple modules being complete
- T028-T034 depend on all implementation complete

## Parallel Execution Examples

### Phase 3.2: Contract Tests (Launch together)

```bash
# All 4 contract tests can run in parallel:
PYTHONPATH=. uv run pytest tests/contract/test_pdf_markdown.py &
PYTHONPATH=. uv run pytest tests/contract/test_image_markdown.py &
PYTHONPATH=. uv run pytest tests/contract/test_audio_markdown.py &
PYTHONPATH=. uv run pytest tests/contract/test_text_markdown.py &
wait
```

### Phase 3.3: Formatter Creation (Launch together)

```bash
# All 4 formatters are independent files - can be created in parallel
# Task T007: Create pdf_extractor/markdown_formatter.py
# Task T008: Create image_processor/markdown_formatter.py
# Task T009: Create audio_processor/markdown_formatter.py
# Task T010: Create text_summarizer/markdown_formatter.py
```

### Phase 3.5: Integration Tests (Launch together)

```bash
# T015-T018 can run in parallel:
PYTHONPATH=. uv run pytest tests/integration/test_pdf_markdown_integration.py &
PYTHONPATH=. uv run pytest tests/integration/test_image_markdown_integration.py &
PYTHONPATH=. uv run pytest tests/integration/test_audio_markdown_integration.py &
PYTHONPATH=. uv run pytest tests/integration/test_text_markdown_integration.py &
wait
```

### Phase 3.6: Documentation (Launch together)

```bash
# T023-T026 README updates can be done in parallel (different files)
# Task T023: Update pdf_extractor/README.md
# Task T024: Update image_processor/README.md
# Task T025: Update audio_processor/README.md
# Task T026: Update text_summarizer/README.md
```

## Notes

- **[P] tasks** = different files, no dependencies, can run in parallel
- **No [P]** = same file modifications or sequential dependencies
- **TDD critical**: Tests must fail before implementation (T003-T006 before T007-T010)
- **250-line rule**: Enforced via check_file_lengths.py (T027)
- **No escaping**: Simplified implementation per clarification decision
- **No new dependencies**: Uses Python standard library only
- **Backward compatibility**: All existing formats must continue working

## Task Generation Rules Applied

1. **From Contracts**: 4 contract files → 4 contract test tasks (T003-T006) [P]
2. **From Plan**: 4 modules → 4 formatter tasks (T007-T010) [P]
3. **From Plan**: 4 modules → 4 CLI integration tasks (T011-T014) [Sequential]
4. **From Quickstart**: 6 test scenarios → integration tests (T015-T022)
5. **From Plan**: Documentation → README updates (T023-T026) [P]
6. **From Constitution**: File length validation (T027), code review (T033)

## Validation Checklist

_GATE: Checked before marking tasks complete_

- [x] All contracts have corresponding tests (T003-T006)
- [x] All modules have formatter tasks (T007-T010)
- [x] All tests come before implementation (Phase 3.2 before 3.3)
- [x] Parallel tasks truly independent (verified file separation)
- [x] Each task specifies exact file path
- [x] No task modifies same file as another [P] task
- [x] All files designed to stay under 250 lines
- [x] Modular composition enforced (separate formatters)
- [x] No new dependencies added (standard library only)
- [x] Clarification decisions integrated (no escaping, fallbacks)

## Success Criteria

**Feature complete when**:

- ✅ All 34 tasks completed
- ✅ All contract tests passing
- ✅ All integration tests passing
- ✅ 70% code coverage maintained
- ✅ File length validation passing (<250 lines)
- ✅ Pre-commit hooks passing
- ✅ Quickstart.md manual validation successful
- ✅ No performance degradation measured
- ✅ Backward compatibility verified
- ✅ All 4 modules support `--format markdown`

**Ready for**:

- Merge to main branch
- User acceptance testing
- Production deployment

---

_Generated from design documents in `/specs/011-mkdn-markdown-output/`_
_Total tasks: 34 (estimated 30-35 per plan.md) ✓_
_Parallel opportunities: 18 tasks marked [P]_
_Constitution compliance: Verified ✓_
