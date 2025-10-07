"""Consumer implementations for progress tracking."""

import logging
import time
from collections.abc import Callable

from .models import ProgressState, ProgressUpdate


class CallbackProgressConsumer:
    """Adapts legacy callback(current, total) signatures."""

    def __init__(self, callback: Callable[[int, int | None], None]) -> None:
        """
        Create callback adapter consumer.

        Args:
            callback: Function called as callback(current, total)
        """
        self.callback = callback

    def on_progress(self, update: ProgressUpdate) -> None:
        """Invoke callback with current/total."""
        try:
            self.callback(update.state.current, update.state.total)
        except Exception as e:
            logging.exception(f"Callback error: {e}")

    def on_complete(self, state: ProgressState) -> None:
        """Handle completion event."""
        try:
            self.callback(state.current, state.total)
        except Exception as e:
            logging.exception(f"Callback error on complete: {e}")


class LoggingProgressConsumer:
    """Logs progress updates at configurable intervals."""

    def __init__(self, logger: logging.Logger | None = None, level: int = logging.INFO, log_interval: float = 5.0) -> None:
        """
        Create logging consumer.

        Args:
            logger: Logger instance (default: root logger)
            level: Log level (default: INFO)
            log_interval: Min seconds between log messages (default 5.0)
        """
        self.logger = logger or logging.getLogger(__name__)
        self.level = level
        self.log_interval = log_interval
        self._last_log_time = 0.0

    def on_progress(self, update: ProgressUpdate) -> None:
        """Log progress if interval elapsed."""
        now = time.monotonic()
        if now - self._last_log_time >= self.log_interval:
            state = update.state
            if state.total is not None:
                percentage = state.percentage or 0.0
                message = f"Progress: {state.label or 'Processing'} - {state.current}/{state.total} ({percentage:.1f}%)"
            else:
                message = f"Progress: {state.label or 'Processing'} - {state.current} items"
            self.logger.log(self.level, message)
            self._last_log_time = now

    def on_complete(self, state: ProgressState) -> None:
        """Log completion."""
        message = f"Complete: {state.label or 'Processing'} - {state.current} items"
        self.logger.log(self.level, message)
