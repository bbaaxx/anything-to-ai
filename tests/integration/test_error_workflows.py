"""Integration tests for error handling workflows."""

import pytest
import tempfile
import os
from PIL import Image
from image_processor import process_image, process_images, validate_image
from image_processor.exceptions import (
    ImageNotFoundError,
    UnsupportedFormatError,
    CorruptedImageError,
    ValidationError
)


class TestErrorHandlingWorkflows:
    """Integration tests for complete error handling scenarios."""

    @pytest.fixture
    def corrupted_image_file(self):
        """Create a corrupted image file for testing."""
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as f:
            # Write invalid JPEG data
            f.write(b'This is not a valid image file')
            corrupted_path = f.name

        yield corrupted_path
        os.unlink(corrupted_path)

    @pytest.fixture
    def text_file_as_image(self):
        """Create a text file with image extension."""
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as f:
            f.write(b'This is a text file pretending to be an image')
            text_path = f.name

        yield text_path
        os.unlink(text_path)

    def test_missing_file_error_workflow(self):
        """Test complete error workflow for missing files."""
        nonexistent_path = "definitely_does_not_exist.jpg"

        # Single image processing
        with pytest.raises(ImageNotFoundError) as exc_info:
            process_image(nonexistent_path)

        error = exc_info.value
        assert error.image_path == nonexistent_path
        assert "not found" in str(error).lower()

        # Validation should also fail
        with pytest.raises(ImageNotFoundError):
            validate_image(nonexistent_path)

    def test_unsupported_format_error_workflow(self):
        """Test complete error workflow for unsupported formats."""
        # Create a text file
        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as f:
            f.write(b'This is a text file')
            text_path = f.name

        try:
            # Single image processing
            with pytest.raises(UnsupportedFormatError) as exc_info:
                process_image(text_path)

            error = exc_info.value
            assert error.image_path == text_path
            assert "unsupported" in str(error).lower()

            # Validation should also fail
            with pytest.raises(UnsupportedFormatError):
                validate_image(text_path)

        finally:
            os.unlink(text_path)

    def test_corrupted_image_error_workflow(self, corrupted_image_file):
        """Test complete error workflow for corrupted images."""
        # Single image processing
        with pytest.raises(CorruptedImageError) as exc_info:
            process_image(corrupted_image_file)

        error = exc_info.value
        assert error.image_path == corrupted_image_file
        assert "corrupted" in str(error).lower()

        # Validation should also fail
        with pytest.raises(CorruptedImageError):
            validate_image(corrupted_image_file)

    def test_batch_processing_mixed_errors_workflow(self, corrupted_image_file):
        """Test batch processing with mixed valid/invalid files."""
        # Create one valid image
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as f:
            img = Image.new('RGB', (100, 100), color='red')
            img.save(f.name, 'JPEG')
            valid_image = f.name

        try:
            mixed_paths = [
                valid_image,
                "nonexistent.jpg",
                corrupted_image_file
            ]

            # Batch processing should handle mixed results gracefully
            results = process_images(mixed_paths)

            # Verify results structure
            assert results.total_images == 3
            assert len(results.results) == 3
            assert results.successful_count >= 0
            assert results.failed_count >= 0
            assert results.successful_count + results.failed_count == 3

            # At least one should succeed (the valid image)
            success_count = sum(1 for r in results.results if r.success)
            assert success_count >= 1

            # Verify individual result details
            for result in results.results:
                if result.success:
                    assert len(result.description) > 0
                else:
                    # Failed results should have empty or error descriptions
                    assert result.description == "" or "error" in result.description.lower()

        finally:
            os.unlink(valid_image)

    def test_validation_error_workflow_invalid_config(self):
        """Test validation error workflow for invalid configuration."""
        # Test various validation scenarios
        with pytest.raises(ValidationError) as exc_info:
            from image_processor import create_config
            create_config(description_style="invalid_style")

        assert "style" in str(exc_info.value).lower()

        with pytest.raises(ValidationError) as exc_info:
            create_config(max_length=0)

        assert "length" in str(exc_info.value).lower()

        with pytest.raises(ValidationError) as exc_info:
            create_config(batch_size=0)

        assert "batch" in str(exc_info.value).lower()

    def test_graceful_degradation_workflow(self):
        """Test graceful degradation when some operations fail."""
        # Create mixed batch with some valid, some invalid files
        test_paths = [
            "nonexistent1.jpg",
            "nonexistent2.png",
            "invalid.txt"
        ]

        # Batch processing should not crash, even with all invalid files
        results = process_images(test_paths)

        # Should return proper structure even for all failures
        assert results.total_images == 3
        assert len(results.results) == 3
        assert results.failed_count == 3
        assert results.successful_count == 0
        assert results.success is False
        assert results.error_message is not None

    def test_error_message_consistency_workflow(self, corrupted_image_file):
        """Test error message consistency across different scenarios."""
        # Test that similar errors produce consistent messages

        # Missing file errors
        try:
            process_image("missing1.jpg")
        except ImageNotFoundError as e1:
            try:
                process_image("missing2.jpg")
            except ImageNotFoundError as e2:
                # Error messages should follow same pattern
                assert "not found" in str(e1).lower()
                assert "not found" in str(e2).lower()

        # Corrupted file errors
        try:
            process_image(corrupted_image_file)
        except CorruptedImageError as e1:
            try:
                validate_image(corrupted_image_file)
            except CorruptedImageError as e2:
                # Error messages should be consistent
                assert "corrupted" in str(e1).lower()
                assert "corrupted" in str(e2).lower()

    def test_error_recovery_workflow(self):
        """Test error recovery in streaming scenarios."""
        from image_processor import process_images_streaming

        # Mix of valid and invalid files
        test_paths = [
            "nonexistent1.jpg",
            "nonexistent2.jpg"
        ]

        # Streaming should handle errors gracefully
        results = []
        try:
            for result in process_images_streaming(test_paths):
                results.append(result)
        except Exception:
            # Should not raise unhandled exceptions
            pytest.fail("Streaming should handle errors gracefully")

        # Should return results for all attempted files
        assert len(results) == len(test_paths)

        # All should be failures in this case
        for result in results:
            assert result.success is False
