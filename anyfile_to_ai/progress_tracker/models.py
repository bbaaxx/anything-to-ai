"""Data models and protocols for progress tracking."""

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Protocol, runtime_checkable


class UpdateType(Enum):
    """Progress update event types."""

    STARTED = "started"
    PROGRESS = "progress"
    TOTAL_CHANGED = "total_changed"
    COMPLETED = "completed"
    ERROR = "error"


@dataclass(frozen=True)
class ProgressState:
    """Immutable snapshot of progress state."""

    current: int
    total: int | None
    label: str | None = None
    timestamp: float = field(default_factory=time.monotonic)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if self.current < 0:
            raise ValueError("current must be non-negative")
        if self.total is not None and self.current > self.total:
            raise ValueError("current cannot exceed total")
        if self.label and len(self.label) > 100:
            raise ValueError("label too long (max 100 chars)")

    @property
    def percentage(self) -> float | None:
        """Completion percentage (0.0-100.0), None if indeterminate."""
        if self.total is None or self.total == 0:
            return None
        return (self.current / self.total) * 100.0

    @property
    def is_complete(self) -> bool:
        """True if current == total."""
        return self.total is not None and self.current == self.total

    @property
    def is_indeterminate(self) -> bool:
        """True if total is None."""
        return self.total is None

    @property
    def items_remaining(self) -> int | None:
        """Items left to process, None if indeterminate."""
        if self.total is None:
            return None
        return self.total - self.current


@dataclass(frozen=True)
class ProgressUpdate:
    """Progress update event payload."""

    state: ProgressState
    delta: int
    update_type: UpdateType


@runtime_checkable
class ProgressConsumer(Protocol):
    """Interface for progress update handlers."""

    def on_progress(self, update: ProgressUpdate) -> None:
        """Handle progress update event."""
        ...

    def on_complete(self, state: ProgressState) -> None:
        """Handle completion event."""
        ...
