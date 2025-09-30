"""Command line interface logic."""
import argparse
import json
import sys
from .reader import extract_text, get_pdf_info
from .streaming import extract_text_streaming
from .models import ExtractionConfig
from .enhanced_models import EnhancedExtractionConfig
from .image_integration import PDFImageProcessor
from .output_formatters import OutputFormatter
from .exceptions import (
    PDFNotFoundError,
    PDFCorruptedError,
    PDFPasswordProtectedError,
    PDFNoTextError,
    ProcessingInterruptedError,
    VLMConfigurationError,
    ConfigurationValidationError,
)


class CLICommands:
    """Command line interface contract implementation."""

    @staticmethod
    def extract(
        file_path: str,
        stream: bool = False,
        format_type: str = "plain",
        progress: bool = False,
        include_images: bool = False,
        image_style: str = "detailed",
        image_fallback: str = "[Image: processing failed]",
        max_images: int = None,
        batch_size: int = 4
    ) -> int:
        """
        CLI extract command with optional image processing.

        Args:
            file_path: Path to PDF file
            stream: Enable streaming mode
            format_type: Output format (plain/json/csv)
            progress: Show progress information
            include_images: Enable AI-generated image descriptions
            image_style: Style of image descriptions (brief/detailed/technical)
            image_fallback: Fallback text when image processing fails
            max_images: Maximum images to process per page
            batch_size: Batch size for image processing

        Returns:
            Exit code (0 for success, non-zero for error)
        """
        try:
            def progress_callback(current, total):
                if progress:
                    percentage = (current / total) * 100
                    print(f"Progress: {current}/{total} ({percentage:.1f}%)", file=sys.stderr)

            # Use enhanced extraction if images are requested
            if include_images:
                # Create image processing configuration
                try:
                    from image_processor.config import ProcessingConfig
                    image_config = ProcessingConfig(style=image_style)
                except ImportError:
                    # Fallback if image_processor config not available
                    image_config = None

                enhanced_config = EnhancedExtractionConfig(
                    streaming_enabled=stream,
                    progress_callback=progress_callback if progress else None,
                    output_format=format_type,
                    include_images=True,
                    image_processing_config=image_config,
                    image_fallback_text=image_fallback,
                    max_images_per_page=max_images,
                    image_batch_size=batch_size
                )

                processor = PDFImageProcessor()

                if stream:
                    # Enhanced streaming mode
                    enhanced_pages = []
                    for enhanced_page in processor.extract_with_images_streaming(file_path, enhanced_config):
                        enhanced_pages.append(enhanced_page)
                        if progress:
                            print(f"Page {enhanced_page.page_number}: {enhanced_page.images_found} images found", file=sys.stderr)

                    OutputFormatter.print_enhanced_output(enhanced_pages, format_type, file_path, streaming=True)
                else:
                    # Enhanced non-streaming mode
                    result = processor.extract_with_images(file_path, enhanced_config)
                    OutputFormatter.print_enhanced_result(result, format_type, file_path)
            else:
                # Regular extraction (backward compatibility)
                config = ExtractionConfig(
                    streaming_enabled=stream,
                    progress_callback=progress_callback if progress else None,
                    output_format=format_type
                )

                if stream:
                    pages = []
                    for page_result in extract_text_streaming(file_path, config):
                        pages.append(page_result)

                    OutputFormatter.print_regular_output(pages, format_type, file_path, streaming=True)
                else:
                    result = extract_text(file_path, config)
                    OutputFormatter.print_regular_result(result, format_type, file_path)

            return 0

        except VLMConfigurationError as e:
            print(f"Error: {e}", file=sys.stderr)
            return 7
        except ConfigurationValidationError as e:
            print(f"Error: {e}", file=sys.stderr)
            return 8
        except PDFNotFoundError:
            print(f"Error: PDF file not found: {file_path}", file=sys.stderr)
            return 1
        except PDFCorruptedError:
            print(f"Error: PDF file is corrupted: {file_path}", file=sys.stderr)
            return 2
        except PDFPasswordProtectedError:
            print(f"Error: PDF file is password protected: {file_path}", file=sys.stderr)
            return 3
        except PDFNoTextError:
            print(f"Error: PDF contains no extractable text: {file_path}", file=sys.stderr)
            return 4
        except ProcessingInterruptedError:
            print(f"Error: PDF processing was interrupted: {file_path}", file=sys.stderr)
            return 5
        except Exception as e:
            print(f"Error: Unexpected error: {e}", file=sys.stderr)
            return 6

    @staticmethod
    def info(file_path: str) -> int:
        """
        CLI info command - show PDF information.

        Args:
            file_path: Path to PDF file

        Returns:
            Exit code (0 for success, non-zero for error)
        """
        try:
            info = get_pdf_info(file_path)
            info["file_path"] = file_path
            info["requires_streaming"] = info["is_large_file"]

            print(json.dumps(info, indent=2))
            return 0

        except PDFNotFoundError:
            print(f"Error: PDF file not found: {file_path}", file=sys.stderr)
            return 1
        except PDFCorruptedError:
            print(f"Error: PDF file is corrupted: {file_path}", file=sys.stderr)
            return 2
        except Exception as e:
            print(f"Error: Unexpected error: {e}", file=sys.stderr)
            return 6


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(description="PDF text extraction tool")
    parser.add_argument("--version", action="version", version="pdf-extractor 0.1.0")

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Extract command
    extract_parser = subparsers.add_parser("extract", help="Extract text from PDF")
    extract_parser.add_argument("file_path", help="Path to PDF file")
    extract_parser.add_argument(
        "--stream", action="store_true", help="Enable streaming mode for large files"
    )
    extract_parser.add_argument(
        "--format", choices=["plain", "json", "csv"], default="plain",
        help="Output format (default: plain)"
    )
    extract_parser.add_argument(
        "--progress", action="store_true", help="Show progress information"
    )

    # Enhanced image processing options
    extract_parser.add_argument(
        "--include-images", action="store_true",
        help="Include AI-generated descriptions of images found in PDF"
    )
    extract_parser.add_argument(
        "--image-style", choices=["brief", "detailed", "technical"], default="detailed",
        help="Style of image descriptions (default: detailed)"
    )
    extract_parser.add_argument(
        "--image-fallback", default="[Image: processing failed]",
        help="Fallback text when image processing fails"
    )
    extract_parser.add_argument(
        "--max-images", type=int,
        help="Maximum number of images to process per page"
    )
    extract_parser.add_argument(
        "--batch-size", type=int, default=4,
        help="Batch size for image processing (1-10, default: 4)"
    )

    # Info command
    info_parser = subparsers.add_parser("info", help="Show PDF information")
    info_parser.add_argument("file_path", help="Path to PDF file")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    if args.command == "extract":
        return CLICommands.extract(
            args.file_path,
            stream=args.stream,
            format_type=args.format,
            progress=args.progress,
            include_images=args.include_images,
            image_style=args.image_style,
            image_fallback=args.image_fallback,
            max_images=args.max_images,
            batch_size=args.batch_size
        )
    elif args.command == "info":
        return CLICommands.info(args.file_path)

    return 0


if __name__ == "__main__":
    sys.exit(main())
