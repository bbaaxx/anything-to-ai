# Progress Tracker Module

Unified progress tracking system for processing modules with async-first composable design.

## Quick Start

```python
from progress_tracker import ProgressEmitter, CLIProgressConsumer

# Create emitter with total items
emitter = ProgressEmitter(total=100, label="Processing files")

# Add CLI consumer for visual feedback
emitter.add_consumer(CLIProgressConsumer())

# Update progress
for i in range(100):
    process_item(i)
    emitter.update(1)

# Mark complete
emitter.complete()
```

## Features

- **Immutable State**: ProgressState and ProgressUpdate are frozen dataclasses
- **Throttling**: Default 10 Hz (100ms) to minimize overhead
- **Hierarchical Progress**: Parent-child emitters with weighted averaging
- **Async Streaming**: Native async/await support via async generators
- **Exception Safe**: Consumer errors caught and logged, processing continues
- **Indeterminate Progress**: Support for unknown totals with spinners
- **Dynamic Totals**: Update total mid-process as items are discovered

## API Reference

### ProgressEmitter

Main class for tracking progress:

```python
# Constructor
emitter = ProgressEmitter(
    total=100,                    # Total items (None for indeterminate)
    label="Processing",           # Human-readable label
    throttle_interval=0.1         # Min seconds between updates (default 0.1)
)

# Basic methods
emitter.update(1)                 # Increment by 1
emitter.update(5, force=True)     # Force update (bypass throttling)
emitter.set_current(50)           # Set absolute value
emitter.update_total(200)         # Change total dynamically (always forces)
emitter.complete()                # Mark as complete (always forces)

# Consumer management
emitter.add_consumer(consumer)    # Register a consumer
emitter.remove_consumer(consumer) # Unregister a consumer

# Hierarchical progress
child = emitter.create_child(
    total=50,                     # Child's total
    weight=0.5,                   # Contribution to parent (0.0-1.0)
    label="Subtask"               # Child's label
)

# Async streaming
async for update in emitter.stream():
    print(f"Progress: {update.state.percentage}%")
    if update.update_type == UpdateType.COMPLETED:
        break

# Properties (read-only)
current = emitter.current         # Current progress value
total = emitter.total             # Total items
state = emitter.state             # Current ProgressState snapshot
```

### Consumers

Three built-in consumer implementations:

#### CLIProgressConsumer

Renders progress bars to stderr using alive-progress:

```python
from progress_tracker import CLIProgressConsumer

# Basic usage
consumer = CLIProgressConsumer()

# With options
consumer = CLIProgressConsumer(
    show_percentage=True,         # Display percentage (default: True)
    show_count=True,              # Display "X/Y items" (default: True)
    title="Custom Title"          # Override progress label
)
```

#### CallbackProgressConsumer

Wraps legacy callback(current, total) signatures:

```python
from progress_tracker import CallbackProgressConsumer

def my_callback(current: int, total: int):
    print(f"Progress: {current}/{total}")

consumer = CallbackProgressConsumer(my_callback)
```

#### LoggingProgressConsumer

Logs progress at configurable intervals:

```python
from progress_tracker import LoggingProgressConsumer
import logging

logger = logging.getLogger(__name__)
consumer = LoggingProgressConsumer(
    logger=logger,                # Logger instance
    log_interval=5.0              # Seconds between log messages (default: 5.0)
)
```

## Usage Patterns

### Basic Progress Bar

```python
from progress_tracker import ProgressEmitter, CLIProgressConsumer

emitter = ProgressEmitter(total=100, label="Processing")
emitter.add_consumer(CLIProgressConsumer())

for i in range(100):
    process_item(i)
    emitter.update(1)

emitter.complete()
```

### Indeterminate Progress

```python
from progress_tracker import ProgressEmitter, CLIProgressConsumer

# Unknown total - shows spinner + count
emitter = ProgressEmitter(total=None, label="Streaming")
emitter.add_consumer(CLIProgressConsumer())

for item in stream:
    process_item(item)
    emitter.update(1)

# Discover total and complete
emitter.update_total(items_processed)
emitter.complete()
```

### Hierarchical Progress

```python
from progress_tracker import ProgressEmitter, CLIProgressConsumer

parent = ProgressEmitter(total=100, label="Overall")
parent.add_consumer(CLIProgressConsumer())

# Phase 1: 40% of work
phase1 = parent.create_child(total=100, weight=0.4, label="Phase 1")
for i in range(100):
    process_phase1(i)
    phase1.update(1)
phase1.complete()

# Phase 2: 60% of work
phase2 = parent.create_child(total=50, weight=0.6, label="Phase 2")
for i in range(50):
    process_phase2(i)
    phase2.update(1)
phase2.complete()

parent.complete()
```

### Multiple Consumers

```python
from progress_tracker import (
    ProgressEmitter,
    CLIProgressConsumer,
    LoggingProgressConsumer
)
import logging

emitter = ProgressEmitter(total=100, label="Processing")

# Console progress bar
emitter.add_consumer(CLIProgressConsumer())

# Log progress every 5 seconds
logger = logging.getLogger(__name__)
emitter.add_consumer(LoggingProgressConsumer(logger, log_interval=5.0))

for i in range(100):
    process_item(i)
    emitter.update(1)

emitter.complete()
```

### Async Streaming

```python
import asyncio
from progress_tracker import ProgressEmitter, UpdateType

async def monitor_progress(emitter: ProgressEmitter):
    async for update in emitter.stream():
        print(f"Progress: {update.state.percentage:.1f}%")
        if update.update_type == UpdateType.COMPLETED:
            break

async def process_with_monitoring(items: list):
    emitter = ProgressEmitter(total=len(items), label="Processing")

    # Start monitoring in background
    monitor_task = asyncio.create_task(monitor_progress(emitter))

    # Process items
    for item in items:
        await process_item_async(item)
        emitter.update(1)

    emitter.complete()
    await monitor_task
```

## Integration with Modules

All processing modules support the unified progress system:

```python
from progress_tracker import ProgressEmitter, CLIProgressConsumer

# Example: PDF extraction
from pdf_extractor.reader import extract_text

emitter = ProgressEmitter(total=None, label="Extracting PDF")
emitter.add_consumer(CLIProgressConsumer())

result = extract_text("document.pdf", progress_emitter=emitter)

# Example: Text summarization
from text_summarizer.processor import TextSummarizer

summarizer = TextSummarizer()
emitter = ProgressEmitter(total=None, label="Summarizing")
emitter.add_consumer(CLIProgressConsumer())

result = summarizer.summarize(text, progress_emitter=emitter)
```

## Testing

```bash
# Contract tests (49 tests)
uv run pytest tests/contract/test_progress_protocol.py -v

# Integration tests (24 tests)
uv run pytest tests/integration/test_cli_progress.py -v
uv run pytest tests/integration/test_hierarchical.py -v
uv run pytest tests/integration/test_module_integration.py -v

# All progress tests (73 tests)
uv run pytest tests/contract/test_progress_protocol.py tests/integration/test_cli_progress.py tests/integration/test_hierarchical.py tests/integration/test_module_integration.py -v
```

## Migration from Legacy APIs

### From pdf_extractor.ProgressInfo

**Old**:
```python
from pdf_extractor.progress import ProgressInfo

info = ProgressInfo.create_started(total_pages)
# ... (deprecated)
```

**New**:
```python
from progress_tracker import ProgressEmitter, CLIProgressConsumer

emitter = ProgressEmitter(total=total_pages, label="Extracting PDF")
emitter.add_consumer(CLIProgressConsumer())
```

### From image_processor/audio_processor.ProgressTracker

**Old**:
```python
from image_processor.progress import ProgressTracker

tracker = ProgressTracker(
    total_items=100,
    callback=lambda c, t: print(f"{c}/{t}")
)
tracker.update(1)
# ... (deprecated)
```

**New**:
```python
from progress_tracker import ProgressEmitter, CallbackProgressConsumer

emitter = ProgressEmitter(total=100, label="Processing")
emitter.add_consumer(CallbackProgressConsumer(lambda c, t: print(f"{c}/{t}")))
emitter.update(1)
```

## Performance

- **Overhead**: <1% processing time with default throttling (10 Hz)
- **Memory**: ~160 bytes per update (ProgressUpdate + ProgressState)
- **Throttling**: Reduces consumer calls by 90% for fast operations

## Documentation

See `specs/010-unify-progress-bars/` for:
- `spec.md` - Feature specification
- `data-model.md` - Entity definitions and relationships
- `contracts/api.md` - Full API reference
- `quickstart.md` - Integration examples and patterns
- `research.md` - Technical decisions and alternatives
