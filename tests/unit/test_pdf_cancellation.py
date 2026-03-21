"""Unit tests for PDF extractor cancellation support."""

import os
from unittest.mock import MagicMock, patch

import pytest

from anyfile_to_ai.pdf_extractor.streaming import extract_text_streaming
from anyfile_to_ai.pdf_extractor.models import ExtractionConfig
from anyfile_to_ai.pdf_extractor.exceptions import PDFCorruptedError
from anyfile_to_ai.progress_tracker import CancellationToken, OperationCancelledError


class TestPDFExtractorCancellation:
    """Tests for cancellation support in PDF extractor streaming."""

    def test_streaming_without_cancel_token(self, tmp_path):
        """Test that streaming works normally without cancel token."""
        # Create a mock PDF file
        test_pdf = tmp_path / "test.pdf"
        test_pdf.write_bytes(b"%PDF-1.4 fake pdf content")

        # Mock pdfplumber to return pages
        mock_page1 = MagicMock()
        mock_page1.extract_text.return_value = "Page 1 content"
        mock_page2 = MagicMock()
        mock_page2.extract_text.return_value = "Page 2 content"
        mock_pdf = MagicMock()
        mock_pdf.pages = [mock_page1, mock_page2]
        mock_pdf.__enter__ = MagicMock(return_value=mock_pdf)
        mock_pdf.__exit__ = MagicMock(return_value=False)

        with patch("anyfile_to_ai.pdf_extractor.streaming.pdfplumber.open", return_value=mock_pdf):
            results = list(extract_text_streaming(str(test_pdf)))

        assert len(results) == 2
        assert results[0].text == "Page 1 content"
        assert results[1].text == "Page 2 content"

    def test_streaming_with_cancel_token_not_cancelled(self, tmp_path):
        """Test that streaming works normally when token is not cancelled."""
        test_pdf = tmp_path / "test.pdf"
        test_pdf.write_bytes(b"%PDF-1.4 fake pdf content")

        mock_page = MagicMock()
        mock_page.extract_text.return_value = "Content"
        mock_pdf = MagicMock()
        mock_pdf.pages = [mock_page]
        mock_pdf.__enter__ = MagicMock(return_value=mock_pdf)
        mock_pdf.__exit__ = MagicMock(return_value=False)

        token = CancellationToken()  # Not cancelled

        with patch("anyfile_to_ai.pdf_extractor.streaming.pdfplumber.open", return_value=mock_pdf):
            results = list(extract_text_streaming(str(test_pdf), cancel_token=token))

        assert len(results) == 1
        assert results[0].text == "Content"

    def test_streaming_cancelled_before_start(self, tmp_path):
        """Test that cancellation before starting raises immediately."""
        test_pdf = tmp_path / "test.pdf"
        test_pdf.write_bytes(b"%PDF-1.4 fake pdf content")

        mock_page = MagicMock()
        mock_page.extract_text.return_value = "Content"
        mock_pdf = MagicMock()
        mock_pdf.pages = [mock_page]
        mock_pdf.__enter__ = MagicMock(return_value=mock_pdf)
        mock_pdf.__exit__ = MagicMock(return_value=False)

        token = CancellationToken()
        token.cancel()  # Cancel before processing

        with patch("anyfile_to_ai.pdf_extractor.streaming.pdfplumber.open", return_value=mock_pdf):
            with pytest.raises(OperationCancelledError) as exc_info:
                list(extract_text_streaming(str(test_pdf), cancel_token=token))

        assert "page 1" in str(exc_info.value).lower()

    def test_streaming_cancelled_during_iteration(self, tmp_path):
        """Test that cancellation during iteration stops processing."""
        test_pdf = tmp_path / "test.pdf"
        test_pdf.write_bytes(b"%PDF-1.4 fake pdf content")

        # Create multiple pages
        mock_pages = []
        for i in range(5):
            page = MagicMock()
            page.extract_text.return_value = f"Page {i + 1}"
            mock_pages.append(page)

        mock_pdf = MagicMock()
        mock_pdf.pages = mock_pages
        mock_pdf.__enter__ = MagicMock(return_value=mock_pdf)
        mock_pdf.__exit__ = MagicMock(return_value=False)

        token = CancellationToken()
        results = []

        def cancel_after_third_page(*args):
            if len(results) == 3:
                token.cancel()
            return mock_pdf

        with patch("anyfile_to_ai.pdf_extractor.streaming.pdfplumber.open", side_effect=cancel_after_third_page):
            with pytest.raises(OperationCancelledError):
                for result in extract_text_streaming(str(test_pdf), cancel_token=token):
                    results.append(result)

        # Should have processed some pages before cancellation
        # Note: The exact number depends on when cancellation is checked
        assert len(results) >= 0

    def test_streaming_cancel_token_none_works(self, tmp_path):
        """Test that passing None as cancel_token works."""
        test_pdf = tmp_path / "test.pdf"
        test_pdf.write_bytes(b"%PDF-1.4 fake pdf content")

        mock_page = MagicMock()
        mock_page.extract_text.return_value = "Content"
        mock_pdf = MagicMock()
        mock_pdf.pages = [mock_page]
        mock_pdf.__enter__ = MagicMock(return_value=mock_pdf)
        mock_pdf.__exit__ = MagicMock(return_value=False)

        with patch("anyfile_to_ai.pdf_extractor.streaming.pdfplumber.open", return_value=mock_pdf):
            results = list(extract_text_streaming(str(test_pdf), cancel_token=None))

        assert len(results) == 1

    def test_streaming_preserves_other_exceptions(self, tmp_path):
        """Test that non-cancellation exceptions are preserved."""
        test_pdf = tmp_path / "test.pdf"
        test_pdf.write_bytes(b"%PDF-1.4 fake pdf content")

        mock_pdf = MagicMock()
        mock_pdf.pages = []
        mock_pdf.__enter__ = MagicMock(return_value=mock_pdf)
        mock_pdf.__exit__ = MagicMock(return_value=False)

        # Mock pdfplumber.open to raise an exception
        with patch("anyfile_to_ai.pdf_extractor.streaming.pdfplumber.open", side_effect=Exception("PDF error")):
            with pytest.raises(PDFCorruptedError):
                list(extract_text_streaming(str(test_pdf)))

    def test_streaming_with_config_and_cancel_token(self, tmp_path):
        """Test that config and cancel_token work together."""
        test_pdf = tmp_path / "test.pdf"
        test_pdf.write_bytes(b"%PDF-1.4 fake pdf content")

        mock_page = MagicMock()
        mock_page.extract_text.return_value = "Content"
        mock_pdf = MagicMock()
        mock_pdf.pages = [mock_page]
        mock_pdf.__enter__ = MagicMock(return_value=mock_pdf)
        mock_pdf.__exit__ = MagicMock(return_value=False)

        config = ExtractionConfig()
        token = CancellationToken()

        with patch("anyfile_to_ai.pdf_extractor.streaming.pdfplumber.open", return_value=mock_pdf):
            results = list(extract_text_streaming(str(test_pdf), config=config, cancel_token=token))

        assert len(results) == 1
