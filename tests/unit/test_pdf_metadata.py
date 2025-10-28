"""Unit tests for PDF metadata extraction."""

import os
from datetime import datetime, timezone, UTC
from unittest.mock import MagicMock, patch

import pytest

from anyfile_to_ai.pdf_extractor.metadata import (
    _extract_configuration_metadata,
    _extract_pdf_creation_date,
    _extract_pdf_info_field,
    _extract_pdf_modification_date,
    _extract_pdf_source_metadata,
    _extract_processing_metadata,
    _get_file_size,
    _parse_pdf_date,
    extract_pdf_metadata,
)


class TestProcessingMetadata:
    """Tests for processing metadata extraction."""

    def test_extract_processing_metadata_basic(self):
        """Test basic processing metadata extraction."""
        result = _extract_processing_metadata(2.5)

        assert "timestamp" in result
        assert result["model_version"] == "pdfplumber-0.11.7"
        assert result["processing_time_seconds"] == 2.5

    def test_timestamp_is_iso8601_with_timezone(self):
        """Test timestamp is ISO 8601 format with timezone."""
        result = _extract_processing_metadata(1.0)
        timestamp = result["timestamp"]

        dt = datetime.fromisoformat(timestamp)
        assert dt.tzinfo == UTC

    def test_processing_time_zero(self):
        """Test processing time can be zero."""
        result = _extract_processing_metadata(0.0)
        assert result["processing_time_seconds"] == 0.0


class TestConfigurationMetadata:
    """Tests for configuration metadata extraction."""

    def test_extract_configuration_metadata_basic(self):
        """Test basic configuration metadata extraction."""
        user_config = {"format": "json"}
        effective_config = {"format": "json", "progress": True}

        result = _extract_configuration_metadata(user_config, effective_config)

        assert result["user_provided"] == user_config
        assert result["effective"] == effective_config

    def test_empty_user_config(self):
        """Test extraction with empty user config."""
        user_config = {}
        effective_config = {"format": "plain", "progress": False}

        result = _extract_configuration_metadata(user_config, effective_config)

        assert result["user_provided"] == {}
        assert result["effective"] == effective_config


class TestFileSize:
    """Tests for file size extraction."""

    def test_get_file_size_success(self, tmp_path):
        """Test successful file size extraction."""
        test_file = tmp_path / "test.pdf"
        test_file.write_text("test content")

        size = _get_file_size(str(test_file))
        assert isinstance(size, int)
        assert size == len("test content")

    def test_get_file_size_missing_file(self):
        """Test file size extraction for missing file."""
        size = _get_file_size("/nonexistent/path/file.pdf")
        assert size == "unavailable"

    def test_get_file_size_permission_error(self):
        """Test file size extraction with permission error."""
        with patch("os.stat", side_effect=OSError("Permission denied")):
            size = _get_file_size("/some/path.pdf")
            assert size == "unavailable"


class TestPDFDateParsing:
    """Tests for PDF date parsing."""

    def test_parse_pdf_date_full_format(self):
        """Test parsing full PDF date format."""
        pdf_date = "D:20250115093000+00'00'"
        result = _parse_pdf_date(pdf_date)

        assert result.startswith("2025-01-15")
        dt = datetime.fromisoformat(result)
        assert dt.year == 2025
        assert dt.month == 1
        assert dt.day == 15

    def test_parse_pdf_date_minimal_format(self):
        """Test parsing minimal PDF date (date only)."""
        pdf_date = "D:20250115"
        result = _parse_pdf_date(pdf_date)

        assert result.startswith("2025-01-15")

    def test_parse_pdf_date_invalid_format(self):
        """Test parsing invalid PDF date format."""
        result = _parse_pdf_date("invalid_date")
        assert result == "unavailable"

    def test_parse_pdf_date_empty_string(self):
        """Test parsing empty date string."""
        result = _parse_pdf_date("")
        assert result == "unavailable"


class TestPDFInfoFields:
    """Tests for PDF info field extraction."""

    def test_extract_creation_date_success(self):
        """Test successful creation date extraction."""
        pdf_obj = MagicMock()
        pdf_obj.metadata = {"CreationDate": "D:20250115093000+00'00'"}

        result = _extract_pdf_creation_date(pdf_obj)
        assert result.startswith("2025-01-15")

    def test_extract_creation_date_missing(self):
        """Test creation date extraction when field is missing."""
        pdf_obj = MagicMock()
        pdf_obj.metadata = {}

        result = _extract_pdf_creation_date(pdf_obj)
        assert result == "unavailable"

    def test_extract_creation_date_no_metadata(self):
        """Test creation date extraction when metadata is None."""
        pdf_obj = MagicMock()
        pdf_obj.metadata = None

        result = _extract_pdf_creation_date(pdf_obj)
        assert result == "unavailable"

    def test_extract_modification_date_success(self):
        """Test successful modification date extraction."""
        pdf_obj = MagicMock()
        pdf_obj.metadata = {"ModDate": "D:20250220144500+00'00'"}

        result = _extract_pdf_modification_date(pdf_obj)
        assert result.startswith("2025-02-20")

    def test_extract_info_field_author_success(self):
        """Test successful author extraction."""
        pdf_obj = MagicMock()
        pdf_obj.metadata = {"Author": "John Doe"}

        result = _extract_pdf_info_field(pdf_obj, "Author")
        assert result == "John Doe"

    def test_extract_info_field_missing(self):
        """Test info field extraction when field is missing."""
        pdf_obj = MagicMock()
        pdf_obj.metadata = {}

        result = _extract_pdf_info_field(pdf_obj, "Author")
        assert result == "unavailable"

    def test_extract_info_field_empty_value(self):
        """Test info field extraction with empty value."""
        pdf_obj = MagicMock()
        pdf_obj.metadata = {"Author": ""}

        result = _extract_pdf_info_field(pdf_obj, "Author")
        assert result == "unavailable"


class TestPDFSourceMetadata:
    """Tests for PDF source metadata extraction."""

    def test_extract_pdf_source_metadata_complete(self, tmp_path):
        """Test complete PDF source metadata extraction."""
        test_file = tmp_path / "test.pdf"
        test_file.write_text("test pdf content")

        pdf_obj = MagicMock()
        pdf_obj.pages = [MagicMock(), MagicMock(), MagicMock()]
        pdf_obj.metadata = {
            "CreationDate": "D:20250115093000+00'00'",
            "ModDate": "D:20250220144500+00'00'",
            "Author": "Test Author",
            "Title": "Test Document",
        }

        result = _extract_pdf_source_metadata(str(test_file), pdf_obj)

        assert result["file_path"] == str(test_file)
        assert isinstance(result["file_size_bytes"], int)
        assert result["page_count"] == 3
        assert result["creation_date"].startswith("2025-01-15")
        assert result["modification_date"].startswith("2025-02-20")
        assert result["author"] == "Test Author"
        assert result["title"] == "Test Document"

    def test_extract_pdf_source_metadata_minimal(self):
        """Test PDF source metadata with minimal available fields."""
        pdf_obj = MagicMock()
        pdf_obj.pages = [MagicMock()]
        pdf_obj.metadata = None

        result = _extract_pdf_source_metadata("/nonexistent/file.pdf", pdf_obj)

        assert result["file_path"] == "/nonexistent/file.pdf"
        assert result["file_size_bytes"] == "unavailable"
        assert result["page_count"] == 1
        assert result["creation_date"] == "unavailable"
        assert result["modification_date"] == "unavailable"
        assert result["author"] == "unavailable"
        assert result["title"] == "unavailable"


class TestFullMetadataExtraction:
    """Tests for complete metadata extraction."""

    def test_extract_pdf_metadata_complete(self, tmp_path):
        """Test complete PDF metadata extraction."""
        test_file = tmp_path / "test.pdf"
        test_file.write_text("test pdf content")

        pdf_obj = MagicMock()
        pdf_obj.pages = [MagicMock(), MagicMock()]
        pdf_obj.metadata = {
            "CreationDate": "D:20250115093000+00'00'",
            "Title": "Test PDF",
        }

        user_config = {"format": "json"}
        effective_config = {"format": "json", "progress": True}

        result = extract_pdf_metadata(str(test_file), pdf_obj, 2.5, user_config, effective_config)

        assert "processing" in result
        assert "configuration" in result
        assert "source" in result

        assert result["processing"]["processing_time_seconds"] == 2.5
        assert result["configuration"]["user_provided"] == user_config
        assert result["source"]["page_count"] == 2

    def test_metadata_structure_consistency(self):
        """Test metadata structure is consistent."""
        pdf_obj = MagicMock()
        pdf_obj.pages = [MagicMock()]
        pdf_obj.metadata = None

        result = extract_pdf_metadata("/test.pdf", pdf_obj, 1.0, {}, {})

        required_sections = ["processing", "configuration", "source"]
        for section in required_sections:
            assert section in result
            assert isinstance(result[section], dict)
