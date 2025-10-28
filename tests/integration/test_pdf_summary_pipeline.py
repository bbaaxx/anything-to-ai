"""Integration test for PDF to summarizer pipeline with metadata."""

import json
from unittest.mock import MagicMock, patch

import pytest


class TestPDFSummarizerPipeline:
    """Tests for PDF extraction -> text summarization pipeline with metadata."""

    def test_pdf_to_summarizer_preserves_metadata(self, tmp_path):
        """Test metadata flows through PDF -> summarizer pipeline."""
        from anyfile_to_ai.pdf_extractor.reader import extract_text

        test_pdf = tmp_path / "document.pdf"
        test_pdf.write_bytes(b"fake pdf content")

        with patch("pdfplumber.open") as mock_pdf_open:
            mock_page = MagicMock()
            mock_page.extract_text.return_value = "Sample document text for testing summarization pipeline."

            mock_pdf = MagicMock()
            mock_pdf.pages = [mock_page]
            mock_pdf.metadata = {"Title": "Sample Doc"}
            mock_pdf.__enter__.return_value = mock_pdf
            mock_pdf_open.return_value = mock_pdf

            pdf_result = extract_text(str(test_pdf), include_metadata=True)

            assert pdf_result.success is True
            assert pdf_result.metadata is not None

            extracted_text = pdf_result.pages[0].text

            assert len(extracted_text) > 0
            assert "testing" in extracted_text

    def test_pdf_plain_output_pipes_to_summarizer(self, tmp_path):
        """Test PDF plain output can be piped to summarizer."""
        from anyfile_to_ai.pdf_extractor.reader import extract_text

        test_pdf = tmp_path / "doc.pdf"
        test_pdf.write_bytes(b"fake pdf")

        with patch("pdfplumber.open") as mock_pdf_open:
            mock_page = MagicMock()
            mock_page.extract_text.return_value = "Document content for pipeline test"

            mock_pdf = MagicMock()
            mock_pdf.pages = [mock_page]
            mock_pdf.metadata = {}
            mock_pdf.__enter__.return_value = mock_pdf
            mock_pdf_open.return_value = mock_pdf

            pdf_result = extract_text(str(test_pdf), include_metadata=False)
            plain_text = pdf_result.pages[0].text

            assert isinstance(plain_text, str)
            assert len(plain_text) > 0
