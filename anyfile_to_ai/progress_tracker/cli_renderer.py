"""CLI progress rendering using alive-progress."""

from alive_progress import alive_bar

from .models import ProgressState, ProgressUpdate, UpdateType


class CLIProgressConsumer:
    """Renders progress to stderr using alive-progress."""

    def __init__(self, show_percentage: bool = True, show_count: bool = True, title: str | None = None) -> None:
        """
        Create CLI progress consumer.

        Args:
            show_percentage: Display percentage (default True)
            show_count: Display "X/Y items" (default True)
            title: Override progress label with fixed title
        """
        self.show_percentage = show_percentage
        self.show_count = show_count
        self.title = title
        self._bar = None
        self._bar_context = None
        self._is_indeterminate = False
        self._last_total = None

    def on_progress(self, update: ProgressUpdate) -> None:
        """Render update to stderr."""
        state = update.state

        if self._bar is None or state.total != self._last_total:
            if self._bar_context is not None:
                self._bar_context.__exit__(None, None, None)

            if state.total is None:
                self._is_indeterminate = True
                self._bar_context = alive_bar(monitor=True, title=self.title or state.label or "Processing")
            else:
                self._is_indeterminate = False
                self._bar_context = alive_bar(state.total, title=self.title or state.label or "Processing")

            self._bar = self._bar_context.__enter__()
            self._last_total = state.total

        if self._is_indeterminate:
            if self.show_count:
                self._bar.text = f"{state.current} items"
            self._bar()
        else:
            if update.update_type == UpdateType.STARTED:
                self._bar(0)
            else:
                target = state.current
                if self._bar.current < target:
                    self._bar(target - self._bar.current)

            if self.show_count and state.label:
                self._bar.text = state.label

    def on_complete(self, state: ProgressState) -> None:
        """Finalize progress bar display."""
        if self._bar_context is not None:
            if self._bar is not None and not self._is_indeterminate:
                if state.total is not None and self._bar.current < state.total:
                    self._bar(state.total - self._bar.current)

            self._bar_context.__exit__(None, None, None)
            self._bar_context = None
            self._bar = None
