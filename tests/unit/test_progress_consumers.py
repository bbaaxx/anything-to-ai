"""Unit tests for progress_tracker consumers."""

import logging
import time
from unittest.mock import Mock, MagicMock, patch
from anyfile_to_ai.progress_tracker.consumers import (
    CallbackProgressConsumer,
    LoggingProgressConsumer,
)
from anyfile_to_ai.progress_tracker.cli_renderer import CLIProgressConsumer
from anyfile_to_ai.progress_tracker.models import (
    ProgressState,
    ProgressUpdate,
    UpdateType,
)


class TestCallbackProgressConsumer:
    """Unit tests for CallbackProgressConsumer."""

    def test_create_with_callback(self):
        """Test creating consumer with callback."""
        callback = Mock()
        consumer = CallbackProgressConsumer(callback)
        assert consumer.callback == callback

    def test_on_progress_calls_callback(self):
        """Test that on_progress invokes callback with current/total."""
        callback = Mock()
        consumer = CallbackProgressConsumer(callback)

        state = ProgressState(current=5, total=10)
        update = ProgressUpdate(state, delta=1, update_type=UpdateType.PROGRESS)

        consumer.on_progress(update)
        callback.assert_called_once_with(5, 10)

    def test_on_progress_indeterminate(self):
        """Test on_progress with indeterminate progress."""
        callback = Mock()
        consumer = CallbackProgressConsumer(callback)

        state = ProgressState(current=5, total=None)
        update = ProgressUpdate(state, delta=1, update_type=UpdateType.PROGRESS)

        consumer.on_progress(update)
        callback.assert_called_once_with(5, None)

    def test_on_complete_calls_callback(self):
        """Test that on_complete invokes callback."""
        callback = Mock()
        consumer = CallbackProgressConsumer(callback)

        state = ProgressState(current=10, total=10)

        consumer.on_complete(state)
        callback.assert_called_once_with(10, 10)

    def test_callback_exception_logged(self):
        """Test that callback exceptions are logged."""

        def error_callback(current, total):
            msg = "Test error"
            raise RuntimeError(msg)

        consumer = CallbackProgressConsumer(error_callback)
        state = ProgressState(current=5, total=10)
        update = ProgressUpdate(state, delta=1, update_type=UpdateType.PROGRESS)

        consumer.on_progress(update)

    def test_multiple_updates(self):
        """Test multiple progress updates."""
        calls = []

        def callback(current, total):
            calls.append((current, total))

        consumer = CallbackProgressConsumer(callback)

        for i in range(1, 6):
            state = ProgressState(current=i, total=10)
            update = ProgressUpdate(state, delta=1, update_type=UpdateType.PROGRESS)
            consumer.on_progress(update)

        assert calls == [(1, 10), (2, 10), (3, 10), (4, 10), (5, 10)]


class TestLoggingProgressConsumer:
    """Unit tests for LoggingProgressConsumer."""

    def test_create_with_defaults(self):
        """Test creating consumer with default logger."""
        consumer = LoggingProgressConsumer()
        assert consumer.logger is not None
        assert consumer.level == logging.INFO
        assert consumer.log_interval == 5.0

    def test_create_with_custom_logger(self):
        """Test creating consumer with custom logger."""
        logger = logging.getLogger("test")
        consumer = LoggingProgressConsumer(logger=logger, level=logging.DEBUG, log_interval=2.0)
        assert consumer.logger == logger
        assert consumer.level == logging.DEBUG
        assert consumer.log_interval == 2.0

    def test_on_progress_logs_message(self):
        """Test that on_progress logs progress message."""
        logger = Mock()
        consumer = LoggingProgressConsumer(logger=logger, log_interval=0.0)

        state = ProgressState(current=50, total=100, label="Test")
        update = ProgressUpdate(state, delta=1, update_type=UpdateType.PROGRESS)

        consumer.on_progress(update)
        logger.log.assert_called_once()
        call_args = logger.log.call_args
        assert call_args[0][0] == logging.INFO
        assert "50/100" in call_args[0][1]
        assert "50.0%" in call_args[0][1]

    def test_on_progress_indeterminate(self):
        """Test logging indeterminate progress."""
        logger = Mock()
        consumer = LoggingProgressConsumer(logger=logger, log_interval=0.0)

        state = ProgressState(current=42, total=None, label="Test")
        update = ProgressUpdate(state, delta=1, update_type=UpdateType.PROGRESS)

        consumer.on_progress(update)
        call_args = logger.log.call_args
        assert "42 items" in call_args[0][1]

    def test_log_interval_throttling(self):
        """Test that log_interval throttles logging."""
        logger = Mock()
        consumer = LoggingProgressConsumer(logger=logger, log_interval=0.1)

        state = ProgressState(current=1, total=10)
        update = ProgressUpdate(state, delta=1, update_type=UpdateType.PROGRESS)

        consumer.on_progress(update)
        assert logger.log.call_count == 1

        consumer.on_progress(update)
        consumer.on_progress(update)
        assert logger.log.call_count == 1

    def test_log_interval_elapsed(self):
        """Test logging after interval elapses."""
        logger = Mock()
        consumer = LoggingProgressConsumer(logger=logger, log_interval=0.05)

        state = ProgressState(current=1, total=10)
        update = ProgressUpdate(state, delta=1, update_type=UpdateType.PROGRESS)

        consumer.on_progress(update)
        assert logger.log.call_count == 1

        time.sleep(0.06)
        consumer.on_progress(update)
        assert logger.log.call_count == 2

    def test_on_complete_logs_completion(self):
        """Test that on_complete logs completion message."""
        logger = Mock()
        consumer = LoggingProgressConsumer(logger=logger)

        state = ProgressState(current=100, total=100, label="Test")

        consumer.on_complete(state)
        logger.log.assert_called_once()
        call_args = logger.log.call_args
        assert "Complete" in call_args[0][1]
        assert "100 items" in call_args[0][1]

    def test_default_label(self):
        """Test default label when none provided."""
        logger = Mock()
        consumer = LoggingProgressConsumer(logger=logger, log_interval=0.0)

        state = ProgressState(current=50, total=100)
        update = ProgressUpdate(state, delta=1, update_type=UpdateType.PROGRESS)

        consumer.on_progress(update)
        call_args = logger.log.call_args
        assert "Processing" in call_args[0][1]


class TestCLIProgressConsumer:
    """Unit tests for CLIProgressConsumer."""

    def test_create_with_defaults(self):
        """Test creating CLI consumer with defaults."""
        consumer = CLIProgressConsumer()
        assert consumer.show_percentage is True
        assert consumer.show_count is True
        assert consumer.title is None

    def test_create_with_custom_options(self):
        """Test creating CLI consumer with custom options."""
        consumer = CLIProgressConsumer(show_percentage=False, show_count=False, title="Custom Title")
        assert consumer.show_percentage is False
        assert consumer.show_count is False
        assert consumer.title == "Custom Title"

    @patch("progress_tracker.cli_renderer.alive_bar")
    def test_on_progress_creates_bar(self, mock_alive_bar):
        """Test that on_progress creates progress bar."""
        mock_context = MagicMock()
        mock_bar = MagicMock()
        mock_bar.current = 0
        mock_context.__enter__ = Mock(return_value=mock_bar)
        mock_context.__exit__ = Mock()
        mock_alive_bar.return_value = mock_context

        consumer = CLIProgressConsumer()
        state = ProgressState(current=1, total=10, label="Test")
        update = ProgressUpdate(state, delta=1, update_type=UpdateType.STARTED)

        consumer.on_progress(update)

        mock_alive_bar.assert_called_once()
        mock_context.__enter__.assert_called_once()

    @patch("progress_tracker.cli_renderer.alive_bar")
    def test_on_progress_indeterminate(self, mock_alive_bar):
        """Test on_progress with indeterminate progress."""
        mock_context = MagicMock()
        mock_bar = MagicMock()
        mock_context.__enter__ = Mock(return_value=mock_bar)
        mock_context.__exit__ = Mock()
        mock_alive_bar.return_value = mock_context

        consumer = CLIProgressConsumer()
        state = ProgressState(current=5, total=None, label="Test")
        update = ProgressUpdate(state, delta=1, update_type=UpdateType.PROGRESS)

        consumer.on_progress(update)

        mock_alive_bar.assert_called_with(monitor=True, title="Test")

    @patch("progress_tracker.cli_renderer.alive_bar")
    def test_on_complete_closes_bar(self, mock_alive_bar):
        """Test that on_complete finalizes the bar."""
        mock_context = MagicMock()
        mock_bar = MagicMock()
        mock_bar.current = 5
        mock_context.__enter__ = Mock(return_value=mock_bar)
        mock_context.__exit__ = Mock()
        mock_alive_bar.return_value = mock_context

        consumer = CLIProgressConsumer()

        state = ProgressState(current=5, total=10, label="Test")
        update = ProgressUpdate(state, delta=1, update_type=UpdateType.PROGRESS)
        consumer.on_progress(update)

        final_state = ProgressState(current=10, total=10, label="Test")
        consumer.on_complete(final_state)

        mock_context.__exit__.assert_called()

    @patch("progress_tracker.cli_renderer.alive_bar")
    def test_total_change_recreates_bar(self, mock_alive_bar):
        """Test that changing total recreates the bar."""
        mock_context = MagicMock()
        mock_bar = MagicMock()
        mock_bar.current = 0
        mock_context.__enter__ = Mock(return_value=mock_bar)
        mock_context.__exit__ = Mock()
        mock_alive_bar.return_value = mock_context

        consumer = CLIProgressConsumer()

        state1 = ProgressState(current=1, total=10)
        update1 = ProgressUpdate(state1, delta=1, update_type=UpdateType.STARTED)
        consumer.on_progress(update1)
        assert mock_alive_bar.call_count == 1

        state2 = ProgressState(current=5, total=20)
        update2 = ProgressUpdate(state2, delta=1, update_type=UpdateType.TOTAL_CHANGED)
        consumer.on_progress(update2)
        assert mock_alive_bar.call_count == 2

    @patch("progress_tracker.cli_renderer.alive_bar")
    def test_custom_title_used(self, mock_alive_bar):
        """Test that custom title is used."""
        mock_context = MagicMock()
        mock_bar = MagicMock()
        mock_bar.current = 0
        mock_context.__enter__ = Mock(return_value=mock_bar)
        mock_context.__exit__ = Mock()
        mock_alive_bar.return_value = mock_context

        consumer = CLIProgressConsumer(title="Custom")
        state = ProgressState(current=1, total=10, label="Original")
        update = ProgressUpdate(state, delta=1, update_type=UpdateType.STARTED)

        consumer.on_progress(update)

        mock_alive_bar.assert_called_with(10, title="Custom")


class TestConsumerProtocolCompliance:
    """Test that all consumers implement the ProgressConsumer protocol."""

    def test_callback_consumer_has_required_methods(self):
        """Test CallbackProgressConsumer has required methods."""
        consumer = CallbackProgressConsumer(lambda c, t: None)
        assert hasattr(consumer, "on_progress")
        assert hasattr(consumer, "on_complete")
        assert callable(consumer.on_progress)
        assert callable(consumer.on_complete)

    def test_logging_consumer_has_required_methods(self):
        """Test LoggingProgressConsumer has required methods."""
        consumer = LoggingProgressConsumer()
        assert hasattr(consumer, "on_progress")
        assert hasattr(consumer, "on_complete")
        assert callable(consumer.on_progress)
        assert callable(consumer.on_complete)

    def test_cli_consumer_has_required_methods(self):
        """Test CLIProgressConsumer has required methods."""
        consumer = CLIProgressConsumer()
        assert hasattr(consumer, "on_progress")
        assert hasattr(consumer, "on_complete")
        assert callable(consumer.on_progress)
        assert callable(consumer.on_complete)
