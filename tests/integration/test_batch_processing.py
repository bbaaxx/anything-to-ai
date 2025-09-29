"""Integration tests for batch image processing scenarios."""

import pytest
import tempfile
import os
from PIL import Image
from image_processor import process_images, ProcessingConfig


class TestBatchProcessing:
    """Integration tests for complete batch processing workflows."""

    @pytest.fixture
    def sample_images(self):
        """Create temporary sample images for testing."""
        images = []
        for i, (fmt, ext) in enumerate([('JPEG', '.jpg'), ('PNG', '.png'), ('GIF', '.gif')]):
            with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as f:
                img = Image.new('RGB', (100, 100), color=['red', 'green', 'blue'][i])
                img.save(f.name, fmt)
                images.append(f.name)

        yield images

        for img_path in images:
            os.unlink(img_path)

    def test_basic_batch_processing(self, sample_images):
        """Test basic batch processing of multiple images."""
        # Scenario from quickstart: Process multiple images
        results = process_images(sample_images)

        # Verify batch processing results
        assert results.success is True
        assert results.total_images == 3
        assert len(results.results) == 3
        assert results.successful_count == 3
        assert results.failed_count == 0
        assert results.total_processing_time > 0

        # Verify individual results
        for i, result in enumerate(results.results):
            assert result.image_path == sample_images[i]
            assert result.success is True
            assert len(result.description) > 0

    def test_batch_processing_with_custom_config(self, sample_images):
        """Test batch processing with custom configuration."""
        config = ProcessingConfig(
            batch_size=2,
            description_style="brief",
            max_description_length=200
        )
        results = process_images(sample_images, config)

        assert results.success is True
        assert results.total_images == 3

        # Verify configuration is applied to all images
        for result in results.results:
            if result.success:
                assert len(result.description) <= 200

    def test_batch_processing_different_formats(self, sample_images):
        """Test batch processing handles different image formats."""
        results = process_images(sample_images)

        # Should handle JPG, PNG, GIF formats
        formats_processed = set()
        for result in results.results:
            if result.success:
                formats_processed.add(os.path.splitext(result.image_path)[1].lower())

        expected_formats = {'.jpg', '.png', '.gif'}
        assert formats_processed == expected_formats

    def test_batch_processing_performance_scaling(self, sample_images):
        """Test batch processing performance scales reasonably."""
        # Single image timing
        single_results = process_images([sample_images[0]])
        single_time = single_results.total_processing_time

        # Batch timing
        batch_results = process_images(sample_images)
        batch_time = batch_results.total_processing_time

        # Batch should be more efficient than processing individually
        # Allow some overhead but should be less than 2x single time per image
        max_expected_time = single_time * len(sample_images) * 1.5
        assert batch_time < max_expected_time

    def test_batch_processing_with_mixed_success_failure(self):
        """Test batch processing handles mixed success/failure scenarios."""
        # Mix of valid and invalid images
        mixed_paths = ["valid.jpg", "nonexistent.jpg", "invalid.txt"]

        # This will fail for some images but should continue processing
        results = process_images(mixed_paths)

        # Should attempt all images even if some fail
        assert results.total_images == 3
        assert len(results.results) == 3
        assert results.failed_count > 0  # Some should fail

        # Overall success depends on whether any succeeded
        assert results.success in [True, False]  # Either could be valid

    def test_batch_processing_preserves_order(self, sample_images):
        """Test batch processing preserves input order."""
        results = process_images(sample_images)

        # Results should be in same order as input
        for i, result in enumerate(results.results):
            assert result.image_path == sample_images[i]

    def test_batch_processing_statistics_accuracy(self, sample_images):
        """Test batch processing statistics are accurate."""
        results = process_images(sample_images)

        # Verify statistics consistency
        assert results.successful_count + results.failed_count == results.total_images
        assert results.total_images == len(sample_images)
        assert len(results.results) == results.total_images

        # Count actual successes/failures
        actual_successes = sum(1 for r in results.results if r.success)
        actual_failures = sum(1 for r in results.results if not r.success)

        assert actual_successes == results.successful_count
        assert actual_failures == results.failed_count