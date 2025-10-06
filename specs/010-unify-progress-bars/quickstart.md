# Quickstart Guide: Unified Progress Tracking

**Feature**: 010-unify-progress-bars
**Audience**: Developers integrating progress tracking
**Time**: 5-10 minutes

## Installation

```bash
# Install progress_tracker module (once implemented)
uv add progress-tracker

# Or for development
cd /path/to/anyfile-to-ai
uv sync
```

## Basic Usage (CLI Progress Bar)

```python
from progress_tracker import ProgressEmitter, CLIProgressConsumer

def process_files(files: list[str]):
    """Process files with CLI progress bar."""
    # Create emitter with known total
    emitter = ProgressEmitter(total=len(files), label="Processing files")

    # Add CLI consumer for visual feedback
    emitter.add_consumer(CLIProgressConsumer())

    # Process items
    for file in files:
        process_file(file)
        emitter.update(1)  # Increment by 1

    # Mark complete
    emitter.complete()
```

**Output** (stderr):

```
Processing files |████████████████████████████████| 100% (42/42)
```

## Programmatic Usage (Callback)

```python
from progress_tracker import ProgressEmitter, CallbackProgressConsumer

def my_progress_callback(current: int, total: int):
    """Custom progress handler."""
    print(f"Progress: {current}/{total}")

def process_items(items: list):
    """Process items with custom callback."""
    emitter = ProgressEmitter(total=len(items))
    emitter.add_consumer(CallbackProgressConsumer(my_progress_callback))

    for item in items:
        process_item(item)
        emitter.update(1)

    emitter.complete()
```

## Async Streaming

```python
import asyncio
from progress_tracker import ProgressEmitter

async def monitor_progress(emitter: ProgressEmitter):
    """Async progress monitoring."""
    async for update in emitter.stream():
        print(f"Current: {update.state.current}, Percentage: {update.state.percentage}")

async def process_with_monitoring(items: list):
    """Process items with async monitoring."""
    emitter = ProgressEmitter(total=len(items))

    # Start monitoring in background
    monitor_task = asyncio.create_task(monitor_progress(emitter))

    # Process items
    for item in items:
        await process_item_async(item)
        emitter.update(1)

    emitter.complete()
    await monitor_task
```

## Hierarchical Progress (Multi-Phase)

```python
from progress_tracker import ProgressEmitter, CLIProgressConsumer

def process_document(pdf_path: str):
    """Process document with multiple phases."""
    # Create parent emitter
    parent = ProgressEmitter(total=2, label="Process Document")
    parent.add_consumer(CLIProgressConsumer(title="Document Processing"))

    # Phase 1: Extract text (40% of work)
    text_phase = parent.create_child(total=100, weight=0.4, label="Extract Text")
    for page in range(100):
        extract_text(pdf_path, page)
        text_phase.update(1)
    text_phase.complete()

    # Phase 2: Process images (60% of work)
    image_phase = parent.create_child(total=50, weight=0.6, label="Process Images")
    for image in range(50):
        process_image(pdf_path, image)
        image_phase.update(1)
    image_phase.complete()

    # Mark parent complete
    parent.complete()
```

**Output** (stderr):

```
Document Processing |██████████                    | 40% (Extract Text: 100/100)
Document Processing |████████████████████████████  | 100% (Process Images: 50/50)
```

## Indeterminate Progress (Unknown Total)

```python
from progress_tracker import ProgressEmitter, CLIProgressConsumer

def process_stream(data_stream):
    """Process streaming data with unknown total."""
    # Create with total=None for indeterminate
    emitter = ProgressEmitter(total=None, label="Streaming input")
    emitter.add_consumer(CLIProgressConsumer())

    items_processed = 0
    for item in data_stream:
        process_item(item)
        emitter.update(1)
        items_processed += 1

    # Can't call complete() with indeterminate progress
    # Instead, discover total and update
    emitter.update_total(items_processed)
    emitter.complete()
```

**Output** (stderr):

```
Streaming input ⠋ Processed: 42 items
```

## Dynamic Total Updates

```python
from progress_tracker import ProgressEmitter, CLIProgressConsumer

def process_with_discovery(initial_files: list[str]):
    """Process files and discover more during processing."""
    emitter = ProgressEmitter(total=len(initial_files), label="Processing files")
    emitter.add_consumer(CLIProgressConsumer())

    all_files = initial_files.copy()

    for i, file in enumerate(all_files):
        process_file(file)
        emitter.update(1)

        # Discover more files during processing
        new_files = discover_related_files(file)
        if new_files:
            all_files.extend(new_files)
            emitter.update_total(len(all_files))  # Update total dynamically

    emitter.complete()
```

## Module Integration Pattern

```python
from typing import Optional
from progress_tracker import ProgressEmitter

def process_images(
    image_paths: list[str],
    progress_emitter: Optional[ProgressEmitter] = None
) -> list[dict]:
    """
    Process images with optional progress tracking.

    Args:
        image_paths: Paths to images
        progress_emitter: Optional progress tracker

    Returns:
        Processing results
    """
    if progress_emitter:
        progress_emitter.update_total(len(image_paths))

    results = []
    for path in image_paths:
        result = process_single_image(path)
        results.append(result)

        if progress_emitter:
            emitter.update(1)

    if progress_emitter:
        progress_emitter.complete()

    return results
```

**CLI Usage**:

```python
def cli_main(image_paths: list[str], verbose: bool):
    """CLI entry point."""
    emitter = ProgressEmitter(total=len(image_paths), label="Processing images")

    if verbose:
        emitter.add_consumer(CLIProgressConsumer())

    results = process_images(image_paths, progress_emitter=emitter)

    # Output results to stdout (progress was on stderr)
    import json
    print(json.dumps(results, indent=2))
```

## Error Handling

```python
from progress_tracker import ProgressEmitter, CLIProgressConsumer
import logging

logger = logging.getLogger(__name__)

def process_with_error_handling(items: list):
    """Process items with robust error handling."""
    emitter = ProgressEmitter(total=len(items))
    emitter.add_consumer(CLIProgressConsumer())

    success_count = 0
    error_count = 0

    for item in items:
        try:
            process_item(item)
            success_count += 1
        except Exception as e:
            logger.error(f"Failed to process {item}: {e}")
            error_count += 1
        finally:
            emitter.update(1)  # Update progress regardless of success

    emitter.complete()

    logger.info(f"Processed {success_count} items, {error_count} errors")
```

## Testing Your Integration

```python
import pytest
from progress_tracker import ProgressEmitter, CallbackProgressConsumer

def test_progress_tracking():
    """Test that progress updates are sent correctly."""
    updates = []

    def capture_progress(current: int, total: int):
        updates.append((current, total))

    emitter = ProgressEmitter(total=3)
    emitter.add_consumer(CallbackProgressConsumer(capture_progress))

    emitter.update(1)
    emitter.update(1)
    emitter.update(1)
    emitter.complete()

    assert updates == [(1, 3), (2, 3), (3, 3), (3, 3)]
```

## Performance Tips

### Throttling (Default Behavior)

Progress updates are automatically throttled to 10 Hz (one update every 100ms) to avoid performance overhead:

```python
# Automatic throttling - only 10 updates/sec reach consumers
emitter = ProgressEmitter(total=10000)
for i in range(10000):
    process_fast_item(i)
    emitter.update(1)  # Only ~100 updates actually sent to consumers
```

### Force Updates (Override Throttling)

```python
# Force critical updates
emitter.update(1, force=True)  # Bypass throttling

# These are always forced (no need to specify):
emitter.update_total(new_total)  # Always notifies
emitter.complete()  # Always notifies
```

### Custom Throttle Interval

```python
# More aggressive throttling (5 Hz = 200ms)
emitter = ProgressEmitter(total=100, throttle_interval=0.2)

# Less throttling (20 Hz = 50ms)
emitter = ProgressEmitter(total=100, throttle_interval=0.05)
```

## Common Patterns

### Pattern 1: CLI with Quiet Mode

```python
def cli_process(files: list[str], quiet: bool = False):
    """Process with optional progress display."""
    emitter = ProgressEmitter(total=len(files))

    if not quiet:
        emitter.add_consumer(CLIProgressConsumer())

    for file in files:
        process_file(file)
        emitter.update(1)

    emitter.complete()
```

### Pattern 2: Multiple Consumers

```python
from progress_tracker import CLIProgressConsumer, LoggingProgressConsumer
import logging

def process_with_logging(items: list):
    """Progress to both CLI and logs."""
    emitter = ProgressEmitter(total=len(items))

    # Console progress bar
    emitter.add_consumer(CLIProgressConsumer())

    # Log progress every 5 seconds
    emitter.add_consumer(LoggingProgressConsumer(
        logger=logging.getLogger(__name__),
        log_interval=5.0
    ))

    for item in items:
        process_item(item)
        emitter.update(1)

    emitter.complete()
```

### Pattern 3: Nested Loops

```python
def process_batches(batches: list[list]):
    """Process batches of items with nested progress."""
    parent = ProgressEmitter(total=len(batches), label="Batches")
    parent.add_consumer(CLIProgressConsumer())

    for batch in batches:
        # Create child for this batch
        child = parent.create_child(total=len(batch), weight=1.0/len(batches))

        for item in batch:
            process_item(item)
            child.update(1)

        child.complete()

    parent.complete()
```

## Migrating from Legacy APIs

### From pdf_extractor.ProgressInfo

**Old**:

```python
def extract_pdf(path, callback):
    for page in pages:
        progress = ProgressInfo(
            pages_processed=i,
            total_pages=len(pages),
            percentage=(i/len(pages))*100,
            current_page=i,
            estimated_remaining=0.0
        )
        callback(progress)
```

**New**:

```python
def extract_pdf(path, progress_emitter=None):
    if progress_emitter:
        progress_emitter.update_total(len(pages))

    for page in pages:
        extract_page(page)
        if progress_emitter:
            progress_emitter.update(1)
```

### From image_processor.ProgressTracker

**Old**:

```python
tracker = ProgressTracker(
    total_items=100,
    callback=lambda c, t: print(f"{c}/{t}")
)
for item in items:
    process_item(item)
    tracker.update(1)
```

**New**:

```python
emitter = ProgressEmitter(total=100)
emitter.add_consumer(CallbackProgressConsumer(lambda c, t: print(f"{c}/{t}")))
for item in items:
    process_item(item)
    emitter.update(1)
```

## Next Steps

1. **Read API Documentation**: See [`contracts/api.md`](./contracts/api.md) for full API reference
2. **Review Data Model**: See [`data-model.md`](./data-model.md) for entity definitions
3. **Run Tests**: Execute `uv run pytest tests/contract/test_progress_protocol.py`
4. **Integrate into Module**: Follow module integration pattern above

## Troubleshooting

### Progress Bar Not Appearing

- Check that consumer is added: `emitter.add_consumer(CLIProgressConsumer())`
- Verify output is going to stderr (stdout may be buffered/piped)
- Ensure processing isn't too fast (progress may complete before render)

### Percentage Not Updating

- Confirm throttling isn't too aggressive (default 0.1s)
- Check that `update()` is being called in the loop
- Verify total was set correctly in constructor

### Complete() Raises ValueError

- Error: "cannot complete indeterminate progress"
- Fix: Call `update_total(discovered_total)` before `complete()`

### Memory Leak with Many Updates

- Progress updates are throttled by default (10 Hz)
- If storing updates externally, implement your own throttling
- Use async streaming with bounded queues if needed

## Support

For questions or issues:

- Review [`research.md`](./research.md) for design decisions
- Check [`data-model.md`](./data-model.md) for entity relationships
- See [`contracts/api.md`](./contracts/api.md) for API details
- Run contract tests: `uv run pytest tests/contract/`
