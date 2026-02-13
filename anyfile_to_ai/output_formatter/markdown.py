"""Markdown profile-aware rendering helpers."""

from typing import Any

from .errors import InvalidPayloadError


def format_audio_timestamp(seconds: float) -> str:
    """Format seconds into HH:MM:SS.CC with bounds validation."""
    if seconds < 0:
        msg = f"Timestamp cannot be negative: {seconds}"
        raise InvalidPayloadError(msg)
    if seconds > 7200:
        msg = f"Timestamp exceeds maximum duration (2 hours): {seconds}"
        raise InvalidPayloadError(msg)

    total_centiseconds = round(seconds * 100)
    hours = total_centiseconds // 360000
    remaining = total_centiseconds % 360000
    minutes = remaining // 6000
    remaining %= 6000
    secs = remaining // 100
    centiseconds = remaining % 100
    return f"{hours:02d}:{minutes:02d}:{secs:02d}.{centiseconds:02d}"


def _format_audio_duration(seconds: float) -> str:
    """Format seconds into HH:MM:SS."""
    total_seconds = int(seconds)
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    secs = total_seconds % 60
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"


def render_markdown(profile: str, payload: dict[str, Any]) -> str:
    """Render markdown output for a profile."""
    content = payload.get("content", "")
    if not isinstance(content, str):
        raise InvalidPayloadError("Payload must include string field 'content'")

    if profile == "text":
        lines = ["# Summary", "", content, ""]
        tags = payload.get("tags", [])
        if tags:
            lines.extend(["## Tags", ""])
            lines.extend(f"- {tag}" for tag in tags)
            lines.append("")
        return "\n".join(lines)

    if profile == "pdf":
        filename = payload.get("filename", "document.pdf")
        pages = payload.get("pages", [])
        lines = [f"# PDF Document: {filename}", ""]
        if pages:
            for page in pages:
                number = page.get("number", 1)
                text = page.get("text", "")
                lines.extend([f"## Page {number}", "", text or "(empty page)", ""])
            return "\n".join(lines)
        lines.append(content)
        return "\n".join(lines)

    if profile == "image":
        entries = payload.get("results", [])
        lines = ["# Image Descriptions", ""]
        for entry in entries:
            filename = entry.get("filename", "unknown.jpg")
            image_path = entry.get("image_path", filename)
            description = entry.get("description", "")
            lines.extend([f"## {filename}", "", f"![{description or 'Image'}]({image_path})", "", description or "Description unavailable - VLM processing failed.", ""])
        return "\n".join(lines)

    if profile == "audio":
        segments = payload.get("segments", [])
        metadata = payload.get("metadata")
        use_legacy_heading = payload.get("legacy_audio_heading", True)
        use_legacy_document = payload.get("legacy_audio_document", False)
        use_hhmmss_timestamp = payload.get("legacy_audio_timestamp_no_centiseconds", False)
        lines: list[str] = []

        if use_legacy_document:
            filename = payload.get("filename", "audio.mp3")
            duration = float(payload.get("duration", 0.0))
            model = payload.get("model", "unknown")
            language = payload.get("language", "en")
            lines.extend(
                [
                    f"# Transcription: {filename}",
                    "",
                    f"- Duration: {_format_audio_duration(duration)}",
                    f"- Model: {model}",
                    f"- Language: {language}",
                    "",
                ]
            )

        for segment in segments:
            start = float(segment.get("start", 0.0))
            text = str(segment.get("text", ""))
            ts = _format_audio_duration(start) if use_hhmmss_timestamp else format_audio_timestamp(start)
            if use_legacy_heading:
                speaker = segment.get("speaker") or "Speaker"
                lines.extend([f"## [{ts}] {speaker}", "", text, ""])
            else:
                lines.append(f"[{ts}] {text}".rstrip())
        if not segments:
            lines.append(content)

        if use_legacy_document and metadata is not None:
            lines.append("")
            lines.append("## Processing Metadata")
            lines.append("")
            lines.append(f"- Processing Time: {metadata['processing']['processing_time_seconds']:.2f}s")
            lines.append(f"- Sample Rate: {metadata['source'].get('sample_rate_hz', 'unknown')} Hz")
            lines.append(f"- Channels: {metadata['source'].get('channels', 'unknown')}")
            if metadata["source"].get("language_confidence") != "unavailable":
                conf = metadata["source"].get("language_confidence", 0)
                lines.append(f"- Language Confidence: {conf:.2%}")

        return "\n".join(lines)

    return content
