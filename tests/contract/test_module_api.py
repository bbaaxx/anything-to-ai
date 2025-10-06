"""
Contract tests for image processor module API.
These tests MUST FAIL initially as they test the VLM integration before implementation.
"""

import pytest
import os
from unittest.mock import patch

# Import the module interfaces we're testing
from anyfile_to_ai.image_processor import (
    create_config, process_images, validate_model_availability,
    get_available_models, ProcessingConfig, DescriptionResult
)
from anyfile_to_ai.image_processor.exceptions import ValidationError


class TestModuleAPIContract:
    """Test the module API contract for VLM integration."""

    def test_create_config_requires_vision_model_env(self):
        """Test that create_config reads from VISION_MODEL environment variable."""
        # This should FAIL initially - no VLM environment handling yet
        with patch.dict(os.environ, {}, clear=True):
            # Remove VISION_MODEL if set
            os.environ.pop('VISION_MODEL', None)

            # Should raise VLMConfigurationError when no VISION_MODEL set
            from anyfile_to_ai.image_processor.vlm_exceptions import VLMConfigurationError
            with pytest.raises(VLMConfigurationError) as exc_info:
                create_config()

            assert "VISION_MODEL" in str(exc_info.value)

    def test_create_config_with_vision_model_env(self):
        """Test create_config with VISION_MODEL environment variable set."""
        # This should FAIL initially - no VLM environment handling yet
        with patch.dict(os.environ, {'VISION_MODEL': 'google/gemma-3-4b'}):
            config = create_config()

            # Should contain VLM-specific fields
            assert hasattr(config, 'model_name')
            assert config.model_name == 'google/gemma-3-4b'
            assert hasattr(config, 'vlm_timeout_behavior')
            assert hasattr(config, 'auto_download_models')
            assert hasattr(config, 'validate_model_before_load')

    def test_process_images_returns_enhanced_results(self):
        """Test that process_images returns enhanced results with VLM data."""
        # This should FAIL initially - no VLM integration yet
        with patch.dict(os.environ, {'VISION_MODEL': 'google/gemma-3-4b'}):
            config = create_config()

            # Mock image files for testing
            test_images = ['test_image.jpg']

            # This will fail because VLM integration not implemented
            result = process_images(test_images, config)

            # Enhanced result should contain VLM fields
            assert hasattr(result, 'results')
            assert len(result.results) > 0

            first_result = result.results[0]
            # Test enhanced fields that should be added
            assert hasattr(first_result, 'technical_metadata')
            assert hasattr(first_result, 'vlm_processing_time')
            assert hasattr(first_result, 'model_version')
            assert hasattr(first_result, 'confidence_score')

            # VLM description should be real, not mock
            assert first_result.description != "Mock description for test image"

    def test_validate_model_availability_function_exists(self):
        """Test that validate_model_availability function is available."""
        # This should FAIL initially - function doesn't exist yet
        try:
            result = validate_model_availability('google/gemma-3-4b')
            assert isinstance(result, bool)
        except AttributeError:
            pytest.fail("validate_model_availability function not implemented")

    def test_get_available_models_function_exists(self):
        """Test that get_available_models function is available."""
        # This should FAIL initially - function doesn't exist yet
        try:
            models = get_available_models()
            assert isinstance(models, list)
            # Should contain at least some model identifiers
            assert len(models) >= 0  # Could be empty if no models available
        except AttributeError:
            pytest.fail("get_available_models function not implemented")

    def test_processing_config_has_vlm_fields(self):
        """Test that ProcessingConfig has VLM-specific fields."""
        # This should FAIL initially - VLM fields not added yet
        config = ProcessingConfig()

        # Should have new VLM fields
        assert hasattr(config, 'vlm_timeout_behavior')
        assert hasattr(config, 'auto_download_models')
        assert hasattr(config, 'validate_model_before_load')

    def test_description_result_has_enhanced_fields(self):
        """Test that DescriptionResult has enhanced VLM fields."""
        # This should FAIL initially - enhanced fields not added yet
        # We'll test the structure by trying to create one
        try:
            result = DescriptionResult(
                image_path="test.jpg",
                description="test description",
                confidence_score=0.95,
                processing_time=1.0,
                model_used="google/gemma-3-4b",
                prompt_used="test prompt",
                success=True,
                # New enhanced fields that should exist
                technical_metadata={"format": "JPEG", "dimensions": [100, 100], "file_size": 1000},
                vlm_processing_time=0.8,
                model_version="v1.0"
            )

            # All fields should be accessible
            assert result.technical_metadata is not None
            assert result.vlm_processing_time > 0
            assert result.model_version is not None

        except TypeError as e:
            pytest.fail(f"DescriptionResult missing enhanced fields: {e}")

    def test_backward_compatibility_preserved(self):
        """Test that existing API signatures are preserved."""
        # These should continue to work

        # Test create_config with existing parameters
        config = create_config(
            description_style="detailed",
            max_length=500,
            batch_size=4
        )
        assert config.description_style == "detailed"
        assert config.max_description_length == 500
        assert config.batch_size == 4

    def test_environment_variable_contract(self):
        """Test environment variable handling contract."""
        # This should FAIL initially - no VLM environment handling

        # Test that we can check for VISION_MODEL requirement
        with patch.dict(os.environ, {}, clear=True):
            os.environ.pop('VISION_MODEL', None)

            # Should be able to detect missing environment variable
            try:
                # This should eventually check environment and fail appropriately
                from anyfile_to_ai.image_processor.config import validate_vision_model_env
                validate_vision_model_env()
                pytest.fail("Should have raised ValidationError for missing VISION_MODEL")
            except ValidationError:
                pass  # Expected
            except (ImportError, AttributeError):
                pytest.fail("VLM configuration module not implemented")

    def test_error_hierarchy_extended(self):
        """Test that VLM-specific exceptions are available."""
        # This should FAIL initially - VLM exceptions not implemented
        try:
            from anyfile_to_ai.image_processor.exceptions import (
                VLMConfigurationError, VLMModelLoadError, VLMProcessingError,
                VLMTimeoutError, VLMModelNotFoundError
            )

            # All VLM exceptions should inherit from ImageProcessingError
            from anyfile_to_ai.image_processor.exceptions import ImageProcessingError

            assert issubclass(VLMConfigurationError, ImageProcessingError)
            assert issubclass(VLMModelLoadError, ImageProcessingError)
            assert issubclass(VLMProcessingError, ImageProcessingError)
            assert issubclass(VLMTimeoutError, VLMProcessingError)
            assert issubclass(VLMModelNotFoundError, VLMConfigurationError)

        except ImportError:
            pytest.fail("VLM-specific exceptions not implemented")
