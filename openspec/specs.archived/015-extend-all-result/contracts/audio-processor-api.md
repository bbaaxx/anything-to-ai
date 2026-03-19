# API Contract: Audio Processor with Metadata

**Module**: `anyfile_to_ai.audio_processor`
**Version**: 0.2.0 (with metadata support)

---

## CLI Interface

### Command

```bash
uv run python -m audio_processor <audio_files> [OPTIONS]
```

### New Options

```
--include-metadata    Include source file and processing metadata in output
```

### Examples

```bash
# Transcribe with metadata (JSON output)
uv run python -m audio_processor podcast.mp3 --format json --include-metadata

# Transcribe with metadata (markdown output)
uv run python -m audio_processor interview.wav --format markdown --include-metadata --timestamps

# Transcribe without metadata (backward compatible)
uv run python -m audio_processor audio.mp3 --format plain
```

---

## Data Model Changes

### TranscriptionResult Extension

```python
@dataclass
class TranscriptionResult:
    audio_path: str
    text: str
    confidence_score: float | None
    processing_time: float
    model_used: str
    quantization: str
    detected_language: str | None
    success: bool
    error_message: str | None
    segments: list[TranscriptionSegment] | None = None
    metadata: dict | None = None  # NEW: Optional metadata
```

### Metadata Structure (when enabled)

```python
{
    "processing": {
        "timestamp": "2025-10-25T14:40:00+00:00",
        "model_version": "lightning-whisper-mlx-medium",
        "processing_time_seconds": 15.3
    },
    "configuration": {
        "user_provided": {
            "model": "medium",
            "language": "en",
            "timestamps": true
        },
        "effective": {
            "model": "medium",
            "language": "en",
            "timestamps": true,
            "quantization": "none",
            "batch_size": 12,
            "timeout_seconds": 600,
            "max_duration_seconds": 7200
        }
    },
    "source": {
        "file_path": "/path/to/podcast.mp3",
        "file_size_bytes": 5242880,
        "duration_seconds": 180.5,
        "sample_rate_hz": 44100,
        "channels": 2,
        "format": "mp3",
        "detected_language": "en",
        "language_confidence": 0.95
    }
}
```

---

## JSON Output Contract

### With Metadata Enabled

```json
{
  "audio_path": "/path/to/podcast.mp3",
  "text": "Welcome to this podcast episode where we discuss...",
  "confidence_score": 0.95,
  "processing_time": 15.3,
  "model_used": "medium",
  "quantization": "none",
  "detected_language": "en",
  "success": true,
  "error_message": null,
  "segments": [
    {
      "start": 0.0,
      "end": 5.2,
      "text": "Welcome to this podcast episode"
    }
  ],
  "metadata": {
    "processing": {
      "timestamp": "2025-10-25T14:40:00+00:00",
      "model_version": "lightning-whisper-mlx-medium",
      "processing_time_seconds": 15.3
    },
    "configuration": {
      "user_provided": {
        "model": "medium",
        "language": "en"
      },
      "effective": {
        "model": "medium",
        "language": "en",
        "quantization": "none",
        "batch_size": 12,
        "timeout_seconds": 600
      }
    },
    "source": {
      "file_path": "/path/to/podcast.mp3",
      "file_size_bytes": 5242880,
      "duration_seconds": 180.5,
      "sample_rate_hz": 44100,
      "channels": 2,
      "format": "mp3",
      "detected_language": "en",
      "language_confidence": 0.95
    }
  }
}
```

### Without Metadata (Default)

```json
{
  "audio_path": "/path/to/podcast.mp3",
  "text": "Welcome to this podcast episode...",
  "confidence_score": 0.95,
  "processing_time": 15.3,
  "model_used": "medium",
  "quantization": "none",
  "detected_language": "en",
  "success": true,
  "error_message": null,
  "segments": [...],
  "metadata": null
}
```

---

## Markdown Output Contract

### With Metadata Enabled

```markdown
---
processing_timestamp: 2025-10-25T14:40:00+00:00
model_version: lightning-whisper-mlx-medium
audio_duration: 180.5
detected_language: en
language_confidence: 0.95
---

# Audio Transcription: podcast.mp3

Welcome to this podcast episode where we discuss...

## Timestamps

- [00:00 - 00:05] Welcome to this podcast episode
- [00:05 - 00:12] where we discuss artificial intelligence
- [00:12 - 00:20] and its impact on society

## Metadata

### Processing
- **Timestamp**: 2025-10-25T14:40:00+00:00
- **Model**: medium (lightning-whisper-mlx)
- **Processing Time**: 15.3s
- **Quantization**: none

### Source Audio
- **File Size**: 5.0 MB
- **Duration**: 180.5s (3:00.5)
- **Sample Rate**: 44100 Hz
- **Channels**: 2 (stereo)
- **Format**: mp3

### Language Detection
- **Detected**: en (English)
- **Confidence**: 0.95 (95%)
```

---

## Language Detection Metadata

### High Confidence Detection

```python
"source": {
    "detected_language": "en",
    "language_confidence": 0.95
}
```

### Low Confidence Detection

```python
"source": {
    "detected_language": "en",
    "language_confidence": 0.45  # Include actual score regardless of value
}
```

### Auto-Detection Disabled (User Specified Language)

```python
"source": {
    "detected_language": "es",  # User-specified via --language es
    "language_confidence": "unavailable"  # Not calculated
}
```

---

## Contract Tests

### Test Scenarios

1. **Metadata disabled (default)**:
   - Transcribe without `--include-metadata`
   - Assert `result.metadata is None`

2. **Metadata enabled with language detection**:
   - Transcribe with auto language detection
   - Assert metadata.source.detected_language is ISO 639-1 code
   - Assert metadata.source.language_confidence is float 0.0-1.0

3. **Metadata enabled with user-specified language**:
   - Transcribe with `--language en --include-metadata`
   - Assert metadata.source.detected_language = "en"
   - Assert metadata.source.language_confidence = "unavailable"

4. **Audio file metadata extraction**:
   - Assert duration_seconds matches AudioDocument
   - Assert sample_rate_hz matches AudioDocument
   - Assert file_size_bytes is correct

5. **Configuration metadata validation**:
   - Assert user_provided contains only specified flags
   - Assert effective contains all config with defaults
   - Assert model, quantization, timeout present in effective

---

## Backward Compatibility

✅ **Fully backward compatible**:
- Default behavior unchanged (metadata disabled)
- Existing transcription output preserved
- No breaking changes to TranscriptionResult model
- New field is optional

---

## Error Handling

### Missing Audio File

```json
{
  "audio_path": "/path/to/missing.mp3",
  "text": "",
  "success": false,
  "error_message": "File not found: missing.mp3",
  "metadata": null
}
```

### Unsupported Format (with metadata enabled)

```json
{
  "audio_path": "/path/to/audio.ogg",
  "text": "",
  "success": false,
  "error_message": "Unsupported audio format: ogg",
  "metadata": {
    "processing": {
      "timestamp": "2025-10-25T14:40:00+00:00",
      "model_version": "lightning-whisper-mlx-medium",
      "processing_time_seconds": 0.05
    },
    "source": {
      "file_path": "/path/to/audio.ogg",
      "file_size_bytes": 1234567,
      "duration_seconds": "unavailable",
      "sample_rate_hz": "unavailable",
      "channels": "unavailable",
      "format": "ogg",
      "detected_language": "unavailable",
      "language_confidence": "unavailable"
    }
  }
}
```

---

## Duration and Sample Rate

### Source Metadata Fields

- **duration_seconds**: Extracted during audio validation (AudioDocument.duration)
- **sample_rate_hz**: Extracted during audio validation (AudioDocument.sample_rate)
- **channels**: Mono (1) or stereo (2)
- **format**: File extension (mp3, wav, m4a)

These fields are already available in the processing pipeline; no additional parsing required.

---

**Contract Version**: 1.0
**Schema**: [metadata-schema.json](./metadata-schema.json)
