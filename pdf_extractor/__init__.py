"""PDF Text Extraction Module."""

# Core functions
from .reader import extract_text, get_pdf_info
from .streaming import extract_text_streaming

# Data models
from .models import (
    PDFDocument,
    PageResult,
    ExtractionResult,
    ExtractionConfig,
    ProgressCallback,
)

# Exceptions
from .exceptions import (
    PDFExtractionError,
    PDFNotFoundError,
    PDFCorruptedError,
    PDFPasswordProtectedError,
    PDFNoTextError,
    ProcessingInterruptedError,
)

# Progress tracking
from .progress import ProgressInfo

__version__ = "0.1.0"

__all__ = [
    # Core functions
    "extract_text",
    "extract_text_streaming",
    "get_pdf_info",
    # Data models
    "PDFDocument",
    "PageResult",
    "ExtractionResult",
    "ExtractionConfig",
    "ProgressCallback",
    # Exceptions
    "PDFExtractionError",
    "PDFNotFoundError",
    "PDFCorruptedError",
    "PDFPasswordProtectedError",
    "PDFNoTextError",
    "ProcessingInterruptedError",
    # Progress tracking
    "ProgressInfo",
]
