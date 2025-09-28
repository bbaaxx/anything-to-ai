"""Contract tests for PDF extractor API interface."""
import pytest
from pdf_extractor import extract_text, extract_text_streaming, get_pdf_info
from pdf_extractor import ExtractionConfig, ExtractionResult, PageResult


class TestExtractTextContract:
    """Test extract_text() function contract."""

    def test_extract_text_returns_extraction_result(self):
        """Test extract_text() returns ExtractionResult object."""
        result = extract_text("sample.pdf")
        assert isinstance(result, ExtractionResult)
        assert hasattr(result, "success")
        assert hasattr(result, "pages")
        assert hasattr(result, "total_pages")
        assert hasattr(result, "total_chars")
        assert hasattr(result, "processing_time")

    def test_extract_text_with_config(self):
        """Test extract_text() accepts optional ExtractionConfig."""
        config = ExtractionConfig(streaming_enabled=False, output_format="json")
        result = extract_text("sample.pdf", config)
        assert isinstance(result, ExtractionResult)

    def test_extract_text_raises_pdf_not_found_error(self):
        """Test extract_text() raises PDFNotFoundError for missing file."""
        from pdf_extractor.exceptions import PDFNotFoundError

        with pytest.raises(PDFNotFoundError):
            extract_text("nonexistent.pdf")


class TestExtractTextStreamingContract:
    """Test extract_text_streaming() function contract."""

    def test_extract_text_streaming_returns_generator(self):
        """Test extract_text_streaming() returns generator of PageResult objects."""
        gen = extract_text_streaming("sample.pdf")
        page_result = next(gen)
        assert isinstance(page_result, PageResult)
        assert hasattr(page_result, "page_number")
        assert hasattr(page_result, "text")
        assert hasattr(page_result, "char_count")
        assert hasattr(page_result, "extraction_time")

    def test_extract_text_streaming_with_config(self):
        """Test extract_text_streaming() accepts optional ExtractionConfig."""
        config = ExtractionConfig(progress_callback=lambda x, y: None)
        gen = extract_text_streaming("sample.pdf", config)
        page_result = next(gen)
        assert isinstance(page_result, PageResult)


class TestGetPdfInfoContract:
    """Test get_pdf_info() function contract."""

    def test_get_pdf_info_returns_dict(self):
        """Test get_pdf_info() returns dictionary with required fields."""
        info = get_pdf_info("sample.pdf")
        assert isinstance(info, dict)
        assert "page_count" in info
        assert "file_size" in info
        assert "is_large_file" in info
        assert isinstance(info["page_count"], int)
        assert isinstance(info["file_size"], int)
        assert isinstance(info["is_large_file"], bool)
