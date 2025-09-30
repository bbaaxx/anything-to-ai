# Audio Transcription Module

A Python module for transcribing audio files using MLX-optimized Whisper models for Apple Silicon. Features multilingual support, batch processing, and progress tracking.

## Installation & Setup

### Prerequisites
- Python 3.13 or higher
- Apple Silicon Mac (for MLX optimization)
- UV package manager (recommended) or pip

### Dependencies Installation

Using UV (recommended):
```bash
uv add lightning-whisper-mlx
```

Using pip:
```bash
pip install lightning-whisper-mlx
```

### Verify Installation
```bash
python -m audio_processor --help
```

## CLI Usage

### Basic Audio Transcription
```bash
# Transcribe single audio file
python -m audio_processor audio.mp3

# Transcribe with JSON output
python -m audio_processor audio.mp3 --format json

# Transcribe with progress tracking
python -m audio_processor audio.mp3 --verbose

# Transcribe multiple files
python -m audio_processor audio1.mp3 audio2.wav audio3.m4a
```

### Model Selection
```bash
# Use tiny model for speed
python -m audio_processor audio.mp3 --model tiny

# Use large model for accuracy
python -m audio_processor audio.mp3 --model large-v3

# List of available models:
# tiny, small, distil-small.en, base, medium, distil-medium.en,
# large, large-v2, distil-large-v2, large-v3, distil-large-v3
```

### Language Options
```bash
# Auto-detect language (default)
python -m audio_processor audio.mp3

# Specify language hint for better accuracy
python -m audio_processor audio.mp3 --language es  # Spanish
python -m audio_processor audio.mp3 --language fr  # French
python -m audio_processor audio.mp3 --language en  # English
```

### Output Formats
```bash
# JSON output (structured)
python -m audio_processor audio.mp3 --format json

# Plain text output (default)
python -m audio_processor audio.mp3 --format plain

# Save output to file
python -m audio_processor audio.mp3 --format json --output transcript.json
```

### Advanced Options
```bash
# Batch processing with progress
python -m audio_processor *.mp3 --verbose

# Custom batch size (decoder parameter)
python -m audio_processor audio.mp3 --batch-size 24

# With timeout
python -m audio_processor audio.mp3 --timeout 300

# Quiet mode (results only)
python -m audio_processor audio.mp3 --quiet
```

### CLI Options
- `--format, -f`: Output format (`plain`, `json`)
- `--model, -m`: Whisper model selection (default: `medium`)
- `--quantization, -q`: Quantization level (`none`, `4bit`, `8bit`) - default: `none`
- `--language, -l`: Language hint (ISO 639-1 code, e.g., `en`, `es`)
- `--batch-size, -b`: Whisper decoder batch size (default: 12)
- `--output, -o`: Save results to file
- `--timeout, -t`: Processing timeout per file in seconds (default: 600)
- `--verbose, -v`: Enable progress output
- `--quiet`: Suppress all output except results

## Python API Usage

### Basic Transcription

```python
from audio_processor import process_audio, create_config

# Simple single audio transcription
result = process_audio('audio.mp3')
if result.success:
    print(f"Text: {result.text}")
    print(f"Language: {result.detected_language}")
    print(f"Time: {result.processing_time:.2f}s")
```

### Batch Processing
```python
from audio_processor import process_audio_batch

# Process multiple audio files
audio_files = ['audio1.mp3', 'audio2.wav', 'audio3.m4a']
results = process_audio_batch(audio_files)

print(f"Processed {results.successful_count}/{results.total_files} files")
for result in results.results:
    if result.success:
        print(f"{result.audio_path}: {result.text[:100]}...")
```

### Advanced Configuration

```python
from audio_processor import process_audio_batch, create_config

# Custom configuration
config = create_config(
    model="large-v3",
    quantization="none",
    language="en",
    output_format="json",
    verbose=True
)

results = process_audio_batch(audio_files, config)
```

### Streaming with Progress

```python
from audio_processor import process_audio_batch, create_config

def progress_handler(current, total):
    print(f"Processing {current}/{total} audio files...")

config = create_config(
    model="medium",
    progress_callback=progress_handler,
    verbose=True
)

# Batch process with progress updates
results = process_audio_batch(audio_files, config)
```

### Audio Validation

```python
from audio_processor import validate_audio, get_audio_info, get_supported_formats

# Validate audio before processing
try:
    audio_doc = validate_audio('audio.mp3')
    print(f"Valid: {audio_doc.format}, {audio_doc.duration}s")
except Exception as e:
    print(f"Invalid audio: {e}")

# Get audio metadata without processing
info = get_audio_info('audio.mp3')
print(f"Duration: {info['duration']}s, Format: {info['format']}")

# Check supported formats
formats = get_supported_formats()
print(f"Supported formats: {formats}")  # ['m4a', 'mp3', 'wav']
```

## Configuration Options

### TranscriptionConfig Parameters

- **model** (`str`): Whisper model selection (default: `"medium"`)
  - Speed: `tiny` > `small` > `base` > `medium` > `large`
  - Accuracy: `tiny` < `small` < `base` < `medium` < `large`
  - Distilled models (e.g., `distil-medium.en`) are faster
- **quantization** (`str`): Model quantization (default: `"none"`)
  - `"none"`: No quantization (best accuracy, slower)
  - `"4bit"`: 4-bit quantization (faster, less memory) - may have compatibility issues
  - `"8bit"`: 8-bit quantization (middle ground) - may have compatibility issues
- **batch_size** (`int`): Decoder batch size (default: 12, range: 1-128)
- **language** (`str | None`): Language hint or `None` for auto-detect (default: `None`)
- **output_format** (`str`): Output format (`"plain"` or `"json"`)
- **timeout_seconds** (`int`): Processing timeout per file (default: 600)
- **progress_callback** (`Callable[[int, int], None]`): Progress tracking function
- **verbose** (`bool`): Enable verbose output (default: `False`)
- **max_duration_seconds** (`int`): Maximum audio duration (default: 7200 = 2 hours)

### Model Selection Guide

**For Speed**:
```python
config = create_config(model="tiny", quantization="none")
```

**For Accuracy**:
```python
config = create_config(model="large-v3", quantization="none")
```

**Balanced**:
```python
config = create_config(model="medium", quantization="none")  # Default
```

## Environment Setup

### Performance Optimization
```bash
# MLX is automatically optimized for Apple Silicon
# No additional environment setup needed

# For memory-constrained environments, use smaller models
python -m audio_processor audio.mp3 --model tiny
```

### Model Downloads
- Models are automatically downloaded on first use
- Cached in `~/.cache/huggingface/`
- First run will download ~1-5GB depending on model

## Error Handling

### Exception Types

```python
from audio_processor import (
    AudioProcessingError,
    AudioNotFoundError,
    UnsupportedFormatError,
    CorruptedAudioError,
    NoSpeechDetectedError,
    DurationExceededError,
    ValidationError,
    ModelLoadError,
    ProcessingTimeoutError
)

try:
    result = process_audio('audio.mp3')
except AudioNotFoundError:
    print("Audio file not found")
except UnsupportedFormatError:
    print("Unsupported audio format (use mp3, wav, or m4a)")
except NoSpeechDetectedError:
    print("No speech detected in audio")
except DurationExceededError:
    print("Audio exceeds 2-hour limit")
except ModelLoadError as e:
    print(f"Failed to load Whisper model: {e}")
except ProcessingTimeoutError:
    print("Transcription timed out")
```

### Common Issues & Solutions

**No Speech Detected**:
```python
# Whisper may hallucinate text on silence/noise
# Use a different model or check audio quality
config = create_config(model="large-v3")
```

**Out of Memory**:
```python
# Use smaller model or reduce batch size
config = create_config(model="tiny", batch_size=6)
```

**Slow Processing**:
```python
# Use distilled models for faster processing
config = create_config(model="distil-medium.en")
```

**Model Download Issues**:
```bash
# Check internet connection
# Models are downloaded from HuggingFace
# Manually pre-download if needed
```

## Data Models

### Core Objects

```python
# Audio metadata
AudioDocument(file_path, format, duration, sample_rate, file_size, channels)

# Transcription result for single audio
TranscriptionResult(
    audio_path, text, confidence_score, processing_time,
    model_used, quantization, detected_language, success, error_message
)

# Batch processing result
ProcessingResult(
    success, results, total_files, successful_count,
    failed_count, total_processing_time, average_processing_time, error_summary
)
```

## Examples with Sample Data

```python
# Example with project sample audio
sample_audio = "sample-data/audio/podcast.mp3"

# Quick transcription
result = process_audio(sample_audio)
print(f"Transcription: {result.text}")

# Batch process all samples
import glob
sample_audios = glob.glob("sample-data/audio/*.mp3")
results = process_audio_batch(sample_audios)

# With language hint
config = create_config(language="en")
result = process_audio(sample_audio, config)
print(f"English transcription: {result.text}")
```

## Supported Audio Formats

- **MP3** (.mp3)
- **WAV** (.wav)
- **M4A** (.m4a)

Check programmatically:
```python
from audio_processor import get_supported_formats
print(get_supported_formats())  # ['m4a', 'mp3', 'wav']
```

## Performance Notes

- **MLX Optimization**: 10x faster than CPU Whisper on Apple Silicon
- **Model Size**: Larger models are more accurate but slower
- **Audio Length**: ~1 minute audio takes ~5-15 seconds with medium model
- **Memory Usage**: ~2-4GB RAM for medium model
- **Batch Processing**: Sequential processing (not parallel) for stability

## Limitations

- **Maximum Duration**: 2 hours per audio file
- **Language Detection**: Auto-detection works best with clear speech
- **Background Noise**: May affect transcription quality
- **Quantization**: 4bit/8bit quantization has compatibility issues with current MLX version (use `none`)
- **No Timestamps**: Text-only output (no word-level timestamps)

## Integration Examples

### With PDF Extractor
```python
from pdf_extractor import extract_text
from audio_processor import process_audio

# Extract PDF and transcribe related audio
pdf_text = extract_text('document.pdf')
audio_text = process_audio('presentation.mp3')

combined = f"Document: {pdf_text.pages[0].text}\n\nAudio: {audio_text.text}"
```

### With Image Processor
```python
from image_processor import process_image
from audio_processor import process_audio

# Describe image and transcribe audio
img_result = process_image('slide.jpg')
audio_result = process_audio('narration.mp3')

print(f"Image: {img_result.description}")
print(f"Narration: {audio_result.text}")
```

## Testing

```bash
# Run contract tests
PYTHONPATH=. uv run pytest tests/contract/test_audio*.py -v

# Test with sample audio
python -m audio_processor sample-data/audio/silence.mp3 --verbose
```

## Version

Current version: 0.1.0

## License

[Your License Here]