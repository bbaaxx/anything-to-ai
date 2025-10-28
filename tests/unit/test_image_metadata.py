"""Unit tests for Image EXIF metadata extraction."""

import os
from datetime import datetime, timezone, UTC
from unittest.mock import MagicMock, Mock, patch

import pytest
from PIL import Image

from anyfile_to_ai.image_processor.metadata import (
    _extract_camera_info,
    _extract_configuration_metadata,
    _extract_exif_data,
    _extract_image_source_metadata,
    _extract_processing_metadata,
    _get_file_size,
    extract_image_metadata,
)


class TestProcessingMetadata:
    """Tests for processing metadata extraction."""

    def test_extract_processing_metadata_basic(self):
        """Test basic processing metadata extraction."""
        result = _extract_processing_metadata(1.8, "mlx-community/gemma-3-4b")

        assert "timestamp" in result
        assert result["model_version"] == "mlx-community/gemma-3-4b"
        assert result["processing_time_seconds"] == 1.8

    def test_timestamp_is_iso8601_with_timezone(self):
        """Test timestamp is ISO 8601 format with timezone."""
        result = _extract_processing_metadata(1.0, "test-model")
        timestamp = result["timestamp"]

        dt = datetime.fromisoformat(timestamp)
        assert dt.tzinfo == UTC


class TestConfigurationMetadata:
    """Tests for configuration metadata extraction."""

    def test_extract_configuration_metadata_basic(self):
        """Test basic configuration metadata extraction."""
        user_config = {"style": "detailed"}
        effective_config = {"style": "detailed", "timeout": 60}

        result = _extract_configuration_metadata(user_config, effective_config)

        assert result["user_provided"] == user_config
        assert result["effective"] == effective_config


class TestFileSize:
    """Tests for file size extraction."""

    def test_get_file_size_success(self, tmp_path):
        """Test successful file size extraction."""
        test_file = tmp_path / "test.jpg"
        test_file.write_bytes(b"fake image data")

        size = _get_file_size(str(test_file))
        assert isinstance(size, int)
        assert size == len(b"fake image data")

    def test_get_file_size_missing_file(self):
        """Test file size extraction for missing file."""
        size = _get_file_size("/nonexistent/path/image.jpg")
        assert size == "unavailable"


class TestEXIFExtraction:
    """Tests for EXIF data extraction."""

    def test_extract_exif_data_with_tags(self):
        """Test EXIF extraction with valid tags."""
        mock_image = MagicMock(spec=Image.Image)
        mock_exif = {
            271: "Canon",
            272: "EOS 5D Mark IV",
            306: "2025:10:25 14:30:00",
        }
        mock_image.getexif.return_value = mock_exif

        result = _extract_exif_data(mock_image)

        assert "Make" in result
        assert result["Make"] == "Canon"
        assert "Model" in result
        assert result["Model"] == "EOS 5D Mark IV"

    def test_extract_exif_data_no_exif(self):
        """Test EXIF extraction when no EXIF data available."""
        mock_image = MagicMock(spec=Image.Image)
        mock_image.getexif.return_value = None

        result = _extract_exif_data(mock_image)
        assert result == {}

    def test_extract_exif_data_empty_exif(self):
        """Test EXIF extraction with empty EXIF dict."""
        mock_image = MagicMock(spec=Image.Image)
        mock_image.getexif.return_value = {}

        result = _extract_exif_data(mock_image)
        assert result == {}

    def test_extract_exif_data_bytes_value(self):
        """Test EXIF extraction with bytes values."""
        mock_image = MagicMock(spec=Image.Image)
        mock_exif = {
            271: b"Canon",
            272: "EOS 5D",
            37510: b"\xff\xfe\x00",
        }
        mock_image.getexif.return_value = mock_exif

        result = _extract_exif_data(mock_image)

        assert result["Make"] == "Canon"
        assert result["Model"] == "EOS 5D"
        assert 37510 not in result

    def test_extract_exif_data_exception_handling(self):
        """Test EXIF extraction handles exceptions gracefully."""
        mock_image = MagicMock(spec=Image.Image)
        mock_image.getexif.side_effect = AttributeError("No EXIF")

        result = _extract_exif_data(mock_image)
        assert result == {}


class TestCameraInfoExtraction:
    """Tests for camera info extraction from EXIF."""

    def test_extract_camera_info_complete(self):
        """Test camera info extraction with all fields present."""
        exif_data = {
            "Make": "Canon",
            "Model": "EOS 5D Mark IV",
            "LensModel": "EF 50mm f/1.8",
        }

        result = _extract_camera_info(exif_data)

        assert result["make"] == "Canon"
        assert result["model"] == "EOS 5D Mark IV"
        assert result["lens"] == "EF 50mm f/1.8"

    def test_extract_camera_info_partial(self):
        """Test camera info extraction with some fields missing."""
        exif_data = {
            "Make": "Canon",
            "Model": "EOS 5D",
        }

        result = _extract_camera_info(exif_data)

        assert result["make"] == "Canon"
        assert result["model"] == "EOS 5D"
        assert "lens" not in result

    def test_extract_camera_info_empty(self):
        """Test camera info extraction with no camera fields."""
        exif_data = {"DateTime": "2025:10:25 14:30:00"}

        result = _extract_camera_info(exif_data)
        assert result == {}


class TestImageSourceMetadata:
    """Tests for image source metadata extraction."""

    def test_extract_image_source_metadata_with_exif(self, tmp_path):
        """Test image source metadata with EXIF data."""
        test_file = tmp_path / "test.jpg"
        test_file.write_bytes(b"fake jpeg data")

        mock_image = MagicMock(spec=Image.Image)
        mock_image.width = 1920
        mock_image.height = 1080
        mock_image.format = "JPEG"
        mock_image.getexif.return_value = {
            271: "Canon",
            272: "EOS 5D",
        }

        result = _extract_image_source_metadata(str(test_file), mock_image)

        assert result["file_path"] == str(test_file)
        assert isinstance(result["file_size_bytes"], int)
        assert result["dimensions"]["width"] == 1920
        assert result["dimensions"]["height"] == 1080
        assert result["format"] == "JPEG"
        assert "Make" in result["exif"]
        assert result["camera_info"]["make"] == "Canon"

    def test_extract_image_source_metadata_no_exif(self):
        """Test image source metadata without EXIF data."""
        mock_image = MagicMock(spec=Image.Image)
        mock_image.width = 800
        mock_image.height = 600
        mock_image.format = "PNG"
        mock_image.getexif.return_value = {}

        result = _extract_image_source_metadata("/test.png", mock_image)

        assert result["format"] == "PNG"
        assert result["exif"] == {}
        assert "camera_info" not in result

    def test_extract_image_source_metadata_unknown_format(self):
        """Test image source metadata with unknown format."""
        mock_image = MagicMock(spec=Image.Image)
        mock_image.width = 100
        mock_image.height = 100
        mock_image.format = None
        mock_image.getexif.return_value = {}

        result = _extract_image_source_metadata("/test.img", mock_image)
        assert result["format"] == "unknown"


class TestFullMetadataExtraction:
    """Tests for complete metadata extraction."""

    def test_extract_image_metadata_complete(self, tmp_path):
        """Test complete image metadata extraction."""
        test_file = tmp_path / "test.jpg"
        test_file.write_bytes(b"fake jpeg data")

        mock_image = MagicMock(spec=Image.Image)
        mock_image.width = 1920
        mock_image.height = 1080
        mock_image.format = "JPEG"
        mock_image.getexif.return_value = {271: "Canon"}

        user_config = {"style": "detailed"}
        effective_config = {"style": "detailed", "timeout": 60}

        result = extract_image_metadata(
            str(test_file),
            mock_image,
            1.8,
            "mlx-community/gemma-3-4b",
            user_config,
            effective_config,
        )

        assert "processing" in result
        assert "configuration" in result
        assert "source" in result

        assert result["processing"]["processing_time_seconds"] == 1.8
        assert result["processing"]["model_version"] == "mlx-community/gemma-3-4b"
        assert result["configuration"]["user_provided"] == user_config
        assert result["source"]["dimensions"]["width"] == 1920

    def test_metadata_structure_consistency(self):
        """Test metadata structure is consistent."""
        mock_image = MagicMock(spec=Image.Image)
        mock_image.width = 100
        mock_image.height = 100
        mock_image.format = "JPEG"
        mock_image.getexif.return_value = {}

        result = extract_image_metadata("/test.jpg", mock_image, 1.0, "model", {}, {})

        required_sections = ["processing", "configuration", "source"]
        for section in required_sections:
            assert section in result
            assert isinstance(result[section], dict)
