## Context

`VLMProcessor._process_with_timeout` currently uses `signal.SIGALRM` to enforce inference timeouts. SIGALRM has two critical limitations:

1. **Thread restriction**: Only works on the main thread; raises `ValueError` if called from a worker thread (e.g., batch processing via `ThreadPoolExecutor`).
2. **Native code bypass**: MLX and CoreML inference runs in C extensions that do not check Python signal state, so SIGALRM cannot interrupt a truly hung native call.

The reference implementation from `mlx-video-ocr` (`engines/ocr_engine.py`) demonstrates the correct pattern: spawn a `multiprocessing.Process` per inference call, join with a wall-clock timeout, then escalate terminate → kill if the process is still alive.

Current config surface (`VLMConfig.timeout_seconds`, `ModelConfiguration.timeout_seconds`) already exists and is wired through — only the enforcement mechanism needs to change.

## Goals / Non-Goals

**Goals:**
- Replace SIGALRM-based timeout with subprocess-isolated inference that enforces a true wall-clock timeout.
- Support graceful escalation: `terminate()` first, then `kill()` after a short grace period.
- Preserve all three existing `timeout_behavior` modes: `error`, `fallback`, `continue`.
- Keep public API signatures unchanged (`process_image_with_vlm`, `process_batch_with_vlm`).
- Work correctly when called from non-main threads (batch processing path).
- Stdlib-only implementation (`multiprocessing`, `queue`) — no new dependencies.

**Non-Goals:**
- Parallelising batch inference across multiple subprocesses (separate concern).
- Changing model loading or caching behaviour.
- Supporting Windows-specific process isolation quirks beyond what stdlib provides.

## Decisions

### D1: Subprocess per inference call (not thread-based)

**Decision**: Spawn a `multiprocessing.Process` for each `model.process_image()` call.

**Rationale**: Threads share the GIL and cannot interrupt native C-extension calls. A subprocess has its own memory space and can be forcibly killed regardless of what native code is executing. This is the only reliable way to enforce a wall-clock timeout on MLX/CoreML inference.

**Alternatives considered**:
- `concurrent.futures.ThreadPoolExecutor` with `Future.cancel()` — cannot cancel a running thread.
- `asyncio` with `asyncio.wait_for` — same limitation; async does not preempt synchronous native calls.
- Keep SIGALRM — fails in non-main threads and cannot interrupt native code.

### D2: `SubprocessTimeoutRunner` as a standalone utility class

**Decision**: Extract the subprocess logic into `SubprocessTimeoutRunner` in a new file `anyfile_to_ai/image_processor/subprocess_runner.py`.

**Rationale**: Keeps `vlm_processor.py` focused on orchestration. The runner is independently testable and reusable by other processors (e.g., audio) in the future.

**Alternatives considered**:
- Inline in `_process_with_timeout` — harder to unit-test the escalation logic in isolation.

### D3: `multiprocessing.Queue` for result/error passing

**Decision**: Use a `multiprocessing.Queue` to pass the result dict (or serialised exception) from the child process back to the parent.

**Rationale**: Queues are safe across process boundaries and handle arbitrary picklable objects. The child puts either `{"ok": result}` or `{"error": repr(exc)}` on the queue; the parent reads after `join()`.

**Alternatives considered**:
- `multiprocessing.Pipe` — lower-level, requires explicit send/recv and is harder to use safely with exceptions.
- Shared memory / `Value` — not suitable for variable-size dicts.

### D4: Terminate → kill escalation with 5-second grace period

**Decision**: After the primary timeout, call `process.terminate()` (SIGTERM), wait up to 5 seconds, then call `process.kill()` (SIGKILL) if still alive.

**Rationale**: Mirrors the reference implementation. SIGTERM allows the child to flush buffers; SIGKILL is the guaranteed backstop. 5 seconds is sufficient for MLX cleanup without blocking the caller excessively.

### D5: Model must be re-loaded in child process

**Decision**: The child process receives the image path, prompt, model name, and config — not a pre-loaded model object. It loads the model itself.

**Rationale**: MLX model objects are not picklable across process boundaries. The child must call `create_vlm_model` and `_ensure_model_loaded` independently. This adds per-call model load overhead; acceptable because the primary use case is single-image processing and the timeout scenario is already a degraded path.

**Trade-off**: For batch processing, each subprocess re-loads the model. This is a known cost. A future optimisation could use a persistent worker process pool, but that is out of scope.

## Risks / Trade-offs

- **Model reload overhead per call** → Acceptable for the timeout-protection use case; document in module README. Future: persistent worker pool.
- **Pickling failures for non-picklable config objects** → Mitigate by ensuring `ModelConfiguration` is a plain dataclass with picklable fields (already the case).
- **macOS `spawn` start method** → Python 3.11+ on macOS defaults to `spawn` (not `fork`), which requires the child entry-point to be importable at module level. The `_run_inference_in_process` function MUST be a module-level function, not a closure or lambda.
- **Queue deadlock on large results** → MLX inference results are text strings (not large binary blobs); queue buffer overflow is not a practical concern.
- **Zombie processes on rapid failures** → `process.join()` is always called (in the timeout branch too), preventing zombies.

## Migration Plan

1. Add `subprocess_runner.py` with `SubprocessTimeoutRunner` and the module-level `_run_inference_in_process` worker function.
2. Update `vlm_processor.py`: replace `_process_with_timeout` body to delegate to `SubprocessTimeoutRunner.run()`; remove `signal` import.
3. Update / add unit tests for the runner (mock `multiprocessing.Process`).
4. Update integration tests that assert on timeout behaviour.
5. No config changes, no CLI changes, no README changes beyond module-level notes.
6. **Rollback**: Revert `vlm_processor.py` and delete `subprocess_runner.py` — no database or schema migrations involved.

## Open Questions

- Should `SubprocessTimeoutRunner` be placed in a shared `anyfile_to_ai/utils/` package for reuse by `audio_processor`? (Deferred — keep in `image_processor` for now, move later if needed.)
- Is the 5-second kill grace period configurable? (Not for this change — hardcoded constant `KILL_GRACE_SECONDS = 5`.)
