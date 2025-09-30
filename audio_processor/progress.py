"""
Progress tracking utilities for audio processing.
"""

from typing import Optional, Callable


class ProgressTracker:
    """Handles progress tracking and callback management."""

    def __init__(self, total_items: int, callback: Optional[Callable[[int, int], None]] = None):
        self.total_items = total_items
        self.current_item = 0
        self.callback = callback

    def update(self, increment: int = 1) -> None:
        """Update progress counter and call callback if provided."""
        self.current_item += increment
        if self.callback:
            try:
                self.callback(self.current_item, self.total_items)
            except Exception:
                # Silently ignore callback errors to not disrupt processing
                pass

    def set_current(self, current: int) -> None:
        """Set current progress value."""
        self.current_item = current
        if self.callback:
            try:
                self.callback(self.current_item, self.total_items)
            except Exception:
                pass

    def complete(self) -> None:
        """Mark progress as complete."""
        self.current_item = self.total_items
        if self.callback:
            try:
                self.callback(self.current_item, self.total_items)
            except Exception:
                pass