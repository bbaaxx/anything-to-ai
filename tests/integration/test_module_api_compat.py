"""
Integration tests for VLM module API compatibility.
These tests MUST FAIL initially as they test enhanced API compatibility.
"""

import pytest
import os
import tempfile
from unittest.mock import patch
from PIL import Image

from anyfile_to_ai.image_processor import create_config, process_image
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


def _process_images_or_skip(image_paths: list[str], config):
    provider = (os.environ.get("PROVIDER") or "mlx").strip().lower()
    try:
        return image_processor.process_images(image_paths, config)
    except ProcessingError as exc:
        skip_reason = generation_skip_reason(exc, provider)
        if skip_reason:
            pytest.skip(skip_reason)
        raise


class TestModuleAPICompatibility:
    """Test module API compatibility with VLM enhancements."""

    @pytest.fixture
    def sample_image(self):
        """Create a temporary test image."""
        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
            img = Image.new("RGB", (100, 100), color="purple")
            img.save(tmp.name, "JPEG")
            yield tmp.name
            os.unlink(tmp.name)

    def test_enhanced_api_functions_available(self):
        """Test that enhanced API functions are available."""
        # This should FAIL initially - enhanced API functions not implemented
        enhanced_functions = ["validate_model_availability", "get_available_models"]

        for func_name in enhanced_functions:
            assert hasattr(image_processor, func_name), f"Missing function: {func_name}"

    def test_validate_model_availability_api(self):
        """Test validate_model_availability API behavior."""
        model_name = os.environ.get("VISION_MODEL", "google/gemma-3-4b")
        result = image_processor.validate_model_availability(model_name)
        assert isinstance(result, bool)

        # Invalid model should return False
        result = image_processor.validate_model_availability("invalid/model")
        assert result is False

    def test_get_available_models_api(self):
        """Test get_available_models API behavior."""
        # This should FAIL initially - function not implemented
        models = image_processor.get_available_models()
        assert isinstance(models, list)

        # Should contain model identifiers
        for model in models:
            assert isinstance(model, str)
            assert len(model) > 0

    def test_enhanced_config_creation(self):
        """Test enhanced configuration creation."""
        with patch.dict(os.environ, {"VISION_MODEL": _vision_model_or_skip()}):
            config = create_config()

            # Should have enhanced VLM fields
            vlm_fields = [
                "vlm_timeout_behavior",
                "auto_download_models",
                "validate_model_before_load",
            ]

            for field in vlm_fields:
                assert hasattr(config, field), f"Missing VLM field: {field}"

    def test_enhanced_result_structure(self, sample_image):
        """Test enhanced result structure from processing."""
        with patch.dict(os.environ, {"VISION_MODEL": _vision_model_or_skip()}):
            config = create_config()

            result = _process_image_or_skip(sample_image, config)

            # Should have enhanced result fields
            enhanced_fields = [
                "technical_metadata",
                "vlm_processing_time",
                "model_version",
                "confidence_score",
            ]

            for field in enhanced_fields:
                assert hasattr(result, field), f"Missing enhanced field: {field}"

    def test_technical_metadata_structure(self, sample_image):
        """Test technical metadata structure in results."""
        with patch.dict(os.environ, {"VISION_MODEL": _vision_model_or_skip()}):
            config = create_config()

            result = _process_image_or_skip(sample_image, config)

            assert hasattr(result, "technical_metadata")
            tech_meta = result.technical_metadata

            # Technical metadata should have expected structure
            expected_fields = ["format", "dimensions", "file_size"]
            for field in expected_fields:
                assert field in tech_meta, f"Missing metadata field: {field}"

    def test_model_info_in_results(self, sample_image):
        """Test model information in processing results."""
        with patch.dict(os.environ, {"VISION_MODEL": _vision_model_or_skip()}):
            config = create_config()

            result = _process_image_or_skip(sample_image, config)

            # Should track which model was used
            assert result.model_used
            assert hasattr(result, "model_version")
            assert result.model_version is not None

    def test_confidence_scoring_api(self, sample_image):
        """Test confidence scoring in API results."""
        with patch.dict(os.environ, {"VISION_MODEL": _vision_model_or_skip()}):
            config = create_config()

            result = _process_image_or_skip(sample_image, config)

            # Confidence score should be present and valid
            assert hasattr(result, "confidence_score")
            if result.confidence_score is not None:
                assert 0.0 <= result.confidence_score <= 1.0

    def test_separate_timing_metrics(self, sample_image):
        """Test separate timing metrics for VLM vs total processing."""
        with patch.dict(os.environ, {"VISION_MODEL": _vision_model_or_skip()}):
            config = create_config()

            result = _process_image_or_skip(sample_image, config)

            # Should have separate VLM processing time
            assert hasattr(result, "vlm_processing_time")
            assert result.vlm_processing_time > 0
            assert result.processing_time > 0

            # VLM time should be part of total time
            assert result.vlm_processing_time <= result.processing_time

    def test_error_handling_api_compatibility(self):
        """Test error handling API compatibility."""
        # This should FAIL initially - enhanced error handling not implemented
        from anyfile_to_ai.image_processor.exceptions import ImageProcessingError

        # Should be able to import VLM-specific exceptions
        try:
            from anyfile_to_ai.image_processor.exceptions import (
                VLMConfigurationError,
                VLMModelLoadError,
                VLMProcessingError,
                VLMTimeoutError,
            )

            # All should inherit from base exception
            vlm_exceptions = [
                VLMConfigurationError,
                VLMModelLoadError,
                VLMProcessingError,
                VLMTimeoutError,
            ]

            for exc_class in vlm_exceptions:
                assert issubclass(exc_class, ImageProcessingError)

        except ImportError:
            pytest.fail("VLM-specific exceptions not available in API")

    def test_environment_configuration_api(self):
        """Test environment configuration through API."""
        with patch.dict(os.environ, {"VISION_MODEL": "google/gemma-3-4b"}):
            # API should respect environment variables
            config = create_config()

            # Should read from environment
            assert config.model_name == "google/gemma-3-4b"

        # Should fail without environment variable
        with patch.dict(os.environ, {}, clear=True):
            os.environ.pop("VISION_MODEL", None)

            from anyfile_to_ai.image_processor.exceptions import ValidationError
            from anyfile_to_ai.image_processor.vlm_exceptions import VLMConfigurationError

            with pytest.raises((ValidationError, VLMConfigurationError)):
                create_config()

    def test_batch_processing_api_enhancement(self, sample_image):
        """Test batch processing API enhancements."""
        with patch.dict(os.environ, {"VISION_MODEL": _vision_model_or_skip()}):
            config = create_config(batch_size=1)

            result = _process_images_or_skip([sample_image], config)

            # Batch result should have enhanced information
            assert result.success is True
            assert len(result.results) == 1

            # Each result should have enhanced fields
            batch_result = result.results[0]
            assert hasattr(batch_result, "technical_metadata")
            assert hasattr(batch_result, "vlm_processing_time")
