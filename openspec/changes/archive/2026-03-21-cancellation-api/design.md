## Context

The current system processes files (PDFs, images, audio) through streaming operations that can run for extended periods. Users have no way to cancel these operations once started, forcing them to kill the entire process. This wastes resources (API credits, memory, temporary files) and creates poor UX for interactive applications.

The progress_tracker module already provides event-based progress updates via `ProgressConsumer` protocol. Cancellation should integrate naturally with this existing infrastructure.

**Stakeholders:**
- CLI users running long extractions
- Programmatic API users embedding the library
- Downstream services consuming streaming outputs

## Goals / Non-Goals

**Goals:**
- Provide a `CancellationToken` class for cooperative cancellation
- Integrate cancellation into all streaming operations (PDF, image, audio, document)
- Ensure proper resource cleanup on cancellation
- Support both synchronous and asynchronous cancellation patterns
- Maintain backward compatibility (cancellation is opt-in)

**Non-Goals:**
- Hard cancellation (thread interruption) - only cooperative cancellation
- Distributed cancellation across processes/machines
- Cancellation persistence or recovery
- Timeout-based auto-cancellation (separate feature)

## Decisions

### D1: CancellationToken as a simple mutable class

**Decision:** Use a simple class with a mutable `_cancelled` flag rather than threading.Event or asyncio.Event.

**Rationale:**
- Works identically in sync and async contexts
- No threading/asyncio dependency overhead
- Easy to test and reason about
- Can be wrapped for async-specific use cases if needed

**Alternatives considered:**
- `threading.Event` - Requires threading, doesn't work well with asyncio
- `asyncio.Event` - Async-only, doesn't work in sync contexts
- Callback-based cancellation - More complex, harder to compose

### D2: OperationCancelledError as a custom exception

**Decision:** Create a dedicated `OperationCancelledError` inheriting from `Exception` (not `BaseException`).

**Rationale:**
- Clear semantic meaning for callers
- Doesn't interfere with `KeyboardInterrupt` or `SystemExit`
- Can be caught specifically without catching all exceptions
- Allows clean error messages indicating cancellation source

### D3: Opt-in cancellation via optional parameter

**Decision:** Add `cancel_token: CancellationToken | None = None` parameter to streaming functions.

**Rationale:**
- Backward compatible - existing code works unchanged
- Explicit opt-in makes cancellation intent clear
- Type-safe with proper annotations
- Easy to add to existing function signatures

### D4: Check cancellation at iteration boundaries

**Decision:** Check `cancel_token.is_cancelled` at the start of each iteration/yield in streaming operations.

**Rationale:**
- Predictable cancellation points
- Minimal overhead (single boolean check)
- Natural integration with existing loop structures
- Immediate response without complex state management

## Risks / Trade-offs

| Risk | Mitigation |
|------|------------|
| Cancellation check overhead | Negligible - single boolean property access per iteration |
| Resource leaks on cancellation | Document cleanup responsibilities; provide context manager helpers |
| Partial results on cancellation | Yield partial results before raising; document behavior |
| Thread safety of CancellationToken | Document that token should be shared via reference, not copied |

## Open Questions

1. **Should cancelled operations yield partial results?** 
   - Current design: Yes, yield completed iterations before raising
   - Alternative: Raise immediately, discard partial results
   - Recommendation: Yield partials for now, add config later if needed

2. **Should we provide a cancellation timeout?**
   - Out of scope for initial implementation
   - Could be added as `CancellationToken(timeout=...)` later