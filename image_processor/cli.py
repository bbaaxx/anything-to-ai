"""Command-line interface for image processing module."""

import argparse
from typing import List, Optional
from .models import ProcessingResult


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
        """
    )

    parser.add_argument('images', nargs='+', help='Image file paths or directories')
    parser.add_argument('--style', choices=['detailed', 'brief', 'technical'],
                       default='detailed', help='Description style preference')
    parser.add_argument('--max-length', type=int, default=500, metavar='N',
                       help='Maximum description length in characters')
    parser.add_argument('--batch-size', type=int, default=4, metavar='N',
                       help='Number of images to process simultaneously')
    parser.add_argument('--timeout', type=int, default=60, metavar='SECONDS',
                       help='Processing timeout per image')
    parser.add_argument('--output', '-o', help='Output file path')
    parser.add_argument('--format', choices=['plain', 'json', 'csv'],
                       default='plain', help='Output format')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Enable verbose progress output')
    parser.add_argument('--quiet', '-q', action='store_true',
                       help='Suppress all output except results')

    return parser


def main(args: Optional[List[str]] = None) -> int:
    """Main CLI entry point."""
    import sys

    try:
        parser = create_cli_parser()
        parsed_args = parser.parse_args(args)

        # Expand image paths
        image_paths = expand_image_paths(parsed_args.images)

        if not image_paths:
            print("No valid image files found", file=sys.stderr)
            return 1

        # Create configuration
        from . import create_config, process_images

        def progress_handler(current, total):
            if parsed_args.verbose and not parsed_args.quiet:
                print(f"Processing {current}/{total} images...", file=sys.stderr)

        config = create_config(
            description_style=parsed_args.style,
            max_length=parsed_args.max_length,
            batch_size=parsed_args.batch_size,
            progress_callback=progress_handler if parsed_args.verbose else None
        )
        config.timeout_seconds = parsed_args.timeout

        # Process images
        results = process_images(image_paths, config)

        # Format and output results
        output_text = format_output(results, parsed_args.format)

        if parsed_args.output:
            with open(parsed_args.output, 'w') as f:
                f.write(output_text)
            if not parsed_args.quiet:
                print(f"Results saved to {parsed_args.output}", file=sys.stderr)
        else:
            if not parsed_args.quiet:
                print(output_text)

        return 0 if results.success else 1

    except Exception as e:
        if not getattr(parsed_args, 'quiet', False):
            print(f"Error: {e}", file=sys.stderr)
        return 1


def format_output(result: ProcessingResult, format_type: str) -> str:
    """Format processing results for CLI output."""
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
                    "success": r.success
                }
                for r in result.results
            ]
        }
        return json.dumps(data, indent=2)

    elif format_type == "csv":
        import csv
        import io
        output = io.StringIO()
        writer = csv.writer(output)

        # Write header
        writer.writerow(["image_path", "description", "confidence_score", "processing_time", "success"])

        # Write data rows
        for r in result.results:
            writer.writerow([
                r.image_path,
                r.description.replace('\n', ' ').replace('\r', ''),
                r.confidence_score or "",
                r.processing_time,
                r.success
            ])

        return output.getvalue()

    else:  # plain format
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
            lines.append("")

        return "\n".join(lines)


def expand_image_paths(paths: List[str]) -> List[str]:
    """Expand directory paths and glob patterns to image files."""
    import os
    import glob

    expanded = []
    image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'}

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
    return sorted(list(set(expanded)))
