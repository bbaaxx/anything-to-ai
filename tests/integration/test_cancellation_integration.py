"""Integration tests for cancellation flow across modules."""

import pytest
from unittest.mock import MagicMock, patch

from anyfile_to_ai.progress_tracker import CancellationToken, OperationCancelledError


class TestCancellationIntegration:
    """Integration tests for cancellation across modules."""

    @pytest.fixture
    def cancel_token(self):
        """Create a fresh cancellation token for each test."""
        return CancellationToken()

    def test_token_state_transitions(self, cancel_token):
        """Test that token state transitions correctly."""
        # Initial state
        assert cancel_token.is_cancelled is False

        # After cancel
        cancel_token.cancel()
        assert cancel_token.is_cancelled is True

        # After reset
        cancel_token.reset()
        assert cancel_token.is_cancelled is False

    def test_token_reuse_across_operations(self, cancel_token):
        """Test that token can be reused across multiple operations."""
        # First operation - cancelled
        cancel_token.cancel()
        assert cancel_token.is_cancelled is True

        # Reset for second operation
        cancel_token.reset()
        assert cancel_token.is_cancelled is False

        # Second operation - not cancelled
        cancel_token.cancel()
        assert cancel_token.is_cancelled is True

    def test_exception_propagation(self, cancel_token):
        """Test that OperationCancelledError propagates correctly."""
        cancel_token.cancel()

        def operation(token):
            if token.is_cancelled:
                raise OperationCancelledError("Operation cancelled")
            return "success"

        with pytest.raises(OperationCancelledError) as exc_info:
            operation(cancel_token)

        assert "cancelled" in str(exc_info.value).lower()

    def test_partial_results_before_cancellation(self, cancel_token):
        """Test that partial results are yielded before cancellation."""

        def streaming_operation(items, token):
            results = []
            for item in items:
                if token and token.is_cancelled:
                    yield from results
                    raise OperationCancelledError(f"Cancelled at item {item}")
                results.append(item * 2)
                yield results[-1]

        # Process without cancellation
        results = list(streaming_operation([1, 2, 3], None))
        assert results == [2, 4, 6]

        # Process with cancellation
        cancel_token.cancel()
        with pytest.raises(OperationCancelledError):
            list(streaming_operation([1, 2, 3], cancel_token))

    def test_cleanup_on_cancellation(self, cancel_token):
        """Test that resources are cleaned up on cancellation."""
        cleanup_called = False

        def operation_with_cleanup(token):
            try:
                if token and token.is_cancelled:
                    raise OperationCancelledError("Cancelled")
                return "success"
            finally:
                nonlocal cleanup_called
                cleanup_called = True

        cancel_token.cancel()
        with pytest.raises(OperationCancelledError):
            operation_with_cleanup(cancel_token)

        assert cleanup_called is True

    def test_multiple_independent_tokens(self):
        """Test that multiple tokens are independent."""
        token1 = CancellationToken()
        token2 = CancellationToken()

        # Cancel only token1
        token1.cancel()

        assert token1.is_cancelled is True
        assert token2.is_cancelled is False

        # Cancel token2
        token2.cancel()

        assert token1.is_cancelled is True
        assert token2.is_cancelled is True

        # Reset token1
        token1.reset()

        assert token1.is_cancelled is False
        assert token2.is_cancelled is True

    def test_cancellation_in_nested_operations(self, cancel_token):
        """Test cancellation in nested operation calls."""

        def inner_operation(token):
            if token and token.is_cancelled:
                raise OperationCancelledError("Inner cancelled")
            return "inner_result"

        def outer_operation(token):
            inner_result = inner_operation(token)
            if token and token.is_cancelled:
                raise OperationCancelledError("Outer cancelled")
            return f"outer_{inner_result}"

        # Without cancellation
        result = outer_operation(None)
        assert result == "outer_inner_result"

        # With cancellation
        cancel_token.cancel()
        with pytest.raises(OperationCancelledError):
            outer_operation(cancel_token)

    def test_cancellation_with_error_handling(self, cancel_token):
        """Test that cancellation works with error handling patterns."""

        def operation_with_error_handling(token):
            try:
                if token and token.is_cancelled:
                    raise OperationCancelledError("Cancelled")
                # Simulate some work
                return "result"
            except OperationCancelledError:
                # Re-raise cancellation
                raise
            except Exception as e:
                # Handle other errors
                return f"error: {e}"

        cancel_token.cancel()
        with pytest.raises(OperationCancelledError):
            operation_with_error_handling(cancel_token)

    def test_cancellation_timing(self, cancel_token):
        """Test that cancellation is checked at the right time."""
        processed_items = []

        def timed_operation(items, token):
            for i, item in enumerate(items):
                # Check cancellation at iteration boundary
                if token and token.is_cancelled:
                    raise OperationCancelledError(f"Cancelled at item {i}")
                processed_items.append(item)
                # Cancel after processing 2 items
                if i == 1:
                    token.cancel()
                yield item

        # Process items with delayed cancellation
        cancel_token.reset()
        results = []
        with pytest.raises(OperationCancelledError):
            for result in timed_operation([1, 2, 3, 4], cancel_token):
                results.append(result)

        # Should have processed items before cancellation was checked
        assert len(processed_items) >= 2
        assert len(results) >= 2


class TestCancellationWithProgress:
    """Tests for cancellation with progress tracking."""

    def test_cancellation_preserves_progress_state(self):
        """Test that cancellation preserves progress state."""
        token = CancellationToken()
        progress_items = []

        def operation_with_progress(items, token, progress_callback):
            for i, item in enumerate(items):
                if token and token.is_cancelled:
                    raise OperationCancelledError("Cancelled")
                progress_callback(i + 1, len(items))
                yield item

        def track_progress(current, total):
            progress_items.append((current, total))

        # Process with cancellation
        token.cancel()
        with pytest.raises(OperationCancelledError):
            list(operation_with_progress([1, 2, 3], token, track_progress))

        # Progress should be empty (cancelled before processing)
        assert len(progress_items) == 0

    def test_cancellation_after_partial_progress(self):
        """Test cancellation after partial progress."""
        token = CancellationToken()
        progress_items = []

        def operation_with_progress(items, token, progress_callback):
            for i, item in enumerate(items):
                progress_callback(i + 1, len(items))
                if token and token.is_cancelled:
                    raise OperationCancelledError("Cancelled")
                yield item

        def track_progress(current, total):
            progress_items.append((current, total))
            # Cancel after 2 items
            if current == 2:
                token.cancel()

        # Process with delayed cancellation
        results = []
        with pytest.raises(OperationCancelledError):
            for result in operation_with_progress([1, 2, 3, 4], token, track_progress):
                results.append(result)

        # Should have recorded progress for items processed
        # Note: Progress is recorded before yield, so we get progress for items before cancellation
        assert len(progress_items) >= 1
        # Results may be less than progress_items because cancellation happens after progress callback
        assert len(results) >= 1


class TestCancellationEdgeCases:
    """Tests for edge cases in cancellation."""

    def test_none_token_is_safe(self):
        """Test that None token is handled safely."""

        def operation(token):
            if token and token.is_cancelled:
                raise OperationCancelledError("Cancelled")
            return "success"

        # Should work with None token
        result = operation(None)
        assert result == "success"

    def test_token_in_generator(self):
        """Test cancellation in generator function."""
        token = CancellationToken()

        def generator_operation(items, token):
            for item in items:
                if token and token.is_cancelled:
                    return  # Early exit
                yield item

        # Process without cancellation
        results = list(generator_operation([1, 2, 3], token))
        assert results == [1, 2, 3]

        # Process with cancellation
        token.cancel()
        results = list(generator_operation([1, 2, 3], token))
        assert results == []

    def test_token_in_context_manager(self):
        """Test cancellation in context manager pattern."""
        token = CancellationToken()
        entered = False
        exited = False

        class ManagedOperation:
            def __init__(self, token):
                self.token = token

            def __enter__(self):
                nonlocal entered
                entered = True
                if self.token and self.token.is_cancelled:
                    raise OperationCancelledError("Cancelled on enter")
                return self

            def __exit__(self, exc_type, exc_val, exc_tb):
                nonlocal exited
                exited = True
                return False

        # Without cancellation
        with ManagedOperation(None):
            pass
        assert entered is True
        assert exited is True

        # With cancellation - exception raised in __enter__ means __exit__ is not called
        entered = False
        exited = False
        token.cancel()
        with pytest.raises(OperationCancelledError):
            with ManagedOperation(token):
                pass
        assert entered is True
        assert exited is False  # __exit__ not called when exception in __enter__

    def test_concurrent_token_access(self):
        """Test that token can be accessed concurrently (basic check)."""
        import threading

        token = CancellationToken()
        results = []

        def worker():
            results.append(token.is_cancelled)

        # Start threads before cancellation
        threads = [threading.Thread(target=worker) for _ in range(5)]
        for t in threads:
            t.start()

        # Cancel
        token.cancel()

        # Start more threads after cancellation
        threads2 = [threading.Thread(target=worker) for _ in range(5)]
        for t in threads2:
            t.start()

        # Wait for all threads
        for t in threads + threads2:
            t.join()

        # First 5 should see False, last 5 should see True
        assert results[:5] == [False] * 5
        assert results[5:] == [True] * 5
