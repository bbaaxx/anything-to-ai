# Research: Audio-to-Text Transcription Module

**Branch**: `006-audio-to-text` | **Date**: 2025-09-29

## Overview

This document consolidates research findings for implementing an audio-to-text transcription module following the established patterns of `image_processor` and `pdf_extractor` modules. The module will use `lightning-whisper-mlx`, an MLX-optimized Whisper implementation for Apple Silicon.

## Technology Decisions

### Core Library: lightning-whisper-mlx

**Decision**: Use `lightning-whisper-mlx` for audio transcription

**Rationale**:
- 10x faster than Whisper CPP, 4x faster than current MLX Whisper implementation
- Optimized specifically for Apple Silicon (project requirement)
- Supports batched decoding for improved performance
- Provides distilled and quantized model variants for flexible performance/accuracy tradeoffs
- Maintained and actively developed

**Alternatives Considered**:
- `openai-whisper`: Original implementation, slower, CPU-focused
- `whisper.cpp`: C++ implementation, good performance but less Python integration
- `faster-whisper`: CPU/GPU optimized, not Apple Silicon specific

### Supported Models

**Decision**: Support all lightning-whisper-mlx models with user selection

**Models Available**:
- Standard: tiny, small, base, medium, large, large-v2, large-v3
- Distilled: distil-small.en, distil-medium.en, distil-large-v2, distil-large-v3

**Default**: medium with 4bit quantization (per spec clarifications)

**Rationale**:
- Provides flexibility for users to optimize speed vs accuracy
- Medium model balances performance and accuracy
- 4bit quantization reduces memory footprint while maintaining quality
- Matches user requirement for configurable quality/speed tradeoff

### Quantization Options

**Decision**: Support None, 4bit, 8bit quantization with 4bit as default

**Rationale**:
- 4bit quantization significantly reduces memory usage with minimal accuracy loss
- 8bit provides middle-ground option
- None available for maximum accuracy when needed
- Follows lightning-whisper-mlx library capabilities

### Audio Format Support

**Decision**: Support mp3, wav, m4a formats (per spec clarifications)

**Rationale**:
- Most common audio formats for user content
- Covers podcasts (mp3), recordings (wav), and Apple ecosystem (m4a)
- Whisper models handle various audio formats internally
- Reduces complexity by focusing on common formats

**Implementation Note**: Use file extension validation initially, rely on Whisper's audio loading

## Architecture Patterns

### Module Structure (following existing patterns)

**Pattern Source**: `image_processor` module structure

**Core Components**:
1. **models.py**: Data classes for AudioDocument, TranscriptionResult, TranscriptionConfig, ProcessingResult
2. **exceptions.py**: Exception hierarchy starting with AudioProcessingError base class
3. **processor.py**: Core transcription logic using lightning-whisper-mlx
4. **cli.py**: Command-line interface with argparse
5. **__init__.py**: Public API exports (process_audio, process_audio_batch, validate_audio, create_config)
6. **__main__.py**: CLI entry point
7. **progress.py**: Progress callback handling for long audio files
8. **streaming.py**: Batch processing with progress updates
9. **model_loader.py**: Whisper model loading and caching

**File Size Constraint**: Each file ≤ 250 lines (constitutional requirement)

### API Pattern (following image_processor)

**Functions**:
- `process_audio(file_path, config) -> TranscriptionResult`
- `process_audio_batch(file_paths, config) -> ProcessingResult`
- `validate_audio(file_path) -> AudioDocument`
- `create_config(**kwargs) -> TranscriptionConfig`
- `get_supported_formats() -> list`
- `get_audio_info(file_path) -> dict`

**Configuration Pattern**:
- Factory function `create_config()` with parameter validation
- Config object passed to all processing functions
- Default values matching common use cases

### Exception Hierarchy

**Base**: `AudioProcessingError(Exception)`

**Derived Classes**:
- `AudioNotFoundError`: File not found or inaccessible
- `UnsupportedFormatError`: Invalid audio format
- `CorruptedAudioError`: File corrupted or unreadable
- `TranscriptionError`: Whisper processing failed
- `NoSpeechDetectedError`: No speech content in audio (per spec)
- `DurationExceededError`: Audio exceeds 2-hour limit (per spec)
- `ValidationError`: Input parameter validation failures
- `ModelLoadError`: Whisper model loading failed
- `ProcessingTimeoutError`: Transcription timeout exceeded
- `ProcessingInterruptedError`: User or system interruption

### CLI Pattern (following image_processor)

**Arguments**:
- Positional: audio file paths (supports multiple)
- `--format`: Output format (plain/json)
- `--model`: Model selection (tiny/small/.../large-v3)
- `--quantization`: Quantization level (none/4bit/8bit)
- `--language`: Language hint (optional, auto-detect if not provided)
- `--batch-size`: Whisper decoder batch_size parameter
- `--output`: Output file path
- `--verbose`: Progress visibility
- `--quiet`: Suppress output

**Example**:
```bash
python -m audio_processor audio.mp3 --format json --model medium --quantization 4bit
```

## Technical Implementation Details

### lightning-whisper-mlx Integration

**Basic Usage Pattern**:
```python
from lightning_whisper_mlx import LightningWhisperMLX

whisper = LightningWhisperMLX(
    model="medium",
    batch_size=12,
    quant="4bit"
)
result = whisper.transcribe(audio_path="/path/to/audio.mp3")
text = result['text']
```

**Model Loading**:
- Models are auto-downloaded on first use
- Cache models in user's home directory
- Lazy loading: instantiate model only when needed
- Singleton pattern for model reuse across transcriptions

**Batch Processing**:
- Process multiple files sequentially (not parallel)
- Clean up memory between files for large batches
- Progress callbacks after each file completion

### Audio Validation

**Validation Steps**:
1. File existence check
2. File readability check
3. Format validation (extension check)
4. Duration extraction (using audio metadata libraries)
5. Duration limit enforcement (≤2 hours per spec)

**Metadata Extraction**:
- Use `pydub` or `mutagen` for audio metadata
- Extract: duration, format, sample rate, channels, file size
- Store in AudioDocument dataclass

### Progress Handling

**Long Audio Strategy**:
- Whisper processes entire file, no incremental updates
- Show "processing..." status during transcription
- Display progress based on file count for batch operations
- Time estimation based on audio duration and model speed

**Callback Pattern** (matching image_processor):
```python
def progress_callback(current: int, total: int):
    print(f"Processing {current}/{total} files...")
```

### Error Handling

**No Speech Detection**:
- Check Whisper result for empty/minimal text output
- Raise `NoSpeechDetectedError` with descriptive message
- Return error status in batch processing, continue to next file

**Graceful Degradation**:
- Corrupt file: skip and log error
- Model load failure: fail fast with clear message
- Timeout: allow configuration, fail with context

### Multilingual Support

**Language Detection** (per spec):
- Default: auto-detect language
- Optional: language hint parameter
- Use Whisper's built-in language detection
- Return detected language in results

**Implementation**:
```python
# Auto-detect
result = whisper.transcribe(audio_path)

# With hint
result = whisper.transcribe(audio_path, language="en")
```

## Performance Considerations

### Memory Management

**Constraints**:
- Large audio files consume significant memory
- MLX models require Apple Silicon GPU memory
- Batch processing must avoid OOM errors

**Strategies**:
- Process files sequentially, not in parallel
- Clear MLX cache between large files
- Monitor memory usage during batch operations
- Configurable batch_size parameter for Whisper decoder

### Processing Speed

**Expected Performance** (based on lightning-whisper-mlx benchmarks):
- 10x faster than Whisper CPP
- 4x faster than standard MLX Whisper
- Actual speed depends on: model size, quantization, audio duration, hardware

**Optimization**:
- Use distilled models for faster processing
- Enable quantization to reduce memory and improve speed
- Batch decoder operations (configured via batch_size parameter)

## Testing Strategy

### Contract Tests

**Test Coverage**:
- API function signatures match specification
- Exception types and hierarchy
- Configuration validation
- CLI argument parsing

**Test Files** (following existing pattern):
- `tests/contract/test_module_api.py`
- `tests/contract/test_exceptions.py`
- `tests/contract/test_cli_parser.py`

### Integration Tests

**Test Scenarios**:
- Single audio file transcription
- Batch processing multiple files
- Error handling (corrupt file, no speech, unsupported format)
- Progress callbacks
- Format output (plain, json)
- Model and quantization selection
- Language detection and hints
- Duration limit enforcement

**Test Files**:
- `tests/integration/test_single_audio.py`
- `tests/integration/test_batch_processing.py`
- `tests/integration/test_error_workflows.py`

**Test Data Requirements**:
- Sample audio files (mp3, wav, m4a)
- Corrupted audio file
- Silent audio file (no speech)
- Multi-language audio samples
- Long-duration audio (near 2-hour limit)

## Dependencies

**Primary**:
- `lightning-whisper-mlx`: Core transcription engine
- Python 3.13: Project standard

**Audio Handling**:
- `pydub` or `mutagen`: Audio metadata extraction
- Consider: lightweight alternative for minimal dependencies

**Standard Library**:
- `argparse`: CLI parsing
- `dataclasses`: Data structures
- `pathlib`: File path handling
- `json`: JSON output format

**Development**:
- `pytest`: Testing framework
- `pytest-asyncio`: Async test support (if needed)

## Open Questions Resolved

All clarifications addressed in spec Session 2025-09-29:
- ✅ Audio formats: mp3, wav, m4a
- ✅ Language support: Multilingual with optional hints, auto-detect default
- ✅ Timestamp data: Not needed, text only
- ✅ Duration limit: 2 hours maximum
- ✅ Model selection: All library models available
- ✅ Quantization: None, 4bit, 8bit with 4bit default
- ✅ Default model: medium with 4bit quantization
- ✅ No speech handling: Error with "no speech detected" message
- ✅ Batch size: Configurable Whisper decoder batch_size parameter

## Constitutional Compliance

**250-Line Rule**:
- Module broken into 9 small files (similar to image_processor)
- Each file focused on single responsibility
- Estimated file sizes all under 200 lines

**Minimal Dependencies**:
- Core dependency: lightning-whisper-mlx (justified - no alternative for MLX)
- Audio metadata: evaluate lightweight options
- All other functionality uses standard library

**Composition-First**:
- Processor composed of: validator, model_loader, transcriber
- Streaming processor wraps base processor
- CLI uses processor without duplication

**Modular Architecture**:
- Clear interfaces: process_audio(), validate_audio(), create_config()
- Module replaceable without affecting system
- No tight coupling to other modules

**Experimental Mindset**:
- Learning: MLX optimization techniques
- Quick iteration: start with basic transcription, enhance with features
- Document: Whisper model performance characteristics

---

**Research Complete**: All NEEDS CLARIFICATION resolved, technology decisions made, patterns identified
