"""Command-line interface for image processing module."""

import argparse
from .models import ProcessingResult, DescriptionResult


def create_cli_parser() -> argparse.ArgumentParser:
    """Create command-line argument parser."""
    parser = argparse.ArgumentParser(
        description="Process images with VLM to generate text descriptions",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python -m image_processor image.jpg
    python -m image_processor *.png --style brief
    python -m image_processor folder/ --batch-size 2 --output results.json
        """,
    )

    parser.add_argument("images", nargs="+", help="Image file paths or directories")
    parser.add_argument("--style", choices=["detailed", "brief", "technical"], default="detailed", help="Description style preference")
    parser.add_argument("--max-length", type=int, default=500, metavar="N", help="Maximum description length in characters")
    parser.add_argument("--batch-size", type=int, default=4, metavar="N", help="Number of images to process simultaneously")
    parser.add_argument("--timeout", type=int, default=60, metavar="SECONDS", help="Processing timeout per image")
    parser.add_argument("--output", "-o", help="Output file path")
    parser.add_argument("--format", choices=["plain", "json", "csv", "markdown"], default="plain", help="Output format")
    parser.add_argument("--include-metadata", action="store_true", help="Include source file and processing metadata in output")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose progress output")
    parser.add_argument("--quiet", "-q", action="store_true", help="Suppress all output except results")

    return parser


def _check_vlm_environment():
    """Check for VLM environment configuration."""
    import os

    return os.getenv("VISION_MODEL")


def _create_image_config(parsed_args):
    """Create image processing configuration."""
    from . import create_config
    from .vlm_exceptions import VLMConfigurationError

    def progress_handler(current, total):
        if parsed_args.verbose and not parsed_args.quiet:
            pass

    try:
        config = create_config(description_style=parsed_args.style, max_length=parsed_args.max_length, batch_size=parsed_args.batch_size, progress_callback=progress_handler if parsed_args.verbose else None)
        config.timeout_seconds = parsed_args.timeout
        return config
    except VLMConfigurationError as e:
        if hasattr(e, "suggested_fix") and e.suggested_fix:
            pass
        return None


def _handle_image_output(results, parsed_args):
    """Handle image processing output."""

    output_text = format_output(results, parsed_args.format)

    if parsed_args.output:
        with open(parsed_args.output, "w") as f:
            f.write(output_text)
        if not parsed_args.quiet:
            pass
    elif not parsed_args.quiet:
        pass


def main(args: list[str] | None = None) -> int:
    """Main CLI entry point."""

    try:
        from . import process_images

        parser = create_cli_parser()
        parsed_args = parser.parse_args(args)

        # Check for VLM environment configuration
        if not _check_vlm_environment():
            return 1

        # Expand image paths
        image_paths = expand_image_paths(parsed_args.images)

        if not image_paths:
            return 1

        # Create configuration
        config = _create_image_config(parsed_args)
        if config is None:
            return 1

        # Show VLM model info in verbose mode
        if parsed_args.verbose and not parsed_args.quiet:
            pass

        # Process images
        results = process_images(image_paths, config, parsed_args.include_metadata)

        # Handle output
        _handle_image_output(results, parsed_args)

        return 0 if results.success else 1

    except Exception:
        if not getattr(parsed_args, "quiet", False):
            pass
        return 1


def format_output(result: ProcessingResult, format_type: str) -> str:
    """Format processing results for CLI output."""
    if format_type == "markdown":
        import os
        from .markdown_formatter import format_markdown

        # Convert ProcessingResult to list of dicts for formatter
        results_list = [
            {
                "filename": os.path.basename(r.image_path),
                "image_path": r.image_path,
                "description": r.description,
                "processing_success": r.success,
                "metadata": getattr(r, "metadata", None),
            }
            for r in result.results
        ]
        return format_markdown(results_list)

    if format_type == "json":
        import json

        data = {
            "success": result.success,
            "total_images": result.total_images,
            "successful_count": result.successful_count,
            "failed_count": result.failed_count,
            "total_processing_time": result.total_processing_time,
            "results": [
                {
                    "image_path": r.image_path,
                    "description": r.description,
                    "confidence_score": r.confidence_score,
                    "processing_time": r.processing_time,
                    "model_used": r.model_used,
                    "success": r.success,
                    # Enhanced VLM fields
                    "technical_metadata": getattr(r, "technical_metadata", None),
                    "vlm_processing_time": getattr(r, "vlm_processing_time", None),
                    "model_version": getattr(r, "model_version", None),
                    **({"metadata": r.metadata} if getattr(r, "metadata", None) is not None else {}),
                }
                for r in result.results
            ],
        }
        return json.dumps(data, indent=2)

    if format_type == "csv":
        import csv
        import io

        output = io.StringIO()
        writer = csv.writer(output)

        # Check if any result has metadata
        has_metadata = any(getattr(r, "metadata", None) is not None for r in result.results)

        # Write enhanced header
        headers = ["image_path", "description", "confidence_score", "processing_time", "success", "format", "width", "height", "file_size", "model_used", "model_version"]
        if has_metadata:
            headers.extend(["metadata.processing.timestamp", "metadata.processing.model_version", "metadata.source.file_path", "metadata.source.format"])
        writer.writerow(headers)

        # Write data rows
        for r in result.results:
            tech_meta = getattr(r, "technical_metadata", {}) or {}
            row = [
                r.image_path,
                r.description.replace("\n", " ").replace("\r", ""),
                r.confidence_score or "",
                r.processing_time,
                r.success,
                tech_meta.get("format", ""),
                tech_meta.get("dimensions", [0, 0])[0] if tech_meta.get("dimensions") else "",
                tech_meta.get("dimensions", [0, 0])[1] if tech_meta.get("dimensions") else "",
                tech_meta.get("file_size", ""),
                r.model_used,
                getattr(r, "model_version", ""),
            ]
            if has_metadata:
                metadata = getattr(r, "metadata", None)
                if metadata:
                    row.extend(
                        [
                            metadata["processing"]["timestamp"],
                            metadata["processing"]["model_version"],
                            metadata["source"]["file_path"],
                            metadata["source"].get("format", ""),
                        ]
                    )
                else:
                    row.extend(["", "", "", ""])
            writer.writerow(row)

        return output.getvalue()

    # plain format
    lines = []
    lines.append(f"Processed {result.total_images} images")
    lines.append(f"Successful: {result.successful_count}, Failed: {result.failed_count}")
    lines.append(f"Total time: {result.total_processing_time:.2f}s")
    lines.append("")

    for r in result.results:
        status = "✓" if r.success else "✗"
        lines.append(f"{status} {r.image_path}")
        if r.success and r.description:
            lines.append(f"   {r.description}")

            # Add technical metadata in plain format
            tech_meta = getattr(r, "technical_metadata", {}) or {}
            if tech_meta:
                dims = tech_meta.get("dimensions", [0, 0])
                lines.append(f"   Format: {tech_meta.get('format', 'Unknown')}, Size: {dims[0]}x{dims[1]}, {tech_meta.get('file_size', 0)} bytes")
        lines.append("")

    return "\n".join(lines)


def format_single_result(result: DescriptionResult, format_type: str) -> str:
    """Format single processing result for CLI output."""
    if format_type == "json":
        import json

        data = {
            "image_path": result.image_path,
            "description": result.description,
            "confidence_score": result.confidence_score,
            "processing_time": result.processing_time,
            "model_used": result.model_used,
            "success": result.success,
            # Enhanced VLM fields
            "technical_metadata": result.technical_metadata,
            "vlm_processing_time": result.vlm_processing_time,
            "model_version": result.model_version,
        }
        if result.metadata is not None:
            data["metadata"] = result.metadata
        return json.dumps(data, indent=2)

    if format_type == "csv":
        tech_meta = result.technical_metadata or {}
        dims = tech_meta.get("dimensions", [0, 0])
        return (
            f"{result.image_path},{result.description},{result.confidence_score},{result.processing_time},{result.success},{tech_meta.get('format', '')},{dims[0]},{dims[1]},{tech_meta.get('file_size', 0)},{result.model_used},{result.model_version}"
        )

    # plain format
    lines = [f"Image: {result.image_path}"]
    if result.success:
        lines.append(f"Description: {result.description}")
        if result.confidence_score is not None:
            lines.append(f"Confidence: {result.confidence_score:.2f}")
        lines.append(f"Processing time: {result.processing_time:.2f}s")
        if result.model_used:
            lines.append(f"Model: {result.model_used}")

        # Add technical metadata if available
        if result.technical_metadata:
            tech_meta = result.technical_metadata
            dims = tech_meta.get("dimensions", [0, 0])
            lines.append(f"Format: {tech_meta.get('format', 'Unknown')}, Size: {dims[0]}x{dims[1]}, {tech_meta.get('file_size', 0)} bytes")
    else:
        lines.append("Status: Failed")

    return "\n".join(lines)


def expand_image_paths(paths: list[str]) -> list[str]:
    """Expand directory paths and glob patterns to image files."""
    import os
    import glob

    expanded = []
    image_extensions = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"}

    for path in paths:
        if os.path.isfile(path):
            # Direct file path
            if any(path.lower().endswith(ext) for ext in image_extensions):
                expanded.append(path)
        elif os.path.isdir(path):
            # Directory - find all image files
            for ext in image_extensions:
                pattern = os.path.join(path, f"*{ext}")
                expanded.extend(glob.glob(pattern))
                # Also try uppercase
                pattern = os.path.join(path, f"*{ext.upper()}")
                expanded.extend(glob.glob(pattern))
        else:
            # Treat as glob pattern
            matches = glob.glob(path)
            for match in matches:
                if os.path.isfile(match) and any(match.lower().endswith(ext) for ext in image_extensions):
                    expanded.append(match)

    # Remove duplicates and sort
    return sorted(set(expanded))
