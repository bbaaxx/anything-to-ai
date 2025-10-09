"""Unit tests for RetryHandler."""

import pytest
from anyfile_to_ai.llm_client.retry import RetryHandler


class TestRetryHandler:
    """Test cases for RetryHandler functionality."""

    def test_retry_handler_initialization(self):
        """RetryHandler can be initialized with parameters."""
        handler = RetryHandler(max_attempts=5, base_delay=2.0, max_delay=20.0, exponential_base=3.0)

        assert handler.max_attempts == 5
        assert handler.base_delay == 2.0
        assert handler.max_delay == 20.0
        assert handler.exponential_base == 3.0

    def test_calculate_delay_exponential_backoff(self):
        """Delay increases exponentially with attempts."""
        handler = RetryHandler(base_delay=1.0, exponential_base=2.0)

        assert handler.calculate_delay(0) == 1.0  # 1.0 * 2^0
        assert handler.calculate_delay(1) == 2.0  # 1.0 * 2^1
        assert handler.calculate_delay(2) == 4.0  # 1.0 * 2^2
        assert handler.calculate_delay(3) == 8.0  # 1.0 * 2^3

    def test_calculate_delay_respects_max_delay(self):
        """Delay is capped at max_delay."""
        handler = RetryHandler(base_delay=1.0, max_delay=5.0, exponential_base=2.0)

        # 1.0 * 2^3 = 8.0, but should be capped at 5.0
        assert handler.calculate_delay(3) == 5.0

    def test_execute_with_retry_success_first_attempt(self):
        """Function succeeds on first attempt."""
        handler = RetryHandler()

        def successful_func():
            return "success"

        result = handler.execute_with_retry(successful_func)

        assert result["success"] is True
        assert result["result"] == "success"
        assert result["attempts"] == 1
        assert result["error"] is None

    def test_execute_with_retry_success_after_retries(self):
        """Function succeeds after retries."""
        handler = RetryHandler(max_attempts=3, base_delay=0.01)
        call_count = 0

        def flaky_func():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                msg = "Temporary error"
                raise ValueError(msg)
            return "success"

        result = handler.execute_with_retry(flaky_func, retry_on_exceptions=(ValueError,))

        assert result["success"] is True
        assert result["result"] == "success"
        assert result["attempts"] == 3
        assert result["error"] is None

    def test_execute_with_retry_all_attempts_fail(self):
        """Function fails after all retry attempts."""
        handler = RetryHandler(max_attempts=3, base_delay=0.01)

        def always_fails():
            msg = "Always fails"
            raise ValueError(msg)

        result = handler.execute_with_retry(always_fails, retry_on_exceptions=(ValueError,))

        assert result["success"] is False
        assert result["result"] is None
        assert result["attempts"] == 3
        assert isinstance(result["error"], ValueError)

    def test_execute_with_retry_on_retry_callback(self):
        """on_retry callback is called on each retry."""
        handler = RetryHandler(max_attempts=3, base_delay=0.01)
        retry_calls = []

        def failing_func():
            msg = "Error"
            raise ValueError(msg)

        def on_retry_callback(exception, attempt):
            retry_calls.append((exception, attempt))

        handler.execute_with_retry(failing_func, retry_on_exceptions=(ValueError,), on_retry=on_retry_callback)

        # Should be called for attempts 1 and 2 (not after the last attempt)
        assert len(retry_calls) == 2
        assert retry_calls[0][1] == 1
        assert retry_calls[1][1] == 2

    def test_execute_with_retry_does_not_retry_unexpected_exceptions(self):
        """Function does not retry on unexpected exception types."""
        handler = RetryHandler(max_attempts=3)

        def raises_unexpected():
            msg = "Not retryable"
            raise TypeError(msg)

        # Should raise immediately without retries since TypeError is not in retry_on_exceptions
        with pytest.raises(TypeError):
            handler.execute_with_retry(raises_unexpected, retry_on_exceptions=(ValueError,))
