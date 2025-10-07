"""Streaming/pagination for large files."""

import time
import os
from collections.abc import Generator
import pdfplumber
from .models import PageResult, ExtractionConfig
from .exceptions import PDFNotFoundError, PDFCorruptedError


def extract_text_streaming(file_path: str, config: ExtractionConfig | None = None) -> Generator[PageResult, None, None]:
    """
    Stream text extraction page by page (generator).

    Args:
        file_path: Path to PDF file
        config: Extraction configuration

    Yields:
        PageResult for each processed page

    Raises:
        Same exceptions as extract_text()
    """
    config = config or ExtractionConfig()

    # Validate file exists
    if not os.path.exists(file_path):
        raise PDFNotFoundError(file_path)

    try:
        with pdfplumber.open(file_path) as pdf:
            total_pages = len(pdf.pages)

            for page_num, page in enumerate(pdf.pages, 1):
                page_start = time.time()
                text = page.extract_text() or ""
                page_time = time.time() - page_start

                page_result = PageResult(page_number=page_num, text=text, char_count=len(text), extraction_time=page_time)

                # Call progress callback if provided
                if config.progress_callback:
                    config.progress_callback(page_num, total_pages)

                yield page_result

    except Exception as e:
        raise PDFCorruptedError(file_path, str(e))
