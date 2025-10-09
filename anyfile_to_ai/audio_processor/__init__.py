"""
Audio Processor Module - Whisper-based Audio-to-Text Transcription

This module provides audio transcription capabilities using MLX-optimized Whisper models.

Public API:
    - process_audio: Process single audio file
    - process_audio_batch: Process multiple audio files
    - validate_audio: Validate audio file and extract metadata
    - create_config: Create transcription configuration
    - get_supported_formats: Get list of supported audio formats
    - get_audio_info: Get audio file metadata

Data Models:
    - AudioDocument: Audio file metadata
    - TranscriptionResult: Transcription result with text and metadata
    - TranscriptionConfig: Configuration for transcription
    - ProcessingResult: Batch processing result

Exceptions:
    - AudioProcessingError: Base exception
    - AudioNotFoundError: File not found
    - UnsupportedFormatError: Format not supported
    - CorruptedAudioError: File corrupted
    - TranscriptionError: Transcription failed
    - NoSpeechDetectedError: No speech detected
    - DurationExceededError: Duration limit exceeded
    - ValidationError: Parameter validation failed
    - ModelLoadError: Model loading failed
    - ProcessingTimeoutError: Processing timeout
    - ProcessingInterruptedError: Processing interrupted
"""

__version__ = "0.1.0"

# Import public API functions
from anyfile_to_ai.audio_processor.processor import (
    process_audio,
    validate_audio,
    get_supported_formats,
    get_audio_info,
)
from anyfile_to_ai.audio_processor.streaming import process_audio_batch
from anyfile_to_ai.audio_processor.config import create_config

# Import data models
from anyfile_to_ai.audio_processor.models import (
    AudioDocument,
    TranscriptionResult,
    TranscriptionConfig,
    ProcessingResult,
)

# Import exceptions
from anyfile_to_ai.audio_processor.exceptions import (
    AudioProcessingError,
    AudioNotFoundError,
    UnsupportedFormatError,
    CorruptedAudioError,
    TranscriptionError,
    NoSpeechDetectedError,
    DurationExceededError,
    ValidationError,
    ModelLoadError,
    ProcessingTimeoutError,
    ProcessingInterruptedError,
)

# Public API exports
__all__ = [
    # Data models
    "AudioDocument",
    "AudioNotFoundError",
    # Exceptions
    "AudioProcessingError",
    "CorruptedAudioError",
    "DurationExceededError",
    "ModelLoadError",
    "NoSpeechDetectedError",
    "ProcessingInterruptedError",
    "ProcessingResult",
    "ProcessingTimeoutError",
    "TranscriptionConfig",
    "TranscriptionError",
    "TranscriptionResult",
    "UnsupportedFormatError",
    "ValidationError",
    "create_config",
    "get_audio_info",
    "get_supported_formats",
    # Functions
    "process_audio",
    "process_audio_batch",
    "validate_audio",
]
