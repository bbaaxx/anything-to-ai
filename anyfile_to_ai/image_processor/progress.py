"""Progress tracking for image processing."""

from collections.abc import Callable


class ProgressTracker:
    """Tracks progress of image processing operations."""

    def __init__(
        self,
        total: int = 0,
        callback: Callable[[int, int], None] | None = None,
    ):
        """
        Initialize progress tracker.

        Args:
            total: Total number of items to process
            callback: Optional callback function (current, total)
        """
        self.total = total
        self.current = 0
        self.callback = callback

    def update(self, current: int | None = None) -> None:
        """
        Update progress.

        Args:
            current: Current progress value (if None, increments by 1)
        """
        if current is None:
            self.current += 1
        else:
            self.current = current
        if self.callback:
            self.callback(self.current, self.total)

    def increment(self) -> None:
        """Increment progress by 1."""
        self.current += 1
        if self.callback:
            self.callback(self.current, self.total)
