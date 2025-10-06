# Research: Markdown Output Format Support

**Feature**: 011-mkdn-markdown-output
**Date**: 2025-10-02
**Phase**: 0 - Research

## Research Tasks Completed

### 1. Markdown Syntax Standards

**Decision**: Use CommonMark specification as baseline, with GitHub Flavored Markdown extensions

**Rationale**:
- CommonMark is well-specified, unambiguous standard
- GFM adds practical features (tables, task lists) without breaking compatibility
- Both are widely supported by markdown processors and LLMs

**Syntax Reference**:
```markdown
# Heading 1 (document title)
## Heading 2 (major sections)
### Heading 3 (subsections)

- Unordered list item
* Alternative bullet style
+ Another alternative

1. Ordered list
2. Second item

![Alt text](image_path.jpg)

`inline code`

```
code block
```
```

**Escaping Rules**:
Characters that need escaping in markdown text: `* _ [ ] ( ) # + - . ! \ | { }`

**Alternatives Considered**:
- Plain Markdown (too loose, inconsistent rendering)
- Strict CommonMark only (lacks tables, limiting for structured data)
- Custom markdown dialect (unnecessary complexity)

### 2. PDF Structure Detection

**Decision**: Use heuristic-based structure detection with conservative fallbacks

**Rationale**:
- PDFs don't contain semantic structure metadata
- Font size and style changes indicate heading hierarchy
- Better to under-detect than over-detect (fewer false positives)
- Simple paragraphs work when structure detection fails

**Detection Methods**:

1. **Heading Detection**:
   - Font size > 1.2x body text → heading candidate
   - Bold text at line start → potential heading
   - Short lines (<60 chars) with size/weight changes → heading
   - Heading levels: largest = H1, medium = H2, smaller = H3

2. **List Detection**:
   - Lines starting with bullet characters (•, -, *, ◦)
   - Lines starting with numbers followed by period/parenthesis
   - Indented continuation lines belong to previous item

3. **Paragraph Detection**:
   - Regular text blocks without special formatting
   - Preserve line breaks between paragraphs
   - Avoid breaking mid-sentence

4. **Table Detection**:
   - Use pdfplumber's table detection
   - Convert to markdown tables if structure is clear
   - Fall back to plain text if ambiguous

**Conservative Approach**:
- If uncertain about structure, output as plain text
- Add markers only when confident (>80% certainty based on formatting)
- Prefer false negatives over false positives

**Alternatives Considered**:
- ML-based structure detection (overkill, dependency-heavy)
- Manual structure annotation (not automated)
- MarkItDown's approach (external dependency, we want to learn)

### 3. Markdown for LLM Consumption

**Decision**: Optimize for semantic clarity, not token count

**Rationale**:
- Modern LLMs handle markdown well natively
- Clear structure helps LLM understanding more than token savings
- Human readability and LLM processing are aligned goals

**Best Practices**:

1. **Heading Hierarchy**:
   - Use clear hierarchy (# > ## > ###)
   - Max 3 levels deep for most documents
   - Document title always H1, sections H2, subsections H3

2. **Image Captions**:
   - Use alt text for VLM descriptions: `![VLM description](path)`
   - Follow with paragraph description if detailed
   - Example:
     ```markdown
     ![A red car on a highway at sunset](image.jpg)

     The image shows a vintage red sports car...
     ```

3. **Timestamp Formatting**:
   - Use consistent format: `[HH:MM:SS]` or `**HH:MM:SS**`
   - Place at start of paragraph or heading
   - Example:
     ```markdown
     ## [00:05:23] Speaker 1

     The main point I want to make is...
     ```

4. **Metadata Placement**:
   - Front matter for document metadata (if needed)
   - Footer for processing metadata
   - Use horizontal rules to separate: `---`

5. **Token Efficiency**:
   - Avoid excessive blank lines (1 blank line between sections max)
   - Use concise headings
   - But prioritize clarity over brevity

**Alternatives Considered**:
- HTML output (more complex, less LLM-friendly)
- Custom structured format (not standard, requires parsing)
- Minimal markdown (loses semantic structure)

### 4. Character Escaping

**Decision**: No escaping of markdown special characters (clarified 2025-10-02)

**Rationale**:
- Modern markdown processors handle raw text appropriately
- Avoids complexity of context-aware escaping logic
- Prevents over-escaping and readability issues
- Content text (VLM descriptions, transcriptions) kept natural
- Aligns with simplicity principle from constitution

**Implementation Strategy**:

1. **No Character Escaping**:
   - Output content as-is without modification
   - Rely on markdown processors to handle special characters
   - Special chars in user content: `* _ [ ] ( ) # + - . ! \` are left unescaped

2. **Justification**:
   - Most markdown processors treat text content safely
   - Edge cases (like `*word*` becoming italic) are acceptable
   - Simpler implementation with fewer bugs
   - Better aligns with "no new dependencies" principle

3. **Known Limitations**:
   - Some content may render with unintended formatting
   - URLs with special chars work correctly in markdown
   - Structure markers we generate (headings) are controlled and safe

**Alternatives Considered**:
- Selective escaping in content only (added complexity, rejected)
- HTML entity encoding (not markdown-standard, rejected)
- Aggressive escaping all chars (creates unreadable output, rejected)

### 5. Module Consistency Patterns

**Decision**: Use consistent document structure across all modules

**Rationale**:
- Users expect consistent output format
- LLMs benefit from predictable structure
- Easier to chain modules in pipelines

**Common Structure**:

```markdown
# {Document Type}: {Filename}

{Optional metadata as list}

## {Section or Content Type}

{Content}

---

*Processed by {module_name} | {timestamp}*
```

**Module-Specific Patterns**:

1. **PDF Extractor**:
   ```markdown
   # PDF Document: filename.pdf

   ## Page 1

   {detected structure with headings/lists}

   ## Page 2

   {content}
   ```

2. **Image Processor**:
   ```markdown
   # Image Descriptions

   ## image1.jpg

   ![Description of image1](image1.jpg)

   {Detailed VLM description}

   ## image2.jpg

   ![Description of image2](image2.jpg)

   {Detailed VLM description}
   ```

3. **Audio Processor**:
   ```markdown
   # Transcription: audio_file.mp3

   - Duration: 05:23
   - Model: whisper-large-v3
   - Language: en

   ## [00:00:00] Speaker 1

   {Transcript text}

   ## [00:01:30] Speaker 2

   {Transcript text}
   ```

4. **Text Summarizer**:
   ```markdown
   # Summary

   {Summary text with natural paragraphs}

   ## Tags

   - tag1
   - tag2
   - tag3
   ```

**Error State Representation**:
When processing fails partially:
```markdown
# {Document Type}: {Filename}

## Error

⚠️ Processing failed: {error message}

{Partial results if available}
```

**Streaming Markdown**:
- Each chunk must be valid markdown
- Use section boundaries for chunk splits
- Ensure closing markers before stream ends

**Alternatives Considered**:
- Module-specific inconsistent formats (harder to chain)
- Single flat structure (loses semantic information)
- JSON embedded in markdown (mixing concerns)

## Technology Decisions

### Dependencies
- **No new dependencies required**
- Use Python standard library for all markdown generation
- String formatting for template generation
- No regex needed (no escaping)

### Shared Utilities Module
- **Location**: `markdown_utils/` at repository root (optional)
- **Components**:
  - `structure.py`: Heading generation, list formatting helpers
  - `__init__.py`: Public API exports
- **Design**: Pure functions, no state, composable
- **Note**: Escaping utilities removed based on clarification decision (no escaping needed)

### Integration Points
- Each module gets `markdown_formatter.py` file
- CLI adds `markdown` choice to existing `--format` argument
- Formatters called from output handling logic
- No changes to core processing logic

## Open Questions Resolved

1. **Q**: Should we use YAML front matter for metadata?
   **A**: No, use simple list format. More readable, less parsing complexity.

2. **Q**: How to handle images in PDFs?
   **A**: Reference by page and position: `Image on page 3: {description}`

3. **Q**: Should audio timestamps be headings or inline?
   **A**: Headings (H2) for better structure and navigation.

4. **Q**: What if PDF structure detection fails?
   **A**: Output as plain text paragraphs, still valid markdown. (Clarified 2025-10-02)

5. **Q**: Should we validate markdown syntax?
   **A**: Not initially. Keep formatters simple. Add validation in tests.

6. **Q**: What happens when images fail VLM processing? (Clarified 2025-10-02)
   **A**: Output markdown with generic fallback: `![Image](image.jpg)` with "Description unavailable" text.

7. **Q**: What markdown format for audio with no speakers/timestamps? (Clarified 2025-10-02)
   **A**: Output transcript as plain paragraphs without speaker headers.

8. **Q**: Should we escape markdown special characters? (Clarified 2025-10-02)
   **A**: No escaping. Rely on markdown processors to handle raw text.

9. **Q**: What happens with multiple format flags? (Clarified 2025-10-02)
   **A**: Use last specified format (rightmost wins).

## Next Steps

Ready for Phase 1: Design & Contracts

- Create data model definitions
- Write API contracts for each module
- Generate contract tests
- Update CLAUDE.md with new commands

---

*Research completed: 2025-10-02*
