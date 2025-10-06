"""Progress emitter for state management and update emission."""

import asyncio
import logging
import time
from typing import AsyncIterator, List, Optional

from .models import ProgressConsumer, ProgressState, ProgressUpdate, UpdateType

logger = logging.getLogger(__name__)


class ProgressEmitter:
    """Mutable progress state manager that generates ProgressUpdate events."""

    def __init__(self, total: Optional[int], label: Optional[str] = None, throttle_interval: float = 0.1) -> None:
        """
        Create progress emitter.

        Args:
            total: Total items to process (None for indeterminate)
            label: Human-readable label
            throttle_interval: Min seconds between updates (default 0.1 = 10 Hz)

        Raises:
            ValueError: If total < 0
        """
        if total is not None and total < 0:
            raise ValueError("total must be non-negative")

        self._current = 0
        self._total = total
        self._label = label
        self._consumers: List[ProgressConsumer] = []
        self._children: List["ProgressEmitter"] = []
        self._weights: List[float] = []
        self._last_update_time = 0.0
        self._throttle_interval = throttle_interval
        self._update_queue: Optional[asyncio.Queue] = None

    @property
    def current(self) -> int:
        """Current progress value (read-only)."""
        return self._current

    @property
    def total(self) -> Optional[int]:
        """Total items (read-only)."""
        return self._total

    @property
    def state(self) -> ProgressState:
        """Current state snapshot."""
        return ProgressState(current=self._current, total=self._total, label=self._label, timestamp=time.monotonic())

    def update(self, increment: int = 1, *, force: bool = False) -> None:
        """
        Increment progress counter.

        Args:
            increment: Items to add (default 1)
            force: Skip throttling if True (default False)

        Raises:
            ValueError: If update would make current > total
        """
        new_current = self._current + increment
        if new_current < 0:
            raise ValueError("update would make current negative")
        if self._total is not None and new_current > self._total:
            raise ValueError("update would exceed total")

        self._current = new_current
        update_type = UpdateType.STARTED if self._current == increment and self._current > 0 else UpdateType.PROGRESS
        is_first_update = update_type == UpdateType.STARTED

        if self._should_notify(force or is_first_update):
            self._notify_consumers(update_type, increment, force or is_first_update)

    def set_current(self, value: int, *, force: bool = False) -> None:
        """
        Set absolute progress value.

        Args:
            value: New current value
            force: Skip throttling if True

        Raises:
            ValueError: If value < 0 or value > total
        """
        if value < 0:
            raise ValueError("value must be non-negative")
        if self._total is not None and value > self._total:
            raise ValueError("value cannot exceed total")

        delta = value - self._current
        self._current = value
        update_type = UpdateType.STARTED if value == 0 else UpdateType.PROGRESS

        if self._should_notify(force):
            self._notify_consumers(update_type, delta, force)

    def update_total(self, new_total: Optional[int]) -> None:
        """
        Update total count (dynamic discovery).
        Always forces notification regardless of throttling.

        Args:
            new_total: New total value (None for indeterminate)

        Raises:
            ValueError: If new_total < current
        """
        if new_total is not None and new_total < self._current:
            raise ValueError("new total cannot be less than current")

        self._total = new_total
        self._notify_consumers(UpdateType.TOTAL_CHANGED, 0, force=True)

    def complete(self) -> None:
        """
        Mark progress as complete (sets current=total).
        Always forces notification.

        Raises:
            ValueError: If total is None
        """
        if self._total is None:
            raise ValueError("cannot complete indeterminate progress")

        self._current = self._total
        self._notify_consumers(UpdateType.COMPLETED, 0, force=True)

    def add_consumer(self, consumer: ProgressConsumer) -> None:
        """Register consumer to receive updates."""
        self._consumers.append(consumer)

    def remove_consumer(self, consumer: ProgressConsumer) -> None:
        """Unregister consumer."""
        if consumer in self._consumers:
            self._consumers.remove(consumer)

    def create_child(self, total: Optional[int], weight: float = 1.0, label: Optional[str] = None) -> "ProgressEmitter":
        """
        Create child emitter for hierarchical progress.

        Args:
            total: Child's total items
            weight: Relative weight for parent calculation (default 1.0)
            label: Child's label

        Returns:
            Child emitter (updates propagate to parent)

        Raises:
            ValueError: If weight <= 0
        """
        if weight <= 0:
            raise ValueError("weight must be positive")

        child = ProgressEmitter(total, label, self._throttle_interval)
        self._children.append(child)
        self._weights.append(weight)

        class ChildConsumer:
            def __init__(self, parent):
                self.parent = parent

            def on_progress(self, update: ProgressUpdate) -> None:
                self.parent._recalculate_from_children()

            def on_complete(self, state: ProgressState) -> None:
                self.parent._recalculate_from_children()

        child.add_consumer(ChildConsumer(self))
        return child

    async def stream(self) -> AsyncIterator[ProgressUpdate]:
        """
        Async generator yielding progress updates.

        Yields:
            ProgressUpdate events as they occur
        """
        if self._update_queue is None:
            self._update_queue = asyncio.Queue()

        class StreamConsumer:
            def __init__(self, queue):
                self.queue = queue

            def on_progress(self, update: ProgressUpdate) -> None:
                try:
                    self.queue.put_nowait(update)
                except asyncio.QueueFull:
                    pass

            def on_complete(self, state: ProgressState) -> None:
                try:
                    self.queue.put_nowait(ProgressUpdate(state, 0, UpdateType.COMPLETED))
                except asyncio.QueueFull:
                    pass

        consumer = StreamConsumer(self._update_queue)
        self.add_consumer(consumer)

        try:
            while True:
                update = await self._update_queue.get()
                yield update
                if update.update_type == UpdateType.COMPLETED:
                    break
        finally:
            self.remove_consumer(consumer)

    def _should_notify(self, force: bool) -> bool:
        """Check if notification should be sent based on throttling."""
        if force:
            self._last_update_time = time.monotonic()
            return True
        now = time.monotonic()
        if now - self._last_update_time >= self._throttle_interval:
            self._last_update_time = now
            return True
        return False

    def _notify_consumers(self, update_type: UpdateType, delta: int, force: bool = False) -> None:
        """Notify all consumers with exception handling."""
        if not force and not self._should_notify(force):
            return

        state = self.state
        update = ProgressUpdate(state, delta, update_type)

        for consumer in self._consumers:
            try:
                consumer.on_progress(update)
                if update_type == UpdateType.COMPLETED:
                    consumer.on_complete(state)
            except Exception as e:
                logger.error(f"Progress consumer error: {e}", exc_info=True)

    def _recalculate_from_children(self) -> None:
        """Recalculate parent progress based on weighted average of children."""
        if not self._children:
            return

        total_weight = sum(self._weights)
        if total_weight == 0:
            return

        normalized_weights = [w / total_weight for w in self._weights]
        weighted_sum = 0.0

        for child, weight in zip(self._children, normalized_weights):
            if child.total is not None and child.total > 0:
                child_percentage = (child.current / child.total) * 100.0
                weighted_sum += child_percentage * weight

        if self._total is not None and self._total > 0:
            self._current = int((weighted_sum / 100.0) * self._total)
            self._notify_consumers(UpdateType.PROGRESS, 0)
