"""Command line interface logic."""
import argparse
import json
import sys
from .reader import extract_text, get_pdf_info
from .streaming import extract_text_streaming
from .models import ExtractionConfig
from .exceptions import (
    PDFNotFoundError,
    PDFCorruptedError,
    PDFPasswordProtectedError,
    PDFNoTextError,
    ProcessingInterruptedError,
)


class CLICommands:
    """Command line interface contract implementation."""

    @staticmethod
    def extract(
        file_path: str,
        stream: bool = False,
        format_type: str = "plain",
        progress: bool = False
    ) -> int:
        """
        CLI extract command.

        Args:
            file_path: Path to PDF file
            stream: Enable streaming mode
            format_type: Output format (plain/json)
            progress: Show progress information

        Returns:
            Exit code (0 for success, non-zero for error)
        """
        try:
            def progress_callback(current, total):
                if progress:
                    percentage = (current / total) * 100
                    print(f"Progress: {current}/{total} ({percentage:.1f}%)", file=sys.stderr)

            config = ExtractionConfig(
                streaming_enabled=stream,
                progress_callback=progress_callback if progress else None,
                output_format=format_type
            )

            if stream:
                # Streaming mode
                pages = []
                for page_result in extract_text_streaming(file_path, config):
                    pages.append(page_result)

                if format_type == "json":
                    output = {
                        "success": True,
                        "file_path": file_path,
                        "total_pages": len(pages),
                        "total_chars": sum(p.char_count for p in pages),
                        "pages": [
                            {
                                "page_number": p.page_number,
                                "text": p.text,
                                "char_count": p.char_count,
                                "extraction_time": p.extraction_time
                            } for p in pages
                        ]
                    }
                    print(json.dumps(output, indent=2))
                else:
                    for page in pages:
                        print(page.text)
            else:
                # Non-streaming mode
                result = extract_text(file_path, config)

                if format_type == "json":
                    output = {
                        "success": result.success,
                        "file_path": file_path,
                        "total_pages": result.total_pages,
                        "total_chars": result.total_chars,
                        "processing_time": result.processing_time,
                        "pages": [
                            {
                                "page_number": p.page_number,
                                "text": p.text,
                                "char_count": p.char_count,
                                "extraction_time": p.extraction_time
                            } for p in result.pages
                        ]
                    }
                    print(json.dumps(output, indent=2))
                else:
                    for page in result.pages:
                        print(page.text)

            return 0

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
        "--format", choices=["plain", "json"], default="plain",
        help="Output format (default: plain)"
    )
    extract_parser.add_argument(
        "--progress", action="store_true", help="Show progress information"
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
            progress=args.progress
        )
    elif args.command == "info":
        return CLICommands.info(args.file_path)

    return 0


if __name__ == "__main__":
    sys.exit(main())
