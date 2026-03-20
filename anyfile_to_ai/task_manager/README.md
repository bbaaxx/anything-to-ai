# Task Manager Module

> **Persistent Task State Storage for Long-Running Operations**

A Python module that provides JSON-based persistence for task state with checkpoint-based resume capability, page-level progress tracking, and automatic cleanup.

## Features

- **Persistent Storage**: Task state saved to JSON files in `.anything-to-ai/tasks/`
- **Checkpoint Resume**: Resume from last checkpoint on failure/interruption
- **Page-Level Tracking**: Track progress at page granularity for document processing
- **Auto-Cleanup**: TTL-based removal of stale tasks (default: 7 days)
- **Atomic Writes**: Temp file + rename for data integrity
- **File Locking**: `fcntl`-based locking for concurrent access safety
- **Thread-Safe**: Safe for concurrent checkpoint operations

## Installation

The task_manager module is part of `anyfile_to_ai` and requires no additional dependencies beyond the Python standard library.

```bash
pip install anyfile_to_ai
```

## Quick Start

### Basic Usage

```python
from anyfile_to_ai.task_manager import TaskManager, TaskState

# Create a task manager (default storage: .anything-to-ai/tasks/)
manager = TaskManager()

# Create a new task
task = manager.create_task(
    task_id="pdf-process-001",
    source_file="/path/to/document.pdf",
    total_pages=100,
)

# Checkpoint progress after each page
for page_num in range(1, task.total_pages + 1):
    process_page(page_num)  # Your processing logic
    manager.checkpoint("pdf-process-001", page_num)

# Check progress
progress = manager.get_task_progress("pdf-process-001")
print(f"Progress: {progress['progress_percent']:.1f}%")
```

### Resume from Checkpoint

```python
from anyfile_to_ai.task_manager import TaskManager, TaskNotFoundError

manager = TaskManager()

try:
    # Try to resume existing task
    task = manager.load_task("pdf-process-001")
    processed = set(task.processed_pages)
    remaining = [p for p in range(1, task.total_pages + 1) if p not in processed]
    print(f"Resuming from page {task.last_processed_page}")
except TaskNotFoundError:
    # Create new task
    task = manager.create_task(
        task_id="pdf-process-001",
        source_file="/path/to/document.pdf",
        total_pages=100,
    )
    remaining = list(range(1, task.total_pages + 1))

# Process remaining pages
for page_num in remaining:
    process_page(page_num)
    manager.checkpoint("pdf-process-001", page_num)
```

### Using with Routes

```python
from anyfile_to_ai.routes.pdf import (
    create_pdf_task,
    get_pdf_progress,
    checkpoint_pdf_page,
    resume_pdf_task,
)

# Create task
task = create_pdf_task("job-123", "/data/report.pdf", total_pages=50)

# Checkpoint after each page
for page in range(1, 51):
    process_page(page)
    checkpoint_pdf_page("job-123", page)

# Get progress
progress = get_pdf_progress("job-123")
print(f"Status: {progress['status']}")
print(f"Progress: {progress['progress_percent']:.1f}%")

# Resume from checkpoint
task, remaining_pages = resume_pdf_task("job-123")
```

## API Reference

### TaskManager

```python
class TaskManager:
    def __init__(
        self,
        storage_dir: Path | str | None = None,  # Default: .anything-to-ai/tasks/
        ttl_days: int = 7,                        # Days before auto-cleanup (0 = disabled)
        max_task_size_mb: int = 10,               # Max task file size in MB
    ) -> None:
        ...

    def create_task(
        self,
        task_id: str,
        source_file: str,
        total_pages: int,
        metadata: dict[str, Any] | None = None,
    ) -> TaskState:
        """Create a new task and persist it."""
        ...

    def load_task(self, task_id: str) -> TaskState:
        """Load an existing task from storage."""
        ...

    def save_task(self, task: TaskState) -> None:
        """Save task state to storage."""
        ...

    def checkpoint(self, task_id: str, processed_page: int) -> TaskState:
        """Update task with a newly processed page (atomic)."""
        ...

    def delete_task(self, task_id: str) -> None:
        """Delete a task from storage."""
        ...

    def list_tasks(self) -> list[str]:
        """List all task IDs in storage."""
        ...

    def task_exists(self, task_id: str) -> bool:
        """Check if a task exists."""
        ...

    def get_task_progress(self, task_id: str) -> dict[str, Any]:
        """Get progress information for a task."""
        ...
```

### TaskState

```python
@dataclass
class TaskState:
    task_id: str                    # Unique identifier
    source_file: str                # Path to source file
    total_pages: int                # Total pages to process
    processed_pages: list[int]      # Pages completed
    status: str                     # pending | in_progress | completed | failed
    created_at: str                 # ISO timestamp
    updated_at: str                 # ISO timestamp
    error_message: str | None       # Error if failed
    metadata: dict[str, Any]         # Custom metadata

    @property
    def progress_percent(self) -> float:
        """Progress as percentage (0-100)."""
        ...

    @property
    def is_complete(self) -> bool:
        """True if all pages processed."""
        ...

    @property
    def last_processed_page(self) -> int | None:
        """Last processed page number, or None."""
        ...

    def to_json(self) -> str:
        """Serialize to JSON string."""
        ...

    @classmethod
    def from_json(cls, json_str: str) -> "TaskState":
        """Deserialize from JSON string."""
        ...
```

### Exceptions

```python
class TaskStateError(Exception):
    """Base exception for task state errors."""
    ...

class TaskNotFoundError(TaskStateError):
    """Raised when a task cannot be found."""
    ...

class TaskCorruptError(TaskStateError):
    """Raised when task data is corrupted or invalid."""
    ...

class TaskIOError(TaskStateError):
    """Raised when file I/O operations fail."""
    ...

class TaskLockError(TaskStateError):
    """Raised when file locking fails."""
    ...
```

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `ANYFILE_TASKS_DIR` | `.anything-to-ai/tasks/` | Storage directory for task files |
| `ANYFILE_TASKS_TTL_DAYS` | `7` | Days before auto-cleanup (0 = disabled) |

### Custom Storage Location

```python
from pathlib import Path

# Custom storage directory
manager = TaskManager(
    storage_dir=Path("/var/lib/myapp/tasks"),
    ttl_days=30,  # Keep tasks for 30 days
)
```

## Storage Format

Tasks are stored as JSON files:

```
.anything-to-ai/tasks/
├── task-001.json
├── task-002.json
└── task-003.json
```

Each file contains:

```json
{
  "task_id": "pdf-process-001",
  "source_file": "/path/to/document.pdf",
  "total_pages": 100,
  "processed_pages": [1, 2, 3, 4, 5],
  "status": "in_progress",
  "created_at": "2026-03-20T00:00:00+00:00",
  "updated_at": "2026-03-20T00:05:00+00:00",
  "error_message": null,
  "metadata": {}
}
```

## Error Handling

```python
from anyfile_to_ai.task_manager import (
    TaskManager,
    TaskNotFoundError,
    TaskCorruptError,
    TaskIOError,
)

manager = TaskManager()

try:
    task = manager.load_task("nonexistent-task")
except TaskNotFoundError:
    print("Task not found - create a new one")
except TaskCorruptError as e:
    print(f"Task data is corrupt: {e}")
except TaskIOError as e:
    print(f"File system error: {e}")
```

## Best Practices

1. **Use meaningful task IDs**: Include context like file name or job ID
   ```python
   task_id = f"pdf-{file_hash}-{timestamp}"
   ```

2. **Checkpoint frequently**: Call `checkpoint()` after each unit of work
   ```python
   for page in pages:
       process(page)
       manager.checkpoint(task_id, page)  # Persist immediately
   ```

3. **Handle resume gracefully**: Always check for existing tasks
   ```python
   try:
       task = manager.load_task(task_id)
       # Resume from checkpoint
   except TaskNotFoundError:
       task = manager.create_task(task_id, ...)
   ```

4. **Clean up completed tasks**: Delete tasks when done
   ```python
   if task.is_complete:
       manager.delete_task(task_id)
   ```

## Thread Safety

The `checkpoint()` method uses file locking for concurrent access safety:

```python
# Safe for concurrent access
from threading import Thread

def worker(task_id, pages):
    for page in pages:
        process(page)
        manager.checkpoint(task_id, page)  # Thread-safe

threads = [
    Thread(target=worker, args=(task_id, page_range))
    for page_range in split_pages(pages, num_threads)
]
```

## Related Modules

- **`anyfile_to_ai.routes.pdf`**: PDF processing routes with TaskManager integration
- **`anyfile_to_ai.pdf_extractor`**: PDF text extraction with progress tracking