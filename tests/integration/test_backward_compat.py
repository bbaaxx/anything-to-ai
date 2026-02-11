"""
Integration tests for VLM backward compatibility.
These tests MUST FAIL initially as they test enhanced compatibility.
"""

import pytest
import os
import tempfile
from unittest.mock import patch
from PIL import Image

from anyfile_to_ai.image_processor import create_config, process_image, process_images
from anyfile_to_ai.image_processor.exceptions import ProcessingError
from anyfile_to_ai import image_processor
from provider_env import generation_skip_reason


def _vision_model_or_skip() -> str:
    model = os.environ.get("VISION_MODEL")
    if not model:
        pytest.skip("VISION_MODEL not set for runtime-dependent image integration tests")
    return model


def _process_image_or_skip(image_path: str, config):
    provider = (os.environ.get("PROVIDER") or "mlx").strip().lower()
    try:
        return process_image(image_path, config)
    except ProcessingError as exc:
        skip_reason = generation_skip_reason(exc, provider)
        if skip_reason:
            pytest.skip(skip_reason)
        raise


class TestBackwardCompatibility:
    """Test that VLM integration maintains backward compatibility."""

    @pytest.fixture
    def sample_image(self):
        """Create a temporary test image."""
        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
            img = Image.new("RGB", (100, 100), color="yellow")
            img.save(tmp.name, "JPEG")
            yield tmp.name
            os.unlink(tmp.name)

    def test_existing_create_config_signature(self):
        """Test that existing create_config signature still works."""
        # All existing parameter combinations should work with the active model.
        with patch.dict(os.environ, {"VISION_MODEL": _vision_model_or_skip()}):
            # All existing parameter combinations should work
            config1 = create_config()
            config2 = create_config(description_style="brief")
            config3 = create_config(description_style="detailed", max_length=300)
            config4 = create_config(description_style="technical", max_length=500, batch_size=2)

            # All should have expected existing fields
            for config in [config1, config2, config3, config4]:
                assert hasattr(config, "description_style")
                assert hasattr(config, "max_description_length")
                assert hasattr(config, "batch_size")

    def test_existing_process_image_signature(self, sample_image):
        """Test that existing process_image signature still works."""
        with patch.dict(os.environ, {"VISION_MODEL": _vision_model_or_skip()}):
            config = create_config()

            # Existing signature should work
            result = _process_image_or_skip(sample_image, config)

            # Should have all existing fields
            assert hasattr(result, "image_path")
            assert hasattr(result, "description")
            assert hasattr(result, "processing_time")
            assert hasattr(result, "success")

    def test_existing_process_images_signature(self, sample_image):
        """Test that existing process_images signature still works."""
        with patch.dict(os.environ, {"VISION_MODEL": _vision_model_or_skip()}):
            config = create_config(batch_size=1)

            # Existing signature should work
            result = process_images([sample_image], config)

            # Should have all existing fields
            assert hasattr(result, "success")
            assert hasattr(result, "results")
            assert hasattr(result, "total_images")
            assert hasattr(result, "successful_count")
            assert hasattr(result, "failed_count")

    def test_existing_exception_hierarchy_preserved(self):
        """Test that existing exception hierarchy is preserved."""
        from anyfile_to_ai.image_processor.exceptions import (
            ImageProcessingError,
            ImageNotFoundError,
            UnsupportedFormatError,
            CorruptedImageError,
            ProcessingError,
            ValidationError,
        )

        # All existing exceptions should still exist
        assert issubclass(ImageNotFoundError, ImageProcessingError)
        assert issubclass(UnsupportedFormatError, ImageProcessingError)
        assert issubclass(CorruptedImageError, ImageProcessingError)
        assert issubclass(ProcessingError, ImageProcessingError)
        assert issubclass(ValidationError, ImageProcessingError)

    def test_existing_output_format_compatibility(self, sample_image):
        """Test that output formats remain compatible."""
        with patch.dict(os.environ, {"VISION_MODEL": _vision_model_or_skip()}):
            config = create_config()

            result = _process_image_or_skip(sample_image, config)

            # Result should have all existing fields with correct types
            assert isinstance(result.image_path, str)
            assert isinstance(result.description, str)
            assert isinstance(result.processing_time, (int, float))
            assert isinstance(result.success, bool)

    def test_existing_module_api_preserved(self):
        """Test that existing module API functions are preserved."""

        # All existing functions should still be available
        existing_functions = [
            "process_image",
            "process_images",
            "validate_image",
            "get_supported_formats",
            "process_images_streaming",
            "create_config",
            "get_image_info",
        ]

        for func_name in existing_functions:
            assert hasattr(image_processor, func_name)

    def test_existing_streaming_interface_preserved(self, sample_image):
        """Test that streaming interface remains compatible."""
        with patch.dict(os.environ, {"VISION_MODEL": _vision_model_or_skip()}):
            from anyfile_to_ai.image_processor import process_images_streaming

            config = create_config()

            # Should work with existing signature
            results = list(process_images_streaming([sample_image], config))

            assert len(results) > 0

    def test_enhanced_fields_added_not_replaced(self, sample_image):
        """Test that enhanced fields are added, not replacing existing ones."""
        with patch.dict(os.environ, {"VISION_MODEL": _vision_model_or_skip()}):
            config = create_config()

            result = _process_image_or_skip(sample_image, config)

            # All existing fields should be present
            existing_fields = [
                "image_path",
                "description",
                "processing_time",
                "success",
                "model_used",
                "prompt_used",
            ]

            for field in existing_fields:
                assert hasattr(result, field), f"Missing existing field: {field}"

            # Enhanced fields should be added
            enhanced_fields = [
                "technical_metadata",
                "vlm_processing_time",
                "model_version",
                "confidence_score",
            ]

            for field in enhanced_fields:
                assert hasattr(result, field), f"Missing enhanced field: {field}"
