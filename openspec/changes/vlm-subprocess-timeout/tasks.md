## 1. Subprocess Runner Module

- [ ] 1.1 Create `anyfile_to_ai/image_processor/subprocess_runner.py` with module-level `_run_inference_in_process(image_path, prompt, model_name, config_dict, output_queue)` worker function
- [ ] 1.2 Implement `SubprocessTimeoutRunner` class with `run(image_path, prompt, model_name, config, timeout_seconds)` method that spawns a `multiprocessing.Process`, joins with timeout, and returns the result dict
- [ ] 1.3 Implement terminate → kill escalation in `SubprocessTimeoutRunner.run()`: call `process.terminate()`, join up to `KILL_GRACE_SECONDS = 5`, then call `process.kill()` if still alive
- [ ] 1.4 Ensure `_run_inference_in_process` loads the VLM model inside the child process (calls `create_vlm_model` + `_ensure_model_loaded`) and puts `{"ok": result}` or `{"error": repr(exc)}` on the queue

## 2. VLMProcessor Integration

- [ ] 2.1 Remove `import signal` from `vlm_processor.py` and replace `_process_with_timeout` body to delegate to `SubprocessTimeoutRunner.run()`
- [ ] 2.2 Map `SubprocessTimeoutRunner` result: on `{"ok": ...}` return the result dict; on `{"error": ...}` raise `VLMTimeoutError` or apply `timeout_behavior` fallback/continue logic as before
- [ ] 2.3 Verify `process_image_with_vlm` and `process_batch_with_vlm` public signatures are unchanged after the refactor

## 3. Unit Tests

- [ ] 3.1 Write unit tests for `SubprocessTimeoutRunner` using `unittest.mock.patch("multiprocessing.Process")` to simulate successful completion, timeout + SIGTERM exit, and timeout + SIGKILL escalation
- [ ] 3.2 Write unit tests for `_run_inference_in_process` worker: assert it puts `{"ok": result}` on success and `{"error": ...}` on exception
- [ ] 3.3 Update existing `_process_with_timeout` unit tests in `tests/unit/test_vlm_processor.py` to reflect the new subprocess-based implementation (remove SIGALRM-specific assertions)

## 4. Integration Tests

- [ ] 4.1 Add an integration test that calls `process_image_with_vlm` from a `threading.Thread` and asserts no `ValueError` or signal-related error is raised
- [ ] 4.2 Add an integration test (marked `@pytest.mark.slow`) that verifies `VLMTimeoutError` is raised when `timeout_seconds` is set to a very small value and a mock model hangs

## 5. Validation

- [ ] 5.1 Run `uv run ruff check anyfile_to_ai/image_processor/` and `uv run ruff format anyfile_to_ai/image_processor/` — fix any issues
- [ ] 5.2 Run `uv run pytest tests/unit/test_vlm_processor.py tests/unit/test_subprocess_runner.py` — all tests must pass
- [ ] 5.3 Run `./run_coverage.sh` — confirm overall coverage remains ≥ 80%
