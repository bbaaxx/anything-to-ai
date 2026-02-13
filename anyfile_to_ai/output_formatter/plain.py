"""Plain-text profile-aware rendering."""

from typing import Any

from .errors import InvalidPayloadError


def render_plain(profile: str, payload: dict[str, Any]) -> str:
    """Render plain output for a profile."""
    content = payload.get("content")
    if not isinstance(content, str):
        raise InvalidPayloadError("Payload must include string field 'content'")

    if profile == "text":
        tags = payload.get("tags", [])
        lines = ["SUMMARY:", content, "", "TAGS:"]
        for tag in tags:
            lines.append(f"- {tag}")
        return "\n".join(lines)

    if profile == "audio" and payload.get("segments"):
        segment_lines: list[str] = []
        for segment in payload["segments"]:
            ts = segment.get("display_timestamp") or segment.get("timestamp")
            text = segment.get("text", "")
            if ts:
                segment_lines.append(f"[{ts}] {text}".rstrip())
            else:
                segment_lines.append(text)
        return "\n".join(segment_lines)

    return content
