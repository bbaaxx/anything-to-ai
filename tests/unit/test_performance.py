"""Unit tests for performance validation."""

import pytest
import tempfile
import time
import os
from PIL import Image
from image_processor import process_image, process_images, ProcessingConfig


class TestPerformanceValidation:
    """Unit tests for performance requirements."""

    @pytest.fixture
    def sample_image(self):
        """Create a sample image for performance testing."""
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as f:
            img = Image.new('RGB', (500, 500), color='blue')
            img.save(f.name, 'JPEG')
            yield f.name
        os.unlink(f.name)

    def test_single_image_processing_performance(self, sample_image):
        """Test single image processing meets <2s requirement."""
        start_time = time.time()
        result = process_image(sample_image)
        end_time = time.time()

        processing_time = end_time - start_time

        # Performance requirement: <2s per image
        assert processing_time < 2.0
        assert result.success is True
        assert result.processing_time < 2.0

    def test_batch_processing_efficiency(self, sample_image):
        """Test batch processing is more efficient than individual processing."""
        # Process single image to get baseline
        start_time = time.time()
        process_image(sample_image)
        single_time = time.time() - start_time

        # Process same image 3 times in batch
        start_time = time.time()
        batch_result = process_images([sample_image, sample_image, sample_image])
        batch_time = time.time() - start_time

        # Batch should be more efficient (less than 2x single time)
        efficiency_threshold = single_time * 2.5  # Allow some overhead
        assert batch_time < efficiency_threshold
        assert batch_result.success is True
        assert batch_result.total_images == 3

    def test_streaming_processing_memory_efficiency(self, sample_image):
        """Test streaming processing doesn't accumulate excessive memory."""
        import psutil
        import os

        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss

        # Process multiple images via streaming
        from image_processor import process_images_streaming
        image_paths = [sample_image] * 5

        results = []
        for result in process_images_streaming(image_paths):
            results.append(result)

        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory

        # Memory increase should be reasonable (<50MB for test)
        assert memory_increase < 50 * 1024 * 1024  # 50MB limit
        assert len(results) == 5

    def test_configuration_validation_performance(self):
        """Test configuration validation is fast."""
        from image_processor import create_config

        start_time = time.time()

        # Create multiple configurations
        for i in range(100):
            create_config(
                description_style="brief",
                max_length=200,
                batch_size=2
            )

        end_time = time.time()
        validation_time = end_time - start_time

        # Configuration validation should be very fast
        assert validation_time < 0.1  # 100ms for 100 validations

    def test_error_handling_performance(self):
        """Test error handling doesn't cause significant delays."""
        from image_processor.exceptions import ImageNotFoundError

        start_time = time.time()

        # Test multiple error conditions
        for i in range(10):
            try:
                process_image(f"nonexistent_{i}.jpg")
            except ImageNotFoundError:
                pass  # Expected

        end_time = time.time()
        error_time = end_time - start_time

        # Error handling should be fast
        assert error_time < 0.5  # 500ms for 10 error cases

    def test_progress_callback_overhead(self, sample_image):
        """Test progress callbacks don't significantly impact performance."""
        progress_calls = []

        def progress_callback(current, total):
            progress_calls.append((current, total))

        config_with_progress = ProcessingConfig(progress_callback=progress_callback)
        config_without_progress = ProcessingConfig()

        # Process with progress callback
        start_time = time.time()
        result_with_progress = process_images([sample_image, sample_image], config_with_progress)
        time_with_progress = time.time() - start_time

        # Process without progress callback
        start_time = time.time()
        result_without_progress = process_images([sample_image, sample_image], config_without_progress)
        time_without_progress = time.time() - start_time

        # Progress callback overhead should be minimal
        overhead_ratio = time_with_progress / time_without_progress
        assert overhead_ratio < 1.2  # <20% overhead

        # Verify progress was tracked
        assert len(progress_calls) > 0
        assert result_with_progress.success is True
        assert result_without_progress.success is True
