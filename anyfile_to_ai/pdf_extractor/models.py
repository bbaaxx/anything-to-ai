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
            msg = "page_count must be positive integer"
            raise ValueError(msg)
        if self.file_size < 0:
            msg = "file_size must be non-negative"
            raise ValueError(msg)
        if not self.file_path.endswith(".pdf"):
            msg = "file_path must have .pdf extension"
            raise ValueError(msg)


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
            msg = "page_number must be positive integer"
            raise ValueError(msg)
        if self.char_count < 0:
            msg = "char_count must be non-negative"
            raise ValueError(msg)
        if self.extraction_time < 0:
            msg = "extraction_time must be non-negative"
            raise ValueError(msg)
        if len(self.text) != self.char_count:
            msg = "char_count must match actual text length"
            raise ValueError(msg)


@dataclass
class ExtractionResult:
    """Complete result of text extraction operation."""

    success: bool
    pages: list[PageResult]
    total_pages: int
    total_chars: int
    processing_time: float
    error_message: str | None = None
    metadata: dict | None = None

    def __post_init__(self):
        """Validate ExtractionResult fields."""
        if self.success and self.error_message is not None:
            msg = "If success=True, error_message must be None"
            raise ValueError(msg)
        if not self.success and self.error_message is None:
            msg = "If success=False, error_message must be provided"
            raise ValueError(msg)
        if len(self.pages) != self.total_pages:
            msg = "total_pages must match length of pages list"
            raise ValueError(msg)
        if self.processing_time <= 0:
            msg = "processing_time must be positive"
            raise ValueError(msg)


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
            msg = "output_format must be 'plain' or 'json'"
            raise ValueError(msg)
