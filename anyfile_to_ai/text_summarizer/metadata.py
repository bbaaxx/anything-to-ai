"""Metadata extraction for text summarization."""

from datetime import datetime, timezone, UTC
from pathlib import Path


def extract_text_metadata(
    text: str,
    file_path: str | None,
    processing_time: float,
    model_version: str,
    detected_language: str | None,
    chunked: bool,
    chunk_count: int | None,
    user_config: dict,
    effective_config: dict,
) -> dict:
    """
    Extend SummaryMetadata with universal metadata fields.

    Args:
        text: Input text that was summarized
        file_path: Path to input file, or None for stdin
        processing_time: Processing duration in seconds
        model_version: LLM model version used
        detected_language: ISO 639-1 language code or None
        chunked: Whether text was chunked for processing
        chunk_count: Number of chunks, or None if not chunked
        user_config: User-provided configuration
        effective_config: Effective configuration after defaults

    Returns:
        Dictionary containing universal metadata fields for SummaryMetadata extension
    """
    return {
        "processing_timestamp": datetime.now(UTC).isoformat(),
        "model_version": model_version,
        "configuration": {"user_provided": user_config, "effective": effective_config},
        "source": _extract_text_source_metadata(text, file_path, detected_language, chunked, chunk_count),
    }


def _extract_text_source_metadata(text: str, file_path: str | None, detected_language: str | None, chunked: bool, chunk_count: int | None) -> dict:
    """Extract text-specific source metadata."""
    words = text.split()
    word_count = len(words)
    char_count = len(text)

    path = file_path if file_path else "unavailable"

    file_size: int | str = "unavailable"
    if file_path:
        try:
            file_size = Path(file_path).stat().st_size
        except (OSError, FileNotFoundError):
            file_size = "unavailable"

    lang = detected_language if detected_language else "unavailable"

    return {
        "file_path": path,
        "file_size_bytes": file_size,
        "input_length_words": word_count,
        "input_length_chars": char_count,
        "detected_language": lang,
        "chunked": chunked,
        "chunk_count": chunk_count,
    }
