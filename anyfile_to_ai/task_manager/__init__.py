"""TaskManager module for persistent task state storage.

Provides JSON-based persistence for task state with:
- Checkpoint-based resume capability
- Page-level progress tracking
- Auto-cleanup with TTL
- Atomic writes for data integrity
"""

from anyfile_to_ai.task_manager.models import TaskState
from anyfile_to_ai.task_manager.exceptions import (
    TaskStateError,
    TaskNotFoundError,
    TaskCorruptError,
    TaskIOError,
    TaskLockError,
)
from anyfile_to_ai.task_manager.task_manager import TaskManager

__all__ = [
    "TaskCorruptError",
    "TaskIOError",
    "TaskLockError",
    "TaskManager",
    "TaskNotFoundError",
    "TaskState",
    "TaskStateError",
]
