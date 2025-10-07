"""Unit tests for progress_tracker.emitter.ProgressEmitter."""

import asyncio
import pytest
import time
from anything_to_ai.progress_tracker.emitter import ProgressEmitter
from anything_to_ai.progress_tracker.models import (
    ProgressState,
    ProgressUpdate,
    UpdateType,
)


class MockConsumer:
    """Mock consumer for testing."""

    def __init__(self):
        self.updates = []
        self.completions = []

    def on_progress(self, update: ProgressUpdate) -> None:
        self.updates.append(update)

    def on_complete(self, state: ProgressState) -> None:
        self.completions.append(state)


class TestProgressEmitterCreation:
    """Test ProgressEmitter initialization."""

    def test_create_with_total(self):
        """Test creating emitter with known total."""
        emitter = ProgressEmitter(total=100, label="Test")
        assert emitter.current == 0
        assert emitter.total == 100
        assert emitter.state.label == "Test"

    def test_create_indeterminate(self):
        """Test creating emitter with unknown total."""
        emitter = ProgressEmitter(total=None)
        assert emitter.current == 0
        assert emitter.total is None
        assert emitter.state.is_indeterminate is True

    def test_create_with_custom_throttle(self):
        """Test creating emitter with custom throttle interval."""
        emitter = ProgressEmitter(total=100, throttle_interval=0.5)
        assert emitter._throttle_interval == 0.5

    def test_create_rejects_negative_total(self):
        """Test that negative total raises ValueError."""
        with pytest.raises(ValueError, match="total must be non-negative"):
            ProgressEmitter(total=-1)


class TestProgressEmitterUpdate:
    """Test ProgressEmitter.update() method."""

    def test_update_increments_current(self):
        """Test that update increments current."""
        emitter = ProgressEmitter(total=10)
        emitter.update(1)
        assert emitter.current == 1
        emitter.update(2)
        assert emitter.current == 3

    def test_update_default_increment(self):
        """Test that update defaults to increment of 1."""
        emitter = ProgressEmitter(total=10)
        emitter.update()
        assert emitter.current == 1

    def test_update_notifies_consumers(self):
        """Test that update notifies consumers."""
        emitter = ProgressEmitter(total=10)
        consumer = MockConsumer()
        emitter.add_consumer(consumer)

        emitter.update(1, force=True)
        assert len(consumer.updates) == 1
        assert consumer.updates[0].state.current == 1
        assert consumer.updates[0].delta == 1

    def test_update_exceeding_total_raises(self):
        """Test that update exceeding total raises ValueError."""
        emitter = ProgressEmitter(total=10)
        emitter.update(5)
        with pytest.raises(ValueError, match="update would exceed total"):
            emitter.update(6)

    def test_update_negative_increment_raises(self):
        """Test that negative increment resulting in negative current raises."""
        emitter = ProgressEmitter(total=10)
        emitter.update(5)
        with pytest.raises(ValueError, match="update would make current negative"):
            emitter.update(-10)

    def test_first_update_is_started(self):
        """Test that first update has STARTED type."""
        emitter = ProgressEmitter(total=10)
        consumer = MockConsumer()
        emitter.add_consumer(consumer)

        emitter.update(1)
        assert consumer.updates[0].update_type == UpdateType.STARTED

    def test_subsequent_updates_are_progress(self):
        """Test that subsequent updates have PROGRESS type."""
        emitter = ProgressEmitter(total=10)
        consumer = MockConsumer()
        emitter.add_consumer(consumer)

        emitter.update(1)
        emitter.update(1, force=True)
        assert consumer.updates[1].update_type == UpdateType.PROGRESS


class TestProgressEmitterSetCurrent:
    """Test ProgressEmitter.set_current() method."""

    def test_set_current_absolute_value(self):
        """Test setting current to absolute value."""
        emitter = ProgressEmitter(total=100)
        emitter.set_current(50, force=True)
        assert emitter.current == 50

    def test_set_current_calculates_delta(self):
        """Test that set_current calculates correct delta."""
        emitter = ProgressEmitter(total=100)
        consumer = MockConsumer()
        emitter.add_consumer(consumer)

        emitter.set_current(30, force=True)
        assert consumer.updates[0].delta == 30

        emitter.set_current(50, force=True)
        assert consumer.updates[1].delta == 20

    def test_set_current_rejects_negative(self):
        """Test that set_current rejects negative values."""
        emitter = ProgressEmitter(total=100)
        with pytest.raises(ValueError, match="value must be non-negative"):
            emitter.set_current(-1)

    def test_set_current_rejects_exceeding_total(self):
        """Test that set_current rejects values exceeding total."""
        emitter = ProgressEmitter(total=100)
        with pytest.raises(ValueError, match="value cannot exceed total"):
            emitter.set_current(101)


class TestProgressEmitterUpdateTotal:
    """Test ProgressEmitter.update_total() method."""

    def test_update_total_changes_total(self):
        """Test that update_total changes the total."""
        emitter = ProgressEmitter(total=100)
        emitter.update_total(200)
        assert emitter.total == 200

    def test_update_total_to_none(self):
        """Test changing to indeterminate progress."""
        emitter = ProgressEmitter(total=100)
        emitter.update(50)
        emitter.update_total(None)
        assert emitter.total is None
        assert emitter.state.is_indeterminate is True

    def test_update_total_forces_notification(self):
        """Test that update_total always notifies consumers."""
        emitter = ProgressEmitter(total=100, throttle_interval=999)
        consumer = MockConsumer()
        emitter.add_consumer(consumer)

        emitter.update_total(200)
        assert len(consumer.updates) == 1
        assert consumer.updates[0].update_type == UpdateType.TOTAL_CHANGED

    def test_update_total_rejects_less_than_current(self):
        """Test that update_total rejects values less than current."""
        emitter = ProgressEmitter(total=100)
        emitter.update(50)
        with pytest.raises(ValueError, match="new total cannot be less than current"):
            emitter.update_total(30)


class TestProgressEmitterComplete:
    """Test ProgressEmitter.complete() method."""

    def test_complete_sets_current_to_total(self):
        """Test that complete sets current to total."""
        emitter = ProgressEmitter(total=100)
        emitter.update(50)
        emitter.complete()
        assert emitter.current == 100

    def test_complete_notifies_consumers(self):
        """Test that complete notifies consumers."""
        emitter = ProgressEmitter(total=100)
        consumer = MockConsumer()
        emitter.add_consumer(consumer)

        emitter.complete()
        assert len(consumer.updates) == 1
        assert consumer.updates[0].update_type == UpdateType.COMPLETED
        assert len(consumer.completions) == 1

    def test_complete_raises_if_indeterminate(self):
        """Test that complete raises ValueError if total is None."""
        emitter = ProgressEmitter(total=None)
        with pytest.raises(ValueError, match="cannot complete indeterminate progress"):
            emitter.complete()

    def test_complete_forces_notification(self):
        """Test that complete always notifies regardless of throttling."""
        emitter = ProgressEmitter(total=100, throttle_interval=999)
        consumer = MockConsumer()
        emitter.add_consumer(consumer)

        emitter.complete()
        assert len(consumer.updates) == 1


class TestProgressEmitterConsumers:
    """Test consumer management."""

    def test_add_consumer(self):
        """Test adding consumers."""
        emitter = ProgressEmitter(total=10)
        consumer1 = MockConsumer()
        consumer2 = MockConsumer()

        emitter.add_consumer(consumer1)
        emitter.add_consumer(consumer2)

        emitter.update(1, force=True)
        assert len(consumer1.updates) == 1
        assert len(consumer2.updates) == 1

    def test_remove_consumer(self):
        """Test removing consumers."""
        emitter = ProgressEmitter(total=10)
        consumer = MockConsumer()

        emitter.add_consumer(consumer)
        emitter.update(1, force=True)
        assert len(consumer.updates) == 1

        emitter.remove_consumer(consumer)
        emitter.update(1, force=True)
        assert len(consumer.updates) == 1

    def test_remove_nonexistent_consumer(self):
        """Test that removing non-existent consumer doesn't error."""
        emitter = ProgressEmitter(total=10)
        consumer = MockConsumer()
        emitter.remove_consumer(consumer)


class TestProgressEmitterThrottling:
    """Test throttling behavior."""

    def test_throttling_limits_updates(self):
        """Test that throttling limits update frequency."""
        emitter = ProgressEmitter(total=100, throttle_interval=0.1)
        consumer = MockConsumer()
        emitter.add_consumer(consumer)

        emitter.update(1)
        initial_count = len(consumer.updates)

        emitter.update(1)
        emitter.update(1)
        emitter.update(1)

        assert len(consumer.updates) == initial_count

    def test_force_bypasses_throttling(self):
        """Test that force=True bypasses throttling."""
        emitter = ProgressEmitter(total=100, throttle_interval=999)
        consumer = MockConsumer()
        emitter.add_consumer(consumer)

        emitter.update(1, force=True)
        emitter.update(1, force=True)
        emitter.update(1, force=True)

        assert len(consumer.updates) == 3

    def test_throttling_with_time_delay(self):
        """Test that updates after throttle interval are sent."""
        emitter = ProgressEmitter(total=100, throttle_interval=0.05)
        consumer = MockConsumer()
        emitter.add_consumer(consumer)

        emitter.update(1)
        time.sleep(0.06)
        emitter.update(1)

        assert len(consumer.updates) >= 1


class TestProgressEmitterExceptionHandling:
    """Test exception handling in consumers."""

    def test_consumer_exception_caught(self):
        """Test that consumer exceptions are caught."""
        emitter = ProgressEmitter(total=10)

        class ErrorConsumer:
            def on_progress(self, update):
                raise RuntimeError("Test error")

            def on_complete(self, state):
                pass

        emitter.add_consumer(ErrorConsumer())
        emitter.update(1, force=True)

    def test_exception_continues_to_other_consumers(self):
        """Test that exception in one consumer doesn't affect others."""
        emitter = ProgressEmitter(total=10)

        class ErrorConsumer:
            def on_progress(self, update):
                raise RuntimeError("Test error")

            def on_complete(self, state):
                pass

        good_consumer = MockConsumer()
        emitter.add_consumer(ErrorConsumer())
        emitter.add_consumer(good_consumer)

        emitter.update(1, force=True)
        assert len(good_consumer.updates) == 1


class TestProgressEmitterHierarchical:
    """Test hierarchical progress."""

    def test_create_child(self):
        """Test creating child emitter."""
        parent = ProgressEmitter(total=100)
        child = parent.create_child(total=50, weight=1.0, label="Child")

        assert child.total == 50
        assert child.state.label == "Child"

    def test_create_child_rejects_zero_weight(self):
        """Test that create_child rejects zero or negative weight."""
        parent = ProgressEmitter(total=100)
        with pytest.raises(ValueError, match="weight must be positive"):
            parent.create_child(total=50, weight=0)

    def test_child_updates_propagate_to_parent(self):
        """Test that child updates trigger parent updates."""
        parent = ProgressEmitter(total=100)
        consumer = MockConsumer()
        parent.add_consumer(consumer)

        child = parent.create_child(total=50, weight=1.0)
        child.update(25, force=True)

        assert parent.current > 0

    def test_weighted_average_calculation(self):
        """Test parent calculates weighted average of children."""
        parent = ProgressEmitter(total=100)
        consumer = MockConsumer()
        parent.add_consumer(consumer)

        child1 = parent.create_child(total=100, weight=0.4)
        child2 = parent.create_child(total=100, weight=0.6)

        child1.set_current(50, force=True)
        assert parent.current == 20

        child2.set_current(100, force=True)
        assert parent.current == 80


class TestProgressEmitterAsyncStreaming:
    """Test async streaming functionality."""

    def test_stream_yields_updates(self):
        """Test that stream yields progress updates."""

        async def run_test():
            emitter = ProgressEmitter(total=3)

            async def producer():
                await asyncio.sleep(0.01)
                emitter.update(1)
                await asyncio.sleep(0.01)
                emitter.update(1)
                await asyncio.sleep(0.01)
                emitter.complete()

            updates = []

            async def consumer():
                async for update in emitter.stream():
                    updates.append(update)

            await asyncio.gather(producer(), consumer())

            assert len(updates) > 0
            assert updates[-1].update_type == UpdateType.COMPLETED

        asyncio.run(run_test())

    def test_stream_completes(self):
        """Test that stream completes when progress completes."""

        async def run_test():
            emitter = ProgressEmitter(total=1)

            async def producer():
                await asyncio.sleep(0.01)
                emitter.complete()

            stream_completed = False

            async def consumer():
                nonlocal stream_completed
                async for update in emitter.stream():
                    pass
                stream_completed = True

            await asyncio.gather(producer(), consumer())
            assert stream_completed is True

        asyncio.run(run_test())


class TestProgressEmitterProperties:
    """Test property accessors."""

    def test_current_property(self):
        """Test current property is read-only."""
        emitter = ProgressEmitter(total=10)
        emitter.update(5)
        assert emitter.current == 5

    def test_total_property(self):
        """Test total property is read-only."""
        emitter = ProgressEmitter(total=100)
        assert emitter.total == 100

    def test_state_property(self):
        """Test state property returns ProgressState."""
        emitter = ProgressEmitter(total=100, label="Test")
        emitter.update(50)

        state = emitter.state
        assert isinstance(state, ProgressState)
        assert state.current == 50
        assert state.total == 100
        assert state.label == "Test"

    def test_state_property_is_snapshot(self):
        """Test that state property returns a snapshot."""
        emitter = ProgressEmitter(total=100)
        state1 = emitter.state
        emitter.update(50)
        state2 = emitter.state

        assert state1.current == 0
        assert state2.current == 50
