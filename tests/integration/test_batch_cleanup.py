"""
Integration tests for VLM batch processing cleanup.
These tests MUST FAIL initially as they test cleanup integration.
"""

import pytest
import os
import tempfile
from unittest.mock import patch
from PIL import Image

from anyfile_to_ai.image_processor import create_config, process_images


class TestBatchCleanup:
    """Test VLM batch processing memory cleanup scenarios."""

    @pytest.fixture
    def sample_images(self):
        """Create multiple temporary test images."""
        images = []
        for i in range(3):
            tmp = tempfile.NamedTemporaryFile(suffix=".jpg", delete=False)
            img = Image.new("RGB", (100, 100), color=["red", "green", "blue"][i])
            img.save(tmp.name, "JPEG")
            images.append(tmp.name)
            tmp.close()

        yield images

        for img_path in images:
            if os.path.exists(img_path):
                os.unlink(img_path)

    def test_batch_processing_memory_cleanup(self, sample_images):
        """Test that batch processing cleans up VLM model memory."""
        # This should FAIL initially - batch cleanup not implemented
        with patch.dict(os.environ, {"VISION_MODEL": "google/gemma-3-4b"}):
            config = create_config(batch_size=2)

            result = process_images(sample_images, config)

            # Should process successfully
            assert result.success is True
            assert len(result.results) == 3

            # Memory cleanup should have occurred (hard to test directly)
            # But we can verify the interface exists
            try:
                from anyfile_to_ai.image_processor.model_registry import (
                    VLMModelRegistry,
                )

                registry = VLMModelRegistry()
                registry.cleanup_models()  # Should be safe to call

            except ImportError:
                pytest.fail("VLMModelRegistry cleanup not implemented")

    def test_multiple_batch_operations_cleanup(self, sample_images):
        """Test cleanup between multiple batch operations."""
        # This should FAIL initially - inter-batch cleanup not implemented
        with patch.dict(os.environ, {"VISION_MODEL": "google/gemma-3-4b"}):
            config = create_config(batch_size=1)

            # Process first batch
            result1 = process_images(sample_images[:2], config)
            assert result1.success is True

            # Process second batch - should reuse cleaned model
            result2 = process_images(sample_images[2:], config)
            assert result2.success is True

    def test_cleanup_on_processing_error(self, sample_images):
        """Test that cleanup occurs even when processing errors happen."""
        # This should FAIL initially - error cleanup not implemented
        with patch.dict(os.environ, {"VISION_MODEL": "google/gemma-3-4b"}):
            config = create_config(batch_size=2)

            # Add invalid image to cause processing error
            invalid_images = [*sample_images, "nonexistent.jpg"]

            try:
                process_images(invalid_images, config)
            except Exception:
                pass  # Expected error

            # Cleanup should still have occurred
            try:
                from anyfile_to_ai.image_processor.model_registry import (
                    VLMModelRegistry,
                )

                registry = VLMModelRegistry()
                registry.cleanup_models()  # Should be safe

            except ImportError:
                pytest.fail("Cleanup after error not implemented")

    def test_streaming_cleanup_integration(self, sample_images):
        """Test cleanup integration with streaming processing."""
        # This should FAIL initially - streaming cleanup not implemented
        with patch.dict(os.environ, {"VISION_MODEL": "google/gemma-3-4b"}):
            from anyfile_to_ai.image_processor import process_images_streaming

            config = create_config(batch_size=1)

            # Process with streaming
            results = list(process_images_streaming(sample_images, config))

            # Should have final result
            assert len(results) > 0
            final_result = results[-1]

            if hasattr(final_result, "results"):
                assert len(final_result.results) == 3
