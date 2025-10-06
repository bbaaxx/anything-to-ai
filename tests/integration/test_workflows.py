"""Integration tests for PDF processing workflows."""
import pytest
from anyfile_to_ai.pdf_extractor import extract_text, extract_text_streaming, get_pdf_info
from anyfile_to_ai.pdf_extractor import ExtractionConfig
from anyfile_to_ai.pdf_extractor.exceptions import (
    PDFNotFoundError,
    PDFCorruptedError,
    PDFPasswordProtectedError,
    PDFNoTextError,
)


class TestSmallPDFWorkflow:
    """Test small PDF processing workflow (≤ 20 pages)."""

    def test_small_pdf_basic_extraction(self):
        """Test basic text extraction from small PDF."""
        result = extract_text("small_sample.pdf")
        assert result.success is True
        assert len(result.pages) > 0
        assert result.total_chars > 0
        assert result.processing_time > 0

    def test_small_pdf_info_extraction(self):
        """Test PDF info extraction for small file."""
        info = get_pdf_info("small_sample.pdf")
        assert info["page_count"] <= 20
        assert info["is_large_file"] is False


class TestLargePDFWorkflow:
    """Test large PDF processing workflow (> 20 pages)."""

    def test_large_pdf_streaming_extraction(self):
        """Test streaming text extraction from large PDF."""
        config = ExtractionConfig(streaming_enabled=True)
        pages_processed = 0

        for page_result in extract_text_streaming("large_sample.pdf", config):
            assert page_result.page_number > 0
            assert isinstance(page_result.text, str)
            assert page_result.char_count >= 0
            pages_processed += 1
            if pages_processed >= 5:  # Test first 5 pages
                break

        assert pages_processed == 5

    def test_large_pdf_with_progress_callback(self):
        """Test large PDF processing with progress tracking."""
        progress_calls = []

        def progress_callback(current, total):
            progress_calls.append((current, total))

        config = ExtractionConfig(
            streaming_enabled=True, progress_callback=progress_callback
        )

        # Process first few pages
        pages_processed = 0
        for page_result in extract_text_streaming("large_sample.pdf", config):
            pages_processed += 1
            if pages_processed >= 3:
                break

        assert len(progress_calls) > 0
        assert all(isinstance(call[0], int) for call in progress_calls)
        assert all(isinstance(call[1], int) for call in progress_calls)


class TestErrorHandlingWorkflows:
    """Test error handling scenarios."""

    def test_nonexistent_file_error(self):
        """Test error handling for nonexistent file."""
        with pytest.raises(PDFNotFoundError):
            extract_text("nonexistent_file.pdf")

    def test_corrupted_pdf_error(self):
        """Test error handling for corrupted PDF."""
        with pytest.raises(PDFCorruptedError):
            extract_text("corrupted_file.pdf")

    def test_password_protected_pdf_error(self):
        """Test error handling for password-protected PDF."""
        with pytest.raises(PDFPasswordProtectedError):
            extract_text("protected_file.pdf")

    def test_no_text_pdf_error(self):
        """Test error handling for PDF with no extractable text."""
        with pytest.raises(PDFNoTextError):
            extract_text("image_only.pdf")
