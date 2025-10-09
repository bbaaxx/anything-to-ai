# Contract: Audio Processor API

## Function: process_audio()

**Module**: `anyfile_to_ai.audio_processor.processor`

### Signature

```python
def process_audio(
    file_path: str,
    config: TranscriptionConfig | None = None
) -> TranscriptionResult
```

### Contract Changes

**MODIFIED BEHAVIOR** (when config.timestamps=True):
- MUST extract segments from Whisper result if available
- MUST convert seek positions to seconds
- MUST populate TranscriptionResult.segments field
- MUST warn user if segments unavailable but continue processing

### Input Contract

**Parameters**:
- `file_path`: Valid path to audio file (mp3, wav, m4a)
- `config`: Optional TranscriptionConfig with new `timestamps: bool` field

**Preconditions**:
- File must exist and be readable
- Format must be supported
- Duration must not exceed max_duration_seconds

### Output Contract

**Returns**: TranscriptionResult with the following guarantees:

**When config.timestamps=True and segments available**:
```python
TranscriptionResult(
    # ... existing fields ...
    segments=[  # List of TranscriptionSegment
        TranscriptionSegment(start=float, end=float, text=str),
        # ... more segments ...
    ]
)
```

**Guarantees**:
- `segments` is a list (not None)
- Each segment has: start >= 0.0, end > start, text is non-empty string
- Segments are in chronological order
- Timestamps are in seconds with centisecond precision (0.01s granularity)

**When config.timestamps=True but segments unavailable**:
```python
TranscriptionResult(
    # ... existing fields ...
    segments=None  # Unavailable
)
```

**Guarantees**:
- Warning logged to user
- `success=True` (non-fatal)
- `text` field still contains full transcription
- `error_message=None`

**When config.timestamps=False or config is None**:
```python
TranscriptionResult(
    # ... existing fields ...
    segments=None  # Not requested
)
```

**Guarantees**:
- Existing behavior unchanged
- No warnings logged
- No performance impact

### Error Handling

**Existing errors** (unchanged):
- AudioNotFoundError
- UnsupportedFormatError
- CorruptedAudioError
- DurationExceededError
- ModelLoadError
- ProcessingTimeoutError

**New warning** (non-fatal):
- "Timestamp data unavailable for {file_path}, continuing without timestamps"

### Test Coverage

**Contract test**: `tests/contract/test_timestamp_contracts.py::test_process_audio_with_timestamps`

**Assertions**:
1. With timestamps enabled and valid audio:
   - result.segments is not None
   - result.segments is a list
   - len(result.segments) > 0
   - Each segment matches TranscriptionSegment schema
   - start < end for all segments
   - Segments in chronological order

2. With timestamps disabled:
   - result.segments is None
   - No warnings logged
   - Output identical to pre-feature behavior

3. With timestamps enabled but unavailable:
   - result.segments is None
   - Warning logged
   - result.success is True
   - result.text is not empty
