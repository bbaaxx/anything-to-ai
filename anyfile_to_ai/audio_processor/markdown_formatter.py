"""Markdown formatting for audio transcription results."""

from typing import Any
from anyfile_to_ai.audio_processor.models import TranscriptionSegment


def format_markdown(result: dict[str, Any]) -> str:
    """
    Format audio transcription result as markdown.

    Args:
        result: Dictionary with transcription data:
            - filename: str - Audio filename
            - duration: float - Duration in seconds
            - model: str - Whisper model used
            - language: str - Language code
            - segments: List[Dict] - Transcript segments with optional timestamps/speakers
            - metadata: dict | None - Optional processing metadata

    Returns:
        str: Markdown-formatted transcript with structure:
            - YAML frontmatter (if metadata present)
            - H1: Transcription title with filename
            - Metadata: Duration, Model, Language as bullet list
            - H2: Segments with timestamps and speakers (if available)
            - Content: Transcript text (no escaping)
            - Extended Metadata section (if present)

    Note:
        Special characters are NOT escaped per research.md decision (2025-10-02).
        Fallback: If no speakers/timestamps, output as plain paragraphs.
    """
    filename = result.get("filename", "audio.mp3")
    duration = result.get("duration", 0.0)
    model = result.get("model", "unknown")
    language = result.get("language", "en")
    segments = result.get("segments", [])
    metadata = result.get("metadata")

    lines = []

    if metadata is not None:
        lines.append("---")
        lines.append(f"processing_timestamp: {metadata['processing']['timestamp']}")
        lines.append(f"model_version: {metadata['processing']['model_version']}")
        lines.append(f"detected_language: {metadata['source'].get('detected_language', 'unknown')}")
        lines.append("---")
        lines.append("")

    # Build markdown document
    lines.extend([f"# Transcription: {filename}", ""])

    # Add metadata section
    duration_formatted = _format_duration(duration)
    lines.append(f"- Duration: {duration_formatted}")
    lines.append(f"- Model: {model}")
    lines.append(f"- Language: {language}")
    lines.append("")

    # Add transcript segments
    for segment in segments:
        text = segment.get("text", "")
        start = segment.get("start", 0.0)
        speaker = segment.get("speaker")

        # Format with timestamp and speaker (always show for segments)
        timestamp = _format_timestamp(start)
        speaker_label = speaker if speaker else "Speaker"
        lines.append(f"## [{timestamp}] {speaker_label}")
        lines.append("")

        # Add segment text (no escaping)
        if text.strip():
            lines.append(text.strip())
            lines.append("")

    # Fallback: If no segments, output plain text
    if not segments and "text" in result:
        lines.append(result["text"])
        lines.append("")

    if metadata is not None:
        lines.append("## Processing Metadata")
        lines.append("")
        lines.append(f"- Processing Time: {metadata['processing']['processing_time_seconds']:.2f}s")
        lines.append(f"- Sample Rate: {metadata['source'].get('sample_rate_hz', 'unknown')} Hz")
        lines.append(f"- Channels: {metadata['source'].get('channels', 'unknown')}")
        if metadata["source"].get("language_confidence") != "unavailable":
            conf = metadata["source"].get("language_confidence", 0)
            lines.append(f"- Language Confidence: {conf:.2%}")
        lines.append("")

    return "\n".join(lines)


def _format_duration(seconds: float) -> str:
    """Format duration as HH:MM:SS."""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)

    return f"{hours:02d}:{minutes:02d}:{secs:02d}"


def _format_timestamp(seconds: float) -> str:
    """Format timestamp as HH:MM:SS."""
    return _format_duration(seconds)


def format_timestamp(seconds: float) -> str:
    """
    Format timestamp in HH:MM:SS.CC format (centisecond precision).

    Args:
        seconds: Time in seconds (0.0 to 7200.0)

    Returns:
        str: Formatted timestamp (e.g., "00:01:23.45")

    Raises:
        ValueError: If seconds is negative or exceeds 7200.0
    """
    if seconds < 0.0:
        msg = f"Timestamp cannot be negative: {seconds}"
        raise ValueError(msg)
    if seconds > 7200.0:
        msg = f"Timestamp exceeds maximum duration (2 hours): {seconds}"
        raise ValueError(msg)

    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    centiseconds = round((seconds % 1.0) * 100)

    return f"{hours:02d}:{minutes:02d}:{secs:02d}.{centiseconds:02d}"


def format_segments_markdown(segments: list[TranscriptionSegment], include_text: bool = True) -> str:
    """
    Format timestamped segments for markdown output.

    Args:
        segments: List of TranscriptionSegment objects
        include_text: Whether to include full text (default: True)

    Returns:
        str: Formatted string with one line per segment
    """
    if not segments:
        return ""

    lines = []
    for segment in segments:
        timestamp = format_timestamp(segment.start)
        if include_text:
            lines.append(f"[{timestamp}] {segment.text}")
        else:
            lines.append(f"[{timestamp}]")

    return "\n".join(lines)
