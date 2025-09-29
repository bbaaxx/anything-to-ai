"""
Integration tests for basic VLM processing.
These tests MUST FAIL initially as they test end-to-end VLM integration.
"""

import pytest
import os
import tempfile
from unittest.mock import patch
from PIL import Image

from image_processor import process_image, process_images, create_config
from image_processor.exceptions import ValidationError


class TestBasicVLMIntegration:
    """Test basic VLM processing integration scenarios."""

    @pytest.fixture
    def sample_image(self):
        """Create a temporary test image."""
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp:
            # Create a simple test image
            img = Image.new('RGB', (100, 100), color='red')
            img.save(tmp.name, 'JPEG')
            yield tmp.name
            os.unlink(tmp.name)

    def test_single_image_vlm_processing(self, sample_image):
        """Test processing single image with VLM."""
        # This should FAIL initially - VLM integration not implemented
        with patch.dict(os.environ, {'VISION_MODEL': 'google/gemma-3-4b'}):
            config = create_config(description_style="detailed")

            result = process_image(sample_image, config)

            # Result should contain real VLM description
            assert result.success is True
            assert result.description is not None
            assert len(result.description) > 0

            # Should not be mock description
            assert "Mock description" not in result.description
            assert result.description != f"Mock description for {os.path.basename(sample_image)}"

            # Should have VLM-specific fields
            assert hasattr(result, 'technical_metadata')
            assert hasattr(result, 'vlm_processing_time')
            assert hasattr(result, 'model_version')
            assert hasattr(result, 'confidence_score')

            # Model should be from environment
            assert result.model_used == "google/gemma-3-4b"

    def test_batch_vlm_processing(self, sample_image):
        """Test batch processing multiple images with VLM."""
        # This should FAIL initially - batch VLM processing not implemented
        with patch.dict(os.environ, {'VISION_MODEL': 'google/gemma-3-4b'}):
            # Create additional test images
            image_paths = [sample_image]

            config = create_config(description_style="brief", batch_size=2)

            result = process_images(image_paths, config)

            # Batch result should be successful
            assert result.success is True
            assert len(result.results) == 1
            assert result.successful_count == 1
            assert result.failed_count == 0

            # Each result should have VLM description
            for img_result in result.results:
                assert img_result.success is True
                assert "Mock description" not in img_result.description
                assert img_result.model_used == "google/gemma-3-4b"

    def test_vlm_processing_without_environment_variable(self, sample_image):
        """Test that VLM processing fails appropriately without VISION_MODEL."""
        # This should FAIL initially - environment validation not integrated
        with patch.dict(os.environ, {}, clear=True):
            os.environ.pop('VISION_MODEL', None)

            with pytest.raises(ValidationError) as exc_info:
                config = create_config()
                process_image(sample_image, config)

            assert "VISION_MODEL" in str(exc_info.value)

    def test_vlm_processing_with_different_styles(self, sample_image):
        """Test VLM processing with different description styles."""
        # This should FAIL initially - style-aware VLM processing not implemented
        with patch.dict(os.environ, {'VISION_MODEL': 'google/gemma-3-4b'}):
            styles = ["detailed", "brief", "technical"]

            for style in styles:
                config = create_config(description_style=style)
                result = process_image(sample_image, config)

                assert result.success is True
                assert result.description is not None
                assert len(result.description) > 0

                # Description should reflect the requested style
                # (This is more of a contract that VLM should respect)
                assert "Mock description" not in result.description

    def test_vlm_processing_with_timeout(self, sample_image):
        """Test VLM processing respects timeout configuration."""
        # This should FAIL initially - timeout handling not implemented
        with patch.dict(os.environ, {'VISION_MODEL': 'google/gemma-3-4b'}):
            config = create_config(timeout_seconds=30)

            result = process_image(sample_image, config)

            # Should complete within timeout
            assert result.success is True
            assert result.processing_time <= 30

    def test_vlm_processing_preserves_technical_metadata(self, sample_image):
        """Test that VLM processing preserves existing technical metadata."""
        # This should FAIL initially - metadata preservation not implemented
        with patch.dict(os.environ, {'VISION_MODEL': 'google/gemma-3-4b'}):
            config = create_config()

            result = process_image(sample_image, config)

            # Should have both VLM and technical metadata
            assert result.success is True
            assert hasattr(result, 'technical_metadata')

            # Technical metadata should be present and accurate
            tech_meta = result.technical_metadata
            assert 'format' in tech_meta
            assert 'dimensions' in tech_meta
            assert 'file_size' in tech_meta

            # Dimensions should match the test image (100x100)
            assert tech_meta['dimensions'] == [100, 100]

    def test_vlm_processing_confidence_scores(self, sample_image):
        """Test that VLM processing returns confidence scores when available."""
        # This should FAIL initially - confidence scoring not implemented
        with patch.dict(os.environ, {'VISION_MODEL': 'google/gemma-3-4b'}):
            config = create_config()

            result = process_image(sample_image, config)

            assert result.success is True

            # Confidence score should be present and valid
            if result.confidence_score is not None:
                assert 0.0 <= result.confidence_score <= 1.0

    def test_vlm_processing_model_info(self, sample_image):
        """Test that VLM processing returns model information."""
        # This should FAIL initially - model info tracking not implemented
        with patch.dict(os.environ, {'VISION_MODEL': 'google/gemma-3-4b'}):
            config = create_config()

            result = process_image(sample_image, config)

            assert result.success is True

            # Model information should be present
            assert result.model_used == "google/gemma-3-4b"
            assert hasattr(result, 'model_version')
            assert result.model_version is not None

    def test_vlm_processing_timing_metrics(self, sample_image):
        """Test that VLM processing tracks timing metrics separately."""
        # This should FAIL initially - separate timing not implemented
        with patch.dict(os.environ, {'VISION_MODEL': 'google/gemma-3-4b'}):
            config = create_config()

            result = process_image(sample_image, config)

            assert result.success is True

            # Should have separate timing for VLM vs overall processing
            assert result.processing_time > 0
            assert hasattr(result, 'vlm_processing_time')
            assert result.vlm_processing_time > 0

    def test_vlm_processing_error_handling(self):
        """Test VLM processing handles errors gracefully."""
        # This should FAIL initially - VLM error handling not implemented
        with patch.dict(os.environ, {'VISION_MODEL': 'google/gemma-3-4b'}):
            config = create_config()

            # Test with non-existent image
            with pytest.raises(Exception):  # Should be specific VLM exception
                process_image("nonexistent.jpg", config)

    def test_vlm_processing_streaming_compatibility(self, sample_image):
        """Test that VLM processing works with streaming interface."""
        # This should FAIL initially - streaming VLM integration not implemented
        with patch.dict(os.environ, {'VISION_MODEL': 'google/gemma-3-4b'}):
            from image_processor import process_images_streaming

            config = create_config(batch_size=1)

            # Should be able to process with streaming
            results = list(process_images_streaming([sample_image], config))

            assert len(results) > 0
            final_result = results[-1]  # Final result should be complete

            if hasattr(final_result, 'results'):
                assert len(final_result.results) == 1
                assert final_result.results[0].success is True
                assert "Mock description" not in final_result.results[0].description
