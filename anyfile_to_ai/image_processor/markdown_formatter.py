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
            - metadata: dict | None - Optional metadata

    Returns:
        str: Markdown-formatted document with structure:
            - YAML frontmatter (if metadata present)
            - H1: "Image Descriptions"
            - H2: Section per image (filename)
            - Markdown image syntax: ![description](path)
            - Detailed description paragraph
            - Metadata section (if present)

    Note:
        Special characters are NOT escaped per research.md decision (2025-10-02).
        VLM failures output generic fallback text.
    """
    lines = []

    if results and results[0].get("metadata") is not None:
        metadata = results[0]["metadata"]
        lines.append("---")
        lines.append(f"processing_timestamp: {metadata['processing']['timestamp']}")
        lines.append(f"model_version: {metadata['processing']['model_version']}")
        lines.append("---")
        lines.append("")

    lines.extend(["# Image Descriptions", ""])

    for result in results:
        filename = result.get("filename", "unknown.jpg")
        image_path = result.get("image_path", filename)
        description = result.get("description", "")
        success = result.get("processing_success", True)
        metadata = result.get("metadata")

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

        if metadata is not None:
            lines.append("")
            lines.append("### Metadata")
            lines.append(f"- Processing Time: {metadata['processing']['processing_time_seconds']:.2f}s")
            lines.append(f"- Model: {metadata['processing']['model_version']}")
            if metadata["source"].get("dimensions"):
                dims = metadata["source"]["dimensions"]
                lines.append(f"- Dimensions: {dims['width']}x{dims['height']}")
            if metadata["source"].get("format"):
                lines.append(f"- Format: {metadata['source']['format']}")
            if metadata["source"].get("exif") and metadata["source"]["exif"]:
                lines.append("- EXIF Data: Available")
                camera_info = metadata["source"].get("camera_info", {})
                if camera_info.get("make"):
                    lines.append(f"  - Camera: {camera_info.get('make')} {camera_info.get('model', '')}")

        lines.append("")  # Blank line between images

    return "\n".join(lines)
