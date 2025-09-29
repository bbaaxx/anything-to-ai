"""Contract tests for process_images_streaming() API function."""

import pytest
from image_processor import process_images_streaming, ProcessingConfig, DescriptionResult
from image_processor.exceptions import ValidationError


class TestStreamingProcessingContract:
    """Contract tests for streaming image processing."""

    def test_process_images_streaming_basic_call(self):
        """Test basic process_images_streaming call returns generator."""
        image_paths = ["image1.jpg", "image2.png"]
        result = process_images_streaming(image_paths)
        assert hasattr(result, '__iter__')
        assert hasattr(result, '__next__')

    def test_process_images_streaming_yields_results(self):
        """Test process_images_streaming yields DescriptionResult objects."""
        image_paths = ["image1.jpg", "image2.png"]
        results = list(process_images_streaming(image_paths))
        assert len(results) == 2
        for result in results:
            assert isinstance(result, DescriptionResult)

    def test_process_images_streaming_with_progress_callback(self):
        """Test process_images_streaming calls progress callback."""
        progress_calls = []

        def progress_callback(current, total):
            progress_calls.append((current, total))

        config = ProcessingConfig(progress_callback=progress_callback)
        image_paths = ["image1.jpg", "image2.png"]
        list(process_images_streaming(image_paths, config))

        assert len(progress_calls) > 0
        assert progress_calls[-1] == (2, 2)  # Final call should be (total, total)

    def test_process_images_streaming_empty_list(self):
        """Test process_images_streaming with empty list raises ValidationError."""
        with pytest.raises(ValidationError):
            list(process_images_streaming([]))

    def test_process_images_streaming_order_preservation(self):
        """Test process_images_streaming preserves input order."""
        image_paths = ["first.jpg", "second.png", "third.gif"]
        results = list(process_images_streaming(image_paths))
        assert len(results) == 3
        assert results[0].image_path == "first.jpg"
        assert results[1].image_path == "second.png"
        assert results[2].image_path == "third.gif"

    def test_process_images_streaming_with_config(self):
        """Test process_images_streaming respects configuration."""
        config = ProcessingConfig(description_style="brief", max_description_length=100)
        image_paths = ["image1.jpg"]
        results = list(process_images_streaming(image_paths, config))
        assert len(results) == 1
        assert len(results[0].description) <= 100
