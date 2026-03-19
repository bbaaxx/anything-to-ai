"""Subprocess-isolated runner for VLM inference with wall-clock timeout enforcement.

This module provides a subprocess-based execution wrapper that can enforce a true
wall-clock timeout on VLM inference calls, including native C-extension code (MLX,
CoreML) that cannot be interrupted by signal-based approaches (SIGALRM).

The worker function ``_run_inference_in_process`` MUST remain a module-level function
(not a closure or lambda) so that Python's ``spawn`` start method on macOS can
import and pickle it correctly.
"""

from __future__ import annotations

import multiprocessing
import queue
from typing import Any

# Grace period (seconds) between SIGTERM and SIGKILL during escalation.
KILL_GRACE_SECONDS = 5


def _run_inference_in_process(
    image_path: str,
    prompt: str,
    model_name: str,
    config_dict: dict[str, Any],
    output_queue: multiprocessing.Queue,
) -> None:
    """Worker function executed inside a child process.

    Loads the VLM model, runs inference, and puts the result (or error) on
    ``output_queue``.  Always puts exactly one item:
    - ``{"ok": result_dict}`` on success
    - ``{"error": repr(exc)}`` on any exception

    Args:
        image_path: Path to the image file to process.
        prompt: VLM prompt text.
        model_name: Name of the VLM model to load.
        config_dict: Serialised ``ModelConfiguration`` (from ``to_dict()``).
        output_queue: Queue used to return the result to the parent process.
    """
    try:
        # Import via importlib so the module object is looked up at call time.
        # This makes the function testable: patching the module attribute on
        # ``vlm_model_impl`` is visible here because we access it through the
        # module reference rather than a local ``from ... import`` binding.
        import importlib

        impl = importlib.import_module("anyfile_to_ai.image_processor.vlm_model_impl")
        vlm_model = impl.create_vlm_model(model_name)
        vlm_model._ensure_model_loaded()
        result = vlm_model.process_image(image_path, prompt)
        output_queue.put({"ok": result})
    except Exception as exc:
        output_queue.put({"error": repr(exc)})


class SubprocessTimeoutRunner:
    """Runs VLM inference in an isolated subprocess with a wall-clock timeout.

    Spawns a child process for each call, enforces ``timeout_seconds``, and
    escalates termination: SIGTERM first, then SIGKILL after ``KILL_GRACE_SECONDS``
    if the child is still alive.

    This approach works correctly:
    - From non-main threads (no SIGALRM restriction).
    - Against native C-extension code that ignores Python signal state.
    - On macOS, Linux, and Windows (no platform-specific signal APIs).
    """

    def run(
        self,
        image_path: str,
        prompt: str,
        model_name: str,
        config_dict: dict[str, Any],
        timeout_seconds: int,
    ) -> dict[str, Any]:
        """Run VLM inference in a subprocess with timeout enforcement.

        Args:
            image_path: Path to the image file to process.
            prompt: VLM prompt text.
            model_name: Name of the VLM model to load in the child process.
            config_dict: Serialised ``ModelConfiguration`` (from ``to_dict()``).
            timeout_seconds: Wall-clock timeout in seconds.

        Returns:
            Result dict from the VLM model (keys: ``description``, etc.).

        Raises:
            TimeoutError: If the child process does not complete within
                ``timeout_seconds``.
            RuntimeError: If the child process raises an exception during
                inference (message contains the original repr).
        """
        output_queue: multiprocessing.Queue = multiprocessing.Queue()

        # Look up the worker function from sys.modules at call time so that the
        # function identity always matches the current module state.  This
        # prevents ``PicklingError`` when other modules in the test suite
        # trigger a re-import of ``subprocess_runner`` (e.g., via
        # ``importlib.import_module`` or package-level ``__init__`` imports),
        # which would create a new function object at a different address.
        import sys as _sys

        _runner_mod = _sys.modules[__name__]
        _target = _runner_mod._run_inference_in_process

        process = multiprocessing.Process(
            target=_target,
            args=(image_path, prompt, model_name, config_dict, output_queue),
            daemon=True,
        )
        process.start()
        process.join(timeout=timeout_seconds)

        if process.is_alive():
            # Primary timeout exceeded — escalate: SIGTERM then SIGKILL.
            process.terminate()
            process.join(timeout=KILL_GRACE_SECONDS)
            if process.is_alive():
                process.kill()
                process.join()
            msg = f"VLM inference timed out after {timeout_seconds} seconds"
            raise TimeoutError(msg)

        # Process finished within timeout — retrieve result from queue.
        try:
            payload = output_queue.get_nowait()
        except queue.Empty:
            # Process exited without putting anything on the queue (e.g. killed
            # by OOM or external signal).
            msg = f"VLM subprocess exited without result (exit code: {process.exitcode})"
            raise RuntimeError(msg)

        if "error" in payload:
            msg = f"VLM inference failed in subprocess: {payload['error']}"
            raise RuntimeError(msg)

        return payload["ok"]
