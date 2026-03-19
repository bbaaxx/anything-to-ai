"""Unit tests for SubprocessTimeoutRunner and _run_inference_in_process."""

from __future__ import annotations

import multiprocessing
import queue
from unittest.mock import MagicMock, patch

import pytest

from anyfile_to_ai.image_processor.subprocess_runner import (
    KILL_GRACE_SECONDS,
    SubprocessTimeoutRunner,
    _run_inference_in_process,
)


# ---------------------------------------------------------------------------
# _run_inference_in_process worker tests
# ---------------------------------------------------------------------------


class TestRunInferenceInProcess:
    """Tests for the module-level worker function.

    We verify the queue protocol and picklability without calling
    ``_run_inference_in_process`` directly in the main process.  Calling it
    directly triggers ``importlib.import_module("anyfile_to_ai.image_processor.vlm_model_impl")``,
    which re-imports the ``anyfile_to_ai.image_processor`` package and causes
    ``subprocess_runner`` to be re-imported, creating a new
    ``_run_inference_in_process`` function object.  This breaks subsequent
    tests that rely on the function's identity for pickling.

    The queue protocol (``{"ok": result}`` / ``{"error": repr(exc)}``) is
    exercised end-to-end through ``TestSubprocessTimeoutRunner`` which mocks
    ``multiprocessing.Process`` and controls the queue payload directly.
    """

    def test_worker_function_is_module_level(self):
        """_run_inference_in_process is a module-level function (picklable)."""
        import pickle

        import anyfile_to_ai.image_processor.subprocess_runner as runner_mod

        # Should not raise — module-level functions are picklable.
        pickled = pickle.dumps(runner_mod._run_inference_in_process)
        restored = pickle.loads(pickled)
        assert restored is runner_mod._run_inference_in_process

    def test_worker_function_has_correct_signature(self):
        """_run_inference_in_process accepts the expected arguments."""
        import inspect

        sig = inspect.signature(_run_inference_in_process)
        params = list(sig.parameters.keys())
        assert params == ["image_path", "prompt", "model_name", "config_dict", "output_queue"]

    def test_worker_function_is_importable_by_name(self):
        """_run_inference_in_process can be looked up by module + name (spawn requirement)."""
        import sys

        # Use sys.modules to avoid triggering a re-import of subprocess_runner,
        # which would create a new _run_inference_in_process function object and
        # break subsequent tests that rely on function identity for pickling.
        mod = sys.modules.get("anyfile_to_ai.image_processor.subprocess_runner")
        assert mod is not None, "subprocess_runner should already be imported"
        assert hasattr(mod, "_run_inference_in_process")
        assert callable(mod._run_inference_in_process)


# ---------------------------------------------------------------------------
# SubprocessTimeoutRunner tests (mocked multiprocessing.Process)
# ---------------------------------------------------------------------------


class TestSubprocessTimeoutRunner:
    """Tests for SubprocessTimeoutRunner using mocked Process."""

    def _make_runner(self):
        return SubprocessTimeoutRunner()

    def _make_process_mock(self, *, alive_after_join=False, alive_after_terminate=False, exitcode=0, queue_payload=None):
        """Build a mock Process that simulates various lifecycle scenarios."""
        mock_process = MagicMock()
        mock_process.exitcode = exitcode

        # is_alive() returns True only when we want to simulate timeout
        if alive_after_join:
            # First call (after initial join) → alive; subsequent calls depend on terminate scenario
            if alive_after_terminate:
                mock_process.is_alive.side_effect = [True, True, False]
            else:
                mock_process.is_alive.side_effect = [True, False]
        else:
            mock_process.is_alive.return_value = False

        if queue_payload is not None:
            mock_queue = MagicMock()
            mock_queue.get_nowait.return_value = queue_payload
        else:
            mock_queue = MagicMock()
            mock_queue.get_nowait.side_effect = queue.Empty

        return mock_process, mock_queue

    def test_returns_result_on_success(self):
        """Runner returns result dict when subprocess completes within timeout."""
        expected = {"description": "a dog", "confidence_score": 0.8}
        mock_process, mock_queue = self._make_process_mock(queue_payload={"ok": expected})

        with (
            patch("anyfile_to_ai.image_processor.subprocess_runner.multiprocessing.Process", return_value=mock_process),
            patch("anyfile_to_ai.image_processor.subprocess_runner.multiprocessing.Queue", return_value=mock_queue),
        ):
            runner = self._make_runner()
            result = runner.run("img.png", "describe", "test-model", {}, timeout_seconds=30)

        assert result == expected
        mock_process.start.assert_called_once()
        mock_process.join.assert_called_once_with(timeout=30)
        mock_process.terminate.assert_not_called()
        mock_process.kill.assert_not_called()

    def test_raises_timeout_error_when_process_hangs(self):
        """Runner raises TimeoutError and calls terminate when process exceeds timeout."""
        mock_process, mock_queue = self._make_process_mock(alive_after_join=True, alive_after_terminate=False)

        with (
            patch("anyfile_to_ai.image_processor.subprocess_runner.multiprocessing.Process", return_value=mock_process),
            patch("anyfile_to_ai.image_processor.subprocess_runner.multiprocessing.Queue", return_value=mock_queue),
        ):
            runner = self._make_runner()
            with pytest.raises(TimeoutError, match="timed out after 5 seconds"):
                runner.run("img.png", "describe", "test-model", {}, timeout_seconds=5)

        mock_process.terminate.assert_called_once()
        mock_process.kill.assert_not_called()

    def test_escalates_to_kill_when_terminate_insufficient(self):
        """Runner calls kill() when process survives SIGTERM grace period."""
        mock_process, mock_queue = self._make_process_mock(alive_after_join=True, alive_after_terminate=True)

        with (
            patch("anyfile_to_ai.image_processor.subprocess_runner.multiprocessing.Process", return_value=mock_process),
            patch("anyfile_to_ai.image_processor.subprocess_runner.multiprocessing.Queue", return_value=mock_queue),
        ):
            runner = self._make_runner()
            with pytest.raises(TimeoutError):
                runner.run("img.png", "describe", "test-model", {}, timeout_seconds=5)

        mock_process.terminate.assert_called_once()
        mock_process.kill.assert_called_once()

    def test_terminate_join_uses_kill_grace_seconds(self):
        """Runner joins with KILL_GRACE_SECONDS after terminate."""
        mock_process, mock_queue = self._make_process_mock(alive_after_join=True, alive_after_terminate=False)

        join_calls = []

        def capture_join(**kwargs):
            join_calls.append(kwargs)

        mock_process.join.side_effect = capture_join

        with (
            patch("anyfile_to_ai.image_processor.subprocess_runner.multiprocessing.Process", return_value=mock_process),
            patch("anyfile_to_ai.image_processor.subprocess_runner.multiprocessing.Queue", return_value=mock_queue),
        ):
            runner = self._make_runner()
            with pytest.raises(TimeoutError):
                runner.run("img.png", "describe", "test-model", {}, timeout_seconds=5)

        # Second join call should use KILL_GRACE_SECONDS
        assert len(join_calls) >= 2
        assert join_calls[1].get("timeout") == KILL_GRACE_SECONDS

    def test_raises_runtime_error_on_subprocess_exception(self):
        """Runner raises RuntimeError when subprocess puts an error payload."""
        mock_process, mock_queue = self._make_process_mock(queue_payload={"error": "RuntimeError('boom')"})

        with (
            patch("anyfile_to_ai.image_processor.subprocess_runner.multiprocessing.Process", return_value=mock_process),
            patch("anyfile_to_ai.image_processor.subprocess_runner.multiprocessing.Queue", return_value=mock_queue),
        ):
            runner = self._make_runner()
            with pytest.raises(RuntimeError, match="boom"):
                runner.run("img.png", "describe", "test-model", {}, timeout_seconds=30)

    def test_raises_runtime_error_when_queue_empty(self):
        """Runner raises RuntimeError when process exits without putting result."""
        mock_process, mock_queue = self._make_process_mock(queue_payload=None)  # queue.Empty

        with (
            patch("anyfile_to_ai.image_processor.subprocess_runner.multiprocessing.Process", return_value=mock_process),
            patch("anyfile_to_ai.image_processor.subprocess_runner.multiprocessing.Queue", return_value=mock_queue),
        ):
            runner = self._make_runner()
            with pytest.raises(RuntimeError, match="exited without result"):
                runner.run("img.png", "describe", "test-model", {}, timeout_seconds=30)

    def test_process_started_with_daemon_true(self):
        """Runner spawns a daemon process to avoid zombie processes."""
        mock_process, mock_queue = self._make_process_mock(queue_payload={"ok": {"description": "x"}})

        with (
            patch("anyfile_to_ai.image_processor.subprocess_runner.multiprocessing.Process") as mock_process_cls,
            patch("anyfile_to_ai.image_processor.subprocess_runner.multiprocessing.Queue", return_value=mock_queue),
        ):
            mock_process_cls.return_value = mock_process
            runner = self._make_runner()
            runner.run("img.png", "describe", "test-model", {}, timeout_seconds=30)

        _, kwargs = mock_process_cls.call_args
        assert kwargs.get("daemon") is True
