"""Data models for PDF extraction."""

from dataclasses import dataclass
from collections.abc import Callable


@dataclass
class PDFDocument:
    """Represents a PDF file being processed."""

    file_path: str
    page_count: int
    file_size: int
    is_large_file: bool

    def __post_init__(self):
        """Validate PDFDocument fields."""
        if self.page_count <= 0:
            raise ValueError("page_count must be positive integer")
        if self.file_size < 0:
            raise ValueError("file_size must be non-negative")
        if not self.file_path.endswith(".pdf"):
            raise ValueError("file_path must have .pdf extension")


@dataclass
class PageResult:
    """Extracted text data from a single PDF page."""

    page_number: int
    text: str
    char_count: int
    extraction_time: float

    def __post_init__(self):
        """Validate PageResult fields."""
        if self.page_number <= 0:
            raise ValueError("page_number must be positive integer")
        if self.char_count < 0:
            raise ValueError("char_count must be non-negative")
        if self.extraction_time < 0:
            raise ValueError("extraction_time must be non-negative")
        if len(self.text) != self.char_count:
            raise ValueError("char_count must match actual text length")


@dataclass
class ExtractionResult:
    """Complete result of text extraction operation."""

    success: bool
    pages: list[PageResult]
    total_pages: int
    total_chars: int
    processing_time: float
    error_message: str | None = None

    def __post_init__(self):
        """Validate ExtractionResult fields."""
        if self.success and self.error_message is not None:
            raise ValueError("If success=True, error_message must be None")
        if not self.success and self.error_message is None:
            raise ValueError("If success=False, error_message must be provided")
        if len(self.pages) != self.total_pages:
            raise ValueError("total_pages must match length of pages list")
        if self.processing_time <= 0:
            raise ValueError("processing_time must be positive")


# Progress callback signature
ProgressCallback = Callable[[int, int], None]  # (current_page, total_pages)


@dataclass
class ExtractionConfig:
    """Configuration for PDF text extraction."""

    streaming_enabled: bool = True
    progress_callback: ProgressCallback | None = None
    output_format: str = "plain"  # "plain" or "json"

    def __post_init__(self):
        """Validate ExtractionConfig fields."""
        if self.output_format not in ["plain", "json"]:
            raise ValueError("output_format must be 'plain' or 'json'")
