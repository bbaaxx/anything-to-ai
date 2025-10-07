# Data Model: Audio-to-Text Transcription Module

**Branch**: `006-audio-to-text` | **Date**: 2025-09-29

## Overview

This document defines the data structures for the audio transcription module, extracted from functional requirements and designed to follow patterns established by the `image_processor` module.

## Core Entities

### AudioDocument

Represents a validated audio file with extracted metadata.

**Purpose**: Store audio file information after validation, before processing.

**Fields**:
- `file_path: str` - Absolute path to audio file
- `format: str` - Audio format (mp3, wav, m4a)
- `duration: float` - Audio duration in seconds
- `sample_rate: int` - Sample rate in Hz
- `file_size: int` - File size in bytes
- `channels: int` - Number of audio channels (1=mono, 2=stereo)

**Validation Rules**:
- `file_path` must exist and be readable
- `format` must be in ['mp3', 'wav', 'm4a']
- `duration` must be > 0 and ≤ 7200 seconds (2 hours)
- `sample_rate` must be > 0
- `file_size` must be > 0
- `channels` must be > 0

**State Transitions**: None (immutable after creation)

**Source**: FR-001, FR-002, FR-011, FR-014, FR-023

---

### TranscriptionResult

Contains transcription output with quality metrics and metadata.

**Purpose**: Store the result of transcribing a single audio file.

**Fields**:
- `audio_path: str` - Path to source audio file
- `text: str` - Transcribed text content
- `confidence_score: Optional[float]` - Confidence/quality score (0.0-1.0)
- `processing_time: float` - Time taken for transcription in seconds
- `model_used: str` - Whisper model identifier (e.g., "medium")
- `quantization: str` - Quantization level used (none/4bit/8bit)
- `detected_language: Optional[str]` - Auto-detected or specified language code
- `success: bool` - Whether transcription succeeded
- `error_message: Optional[str]` - Error details if success=False

**Validation Rules**:
- `audio_path` must not be empty
- `text` must not be None (empty string allowed for failed transcriptions)
- `confidence_score` must be between 0.0 and 1.0 if present
- `processing_time` must be ≥ 0
- `model_used` must not be empty
- `success` must be True if error_message is None

**State Transitions**: None (immutable after creation)

**Source**: FR-003, FR-004, FR-005, FR-006, FR-012, FR-022

---

### TranscriptionConfig

Configuration parameters for transcription process.

**Purpose**: Encapsulate all transcription settings in a single validated object.

**Fields**:
- `model: str` - Whisper model selection (default: "medium")
- `quantization: str` - Quantization level (default: "4bit")
- `batch_size: int` - Whisper decoder batch_size (default: 12)
- `language: Optional[str]` - Language hint (None for auto-detect)
- `output_format: str` - Output format preference (default: "plain")
- `timeout_seconds: int` - Processing timeout per file (default: 600)
- `progress_callback: Optional[Callable[[int, int], None]]` - Progress callback function
- `verbose: bool` - Enable verbose output (default: False)
- `max_duration_seconds: int` - Maximum audio duration (default: 7200)

**Validation Rules**:
- `model` must be in ["tiny", "small", "distil-small.en", "base", "medium", "distil-medium.en", "large", "large-v2", "distil-large-v2", "large-v3", "distil-large-v3"]
- `quantization` must be in ["none", "4bit", "8bit"]
- `batch_size` must be between 1 and 128
- `language` must be valid ISO 639-1 code if provided (2-letter, e.g., "en")
- `output_format` must be in ["plain", "json"]
- `timeout_seconds` must be > 0
- `max_duration_seconds` must be > 0 and ≤ 7200

**Defaults Rationale**:
- Model "medium" with "4bit" quantization: balanced performance/accuracy per spec
- Batch size 12: lightning-whisper-mlx default
- Timeout 600s: accommodates 2-hour audio with processing overhead
- Max duration 7200s: 2-hour limit per spec

**Source**: FR-012, FR-016, FR-018, FR-020, FR-022, FR-023

---

### ProcessingResult

Aggregate results from batch transcription operations.

**Purpose**: Store results of processing multiple audio files with statistics.

**Fields**:
- `success: bool` - Overall success status (True if at least one file succeeded)
- `results: List[TranscriptionResult]` - Individual transcription results
- `total_files: int` - Total number of files processed
- `successful_count: int` - Number of successful transcriptions
- `failed_count: int` - Number of failed transcriptions
- `total_processing_time: float` - Total time for all transcriptions in seconds
- `average_processing_time: float` - Average time per file
- `error_summary: Optional[Dict[str, int]]` - Count of error types encountered

**Validation Rules**:
- `total_files` must equal len(results)
- `successful_count + failed_count` must equal `total_files`
- `total_processing_time` must be ≥ 0
- `average_processing_time` must equal `total_processing_time / total_files` if total_files > 0

**State Transitions**: None (immutable after creation)

**Source**: FR-008, FR-009

---

## Supporting Types

### ProgressCallback

Function signature for progress reporting.

**Type**: `Callable[[int, int], None]`

**Parameters**:
- `current: int` - Number of files processed
- `total: int` - Total number of files to process

**Usage**: Called after each file completion during batch processing.

**Source**: FR-009, FR-018

---

## Relationships

```
TranscriptionConfig ──(used by)──> Processor
                                      │
                                      │ validates
                                      ↓
AudioDocument ──(input to)──> Processor ──(produces)──> TranscriptionResult
                                                              │
                                                              │ aggregated into
                                                              ↓
                                                        ProcessingResult
```

**Flow**:
1. Config created via `create_config()` factory
2. Audio file validated → AudioDocument
3. Processor transcribes AudioDocument with Config → TranscriptionResult
4. Batch processor aggregates multiple TranscriptionResults → ProcessingResult

---

## Data Validation Summary

| Entity | Validation Location | Validated By |
|--------|-------------------|--------------|
| AudioDocument | processor.validate_audio() | File system checks, metadata extraction |
| TranscriptionResult | processor.process_single_audio() | Post-processing validation |
| TranscriptionConfig | create_config() factory | Parameter range checks, enum validation |
| ProcessingResult | streaming.process_batch() | Statistics calculation, consistency checks |

---

## Error States

**AudioDocument Creation Failures**:
- File not found → `AudioNotFoundError`
- Unsupported format → `UnsupportedFormatError`
- Corrupted file → `CorruptedAudioError`
- Duration exceeds limit → `DurationExceededError`

**TranscriptionResult Failures** (success=False cases):
- No speech detected → error_message = "No speech detected in audio"
- Processing timeout → error_message = "Transcription timeout exceeded"
- Model processing error → error_message = "Whisper model processing failed: {details}"

**TranscriptionConfig Validation Failures**:
- Invalid parameters → `ValidationError` with specific parameter name

---

## Design Consistency

**Alignment with image_processor**:
- Document/Result/Config naming pattern maintained
- Optional fields use `Optional[Type]`
- Success boolean for result status
- Factory function for config creation with validation
- Progress callback signature matches

**Alignment with pdf_extractor**:
- Similar metadata extraction pattern
- File validation before processing
- Error message propagation in results

**Constitutional Compliance**:
- All entities are simple dataclasses (composition-first)
- No complex state machines (experimental simplicity)
- Clear single responsibility per entity
- No external dependencies in data models (minimal dependencies)

---

**Data Model Complete**: Ready for contract generation
