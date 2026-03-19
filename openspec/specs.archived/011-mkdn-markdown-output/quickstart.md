# Quickstart: Markdown Output Format

**Feature**: 011-mkdn-markdown-output
**Purpose**: Validate markdown output implementation across all modules
**Expected Duration**: 5-10 minutes

## Prerequisites

1. Ensure you're on branch: `011-mkdn-markdown-output`
2. All modules implemented with markdown formatter
3. Test files available in `sample-data/`

## Setup

```bash
# Ensure you're on the correct branch
git checkout 011-mkdn-markdown-output

# Install/update dependencies (if any were added)
uv sync

# Verify tests pass
PYTHONPATH=. uv run pytest tests/contract/test_*markdown*.py -v
```

## Test Sequence

### 1. PDF Markdown Output

**Test**: Extract PDF with markdown format

```bash
# Create a test PDF if needed
echo "Test content" > test_quickstart.txt

# Extract PDF as markdown
uv run python -m pdf_extractor sample-data/test.pdf --format markdown

# Verify output structure
uv run python -m pdf_extractor sample-data/test.pdf --format markdown | head -5
```

**Expected Output**:
```markdown
# PDF Document: test.pdf

## Page 1

{content}
```

**Validation Checklist**:
- [ ] Output starts with `# PDF Document:`
- [ ] Contains `## Page` sections
- [ ] Text content is readable
- [ ] No unescaped markdown special characters in content

### 2. Image Markdown Output

**Test**: Process image with markdown format

```bash
# Set VLM environment variable (if not already set)
export VISION_MODEL=mlx-community/gemma-3-4b-it-4bit

# Process image as markdown
uv run python -m image_processor test_image.jpg --format markdown

# Process multiple images
uv run python -m image_processor sample-data/images/*.jpg --format markdown
```

**Expected Output**:
```markdown
# Image Descriptions

## test_image.jpg

![VLM generated description](test_image.jpg)

{Detailed description paragraph}
```

**Validation Checklist**:
- [ ] Output starts with `# Image Descriptions`
- [ ] Each image has `## {filename}` section
- [ ] Contains `![...](...)` markdown image syntax
- [ ] VLM descriptions are present and meaningful

### 3. Audio Markdown Output

**Test**: Transcribe audio with markdown format

```bash
# Transcribe audio as markdown
uv run python -m audio_processor sample-data/audio/test.mp3 --format markdown

# Check first few lines
uv run python -m audio_processor sample-data/audio/test.mp3 --format markdown | head -10
```

**Expected Output**:
```markdown
# Transcription: test.mp3

- Duration: 00:05:23
- Model: whisper-large-v3
- Language: en

## [00:00:00] Speaker 1

{Transcript text}
```

**Validation Checklist**:
- [ ] Output starts with `# Transcription:`
- [ ] Metadata section present (Duration, Model, Language)
- [ ] Timestamps in format `[HH:MM:SS]`
- [ ] Transcript text is accurate

### 4. Text Summary Markdown Output

**Test**: Summarize text with markdown format

```bash
# Summarize a text file as markdown
uv run python -m text_summarizer sample-data/text/article.txt --format markdown

# Test stdin pipeline
echo "This is a test article about markdown formatting in document processing." | \
  uv run python -m text_summarizer --stdin --format markdown
```

**Expected Output**:
```markdown
# Summary

{Summary paragraph(s)}

## Tags

- tag1
- tag2
- tag3
```

**Validation Checklist**:
- [ ] Output starts with `# Summary`
- [ ] Summary text is coherent
- [ ] Contains `## Tags` section
- [ ] Tags formatted as bullet list

### 5. Pipeline Integration

**Test**: Chain modules with markdown format

```bash
# PDF → Text Summarizer
uv run python -m pdf_extractor sample-data/test.pdf --format plain | \
  uv run python -m text_summarizer --stdin --format markdown

# Audio → Text Summarizer
uv run python -m audio_processor sample-data/audio/test.mp3 --format plain | \
  uv run python -m text_summarizer --stdin --format markdown

# Verify markdown is valid (using basic check)
uv run python -m pdf_extractor sample-data/test.pdf --format markdown > /tmp/test_output.md
cat /tmp/test_output.md
```

**Expected Behavior**:
- [ ] Plain text output pipes correctly to text_summarizer
- [ ] Markdown output from each module is valid
- [ ] Pipeline produces expected results

### 6. Edge Cases

**Test**: Handle special characters and errors

```bash
# Test with file containing markdown special characters
echo "Test with *asterisks* and [brackets] and #hashtags" > /tmp/special_chars.txt
uv run python -m text_summarizer /tmp/special_chars.txt --format markdown

# Test with non-existent file (should error gracefully)
uv run python -m pdf_extractor nonexistent.pdf --format markdown

# Test with empty input
echo "" | uv run python -m text_summarizer --stdin --format markdown
```

**Expected Behavior**:
- [ ] Special characters properly escaped in output
- [ ] Errors produce markdown-formatted error messages
- [ ] Empty input handled gracefully

## Validation

### Automated Tests

```bash
# Run all markdown contract tests
PYTHONPATH=. uv run pytest tests/contract/test_pdf_markdown.py -v
PYTHONPATH=. uv run pytest tests/contract/test_image_markdown.py -v
PYTHONPATH=. uv run pytest tests/contract/test_audio_markdown.py -v
PYTHONPATH=. uv run pytest tests/contract/test_text_markdown.py -v

# Run integration tests
PYTHONPATH=. uv run pytest tests/integration/test_*markdown*.py -v

# Check coverage
PYTHONPATH=. uv run pytest --cov=markdown_utils --cov=pdf_extractor --cov=image_processor --cov=audio_processor --cov=text_summarizer --cov-report=term-missing
```

**Expected Results**:
- [ ] All contract tests pass
- [ ] All integration tests pass
- [ ] Code coverage >= 70%

### Manual Validation

1. **Markdown Syntax Validation**:
   ```bash
   # Save markdown output to file
   uv run python -m pdf_extractor sample-data/test.pdf --format markdown > output.md

   # View in markdown renderer (e.g., cat, less, or open in editor)
   cat output.md
   ```

2. **LLM Consumption Test**:
   ```bash
   # Feed markdown to LLM via text_summarizer
   uv run python -m pdf_extractor sample-data/test.pdf --format markdown | \
     uv run python -m text_summarizer --stdin --format plain
   ```

3. **Cross-Module Consistency**:
   - Compare markdown structure across different modules
   - Verify heading levels are consistent
   - Check that all use same escaping rules

## Success Criteria

All of the following must be true:

- [ ] All 4 modules support `--format markdown` flag
- [ ] All contract tests pass
- [ ] All integration tests pass
- [ ] Markdown output is syntactically valid
- [ ] Special characters properly escaped
- [ ] Structure preserved from source documents
- [ ] Backward compatibility maintained (other formats still work)
- [ ] Code coverage >= 70%
- [ ] No file exceeds 250 lines
- [ ] Documentation updated (module READMEs, CLAUDE.md)

## Troubleshooting

### Issue: VLM model not found
**Solution**: Ensure VISION_MODEL env var is set correctly
```bash
export VISION_MODEL=mlx-community/gemma-3-4b-it-4bit
```

### Issue: Markdown output has escaped backslashes
**Solution**: Check for double-escaping in formatter code

### Issue: Tests fail with "module not found"
**Solution**: Ensure PYTHONPATH is set
```bash
export PYTHONPATH=.
# or
PYTHONPATH=. uv run pytest ...
```

### Issue: File length violations
**Solution**: Split large formatter files
```bash
# Check file lengths
uv run python check_file_lengths.py
```

## Cleanup

```bash
# Remove temporary test files
rm -f /tmp/test_output.md /tmp/special_chars.txt test_quickstart.txt

# Ensure branch is clean
git status
```

## Next Steps

After successful quickstart validation:

1. Update module READMEs with markdown examples
2. Update CLAUDE.md with markdown commands
3. Create PR for feature branch
4. Document any learnings or gotchas

---

**Validation Date**: _____________
**Validated By**: _____________
**Result**: ☐ PASS  ☐ FAIL

**Notes**:
