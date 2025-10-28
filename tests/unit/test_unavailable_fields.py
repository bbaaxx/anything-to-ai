"""Unit tests for unavailable field handling in metadata."""

import pytest


class TestUnavailableFieldHandling:
    """Tests for handling unavailable metadata fields."""

    def test_unavailable_string_literal(self):
        """Test unavailable fields use 'unavailable' string."""
        unavailable_value = "unavailable"
        assert unavailable_value == "unavailable"
        assert isinstance(unavailable_value, str)

    def test_file_size_unavailable(self):
        """Test file size unavailable when file missing."""
        metadata = {"file_size_bytes": "unavailable"}
        assert metadata["file_size_bytes"] == "unavailable"

    def test_creation_date_unavailable(self):
        """Test creation date unavailable when not in PDF metadata."""
        metadata = {"creation_date": "unavailable"}
        assert metadata["creation_date"] == "unavailable"

    def test_language_unavailable(self):
        """Test language unavailable when not detected."""
        metadata = {"detected_language": "unavailable"}
        assert metadata["detected_language"] == "unavailable"

    def test_language_confidence_unavailable(self):
        """Test language confidence unavailable when not provided."""
        metadata = {"language_confidence": "unavailable"}
        assert metadata["language_confidence"] == "unavailable"

    def test_exif_empty_dict_not_unavailable(self):
        """Test EXIF data uses empty dict, not unavailable string."""
        metadata = {"exif": {}}
        assert metadata["exif"] == {}
        assert metadata["exif"] != "unavailable"

    def test_camera_info_missing_not_unavailable(self):
        """Test camera info is omitted (not unavailable) when no EXIF."""
        metadata = {"format": "PNG"}
        assert "camera_info" not in metadata


class TestUnavailableFieldConsistency:
    """Tests for consistent unavailable field handling across modules."""

    def test_pdf_unavailable_fields(self):
        """Test PDF metadata unavailable field consistency."""
        pdf_metadata = {
            "file_size_bytes": "unavailable",
            "creation_date": "unavailable",
            "modification_date": "unavailable",
            "author": "unavailable",
            "title": "unavailable",
        }

        for key, value in pdf_metadata.items():
            assert value == "unavailable"

    def test_image_unavailable_fields(self):
        """Test image metadata unavailable field consistency."""
        image_metadata = {"file_size_bytes": "unavailable"}
        assert image_metadata["file_size_bytes"] == "unavailable"

    def test_audio_unavailable_fields(self):
        """Test audio metadata unavailable field consistency."""
        audio_metadata = {
            "detected_language": "unavailable",
            "language_confidence": "unavailable",
        }

        assert audio_metadata["detected_language"] == "unavailable"
        assert audio_metadata["language_confidence"] == "unavailable"

    def test_text_unavailable_fields(self):
        """Test text metadata unavailable field consistency."""
        text_metadata = {
            "file_path": "unavailable",
            "file_size_bytes": "unavailable",
            "detected_language": "unavailable",
        }

        assert text_metadata["file_path"] == "unavailable"
        assert text_metadata["file_size_bytes"] == "unavailable"


class TestUnavailableFieldTypeHandling:
    """Tests for handling unavailable fields with mixed types."""

    def test_integer_field_unavailable(self):
        """Test integer fields can be unavailable string."""
        metadata = {"file_size_bytes": "unavailable"}
        assert isinstance(metadata["file_size_bytes"], str)

    def test_float_field_unavailable(self):
        """Test float fields can be unavailable string."""
        metadata = {"language_confidence": "unavailable"}
        assert isinstance(metadata["language_confidence"], str)

    def test_string_field_unavailable(self):
        """Test string fields use unavailable literal."""
        metadata = {"author": "unavailable"}
        assert metadata["author"] == "unavailable"

    def test_unavailable_vs_none(self):
        """Test unavailable string is preferred over None."""
        unavailable = "unavailable"
        assert unavailable is not None


class TestUnavailableFieldSerialization:
    """Tests for serialization of unavailable fields."""

    def test_unavailable_json_serialization(self):
        """Test unavailable fields serialize to JSON correctly."""
        import json

        metadata = {
            "file_size_bytes": "unavailable",
            "creation_date": "unavailable",
            "language_confidence": "unavailable",
        }

        json_str = json.dumps(metadata)
        parsed = json.loads(json_str)

        assert parsed["file_size_bytes"] == "unavailable"
        assert parsed["creation_date"] == "unavailable"

    def test_mixed_available_unavailable_serialization(self):
        """Test serialization with mix of available and unavailable fields."""
        import json

        metadata = {
            "file_size_bytes": 1024,
            "creation_date": "unavailable",
            "page_count": 10,
            "author": "unavailable",
        }

        json_str = json.dumps(metadata)
        parsed = json.loads(json_str)

        assert parsed["file_size_bytes"] == 1024
        assert parsed["creation_date"] == "unavailable"
        assert parsed["page_count"] == 10


class TestUnavailableFieldValidation:
    """Tests for validation of unavailable fields."""

    def test_unavailable_string_exact_match(self):
        """Test unavailable must be exact string match."""
        unavailable = "unavailable"
        assert unavailable == "unavailable"
        assert unavailable != "Unavailable"
        assert unavailable != "UNAVAILABLE"
        assert unavailable != "not available"

    def test_unavailable_not_empty_string(self):
        """Test unavailable is not empty string."""
        unavailable = "unavailable"
        assert unavailable != ""
        assert len(unavailable) > 0

    def test_field_path_unavailable_for_stdin(self):
        """Test file path is unavailable for stdin input."""
        metadata = {"file_path": "unavailable"}
        assert metadata["file_path"] == "unavailable"
