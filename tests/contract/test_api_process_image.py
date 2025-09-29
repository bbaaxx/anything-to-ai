"""Contract tests for process_image() API function."""

import pytest
from image_processor import process_image, ProcessingConfig, DescriptionResult
from image_processor.exceptions import ImageNotFoundError, UnsupportedFormatError, ProcessingError


class TestProcessImageContract:
    """Contract tests for single image processing."""

    def test_process_image_basic_call(self):
        """Test basic process_image call returns DescriptionResult."""
        result = process_image("sample.jpg")
        assert isinstance(result, DescriptionResult)
        assert result.image_path == "sample.jpg"
        assert isinstance(result.description, str)
        assert len(result.description) > 0
        assert result.success is True

    def test_process_image_with_config(self):
        """Test process_image with custom configuration."""
        config = ProcessingConfig(
            description_style="brief",
            max_description_length=200
        )
        result = process_image("sample.jpg", config)
        assert isinstance(result, DescriptionResult)
        assert result.success is True
        assert len(result.description) <= 200

    def test_process_image_missing_file(self):
        """Test process_image raises ImageNotFoundError for missing files."""
        with pytest.raises(ImageNotFoundError) as exc_info:
            process_image("nonexistent.jpg")
        assert "nonexistent.jpg" in str(exc_info.value)

    def test_process_image_unsupported_format(self):
        """Test process_image raises UnsupportedFormatError for unsupported formats."""
        with pytest.raises(UnsupportedFormatError) as exc_info:
            process_image("document.txt")
        assert "document.txt" in str(exc_info.value)

    def test_process_image_result_metadata(self):
        """Test process_image returns complete metadata."""
        result = process_image("sample.jpg")
        assert hasattr(result, 'confidence_score')
        assert hasattr(result, 'processing_time')
        assert hasattr(result, 'model_used')
        assert hasattr(result, 'prompt_used')
        assert result.processing_time > 0
        assert isinstance(result.model_used, str)
        assert len(result.model_used) > 0