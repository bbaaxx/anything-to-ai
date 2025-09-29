"""CLI contracts for image VLM processing module.

Defines the command-line interface contracts matching the user scenarios
from the specification.
"""

import argparse
from typing import List, Optional
from .api import ProcessingConfig, ProcessingResult, DescriptionResult


def create_cli_parser() -> argparse.ArgumentParser:
    """Create command-line argument parser.

    Returns:
        ArgumentParser configured for image processing commands
    """
    parser = argparse.ArgumentParser(
        description="Process images with VLM to generate text descriptions",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python -m image_processor image.jpg
    python -m image_processor *.png --style brief
    python -m image_processor folder/ --batch-size 2 --output results.json
    python -m image_processor image.jpg --model large --timeout 120
        """
    )

    # Positional arguments
    parser.add_argument(
        'images',
        nargs='+',
        help='Image file paths or directories to process'
    )

    # Processing options
    parser.add_argument(
        '--style',
        choices=['detailed', 'brief', 'technical'],
        default='detailed',
        help='Description style preference (default: detailed)'
    )

    parser.add_argument(
        '--max-length',
        type=int,
        default=500,
        metavar='N',
        help='Maximum description length in characters (default: 500)'
    )

    parser.add_argument(
        '--batch-size',
        type=int,
        default=4,
        metavar='N',
        help='Number of images to process simultaneously (default: 4)'
    )

    parser.add_argument(
        '--model',
        choices=['small', 'medium', 'large'],
        default='small',
        help='Model size preference (default: small)'
    )

    parser.add_argument(
        '--timeout',
        type=int,
        default=60,
        metavar='SECONDS',
        help='Processing timeout per image (default: 60)'
    )

    # Output options
    parser.add_argument(
        '--output',
        '-o',
        help='Output file path (JSON format, default: stdout)'
    )

    parser.add_argument(
        '--format',
        choices=['plain', 'json', 'csv'],
        default='plain',
        help='Output format (default: plain)'
    )

    parser.add_argument(
        '--verbose',
        '-v',
        action='store_true',
        help='Enable verbose progress output'
    )

    parser.add_argument(
        '--quiet',
        '-q',
        action='store_true',
        help='Suppress all output except results'
    )

    return parser


def main(args: Optional[List[str]] = None) -> int:
    """Main CLI entry point.

    Args:
        args: Command line arguments (defaults to sys.argv)

    Returns:
        Exit code (0 for success, non-zero for failure)
    """
    pass


def process_cli_images(image_paths: List[str], config: ProcessingConfig) -> ProcessingResult:
    """Process images from CLI with configuration.

    Args:
        image_paths: List of image file paths
        config: Processing configuration from CLI args

    Returns:
        ProcessingResult with all processing outcomes
    """
    pass


def format_output(result: ProcessingResult, format_type: str) -> str:
    """Format processing results for CLI output.

    Args:
        result: Processing result to format
        format_type: Output format (plain, json, csv)

    Returns:
        Formatted string for output
    """
    pass


def format_single_result(result: DescriptionResult, format_type: str) -> str:
    """Format single image result for CLI output.

    Args:
        result: Single image processing result
        format_type: Output format (plain, json, csv)

    Returns:
        Formatted string for single result
    """
    pass


def progress_callback(current: int, total: int) -> None:
    """CLI progress callback for verbose output.

    Args:
        current: Current image number
        total: Total number of images
    """
    pass


def expand_image_paths(paths: List[str]) -> List[str]:
    """Expand directory paths and glob patterns to image files.

    Args:
        paths: List of file paths, directories, or patterns

    Returns:
        List of individual image file paths

    Raises:
        ValidationError: No valid images found
    """
    pass


def validate_cli_args(args: argparse.Namespace) -> None:
    """Validate CLI arguments for consistency.

    Args:
        args: Parsed command line arguments

    Raises:
        ValidationError: Invalid argument combination
    """
    pass
