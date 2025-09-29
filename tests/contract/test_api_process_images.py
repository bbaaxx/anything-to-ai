"""Contract tests for process_images() API function."""

import pytest
from image_processor import process_images, ProcessingConfig, ProcessingResult
from image_processor.exceptions import ValidationError


class TestProcessImagesContract:
    """Contract tests for batch image processing."""

    def test_process_images_basic_call(self):
        """Test basic process_images call returns ProcessingResult."""
        image_paths = ["image1.jpg", "image2.png"]
        result = process_images(image_paths)
        assert isinstance(result, ProcessingResult)
        assert result.total_images == 2
        assert len(result.results) == 2
        assert result.successful_count + result.failed_count == result.total_images

    def test_process_images_with_config(self):
        """Test process_images with custom configuration."""
        config = ProcessingConfig(batch_size=2, description_style="brief")
        image_paths = ["image1.jpg", "image2.png", "image3.gif"]
        result = process_images(image_paths, config)
        assert isinstance(result, ProcessingResult)
        assert result.total_images == 3

    def test_process_images_empty_list(self):
        """Test process_images with empty list raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            process_images([])
        assert "empty" in str(exc_info.value).lower()

    def test_process_images_mixed_results(self):
        """Test process_images handles mixed success/failure results."""
        image_paths = ["valid.jpg", "nonexistent.jpg", "valid2.png"]
        result = process_images(image_paths)
        assert isinstance(result, ProcessingResult)
        assert result.total_images == 3
        assert result.successful_count >= 0
        assert result.failed_count >= 0
        assert result.successful_count + result.failed_count == 3

    def test_process_images_timing_metadata(self):
        """Test process_images returns timing metadata."""
        image_paths = ["image1.jpg", "image2.png"]
        result = process_images(image_paths)
        assert hasattr(result, 'total_processing_time')
        assert result.total_processing_time > 0
        for individual_result in result.results:
            assert individual_result.processing_time > 0
