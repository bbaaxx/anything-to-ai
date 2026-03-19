# Quickstart: Timestamp Support for Audio Transcription

**Feature**: 014-timestamp-support-for
**Target**: Developers and testers validating the timestamp feature

## Prerequisites

- Python 3.13+
- uv installed
- Sample audio file (e.g., `sample-data/audio/test.mp3`)

## Installation

```bash
# From repository root
cd /Users/bbaaxx/Code/projects/anyfile-to-ai

# Install dependencies (already done)
uv sync
```

## Quick Test: Basic Timestamp Usage

### 1. Transcribe with timestamps (Markdown output)

```bash
uv run python -m audio_processor sample-data/audio/test.mp3 --timestamps --format markdown
```

**Expected output**:
```
[00:00:00.00] First segment of the audio transcription.
[00:05.23] Second segment continues the conversation.
[00:12.45] Final segment wraps up the audio content.
```

### 2. Transcribe with timestamps (JSON output)

```bash
uv run python -m audio_processor sample-data/audio/test.mp3 --timestamps --format json
```

**Expected output**:
```json
{
  "audio_path": "sample-data/audio/test.mp3",
  "text": "First segment of the audio transcription. Second segment continues the conversation. Final segment wraps up the audio content.",
  "segments": [
    {
      "start": 0.0,
      "end": 5.23,
      "text": "First segment of the audio transcription."
    },
    {
      "start": 5.23,
      "end": 12.45,
      "text": "Second segment continues the conversation."
    },
    {
      "start": 12.45,
      "end": 18.67,
      "text": "Final segment wraps up the audio content."
    }
  ],
  "detected_language": "en",
  "processing_time": 3.45,
  "model_used": "medium",
  "success": true
}
```

### 3. Transcribe without timestamps (existing behavior)

```bash
uv run python -m audio_processor sample-data/audio/test.mp3 --format markdown
```

**Expected output**:
```
First segment of the audio transcription. Second segment continues the conversation. Final segment wraps up the audio content.
```

## Validation Tests

### Contract Tests

```bash
# Run timestamp-specific contract tests
uv run pytest tests/contract/test_timestamp_contracts.py -v
```

**Expected**: All tests pass, verifying:
- TranscriptionSegment model structure
- Timestamp field in TranscriptionResult
- CLI --timestamps flag parsing
- Processor extracts segments correctly

### Integration Tests

```bash
# Run end-to-end timestamp integration tests
uv run pytest tests/integration/test_timestamp_integration.py -v
```

**Expected**: All tests pass, verifying:
- Single file with timestamps works
- Batch processing with timestamps works
- Graceful degradation when timestamps unavailable
- Format output correctly includes timestamps

### Unit Tests

```bash
# Run timestamp formatting unit tests
uv run pytest tests/unit/test_timestamp_formatting.py -v
```

**Expected**: All tests pass, verifying:
- format_timestamp() produces correct HH:MM:SS.CC format
- Edge cases handled (0.0, max duration, rounding)
- Markdown formatting with timestamps
- JSON serialization of segments
- CSV format with timestamps

### Full Test Suite

```bash
# Run all tests to ensure no regressions
uv run pytest tests/ -v
```

**Expected**: All existing tests still pass + new timestamp tests pass

## Common Use Cases

### Use Case 1: Generate Video Subtitles

```bash
# Get timestamped transcription in JSON
uv run python -m audio_processor video_audio.mp3 --timestamps --format json > subtitles.json

# Process subtitles.json to create SRT or VTT format (separate tool)
```

### Use Case 2: Podcast Chapter Markers

```bash
# Get timestamped segments in markdown for manual review
uv run python -m audio_processor podcast.mp3 --timestamps --format markdown > chapters.txt

# Review chapters.txt and create chapter markers at segment timestamps
```

### Use Case 3: Time-Indexed Search

```bash
# Get structured timestamp data
uv run python -m audio_processor meeting.wav --timestamps --format json > transcript.json

# Import transcript.json into search/analysis tool
# Search returns: "keyword found at 01:23:45"
```

### Use Case 4: CSV Export for Spreadsheet Analysis

```bash
# Get timestamp data in CSV format
uv run python -m audio_processor interview.m4a --timestamps --format csv > analysis.csv

# Open analysis.csv in Excel/Google Sheets for segment analysis
```

## Troubleshooting

### Issue: Timestamps not appearing in output

**Symptom**: Output looks the same with or without --timestamps flag

**Possible causes**:
1. Flag not passed correctly
2. Timestamp data unavailable from Whisper model

**Solution**:
```bash
# Verify flag is present
uv run python -m audio_processor audio.mp3 --timestamps --verbose

# Check for warning: "Timestamp data unavailable"
# If warning appears, this is expected behavior (graceful degradation)
```

### Issue: Timestamp precision seems off

**Symptom**: Timestamps don't match audio timing

**Expected**: Timestamps have ~10ms precision (centisecond granularity)

**Verification**:
```bash
# Use a test audio file with known timing
# Verify segment timestamps align with expected values
```

### Issue: Tests failing after implementation

**Symptom**: New contract tests fail

**Solution**:
```bash
# Run tests with verbose output
uv run pytest tests/contract/test_timestamp_contracts.py -vv

# Check error messages for contract violations
# Ensure TranscriptionSegment and TranscriptionResult match contracts
```

## Feature Toggle

### Enable timestamps (new behavior)
```bash
--timestamps
```

### Disable timestamps (existing behavior - default)
```bash
# No flag needed, timestamps off by default
```

## Performance Notes

- Timestamp extraction is enabled by default in lightning-whisper-mlx
- No additional performance overhead when --timestamps flag is used
- Memory impact negligible (~4KB for 10-minute audio, ~53KB for 2-hour max)

## Next Steps

After validating basic functionality:

1. **Integration**: Test with real-world audio files
2. **Edge Cases**: Test with silence, music, non-speech audio
3. **Formats**: Verify all output formats (markdown, json, plain, csv)
4. **Batch**: Test with multiple files simultaneously
5. **Regression**: Ensure existing functionality unchanged when flag not used

## Support

For issues or questions:
- Check test output for specific error messages
- Review contracts in `specs/014-timestamp-support-for/contracts/`
- See data model in `specs/014-timestamp-support-for/data-model.md`
