"""Unit tests for progress_tracker.models."""

import pytest
import time
from anyfile_to_ai.progress_tracker.models import (
    ProgressState,
    ProgressUpdate,
    UpdateType,
    ProgressConsumer,
)


class TestProgressState:
    """Unit tests for ProgressState dataclass."""

    def test_create_with_required_fields(self):
        """Test ProgressState creation with only required fields."""
        state = ProgressState(current=5, total=10)
        assert state.current == 5
        assert state.total == 10
        assert state.label is None
        assert state.timestamp > 0
        assert state.metadata == {}

    def test_create_with_all_fields(self):
        """Test ProgressState creation with all fields."""
        metadata = {"file": "test.txt"}
        state = ProgressState(current=5, total=10, label="Test", timestamp=123.456, metadata=metadata)
        assert state.current == 5
        assert state.total == 10
        assert state.label == "Test"
        assert state.timestamp == 123.456
        assert state.metadata == metadata

    def test_frozen_dataclass(self):
        """Test that ProgressState is immutable."""
        state = ProgressState(current=5, total=10)
        with pytest.raises(AttributeError):
            state.current = 6

    def test_percentage_determinate(self):
        """Test percentage calculation with known total."""
        state = ProgressState(current=25, total=100)
        assert state.percentage == 25.0

        state = ProgressState(current=50, total=200)
        assert state.percentage == 25.0

        state = ProgressState(current=0, total=100)
        assert state.percentage == 0.0

        state = ProgressState(current=100, total=100)
        assert state.percentage == 100.0

    def test_percentage_indeterminate(self):
        """Test percentage is None when total is None."""
        state = ProgressState(current=5, total=None)
        assert state.percentage is None

    def test_percentage_zero_total(self):
        """Test percentage is None when total is 0."""
        state = ProgressState(current=0, total=0)
        assert state.percentage is None

    def test_is_complete_true(self):
        """Test is_complete when current equals total."""
        state = ProgressState(current=100, total=100)
        assert state.is_complete is True

    def test_is_complete_false(self):
        """Test is_complete when current is less than total."""
        state = ProgressState(current=50, total=100)
        assert state.is_complete is False

    def test_is_complete_indeterminate(self):
        """Test is_complete is False when total is None."""
        state = ProgressState(current=50, total=None)
        assert state.is_complete is False

    def test_is_indeterminate_true(self):
        """Test is_indeterminate when total is None."""
        state = ProgressState(current=5, total=None)
        assert state.is_indeterminate is True

    def test_is_indeterminate_false(self):
        """Test is_indeterminate when total is set."""
        state = ProgressState(current=5, total=10)
        assert state.is_indeterminate is False

    def test_items_remaining_determinate(self):
        """Test items_remaining calculation."""
        state = ProgressState(current=30, total=100)
        assert state.items_remaining == 70

        state = ProgressState(current=100, total=100)
        assert state.items_remaining == 0

    def test_items_remaining_indeterminate(self):
        """Test items_remaining is None when total is None."""
        state = ProgressState(current=50, total=None)
        assert state.items_remaining is None

    def test_validation_negative_current(self):
        """Test that negative current raises ValueError."""
        with pytest.raises(ValueError, match="current must be non-negative"):
            ProgressState(current=-1, total=10)

    def test_validation_current_exceeds_total(self):
        """Test that current > total raises ValueError."""
        with pytest.raises(ValueError, match="current cannot exceed total"):
            ProgressState(current=11, total=10)

    def test_validation_label_too_long(self):
        """Test that label > 100 chars raises ValueError."""
        long_label = "x" * 101
        with pytest.raises(ValueError, match="label too long"):
            ProgressState(current=5, total=10, label=long_label)

    def test_validation_label_max_length_ok(self):
        """Test that label of exactly 100 chars is accepted."""
        max_label = "x" * 100
        state = ProgressState(current=5, total=10, label=max_label)
        assert len(state.label) == 100

    def test_default_timestamp(self):
        """Test that timestamp defaults to current time."""
        before = time.monotonic()
        state = ProgressState(current=5, total=10)
        after = time.monotonic()
        assert before <= state.timestamp <= after

    def test_custom_metadata(self):
        """Test custom metadata storage."""
        metadata = {"file": "test.pdf", "phase": "extraction", "count": 42}
        state = ProgressState(current=5, total=10, metadata=metadata)
        assert state.metadata == metadata
        assert state.metadata["file"] == "test.pdf"
        assert state.metadata["count"] == 42


class TestProgressUpdate:
    """Unit tests for ProgressUpdate dataclass."""

    def test_create_progress_update(self):
        """Test ProgressUpdate creation."""
        state = ProgressState(current=5, total=10)
        update = ProgressUpdate(state=state, delta=1, update_type=UpdateType.PROGRESS)
        assert update.state == state
        assert update.delta == 1
        assert update.update_type == UpdateType.PROGRESS

    def test_frozen_dataclass(self):
        """Test that ProgressUpdate is immutable."""
        state = ProgressState(current=5, total=10)
        update = ProgressUpdate(state=state, delta=1, update_type=UpdateType.PROGRESS)
        with pytest.raises(AttributeError):
            update.delta = 2

    def test_negative_delta(self):
        """Test that negative delta is allowed (for total changes)."""
        state = ProgressState(current=5, total=10)
        update = ProgressUpdate(state=state, delta=-1, update_type=UpdateType.TOTAL_CHANGED)
        assert update.delta == -1


class TestUpdateType:
    """Unit tests for UpdateType enum."""

    def test_has_all_values(self):
        """Test that UpdateType has all required values."""
        assert hasattr(UpdateType, "STARTED")
        assert hasattr(UpdateType, "PROGRESS")
        assert hasattr(UpdateType, "TOTAL_CHANGED")
        assert hasattr(UpdateType, "COMPLETED")
        assert hasattr(UpdateType, "ERROR")

    def test_enum_values(self):
        """Test UpdateType enum string values."""
        assert UpdateType.STARTED.value == "started"
        assert UpdateType.PROGRESS.value == "progress"
        assert UpdateType.TOTAL_CHANGED.value == "total_changed"
        assert UpdateType.COMPLETED.value == "completed"
        assert UpdateType.ERROR.value == "error"


class TestProgressConsumer:
    """Unit tests for ProgressConsumer protocol."""

    def test_consumer_protocol_structure(self):
        """Test that ProgressConsumer is a Protocol."""
        assert hasattr(ProgressConsumer, "__protocol_attrs__")

    def test_consumer_has_on_progress(self):
        """Test that protocol defines on_progress method."""

        class TestConsumer:
            def on_progress(self, update: ProgressUpdate) -> None:
                pass

            def on_complete(self, state: ProgressState) -> None:
                pass

        assert isinstance(TestConsumer(), ProgressConsumer)

    def test_consumer_has_on_complete(self):
        """Test that protocol defines on_complete method."""

        class TestConsumer:
            def on_progress(self, update: ProgressUpdate) -> None:
                pass

            def on_complete(self, state: ProgressState) -> None:
                pass

        consumer = TestConsumer()
        assert hasattr(consumer, "on_complete")

    def test_incomplete_consumer_not_protocol_compliant(self):
        """Test that missing methods fails protocol check."""

        class IncompleteConsumer:
            def on_progress(self, update: ProgressUpdate) -> None:
                pass

        assert not isinstance(IncompleteConsumer(), ProgressConsumer)
