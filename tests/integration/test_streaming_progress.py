"""Integration tests for streaming processing with progress tracking."""

import pytest
import tempfile
import os
from PIL import Image
from image_processor import process_images_streaming, ProcessingConfig


class TestStreamingProgress:
    """Integration tests for streaming processing with progress callbacks."""

    @pytest.fixture
    def sample_images(self):
        """Create temporary sample images for testing."""
        images = []
        for i in range(4):  # Create 4 images for progress testing
            with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as f:
                img = Image.new('RGB', (100, 100), color=['red', 'green', 'blue', 'yellow'][i])
                img.save(f.name, 'JPEG')
                images.append(f.name)

        yield images

        for img_path in images:
            os.unlink(img_path)

    def test_streaming_processing_basic(self, sample_images):
        """Test basic streaming processing returns generator."""
        # Scenario from quickstart: Streaming processing
        result_generator = process_images_streaming(sample_images)

        # Should be a generator/iterator
        assert hasattr(result_generator, '__iter__')
        assert hasattr(result_generator, '__next__')

        # Collect all results
        results = list(result_generator)
        assert len(results) == len(sample_images)

        # Verify each result
        for i, result in enumerate(results):
            assert result.image_path == sample_images[i]
            assert result.success is True
            assert len(result.description) > 0

    def test_streaming_with_progress_callback(self, sample_images):
        """Test streaming processing calls progress callback correctly."""
        progress_calls = []

        def progress_handler(current, total):
            progress_calls.append((current, total))

        config = ProcessingConfig(progress_callback=progress_handler)
        results = list(process_images_streaming(sample_images, config))

        # Verify progress was tracked
        assert len(progress_calls) > 0
        assert len(results) == len(sample_images)

        # Verify progress calls are reasonable
        for current, total in progress_calls:
            assert current <= total
            assert total == len(sample_images)

        # Final progress should be complete
        final_current, final_total = progress_calls[-1]
        assert final_current == final_total

    def test_streaming_progress_callback_frequency(self, sample_images):
        """Test progress callback is called for each image."""
        progress_calls = []

        def progress_handler(current, total):
            progress_calls.append((current, total))

        config = ProcessingConfig(progress_callback=progress_handler)
        results = list(process_images_streaming(sample_images, config))

        # Should have at least one call per image processed
        assert len(progress_calls) >= len(sample_images)

        # Verify monotonic progress
        for i in range(1, len(progress_calls)):
            current_progress = progress_calls[i][0]
            previous_progress = progress_calls[i-1][0]
            assert current_progress >= previous_progress

    def test_streaming_order_preservation(self, sample_images):
        """Test streaming processing preserves input order."""
        results = list(process_images_streaming(sample_images))

        # Results should be in same order as input
        for i, result in enumerate(results):
            assert result.image_path == sample_images[i]

    def test_streaming_with_custom_config(self, sample_images):
        """Test streaming processing respects configuration."""
        config = ProcessingConfig(
            description_style="brief",
            max_description_length=100,
            batch_size=2
        )

        results = list(process_images_streaming(sample_images, config))

        # Verify configuration is applied
        for result in results:
            if result.success:
                assert len(result.description) <= 100

    def test_streaming_memory_efficiency(self, sample_images):
        """Test streaming processing is memory efficient."""
        # This test verifies that streaming doesn't load all images at once
        # by checking that we can process a result before all are complete

        results_processed = []

        def progress_handler(current, total):
            # We should be able to access already processed results
            # before all processing is complete
            if current < total:
                assert len(results_processed) >= current - 1

        config = ProcessingConfig(progress_callback=progress_handler)
        result_generator = process_images_streaming(sample_images, config)

        # Process one at a time to verify streaming behavior
        for result in result_generator:
            results_processed.append(result)
            assert result.success is True

        assert len(results_processed) == len(sample_images)

    def test_streaming_early_termination(self, sample_images):
        """Test streaming processing can be terminated early."""
        # Take only first 2 results from generator
        result_generator = process_images_streaming(sample_images)
        partial_results = []

        for i, result in enumerate(result_generator):
            partial_results.append(result)
            if i >= 1:  # Stop after 2 results
                break

        # Should have only processed 2 images
        assert len(partial_results) == 2
        for result in partial_results:
            assert result.success is True

    def test_streaming_progress_percentage_calculation(self, sample_images):
        """Test progress can be used to calculate percentages."""
        progress_percentages = []

        def progress_handler(current, total):
            percentage = (current / total) * 100
            progress_percentages.append(percentage)

        config = ProcessingConfig(progress_callback=progress_handler)
        list(process_images_streaming(sample_images, config))

        # Verify percentage calculations
        assert len(progress_percentages) > 0
        assert all(0 <= p <= 100 for p in progress_percentages)
        assert progress_percentages[-1] == 100.0  # Should reach 100%
