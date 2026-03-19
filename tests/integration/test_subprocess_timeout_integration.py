"""Integration tests for subprocess-based VLM timeout enforcement.

These tests verify that:
- Timeout is enforced correctly when called from a non-main thread.
- VLMTimeoutError is raised when a mock model hangs beyond timeout_seconds.

Tests that require a real model are marked ``@pytest.mark.slow`` and will be
skipped automatically in fast test runs.
"""

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


def _make_processor() -> VLMProcessor:
    """Return a VLMProcessor with registry mocked (no real model needed)."""
    processor = VLMProcessor.__new__(VLMProcessor)
    processor.registry = MagicMock()
    processor.registry.is_model_loaded.return_value = True
    mock_loaded = MagicMock()
    mock_loaded.model_info = {"name": "test-model", "version": "1.0"}
    processor.registry.get_current_model.return_value = mock_loaded
    processor._current_model = MagicMock()
    processor._current_model.model_name = "test-model"
    return processor


def _make_config(**kwargs) -> ModelConfiguration:
    defaults = {"model_name": "test-model", "timeout_seconds": 5, "timeout_behavior": "error"}
    defaults.update(kwargs)
    return ModelConfiguration(**defaults)


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
# Task 4.1: Timeout enforced from non-main thread
# ---------------------------------------------------------------------------


class TestTimeoutFromNonMainThread:
    """Verify timeout works correctly when called from a worker thread."""

    def test_success_from_worker_thread(self):
        """process_image_with_vlm succeeds when called from a non-main thread."""
        expected = {"description": "a tree", "confidence_score": 0.85, "processing_time": 0.1, "model_info": {}}
        processor = _make_processor()
        config = _make_config(timeout_seconds=30)
        errors: list[Exception] = []
        results: list[dict] = []

        def run_in_thread():
            try:
                mock_cls, _ = _make_runner_mock(result=expected)
                mod = _get_vlm_processor_mod()
                with patch.object(mod, "SubprocessTimeoutRunner", mock_cls):
                    result = processor.process_image_with_vlm("img.png", "describe", config)
                    results.append(result)
            except Exception as exc:
                errors.append(exc)

        thread = threading.Thread(target=run_in_thread)
        thread.start()
        thread.join(timeout=10)

        assert not thread.is_alive(), "Thread did not complete in time"
        assert not errors, f"Unexpected error in thread: {errors[0]!r}"
        # VLMProcessor enriches the result with processing_time and model_info;
        # assert on the fields we care about rather than exact equality.
        assert results[0]["description"] == expected["description"]
        assert results[0]["confidence_score"] == expected["confidence_score"]

    def test_no_value_error_from_signal_in_thread(self):
        """No ValueError (SIGALRM restriction) is raised from a worker thread."""
        processor = _make_processor()
        config = _make_config(timeout_seconds=5)
        errors: list[Exception] = []

        def run_in_thread():
            try:
                mock_cls, _ = _make_runner_mock(result={"description": "ok", "confidence_score": 1.0})
                mod = _get_vlm_processor_mod()
                with patch.object(mod, "SubprocessTimeoutRunner", mock_cls):
                    processor.process_image_with_vlm("img.png", "describe", config)
            except ValueError as exc:
                errors.append(exc)
            except Exception:
                pass  # Other exceptions are not what we're testing here

        thread = threading.Thread(target=run_in_thread)
        thread.start()
        thread.join(timeout=10)

        assert not errors, f"ValueError raised in thread (SIGALRM regression): {errors[0]!r}"


# ---------------------------------------------------------------------------
# Task 4.2: VLMTimeoutError raised when mock model hangs
# ---------------------------------------------------------------------------


class TestTimeoutRaisedOnHangingModel:
    """Verify VLMTimeoutError is raised when the subprocess runner times out."""

    @pytest.mark.slow
    def test_vlm_timeout_error_raised_on_hang(self):
        """VLMTimeoutError is raised when SubprocessTimeoutRunner times out."""
        processor = _make_processor()
        config = _make_config(timeout_seconds=1, timeout_behavior="error")
        mock_cls, _ = _make_runner_mock(side_effect=TimeoutError("timed out after 1 seconds"))

        mod = _get_vlm_processor_mod()
        with patch.object(mod, "SubprocessTimeoutRunner", mock_cls):
            with pytest.raises(VLMTimeoutError) as exc_info:
                processor.process_image_with_vlm("img.png", "describe", config)

        assert "timed out" in str(exc_info.value).lower()

    @pytest.mark.slow
    def test_timeout_fallback_returns_result_on_hang(self):
        """timeout_behavior='fallback' returns a result dict even when model hangs."""
        processor = _make_processor()
        config = _make_config(timeout_seconds=1, timeout_behavior="fallback")
        mock_cls, _ = _make_runner_mock(side_effect=TimeoutError("timed out after 1 seconds"))

        mod = _get_vlm_processor_mod()
        with patch.object(mod, "SubprocessTimeoutRunner", mock_cls):
            result = processor.process_image_with_vlm("img.png", "describe", config)

        assert isinstance(result, dict)
        assert "description" in result

    @pytest.mark.slow
    def test_timeout_continue_returns_result_on_hang(self):
        """timeout_behavior='continue' returns a partial result dict when model hangs."""
        processor = _make_processor()
        config = _make_config(timeout_seconds=1, timeout_behavior="continue")
        mock_cls, _ = _make_runner_mock(side_effect=TimeoutError("timed out after 1 seconds"))

        mod = _get_vlm_processor_mod()
        with patch.object(mod, "SubprocessTimeoutRunner", mock_cls):
            result = processor.process_image_with_vlm("img.png", "describe", config)

        assert isinstance(result, dict)
        assert "description" in result
