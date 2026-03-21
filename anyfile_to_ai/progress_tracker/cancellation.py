"""Cancellation support for long-running operations.

This module provides a simple cancellation mechanism for operations that
support graceful termination. Operations can check for cancellation at
iteration boundaries and yield partial results before raising.

Example:
    >>> token = CancellationToken()
    >>> token.is_cancelled
    False
    >>> token.cancel()
    >>> token.is_cancelled
    True

    >>> # In a streaming operation
    >>> def process_streaming(items, cancel_token=None):
    ...     results = []
    ...     for item in items:
    ...         if cancel_token and cancel_token.is_cancelled:
    ...             yield from results  # Yield partial results
    ...             raise OperationCancelledError("Operation cancelled")
    ...         results.append(process(item))
    ...         yield results[-1]
"""

__all__ = ["CancellationToken", "OperationCancelledError"]


class OperationCancelledError(Exception):
    """Raised when an operation is cancelled via CancellationToken.

    This exception indicates that the operation was intentionally cancelled
    by the user and should be handled appropriately. Operations should
    yield any partial results before raising this exception.

    Attributes:
        message: Human-readable description of the cancellation.
    """

    def __init__(self, message: str = "Operation cancelled"):
        self.message = message
        super().__init__(message)


class CancellationToken:
    """Thread-safe cancellation token for cooperative cancellation.

    A simple mutable token that can be passed to operations to enable
    graceful cancellation. Operations should check `is_cancelled` at
    iteration boundaries and raise `OperationCancelledError` when cancelled.

    This token is designed to work in both synchronous and asynchronous
    contexts without requiring async/await syntax.

    Thread Safety:
        The cancellation state is stored in a mutable attribute. While
        Python's GIL provides some thread safety for simple reads/writes,
        this token is primarily designed for single-threaded use or when
        the cancellation signal comes from a single thread.

    Example:
        >>> token = CancellationToken()
        >>> token.is_cancelled
        False
        >>> token.cancel()
        >>> token.is_cancelled
        True

        >>> # Reset for reuse
        >>> token.reset()
        >>> token.is_cancelled
        False
    """

    def __init__(self) -> None:
        """Initialize a new cancellation token in non-cancelled state."""
        self._cancelled: bool = False

    @property
    def is_cancelled(self) -> bool:
        """Check if cancellation has been requested.

        Returns:
            True if cancel() has been called, False otherwise.
        """
        return self._cancelled

    def cancel(self) -> None:
        """Request cancellation of the operation.

        After calling this method, `is_cancelled` will return True.
        Operations checking this token should yield partial results and
        raise OperationCancelledError.
        """
        self._cancelled = True

    def reset(self) -> None:
        """Reset the token to non-cancelled state for reuse.

        This allows reusing the same token instance for multiple operations.
        """
        self._cancelled = False

    def __repr__(self) -> str:
        """Return a string representation of the token state."""
        status = "cancelled" if self._cancelled else "active"
        return f"CancellationToken({status})"
