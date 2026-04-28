"""Unit tests for token reduction fallback functionality."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from anyfile_to_ai.image_processor.config import VLMConfig
from anyfile_to_ai.image_processor.vlm_exceptions import (
    VLMContextLengthError,
    VLMMemoryError,
    VLMProcessingError,
)
from anyfile_to_ai.image_processor.vlm_models import ModelConfiguration
from anyfile_to_ai.image_processor.vlm_processor import (
    VLMProcessor,
    _get_default_fallback_levels,
    _is_memory_or_context_error,
)


# ---------------------------------------------------------------------------
# Exception class tests
# ---------------------------------------------------------------------------


class TestVLMMemoryError:
    """Tests for VLMMemoryError exception class."""

    def test_inherits_from_vlm_processing_error(self):
        """VLMMemoryError should inherit from VLMProcessingError."""
        assert issubclass(VLMMemoryError, VLMProcessingError)

    def test_stores_attempted_tokens(self):
        """VLMMemoryError should store attempted_tokens attribute."""
        error = VLMMemoryError(
            "Out of memory",
            image_path="test.jpg",
            model_name="test-model",
            attempted_tokens=8192,
        )
        assert error.attempted_tokens == 8192
        assert error.image_path == "test.jpg"
        assert error.model_name == "test-model"

    def test_attempted_tokens_optional(self):
        """VLMMemoryError should work without attempted_tokens."""
        error = VLMMemoryError("Out of memory", image_path="test.jpg")
        assert error.attempted_tokens is None
        assert error.image_path == "test.jpg"


class TestVLMContextLengthError:
    """Tests for VLMContextLengthError exception class."""

    def test_inherits_from_vlm_processing_error(self):
        """VLMContextLengthError should inherit from VLMProcessingError."""
        assert issubclass(VLMContextLengthError, VLMProcessingError)

    def test_stores_attempted_tokens(self):
        """VLMContextLengthError should store attempted_tokens attribute."""
        error = VLMContextLengthError(
            "Context length exceeded",
            image_path="test.jpg",
            model_name="test-model",
            attempted_tokens=4096,
        )
        assert error.attempted_tokens == 4096
        assert error.image_path == "test.jpg"

    def test_attempted_tokens_optional(self):
        """VLMContextLengthError should work without attempted_tokens."""
        error = VLMContextLengthError("Context length exceeded", image_path="test.jpg")
        assert error.attempted_tokens is None


# ---------------------------------------------------------------------------
# Error detection helper tests
# ---------------------------------------------------------------------------


class TestIsMemoryOrContextError:
    """Tests for _is_memory_or_context_error detection helper."""

    def test_detects_vlm_memory_error(self):
        """Should detect VLMMemoryError as recoverable memory error."""
        error = VLMMemoryError("Out of memory", attempted_tokens=8192)
        is_recoverable, error_type = _is_memory_or_context_error(error)
        assert is_recoverable is True
        assert error_type == "memory"

    def test_detects_vlm_context_length_error(self):
        """Should detect VLMContextLengthError as recoverable context error."""
        error = VLMContextLengthError("Context length exceeded", attempted_tokens=4096)
        is_recoverable, error_type = _is_memory_or_context_error(error)
        assert is_recoverable is True
        assert error_type == "context"

    def test_detects_memory_error_by_pattern(self):
        """Should detect memory errors by message pattern."""
        error = RuntimeError("CUDA out of memory: allocation failed")
        is_recoverable, error_type = _is_memory_or_context_error(error)
        assert is_recoverable is True
        assert error_type == "memory"

    def test_detects_context_error_by_pattern(self):
        """Should detect context errors by message pattern."""
        error = RuntimeError("maximum context length exceeded")
        is_recoverable, error_type = _is_memory_or_context_error(error)
        assert is_recoverable is True
        assert error_type == "context"

    def test_detects_memory_error_by_type_name(self):
        """Should detect memory errors by exception type name."""
        error = MemoryError("cannot allocate memory")
        is_recoverable, error_type = _is_memory_or_context_error(error)
        assert is_recoverable is True
        assert error_type == "memory"

    def test_returns_false_for_non_recoverable_errors(self):
        """Should return False for non-memory/context errors."""
        error = ValueError("Invalid input")
        is_recoverable, error_type = _is_memory_or_context_error(error)
        assert is_recoverable is False
        assert error_type == "unknown"

    def test_detects_mps_out_of_memory(self):
        """Should detect MPS out of memory errors."""
        error = RuntimeError("MPS out of memory")
        is_recoverable, error_type = _is_memory_or_context_error(error)
        assert is_recoverable is True
        assert error_type == "memory"

    def test_detects_token_limit_error(self):
        """Should detect token limit errors."""
        error = RuntimeError("token limit exceeded")
        is_recoverable, error_type = _is_memory_or_context_error(error)
        assert is_recoverable is True
        assert error_type == "context"


# ---------------------------------------------------------------------------
# Default fallback levels tests
# ---------------------------------------------------------------------------


class TestGetDefaultFallbackLevels:
    """Tests for _get_default_fallback_levels helper."""

    def test_returns_levels_capped_at_initial_tokens(self):
        """Should return levels capped at initial_max_tokens."""
        levels = _get_default_fallback_levels(4096)
        assert levels == [4096, 2048, 1024, 512]
        assert all(level <= 4096 for level in levels)

    def test_returns_all_levels_for_large_initial_tokens(self):
        """Should return all default levels for large initial_max_tokens."""
        levels = _get_default_fallback_levels(8192)
        assert levels == [8192, 4096, 2048, 1024, 512]

    def test_returns_single_level_for_small_initial_tokens(self):
        """Should return single level for very small initial_max_tokens."""
        levels = _get_default_fallback_levels(256)
        assert levels == [256]

    def test_returns_min_level_for_very_small_initial_tokens(self):
        """Should return min(initial, 512) for very small initial_max_tokens."""
        levels = _get_default_fallback_levels(100)
        assert levels == [100]


# ---------------------------------------------------------------------------
# VLMConfig fallback configuration tests
# ---------------------------------------------------------------------------


class TestVLMConfigFallbackFields:
    """Tests for VLMConfig fallback configuration fields."""

    def test_enable_token_fallback_defaults_to_true(self):
        """enable_token_fallback should default to True."""
        config = VLMConfig(model_name="test-model")
        assert config.enable_token_fallback is True

    def test_token_fallback_levels_defaults_to_none(self):
        """token_fallback_levels should default to None."""
        config = VLMConfig(model_name="test-model")
        assert config.token_fallback_levels is None

    def test_enable_token_fallback_can_be_set(self):
        """enable_token_fallback should be settable."""
        config = VLMConfig(model_name="test-model", enable_token_fallback=False)
        assert config.enable_token_fallback is False

    def test_token_fallback_levels_can_be_set(self):
        """token_fallback_levels should be settable."""
        config = VLMConfig(model_name="test-model", token_fallback_levels=[4096, 2048, 1024])
        assert config.token_fallback_levels == [4096, 2048, 1024]


class TestModelConfigurationFallbackFields:
    """Tests for ModelConfiguration fallback configuration fields."""

    def test_enable_token_fallback_defaults_to_true(self):
        """enable_token_fallback should default to True."""
        config = ModelConfiguration(model_name="test-model")
        assert config.enable_token_fallback is True

    def test_token_fallback_levels_defaults_to_none(self):
        """token_fallback_levels should default to None."""
        config = ModelConfiguration(model_name="test-model")
        assert config.token_fallback_levels is None

    def test_to_dict_includes_fallback_fields(self):
        """to_dict should include fallback fields."""
        config = ModelConfiguration(model_name="test-model", enable_token_fallback=False, token_fallback_levels=[2048, 1024])
        d = config.to_dict()
        assert d["enable_token_fallback"] is False
        assert d["token_fallback_levels"] == [2048, 1024]

    def test_from_dict_includes_fallback_fields(self):
        """from_dict should include fallback fields."""
        d = {"model_name": "test-model", "enable_token_fallback": False, "token_fallback_levels": [2048, 1024]}
        config = ModelConfiguration.from_dict(d)
        assert config.enable_token_fallback is False
        assert config.token_fallback_levels == [2048, 1024]


# ---------------------------------------------------------------------------
# process_with_fallback tests
# ---------------------------------------------------------------------------


class TestProcessWithFallback:
    """Tests for process_with_fallback public method."""

    def _make_processor_with_mock(self):
        """Create a VLMProcessor with mocked registry and model."""
        processor = VLMProcessor.__new__(VLMProcessor)
        processor.registry = MagicMock()
        processor.registry.is_model_loaded.return_value = True
        mock_loaded = MagicMock()
        mock_loaded.model_info = {"name": "test-model", "version": "1.0"}
        processor.registry.get_current_model.return_value = mock_loaded
        processor._current_model = MagicMock()
        processor._current_model.model_name = "test-model"
        return processor

    def test_calls_process_image_with_vlm_when_fallback_disabled(self):
        """Should call process_image_with_vlm directly when fallback disabled."""
        processor = self._make_processor_with_mock()
        config = ModelConfiguration(model_name="test-model", enable_token_fallback=False)

        with patch.object(processor, "process_image_with_vlm") as mock_process:
            mock_process.return_value = {"description": "test", "confidence_score": 0.9}
            result = processor.process_with_fallback("img.png", "describe", config)

        assert result["description"] == "test"
        mock_process.assert_called_once_with("img.png", "describe", config)

    def test_returns_result_on_success(self):
        """Should return result when processing succeeds."""
        processor = self._make_processor_with_mock()
        config = ModelConfiguration(model_name="test-model", enable_token_fallback=True)

        with patch.object(processor, "process_image_with_vlm") as mock_process:
            mock_process.return_value = {"description": "a cat", "confidence_score": 0.9}
            result = processor.process_with_fallback("img.png", "describe", config)

        assert result["description"] == "a cat"
        mock_process.assert_called_once()

    def test_retries_on_memory_error(self):
        """Should retry with smaller tokens on memory error."""
        processor = self._make_processor_with_mock()
        config = ModelConfiguration(model_name="test-model", enable_token_fallback=True, token_fallback_levels=[4096, 2048, 1024])

        call_count = [0]

        def mock_process(*args, **kwargs):
            call_count[0] += 1
            if call_count[0] == 1:
                raise VLMMemoryError("Out of memory", attempted_tokens=4096)
            return {"description": "success", "confidence_score": 0.9}

        with patch.object(processor, "process_image_with_vlm", side_effect=mock_process):
            result = processor.process_with_fallback("img.png", "describe", config)

        assert result["description"] == "success"
        assert call_count[0] == 2  # Initial call + 1 retry

    def test_retries_on_context_error(self):
        """Should retry with smaller tokens on context error."""
        processor = self._make_processor_with_mock()
        config = ModelConfiguration(model_name="test-model", enable_token_fallback=True, token_fallback_levels=[4096, 2048, 1024])

        call_count = [0]

        def mock_process(*args, **kwargs):
            call_count[0] += 1
            if call_count[0] == 1:
                raise VLMContextLengthError("Context exceeded", attempted_tokens=4096)
            return {"description": "success", "confidence_score": 0.9}

        with patch.object(processor, "process_image_with_vlm", side_effect=mock_process):
            result = processor.process_with_fallback("img.png", "describe", config)

        assert result["description"] == "success"
        assert call_count[0] == 2

    def test_raises_error_after_all_levels_exhausted(self):
        """Should raise VLMProcessingError after all levels exhausted."""
        processor = self._make_processor_with_mock()
        config = ModelConfiguration(model_name="test-model", enable_token_fallback=True, token_fallback_levels=[4096, 2048])

        def mock_process(*args, **kwargs):
            raise VLMMemoryError("Out of memory", attempted_tokens=4096)

        with patch.object(processor, "process_image_with_vlm", side_effect=mock_process):
            with pytest.raises(VLMProcessingError, match="failed at all token levels"):
                processor.process_with_fallback("img.png", "describe", config)

    def test_raises_non_recoverable_error_immediately(self):
        """Should raise non-recoverable errors immediately without retry."""
        processor = self._make_processor_with_mock()
        config = ModelConfiguration(model_name="test-model", enable_token_fallback=True, token_fallback_levels=[4096, 2048])

        call_count = [0]

        def mock_process(*args, **kwargs):
            call_count[0] += 1
            raise ValueError("Invalid input")

        with patch.object(processor, "process_image_with_vlm", side_effect=mock_process):
            with pytest.raises(ValueError, match="Invalid input"):
                processor.process_with_fallback("img.png", "describe", config)

        assert call_count[0] == 1  # No retries for non-recoverable errors

    def test_uses_default_levels_when_not_configured(self):
        """Should use default levels when token_fallback_levels is None."""
        processor = self._make_processor_with_mock()
        config = ModelConfiguration(model_name="test-model", enable_token_fallback=True, token_fallback_levels=None)

        with patch.object(processor, "process_image_with_vlm") as mock_process:
            mock_process.return_value = {"description": "success", "confidence_score": 0.9}
            result = processor.process_with_fallback("img.png", "describe", config, initial_max_tokens=4096)

        assert result["description"] == "success"
        mock_process.assert_called_once()


# ---------------------------------------------------------------------------
# Backward compatibility tests
# ---------------------------------------------------------------------------


class TestBackwardCompatibility:
    """Tests for backward compatibility with existing API."""

    def test_process_image_with_vlm_unchanged_signature(self):
        """process_image_with_vlm should maintain existing signature."""
        import inspect

        sig = inspect.signature(VLMProcessor.process_image_with_vlm)
        params = list(sig.parameters.keys())
        assert params == ["self", "image_path", "prompt", "config"]

    def test_process_image_with_vlm_no_fallback_by_default(self):
        """process_image_with_vlm should not use token fallback by default."""
        processor = VLMProcessor.__new__(VLMProcessor)
        processor.registry = MagicMock()
        processor.registry.is_model_loaded.return_value = True
        mock_loaded = MagicMock()
        mock_loaded.model_info = {"name": "test-model", "version": "1.0"}
        processor.registry.get_current_model.return_value = mock_loaded
        processor._current_model = MagicMock()
        processor._current_model.model_name = "test-model"

        ModelConfiguration(model_name="test-model")

        # Verify that process_image_with_vlm doesn't call process_with_fallback
        # by checking the implementation doesn't reference fallback logic
        import inspect

        source = inspect.getsource(VLMProcessor.process_image_with_vlm)
        assert "process_with_fallback" not in source
        assert "token_fallback" not in source.lower()

    def test_vlm_config_backward_compatible(self):
        """VLMConfig should work without new fallback fields."""
        # Old-style config creation should still work
        config = VLMConfig(model_name="test-model", timeout_seconds=60, timeout_behavior="error")
        assert config.model_name == "test-model"
        assert config.timeout_seconds == 60
        assert config.timeout_behavior == "error"
        # New fields should have defaults
        assert config.enable_token_fallback is True
        assert config.token_fallback_levels is None
