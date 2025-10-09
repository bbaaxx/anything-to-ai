# Contract: CLI Interface

## Command: audio_processor

**Module**: `anyfile_to_ai.audio_processor.cli`

### New Flag: --timestamps

**Type**: Boolean flag (no argument)
**Default**: False (disabled)
**Short form**: None

### Usage

```bash
# Enable timestamps in output
uv run python -m audio_processor audio.mp3 --timestamps

# With format options
uv run python -m audio_processor audio.mp3 --timestamps --format markdown
uv run python -m audio_processor audio.mp3 --timestamps --format json

# Batch processing with timestamps
uv run python -m audio_processor file1.mp3 file2.wav --timestamps

# Without timestamps (existing behavior)
uv run python -m audio_processor audio.mp3
```

### Contract

**When --timestamps flag is present**:
- Creates config with `timestamps=True`
- Passes config to processor
- Output includes timestamp information in chosen format

**When --timestamps flag is absent**:
- Creates config with `timestamps=False` (default)
- Existing behavior unchanged
- No timestamp information in output

### Output Contract

**Markdown format with --timestamps**:
```
[00:00:00.00] First segment of transcribed text.
[00:05.23] Second segment continues here.
[00:12.45] Final segment of the audio.
```

**Markdown format without --timestamps** (unchanged):
```
First segment of transcribed text. Second segment continues here. Final segment of the audio.
```

**JSON format with --timestamps**:
```json
{
  "audio_path": "/path/to/audio.mp3",
  "text": "Full transcription text...",
  "segments": [
    {"start": 0.0, "end": 5.23, "text": "First segment of transcribed text."},
    {"start": 5.23, "end": 12.45, "text": "Second segment continues here."},
    {"start": 12.45, "end": 18.67, "text": "Final segment of the audio."}
  ],
  "detected_language": "en",
  "processing_time": 3.45,
  "model_used": "medium"
}
```

**JSON format without --timestamps** (unchanged):
```json
{
  "audio_path": "/path/to/audio.mp3",
  "text": "Full transcription text...",
  "detected_language": "en",
  "processing_time": 3.45,
  "model_used": "medium"
}
```

### Exit Codes

**Unchanged**: Existing exit code behavior maintained
- 0: Success
- 1: Error

### Help Text

**Addition to --help output**:
```
--timestamps          Include timestamps in transcription output (segment-level)
```

### Test Coverage

**Contract test**: `tests/contract/test_timestamp_contracts.py::test_cli_timestamps_flag`

**Assertions**:
1. Flag parsing works correctly
2. Config created with correct timestamps value
3. Output format changes when flag present
4. Backward compatibility: no flag = no timestamps
5. Works with all format options (json, markdown, plain)
6. Works with batch processing
