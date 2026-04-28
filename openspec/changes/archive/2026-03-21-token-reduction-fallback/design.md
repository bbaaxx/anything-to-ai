## Context

The `VLMProcessor` class in `anyfile_to_ai/image_processor/vlm_processor.py` currently handles image processing with timeout-based fallback mechanisms but lacks automatic recovery from memory or context length errors during VLM inference. When processing large images or complex documents, the MLX-based VLM models can fail with out-of-memory errors or context length exceeded errors, causing complete processing failure.

**Current State:**
- `VLMProcessor.process_image_with_vlm()` delegates to `_process_with_timeout()` which isolates execution in a subprocess
- Timeout handling provides configurable behavior (error, fallback, continue)
- No retry mechanism for resource-related failures
- Users have no way to recover from transient memory/context failures automatically

**Constraints:**
- Must integrate with existing `ModelConfiguration` and `VLMConfig`
- Must preserve backward compatibility with existing timeout behavior
- Must not add new external dependencies

## Goals / Non-Goals

**Goals:**
- Implement progressive token reduction fallback for memory/context failures
- Add granular exception types for different failure modes
- Provide configuration options to control fallback behavior
- Maintain zero breaking changes to existing API

**Non-Goals:**
- Changing existing timeout handling logic
- Adding new VLM model types
- Modifying subprocess isolation architecture
- Implementing retry for network/IO errors (out of scope)

## Decisions

### D1: Token Reduction Strategy

**Decision**: Progressive reduction with configurable levels (default: 8192→ 4096→2048→1024→512).

**Rationale**: 
- Graceful degradation: smaller outputs are better than complete failure
- User-controlled: configurable via `token_fallback_levels`
- Predictable: fixed levels avoid arbitrary heuristics

**Alternatives Considered:**
1. Binary retry with same tokens - rejected: doesn't address root cause (resource limits)
2. Adaptive reduction based on error type - rejected: adds complexity without clear benefit
3. User-specified single fallback value - rejected: less flexible, harder to tune

### D2: Exception Hierarchy

**Decision**: Add `VLMMemoryError` and `VLMContextLengthError` as subclasses of `VLMProcessingError`.

**Rationale**:
- Enables selective catching by error type
- Aligns with existing exception hierarchy pattern
- Allows future extensions for other failure modes

### D3: Configuration Integration

**Decision**: Add `enable_token_fallback: bool = True` and `token_fallback_levels: list[int] | None` to `VLMConfig`.

**Rationale**:
- Consistent with existing `VLMConfig` pattern
- Sensible defaults enable feature without configuration
- Explicit levels allow power-user tuning

### D4: Method Placement

**Decision**: Add `process_with_fallback()` method to `VLMProcessor`, keep `process_image_with_vlm()` unchanged.

**Rationale**:
- Preserves existing API contract
- Opt-in: existing callers get current behavior
- Clear naming indicates enhanced functionality

## Risks / Trade-offs

| Risk | Mitigation |
|------|------------|
| Reduced output quality with smaller tokens | Document trade-off; user can disable fallback |
| Fallback adds latency on failure | Only activates on error; success path unchanged |
| False positive memory errors | Exception detection based on error patterns; tests cover edge cases |
| Breaking existing error handling | New exceptions inherit from `VLMProcessingError`; catches still work |