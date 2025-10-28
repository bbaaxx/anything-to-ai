"""Integration test for PDF extraction with full metadata."""

import json
from datetime import datetime, timezone, UTC
from unittest.mock import MagicMock, patch

import pytest


class TestPDFMetadataIntegration:
    """End-to-end tests for PDF extraction with metadata."""

    def test_pdf_extraction_with_metadata_enabled(self, tmp_path):
        """Test complete PDF extraction workflow with metadata enabled."""
        from anyfile_to_ai.pdf_extractor.reader import extract_text

        test_pdf = tmp_path / "test.pdf"
        test_pdf.write_bytes(b"fake pdf content")

        with patch("pdfplumber.open") as mock_pdf_open:
            mock_page = MagicMock()
            mock_page.extract_text.return_value = "Sample PDF text content"

            mock_pdf = MagicMock()
            mock_pdf.pages = [mock_page, mock_page]
            mock_pdf.metadata = {
                "CreationDate": "D:20250115093000+00'00'",
                "Title": "Test Document",
                "Author": "Test Author",
            }
            mock_pdf.__enter__.return_value = mock_pdf
            mock_pdf_open.return_value = mock_pdf

            result = extract_text(str(test_pdf), include_metadata=True)

            assert result.success is True
            assert result.metadata is not None
            assert "processing" in result.metadata
            assert "configuration" in result.metadata
            assert "source" in result.metadata

            assert result.metadata["processing"]["model_version"] == "pdfplumber-0.11.7"
            assert result.metadata["source"]["page_count"] == 2
            assert result.metadata["source"]["title"] == "Test Document"

    def test_pdf_extraction_without_metadata(self, tmp_path):
        """Test PDF extraction with metadata disabled (default)."""
        from anyfile_to_ai.pdf_extractor.reader import extract_text

        test_pdf = tmp_path / "test.pdf"
        test_pdf.write_bytes(b"fake pdf content")

        with patch("pdfplumber.open") as mock_pdf_open:
            mock_page = MagicMock()
            mock_page.extract_text.return_value = "Sample PDF text"

            mock_pdf = MagicMock()
            mock_pdf.pages = [mock_page]
            mock_pdf.metadata = {}
            mock_pdf.__enter__.return_value = mock_pdf
            mock_pdf_open.return_value = mock_pdf

            result = extract_text(str(test_pdf), include_metadata=False)

            assert result.success is True
            assert result.metadata is None

    def test_pdf_metadata_json_serialization(self, tmp_path):
        """Test PDF metadata serializes correctly to JSON."""
        from anyfile_to_ai.pdf_extractor.reader import extract_text

        test_pdf = tmp_path / "test.pdf"
        test_pdf.write_bytes(b"fake pdf content")

        with patch("pdfplumber.open") as mock_pdf_open:
            mock_page = MagicMock()
            mock_page.extract_text.return_value = "Text"

            mock_pdf = MagicMock()
            mock_pdf.pages = [mock_page]
            mock_pdf.metadata = {"Title": "Test"}
            mock_pdf.__enter__.return_value = mock_pdf
            mock_pdf_open.return_value = mock_pdf

            result = extract_text(str(test_pdf), include_metadata=True)

            assert result.metadata is not None
            metadata_json = json.dumps(result.metadata)
            parsed = json.loads(metadata_json)

            assert "processing" in parsed
            assert "source" in parsed

    def test_pdf_metadata_unavailable_fields(self, tmp_path):
        """Test PDF metadata handles unavailable fields correctly."""
        from anyfile_to_ai.pdf_extractor.reader import extract_text

        test_pdf = tmp_path / "test.pdf"
        test_pdf.write_bytes(b"fake pdf")

        with patch("pdfplumber.open") as mock_pdf_open:
            mock_page = MagicMock()
            mock_page.extract_text.return_value = "Text"

            mock_pdf = MagicMock()
            mock_pdf.pages = [mock_page]
            mock_pdf.metadata = None
            mock_pdf.__enter__.return_value = mock_pdf
            mock_pdf_open.return_value = mock_pdf

            result = extract_text(str(test_pdf), include_metadata=True)

            assert result.metadata is not None
            assert result.metadata["source"]["creation_date"] == "unavailable"
            assert result.metadata["source"]["author"] == "unavailable"
            assert result.metadata["source"]["title"] == "unavailable"

    def test_pdf_metadata_timestamp_format(self, tmp_path):
        """Test PDF metadata timestamp is ISO 8601 format."""
        from anyfile_to_ai.pdf_extractor.reader import extract_text

        test_pdf = tmp_path / "test.pdf"
        test_pdf.write_bytes(b"fake pdf")

        with patch("pdfplumber.open") as mock_pdf_open:
            mock_page = MagicMock()
            mock_page.extract_text.return_value = "Text"

            mock_pdf = MagicMock()
            mock_pdf.pages = [mock_page]
            mock_pdf.metadata = {}
            mock_pdf.__enter__.return_value = mock_pdf
            mock_pdf_open.return_value = mock_pdf

            result = extract_text(str(test_pdf), include_metadata=True)

            assert result.metadata is not None
            timestamp = result.metadata["processing"]["timestamp"]
            dt = datetime.fromisoformat(timestamp)
            assert dt.tzinfo == UTC
