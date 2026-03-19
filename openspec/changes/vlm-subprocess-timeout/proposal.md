## Why

VLM inference via `_process_with_timeout` currently uses `signal.SIGALRM` for timeout enforcement, which only works on Unix main threads and cannot interrupt native C-extension calls (e.g., MLX/CoreML model inference). This means a hung VLM call under memory pressure or on a problematic image can block the process indefinitely, making the image processor unreliable in production and batch workflows.

## What Changes

- Replace the `signal.SIGALRM`-based `_process_with_timeout` in `VLMProcessor` with a subprocess-isolated execution path that spawns a child process per VLM inference call.
- Add a `SubprocessTimeoutRunner` utility that wraps any callable in a `multiprocessing.Process`, enforces a configurable wall-clock timeout, and performs graceful terminate → kill escalation.
- Expose a `timeout_seconds` config knob (already present in `VLMConfig` / `ModelConfiguration`) that is forwarded to the new runner.
- Preserve all existing timeout behaviors (`error`, `fallback`, `continue`) — only the enforcement mechanism changes.
- No changes to public API signatures (`process_image_with_vlm`, `process_batch_with_vlm`).

## Capabilities

### New Capabilities

- `vlm-subprocess-timeout`: Subprocess-isolated VLM inference with configurable wall-clock timeout, graceful terminate/kill escalation, and cross-platform reliability (no SIGALRM dependency).

### Modified Capabilities

<!-- No existing spec-level requirements are changing; this is a new capability. -->

## Impact

- **Modified file**: `anyfile_to_ai/image_processor/vlm_processor.py` — `_process_with_timeout` replaced; new `SubprocessTimeoutRunner` added (same file or extracted to `anyfile_to_ai/image_processor/subprocess_runner.py`).
- **Config**: `VLMConfig.timeout_seconds` and `ModelConfiguration.timeout_seconds` already exist — no schema changes needed.
- **Dependencies**: `multiprocessing` (stdlib only — no new packages).
- **Tests**: Existing timeout unit/integration tests must be updated; new tests for subprocess escalation path required.
- **Platform**: Removes Unix-only `signal.SIGALRM` constraint; subprocess approach works on macOS, Linux, and Windows.
