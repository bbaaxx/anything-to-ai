"""
Exception hierarchy for audio processing errors.
"""

from typing import Optional


class AudioProcessingError(Exception):
    """Base exception for all audio processing errors."""

    def __init__(self, message: str, audio_path: Optional[str] = None):
        super().__init__(message)
        self.audio_path = audio_path


class AudioNotFoundError(AudioProcessingError):
    """Audio file not found or inaccessible."""
    pass


class UnsupportedFormatError(AudioProcessingError):
    """Audio format not supported (only mp3, wav, m4a allowed)."""
    pass


class CorruptedAudioError(AudioProcessingError):
    """Audio file corrupted or unreadable."""
    pass


class TranscriptionError(AudioProcessingError):
    """Whisper transcription processing failed."""
    pass


class NoSpeechDetectedError(AudioProcessingError):
    """No speech content detected in audio."""
    pass


class DurationExceededError(AudioProcessingError):
    """Audio duration exceeds maximum limit (2 hours)."""
    pass


class ValidationError(AudioProcessingError):
    """Input parameter validation failed."""

    def __init__(self, message: str, parameter_name: Optional[str] = None, audio_path: Optional[str] = None):
        super().__init__(message, audio_path)
        self.parameter_name = parameter_name


class ModelLoadError(AudioProcessingError):
    """Whisper model failed to load."""

    def __init__(self, message: str, model_name: str, audio_path: Optional[str] = None):
        super().__init__(message, audio_path)
        self.model_name = model_name


class ProcessingTimeoutError(AudioProcessingError):
    """Processing exceeded timeout limit."""

    def __init__(self, message: str, timeout_seconds: int, audio_path: Optional[str] = None):
        super().__init__(message, audio_path)
        self.timeout_seconds = timeout_seconds


class ProcessingInterruptedError(AudioProcessingError):
    """Processing interrupted by user or system."""

    def __init__(self, message: str, files_processed: int, total_files: int, audio_path: Optional[str] = None):
        super().__init__(message, audio_path)
        self.files_processed = files_processed
        self.total_files = total_files
