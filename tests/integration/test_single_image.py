"""Integration tests for single image processing scenarios."""

import pytest
import tempfile
import os
from PIL import Image
from anything_to_ai.image_processor import process_image, ProcessingConfig


class TestSingleImageProcessing:
    """Integration tests for complete single image processing workflows."""

    @pytest.fixture
    def sample_image(self):
        """Create a temporary sample image for testing."""
        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as f:
            # Create a simple 100x100 RGB image
            img = Image.new("RGB", (100, 100), color="red")
            img.save(f.name, "JPEG")
            yield f.name
        os.unlink(f.name)

    def test_basic_single_image_processing(self, sample_image):
        """Test basic single image processing with default settings."""
        # Scenario from quickstart: Basic processing with defaults
        result = process_image(sample_image)

        # Verify complete workflow
        assert result.success is True
        assert result.image_path == sample_image
        assert len(result.description) > 0
        assert result.processing_time > 0
        assert result.model_used is not None
        assert result.prompt_used is not None

    def test_single_image_with_custom_config(self, sample_image):
        """Test single image processing with custom configuration."""
        # Scenario from quickstart: Custom configuration
        config = ProcessingConfig(description_style="brief", max_description_length=200)
        result = process_image(sample_image, config)

        # Verify configuration is respected
        assert result.success is True
        assert len(result.description) <= 200
        assert "brief" in result.prompt_used.lower() or result.description != ""

    def test_single_image_detailed_style(self, sample_image):
        """Test single image processing with detailed style."""
        config = ProcessingConfig(description_style="detailed", max_description_length=800)
        result = process_image(sample_image, config)

        assert result.success is True
        # Detailed descriptions should be longer when possible
        assert len(result.description) > 50

    def test_single_image_technical_style(self, sample_image):
        """Test single image processing with technical style."""
        config = ProcessingConfig(description_style="technical", max_description_length=500)
        result = process_image(sample_image, config)

        assert result.success is True
        # Technical descriptions should contain specific terminology
        assert len(result.description) > 0

    def test_single_image_performance_requirements(self, sample_image):
        """Test single image processing meets performance requirements."""
        result = process_image(sample_image)

        # Performance requirement: <2s per image
        assert result.processing_time < 2.0
        assert result.success is True

    def test_single_image_metadata_completeness(self, sample_image):
        """Test single image processing returns complete metadata."""
        result = process_image(sample_image)

        # Verify all required metadata is present
        assert hasattr(result, "confidence_score")
        assert hasattr(result, "processing_time")
        assert hasattr(result, "model_used")
        assert hasattr(result, "prompt_used")
        assert hasattr(result, "success")

        # Verify data types
        assert isinstance(result.image_path, str)
        assert isinstance(result.description, str)
        assert isinstance(result.processing_time, float)
        assert isinstance(result.model_used, str)
        assert isinstance(result.prompt_used, str)
        assert isinstance(result.success, bool)
