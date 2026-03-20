"""TaskManager for persistent task state storage.

Provides JSON-based persistence for task state with:
- Checkpoint-based resume capability
- Page-level progress tracking
- Auto-cleanup with TTL
- Atomic writes for data integrity
"""

import json
import os
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import fcntl

from anyfile_to_ai.task_manager.models import TaskState
from anyfile_to_ai.task_manager.exceptions import (
    TaskStateError,
    TaskNotFoundError,
    TaskCorruptError,
    TaskIOError,
    TaskLockError,
)


class TaskManager:
    """Manages persistent task state storage.

    Task state is stored as JSON files in a configurable directory.
    Each task is stored in a separate file: {task_id}.json

    Features:
    - Atomic writes (temp file + rename)
    - File locking for concurrent access
    - TTL-based auto-cleanup
    - JSON validation on load

    Attributes:
        storage_dir: Directory where task files are stored
        ttl_days: Number of days before tasks are auto-cleaned (0 = no cleanup)
        max_task_size_mb: Maximum task file size in MB
    """

    DEFAULT_STORAGE_DIR = ".anything-to-ai/tasks"
    DEFAULT_TTL_DAYS = 7
    DEFAULT_MAX_TASK_SIZE_MB = 10

    def __init__(
        self,
        storage_dir: Path | str | None = None,
        ttl_days: int = DEFAULT_TTL_DAYS,
        max_task_size_mb: int = DEFAULT_MAX_TASK_SIZE_MB,
    ) -> None:
        """Initialize TaskManager.

        Args:
            storage_dir: Directory for task storage. Defaults to .anything-to-ai/tasks
            ttl_days: Days before auto-cleanup. 0 disables cleanup.
            max_task_size_mb: Maximum task file size in MB.
        """
        if storage_dir is None:
            storage_dir = Path.cwd() / self.DEFAULT_STORAGE_DIR
        self.storage_dir = Path(storage_dir)
        self.ttl_days = ttl_days
        self.max_task_size_mb = max_task_size_mb

        # Ensure storage directory exists
        self._ensure_storage_dir()

        # Run cleanup on init if TTL is enabled
        if self.ttl_days > 0:
            self._cleanup_expired_tasks()

    def _ensure_storage_dir(self) -> None:
        """Ensure the storage directory exists."""
        self.storage_dir.mkdir(parents=True, exist_ok=True)

    def _get_task_path(self, task_id: str) -> Path:
        """Get the file path for a task.

        Args:
            task_id: Unique task identifier

        Returns:
            Path to the task JSON file
        """
        return self.storage_dir / f"{task_id}.json"

    def _acquire_lock(self, file_path: Path) -> None:
        """Acquire an exclusive lock on a file.

        Args:
            file_path: Path to the file to lock

        Raises:
            TaskLockError: If lock cannot be acquired
        """
        lock_path = file_path.with_suffix(file_path.suffix + ".lock")
        try:
            lock_file = open(lock_path, "w")
            fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX)
            # Store lock file handle for later release
            self._lock_files = getattr(self, "_lock_files", {})
            self._lock_files[str(file_path)] = lock_file
        except (IOError, OSError) as e:
            raise TaskLockError(
                operation="acquire",
                task_id=None,
                file_path=file_path,
            ) from e

    def _release_lock(self, file_path: Path) -> None:
        """Release the lock on a file.

        Args:
            file_path: Path to the file to unlock
        """
        lock_files = getattr(self, "_lock_files", {})
        lock_file = lock_files.pop(str(file_path), None)
        if lock_file:
            try:
                fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)
                lock_file.close()
            except (IOError, OSError):
                pass  # Ignore errors during unlock

            # Remove lock file
            lock_path = file_path.with_suffix(file_path.suffix + ".lock")
            try:
                lock_path.unlink(missing_ok=True)
            except (IOError, OSError):
                pass  # Ignore errors during lock file removal

    def _atomic_write(self, file_path: Path, content: str) -> None:
        """Write content to file atomically using temp file + rename.

        Args:
            file_path: Target file path
            content: Content to write

        Raises:
            TaskIOError: If write fails
        """
        temp_path = None
        try:
            # Write to temp file first
            fd, temp_path_str = tempfile.mkstemp(
                dir=self.storage_dir,
                suffix=".tmp",
            )
            temp_path = Path(temp_path_str)
            with os.fdopen(fd, "w") as f:
                f.write(content)

            # Atomic rename
            os.replace(temp_path, file_path)
        except (IOError, OSError) as e:
            # Clean up temp file if it exists
            if temp_path and temp_path.exists():
                try:
                    temp_path.unlink()
                except (IOError, OSError):
                    pass
            raise TaskIOError(
                operation="write",
                task_id=None,
                file_path=file_path,
                cause=e,
            ) from e

    def _validate_task_size(self, file_path: Path) -> None:
        """Validate that task file is within size limits.

        Args:
            file_path: Path to task file

        Raises:
            TaskCorruptError: If file exceeds size limit
        """
        try:
            size_mb = file_path.stat().st_size / (1024 * 1024)
            if size_mb > self.max_task_size_mb:
                raise TaskCorruptError(
                    task_id=None,
                    reason=f"Task file exceeds size limit ({size_mb:.2f}MB > {self.max_task_size_mb}MB)",
                    file_path=file_path,
                )
        except FileNotFoundError:
            raise TaskNotFoundError(
                task_id=None,
                file_path=file_path,
            )

    def _cleanup_expired_tasks(self) -> int:
        """Remove tasks older than TTL.

        Uses file modification time for cleanup, not task's updated_at field.

        Returns:
            Number of tasks removed
        """
        if self.ttl_days <= 0:
            return 0

        removed_count = 0
        cutoff = datetime.now(timezone.utc) - timedelta(days=self.ttl_days)

        for task_file in self.storage_dir.glob("*.json"):
            try:
                # Use file modification time for cleanup
                file_mtime = datetime.fromtimestamp(
                    task_file.stat().st_mtime,
                    tz=timezone.utc,
                )

                # Remove if expired
                if file_mtime < cutoff:
                    self.delete_task(task_file.stem)
                    removed_count += 1
            except (TaskStateError, ValueError):
                # Remove corrupt tasks
                try:
                    task_file.unlink()
                    removed_count += 1
                except (IOError, OSError):
                    pass

        return removed_count

    def create_task(
        self,
        task_id: str,
        source_file: str,
        total_pages: int,
        metadata: dict[str, Any] | None = None,
    ) -> TaskState:
        """Create a new task and persist it.

        Args:
            task_id: Unique task identifier
            source_file: Path to the source file being processed
            total_pages: Total number of pages to process
            metadata: Optional additional metadata

        Returns:
            Created TaskState instance

        Raises:
            TaskStateError: If task already exists
            TaskIOError: If write fails
        """
        task_path = self._get_task_path(task_id)

        # Check if task already exists
        if task_path.exists():
            raise TaskStateError(
                f"Task already exists: {task_id}",
                task_id=task_id,
                file_path=task_path,
            )

        # Create task state
        task = TaskState(
            task_id=task_id,
            source_file=source_file,
            total_pages=total_pages,
            metadata=metadata or {},
        )

        # Persist to disk
        self._atomic_write(task_path, task.to_json())

        return task

    def load_task(self, task_id: str) -> TaskState:
        """Load a task from persistent storage.

        Args:
            task_id: Unique task identifier

        Returns:
            TaskState instance

        Raises:
            TaskNotFoundError: If task doesn't exist
            TaskCorruptError: If task data is invalid
        """
        task_path = self._get_task_path(task_id)

        # Check if task exists
        if not task_path.exists():
            raise TaskNotFoundError(task_id=task_id, file_path=task_path)

        # Validate size
        self._validate_task_size(task_path)

        # Read and parse
        try:
            content = task_path.read_text()
            task = TaskState.from_json(content)
            return task
        except json.JSONDecodeError as e:
            raise TaskCorruptError(
                task_id=task_id,
                reason=f"Invalid JSON: {e}",
                file_path=task_path,
            ) from e
        except ValueError as e:
            raise TaskCorruptError(
                task_id=task_id,
                reason=str(e),
                file_path=task_path,
            ) from e
        except (IOError, OSError) as e:
            raise TaskIOError(
                operation="read",
                task_id=task_id,
                file_path=task_path,
                cause=e,
            ) from e

    def save_task(self, task: TaskState) -> None:
        """Save task state to persistent storage.

        Args:
            task: TaskState instance to save

        Raises:
            TaskIOError: If write fails
        """
        task_path = self._get_task_path(task.task_id)

        # Update timestamp
        task.updated_at = datetime.now(timezone.utc).isoformat()

        # Persist to disk
        self._atomic_write(task_path, task.to_json())

    def checkpoint(
        self,
        task_id: str,
        processed_page: int,
    ) -> TaskState:
        """Update task with a newly processed page.

        This is the core method for incremental progress tracking.
        It atomically updates the task state with the new page.

        Args:
            task_id: Unique task identifier
            processed_page: Page number that was just processed

        Returns:
            Updated TaskState instance

        Raises:
            TaskNotFoundError: If task doesn't exist
            TaskCorruptError: If task data is invalid
            TaskIOError: If write fails
        """
        # Load current state
        task = self.load_task(task_id)

        # Acquire lock for atomic update
        task_path = self._get_task_path(task_id)
        self._acquire_lock(task_path)

        try:
            # Reload to get latest state (in case of concurrent updates)
            task = self.load_task(task_id)

            # Add page if not already processed
            if processed_page not in task.processed_pages:
                task.processed_pages.append(processed_page)
                task.processed_pages.sort()

            # Update status if needed
            if task.status == "pending":
                task.status = "in_progress"
            elif task.is_complete and task.status == "in_progress":
                task.status = "completed"

            # Save updated state
            self.save_task(task)

            return task
        finally:
            self._release_lock(task_path)

    def delete_task(self, task_id: str) -> None:
        """Delete a task from persistent storage.

        Args:
            task_id: Unique task identifier

        Raises:
            TaskNotFoundError: If task doesn't exist
            TaskIOError: If deletion fails
        """
        task_path = self._get_task_path(task_id)

        if not task_path.exists():
            raise TaskNotFoundError(task_id=task_id, file_path=task_path)

        try:
            task_path.unlink()
        except (IOError, OSError) as e:
            raise TaskIOError(
                operation="delete",
                task_id=task_id,
                file_path=task_path,
                cause=e,
            ) from e

    def list_tasks(self) -> list[str]:
        """List all task IDs in storage.

        Returns:
            List of task IDs (filenames without .json extension)
        """
        task_ids = []
        for task_file in self.storage_dir.glob("*.json"):
            task_ids.append(task_file.stem)
        return sorted(task_ids)

    def task_exists(self, task_id: str) -> bool:
        """Check if a task exists.

        Args:
            task_id: Unique task identifier

        Returns:
            True if task exists, False otherwise
        """
        return self._get_task_path(task_id).exists()

    def get_task_progress(self, task_id: str) -> dict[str, Any]:
        """Get progress information for a task.

        Args:
            task_id: Unique task identifier

        Returns:
            Dictionary with progress information:
            - total_pages: Total pages to process
            - processed_pages: Number of pages processed
            - remaining_pages: Number of pages remaining
            - progress_percent: Progress as percentage
            - status: Current task status

        Raises:
            TaskNotFoundError: If task doesn't exist
        """
        task = self.load_task(task_id)
        return {
            "total_pages": task.total_pages,
            "processed_pages": len(task.processed_pages),
            "remaining_pages": task.total_pages - len(task.processed_pages),
            "progress_percent": task.progress_percent,
            "status": task.status,
        }
