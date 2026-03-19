# Research: Metadata Dictionary for Result Models

**Feature**: 015-extend-all-result
**Date**: 2025-10-25
**Status**: Complete

## Research Questions

### 1. ISO 8601 Timestamp Formatting

**Question**: What is the best approach for ISO 8601 timestamp formatting with timezone in Python?

**Decision**: Use `datetime.now(timezone.utc).isoformat()` for processing timestamps

**Rationale**:
- ISO 8601 format is internationally recognized and unambiguous
- `isoformat()` produces standard format: "2025-10-25T14:30:00+00:00"
- `timezone.utc` ensures consistent timezone handling across platforms
- No external dependencies (stdlib datetime module)
- Parse-friendly for downstream consumers

**Alternatives Considered**:
- `strftime('%Y-%m-%dT%H:%M:%S%z')`: More verbose, less readable, harder to maintain
- Unix timestamps: Not human-readable, loses timezone information
- `datetime.now()` without timezone: Ambiguous, causes timezone confusion

**Implementation**:
```python
from datetime import datetime, timezone

processing_timestamp = datetime.now(timezone.utc).isoformat()
# Example: "2025-10-25T14:30:00+00:00"
```

---

### 2. EXIF Data Extraction from Images

**Question**: What is the best approach for extracting comprehensive EXIF data from images using Pillow?

**Decision**: Use `PIL.Image.getexif()` with tag enumeration for complete EXIF preservation

**Rationale**:
- `getexif()` returns all available EXIF tags as dict-like object
- Pillow is already a project dependency (no new dependency)
- Handles missing/corrupted EXIF data gracefully (returns empty dict)
- Compatible with all image formats that support EXIF (JPEG, TIFF, PNG)
- Can iterate over all tags and convert to human-readable format

**Alternatives Considered**:
- `exifread` library: Additional dependency, no significant advantage over Pillow
- `piexif`: More complex API, not necessary for read-only access
- Manual binary parsing: Too complex, reinventing the wheel

**Implementation**:
```python
from PIL import Image
from PIL.ExifTags import TAGS

def extract_exif_metadata(image_path: str) -> dict[str, Any]:
    """Extract all available EXIF tags from image."""
    try:
        image = Image.open(image_path)
        exif_data = image.getexif()

        if not exif_data:
            return {}

        # Convert numeric tags to human-readable names
        exif_dict = {}
        for tag_id, value in exif_data.items():
            tag_name = TAGS.get(tag_id, tag_id)
            exif_dict[tag_name] = value

        return exif_dict
    except Exception:
        return {}  # Return empty dict for missing/corrupted EXIF
```

---

### 3. Metadata Schema Design

**Question**: How should metadata be structured to maintain consistency across modules while allowing type-specific fields?

**Decision**: Use nested dictionary structure with "universal" and "source" sections

**Rationale**:
- Universal fields (processing_timestamp, model_version, configuration) are common across all modules
- Source-specific fields (EXIF, file metadata, quality metrics) vary by type
- Nested structure makes schema clear and extensible
- Compatible with JSON serialization (no special types)
- Easy to document and validate

**Schema Structure**:
```python
metadata = {
    "processing": {
        "timestamp": "2025-10-25T14:30:00+00:00",  # ISO 8601
        "model_version": "mlx-community/gemma-3-4b",
        "processing_time_seconds": 2.45
    },
    "configuration": {
        "user_provided": {"style": "detailed"},  # Explicit flags
        "effective": {"style": "detailed", "timeout": 60}  # After defaults
    },
    "source": {
        # Type-specific fields
        # PDF: page_count, file_size, creation_date
        # Image: exif, dimensions, camera_info
        # Audio: duration, sample_rate, language_confidence
    }
}
```

**Alternatives Considered**:
- Flat dictionary: Harder to distinguish universal vs type-specific fields, name collisions
- TypedDict/dataclass: More rigid, harder to extend per type, not JSON-serializable by default
- Separate metadata classes per module: Inconsistent API, harder to maintain

---

### 4. CLI Flag Implementation

**Question**: How should the `--include-metadata` flag be implemented consistently across modules?

**Decision**: Use argparse `store_true` action with default=False

**Rationale**:
- Consistent with existing CLI patterns in the project
- Boolean flag (no value required): `--include-metadata` enables, omission disables
- Default=False ensures backward compatibility (metadata disabled by default)
- Easy to pass to processing functions as boolean parameter

**Implementation**:
```python
parser.add_argument(
    "--include-metadata",
    action="store_true",
    default=False,
    help="Include source file and processing metadata in output"
)
```

---

### 5. Metadata Preservation Across Output Formats

**Question**: How should metadata be preserved when converting to different output formats (JSON, plain text, markdown, CSV)?

**Decision**: Format-specific metadata rendering strategies

**Rationale**:
- JSON: Natural nested object structure, metadata as top-level key
- Markdown: YAML frontmatter or dedicated "## Metadata" section
- Plain text: Exclude metadata (not human-readable in plain format)
- CSV: Flattened metadata columns (dot notation for nested fields)

**Format Strategies**:

**JSON**:
```json
{
  "result": {
    "text": "...",
    "success": true
  },
  "metadata": {
    "processing": {...},
    "source": {...}
  }
}
```

**Markdown**:
```markdown
---
processing_timestamp: 2025-10-25T14:30:00+00:00
model_version: medium
---

# Result

[content here]

## Metadata

- Processing Time: 2.45s
- File Size: 1.2 MB
```

**CSV** (flattened):
```csv
text,success,metadata.processing.timestamp,metadata.source.file_size
"...",true,2025-10-25T14:30:00+00:00,1234567
```

**Plain Text**: Exclude metadata entirely (keep output clean)

**Alternatives Considered**:
- Always include metadata: Breaks plain text readability
- Separate metadata files: Complicates pipeline usage
- Metadata-only output mode: Not requested in spec

---

### 6. Handling Missing/Unavailable Metadata

**Question**: How should the system handle missing or unavailable metadata fields?

**Decision**: Use descriptive string placeholders ("unavailable", "unknown") or None

**Rationale**:
- Per clarifications: Set field to "unavailable" or "unknown" (not omit)
- Maintains consistent schema across all outputs
- Clear signal that field was checked but not available
- Differentiates between "not checked" (missing field) and "checked but unavailable" (placeholder)

**Implementation Strategy**:
```python
def get_file_creation_date(file_path: str) -> str:
    """Get file creation date in ISO 8601 format."""
    try:
        stat_info = os.stat(file_path)
        creation_time = datetime.fromtimestamp(stat_info.st_ctime, tz=timezone.utc)
        return creation_time.isoformat()
    except (OSError, ValueError):
        return "unavailable"
```

---

### 7. Configuration Metadata (Explicit vs Effective)

**Question**: How should configuration parameters be represented in metadata?

**Decision**: Include both "user_provided" and "effective" configuration

**Rationale**:
- Per clarifications: "Both explicit and effective config (verbose but comprehensive)"
- User_provided: Only flags/params explicitly set by user
- Effective: Complete configuration after applying defaults
- Enables debugging (see what user specified vs what was actually used)
- Supports reproducibility (effective config can recreate exact processing)

**Implementation**:
```python
metadata["configuration"] = {
    "user_provided": {
        "model": "medium",  # User specified --model medium
    },
    "effective": {
        "model": "medium",
        "quantization": "none",  # Default value
        "batch_size": 12,  # Default value
        "timeout_seconds": 600,  # Default value
    }
}
```

---

### 8. PDF Metadata Extraction

**Question**: What PDF metadata should be extracted and how?

**Decision**: Use os.stat for file metadata, pdfplumber for page count, PDF info dict for creation date

**Rationale**:
- os.stat.st_size: File size in bytes (reliable, cross-platform)
- pdfplumber.pages: Page count (already used in module)
- PDF.info dict: Creation/modification dates from PDF metadata (if available)
- All are non-invasive reads, no parsing overhead

**Implementation**:
```python
import os
from datetime import datetime, timezone

def extract_pdf_metadata(pdf_path: str, pdf_obj) -> dict:
    """Extract PDF-specific metadata."""
    metadata = {}

    # File size
    try:
        metadata["file_size_bytes"] = os.stat(pdf_path).st_size
    except OSError:
        metadata["file_size_bytes"] = "unavailable"

    # Page count
    metadata["page_count"] = len(pdf_obj.pages)

    # Creation date from PDF metadata
    try:
        if pdf_obj.metadata and "CreationDate" in pdf_obj.metadata:
            creation_date = pdf_obj.metadata["CreationDate"]
            # Parse PDF date format (D:YYYYMMDDHHmmSS)
            # Convert to ISO 8601
            metadata["creation_date"] = parse_pdf_date(creation_date)
        else:
            metadata["creation_date"] = "unavailable"
    except Exception:
        metadata["creation_date"] = "unavailable"

    return metadata
```

---

### 9. Audio Metadata Extraction

**Question**: What audio metadata should be extracted and from what source?

**Decision**: Use lightning-whisper-mlx transcription result for language confidence, duration, and detected language

**Rationale**:
- Duration: Already extracted during audio validation (AudioDocument.duration)
- Sample rate: Already extracted (AudioDocument.sample_rate)
- Language confidence: Available from whisper model output (if language detection enabled)
- No additional parsing required (all from existing processing pipeline)

**Implementation**:
```python
def extract_audio_metadata(audio_doc: AudioDocument, result) -> dict:
    """Extract audio-specific metadata."""
    return {
        "duration_seconds": audio_doc.duration,
        "sample_rate_hz": audio_doc.sample_rate,
        "file_size_bytes": audio_doc.file_size,
        "channels": audio_doc.channels,
        "format": audio_doc.format,
        "detected_language": result.detected_language or "unavailable",
        "language_confidence": result.confidence_score or "unavailable",
    }
```

---

## Summary of Decisions

| Area | Decision | Rationale |
|------|----------|-----------|
| Timestamps | `datetime.now(timezone.utc).isoformat()` | Standard ISO 8601, unambiguous, stdlib only |
| EXIF Data | `PIL.Image.getexif()` with tag enumeration | Comprehensive, uses existing dependency |
| Schema Design | Nested dict: processing, configuration, source | Clear separation of universal vs type-specific |
| CLI Flag | `--include-metadata` (store_true, default=False) | Backward compatible, consistent pattern |
| Format Preservation | Format-specific strategies (JSON nested, markdown frontmatter, CSV flattened) | Optimized for each format's strengths |
| Missing Fields | String placeholders ("unavailable") or None | Consistent schema, clear unavailability signal |
| Configuration | Both user_provided and effective | Complete debugging/reproducibility context |
| PDF Metadata | os.stat + pdfplumber + PDF info dict | Reliable, no new dependencies |
| Audio Metadata | Existing AudioDocument + whisper result | No additional parsing, reuse existing data |

---

## Dependencies Confirmed

**No new dependencies required**:
- datetime (stdlib): ISO 8601 timestamps
- os (stdlib): File metadata (size, timestamps)
- pathlib (stdlib): Path handling
- PIL/Pillow (existing): EXIF extraction
- pdfplumber (existing): PDF metadata
- lightning-whisper-mlx (existing): Audio transcription metadata

**Dependency Status**: ✅ All dependencies already in project

---

## Open Questions

None. All research questions resolved through clarifications session and technical investigation.

---

## Next Steps

1. Design detailed metadata schema (data-model.md)
2. Define API contracts for metadata structure (contracts/)
3. Create contract tests for metadata validation
4. Implement metadata extraction functions per module
5. Update CLI parsers with --include-metadata flag
6. Update formatters to handle metadata in output

---

**Research Status**: ✅ COMPLETE - Ready for Phase 1 (Design & Contracts)
