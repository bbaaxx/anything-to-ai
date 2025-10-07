"""Markdown formatting for text summarization results."""

from typing import Any


def format_markdown(result: dict[str, Any]) -> str:
    """
    Format text summarization result as markdown.

    Args:
        result: Dictionary with summarization data:
            - summary: str - Generated summary text
            - tags: List[str] - Content tags
            - metadata: Optional[Dict] - Processing metadata

    Returns:
        str: Markdown-formatted summary with structure:
            - H1: "Summary"
            - Summary paragraphs (natural text)
            - H2: "Tags" section
            - Tags as bullet list
            - H2: "Metadata" section (if included)

    Note:
        Special characters are NOT escaped per research.md decision (2025-10-02).
        Summary text output as natural paragraphs.
    """
    summary = result.get("summary", "")
    tags = result.get("tags", [])
    metadata = result.get("metadata")

    # Build markdown document
    lines = ["# Summary", ""]

    # Add summary text (no escaping)
    if summary.strip():
        # Split into paragraphs if needed (preserve existing paragraph structure)
        summary_paragraphs = summary.strip().split("\n\n")
        for para in summary_paragraphs:
            if para.strip():
                lines.append(para.strip())
                lines.append("")

    # Add tags section
    if tags:
        lines.append("## Tags")
        lines.append("")
        for tag in tags:
            lines.append(f"- {tag}")
        lines.append("")

    # Add optional metadata section
    if metadata:
        lines.append("## Metadata")
        lines.append("")
        _format_metadata(metadata, lines)
        lines.append("")

    return "\n".join(lines)


def _format_metadata(metadata: dict[str, Any], lines: list) -> None:
    """Format metadata as bullet list."""
    if "input_length" in metadata:
        lines.append(f"- Input length: {metadata['input_length']} words")

    if "chunked" in metadata:
        chunked_text = "Yes" if metadata["chunked"] else "No"
        lines.append(f"- Chunked: {chunked_text}")

    if "processing_time" in metadata:
        time_val = metadata["processing_time"]
        lines.append(f"- Processing time: {time_val:.1f}s")
