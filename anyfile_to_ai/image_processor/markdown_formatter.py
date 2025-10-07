"""Markdown formatting for image processing results."""

from typing import Any


def format_markdown(results: list[dict[str, Any]]) -> str:
    """
    Format image processing results as markdown.

    Args:
        results: List of image result dictionaries with keys:
            - filename: str - Image filename
            - image_path: str - Path to image file
            - description: str - VLM-generated description
            - processing_success: bool - Whether VLM processing succeeded

    Returns:
        str: Markdown-formatted document with structure:
            - H1: "Image Descriptions"
            - H2: Section per image (filename)
            - Markdown image syntax: ![description](path)
            - Detailed description paragraph

    Note:
        Special characters are NOT escaped per research.md decision (2025-10-02).
        VLM failures output generic fallback text.
    """
    lines = ["# Image Descriptions", ""]

    for result in results:
        filename = result.get("filename", "unknown.jpg")
        image_path = result.get("image_path", filename)
        description = result.get("description", "")
        success = result.get("processing_success", True)

        # Add image section heading
        lines.append(f"## {filename}")
        lines.append("")

        # Add markdown image reference
        if success and description:
            # Use description as-is (no escaping)
            lines.append(f"![{description}]({image_path})")
            lines.append("")
            # Add detailed description paragraph
            lines.append(description)
        else:
            # VLM failure fallback
            lines.append(f"![Image]({image_path})")
            lines.append("")
            lines.append("Description unavailable - VLM processing failed.")

        lines.append("")  # Blank line between images

    return "\n".join(lines)
