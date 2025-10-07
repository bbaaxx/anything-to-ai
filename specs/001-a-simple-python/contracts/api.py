# API Contract: PDF Text Extraction Module
# This file defines the programmatic interface contracts

from typing import Any
from collections.abc import Callable
from dataclasses import dataclass

# Progress callback signature
ProgressCallback = Callable[[int, int], None]  # (current_page, total_pages)


@dataclass
class ExtractionConfig:
    """Configuration for PDF text extraction"""

    streaming_enabled: bool = True
    progress_callback: ProgressCallback | None = None
    output_format: str = "plain"  # "plain" or "json"

    def __post_init__(self):
        if self.output_format not in ["plain", "json"]:
            raise ValueError("output_format must be 'plain' or 'json'")


@dataclass
class PageResult:
    """Result from extracting a single page"""

    page_number: int
    text: str
    char_count: int
    extraction_time: float


@dataclass
class ExtractionResult:
    """Complete extraction result"""

    success: bool
    pages: list[PageResult]
    total_pages: int
    total_chars: int
    processing_time: float
    error_message: str | None = None


# Core API Functions


def extract_text(file_path: str, config: ExtractionConfig | None = None) -> ExtractionResult:
    """
    Extract text from PDF file

    Args:
        file_path: Path to PDF file
        config: Extraction configuration

    Returns:
        ExtractionResult with success status and extracted content

    Raises:
        PDFNotFoundError: File does not exist
        PDFCorruptedError: PDF is corrupted or invalid
        PDFPasswordProtectedError: PDF requires password
        PDFNoTextError: PDF contains no extractable text
    """


def extract_text_streaming(file_path: str, config: ExtractionConfig | None = None):
    """
    Stream text extraction page by page (generator)

    Args:
        file_path: Path to PDF file
        config: Extraction configuration

    Yields:
        PageResult for each processed page

    Raises:
        Same exceptions as extract_text()
    """


def get_pdf_info(file_path: str) -> dict[str, Any]:
    """
    Get basic PDF information without extracting text

    Args:
        file_path: Path to PDF file

    Returns:
        Dictionary with page_count, file_size, is_large_file

    Raises:
        PDFNotFoundError: File does not exist
        PDFCorruptedError: PDF is corrupted or invalid
    """


# CLI Contract (command line interface)


class CLICommands:
    """Command line interface contract"""

    @staticmethod
    def extract(file_path: str, stream: bool = False, format_type: str = "plain", progress: bool = False) -> int:
        """
        CLI extract command

        Args:
            file_path: Path to PDF file
            stream: Enable streaming mode
            format_type: Output format (plain/json)
            progress: Show progress information

        Returns:
            Exit code (0 for success, non-zero for error)
        """

    @staticmethod
    def info(file_path: str) -> int:
        """
        CLI info command - show PDF information

        Args:
            file_path: Path to PDF file

        Returns:
            Exit code (0 for success, non-zero for error)
        """
