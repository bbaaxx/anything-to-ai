"""
Core audio processing functionality using Whisper.
"""

import os
import time
from pathlib import Path
from typing import Any
from anyfile_to_ai.audio_processor.models import (
    AudioDocument,
    TranscriptionResult,
    TranscriptionConfig,
)
from anyfile_to_ai.audio_processor.exceptions import (
    AudioNotFoundError,
    UnsupportedFormatError,
    CorruptedAudioError,
    DurationExceededError,
    NoSpeechDetectedError,
)
from anyfile_to_ai.audio_processor.model_loader import get_model_loader


# Supported audio formats
SUPPORTED_FORMATS = ["m4a", "mp3", "wav"]


def get_supported_formats() -> list[str]:
    """
    Get list of supported audio formats.

    Returns:
        List[str]: Sorted list of supported formats
    """
    return sorted(SUPPORTED_FORMATS)


def validate_audio(file_path: str) -> AudioDocument:
    """
    Validate audio file and extract metadata.

    Args:
        file_path: Path to audio file

    Returns:
        AudioDocument: Audio metadata document

    Raises:
        AudioNotFoundError: File not found
        UnsupportedFormatError: Format not supported
        CorruptedAudioError: File corrupted
        DurationExceededError: Duration exceeds limit
    """
    # Check file existence
    if not os.path.exists(file_path):
        raise AudioNotFoundError(f"Audio file not found: {file_path}", audio_path=file_path)

    # Check file is readable
    if not os.path.isfile(file_path):
        raise AudioNotFoundError(f"Path is not a file: {file_path}", audio_path=file_path)

    # Get file extension
    file_ext = Path(file_path).suffix.lower().lstrip(".")

    # Validate format
    if file_ext not in SUPPORTED_FORMATS:
        raise UnsupportedFormatError(
            f"Unsupported audio format: {file_ext}. Supported formats: {', '.join(SUPPORTED_FORMATS)}",
            audio_path=file_path,
        )

    # Get file size
    try:
        file_size = os.path.getsize(file_path)
    except Exception as e:
        raise CorruptedAudioError(f"Cannot read file size: {e!s}", audio_path=file_path)

    # Extract audio metadata using ffprobe or similar
    # For now, use a simple approach with estimated values
    # In production, would use a library like mutagen or ffprobe
    try:
        # Placeholder: Extract metadata
        # This would use actual audio metadata extraction in production
        duration = _estimate_duration(file_path, file_size)
        sample_rate = 44100  # Placeholder
        channels = 2  # Placeholder

        # Validate duration limit (2 hours = 7200 seconds)
        if duration > 7200:
            raise DurationExceededError(
                f"Audio duration ({duration}s) exceeds 2-hour limit (7200s)",
                audio_path=file_path,
            )

        return AudioDocument(
            file_path=file_path,
            format=file_ext,
            duration=duration,
            sample_rate=sample_rate,
            file_size=file_size,
            channels=channels,
        )

    except (DurationExceededError, AudioNotFoundError, UnsupportedFormatError):
        raise
    except Exception as e:
        raise CorruptedAudioError(f"Failed to extract audio metadata: {e!s}", audio_path=file_path)


def _estimate_duration(file_path: str, file_size: int) -> float:
    """
    Estimate audio duration based on file size.

    This is a placeholder. In production, would use actual metadata extraction.

    Args:
        file_path: Path to audio file
        file_size: File size in bytes

    Returns:
        float: Estimated duration in seconds
    """
    # Very rough estimation: assume ~128kbps bitrate for mp3
    # 1 minute of 128kbps audio = ~960KB
    estimated_duration = (file_size / 1024 / 960) * 60
    return max(1.0, estimated_duration)  # Minimum 1 second


def get_audio_info(file_path: str) -> dict[str, Any]:
    """
    Get audio file metadata without processing.

    Args:
        file_path: Path to audio file

    Returns:
        Dict with audio metadata

    Raises:
        AudioNotFoundError: File not found
        UnsupportedFormatError: Format not supported
    """
    audio_doc = validate_audio(file_path)

    return {
        "file_path": audio_doc.file_path,
        "format": audio_doc.format,
        "duration": audio_doc.duration,
        "sample_rate": audio_doc.sample_rate,
        "file_size": audio_doc.file_size,
        "channels": audio_doc.channels,
    }


def process_audio(file_path: str, config: TranscriptionConfig | None = None) -> TranscriptionResult:
    """
    Process single audio file and generate transcribed text.

    Args:
        file_path: Path to audio file
        config: Processing configuration (uses defaults if not provided)

    Returns:
        TranscriptionResult: Transcription result with text and metadata

    Raises:
        AudioNotFoundError: Audio file not found
        UnsupportedFormatError: Audio format not supported
        CorruptedAudioError: Audio file corrupted
        DurationExceededError: Audio exceeds 2-hour limit
        ModelLoadError: Whisper model failed to load
        ProcessingTimeoutError: Processing exceeded timeout
    """
    # Use default config if not provided
    if config is None:
        from anyfile_to_ai.audio_processor.config import create_config

        config = create_config()

    # Validate audio file
    audio_doc = validate_audio(file_path)

    # Check duration against config max
    if audio_doc.duration > config.max_duration_seconds:
        raise DurationExceededError(
            f"Audio duration ({audio_doc.duration}s) exceeds configured limit ({config.max_duration_seconds}s)",
            audio_path=file_path,
        )

    # Record start time
    start_time = time.time()

    try:
        # Load model
        model_loader = get_model_loader()
        whisper_model = model_loader.load_model(config.model, config.quantization, config.batch_size)

        # Transcribe audio
        transcribe_kwargs = {"audio_path": file_path}
        if config.language:
            transcribe_kwargs["language"] = config.language

        result = whisper_model.transcribe(**transcribe_kwargs)

        # Extract transcription text
        text = result.get("text", "").strip()

        # Detect no speech
        if not text or len(text) < 5:  # Threshold for "no speech"
            raise NoSpeechDetectedError("No speech detected in audio", audio_path=file_path)

        # Extract metadata
        detected_language = result.get("language", config.language)
        confidence_score = None  # lightning-whisper-mlx may not provide this

        # Calculate processing time
        processing_time = time.time() - start_time

        return TranscriptionResult(
            audio_path=file_path,
            text=text,
            confidence_score=confidence_score,
            processing_time=processing_time,
            model_used=config.model,
            quantization=config.quantization,
            detected_language=detected_language,
            success=True,
            error_message=None,
        )

    except NoSpeechDetectedError:
        # Return failed result for no speech
        processing_time = time.time() - start_time
        return TranscriptionResult(
            audio_path=file_path,
            text="",
            confidence_score=None,
            processing_time=processing_time,
            model_used=config.model,
            quantization=config.quantization,
            detected_language=None,
            success=False,
            error_message="No speech detected in audio",
        )

    except Exception as e:
        # Return failed result for other errors
        processing_time = time.time() - start_time
        error_msg = f"Transcription failed: {e!s}"

        return TranscriptionResult(
            audio_path=file_path,
            text="",
            confidence_score=None,
            processing_time=processing_time,
            model_used=config.model,
            quantization=config.quantization,
            detected_language=None,
            success=False,
            error_message=error_msg,
        )
