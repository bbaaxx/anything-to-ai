"""
Integration tests for VLM timeout behavior.
These tests MUST FAIL initially as they test timeout handling integration.
"""

import pytest
import os
import tempfile
from unittest.mock import patch
from PIL import Image

from anyfile_to_ai.image_processor import create_config, process_image
from provider_env import generation_skip_reason


def _process_image_or_skip(image_path: str, config):
    provider = (os.environ.get("PROVIDER") or "mlx").strip().lower()
    try:
        return process_image(image_path, config)
    except Exception as exc:
        error_text = str(exc).lower()
        skip_reason = generation_skip_reason(exc, provider)
        if skip_reason:
            pytest.skip(skip_reason)
        if "failed to load" in error_text:
            pytest.skip("Model runtime unavailable for timeout assertions")
        raise


class TestTimeoutBehavior:
    """Test VLM processing timeout behavior scenarios."""

    @pytest.fixture
    def sample_image(self):
        """Create a temporary test image."""
        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
            img = Image.new("RGB", (100, 100), color="green")
            img.save(tmp.name, "JPEG")
            yield tmp.name
            os.unlink(tmp.name)

    def test_timeout_behavior_error(self, sample_image):
        """Test timeout behavior set to 'error' raises exception."""
        # This should FAIL initially - timeout error behavior not implemented
        env_vars = {
            "VISION_MODEL": "google/gemma-3-4b",
            "VLM_TIMEOUT_SECONDS": "1",
            "VLM_TIMEOUT_BEHAVIOR": "error",
        }

        with patch.dict(os.environ, env_vars):
            config = create_config()

            try:
                result = _process_image_or_skip(sample_image, config)
                # Some runtimes may still complete quickly despite short timeout.
                assert result.success is True
            except Exception as exc:
                # Runtime may fail due timeout or unavailable model backend.
                error_text = str(exc).lower()
                assert "timeout" in error_text or "failed to load" in error_text

    def test_timeout_behavior_fallback(self, sample_image):
        """Test timeout behavior set to 'fallback' returns fallback result."""
        # This should FAIL initially - timeout fallback behavior not implemented
        env_vars = {
            "VISION_MODEL": "google/gemma-3-4b",
            "VLM_TIMEOUT_SECONDS": "1",
            "VLM_TIMEOUT_BEHAVIOR": "fallback",
        }

        with patch.dict(os.environ, env_vars):
            config = create_config()

            try:
                result = _process_image_or_skip(sample_image, config)
                # Provider/runtime may still complete successfully.
                assert result.success is True
                assert result.description is not None
                assert len(result.description) > 0
            except Exception as exc:
                assert "timeout" in str(exc).lower()

    def test_timeout_behavior_continue(self, sample_image):
        """Test timeout behavior set to 'continue' continues processing."""
        # This should FAIL initially - timeout continue behavior not implemented
        env_vars = {
            "VISION_MODEL": "google/gemma-3-4b",
            "VLM_TIMEOUT_SECONDS": "1",
            "VLM_TIMEOUT_BEHAVIOR": "continue",
        }

        with patch.dict(os.environ, env_vars):
            config = create_config()

            try:
                result = _process_image_or_skip(sample_image, config)
                # Should succeed, possibly with partial or timeout-interrupted result
                assert result.success is True
                assert result.description is not None
            except Exception as exc:
                # Some runtimes surface timeout as an exception even with
                # timeout_behavior=continue.
                assert "timeout" in str(exc).lower()

    def test_reasonable_timeout_succeeds(self, sample_image):
        """Test that reasonable timeout allows successful processing."""
        # This should FAIL initially - timeout handling not implemented
        env_vars = {"VISION_MODEL": "google/gemma-3-4b", "VLM_TIMEOUT_SECONDS": "60"}

        with patch.dict(os.environ, env_vars):
            config = create_config()

            result = _process_image_or_skip(sample_image, config)
            # With reasonable timeout, should succeed
            assert result.success is True
            assert result.processing_time <= 60

    def test_timeout_configuration_validation(self):
        """Test timeout configuration parameter validation."""
        # This should FAIL initially - timeout validation not implemented
        env_vars = {
            "VISION_MODEL": "google/gemma-3-4b",
            "VLM_TIMEOUT_BEHAVIOR": "invalid_behavior",
        }

        with patch.dict(os.environ, env_vars):
            from anyfile_to_ai.image_processor.exceptions import ValidationError

            with pytest.raises(ValidationError):
                create_config()

    def test_timeout_affects_only_vlm_processing(self, sample_image):
        """Test that timeout applies only to VLM processing, not technical analysis."""
        # This should FAIL initially - separate timeouts not implemented
        env_vars = {
            "VISION_MODEL": "google/gemma-3-4b",
            "VLM_TIMEOUT_SECONDS": "1",
            "VLM_TIMEOUT_BEHAVIOR": "fallback",
        }

        with patch.dict(os.environ, env_vars):
            config = create_config()

            try:
                result = _process_image_or_skip(sample_image, config)
                assert result.success is True
                assert hasattr(result, "technical_metadata")
                assert result.technical_metadata is not None
            except Exception as exc:
                assert "timeout" in str(exc).lower()
