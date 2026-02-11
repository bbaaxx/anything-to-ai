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
        from anyfile_to_ai.image_processor.models import DescriptionResult

        test_image = tmp_path / "test.jpg"
        test_image.write_bytes(b"fake jpeg data")

        mock_result = DescriptionResult(
            image_path=str(test_image),
            description="A photo",
            confidence_score=0.95,
            processing_time=1.5,
            model_used="model-v1",
            prompt_used="Describe this image in a detailed manner.",
            success=True,
            technical_metadata={"format": "JPEG", "dimensions": [1920, 1080], "file_size": 14},
            vlm_processing_time=1.2,
            model_version="v1",
            metadata={
                "processing": {"timestamp": "2026-01-01T00:00:00Z"},
                "source": {"exif": {"Make": "Canon", "Model": "EOS 5D"}},
            },
        )
        mock_processor = MagicMock()
        mock_processor.validate_image.return_value = MagicMock(file_path=str(test_image))
        mock_processor.process_single_image.return_value = mock_result

        with patch("anyfile_to_ai.image_processor._get_processor", return_value=mock_processor):
            from anyfile_to_ai.image_processor.models import ProcessingConfig

            config = ProcessingConfig(description_style="detailed", model_name="test-model")
            result = process_image(str(test_image), config=config, include_metadata=True)

            assert result.success is True
            assert result.metadata is not None
            assert "processing" in result.metadata
            assert "source" in result.metadata
            assert "Make" in result.metadata["source"]["exif"]

    def test_image_processing_without_metadata(self, tmp_path):
        """Test image processing with metadata disabled."""
        from anyfile_to_ai.image_processor import process_image
        from anyfile_to_ai.image_processor.models import DescriptionResult

        test_image = tmp_path / "test.png"
        test_image.write_bytes(b"fake png data")

        mock_result = DescriptionResult(
            image_path=str(test_image),
            description="A screenshot",
            confidence_score=0.90,
            processing_time=1.0,
            model_used="model-v1",
            prompt_used="Describe this image in a brief manner.",
            success=True,
            technical_metadata={"format": "PNG", "dimensions": [800, 600], "file_size": 13},
            vlm_processing_time=0.8,
            model_version="v1",
            metadata=None,
        )
        mock_processor = MagicMock()
        mock_processor.validate_image.return_value = MagicMock(file_path=str(test_image))
        mock_processor.process_single_image.return_value = mock_result

        with patch("anyfile_to_ai.image_processor._get_processor", return_value=mock_processor):
            from anyfile_to_ai.image_processor.models import ProcessingConfig

            config = ProcessingConfig(description_style="brief", model_name="test-model")
            result = process_image(str(test_image), config=config, include_metadata=False)

            assert result.success is True
            assert result.metadata is None

    def test_image_exif_camera_info_extraction(self, tmp_path):
        """Test camera info is correctly extracted from EXIF."""
        from anyfile_to_ai.image_processor import process_image
        from anyfile_to_ai.image_processor.models import DescriptionResult

        test_image = tmp_path / "photo.jpg"
        test_image.write_bytes(b"fake photo data")

        mock_result = DescriptionResult(
            image_path=str(test_image),
            description="Photo",
            confidence_score=0.98,
            processing_time=2.0,
            model_used="model",
            prompt_used="Describe this image in a detailed manner.",
            success=True,
            technical_metadata={"format": "JPEG", "dimensions": [3000, 2000], "file_size": 14},
            vlm_processing_time=1.6,
            model_version="v1",
            metadata={
                "source": {
                    "camera_info": {
                        "make": "Nikon",
                        "model": "D850",
                    }
                }
            },
        )
        mock_processor = MagicMock()
        mock_processor.validate_image.return_value = MagicMock(file_path=str(test_image))
        mock_processor.process_single_image.return_value = mock_result

        with patch("anyfile_to_ai.image_processor._get_processor", return_value=mock_processor):
            result = process_image(str(test_image), include_metadata=True)

            assert result.metadata is not None
            assert "camera_info" in result.metadata["source"]
            assert result.metadata["source"]["camera_info"]["make"] == "Nikon"
