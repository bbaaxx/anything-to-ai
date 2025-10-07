"""Retry logic with exponential backoff for LLM client.

This module provides retry handling with exponential backoff and configurable delays.
"""

import time
from typing import Any
from collections.abc import Callable


class RetryHandler:
    """Handles retry logic with exponential backoff."""

    def __init__(
        self,
        max_attempts: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 10.0,
        exponential_base: float = 2.0,
    ):
        """Initialize retry handler.

        Args:
            max_attempts: Maximum number of retry attempts (default: 3)
            base_delay: Base delay in seconds before first retry (default: 1.0)
            max_delay: Maximum delay in seconds between retries (default: 10.0)
            exponential_base: Base for exponential backoff calculation (default: 2.0)
        """
        self.max_attempts = max_attempts
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base

    def calculate_delay(self, attempt: int) -> float:
        """Calculate delay for given retry attempt using exponential backoff.

        Args:
            attempt: Current attempt number (0-based)

        Returns:
            Delay in seconds, capped at max_delay
        """
        delay = self.base_delay * (self.exponential_base**attempt)
        return min(delay, self.max_delay)

    def execute_with_retry(
        self,
        func: Callable[[], Any],
        retry_on_exceptions: tuple = (Exception,),
        on_retry: Callable[[Exception, int], None] | None = None,
    ) -> dict[str, Any]:
        """Execute function with retry logic.

        Args:
            func: Function to execute
            retry_on_exceptions: Tuple of exception types to retry on
            on_retry: Optional callback called on each retry with (exception, attempt)

        Returns:
            Dictionary with:
                - result: Function return value if successful
                - success: Boolean indicating success
                - attempts: Number of attempts made
                - error: Exception if all attempts failed

        Raises:
            The last exception if all retry attempts fail
        """
        last_exception = None

        for attempt in range(self.max_attempts):
            try:
                result = func()
                return {"result": result, "success": True, "attempts": attempt + 1, "error": None}
            except retry_on_exceptions as e:
                last_exception = e

                # If this was the last attempt, don't sleep
                if attempt < self.max_attempts - 1:
                    delay = self.calculate_delay(attempt)

                    # Call retry callback if provided
                    if on_retry:
                        on_retry(e, attempt + 1)

                    time.sleep(delay)

        # All attempts failed
        return {"result": None, "success": False, "attempts": self.max_attempts, "error": last_exception}
