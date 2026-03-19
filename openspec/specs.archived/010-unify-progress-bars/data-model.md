# Data Model: Unified Progress Tracking

**Feature**: 010-unify-progress-bars
**Date**: 2025-10-02

## Overview

This document defines the data structures, state models, and relationships for the unified progress tracking system. All entities follow the dataclass pattern for immutability and type safety.

## Core Entities

### 1. ProgressState

**Purpose**: Immutable snapshot of progress at a point in time

**Fields**:

| Field | Type | Description | Validation |
|-------|------|-------------|------------|
| `current` | `int` | Items completed so far | >= 0 |
| `total` | `Optional[int]` | Total items to process | >= current if not None |
| `label` | `Optional[str]` | Human-readable description | Max 100 chars |
| `timestamp` | `float` | Unix timestamp when state created | > 0 (from time.monotonic()) |
| `metadata` | `Dict[str, Any]` | Optional additional data | Any JSON-serializable values |

**Derived Properties**:
- `percentage: Optional[float]` - Completion percentage (0.0-100.0), None if total is None
- `is_complete: bool` - True if current == total (and total is not None)
- `is_indeterminate: bool` - True if total is None
- `items_remaining: Optional[int]` - total - current, None if total is None

**State Transitions**:
```
Initial (0/N)
    ↓ update(increment)
In Progress (k/N, 0 < k < N)
    ↓ update(increment) or complete()
Complete (N/N)
```

**Special Cases**:
- Indeterminate: `total=None` → percentage and items_remaining are None
- Dynamic total: total can increase/decrease mid-process via `update_total()`

**Example**:
```python
@dataclass(frozen=True)
class ProgressState:
    current: int
    total: Optional[int]
    label: Optional[str] = None
    timestamp: float = field(default_factory=time.monotonic)
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def percentage(self) -> Optional[float]:
        if self.total is None or self.total == 0:
            return None
        return (self.current / self.total) * 100.0
```

### 2. ProgressUpdate

**Purpose**: Event payload sent to consumers when progress changes

**Fields**:

| Field | Type | Description | Validation |
|-------|------|-------------|------------|
| `state` | `ProgressState` | Current progress snapshot | Valid ProgressState |
| `delta` | `int` | Items added since last update | Can be negative if total decreased |
| `update_type` | `UpdateType` | Type of update event | One of UpdateType enum values |

**UpdateType Enum**:
- `STARTED`: Initial progress started (current=0)
- `PROGRESS`: Regular incremental update
- `TOTAL_CHANGED`: Total count was modified
- `COMPLETED`: Processing reached 100% (current=total)
- `ERROR`: Processing encountered error (consumer decides whether to display)

**Usage**:
```python
@dataclass(frozen=True)
class ProgressUpdate:
    state: ProgressState
    delta: int
    update_type: UpdateType
```

### 3. ProgressEmitter

**Purpose**: Mutable state manager that generates ProgressUpdate events

**Fields**:

| Field | Type | Description | Validation |
|-------|------|-------------|------------|
| `_current` | `int` | Current item count (private) | >= 0 |
| `_total` | `Optional[int]` | Total item count (private) | >= _current if not None |
| `_label` | `Optional[str]` | Progress label (private) | Max 100 chars |
| `_consumers` | `List[ProgressConsumer]` | Registered consumers (private) | N/A |
| `_children` | `List[ProgressEmitter]` | Child emitters (private) | For hierarchical progress |
| `_weights` | `List[float]` | Child weights (private) | Sum to 1.0 |
| `_last_update_time` | `float` | Last notify timestamp (private) | For throttling |
| `_throttle_interval` | `float` | Min seconds between updates | Default 0.1 (10 Hz) |

**Public Methods**:

```python
def update(self, increment: int = 1, force: bool = False) -> None:
    """Increment current by increment, notify consumers (respects throttling unless force=True)"""

def set_current(self, value: int, force: bool = False) -> None:
    """Set current to absolute value, notify consumers"""

def update_total(self, new_total: Optional[int]) -> None:
    """Change total (dynamic discovery), always forces notification"""

def complete(self) -> None:
    """Set current=total, send COMPLETED event, always forces notification"""

def add_consumer(self, consumer: ProgressConsumer) -> None:
    """Register a consumer to receive updates"""

def remove_consumer(self, consumer: ProgressConsumer) -> None:
    """Unregister a consumer"""

def create_child(self, total: Optional[int], weight: float = 1.0, label: Optional[str] = None) -> ProgressEmitter:
    """Create child emitter for hierarchical progress, child updates propagate to parent"""

async def stream(self) -> AsyncIterator[ProgressUpdate]:
    """Async generator yielding ProgressUpdate events (for async consumers)"""
```

**Internal Logic**:
- Throttling: Skip notifications if time since last update < throttle_interval (except force=True)
- Parent updates: When child emitter updates, parent recalculates weighted average and notifies
- Exception safety: Try-except around consumer notifications, log errors but continue

**State Invariants**:
- `0 <= _current <= _total` (if total is not None)
- `len(_children) == len(_weights)` (child/weight correspondence)
- `sum(_weights) == 1.0` (if children exist)

### 4. ProgressConsumer (Protocol)

**Purpose**: Abstract interface for progress update handlers

**Required Methods**:

```python
from typing import Protocol

class ProgressConsumer(Protocol):
    def on_progress(self, update: ProgressUpdate) -> None:
        """Handle a progress update event"""
        ...

    def on_complete(self, state: ProgressState) -> None:
        """Handle completion event (optional, default no-op)"""
        ...
```

**Contract**:
- `on_progress` MUST NOT raise exceptions (caller wraps in try-except, but consumers should handle their own errors)
- `on_progress` MUST NOT block for extended periods (use async consumers for long operations)
- `on_complete` called once when processing reaches 100%

**Implementations Planned**:
1. `CLIProgressConsumer`: Renders to stderr using alive-progress
2. `CallbackProgressConsumer`: Wraps legacy callback(current, total) signatures
3. `LoggingProgressConsumer`: Writes progress to logger at configurable intervals
4. (Future) `WebSocketProgressConsumer`: Streams updates to remote clients

## Entity Relationships

```
ProgressEmitter (1) ──[generates]──> (*) ProgressUpdate
     │                                      │
     │ contains                             │ contains
     │                                      │
     └──> (0..N) ProgressConsumer           └──> (1) ProgressState
              │
              │ implements
              │
              └── CLIProgressConsumer
              └── CallbackProgressConsumer
              └── LoggingProgressConsumer

ProgressEmitter (1) ──[parent-child]──> (*) ProgressEmitter (children)
```

## Hierarchical Progress Model

**Composition Pattern**:
- Parent emitter contains child emitters
- Each child has a weight (relative contribution to parent progress)
- Parent's current = weighted sum of children's percentages

**Example Scenario** (PDF extraction with image processing):
```
Parent: "Process Document" (total=100 pages)
  ├─ Child 1: "Extract Text" (weight=0.3, total=100 pages)
  └─ Child 2: "Process Images" (weight=0.7, total=50 images)

If Child 1 is 50% done and Child 2 is 0% done:
  Parent percentage = 0.3 * 50% + 0.7 * 0% = 15%
```

**Weight Calculation**:
- Default: Equal weights (1.0 / num_children)
- Custom: Provide weights based on relative complexity/time
- Auto-normalize: Weights normalized to sum to 1.0 if user provides unnormalized values

**Update Propagation**:
1. Child emitter calls `update()`
2. Child notifies its consumers
3. Child notifies parent via internal callback
4. Parent recalculates weighted progress
5. Parent notifies its consumers (subject to throttling)

## State Lifecycle

### Single-Level Progress

```python
# 1. Create emitter
emitter = ProgressEmitter(total=100, label="Processing files")

# 2. Register consumers
cli_consumer = CLIProgressConsumer()
emitter.add_consumer(cli_consumer)

# 3. Process items
for item in items:
    process_item(item)
    emitter.update(1)  # Sends PROGRESS update

# 4. Complete
emitter.complete()  # Sends COMPLETED update
```

### Hierarchical Progress

```python
# 1. Create parent
parent = ProgressEmitter(total=2, label="Overall")

# 2. Create children with weights
child1 = parent.create_child(total=100, weight=0.4, label="Phase 1")
child2 = parent.create_child(total=50, weight=0.6, label="Phase 2")

# 3. Children update independently
child1.update(50)  # Triggers parent update (parent at 20%)
child2.update(25)  # Triggers parent update (parent at 50%)

# 4. Children complete
child1.complete()  # Parent at 40%
child2.complete()  # Parent at 100%
```

### Indeterminate Progress

```python
# 1. Create with total=None
emitter = ProgressEmitter(total=None, label="Streaming input")
consumer = CLIProgressConsumer()  # Renders as spinner + count
emitter.add_consumer(consumer)

# 2. Update without known total
for item in stream:
    process_item(item)
    emitter.update(1)  # Shows "Processed: N items"

# 3. Discover total mid-stream
if total_discovered:
    emitter.update_total(discovered_total)  # Switches to determinate bar

# 4. Complete
emitter.complete()
```

### Dynamic Total Updates

```python
emitter = ProgressEmitter(total=100)
emitter.update(50)  # 50%

# Discover more items
emitter.update_total(150)  # Percentage drops to 33%
emitter.update(100)  # Back to 100%
```

## Validation Rules

### ProgressState Validation

```python
def __post_init__(self):
    if self.current < 0:
        raise ValueError("current must be non-negative")
    if self.total is not None and self.current > self.total:
        raise ValueError("current cannot exceed total")
    if self.label and len(self.label) > 100:
        raise ValueError("label too long (max 100 chars)")
```

### ProgressEmitter Validation

```python
def update(self, increment: int = 1) -> None:
    new_current = self._current + increment
    if new_current < 0:
        raise ValueError("update would make current negative")
    if self._total is not None and new_current > self._total:
        raise ValueError("update would exceed total")
    self._current = new_current
    self._notify_consumers(...)
```

## Serialization

**JSON Representation** (for logging, API responses):

```json
{
  "current": 50,
  "total": 100,
  "percentage": 50.0,
  "label": "Processing files",
  "timestamp": 1696251234.567,
  "metadata": {
    "current_file": "document.pdf",
    "phase": "extraction"
  }
}
```

**Async Stream** (for real-time monitoring):

```python
async for update in emitter.stream():
    json_str = json.dumps({
        "current": update.state.current,
        "total": update.state.total,
        "percentage": update.state.percentage,
        "type": update.update_type.value
    })
    await websocket.send(json_str)
```

## Performance Characteristics

**Memory**:
- ProgressState: ~80 bytes (5 fields + overhead)
- ProgressEmitter: ~200 bytes + (N consumers × 8 bytes) + (M children × 8 bytes)
- Per-update overhead: ~160 bytes (new ProgressUpdate + ProgressState)

**Time Complexity**:
- `update()`: O(1) amortized (throttling prevents excessive consumer calls)
- `add_consumer()`: O(1)
- Child update propagation: O(depth) where depth is hierarchy levels
- Weighted percentage calculation: O(num_children)

**Throttling Impact**:
- Without throttling: O(N) consumer calls for N items
- With 10 Hz throttling: O(N/10) consumer calls (90% reduction for fast processing)

## Migration from Legacy APIs

### pdf_extractor (ProgressInfo → ProgressState)

**Old**:
```python
@dataclass
class ProgressInfo:
    pages_processed: int
    total_pages: int
    percentage: float
    current_page: int
    estimated_remaining: float
```

**New**:
```python
state = ProgressState(
    current=progress_info.pages_processed,
    total=progress_info.total_pages,
    metadata={
        "current_page": progress_info.current_page,
        "estimated_remaining": progress_info.estimated_remaining
    }
)
```

### image_processor / audio_processor (ProgressTracker → ProgressEmitter)

**Old**:
```python
tracker = ProgressTracker(total_items=100, callback=lambda c, t: print(f"{c}/{t}"))
tracker.update(1)
```

**New**:
```python
emitter = ProgressEmitter(total=100)
emitter.add_consumer(CallbackProgressConsumer(lambda c, t: print(f"{c}/{t}")))
emitter.update(1)
```

## Summary

The data model provides:
- **Immutable state snapshots** (ProgressState) for thread-safety and debugging
- **Event-driven updates** (ProgressUpdate) for loose coupling
- **Composable emitters** (ProgressEmitter) for hierarchical progress
- **Protocol-based consumers** (ProgressConsumer) for extensibility
- **Backward compatibility** via adapter implementations

All entities are <250 lines, independently testable, and follow composition-first principles.
