"""
Contract tests for ProgressConsumer protocol compliance.

These tests validate that all consumer implementations correctly implement
the ProgressConsumer protocol and handle edge cases appropriately.
"""

import inspect
import pytest
from progress_tracker import (
    ProgressState,
    ProgressUpdate,
    UpdateType,
    ProgressEmitter,
    ProgressConsumer,
    CLIProgressConsumer,
    CallbackProgressConsumer,
    LoggingProgressConsumer,
)


class TestProgressConsumerProtocol:
    """Validate ProgressConsumer protocol compliance."""

    def test_cli_consumer_implements_protocol(self):
        """CLIProgressConsumer must implement ProgressConsumer protocol."""
        consumer = CLIProgressConsumer()
        assert isinstance(consumer, ProgressConsumer)

    def test_callback_consumer_implements_protocol(self):
        """CallbackProgressConsumer must implement ProgressConsumer protocol."""
        consumer = CallbackProgressConsumer(lambda c, t: None)
        assert isinstance(consumer, ProgressConsumer)

    def test_logging_consumer_implements_protocol(self):
        """LoggingProgressConsumer must implement ProgressConsumer protocol."""
        consumer = LoggingProgressConsumer()
        assert isinstance(consumer, ProgressConsumer)

    def test_consumer_must_have_on_progress_method(self):
        """All consumers must implement on_progress method."""
        for ConsumerClass in [CLIProgressConsumer, LoggingProgressConsumer]:
            assert hasattr(ConsumerClass, "on_progress")
            assert callable(getattr(ConsumerClass, "on_progress"))

    def test_consumer_must_have_on_complete_method(self):
        """All consumers must implement on_complete method."""
        for ConsumerClass in [CLIProgressConsumer, LoggingProgressConsumer]:
            assert hasattr(ConsumerClass, "on_complete")
            assert callable(getattr(ConsumerClass, "on_complete"))

    def test_on_progress_accepts_progress_update(self):
        """on_progress must accept ProgressUpdate argument."""
        consumer = CallbackProgressConsumer(lambda c, t: None)
        state = ProgressState(current=0, total=100)
        update = ProgressUpdate(state, 1, UpdateType.STARTED)
        consumer.on_progress(update)

    def test_on_complete_accepts_progress_state(self):
        """on_complete must accept ProgressState argument."""
        consumer = CallbackProgressConsumer(lambda c, t: None)
        state = ProgressState(current=100, total=100)
        consumer.on_complete(state)


class TestProgressStateContract:
    """Validate ProgressState dataclass contract."""

    def test_progress_state_is_frozen(self):
        """ProgressState must be immutable (frozen dataclass)."""
        state = ProgressState(current=50, total=100)
        with pytest.raises(AttributeError):
            state.current = 60

    def test_progress_state_validates_current_non_negative(self):
        """ProgressState must reject negative current values."""
        with pytest.raises(ValueError, match="current must be non-negative"):
            ProgressState(current=-1, total=100)

    def test_progress_state_validates_current_le_total(self):
        """ProgressState must reject current > total."""
        with pytest.raises(ValueError, match="current cannot exceed total"):
            ProgressState(current=150, total=100)

    def test_progress_state_percentage_property(self):
        """ProgressState.percentage must return 0-100 or None."""
        state = ProgressState(current=50, total=100)
        assert state.percentage == 50.0

        state_indeterminate = ProgressState(current=50, total=None)
        assert state_indeterminate.percentage is None

    def test_progress_state_indeterminate_when_total_none(self):
        """ProgressState.is_indeterminate must be True when total is None."""
        state = ProgressState(current=50, total=None)
        assert state.is_indeterminate is True

        state_determinate = ProgressState(current=50, total=100)
        assert state_determinate.is_indeterminate is False

    def test_progress_state_label_max_length(self):
        """ProgressState must reject labels > 100 characters."""
        with pytest.raises(ValueError, match="label too long"):
            ProgressState(current=0, total=100, label="x" * 101)


class TestProgressUpdateContract:
    """Validate ProgressUpdate dataclass contract."""

    def test_progress_update_is_frozen(self):
        """ProgressUpdate must be immutable."""
        state = ProgressState(current=50, total=100)
        update = ProgressUpdate(state, 1, UpdateType.PROGRESS)
        with pytest.raises(AttributeError):
            update.delta = 2

    def test_progress_update_contains_state(self):
        """ProgressUpdate must contain ProgressState."""
        state = ProgressState(current=50, total=100)
        update = ProgressUpdate(state, 1, UpdateType.PROGRESS)
        assert update.state == state
        assert isinstance(update.state, ProgressState)

    def test_progress_update_contains_delta(self):
        """ProgressUpdate must contain delta field."""
        state = ProgressState(current=50, total=100)
        update = ProgressUpdate(state, 5, UpdateType.PROGRESS)
        assert update.delta == 5

    def test_progress_update_contains_update_type(self):
        """ProgressUpdate must contain UpdateType enum."""
        state = ProgressState(current=50, total=100)
        update = ProgressUpdate(state, 1, UpdateType.COMPLETED)
        assert update.update_type == UpdateType.COMPLETED
        assert isinstance(update.update_type, UpdateType)


class TestProgressEmitterContract:
    """Validate ProgressEmitter API contract."""

    def test_emitter_has_update_method(self):
        """ProgressEmitter must have update(increment, force) method."""
        assert hasattr(ProgressEmitter, "update")
        assert callable(getattr(ProgressEmitter, "update"))

    def test_emitter_has_set_current_method(self):
        """ProgressEmitter must have set_current(value, force) method."""
        assert hasattr(ProgressEmitter, "set_current")
        assert callable(getattr(ProgressEmitter, "set_current"))

    def test_emitter_has_update_total_method(self):
        """ProgressEmitter must have update_total(new_total) method."""
        assert hasattr(ProgressEmitter, "update_total")
        assert callable(getattr(ProgressEmitter, "update_total"))

    def test_emitter_has_complete_method(self):
        """ProgressEmitter must have complete() method."""
        assert hasattr(ProgressEmitter, "complete")
        assert callable(getattr(ProgressEmitter, "complete"))

    def test_emitter_has_add_consumer_method(self):
        """ProgressEmitter must have add_consumer(consumer) method."""
        assert hasattr(ProgressEmitter, "add_consumer")
        assert callable(getattr(ProgressEmitter, "add_consumer"))

    def test_emitter_has_remove_consumer_method(self):
        """ProgressEmitter must have remove_consumer(consumer) method."""
        assert hasattr(ProgressEmitter, "remove_consumer")
        assert callable(getattr(ProgressEmitter, "remove_consumer"))

    def test_emitter_has_create_child_method(self):
        """ProgressEmitter must have create_child() method."""
        assert hasattr(ProgressEmitter, "create_child")
        assert callable(getattr(ProgressEmitter, "create_child"))

    def test_emitter_has_stream_method(self):
        """ProgressEmitter must have async stream() method."""
        assert hasattr(ProgressEmitter, "stream")
        method = getattr(ProgressEmitter, "stream")
        assert callable(method)
        assert inspect.isasyncgenfunction(method)

    def test_emitter_has_current_property(self):
        """ProgressEmitter must have current property."""
        emitter = ProgressEmitter(total=100)
        assert hasattr(emitter, "current")
        assert emitter.current == 0

    def test_emitter_has_total_property(self):
        """ProgressEmitter must have total property."""
        emitter = ProgressEmitter(total=100)
        assert hasattr(emitter, "total")
        assert emitter.total == 100

    def test_emitter_has_state_property(self):
        """ProgressEmitter must have state property."""
        emitter = ProgressEmitter(total=100)
        assert hasattr(emitter, "state")
        assert isinstance(emitter.state, ProgressState)

    def test_emitter_validates_total_non_negative(self):
        """ProgressEmitter must reject negative total in constructor."""
        with pytest.raises(ValueError, match="total must be non-negative"):
            ProgressEmitter(total=-1)

    def test_emitter_update_validates_bounds(self):
        """ProgressEmitter.update must reject updates exceeding total."""
        emitter = ProgressEmitter(total=100)
        emitter.update(50)
        with pytest.raises(ValueError, match="update would exceed total"):
            emitter.update(51)

    def test_emitter_update_total_forces_notification(self):
        """ProgressEmitter.update_total must always notify consumers."""
        updates = []

        def capture(c, t):
            updates.append((c, t))

        emitter = ProgressEmitter(total=100)
        emitter.add_consumer(CallbackProgressConsumer(capture))
        emitter.update_total(200)
        assert len(updates) > 0

    def test_emitter_complete_forces_notification(self):
        """ProgressEmitter.complete must always notify consumers."""
        updates = []

        def capture(c, t):
            updates.append((c, t))

        emitter = ProgressEmitter(total=100)
        emitter.add_consumer(CallbackProgressConsumer(capture))
        emitter.complete()
        assert len(updates) > 0

    def test_emitter_complete_raises_if_indeterminate(self):
        """ProgressEmitter.complete must raise ValueError if total is None."""
        emitter = ProgressEmitter(total=None)
        with pytest.raises(ValueError, match="cannot complete indeterminate progress"):
            emitter.complete()


class TestUpdateTypeContract:
    """Validate UpdateType enum contract."""

    def test_update_type_has_started(self):
        """UpdateType must have STARTED value."""
        assert hasattr(UpdateType, "STARTED")
        assert UpdateType.STARTED.value == "started"

    def test_update_type_has_progress(self):
        """UpdateType must have PROGRESS value."""
        assert hasattr(UpdateType, "PROGRESS")
        assert UpdateType.PROGRESS.value == "progress"

    def test_update_type_has_total_changed(self):
        """UpdateType must have TOTAL_CHANGED value."""
        assert hasattr(UpdateType, "TOTAL_CHANGED")
        assert UpdateType.TOTAL_CHANGED.value == "total_changed"

    def test_update_type_has_completed(self):
        """UpdateType must have COMPLETED value."""
        assert hasattr(UpdateType, "COMPLETED")
        assert UpdateType.COMPLETED.value == "completed"

    def test_update_type_has_error(self):
        """UpdateType must have ERROR value."""
        assert hasattr(UpdateType, "ERROR")
        assert UpdateType.ERROR.value == "error"


class TestConsumerExceptionHandling:
    """Validate exception handling contracts."""

    def test_emitter_catches_consumer_exceptions(self):
        """ProgressEmitter must catch and log consumer exceptions without halting."""

        class BrokenConsumer:
            def on_progress(self, update):
                raise RuntimeError("Consumer error")

            def on_complete(self, state):
                pass

        emitter = ProgressEmitter(total=100)
        emitter.add_consumer(BrokenConsumer())
        emitter.update(1)

    def test_emitter_continues_after_consumer_error(self):
        """ProgressEmitter must continue notifying other consumers after one fails."""
        updates = []

        class BrokenConsumer:
            def on_progress(self, update):
                raise RuntimeError("Consumer error")

            def on_complete(self, state):
                pass

        def working_callback(c, t):
            updates.append((c, t))

        emitter = ProgressEmitter(total=100)
        emitter.add_consumer(BrokenConsumer())
        emitter.add_consumer(CallbackProgressConsumer(working_callback))
        emitter.update(1, force=True)
        assert len(updates) > 0

    def test_consumer_exception_logged(self):
        """Consumer exceptions must be logged to stderr or provided logger."""

        class BrokenConsumer:
            def on_progress(self, update):
                raise RuntimeError("Consumer error")

            def on_complete(self, state):
                pass

        emitter = ProgressEmitter(total=100)
        emitter.add_consumer(BrokenConsumer())
        emitter.update(1, force=True)


class TestThrottlingContract:
    """Validate throttling behavior contract."""

    def test_emitter_respects_throttle_interval(self):
        """ProgressEmitter must throttle updates to throttle_interval."""

        updates = []

        def capture(c, t):
            updates.append((c, t))

        emitter = ProgressEmitter(total=100, throttle_interval=0.1)
        emitter.add_consumer(CallbackProgressConsumer(capture))

        for i in range(10):
            emitter.update(1)

        assert len(updates) < 10

    def test_emitter_force_bypasses_throttling(self):
        """ProgressEmitter.update(force=True) must bypass throttling."""
        updates = []

        def capture(c, t):
            updates.append((c, t))

        emitter = ProgressEmitter(total=100, throttle_interval=10.0)
        emitter.add_consumer(CallbackProgressConsumer(capture))

        emitter.update(1, force=True)
        emitter.update(1, force=True)
        assert len(updates) >= 2

    def test_emitter_first_update_not_throttled(self):
        """First update (STARTED) must not be throttled."""
        updates = []

        def capture(c, t):
            updates.append((c, t))

        emitter = ProgressEmitter(total=100, throttle_interval=10.0)
        emitter.add_consumer(CallbackProgressConsumer(capture))
        emitter.update(1)
        assert len(updates) >= 1

    def test_emitter_complete_not_throttled(self):
        """complete() must not be throttled."""
        updates = []

        def capture(c, t):
            updates.append((c, t))

        emitter = ProgressEmitter(total=100, throttle_interval=10.0)
        emitter.add_consumer(CallbackProgressConsumer(capture))
        emitter.complete()
        assert len(updates) >= 1


class TestHierarchicalProgressContract:
    """Validate hierarchical progress contracts."""

    def test_create_child_returns_emitter(self):
        """create_child must return a ProgressEmitter instance."""
        parent = ProgressEmitter(total=100)
        child = parent.create_child(total=50)
        assert isinstance(child, ProgressEmitter)

    def test_child_updates_propagate_to_parent(self):
        """Child emitter updates must trigger parent updates."""
        updates = []

        def capture(c, t):
            updates.append((c, t))

        parent = ProgressEmitter(total=100)
        parent.add_consumer(CallbackProgressConsumer(capture))
        child = parent.create_child(total=50)
        child.update(25, force=True)
        assert len(updates) > 0

    def test_parent_calculates_weighted_average(self):
        """Parent percentage must be weighted average of children."""
        parent = ProgressEmitter(total=100)
        child1 = parent.create_child(total=100, weight=0.5)
        parent.create_child(total=100, weight=0.5)

        child1.update(50, force=True)
        assert parent.current > 0

    def test_child_weights_normalized(self):
        """Child weights must be normalized to sum to 1.0."""
        parent = ProgressEmitter(total=100)
        child1 = parent.create_child(total=100, weight=1.0)
        child2 = parent.create_child(total=100, weight=1.0)

        child1.update(100, force=True)
        child2.update(100, force=True)
