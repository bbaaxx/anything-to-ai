## ADDED Requirements

### Requirement: Subprocess-isolated VLM inference with wall-clock timeout
The system SHALL execute VLM model inference inside a dedicated child process so that a configurable wall-clock timeout can be enforced regardless of whether the inference runs native C-extension code (e.g., MLX, CoreML) or is called from a non-main thread.

#### Scenario: Inference completes within timeout
- **WHEN** `VLMProcessor.process_image_with_vlm` is called and the model returns a result before `timeout_seconds` elapses
- **THEN** the result dict is returned to the caller with `description`, `confidence_score`, `processing_time`, and `model_info` populated

#### Scenario: Inference exceeds timeout with error behavior
- **WHEN** `VLMProcessor.process_image_with_vlm` is called, the child process does not complete within `timeout_seconds`, and `timeout_behavior` is `"error"`
- **THEN** a `VLMTimeoutError` is raised with `timeout_seconds` and `image_path` set

#### Scenario: Inference exceeds timeout with fallback behavior
- **WHEN** `VLMProcessor.process_image_with_vlm` is called, the child process does not complete within `timeout_seconds`, and `timeout_behavior` is `"fallback"`
- **THEN** a fallback result dict is returned (no exception raised)

#### Scenario: Inference exceeds timeout with continue behavior
- **WHEN** `VLMProcessor.process_image_with_vlm` is called, the child process does not complete within `timeout_seconds`, and `timeout_behavior` is `"continue"`
- **THEN** a partial/timeout result dict is returned (no exception raised)

### Requirement: Graceful subprocess termination escalation
The system SHALL attempt graceful termination of a timed-out child process before resorting to a forced kill.

#### Scenario: Child process terminates on SIGTERM
- **WHEN** a timeout occurs and `process.terminate()` is called
- **THEN** the child process exits within 5 seconds and `process.kill()` is NOT called

#### Scenario: Child process does not terminate on SIGTERM
- **WHEN** a timeout occurs, `process.terminate()` is called, and the child process is still alive after 5 seconds
- **THEN** `process.kill()` is called to forcibly terminate the child process

### Requirement: Subprocess runner works from non-main threads
The system SHALL enforce timeouts correctly when `process_image_with_vlm` is invoked from a non-main thread (e.g., during batch processing).

#### Scenario: Timeout enforced in worker thread
- **WHEN** `process_image_with_vlm` is called from a `threading.Thread` or `ThreadPoolExecutor` worker
- **THEN** the timeout is enforced without raising `ValueError` or any signal-related error

### Requirement: No new runtime dependencies
The subprocess timeout implementation SHALL use only Python standard library modules (`multiprocessing`, `queue`).

#### Scenario: No third-party packages required
- **WHEN** the image processor module is imported in an environment with only the declared project dependencies
- **THEN** no `ImportError` is raised for the subprocess timeout functionality
