# Quickstart: Metadata Dictionary for Result Models

**Feature**: 015-extend-all-result
**Date**: 2025-10-25

---

## Prerequisites

- Python 3.11+
- anyfile_to_ai package installed with all dependencies
- Sample files: PDF, image (JPEG with EXIF), audio (MP3), text file

---

## Quick Test Commands

### 1. PDF Extractor with Metadata

```bash
# Create test PDF (or use existing)
echo "Sample PDF test" > test.txt

# Extract with metadata
uv run python -m pdf_extractor extract test.pdf --format json --include-metadata
```

**Expected Output**:
```json
{
  "success": true,
  "metadata": {
    "processing": {
      "timestamp": "2025-10-25T...",
      "model_version": "pdfplumber-0.11.7",
      "processing_time_seconds": 0.5
    },
    "source": {
      "file_path": "test.pdf",
      "file_size_bytes": 12345,
      "page_count": 1
    }
  }
}
```

---

### 2. Image Processor with Metadata

```bash
# Process image with EXIF data
uv run python -m image_processor photo.jpg --format json --include-metadata
```

**Expected Output**:
```json
{
  "success": true,
  "metadata": {
    "processing": {
      "timestamp": "2025-10-25T...",
      "model_version": "mlx-community/gemma-3-4b"
    },
    "source": {
      "file_path": "photo.jpg",
      "dimensions": {"width": 1920, "height": 1080},
      "exif": {
        "Make": "Canon",
        "Model": "EOS 5D"
      }
    }
  }
}
```

---

### 3. Audio Processor with Metadata

```bash
# Transcribe audio with metadata
uv run python -m audio_processor podcast.mp3 --format json --include-metadata
```

**Expected Output**:
```json
{
  "success": true,
  "metadata": {
    "processing": {
      "timestamp": "2025-10-25T...",
      "model_version": "lightning-whisper-mlx-medium"
    },
    "source": {
      "duration_seconds": 180.5,
      "sample_rate_hz": 44100,
      "detected_language": "en",
      "language_confidence": 0.95
    }
  }
}
```

---

### 4. Text Summarizer with Metadata

```bash
# Summarize text with metadata (default enabled)
uv run python -m text_summarizer article.txt --format json
```

**Expected Output**:
```json
{
  "summary": "...",
  "tags": ["AI", "technology"],
  "metadata": {
    "input_length": 5000,
    "processing_timestamp": "2025-10-25T...",
    "model_version": "llama2",
    "source": {
      "file_path": "article.txt",
      "input_length_words": 5000
    }
  }
}
```

---

## Validation Checklist

### ✅ Metadata Disabled (Backward Compatibility)

```bash
# PDF without metadata
uv run python -m pdf_extractor extract test.pdf --format json
# Assert: "metadata": null

# Image without metadata
uv run python -m image_processor photo.jpg --format json
# Assert: "metadata": null

# Audio without metadata
uv run python -m audio_processor audio.mp3 --format json
# Assert: "metadata": null

# Text without metadata
uv run python -m text_summarizer article.txt --format json --no-metadata
# Assert: "metadata": null
```

### ✅ Metadata Enabled

```bash
# All modules with --include-metadata
uv run python -m pdf_extractor extract test.pdf --format json --include-metadata
uv run python -m image_processor photo.jpg --format json --include-metadata
uv run python -m audio_processor audio.mp3 --format json --include-metadata
uv run python -m text_summarizer article.txt --format json  # Already enabled by default

# Assert each output contains:
# - metadata.processing.timestamp (ISO 8601)
# - metadata.processing.model_version
# - metadata.configuration (user_provided + effective)
# - metadata.source (type-specific fields)
```

### ✅ Unavailable Fields Handling

```bash
# Test with file missing metadata
uv run python -m pdf_extractor extract generated.pdf --format json --include-metadata
# Assert: creation_date = "unavailable" if not in PDF metadata

# Test with image without EXIF
uv run python -m image_processor screenshot.png --format json --include-metadata
# Assert: exif = {} (empty dict)

# Test with stdin input
cat article.txt | uv run python -m text_summarizer --stdin --format json
# Assert: source.file_path = "unavailable"
```

### ✅ Timestamp Format Validation

```bash
# Check all outputs have ISO 8601 timestamps
uv run python -m pdf_extractor extract test.pdf --format json --include-metadata | jq '.metadata.processing.timestamp'
# Expected format: "2025-10-25T14:30:00+00:00"
```

### ✅ Configuration Metadata

```bash
# Run with specific flags
uv run python -m audio_processor audio.mp3 --model medium --language en --include-metadata --format json

# Assert metadata.configuration:
# {
#   "user_provided": {"model": "medium", "language": "en"},
#   "effective": {"model": "medium", "language": "en", "quantization": "none", ...}
# }
```

### ✅ Format Preservation

```bash
# Test metadata in different output formats
uv run python -m pdf_extractor extract test.pdf --format json --include-metadata
uv run python -m pdf_extractor extract test.pdf --format markdown --include-metadata
uv run python -m image_processor photo.jpg --format csv --include-metadata

# Assert:
# - JSON: nested metadata object
# - Markdown: YAML frontmatter or metadata section
# - CSV: flattened metadata columns
```

---

## Integration Test Scenarios

### Scenario 1: PDF with Full Metadata

```bash
# Process PDF with all metadata fields available
uv run python -m pdf_extractor extract document.pdf --format json --include-metadata > output.json

# Validate:
python -c "
import json
with open('output.json') as f:
    data = json.load(f)
    assert 'metadata' in data
    assert 'processing' in data['metadata']
    assert 'timestamp' in data['metadata']['processing']
    assert 'source' in data['metadata']
    assert data['metadata']['source']['page_count'] > 0
    print('✅ PDF metadata validation passed')
"
```

### Scenario 2: Image with EXIF Data

```bash
# Process JPEG with EXIF
uv run python -m image_processor photo.jpg --format json --include-metadata > output.json

# Validate EXIF extraction
python -c "
import json
with open('output.json') as f:
    data = json.load(f)
    assert 'metadata' in data
    exif = data['metadata']['source']['exif']
    assert isinstance(exif, dict)
    print(f'✅ EXIF tags extracted: {len(exif)} tags')
"
```

### Scenario 3: Audio Language Confidence

```bash
# Transcribe audio with language detection
uv run python -m audio_processor podcast.mp3 --format json --include-metadata > output.json

# Validate language confidence
python -c "
import json
with open('output.json') as f:
    data = json.load(f)
    confidence = data['metadata']['source']['language_confidence']
    assert isinstance(confidence, (float, str))
    if isinstance(confidence, float):
        assert 0.0 <= confidence <= 1.0
    print(f'✅ Language confidence: {confidence}')
"
```

### Scenario 4: Text Summarizer Backward Compatibility

```bash
# Verify existing metadata fields preserved
uv run python -m text_summarizer article.txt --format json > output.json

# Validate backward compatibility
python -c "
import json
with open('output.json') as f:
    data = json.load(f)
    meta = data['metadata']
    # Existing fields must be present
    assert 'input_length' in meta
    assert 'chunked' in meta
    assert 'processing_time' in meta
    # New fields added
    assert 'processing_timestamp' in meta
    assert 'model_version' in meta
    print('✅ Backward compatibility maintained')
"
```

---

## Pipeline Testing

### PDF → Summarizer with Metadata

```bash
# Extract and summarize with metadata preservation
uv run python -m pdf_extractor extract document.pdf --format plain --include-metadata | \
  uv run python -m text_summarizer --stdin --format json

# Validate:
# - PDF metadata extracted (source.file_path available)
# - Summary metadata shows stdin source (file_path = "unavailable")
```

### Audio → Summarizer with Metadata

```bash
# Transcribe and summarize
uv run python -m audio_processor podcast.mp3 --format plain --include-metadata | \
  uv run python -m text_summarizer --stdin --format json

# Validate:
# - Audio metadata extracted
# - Transcription text passed to summarizer
# - Summary metadata shows stdin source
```

---

## Performance Validation

### Metadata Overhead Test

```bash
# Run with metadata disabled (baseline)
time uv run python -m pdf_extractor extract large.pdf --format json

# Run with metadata enabled
time uv run python -m pdf_extractor extract large.pdf --format json --include-metadata

# Expected: Metadata extraction adds <1% overhead
```

---

## Error Handling Tests

### Missing File with Metadata

```bash
# Test error handling with metadata enabled
uv run python -m pdf_extractor extract missing.pdf --format json --include-metadata

# Expected: Error message + attempt to extract available metadata
```

### Corrupted File with Metadata

```bash
# Test with corrupted file
uv run python -m image_processor corrupted.jpg --format json --include-metadata

# Expected: Error + partial metadata (file_size available, dimensions "unavailable")
```

---

## Success Criteria

All tests pass with the following validations:

1. ✅ **Backward Compatibility**: Metadata disabled by default (except text_summarizer), existing output unchanged
2. ✅ **Metadata Structure**: All modules use consistent processing/configuration/source schema
3. ✅ **Unavailable Handling**: Missing fields set to "unavailable" or empty dict (not omitted)
4. ✅ **Timestamp Format**: All timestamps in ISO 8601 with timezone
5. ✅ **Configuration Metadata**: Both user_provided and effective config included
6. ✅ **Type-Specific Fields**: PDF (page_count), Image (EXIF), Audio (language_confidence), Text (chunked)
7. ✅ **Format Preservation**: Metadata included in JSON, markdown, CSV outputs
8. ✅ **Pipeline Support**: Metadata works in chained processing workflows
9. ✅ **Performance**: Metadata extraction adds <1% overhead
10. ✅ **Error Handling**: Partial metadata extracted even on errors

---

## Manual Verification

### Visual Check: Markdown Output

```bash
# Generate markdown with metadata for human review
uv run python -m image_processor photo.jpg --format markdown --include-metadata
```

Expected output should include:
- YAML frontmatter with key metadata
- Metadata section with processing, source, EXIF details
- Human-readable formatting

### Visual Check: CSV Output

```bash
# Generate CSV with flattened metadata
uv run python -m pdf_extractor extract test.pdf --format csv --include-metadata
```

Expected output should include:
- Flattened metadata columns (metadata.processing.timestamp, metadata.source.file_size_bytes)
- Consistent field order

---

## Next Steps

After quickstart validation:
1. Run contract tests (`pytest tests/contract/test_metadata_*.py`)
2. Run integration tests (`pytest tests/integration/test_*_metadata_*.py`)
3. Run full test suite (`uv run pytest`)
4. Verify linting passes (`uv run ruff check .`)
5. Check test coverage (`pytest --cov`)

---

**Status**: Ready for implementation and testing
