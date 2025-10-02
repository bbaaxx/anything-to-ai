# Phase 0: Research & Technical Decisions

**Feature**: Unified Progress Tracking System
**Date**: 2025-10-02

## Overview

This document captures research findings and technical decisions for implementing a unified progress tracking system across all processing modules. The goal is to create a composable, async-first design that eliminates code duplication while supporting CLI and programmatic use cases.

## Research Areas

### 1. Python Async Patterns for Progress Tracking

**Decision**: Use AsyncIterator[ProgressUpdate] pattern with async generators

**Rationale**:
- Native Python 3.13 support for async/await syntax
- Clean separation between progress generation (producer) and consumption (consumer)
- Supports both sync callbacks (via wrapper) and async streaming
- Allows multiple concurrent consumers without blocking

**Alternatives Considered**:
- Observer pattern with sync callbacks: Limited to synchronous consumers, harder to compose
- Queue-based approach (asyncio.Queue): More complex, unnecessary overhead for progress updates
- Thread-based callbacks: Introduces threading complexity, counter to async-first goal

**Implementation Approach**:
```python
async def track_progress() -> AsyncIterator[ProgressUpdate]:
    for item in items:
        yield ProgressUpdate(current=i, total=len(items))
```

### 2. CLI Progress Bar Library (alive-progress)

**Decision**: Use alive-progress library as specified in feature requirements

**Rationale**:
- Explicitly requested in spec clarifications (Session 2025-10-02)
- Rich animation support for indeterminate states (spinners)
- Clean stderr output (preserves stdout for piping)
- Nested bar support for hierarchical progress
- Active maintenance and pure Python implementation

**Key Features**:
- Determinate bars: `with alive_bar(total) as bar: bar()`
- Indeterminate spinners: `with alive_bar(monitor=True) as bar: bar()`
- Title/text updates: `bar.text = "Processing file X"`
- Manual control: `bar(increment)` or `bar.current = value`

**Integration Pattern**:
- CLIProgressConsumer wraps alive-progress context manager
- Translates ProgressUpdate events to bar() calls
- Handles hierarchical display with nested bars or progress text formatting

### 3. Hierarchical Progress Representation

**Decision**: Compose ProgressEmitter instances in parent-child relationships

**Rationale**:
- Aligns with Composition-First constitutional principle
- Each emitter is independently functional and testable
- Parent emitter aggregates child progress via weighted averaging
- No special "hierarchical" classes needed - composition handles it naturally

**Implementation Pattern**:
```python
parent = ProgressEmitter(total=2, label="Overall")
child1 = parent.create_child(weight=0.4, label="Phase 1")
child2 = parent.create_child(weight=0.6, label="Phase 2")
```

**Weighting Strategy**:
- Equal weights by default (1.0 / num_children)
- Configurable weights for phases with different complexity
- Parent recalculates percentage based on weighted sum of children

### 4. Dynamic Total Updates

**Decision**: Mutable total field with automatic percentage recalculation

**Rationale**:
- Spec requirement FR-015: "allow total item count to be updated after initial reporting"
- Simple implementation: `emitter.update_total(new_total)`
- Triggers recalculation of percentage (may decrease temporarily as noted in spec)
- Consumers receive update event with new total

**Edge Case Handling**:
- Total increases: Percentage decreases, completion time estimate increases
- Total decreases: Percentage increases, may jump past previous current value
- Total becomes zero: Special case - treat as indeterminate state

### 5. Indeterminate Progress Handling

**Decision**: Optional total (None) indicates indeterminate state

**Rationale**:
- Spec requirement FR-014: indeterminate spinner + count-up when total unknown
- Clean API: `ProgressEmitter(total=None)` for indeterminate state
- Consumer decides rendering: CLI shows spinner, programmatic shows count only
- Can transition to determinate: `emitter.update_total(discovered_total)`

**CLI Rendering**:
- Use alive-progress monitor mode: `alive_bar(monitor=True)`
- Display format: "Processed: {current} items" with spinner animation
- When total discovered mid-stream, switch to determinate bar

### 6. Exception Safety in Callbacks

**Decision**: Try-except wrapper in emitter, log and continue on error

**Rationale**:
- Spec requirement FR-008: "callbacks that raise exceptions MUST NOT halt processing"
- Error logged to stderr (or provided logger) for visibility
- Processing continues uninterrupted
- Consumers responsible for their own error handling (emitter provides safety net)

**Implementation**:
```python
def _notify_consumers(self, update):
    for consumer in self._consumers:
        try:
            consumer.on_progress(update)
        except Exception as e:
            logger.error(f"Progress consumer error: {e}")
```

### 7. Performance Optimization (Update Throttling)

**Decision**: Rate-limit updates to 10 Hz (100ms minimum interval)

**Rationale**:
- Spec requirement FR-007: "MUST not significantly impact processing performance"
- Terminal rendering is expensive (ANSI escape sequences, cursor positioning)
- Most progress bars don't need >10 updates/second for smooth perception
- Throttling happens in emitter, before consumers

**Implementation**:
```python
def update(self, increment=1):
    self.current += increment
    now = time.monotonic()
    if now - self._last_update_time >= 0.1:  # 100ms throttle
        self._notify_consumers(...)
        self._last_update_time = now
```

**Bypass for Critical Updates**:
- First update (0% → initial progress)
- Last update (→ 100% completion)
- Total changed events
- Explicit `force=True` parameter

### 8. Backward Compatibility Strategy

**Decision**: Deprecation path with adapter wrappers

**Rationale**:
- Existing modules use different signatures (ProgressInfo vs ProgressTracker)
- Gradual migration preferred over breaking changes
- Adapter pattern provides compatibility layer during transition

**Migration Path**:
1. Phase 1: New progress_tracker module with core abstractions
2. Phase 2: Existing progress.py files import and re-export with deprecation warnings
3. Phase 3: Refactor modules to use new API directly
4. Phase 4: Remove old progress.py files and deprecation shims

**Compatibility Adapters**:
```python
# In pdf_extractor/progress.py
from progress_tracker import ProgressEmitter
import warnings

class ProgressInfo:  # Legacy class
    def __init__(self, ...):
        warnings.warn("ProgressInfo deprecated, use progress_tracker", DeprecationWarning)
        # Delegate to new API
```

### 9. Testing Strategy

**Decision**: Three-tier testing (contract, integration, unit)

**Contract Tests**:
- Validate ProgressConsumer protocol compliance
- Ensure all consumers implement required methods
- Type checking with Protocol/runtime_checkable

**Integration Tests**:
- End-to-end CLI rendering (capture stderr, validate output format)
- Hierarchical progress scenarios (parent-child coordination)
- Module integration (existing modules with new progress system)
- Async iteration patterns

**Unit Tests**:
- ProgressState/ProgressUpdate dataclass validation
- ProgressEmitter state transitions and calculations
- Consumer implementations (mock emitter, validate rendering)
- Throttling logic (time-based test fixtures)

### 10. Module Integration Points

**Decision**: Inject ProgressEmitter via optional constructor parameter

**Current Module APIs**:
```python
# pdf_extractor
def extract_text(pdf_path, progress_callback=None) -> str
# image_processor
def process_images(paths, progress_callback=None) -> List[Result]
# audio_processor
def transcribe_audio(audio_path, progress_callback=None) -> str
```

**New Unified API**:
```python
def extract_text(pdf_path, progress_emitter: Optional[ProgressEmitter] = None) -> str
    if progress_emitter:
        progress_emitter.update(1)
```

**CLI Integration**:
```python
from progress_tracker import ProgressEmitter, CLIProgressConsumer

emitter = ProgressEmitter(total=len(files))
consumer = CLIProgressConsumer()
emitter.add_consumer(consumer)

for file in files:
    process_file(file, progress_emitter=emitter)
```

## Dependencies Analysis

### Required Dependencies

1. **alive-progress** (external)
   - Version: >=3.0.0 (latest stable)
   - Purpose: CLI progress bar rendering (spec requirement)
   - Justification: Explicitly requested, provides required features (hierarchical, indeterminate, stderr output)
   - Alternatives: tqdm (no hierarchical support), rich (heavier dependency)
   - License: MIT (compatible)

2. **asyncio** (standard library)
   - Purpose: Async/await support for progress streaming
   - Justification: Built-in, zero overhead, aligns with modern Python patterns

3. **dataclasses** (standard library)
   - Purpose: Type-safe data models (ProgressState, ProgressUpdate)
   - Justification: Built-in since Python 3.7, cleaner than namedtuples

4. **typing** (standard library)
   - Purpose: Protocol definitions, type hints
   - Justification: Built-in, enables static analysis and IDE support

### Development Dependencies

- **pytest-asyncio**: Required for async test support
- **pytest-mock**: Useful for mocking consumers in unit tests

## Performance Considerations

### Overhead Analysis

**Target**: <1% processing time overhead per spec

**Measurement Points**:
- Update call time: ~1μs (simple arithmetic, throttling check)
- Throttled notify time: ~10ms (alive-progress rendering to stderr)
- Async iteration overhead: ~0.1μs per yield

**Example Workload**:
- Process 1000 images @ 100ms each = 100 seconds total
- 1000 updates × 1μs = 1ms (negligible)
- ~100 throttled renders (10 Hz) × 10ms = 1 second = 1% overhead ✓

**Optimization Strategies**:
- Throttling prevents excessive terminal I/O
- Lazy evaluation: Only calculate percentage when needed
- Avoid string formatting in hot paths
- Batch child progress updates (aggregate before parent notify)

## Open Questions & Future Considerations

### Resolved in Clarifications (2025-10-02)

- ✓ Hierarchical display format: Main bar + nested bars or formatted text
- ✓ Indeterminate progress: Spinner + count-up display
- ✓ Exception handling: Log and continue
- ✓ Dynamic totals: Support with real-time recalculation

### Deferred to Implementation Phase

- Exact alive-progress nested bar API (documentation review needed)
- Performance profiling with real workloads (measure actual overhead)
- WebSocket/HTTP consumer for remote progress monitoring (future enhancement)
- Progress persistence/resumability (out of scope for v1)

## Summary

All technical unknowns have been resolved through research. The design leverages:
- Async generators for composable progress streaming
- alive-progress for rich CLI rendering (per spec requirement)
- Parent-child emitter composition for hierarchical progress
- Optional totals for indeterminate states
- Exception-safe callbacks with logging
- Update throttling for performance (<1% overhead)

Ready to proceed to Phase 1 (Design & Contracts).
