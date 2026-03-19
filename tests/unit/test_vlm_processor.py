"""Unit tests for VLMProcessor._process_with_timeout (subprocess-based)."""

from __future__ import annotations

import sys
import threading
from unittest.mock import MagicMock, patch

import pytest

from anyfile_to_ai.image_processor.vlm_exceptions import VLMTimeoutError
from anyfile_to_ai.image_processor.vlm_models import ModelConfiguration
from anyfile_to_ai.image_processor.vlm_processor import VLMProcessor


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _get_vlm_processor_mod():
    """Return the current vlm_processor module from sys.modules.

    Using sys.modules avoids stale module references when other tests trigger
    re-imports of the image_processor package (e.g., via __init__ imports).
    """
    return sys.modules["anyfile_to_ai.image_processor.vlm_processor"]


def _make_config(**kwargs) -> ModelConfiguration:
    defaults = {"model_name": "test-model", "timeout_seconds": 30, "timeout_behavior": "error"}
    defaults.update(kwargs)
    return ModelConfiguration(**defaults)


def _make_processor_with_mock_model(mock_model=None):
    """Return a VLMProcessor with registry and current model mocked out."""
    processor = VLMProcessor.__new__(VLMProcessor)
    processor.registry = MagicMock()
    processor.registry.is_model_loaded.return_value = True
    mock_loaded = MagicMock()
    mock_loaded.model_info = {"name": "test-model", "version": "1.0"}
    processor.registry.get_current_model.return_value = mock_loaded
    processor._current_model = mock_model or MagicMock()
    processor._current_model.model_name = "test-model"
    return processor, mock_loaded


def _make_runner_mock(result=None, side_effect=None):
    """Return a (mock_cls, mock_instance) pair for SubprocessTimeoutRunner."""
    mock_runner = MagicMock()
    if side_effect is not None:
        mock_runner.run.side_effect = side_effect
    else:
        mock_runner.run.return_value = result
    mock_cls = MagicMock(return_value=mock_runner)
    return mock_cls, mock_runner


# ---------------------------------------------------------------------------
# _process_with_timeout tests
# ---------------------------------------------------------------------------


class TestProcessWithTimeout:
    """Tests for the subprocess-based _process_with_timeout method."""

    def test_returns_result_on_success(self):
        """_process_with_timeout returns result dict when runner succeeds."""
        expected = {"description": "a cat", "confidence_score": 0.9}
        processor, _ = _make_processor_with_mock_model()
        mock_cls, mock_runner = _make_runner_mock(result=expected)

        mod = _get_vlm_processor_mod()
        with patch.object(mod, "SubprocessTimeoutRunner", mock_cls):
            result = processor._process_with_timeout(processor._current_model, "img.png", "describe", 30)

        assert result == expected
        mock_runner.run.assert_called_once()

    def test_raises_vlm_timeout_error_on_timeout(self):
        """_process_with_timeout converts TimeoutError to VLMTimeoutError."""
        processor, _ = _make_processor_with_mock_model()
        mock_cls, _ = _make_runner_mock(side_effect=TimeoutError("timed out after 5 seconds"))

        mod = _get_vlm_processor_mod()
        with patch.object(mod, "SubprocessTimeoutRunner", mock_cls):
            with pytest.raises(VLMTimeoutError, match="timed out after 5 seconds"):
                processor._process_with_timeout(processor._current_model, "img.png", "describe", 5)

    def test_does_not_use_signal_module(self):
        """_process_with_timeout no longer imports or uses signal.SIGALRM."""
        import inspect

        source = inspect.getsource(VLMProcessor._process_with_timeout)
        assert "signal.alarm" not in source, "signal.alarm() should be removed"
        assert "signal.SIGALRM" not in source, "signal.SIGALRM should be removed"
        assert "import signal" not in source, "signal module should not be imported in method"

    def test_works_when_called_from_non_main_thread(self):
        """_process_with_timeout does not raise ValueError from non-main thread."""
        expected = {"description": "a bird", "confidence_score": 0.7}
        processor, _ = _make_processor_with_mock_model()
        mock_cls, _ = _make_runner_mock(result=expected)
        errors: list[Exception] = []
        results: list[dict] = []

        def run_in_thread():
            try:
                mod = _get_vlm_processor_mod()
                with patch.object(mod, "SubprocessTimeoutRunner", mock_cls):
                    result = processor._process_with_timeout(processor._current_model, "img.png", "describe", 30)
                    results.append(result)
            except Exception as exc:
                errors.append(exc)

        thread = threading.Thread(target=run_in_thread)
        thread.start()
        thread.join(timeout=5)

        assert not errors, f"Unexpected error in thread: {errors}"
        assert results == [expected]


# ---------------------------------------------------------------------------
# process_image_with_vlm timeout_behavior integration
# ---------------------------------------------------------------------------


class TestProcessImageTimeoutBehavior:
    """Tests that timeout_behavior modes are handled correctly."""

    def _patch_runner_timeout(self):
        """Return (context_manager, mock_runner) that makes runner raise TimeoutError."""
        mock_cls, mock_runner = _make_runner_mock(side_effect=TimeoutError("timed out"))
        mod = _get_vlm_processor_mod()
        return patch.object(mod, "SubprocessTimeoutRunner", mock_cls), mock_runner

    def test_timeout_behavior_error_raises(self):
        """timeout_behavior='error' raises VLMTimeoutError."""
        processor, _ = _make_processor_with_mock_model()
        config = _make_config(timeout_behavior="error", timeout_seconds=5)
        ctx, _ = self._patch_runner_timeout()

        with ctx:
            with pytest.raises(VLMTimeoutError):
                processor.process_image_with_vlm("img.png", "describe", config)

    def test_timeout_behavior_fallback_returns_dict(self):
        """timeout_behavior='fallback' returns a fallback result dict."""
        processor, _ = _make_processor_with_mock_model()
        config = _make_config(timeout_behavior="fallback", timeout_seconds=5)
        ctx, _ = self._patch_runner_timeout()

        with ctx:
            result = processor.process_image_with_vlm("img.png", "describe", config)

        assert "description" in result
        assert "fallback" in result["description"].lower()

    def test_timeout_behavior_continue_returns_dict(self):
        """timeout_behavior='continue' returns a partial result dict."""
        processor, _ = _make_processor_with_mock_model()
        config = _make_config(timeout_behavior="continue", timeout_seconds=5)
        ctx, _ = self._patch_runner_timeout()

        with ctx:
            result = processor.process_image_with_vlm("img.png", "describe", config)

        assert "description" in result
        assert "partial" in result["description"].lower() or "interrupted" in result["description"].lower()
