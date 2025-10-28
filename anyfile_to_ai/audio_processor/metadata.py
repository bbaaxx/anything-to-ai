"""Metadata extraction for audio processing."""

from datetime import datetime, timezone, UTC
from typing import Any

from .models import AudioDocument


def extract_audio_metadata(audio_doc: AudioDocument, processing_time: float, model_version: str, detected_language: str | None, language_confidence: float | None, user_config: dict, effective_config: dict) -> dict:
    """
    Extract comprehensive metadata for audio processing.

    Args:
        audio_doc: Validated AudioDocument with file metadata
        processing_time: Processing duration in seconds
        model_version: Whisper model version used
        detected_language: ISO 639-1 language code or None
        language_confidence: Language detection confidence (0.0-1.0) or None
        user_config: User-provided configuration
        effective_config: Effective configuration after defaults

    Returns:
        Complete metadata dictionary with processing, configuration, and source sections
    """
    return {
        "processing": _extract_processing_metadata(processing_time, model_version),
        "configuration": _extract_configuration_metadata(user_config, effective_config),
        "source": _extract_audio_source_metadata(audio_doc, detected_language, language_confidence),
    }


def _extract_processing_metadata(processing_time: float, model_version: str) -> dict:
    """Extract universal processing metadata."""
    return {
        "timestamp": datetime.now(UTC).isoformat(),
        "model_version": model_version,
        "processing_time_seconds": processing_time,
    }


def _extract_configuration_metadata(user_config: dict, effective_config: dict) -> dict:
    """Extract configuration metadata."""
    return {"user_provided": user_config, "effective": effective_config}


def _extract_audio_source_metadata(audio_doc: AudioDocument, detected_language: str | None, language_confidence: float | None) -> dict:
    """Extract audio-specific source metadata."""
    lang = detected_language if detected_language else "unavailable"

    if language_confidence is not None:
        conf: float | str = language_confidence
    else:
        conf = "unavailable"

    metadata: dict[str, Any] = {
        "file_path": audio_doc.file_path,
        "file_size_bytes": audio_doc.file_size,
        "duration_seconds": audio_doc.duration,
        "sample_rate_hz": audio_doc.sample_rate,
        "channels": audio_doc.channels,
        "format": audio_doc.format,
        "detected_language": lang,
        "language_confidence": conf,
    }

    return metadata
