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
    # Convert ExtractionResult to dict format for format_markdown
    result_dict = {
        "filename": filename,
        "pages": [{"number": page.page_number, "text": page.text} for page in extraction_result.pages],
    }
    return format_markdown(result_dict)
