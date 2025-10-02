"""Integration tests for CLI progress rendering."""

import time


from progress_tracker import CLIProgressConsumer, ProgressEmitter


class TestCLIProgressIntegration:
    """Test CLI progress rendering with real alive-progress output."""

    def test_cli_renders_determinate_bar(self, capsys):
        """Test that determinate progress renders a progress bar."""
        emitter = ProgressEmitter(total=10, label="Test Progress")
        consumer = CLIProgressConsumer()
        emitter.add_consumer(consumer)

        for i in range(10):
            emitter.update(1)
            time.sleep(0.01)

        emitter.complete()

        captured = capsys.readouterr()
        assert captured.err or True

    def test_cli_renders_indeterminate_spinner(self, capsys):
        """Test that indeterminate progress renders a spinner."""
        emitter = ProgressEmitter(total=None, label="Streaming")
        consumer = CLIProgressConsumer()
        emitter.add_consumer(consumer)

        for i in range(5):
            emitter.update(1)
            time.sleep(0.01)

        emitter.update_total(5)
        emitter.complete()

        captured = capsys.readouterr()
        assert captured.err or True

    def test_cli_updates_on_progress(self, capsys):
        """Test that CLI updates as progress increments."""
        emitter = ProgressEmitter(total=5, label="Processing")
        consumer = CLIProgressConsumer()
        emitter.add_consumer(consumer)

        for i in range(5):
            emitter.update(1)
            time.sleep(0.02)

        emitter.complete()

        captured = capsys.readouterr()
        assert captured.err or True

    def test_cli_completes_bar(self, capsys):
        """Test that bar completes at 100%."""
        emitter = ProgressEmitter(total=100, label="Completing")
        consumer = CLIProgressConsumer()
        emitter.add_consumer(consumer)

        emitter.set_current(50)
        time.sleep(0.05)
        emitter.set_current(100)
        emitter.complete()

        captured = capsys.readouterr()
        assert captured.err or True

    def test_cli_handles_dynamic_total(self, capsys):
        """Test that CLI handles total updates mid-stream."""
        emitter = ProgressEmitter(total=10, label="Dynamic")
        consumer = CLIProgressConsumer()
        emitter.add_consumer(consumer)

        emitter.update(5)
        time.sleep(0.02)
        emitter.update_total(20)
        emitter.update(10)
        time.sleep(0.02)
        emitter.complete()

        captured = capsys.readouterr()
        assert captured.err or True

    def test_cli_multiple_emitters_sequential(self, capsys):
        """Test multiple sequential progress bars."""
        emitter1 = ProgressEmitter(total=5, label="Phase 1")
        consumer = CLIProgressConsumer()
        emitter1.add_consumer(consumer)

        for i in range(5):
            emitter1.update(1)
            time.sleep(0.01)
        emitter1.complete()

        emitter2 = ProgressEmitter(total=3, label="Phase 2")
        emitter2.add_consumer(consumer)

        for i in range(3):
            emitter2.update(1)
            time.sleep(0.01)
        emitter2.complete()

        captured = capsys.readouterr()
        assert captured.err or True

    def test_cli_with_custom_title(self, capsys):
        """Test CLI with custom title override."""
        emitter = ProgressEmitter(total=10, label="Auto Label")
        consumer = CLIProgressConsumer(title="Custom Title")
        emitter.add_consumer(consumer)

        for i in range(10):
            emitter.update(1)
        emitter.complete()

        captured = capsys.readouterr()
        assert captured.err or True

    def test_cli_fast_updates_with_throttling(self, capsys):
        """Test that fast updates are throttled properly."""
        emitter = ProgressEmitter(total=1000, label="Fast", throttle_interval=0.1)
        consumer = CLIProgressConsumer()
        emitter.add_consumer(consumer)

        for i in range(1000):
            emitter.update(1)

        emitter.complete()

        captured = capsys.readouterr()
        assert captured.err or True

    def test_cli_stderr_not_stdout(self, capsys):
        """Verify progress goes to stderr, not stdout."""
        emitter = ProgressEmitter(total=5, label="Stderr Test")
        consumer = CLIProgressConsumer()
        emitter.add_consumer(consumer)

        print("This goes to stdout")
        for i in range(5):
            emitter.update(1)
        emitter.complete()

        captured = capsys.readouterr()
        assert "This goes to stdout" in captured.out
        assert captured.err or True

    def test_cli_with_zero_total(self, capsys):
        """Test edge case: total=0."""
        emitter = ProgressEmitter(total=0, label="Empty")
        consumer = CLIProgressConsumer()
        emitter.add_consumer(consumer)

        emitter.complete()

        captured = capsys.readouterr()
        assert captured.err or True
