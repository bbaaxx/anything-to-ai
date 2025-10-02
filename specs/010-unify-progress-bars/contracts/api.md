# Progress Tracker Module API Contract

**Module**: `progress_tracker`
**Version**: 1.0.0
**Date**: 2025-10-02

## Public API

### Exports

```python
from progress_tracker import (
    # Core types
    ProgressState,
    ProgressUpdate,
    UpdateType,

    # Producer
    ProgressEmitter,

    # Consumer protocol
    ProgressConsumer,

    # Consumer implementations
    CLIProgressConsumer,
    CallbackProgressConsumer,
    LoggingProgressConsumer,
)
```

## Type Definitions

### ProgressState (Immutable Dataclass)

```python
@dataclass(frozen=True)
class ProgressState:
    """Immutable snapshot of progress state."""

    current: int
    total: Optional[int]
    label: Optional[str] = None
    timestamp: float = field(default_factory=time.monotonic)
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def percentage(self) -> Optional[float]:
        """Completion percentage (0.0-100.0), None if indeterminate."""
        ...

    @property
    def is_complete(self) -> bool:
        """True if current == total."""
        ...

    @property
    def is_indeterminate(self) -> bool:
        """True if total is None."""
        ...

    @property
    def items_remaining(self) -> Optional[int]:
        """Items left to process, None if indeterminate."""
        ...
```

**Validation**:
- `current >= 0`
- `total >= current` (if total is not None)
- `label` max 100 characters if provided

### UpdateType (Enum)

```python
class UpdateType(Enum):
    """Progress update event types."""

    STARTED = "started"          # Initial progress (current=0)
    PROGRESS = "progress"        # Regular incremental update
    TOTAL_CHANGED = "total_changed"  # Total count modified
    COMPLETED = "completed"      # Reached 100%
    ERROR = "error"              # Error encountered
```

### ProgressUpdate (Immutable Dataclass)

```python
@dataclass(frozen=True)
class ProgressUpdate:
    """Progress update event payload."""

    state: ProgressState
    delta: int
    update_type: UpdateType
```

## ProgressEmitter API

```python
class ProgressEmitter:
    """Mutable progress state manager."""

    def __init__(
        self,
        total: Optional[int],
        label: Optional[str] = None,
        throttle_interval: float = 0.1
    ) -> None:
        """
        Create progress emitter.

        Args:
            total: Total items to process (None for indeterminate)
            label: Human-readable label
            throttle_interval: Min seconds between updates (default 0.1 = 10 Hz)

        Raises:
            ValueError: If total < 0
        """
        ...

    def update(self, increment: int = 1, *, force: bool = False) -> None:
        """
        Increment progress counter.

        Args:
            increment: Items to add (default 1)
            force: Skip throttling if True (default False)

        Raises:
            ValueError: If update would make current > total
        """
        ...

    def set_current(self, value: int, *, force: bool = False) -> None:
        """
        Set absolute progress value.

        Args:
            value: New current value
            force: Skip throttling if True

        Raises:
            ValueError: If value < 0 or value > total
        """
        ...

    def update_total(self, new_total: Optional[int]) -> None:
        """
        Update total count (dynamic discovery).
        Always forces notification regardless of throttling.

        Args:
            new_total: New total value (None for indeterminate)

        Raises:
            ValueError: If new_total < current (cannot decrease below current)
        """
        ...

    def complete(self) -> None:
        """
        Mark progress as complete (sets current=total).
        Always forces notification.

        Raises:
            ValueError: If total is None (cannot complete indeterminate progress)
        """
        ...

    def add_consumer(self, consumer: ProgressConsumer) -> None:
        """Register consumer to receive updates."""
        ...

    def remove_consumer(self, consumer: ProgressConsumer) -> None:
        """Unregister consumer."""
        ...

    def create_child(
        self,
        total: Optional[int],
        weight: float = 1.0,
        label: Optional[str] = None
    ) -> "ProgressEmitter":
        """
        Create child emitter for hierarchical progress.

        Args:
            total: Child's total items
            weight: Relative weight for parent calculation (default 1.0)
            label: Child's label

        Returns:
            Child emitter (updates propagate to parent)

        Raises:
            ValueError: If weight <= 0
        """
        ...

    async def stream(self) -> AsyncIterator[ProgressUpdate]:
        """
        Async generator yielding progress updates.

        Yields:
            ProgressUpdate events as they occur

        Example:
            async for update in emitter.stream():
                print(f"{update.state.percentage:.1f}%")
        """
        ...

    @property
    def current(self) -> int:
        """Current progress value (read-only)."""
        ...

    @property
    def total(self) -> Optional[int]:
        """Total items (read-only)."""
        ...

    @property
    def state(self) -> ProgressState:
        """Current state snapshot."""
        ...
```

## ProgressConsumer Protocol

```python
from typing import Protocol

class ProgressConsumer(Protocol):
    """Interface for progress update handlers."""

    def on_progress(self, update: ProgressUpdate) -> None:
        """
        Handle progress update event.

        Args:
            update: Progress update with state and metadata

        Notes:
            - MUST NOT raise exceptions (emitter wraps in try-except but handle internally)
            - MUST NOT block for extended periods
            - Called from emitter's thread/context
        """
        ...

    def on_complete(self, state: ProgressState) -> None:
        """
        Handle completion event (optional).

        Args:
            state: Final progress state

        Notes:
            - Called once when progress reaches 100%
            - Default implementation is no-op
        """
        ...
```

## Consumer Implementations

### CLIProgressConsumer

```python
class CLIProgressConsumer:
    """Renders progress to stderr using alive-progress."""

    def __init__(
        self,
        show_percentage: bool = True,
        show_count: bool = True,
        title: Optional[str] = None
    ) -> None:
        """
        Create CLI progress consumer.

        Args:
            show_percentage: Display percentage (default True)
            show_count: Display "X/Y items" (default True)
            title: Override progress label with fixed title
        """
        ...

    def on_progress(self, update: ProgressUpdate) -> None:
        """Render update to stderr."""
        ...

    def on_complete(self, state: ProgressState) -> None:
        """Finalize progress bar display."""
        ...
```

**Behavior**:
- Determinate progress (total known): Shows progress bar with percentage
- Indeterminate progress (total=None): Shows spinner with item count
- Hierarchical progress: Shows main bar with current phase in title
- Output to stderr (preserves stdout for piping)

### CallbackProgressConsumer

```python
class CallbackProgressConsumer:
    """Adapts legacy callback(current, total) signatures."""

    def __init__(self, callback: Callable[[int, Optional[int]], None]) -> None:
        """
        Create callback adapter consumer.

        Args:
            callback: Function called as callback(current, total)
        """
        ...

    def on_progress(self, update: ProgressUpdate) -> None:
        """Invoke callback with current/total."""
        ...
```

**Use Case**: Backward compatibility with existing `ProgressTracker` callbacks

### LoggingProgressConsumer

```python
class LoggingProgressConsumer:
    """Logs progress updates at configurable intervals."""

    def __init__(
        self,
        logger: Optional[logging.Logger] = None,
        level: int = logging.INFO,
        log_interval: float = 5.0
    ) -> None:
        """
        Create logging consumer.

        Args:
            logger: Logger instance (default: root logger)
            level: Log level (default: INFO)
            log_interval: Min seconds between log messages (default 5.0)
        """
        ...

    def on_progress(self, update: ProgressUpdate) -> None:
        """Log progress if interval elapsed."""
        ...
```

**Log Format**: `"Progress: {label} - {current}/{total} ({percentage:.1f}%)"`

## Usage Examples

### Basic CLI Progress

```python
from progress_tracker import ProgressEmitter, CLIProgressConsumer

emitter = ProgressEmitter(total=100, label="Processing files")
consumer = CLIProgressConsumer()
emitter.add_consumer(consumer)

for i in range(100):
    process_file(files[i])
    emitter.update(1)

emitter.complete()
```

### Hierarchical Progress

```python
parent = ProgressEmitter(total=2, label="Overall")
cli = CLIProgressConsumer(title="Document Processing")
parent.add_consumer(cli)

# Phase 1: Text extraction
text_phase = parent.create_child(total=100, weight=0.4, label="Extract Text")
for page in pages:
    extract_text(page)
    text_phase.update(1)
text_phase.complete()

# Phase 2: Image processing
image_phase = parent.create_child(total=50, weight=0.6, label="Process Images")
for image in images:
    process_image(image)
    image_phase.update(1)
image_phase.complete()

parent.complete()
```

### Async Streaming

```python
async def monitor_progress(emitter: ProgressEmitter):
    async for update in emitter.stream():
        await websocket.send(json.dumps({
            "current": update.state.current,
            "total": update.state.total,
            "percentage": update.state.percentage
        }))

# Start monitoring in background
asyncio.create_task(monitor_progress(emitter))
```

### Indeterminate Progress

```python
emitter = ProgressEmitter(total=None, label="Streaming input")
emitter.add_consumer(CLIProgressConsumer())

for item in stream:
    process_item(item)
    emitter.update(1)

# Discover total mid-stream
if total_discovered:
    emitter.update_total(discovered_total)

emitter.complete()
```

### Legacy Callback Compatibility

```python
from progress_tracker import ProgressEmitter, CallbackProgressConsumer

def legacy_callback(current: int, total: int):
    print(f"Progress: {current}/{total}")

emitter = ProgressEmitter(total=100)
emitter.add_consumer(CallbackProgressConsumer(legacy_callback))

for i in range(100):
    process_item(i)
    emitter.update(1)
```

## Module Integration Pattern

### Processor Function Signature

```python
def process_items(
    items: List[T],
    progress_emitter: Optional[ProgressEmitter] = None
) -> List[Result]:
    """
    Process items with optional progress tracking.

    Args:
        items: Items to process
        progress_emitter: Optional progress tracker

    Returns:
        Processing results
    """
    if progress_emitter:
        progress_emitter.update_total(len(items))

    results = []
    for item in items:
        result = process_item(item)
        results.append(result)

        if progress_emitter:
            progress_emitter.update(1)

    if progress_emitter:
        progress_emitter.complete()

    return results
```

### CLI Integration

```python
def cli_main(files: List[Path], verbose: bool):
    emitter = ProgressEmitter(total=len(files), label="Processing files")

    if verbose:
        emitter.add_consumer(CLIProgressConsumer())

    results = process_items(files, progress_emitter=emitter)

    # Output to stdout (progress was on stderr)
    print(json.dumps(results, indent=2))
```

## Error Handling

### Consumer Exceptions

**Contract**: Emitter catches and logs consumer exceptions

```python
# In emitter implementation
def _notify_consumers(self, update: ProgressUpdate):
    for consumer in self._consumers:
        try:
            consumer.on_progress(update)
        except Exception as e:
            logger.error(f"Progress consumer error: {e}", exc_info=True)
```

**Consumer Responsibility**: Handle internal errors gracefully

```python
class MyConsumer:
    def on_progress(self, update: ProgressUpdate):
        try:
            self._render(update)
        except Exception as e:
            self.logger.error(f"Render error: {e}")
            # Fallback to simple output or suppress
```

### Validation Errors

**When Raised**: Invalid method arguments

```python
emitter = ProgressEmitter(total=100)
emitter.update(150)  # ValueError: update would exceed total

emitter.update_total(50)  # ValueError: new total < current

emitter = ProgressEmitter(total=None)
emitter.complete()  # ValueError: cannot complete indeterminate progress
```

## Performance Guarantees

- **Throttling**: Max 10 updates/sec per consumer (configurable)
- **Overhead**: <1% of total processing time (measured on 1000-item batches)
- **Memory**: O(1) per emitter (not O(N) for N items)
- **Latency**: <10ms per update (alive-progress rendering time)

## Thread Safety

**Not Thread-Safe**: ProgressEmitter is not thread-safe by default. Use locks if updating from multiple threads.

**Thread-Safe Alternative**: Create separate emitters per thread, aggregate with parent emitter.

```python
# Thread-safe hierarchical pattern
parent = ProgressEmitter(total=num_threads)

def worker(thread_id, items):
    child = parent.create_child(total=len(items), weight=1.0/num_threads)
    for item in items:
        process_item(item)
        child.update(1)
    child.complete()

with ThreadPoolExecutor() as executor:
    futures = [executor.submit(worker, i, items[i]) for i in range(num_threads)]
```

## Versioning

**Semantic Versioning**: Major.Minor.Patch

- **Major**: Breaking API changes
- **Minor**: New features, backward compatible
- **Patch**: Bug fixes, no API changes

**Current**: 1.0.0 (initial stable release)

## Contract Tests

All contracts are validated by tests in `tests/contract/`:

- `test_progress_protocol.py`: Validates ProgressConsumer protocol compliance
- `test_api_contracts.py`: Ensures public API stability
- `test_type_contracts.py`: Validates dataclass schemas and validation rules
