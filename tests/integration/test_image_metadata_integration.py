"""Integration test for Image EXIF extraction workflow."""

import json
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import pytest
from PIL import Image


class TestImageEXIFIntegration:
    """End-to-end tests for image processing with EXIF metadata."""

    def test_image_processing_with_metadata_enabled(self, tmp_path):
        """Test complete image processing workflow with metadata."""
        from anyfile_to_ai.image_processor import process_image

        test_image = tmp_path / "test.jpg"
        test_image.write_bytes(b"fake jpeg data")

        with patch("PIL.Image.open") as mock_image_open:
            mock_img = MagicMock(spec=Image.Image)
            mock_img.width = 1920
            mock_img.height = 1080
            mock_img.format = "JPEG"
            mock_img.getexif.return_value = {271: "Canon", 272: "EOS 5D"}
            mock_image_open.return_value = mock_img

            with patch("anyfile_to_ai.image_processor.processor.generate_description") as mock_gen:
                mock_gen.return_value = ("A photo", 0.95, "model-v1", 1.5)

                from anyfile_to_ai.image_processor.models import ProcessingConfig

                config = ProcessingConfig(description_style="detailed")
                result = process_image(str(test_image), config=config, include_metadata=True)

                assert result.success is True
                assert result.metadata is not None
                assert "processing" in result.metadata
                assert "source" in result.metadata
                assert "Make" in result.metadata["source"]["exif"]

    def test_image_processing_without_metadata(self, tmp_path):
        """Test image processing with metadata disabled."""
        from anyfile_to_ai.image_processor import process_image

        test_image = tmp_path / "test.png"
        test_image.write_bytes(b"fake png data")

        with patch("PIL.Image.open") as mock_image_open:
            mock_img = MagicMock(spec=Image.Image)
            mock_img.width = 800
            mock_img.height = 600
            mock_img.format = "PNG"
            mock_img.getexif.return_value = {}
            mock_image_open.return_value = mock_img

            with patch("anyfile_to_ai.image_processor.processor.generate_description") as mock_gen:
                mock_gen.return_value = ("A screenshot", 0.90, "model-v1", 1.0)

                from anyfile_to_ai.image_processor.models import ProcessingConfig

                config = ProcessingConfig(description_style="brief")
                result = process_image(str(test_image), config=config, include_metadata=False)

                assert result.success is True
                assert result.metadata is None

    def test_image_exif_camera_info_extraction(self, tmp_path):
        """Test camera info is correctly extracted from EXIF."""
        from anyfile_to_ai.image_processor import process_image

        test_image = tmp_path / "photo.jpg"
        test_image.write_bytes(b"fake photo data")

        with patch("PIL.Image.open") as mock_image_open:
            mock_img = MagicMock(spec=Image.Image)
            mock_img.width = 3000
            mock_img.height = 2000
            mock_img.format = "JPEG"
            mock_img.getexif.return_value = {
                271: "Nikon",
                272: "D850",
                42036: "AF-S NIKKOR 24-70mm f/2.8E ED VR",
            }
            mock_image_open.return_value = mock_img

            with patch("anyfile_to_ai.image_processor.processor.generate_description") as mock_gen:
                mock_gen.return_value = ("Photo", 0.98, "model", 2.0)

                result = process_image(str(test_image), include_metadata=True)

                assert result.metadata is not None
                assert "camera_info" in result.metadata["source"]
                assert result.metadata["source"]["camera_info"]["make"] == "Nikon"
