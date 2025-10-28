"""Markdown formatting for PDF extraction results."""

from typing import Any
from anyfile_to_ai.pdf_extractor.models import ExtractionResult


def format_markdown(result: dict[str, Any]) -> str:
    """
    Format PDF extraction result as markdown.

    Args:
        result: Dictionary with 'filename' and 'pages' keys
            - filename: str - PDF filename
            - pages: List[Dict] - Page results with 'number' and 'text' keys

    Returns:
        str: Markdown-formatted document with structure:
            - H1: Document title with filename
            - H2: Page sections
            - Content: Plain paragraphs (no escaping)

    Note:
        Special characters are NOT escaped per research.md decision (2025-10-02).
        Structure detection not implemented initially - output as plain paragraphs.
    """
    filename = result.get("filename", "document.pdf")
    pages = result.get("pages", [])

    # Build markdown document
    lines = [f"# PDF Document: {filename}", ""]

    for page in pages:
        page_num = page.get("number", 1)
        text = page.get("text", "")

        # Add page heading
        lines.append(f"## Page {page_num}")
        lines.append("")

        # Add page content as plain text (no escaping)
        if text.strip():
            lines.append(text.strip())
        else:
            lines.append("(empty page)")

        lines.append("")  # Blank line between pages

    return "\n".join(lines)


def format_extraction_result(extraction_result: ExtractionResult, filename: str) -> str:
    """
    Format ExtractionResult dataclass as markdown.

    Args:
        extraction_result: ExtractionResult instance
        filename: Original PDF filename

    Returns:
        str: Markdown-formatted document
    """
    lines = []

    if extraction_result.metadata is not None:
        lines.append("---")
        lines.append(f"processing_timestamp: {extraction_result.metadata['processing']['timestamp']}")
        lines.append(f"model_version: {extraction_result.metadata['processing']['model_version']}")
        lines.append(f"file_path: {extraction_result.metadata['source']['file_path']}")
        lines.append(f"page_count: {extraction_result.metadata['source'].get('page_count', 'unknown')}")
        lines.append("---")
        lines.append("")

    result_dict = {
        "filename": filename,
        "pages": [{"number": page.page_number, "text": page.text} for page in extraction_result.pages],
    }
    lines.append(format_markdown(result_dict))

    if extraction_result.metadata is not None:
        lines.append("")
        lines.append("## Metadata")
        lines.append("")
        lines.append("### Processing")
        lines.append(f"- Timestamp: {extraction_result.metadata['processing']['timestamp']}")
        lines.append(f"- Model: {extraction_result.metadata['processing']['model_version']}")
        lines.append(f"- Processing Time: {extraction_result.metadata['processing']['processing_time_seconds']:.2f}s")
        lines.append("")
        lines.append("### Source")
        lines.append(f"- File: {extraction_result.metadata['source']['file_path']}")
        if extraction_result.metadata["source"].get("file_size_bytes") != "unavailable":
            file_size_mb = extraction_result.metadata["source"].get("file_size_bytes", 0) / 1024 / 1024
            lines.append(f"- Size: {file_size_mb:.2f} MB")
        lines.append(f"- Pages: {extraction_result.metadata['source'].get('page_count', 'unknown')}")
        if extraction_result.metadata["source"].get("creation_date") != "unavailable":
            lines.append(f"- Created: {extraction_result.metadata['source'].get('creation_date', 'unknown')}")

    return "\n".join(lines)
