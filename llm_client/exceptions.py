"""Exception classes for LLM client.

This module defines the exception hierarchy for LLM client errors,
providing specific exception types for different error conditions.
"""

from typing import Optional


class LLMError(Exception):
    """Base exception for all LLM client errors."""

    def __init__(self, message: str, provider: Optional[str] = None, original_error: Optional[Exception] = None):
        """Initialize LLM error.

        Args:
            message: Error message
            provider: Provider name where error occurred
            original_error: Original exception that caused this error
        """
        super().__init__(message)
        self.message = message
        self.provider = provider
        self.original_error = original_error

    def __str__(self):
        """Return string representation of error."""
        parts = [self.message]
        if self.provider:
            parts.append(f"(provider: {self.provider})")
        if self.original_error:
            parts.append(f"(caused by: {type(self.original_error).__name__}: {self.original_error})")
        return " ".join(parts)


class ConfigurationError(LLMError):
    """Invalid configuration error."""

    pass


class ConnectionError(LLMError):
    """Service unreachable or connection failed."""

    pass


class AuthenticationError(LLMError):
    """API key invalid or missing when required."""

    pass


class ModelNotFoundError(LLMError):
    """Requested model not available."""

    pass


class RateLimitError(LLMError):
    """Rate limit exceeded."""

    pass


class TimeoutError(LLMError):
    """Request timed out."""

    pass


class ValidationError(LLMError):
    """Invalid request data."""

    pass


class GenerationError(LLMError):
    """Error during generation."""

    pass
