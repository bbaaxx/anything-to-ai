# Data Model: Timestamp Support for Audio Transcription

**Feature**: 014-timestamp-support-for
**Date**: 2025-10-06

## Entity Definitions

### TranscriptionSegment

**Purpose**: Represents a time-bounded portion of transcribed audio with start time, end time, and associated text content.

**Fields**:
- `start` (float): Start time of segment in seconds (centisecond precision: 0.01s)
- `end` (float): End time of segment in seconds (centisecond precision: 0.01s)
- `text` (str): Transcribed text for this segment

**Validation Rules**:
- `start` >= 0.0 (non-negative)
- `end` > `start` (end must be after start)
- `text` non-empty for valid segments
- Precision: Values stored as floats, formatted to 2 decimal places for display

**Example**:
```python
TranscriptionSegment(
    start=83.45,
    end=91.23,
    text="This is a sample transcribed segment."
)
```

### TranscriptionResult (Modified)

**Purpose**: Contains transcription output with quality metrics, metadata, and optional timestamp segments.

**New Fields** (additions to existing model):
- `segments` (list[TranscriptionSegment] | None): Optional list of timestamped segments
  - None when timestamps not requested or unavailable
  - Empty list [] is valid (file with no speech)
  - Non-empty when timestamps successfully extracted

**Existing Fields** (unchanged):
- `audio_path` (str)
- `text` (str)
- `confidence_score` (float | None)
- `processing_time` (float)
- `model_used` (str)
- `quantization` (str)
- `detected_language` (str | None)
- `success` (bool)
- `error_message` (str | None)

**Validation Rules** (new):
- If `segments` is not None, all segments must be valid TranscriptionSegment instances
- Segments should be in chronological order (segment[i].end <= segment[i+1].start)
- When `success=False`, segments should be None

**Example with Timestamps**:
```python
TranscriptionResult(
    audio_path="/path/to/audio.mp3",
    text="Full transcription text here.",
    confidence_score=0.95,
    processing_time=12.34,
    model_used="medium",
    quantization="none",
    detected_language="en",
    success=True,
    error_message=None,
    segments=[
        TranscriptionSegment(start=0.0, end=5.23, text="First segment."),
        TranscriptionSegment(start=5.23, end=12.45, text="Second segment."),
    ]
)
```

**Example without Timestamps**:
```python
TranscriptionResult(
    audio_path="/path/to/audio.mp3",
    text="Full transcription text here.",
    # ... other fields ...
    segments=None  # Timestamps not requested or unavailable
)
```

### TranscriptionConfig (Modified)

**Purpose**: Configuration parameters for transcription process.

**New Fields** (additions to existing config):
- `timestamps` (bool): Enable timestamp extraction (default: False)

**Existing Fields** (unchanged):
- `model` (str)
- `quantization` (str)
- `batch_size` (int)
- `language` (str | None)
- `output_format` (str)
- `timeout_seconds` (int)
- `progress_callback` (Callable | None)
- `verbose` (bool)
- `max_duration_seconds` (int)

**Example**:
```python
TranscriptionConfig(
    model="medium",
    quantization="none",
    timestamps=True,  # NEW: Enable timestamp extraction
    output_format="markdown",
    # ... other config ...
)
```

## Relationships

```
TranscriptionConfig
    ↓ (configures)
AudioProcessor.process_audio()
    ↓ (returns)
TranscriptionResult
    ↓ (contains 0..* when timestamps=True)
TranscriptionSegment[]
```

## State Transitions

### Timestamp Extraction Flow

```
1. User requests transcription with --timestamps flag
   → TranscriptionConfig.timestamps = True

2. Processor transcribes audio
   → Whisper returns result with segments data

3a. Segments available:
    → Extract segments from result["segments"]
    → Convert seek positions to seconds
    → Create TranscriptionSegment instances
    → Attach to TranscriptionResult.segments

3b. Segments unavailable/empty:
    → Log warning: "Timestamp data unavailable"
    → Set TranscriptionResult.segments = None
    → Continue with text-only result

4. Formatter receives TranscriptionResult
   → If segments is not None: include timestamps in output
   → If segments is None: output text only (existing behavior)
```

## Data Flow

```
CLI Input (--timestamps)
    ↓
create_config(timestamps=True)
    ↓
process_audio(config)
    ↓
whisper_model.transcribe() → result dict
    ↓
extract_segments(result["segments"])
    ↓
convert_to_transcription_segments()
    ↓
TranscriptionResult(text, segments)
    ↓
format_output(result, config.output_format)
    ↓
Output (markdown with timestamps OR JSON with segments)
```

## Storage Considerations

**In-Memory Only**: No persistent storage required
- All data exists in-memory during processing
- Results formatted and output to stdout or file
- No database or cache needed

## Size Estimates

**TranscriptionSegment**: ~24 bytes overhead + text length
- 8 bytes (float start)
- 8 bytes (float end)
- ~8 bytes (str reference) + text content

**Typical audio file** (10 minutes, ~60 segments):
- Segments data: ~60 * (24 + 50 avg text) = ~4.4 KB
- Negligible impact on memory

**Max audio file** (2 hours, ~720 segments):
- Segments data: ~720 * (24 + 50 avg text) = ~53 KB
- Still minimal memory impact

## Validation Strategy

**Contract Tests** (test_timestamp_contracts.py):
- Verify TranscriptionSegment structure
- Verify TranscriptionResult.segments field type
- Verify timestamp precision (2 decimal places)
- Verify segment ordering

**Integration Tests** (test_timestamp_integration.py):
- Test with actual audio file
- Verify segments extracted correctly
- Verify time conversion accuracy
- Test graceful degradation when segments unavailable

**Unit Tests** (test_timestamp_formatting.py):
- Test timestamp formatting (seconds → HH:MM:SS.CC)
- Test edge cases (0.0, 3599.99, 7200.00)
- Test markdown formatting with timestamps
- Test JSON serialization of segments

## Backward Compatibility

**Guarantee**: 100% backward compatible
- `segments` field is optional (defaults to None)
- Existing code that doesn't check segments continues to work
- JSON output without --timestamps is unchanged
- Markdown output without --timestamps is unchanged

**Migration**: None required - additive change only
