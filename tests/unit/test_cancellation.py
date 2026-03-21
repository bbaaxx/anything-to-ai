"""Unit tests for progress_tracker.cancellation."""

import pytest
from anyfile_to_ai.progress_tracker import CancellationToken, OperationCancelledError


class TestCancellationToken:
    """Unit tests for CancellationToken class."""

    def test_initial_state_not_cancelled(self):
        """Test that token starts in non-cancelled state."""
        token = CancellationToken()
        assert token.is_cancelled is False

    def test_cancel_sets_is_cancelled(self):
        """Test that cancel() sets is_cancelled to True."""
        token = CancellationToken()
        token.cancel()
        assert token.is_cancelled is True

    def test_cancel_is_idempotent(self):
        """Test that calling cancel() multiple times is safe."""
        token = CancellationToken()
        token.cancel()
        token.cancel()
        token.cancel()
        assert token.is_cancelled is True

    def test_reset_returns_to_non_cancelled(self):
        """Test that reset() returns token to non-cancelled state."""
        token = CancellationToken()
        token.cancel()
        assert token.is_cancelled is True
        token.reset()
        assert token.is_cancelled is False

    def test_reset_on_non_cancelled_token(self):
        """Test that reset() on non-cancelled token is safe."""
        token = CancellationToken()
        token.reset()
        assert token.is_cancelled is False

    def test_repr_active(self):
        """Test string representation of active token."""
        token = CancellationToken()
        assert repr(token) == "CancellationToken(active)"

    def test_repr_cancelled(self):
        """Test string representation of cancelled token."""
        token = CancellationToken()
        token.cancel()
        assert repr(token) == "CancellationToken(cancelled)"

    def test_multiple_cancel_reset_cycles(self):
        """Test that token can be reused across multiple cycles."""
        token = CancellationToken()

        # First cycle
        assert token.is_cancelled is False
        token.cancel()
        assert token.is_cancelled is True
        token.reset()
        assert token.is_cancelled is False

        # Second cycle
        token.cancel()
        assert token.is_cancelled is True
        token.reset()
        assert token.is_cancelled is False

        # Third cycle
        assert token.is_cancelled is False


class TestOperationCancelledError:
    """Unit tests for OperationCancelledError exception."""

    def test_default_message(self):
        """Test that exception has default message."""
        error = OperationCancelledError()
        assert error.message == "Operation cancelled"
        assert str(error) == "Operation cancelled"

    def test_custom_message(self):
        """Test that exception accepts custom message."""
        error = OperationCancelledError("PDF extraction cancelled at page 5")
        assert error.message == "PDF extraction cancelled at page 5"
        assert str(error) == "PDF extraction cancelled at page 5"

    def test_is_exception(self):
        """Test that OperationCancelledError is an Exception."""
        error = OperationCancelledError()
        assert isinstance(error, Exception)

    def test_can_be_raised_and_caught(self):
        """Test that exception can be raised and caught."""
        with pytest.raises(OperationCancelledError) as exc_info:
            raise OperationCancelledError("Test cancellation")
        assert exc_info.value.message == "Test cancellation"

    def test_can_be_caught_as_exception(self):
        """Test that exception can be caught as generic Exception."""
        with pytest.raises(Exception) as exc_info:
            raise OperationCancelledError("Test cancellation")
        assert isinstance(exc_info.value, OperationCancelledError)


class TestCancellationTokenIntegration:
    """Integration tests for CancellationToken usage patterns."""

    def test_check_before_operation(self):
        """Test checking token before starting operation."""
        token = CancellationToken()
        token.cancel()

        # Simulate operation that checks before starting
        if token.is_cancelled:
            result = "cancelled"
        else:
            result = "proceed"

        assert result == "cancelled"

    def test_check_during_iteration(self):
        """Test checking token during iteration."""
        token = CancellationToken()
        results = []

        # Simulate processing items
        for i in range(10):
            if token.is_cancelled:
                break
            results.append(i)
            # Cancel after 5 items
            if i == 4:
                token.cancel()

        assert results == [0, 1, 2, 3, 4]

    def test_raise_on_cancel_pattern(self):
        """Test the pattern of raising OperationCancelledError."""
        token = CancellationToken()
        processed = []

        def process_items(items, cancel_token=None):
            for item in items:
                if cancel_token and cancel_token.is_cancelled:
                    raise OperationCancelledError(f"Cancelled at item {item}")
                processed.append(item)

        # Process without cancellation
        process_items([1, 2, 3])
        assert processed == [1, 2, 3]

        # Process with cancellation
        processed.clear()
        token.cancel()
        with pytest.raises(OperationCancelledError):
            process_items([1, 2, 3], cancel_token=token)
        assert processed == []  # No items processed after cancellation

    def test_yield_partial_results_pattern(self):
        """Test the pattern of yielding partial results before raising."""
        token = CancellationToken()

        def process_streaming(items, cancel_token=None):
            results = []
            for item in items:
                if cancel_token and cancel_token.is_cancelled:
                    yield from results  # Yield partial results
                    raise OperationCancelledError(f"Cancelled at item {item}")
                results.append(item * 2)
                yield results[-1]

        # Process without cancellation
        results = list(process_streaming([1, 2, 3]))
        assert results == [2, 4, 6]

        # Process with cancellation after 2 items
        token.cancel()
        results = []
        with pytest.raises(OperationCancelledError):
            for i, result in enumerate(process_streaming([1, 2, 3], cancel_token=token)):
                results.append(result)
                if i == 1:
                    break  # Stop iteration after 2 items
        # No results because token was already cancelled
        assert results == []

    def test_multiple_tokens_independent(self):
        """Test that multiple tokens are independent."""
        token1 = CancellationToken()
        token2 = CancellationToken()

        token1.cancel()
        assert token1.is_cancelled is True
        assert token2.is_cancelled is False

        token2.cancel()
        assert token1.is_cancelled is True
        assert token2.is_cancelled is True

        token1.reset()
        assert token1.is_cancelled is False
        assert token2.is_cancelled is True
