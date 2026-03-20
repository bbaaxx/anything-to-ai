"""Data models for task state persistence."""

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Any
import json


@dataclass
class TaskState:
    """Represents the persistent state of a processing task.

    Attributes:
        task_id: Unique identifier for the task
        source_file: Path to the source file being processed
        total_pages: Total number of pages to process
        processed_pages: List of page numbers that have been processed
        status: Current status of the task (pending, in_progress, completed, failed)
        created_at: ISO timestamp when the task was created
        updated_at: ISO timestamp when the task was last updated
        error_message: Error message if task failed, None otherwise
        metadata: Additional task-specific metadata
    """

    task_id: str
    source_file: str
    total_pages: int
    processed_pages: list[int] = field(default_factory=list)
    status: str = "pending"
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    error_message: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Validate task state after initialization."""
        if not self.task_id:
            raise ValueError("task_id cannot be empty")
        if not self.source_file:
            raise ValueError("source_file cannot be empty")
        if self.total_pages < 0:
            raise ValueError("total_pages cannot be negative")
        if self.status not in ("pending", "in_progress", "completed", "failed"):
            raise ValueError(f"Invalid status: {self.status}")

        # Ensure processed_pages contains valid page numbers
        for page in self.processed_pages:
            if page < 1 or page > self.total_pages:
                raise ValueError(f"Invalid page number {page} for total_pages {self.total_pages}")

    @property
    def progress_percent(self) -> float:
        """Calculate progress as a percentage."""
        if self.total_pages == 0:
            return 0.0
        return (len(self.processed_pages) / self.total_pages) * 100

    @property
    def is_complete(self) -> bool:
        """Check if all pages have been processed."""
        return len(self.processed_pages) == self.total_pages

    @property
    def last_processed_page(self) -> int | None:
        """Get the last processed page number, or None if no pages processed."""
        return max(self.processed_pages) if self.processed_pages else None

    def to_json(self) -> str:
        """Serialize task state to JSON string."""
        return json.dumps(asdict(self), indent=2)

    @classmethod
    def from_json(cls, json_str: str) -> "TaskState":
        """Deserialize task state from JSON string.

        Args:
            json_str: JSON string representation of task state

        Returns:
            TaskState instance

        Raises:
            ValueError: If JSON is invalid or missing required fields
        """
        try:
            data = json.loads(json_str)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON: {e}") from e

        required_fields = {"task_id", "source_file", "total_pages"}
        missing = required_fields - set(data.keys())
        if missing:
            raise ValueError(f"Missing required fields: {missing}")

        return cls(
            task_id=data["task_id"],
            source_file=data["source_file"],
            total_pages=data["total_pages"],
            processed_pages=data.get("processed_pages", []),
            status=data.get("status", "pending"),
            created_at=data.get("created_at", datetime.now(timezone.utc).isoformat()),
            updated_at=data.get("updated_at", datetime.now(timezone.utc).isoformat()),
            error_message=data.get("error_message"),
            metadata=data.get("metadata", {}),
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert task state to dictionary."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "TaskState":
        """Create task state from dictionary.

        Args:
            data: Dictionary with task state fields

        Returns:
            TaskState instance
        """
        return cls(
            task_id=data["task_id"],
            source_file=data["source_file"],
            total_pages=data["total_pages"],
            processed_pages=data.get("processed_pages", []),
            status=data.get("status", "pending"),
            created_at=data.get("created_at", datetime.now(timezone.utc).isoformat()),
            updated_at=data.get("updated_at", datetime.now(timezone.utc).isoformat()),
            error_message=data.get("error_message"),
            metadata=data.get("metadata", {}),
        )
