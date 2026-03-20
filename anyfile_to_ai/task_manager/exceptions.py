"""Custom exceptions for task state management."""

from pathlib import Path


class TaskStateError(Exception):
    """Base exception for task state errors.

    Attributes:
        message: Human-readable error description
        task_id: Optional task identifier
        file_path: Optional path to the task file
    """

    def __init__(
        self,
        message: str,
        task_id: str | None = None,
        file_path: Path | str | None = None,
    ) -> None:
        self.message = message
        self.task_id = task_id
        self.file_path = Path(file_path) if file_path else None
        super().__init__(message)

    def __str__(self) -> str:
        """Return formatted error message."""
        parts = [self.message]
        if self.task_id:
            parts.append(f"task_id={self.task_id}")
        if self.file_path:
            parts.append(f"file={self.file_path}")
        return " | ".join(parts)


class TaskNotFoundError(TaskStateError):
    """Raised when a task cannot be found.

    This occurs when attempting to load a task that doesn't exist
    in the persistent storage.
    """

    def __init__(
        self,
        task_id: str | None = None,
        file_path: Path | str | None = None,
    ) -> None:
        message = f"Task not found: {task_id}" if task_id else "Task not found"
        super().__init__(message, task_id=task_id, file_path=file_path)


class TaskCorruptError(TaskStateError):
    """Raised when task data is corrupted or invalid.

    This occurs when:
    - JSON file cannot be parsed
    - Required fields are missing
    - Field values are invalid
    """

    def __init__(
        self,
        task_id: str | None,
        reason: str,
        file_path: Path | str | None = None,
    ) -> None:
        message = f"Corrupt task data: {reason}"
        super().__init__(message, task_id=task_id, file_path=file_path)


class TaskIOError(TaskStateError):
    """Raised when file I/O operations fail.

    This wraps IOError/OSError with additional context about
    the task operation that failed.
    """

    def __init__(
        self,
        operation: str,
        task_id: str | None = None,
        file_path: Path | str | None = None,
        cause: Exception | None = None,
    ) -> None:
        message = f"Task I/O error during {operation}"
        if cause:
            message = f"{message}: {cause}"
        super().__init__(message, task_id=task_id, file_path=file_path)
        self.__cause__ = cause


class TaskLockError(TaskStateError):
    """Raised when file locking fails.

    This indicates concurrent access issues or lock file problems.
    """

    def __init__(
        self,
        operation: str,
        task_id: str | None = None,
        file_path: Path | str | None = None,
    ) -> None:
        message = f"Failed to acquire lock for {operation}"
        super().__init__(message, task_id=task_id, file_path=file_path)
