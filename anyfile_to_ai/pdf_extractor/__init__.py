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
    # Enhanced exceptions
    ImageExtractionError,
    VLMConfigurationError,
    VLMServiceError,
    EnhancedExtractionError,
    ConfigurationValidationError,
)

# Progress tracking (deprecated - removed, use progress_tracker instead)

__version__ = "0.1.0"

__all__ = [
    "ConfigurationValidationError",
    "EnhancedExtractionError",
    "ExtractionConfig",
    "ExtractionResult",
    "ImageExtractionError",
    "PDFCorruptedError",
    # Data models
    "PDFDocument",
    # Exceptions
    "PDFExtractionError",
    "PDFNoTextError",
    "PDFNotFoundError",
    "PDFPasswordProtectedError",
    "PageResult",
    "ProcessingInterruptedError",
    "ProgressCallback",
    "VLMConfigurationError",
    "VLMServiceError",
    # Core functions
    "extract_text",
    "extract_text_streaming",
    "get_pdf_info",
    # Progress tracking removed - use progress_tracker.ProgressEmitter instead
]
