# API Contract: PDF Extractor with Metadata

**Module**: `anyfile_to_ai.pdf_extractor`
**Version**: 0.2.0 (with metadata support)

---

## CLI Interface

### Command

```bash
uv run python -m pdf_extractor extract <pdf_file> [OPTIONS]
```

### New Options

```
--include-metadata    Include source file and processing metadata in output
```

### Examples

```bash
# Extract with metadata (JSON output)
uv run python -m pdf_extractor extract document.pdf --format json --include-metadata

# Extract with metadata (markdown output)
uv run python -m pdf_extractor extract document.pdf --format markdown --include-metadata

# Extract without metadata (backward compatible)
uv run python -m pdf_extractor extract document.pdf --format json
```

---

## Data Model Changes

### ExtractionResult Extension

```python
@dataclass
class ExtractionResult:
    success: bool
    pages: list[PageResult]
    total_pages: int
    total_chars: int
    processing_time: float
    error_message: str | None = None
    metadata: dict | None = None  # NEW: Optional metadata
```

### Metadata Structure (when enabled)

```python
{
    "processing": {
        "timestamp": "2025-10-25T14:30:00+00:00",
        "model_version": "pdfplumber-0.11.7",
        "processing_time_seconds": 2.5
    },
    "configuration": {
        "user_provided": {
            "format": "json",
            "stream": false
        },
        "effective": {
            "format": "json",
            "stream": false,
            "progress": true
        }
    },
    "source": {
        "file_path": "/path/to/document.pdf",
        "file_size_bytes": 1234567,
        "page_count": 10,
        "creation_date": "2025-01-15T09:30:00+00:00",
        "modification_date": "unavailable",
        "author": "unavailable",
        "title": "Sample Document"
    }
}
```

---

## JSON Output Contract

### With Metadata Enabled

```json
{
  "success": true,
  "pages": [
    {
      "page_number": 1,
      "text": "Page content...",
      "char_count": 500,
      "extraction_time": 0.25
    }
  ],
  "total_pages": 10,
  "total_chars": 5000,
  "processing_time": 2.5,
  "error_message": null,
  "metadata": {
    "processing": {
      "timestamp": "2025-10-25T14:30:00+00:00",
      "model_version": "pdfplumber-0.11.7",
      "processing_time_seconds": 2.5
    },
    "configuration": {
      "user_provided": {"format": "json"},
      "effective": {"format": "json", "stream": false, "progress": true}
    },
    "source": {
      "file_path": "/path/to/document.pdf",
      "file_size_bytes": 1234567,
      "page_count": 10,
      "creation_date": "2025-01-15T09:30:00+00:00"
    }
  }
}
```

### Without Metadata (Default)

```json
{
  "success": true,
  "pages": [...],
  "total_pages": 10,
  "total_chars": 5000,
  "processing_time": 2.5,
  "error_message": null,
  "metadata": null
}
```

---

## Markdown Output Contract

### With Metadata Enabled

```markdown
---
processing_timestamp: 2025-10-25T14:30:00+00:00
model_version: pdfplumber-0.11.7
file_path: /path/to/document.pdf
page_count: 10
file_size_bytes: 1234567
---

# PDF Extraction Result

## Page 1

Page content...

## Page 2

...

---

## Metadata

- **Processing Time**: 2.5s
- **Pages**: 10
- **File Size**: 1.2 MB
- **Creation Date**: 2025-01-15
```

---

## Contract Tests

### Test Scenarios

1. **Metadata disabled (default)**:
   - Run without `--include-metadata`
   - Assert `result.metadata is None`
   - Assert output JSON does not contain metadata key

2. **Metadata enabled**:
   - Run with `--include-metadata`
   - Assert `result.metadata is not None`
   - Assert metadata contains processing, configuration, source keys

3. **Metadata schema validation**:
   - Validate metadata against JSON schema
   - Assert timestamp is ISO 8601 format
   - Assert file_size_bytes is integer or "unavailable"

4. **Unavailable fields handling**:
   - Test with PDF lacking creation date
   - Assert creation_date = "unavailable"
   - Assert schema remains consistent

5. **Configuration metadata**:
   - Run with specific flags (--format json --stream)
   - Assert user_provided contains specified flags
   - Assert effective contains all config with defaults

---

## Backward Compatibility

✅ **Fully backward compatible**:
- Default behavior unchanged (metadata disabled)
- Existing JSON/plain/markdown output formats preserved
- No breaking changes to API or data models
- New field is optional (metadata: dict | None = None)

---

## Error Handling

### Missing File

```json
{
  "success": false,
  "error_message": "File not found: document.pdf",
  "metadata": null
}
```

### Corrupted PDF (with metadata enabled)

```json
{
  "success": false,
  "error_message": "Failed to parse PDF",
  "metadata": {
    "processing": {
      "timestamp": "2025-10-25T14:30:00+00:00",
      "model_version": "pdfplumber-0.11.7",
      "processing_time_seconds": 0.1
    },
    "source": {
      "file_path": "/path/to/corrupted.pdf",
      "file_size_bytes": "unavailable",
      "page_count": "unavailable",
      "creation_date": "unavailable"
    }
  }
}
```

Note: Even on failure, attempt to extract available metadata

---

**Contract Version**: 1.0
**Schema**: [metadata-schema.json](./metadata-schema.json)
