"""Core PDF text extraction functionality."""

import time
import os
from typing import Optional, Dict, Any
import pdfplumber
from .models import PageResult, ExtractionResult, ExtractionConfig
from .exceptions import PDFNotFoundError, PDFCorruptedError

try:
    from anyfile_to_ai.progress_tracker import ProgressEmitter

    _PROGRESS_AVAILABLE = True
except ImportError:
    _PROGRESS_AVAILABLE = False
    ProgressEmitter = None


def extract_text(file_path: str, config: Optional[ExtractionConfig] = None, progress_emitter: Optional["ProgressEmitter"] = None) -> ExtractionResult:
    """Extract text from PDF file.

    Args:
        file_path: Path to PDF file
        config: Extraction configuration (legacy)
        progress_emitter: Optional progress tracker (recommended)
    """
    config = config or ExtractionConfig()
    start_time = time.time()

    # Validate file exists
    if not os.path.exists(file_path):
        raise PDFNotFoundError(file_path)

    try:
        with pdfplumber.open(file_path) as pdf:
            pages = []
            total_chars = 0

            if progress_emitter:
                progress_emitter.update_total(len(pdf.pages))

            for page_num, page in enumerate(pdf.pages, 1):
                page_start = time.time()
                text = page.extract_text() or ""
                page_time = time.time() - page_start

                page_result = PageResult(page_number=page_num, text=text, char_count=len(text), extraction_time=page_time)
                pages.append(page_result)
                total_chars += len(text)

                # New progress system (preferred)
                if progress_emitter:
                    progress_emitter.update(1)
                # Legacy callback support
                elif config.progress_callback:
                    config.progress_callback(page_num, len(pdf.pages))

            if progress_emitter:
                progress_emitter.complete()

            processing_time = time.time() - start_time

            return ExtractionResult(success=True, pages=pages, total_pages=len(pages), total_chars=total_chars, processing_time=processing_time)

    except Exception as e:
        raise PDFCorruptedError(file_path, str(e))


def get_pdf_info(file_path: str) -> Dict[str, Any]:
    """Get basic PDF information without extracting text."""
    if not os.path.exists(file_path):
        raise PDFNotFoundError(file_path)

    try:
        with pdfplumber.open(file_path) as pdf:
            page_count = len(pdf.pages)
            file_size = os.path.getsize(file_path)
            is_large_file = page_count > 20

            return {"page_count": page_count, "file_size": file_size, "is_large_file": is_large_file}

    except Exception as e:
        raise PDFCorruptedError(file_path, str(e))
