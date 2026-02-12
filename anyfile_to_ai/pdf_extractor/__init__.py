"""PDF Text Extraction Module."""

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


def _missing_pdf_dependency_message() -> str:
    return "pdfplumber is required for PDF extraction APIs. Install optional dependency with: pip install 'anyfile_to_ai[pdf]'"


def extract_text(*args, **kwargs):
    """Lazily import and execute extract_text to avoid hard import-time failures."""
    try:
        from .reader import extract_text as _extract_text
    except ImportError as exc:
        raise ImportError(_missing_pdf_dependency_message()) from exc
    return _extract_text(*args, **kwargs)


def get_pdf_info(*args, **kwargs):
    """Lazily import and execute get_pdf_info to avoid hard import-time failures."""
    try:
        from .reader import get_pdf_info as _get_pdf_info
    except ImportError as exc:
        raise ImportError(_missing_pdf_dependency_message()) from exc
    return _get_pdf_info(*args, **kwargs)


def extract_text_streaming(*args, **kwargs):
    """Lazily import and execute extract_text_streaming to avoid hard import-time failures."""
    try:
        from .streaming import extract_text_streaming as _extract_text_streaming
    except ImportError as exc:
        raise ImportError(_missing_pdf_dependency_message()) from exc
    return _extract_text_streaming(*args, **kwargs)


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
