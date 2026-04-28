# API Contract: Image Processor with Metadata

**Module**: `anyfile_to_ai.image_processor`
**Version**: 0.2.0 (with metadata support)

---

## CLI Interface

### Command

```bash
uv run python -m image_processor <image_files> [OPTIONS]
```

### New Options

```
--include-metadata    Include source file and processing metadata in output
```

### Examples

```bash
# Process with metadata (JSON output)
uv run python -m image_processor photo.jpg --format json --include-metadata

# Process multiple images with metadata
uv run python -m image_processor *.jpg --format markdown --include-metadata

# Process without metadata (backward compatible)
uv run python -m image_processor photo.jpg --format json
```

---

## Data Model Changes

### DescriptionResult Extension

```python
@dataclass
class DescriptionResult:
    image_path: str
    description: str
    confidence_score: float | None
    processing_time: float
    model_used: str
    prompt_used: str
    success: bool
    technical_metadata: dict[str, Any] | None = None
    vlm_processing_time: float | None = None
    model_version: str | None = None
    metadata: dict | None = None  # NEW: Optional metadata
```

### Metadata Structure (when enabled)

```python
{
    "processing": {
        "timestamp": "2025-10-25T14:35:00+00:00",
        "model_version": "mlx-community/gemma-3-4b",
        "processing_time_seconds": 1.8
    },
    "configuration": {
        "user_provided": {
            "style": "detailed"
        },
        "effective": {
            "style": "detailed",
            "max_description_length": 500,
            "timeout_seconds": 60,
            "batch_size": 4
        }
    },
    "source": {
        "file_path": "/path/to/photo.jpg",
        "file_size_bytes": 2048576,
        "dimensions": {
            "width": 1920,
            "height": 1080
        },
        "format": "JPEG",
        "exif": {
            "Make": "Canon",
            "Model": "EOS 5D Mark IV",
            "DateTime": "2025:10:25 14:00:00",
            "FNumber": 2.8,
            "ExposureTime": 0.001,
            "ISOSpeedRatings": 400,
            "FocalLength": 50.0
        },
        "camera_info": {
            "make": "Canon",
            "model": "EOS 5D Mark IV",
            "lens": "EF 50mm f/1.8"
        }
    }
}
```

---

## JSON Output Contract

### With Metadata Enabled (Single Image)

```json
{
  "image_path": "/path/to/photo.jpg",
  "description": "A sunset over mountains with vibrant orange and purple hues",
  "confidence_score": null,
  "processing_time": 1.8,
  "model_used": "mlx-community/gemma-3-4b",
  "prompt_used": "Describe this image in a detailed manner.",
  "success": true,
  "metadata": {
    "processing": {
      "timestamp": "2025-10-25T14:35:00+00:00",
      "model_version": "mlx-community/gemma-3-4b",
      "processing_time_seconds": 1.8
    },
    "configuration": {
      "user_provided": {"style": "detailed"},
      "effective": {
        "style": "detailed",
        "max_description_length": 500,
        "timeout_seconds": 60,
        "batch_size": 4
      }
    },
    "source": {
      "file_path": "/path/to/photo.jpg",
      "file_size_bytes": 2048576,
      "dimensions": {"width": 1920, "height": 1080},
      "format": "JPEG",
      "exif": {
        "Make": "Canon",
        "Model": "EOS 5D Mark IV",
        "FNumber": 2.8,
        "ISOSpeedRatings": 400
      }
    }
  }
}
```

### Batch Processing (Multiple Images)

```json
{
  "success": true,
  "results": [
    {
      "image_path": "/path/to/photo1.jpg",
      "description": "...",
      "success": true,
      "metadata": { /* per-image metadata */ }
    },
    {
      "image_path": "/path/to/photo2.jpg",
      "description": "...",
      "success": true,
      "metadata": { /* per-image metadata */ }
    }
  ],
  "total_images": 2,
  "successful_count": 2,
  "failed_count": 0,
  "total_processing_time": 3.6
}
```

Note: Each image in batch gets its own metadata (not batch-level metadata)

---

## Markdown Output Contract

### With Metadata Enabled

```markdown
---
processing_timestamp: 2025-10-25T14:35:00+00:00
model_version: mlx-community/gemma-3-4b
camera_make: Canon
camera_model: EOS 5D Mark IV
dimensions: 1920x1080
---

# Image Analysis: photo.jpg

A sunset over mountains with vibrant orange and purple hues

## Metadata

### Processing
- **Timestamp**: 2025-10-25T14:35:00+00:00
- **Model**: mlx-community/gemma-3-4b
- **Processing Time**: 1.8s

### Source
- **File Size**: 2.0 MB
- **Dimensions**: 1920x1080 pixels
- **Format**: JPEG

### Camera Info
- **Make**: Canon
- **Model**: EOS 5D Mark IV
- **Lens**: EF 50mm f/1.8
- **Settings**: f/2.8, 1/1000s, ISO 400

### EXIF Data
- FNumber: 2.8
- ExposureTime: 0.001
- ISOSpeedRatings: 400
- FocalLength: 50.0
```

---

## EXIF Handling

### Complete EXIF Preservation

All available EXIF tags are extracted and included:

```python
"exif": {
    # Camera identification
    "Make": "Canon",
    "Model": "EOS 5D Mark IV",
    "LensModel": "EF 50mm f/1.8 STM",

    # Capture settings
    "FNumber": 2.8,
    "ExposureTime": 0.001,
    "ISOSpeedRatings": 400,
    "FocalLength": 50.0,
    "WhiteBalance": 0,
    "Flash": 16,

    # Date/time
    "DateTime": "2025:10:25 14:00:00",
    "DateTimeOriginal": "2025:10:25 14:00:00",

    # GPS (if available)
    "GPSLatitude": 37.7749,
    "GPSLongitude": -122.4194,
    "GPSAltitude": 10.5,

    # Additional metadata
    "Copyright": "Photographer Name",
    "Artist": "Photographer Name",
    "Software": "Adobe Lightroom 12.0"
}
```

### Missing EXIF Handling

```python
# Image without EXIF data (e.g., screenshot)
"exif": {},  # Empty dict
"camera_info": {}  # Empty dict
```

---

## Contract Tests

### Test Scenarios

1. **Metadata disabled (default)**:
   - Process image without `--include-metadata`
   - Assert `result.metadata is None`

2. **Metadata enabled with EXIF**:
   - Process JPEG with EXIF data
   - Assert metadata.source.exif contains camera info
   - Assert dimensions match image size

3. **Metadata enabled without EXIF**:
   - Process PNG or screenshot without EXIF
   - Assert metadata.source.exif is empty dict
   - Assert dimensions still captured

4. **Batch processing with metadata**:
   - Process multiple images with metadata
   - Assert each result has independent metadata
   - Assert no batch-level metadata

5. **EXIF tag validation**:
   - Assert all EXIF tags have human-readable names
   - Assert GPS coordinates preserved if present
   - Assert camera_info extracted from EXIF

---

## Backward Compatibility

✅ **Fully backward compatible**:
- Default behavior unchanged (metadata disabled)
- Existing output formats preserved
- No breaking changes to DescriptionResult model
- New field is optional

---

## Error Handling

### Missing Image File

```json
{
  "image_path": "/path/to/missing.jpg",
  "description": "",
  "success": false,
  "error_message": "File not found",
  "metadata": null
}
```

### Corrupted Image (with metadata enabled)

```json
{
  "image_path": "/path/to/corrupted.jpg",
  "description": "",
  "success": false,
  "metadata": {
    "processing": { "timestamp": "...", "model_version": "..." },
    "source": {
      "file_path": "/path/to/corrupted.jpg",
      "file_size_bytes": 12345,
      "dimensions": "unavailable",
      "format": "unavailable",
      "exif": {}
    }
  }
}
```

---

**Contract Version**: 1.0
**Schema**: [metadata-schema.json](./metadata-schema.json)
