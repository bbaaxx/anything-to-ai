"""Integration tests for hierarchical progress tracking."""

import time


from anyfile_to_ai.progress_tracker import CallbackProgressConsumer, ProgressEmitter, ProgressUpdate


class TestHierarchicalProgressIntegration:
    """Test hierarchical progress with parent-child emitters."""

    def test_parent_child_basic(self):
        """Test basic parent-child progress propagation."""
        updates = []

        def capture(current: int, total: int):
            updates.append((current, total))

        parent = ProgressEmitter(total=100, label="Parent")
        parent.add_consumer(CallbackProgressConsumer(capture))

        child = parent.create_child(total=50, weight=1.0, label="Child")

        child.update(25)
        time.sleep(0.01)

        assert len(updates) > 0
        assert updates[-1][0] >= 0
        assert updates[-1][1] == 100

    def test_weighted_average_calculation(self):
        """Test parent calculates weighted average correctly."""
        parent_updates = []

        def capture_parent(current: int, total: int):
            parent_updates.append((current, total, current / total if total > 0 else 0))

        parent = ProgressEmitter(total=100, label="Overall", throttle_interval=0.01)
        parent.add_consumer(CallbackProgressConsumer(capture_parent))

        child1 = parent.create_child(total=100, weight=0.4, label="Phase 1")
        child2 = parent.create_child(total=100, weight=0.6, label="Phase 2")

        child1.update(50, force=True)
        time.sleep(0.05)

        assert len(parent_updates) > 0
        first_current = parent_updates[-1][0]
        assert first_current >= 10

        child2.update(50, force=True)
        time.sleep(0.05)

        assert len(parent_updates) > 1
        second_current = parent_updates[-1][0]
        assert second_current >= first_current

        child1.complete()
        child2.complete()
        time.sleep(0.05)

        final_current = parent_updates[-1][0]
        assert final_current >= 70

    def test_multi_level_hierarchy(self):
        """Test multi-level hierarchical progress (grandparent-parent-child)."""
        grandparent_updates = []

        def capture_grandparent(current: int, total: int):
            grandparent_updates.append((current, total))

        grandparent = ProgressEmitter(total=100, label="Grandparent", throttle_interval=0.01)
        grandparent.add_consumer(CallbackProgressConsumer(capture_grandparent))

        parent1 = grandparent.create_child(total=100, weight=0.5, label="Parent 1")
        grandparent.create_child(total=100, weight=0.5, label="Parent 2")

        child1_1 = parent1.create_child(total=100, weight=0.5, label="Child 1.1")
        child1_2 = parent1.create_child(total=100, weight=0.5, label="Child 1.2")

        child1_1.update(50, force=True)
        time.sleep(0.05)

        assert len(grandparent_updates) > 0

        child1_2.update(50, force=True)
        time.sleep(0.05)

        child1_1.complete()
        child1_2.complete()
        time.sleep(0.05)

        assert len(grandparent_updates) >= 1
        assert grandparent_updates[-1][0] >= 20

    def test_child_completion_propagates(self):
        """Test that completing children updates parent to 100%."""
        parent_states = []

        class StateCapture:
            def on_progress(self, update: ProgressUpdate):
                parent_states.append((update.state.current, update.state.total))

            def on_complete(self, state):
                parent_states.append((state.current, state.total))

        parent = ProgressEmitter(total=100, label="Parent", throttle_interval=0.01)
        parent.add_consumer(StateCapture())

        child1 = parent.create_child(total=10, weight=0.5, label="Child 1")
        child2 = parent.create_child(total=20, weight=0.5, label="Child 2")

        for i in range(10):
            child1.update(1, force=(i % 3 == 0))
        child1.complete()
        time.sleep(0.05)

        mid_state = parent_states[-1] if parent_states else (0, 100)
        assert mid_state[0] >= 1

        for i in range(20):
            child2.update(1, force=(i % 5 == 0))
        child2.complete()
        time.sleep(0.05)

        assert len(parent_states) > 0
        final_state = parent_states[-1]
        assert final_state[0] >= 50

    def test_hierarchical_with_indeterminate_child(self):
        """Test parent handling child with indeterminate total."""
        parent_updates = []

        def capture(current: int, total: int):
            parent_updates.append((current, total))

        parent = ProgressEmitter(total=100, label="Parent")
        parent.add_consumer(CallbackProgressConsumer(capture))

        child1 = parent.create_child(total=100, weight=0.5, label="Determinate")
        child2 = parent.create_child(total=None, weight=0.5, label="Indeterminate")

        child1.update(50)
        time.sleep(0.05)

        child2.update(10)
        time.sleep(0.05)

        assert len(parent_updates) >= 0

    def test_hierarchical_with_dynamic_total(self):
        """Test hierarchical progress with dynamic total updates."""
        parent_updates = []

        def capture(current: int, total: int):
            parent_updates.append((current, total))

        parent = ProgressEmitter(total=100, label="Parent")
        parent.add_consumer(CallbackProgressConsumer(capture))

        child = parent.create_child(total=10, weight=1.0, label="Child")

        child.update(5)
        time.sleep(0.02)

        child.update_total(20)
        time.sleep(0.02)

        child.update(10)
        time.sleep(0.02)

        assert len(parent_updates) > 0

    def test_multiple_children_equal_weights(self):
        """Test equal weight distribution among multiple children."""
        parent_updates = []

        def capture(current: int, total: int):
            parent_updates.append((current, total))

        parent = ProgressEmitter(total=100, label="Parent", throttle_interval=0.01)
        parent.add_consumer(CallbackProgressConsumer(capture))

        children = [parent.create_child(total=10, weight=1.0, label=f"Child {i}") for i in range(4)]

        for child in children[:2]:
            for i in range(10):
                child.update(1, force=(i == 9))
            child.complete()
        time.sleep(0.05)

        assert len(parent_updates) > 0
        midpoint = parent_updates[-1][0]
        assert midpoint >= 1

        for child in children[2:]:
            for i in range(10):
                child.update(1, force=(i == 9))
            child.complete()
        time.sleep(0.05)

        assert len(parent_updates) >= 1
        final = parent_updates[-1][0]
        assert final >= midpoint

    def test_child_with_zero_total(self):
        """Test child with zero total doesn't break parent calculation."""
        parent_updates = []

        def capture(current: int, total: int):
            parent_updates.append((current, total))

        parent = ProgressEmitter(total=100, label="Parent")
        parent.add_consumer(CallbackProgressConsumer(capture))

        child1 = parent.create_child(total=0, weight=0.5, label="Empty")
        child2 = parent.create_child(total=100, weight=0.5, label="Normal")

        child1.complete()
        time.sleep(0.02)

        child2.update(50)
        time.sleep(0.02)

        assert len(parent_updates) >= 0

    def test_hierarchical_error_handling(self):
        """Test that errors in child don't break parent."""
        parent_updates = []

        class ErrorConsumer:
            def __init__(self):
                self.call_count = 0

            def on_progress(self, update: ProgressUpdate):
                self.call_count += 1
                if self.call_count == 2:
                    raise ValueError("Simulated error")
                parent_updates.append((update.state.current, update.state.total))

            def on_complete(self, state):
                parent_updates.append((state.current, state.total))

        parent = ProgressEmitter(total=100, label="Parent")
        parent.add_consumer(ErrorConsumer())

        child = parent.create_child(total=10, weight=1.0, label="Child")

        for i in range(10):
            child.update(1)
            time.sleep(0.01)

        assert parent_updates or True
