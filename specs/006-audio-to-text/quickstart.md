# Quickstart: Audio-to-Text Transcription Module

**Branch**: `006-audio-to-text` | **Date**: 2025-09-29

## Overview

This quickstart validates the audio transcription module implementation through practical examples. Follow these steps to verify all functional requirements are met.

## Prerequisites

```bash
# Ensure you're on the feature branch
git checkout 006-audio-to-text

# Install dependencies
uv add lightning-whisper-mlx

# Verify installation
python -c "import audio_processor; print(audio_processor.__version__)"
```

## Test Data Setup

Create sample audio files for testing:

```bash
# Create test data directory
mkdir -p sample-data/audio

# Sample files needed:
# - sample-data/audio/speech.mp3 (normal speech audio)
# - sample-data/audio/silence.wav (silent audio file)
# - sample-data/audio/spanish.m4a (Spanish speech for language detection)
# - sample-data/audio/long.mp3 (longer audio file, ~5 minutes)
```

## Quick Validation Steps

### 1. Basic Transcription (FR-003, FR-004)

**Test**: Process single audio file with default settings

```bash
python -m audio_processor sample-data/audio/speech.mp3
```

**Expected Output**:
```
Processed 1 files
Successful: 1, Failed: 0
Total time: X.XXs

✓ sample-data/audio/speech.mp3
   [Transcribed text content from the audio file]
   Duration: XX.Xs, Model: medium (4bit), Language: en
```

**Validates**: FR-001, FR-002, FR-003, FR-004, FR-006, FR-012 (defaults)

---

### 2. JSON Output Format (FR-004, FR-015)

**Test**: Process with structured JSON output

```bash
python -m audio_processor sample-data/audio/speech.mp3 --format json
```

**Expected Output**:
```json
{
  "success": true,
  "total_files": 1,
  "successful_count": 1,
  "failed_count": 0,
  "total_processing_time": XX.XX,
  "results": [
    {
      "audio_path": "sample-data/audio/speech.mp3",
      "text": "[Transcribed text]",
      "confidence_score": 0.XX,
      "processing_time": XX.XX,
      "model_used": "medium",
      "quantization": "4bit",
      "detected_language": "en",
      "success": true,
      "error_message": null
    }
  ]
}
```

**Validates**: FR-004, FR-015

---

### 3. Model Selection (FR-012, FR-016)

**Test**: Use different models and quantization

```bash
# Tiny model for speed
python -m audio_processor sample-data/audio/speech.mp3 --model tiny --quantization 4bit

# Large model for accuracy
python -m audio_processor sample-data/audio/speech.mp3 --model large-v3 --quantization 8bit
```

**Expected**: Faster processing with tiny model, more accurate results with large model

**Validates**: FR-012, FR-016

---

### 4. Language Detection (FR-022)

**Test**: Auto-detect and specify language

```bash
# Auto-detect (should detect Spanish)
python -m audio_processor sample-data/audio/spanish.m4a --format json

# Specify language hint
python -m audio_processor sample-data/audio/spanish.m4a --language es --format json
```

**Expected**: detected_language field shows "es" in JSON output

**Validates**: FR-022

---

### 5. Batch Processing (FR-008)

**Test**: Process multiple files at once

```bash
python -m audio_processor sample-data/audio/*.mp3 --verbose --format json
```

**Expected Output** (verbose mode):
```
Processing 3 audio files...
[1/3] Processing sample-data/audio/speech.mp3...
[1/3] ✓ sample-data/audio/speech.mp3 (XX.Xs)
[2/3] Processing sample-data/audio/long.mp3...
[2/3] ✓ sample-data/audio/long.mp3 (XX.Xs)
[3/3] Processing sample-data/audio/silence.mp3...
[3/3] ✗ sample-data/audio/silence.mp3: No speech detected
Completed 2/3 files in XX.XXs

[JSON output with all results]
```

**Validates**: FR-008, FR-009, FR-018 (verbose mode)

---

### 6. Error Handling: No Speech Detected (FR-010)

**Test**: Process silent audio file

```bash
python -m audio_processor sample-data/audio/silence.wav
```

**Expected Output**:
```
Processed 1 files
Successful: 0, Failed: 1
Total time: X.XXs

✗ sample-data/audio/silence.wav
   Error: No speech detected in audio
```

**Validates**: FR-010 (no speech detection)

---

### 7. Error Handling: Unsupported Format (FR-002, FR-010)

**Test**: Process unsupported audio format

```bash
python -m audio_processor sample-data/audio/test.ogg
```

**Expected Output**:
```
Error: Unsupported audio format: sample-data/audio/test.ogg
```

**Exit Code**: 1

**Validates**: FR-002, FR-010, FR-011

---

### 8. Error Handling: File Not Found (FR-001, FR-010)

**Test**: Process non-existent file

```bash
python -m audio_processor nonexistent.mp3
```

**Expected Output**:
```
Error: Audio file not found: nonexistent.mp3
```

**Exit Code**: 1

**Validates**: FR-001, FR-010

---

### 9. Duration Limit (FR-023)

**Test**: Process audio file exceeding 2-hour limit

```bash
# Assuming long-audio.mp3 is >2 hours
python -m audio_processor sample-data/audio/long-audio.mp3
```

**Expected Output**:
```
Error: Audio duration exceeds 2-hour limit: sample-data/audio/long-audio.mp3
```

**Exit Code**: 1

**Validates**: FR-023

---

### 10. Output File Specification (FR-017)

**Test**: Save results to file

```bash
python -m audio_processor sample-data/audio/speech.mp3 --format json --output results.json
cat results.json
```

**Expected**: JSON results saved to results.json file

**Validates**: FR-017

---

### 11. Audio Metadata Extraction (FR-014)

**Test**: Get audio file information without processing

```python
import audio_processor

info = audio_processor.get_audio_info("sample-data/audio/speech.mp3")
print(info)
```

**Expected Output**:
```python
{
    "file_path": "sample-data/audio/speech.mp3",
    "format": "mp3",
    "duration": 120.5,
    "sample_rate": 44100,
    "file_size": 1234567,
    "channels": 2
}
```

**Validates**: FR-014

---

### 12. Programmatic API (FR-019, FR-020)

**Test**: Use module API programmatically

```python
import audio_processor

# Create configuration
config = audio_processor.create_config(
    model="base",
    quantization="4bit",
    output_format="json",
    verbose=True
)

# Process single audio
result = audio_processor.process_audio("sample-data/audio/speech.mp3", config)
print(f"Success: {result.success}")
print(f"Text: {result.text}")
print(f"Language: {result.detected_language}")

# Process batch
results = audio_processor.process_audio_batch([
    "sample-data/audio/speech.mp3",
    "sample-data/audio/spanish.m4a"
], config)

print(f"Total: {results.total_files}")
print(f"Successful: {results.successful_count}")
```

**Expected**: Successful transcription with metadata

**Validates**: FR-019, FR-020

---

### 13. Progress Callbacks (FR-009)

**Test**: Monitor batch processing progress

```python
import audio_processor

def progress_handler(current, total):
    print(f"Progress: {current}/{total} files completed")

config = audio_processor.create_config(
    progress_callback=progress_handler
)

results = audio_processor.process_audio_batch([
    "sample-data/audio/speech.mp3",
    "sample-data/audio/long.mp3",
    "sample-data/audio/spanish.m4a"
], config)
```

**Expected Output**:
```
Progress: 1/3 files completed
Progress: 2/3 files completed
Progress: 3/3 files completed
```

**Validates**: FR-009

---

### 14. Supported Formats Query (FR-002)

**Test**: Get list of supported formats

```python
import audio_processor

formats = audio_processor.get_supported_formats()
print(formats)
```

**Expected Output**:
```python
['m4a', 'mp3', 'wav']
```

**Validates**: FR-002

---

### 15. Configuration Validation (FR-012, FR-020)

**Test**: Validate configuration parameters

```python
import audio_processor
from audio_processor import ValidationError

try:
    # Invalid model
    config = audio_processor.create_config(model="invalid")
except ValidationError as e:
    print(f"Caught expected error: {e}")

try:
    # Invalid batch size
    config = audio_processor.create_config(batch_size=200)
except ValidationError as e:
    print(f"Caught expected error: {e}")
```

**Expected**: ValidationError raised with descriptive messages

**Validates**: FR-012, FR-020

---

## Acceptance Criteria Validation

### Scenario 1: Default Settings (from spec)

✅ Valid audio file with default settings → transcribed text with confidence metrics

```bash
python -m audio_processor sample-data/audio/speech.mp3 --format json
# Verify: success=true, text present, confidence_score present, model_used="medium", quantization="4bit"
```

### Scenario 2: Batch Processing (from spec)

✅ Multiple audio files → results for each with success/failure status

```bash
python -m audio_processor sample-data/audio/*.mp3 --format json
# Verify: total_files matches count, each result has success boolean
```

### Scenario 3: Error Handling (from spec)

✅ Corrupted/unsupported file → clear error message without crash

```bash
python -m audio_processor sample-data/audio/corrupt.mp3
# Verify: error message, exit code 1, no crash
```

### Scenario 4: Progress Updates (from spec)

✅ Long audio file → progress updates showing completion

```bash
python -m audio_processor sample-data/audio/long.mp3 --verbose
# Verify: progress messages during processing
```

### Scenario 5: JSON Output (from spec)

✅ JSON format → structured data with text, confidence, metadata

```bash
python -m audio_processor sample-data/audio/speech.mp3 --format json
# Verify: valid JSON, all required fields present
```

### Scenario 6: Plain Text Output (from spec)

✅ Plain format → clean text without technical metadata

```bash
python -m audio_processor sample-data/audio/speech.mp3 --format plain
# Verify: human-readable format, text present
```

---

## Performance Validation (FR-013)

**Test**: Verify Apple Silicon optimization

```bash
# Monitor system during processing
python -m audio_processor sample-data/audio/long.mp3 --verbose

# Check that MLX framework is used (should be fast)
# Expected: Significantly faster than CPU-based Whisper
```

**Validates**: FR-013

---

## Success Criteria

All tests pass when:

1. ✅ Single audio transcription works with default settings
2. ✅ JSON and plain output formats produce correct results
3. ✅ Model and quantization selection works
4. ✅ Language auto-detection and hints work
5. ✅ Batch processing handles multiple files
6. ✅ No speech detection returns appropriate error
7. ✅ Unsupported formats raise clear errors
8. ✅ Missing files raise clear errors
9. ✅ Duration limit enforced for >2 hour files
10. ✅ Output file specification works
11. ✅ Audio metadata extraction works
12. ✅ Programmatic API works
13. ✅ Progress callbacks work
14. ✅ Supported formats query works
15. ✅ Configuration validation works

---

## Troubleshooting

**Model Download Issues**:
```bash
# Manually download model if auto-download fails
# Models cached in ~/.cache/huggingface/
```

**Memory Issues**:
```bash
# Use smaller model or higher quantization
python -m audio_processor audio.mp3 --model tiny --quantization 4bit
```

**Slow Processing**:
```bash
# Increase batch size (if sufficient memory)
python -m audio_processor audio.mp3 --batch-size 24
```

---

**Quickstart Complete**: Ready for implementation and testing