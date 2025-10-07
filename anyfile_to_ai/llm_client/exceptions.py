"""Exception classes for LLM client.

This module defines the exception hierarchy for LLM client errors,
providing specific exception types for different error conditions.
"""


class LLMError(Exception):
    """Base exception for all LLM client errors."""

    def __init__(self, message: str, provider: str | None = None, original_error: Exception | None = None):
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


class ConnectionError(LLMError):
    """Service unreachable or connection failed."""


class AuthenticationError(LLMError):
    """API key invalid or missing when required."""


class ModelNotFoundError(LLMError):
    """Requested model not available."""


class RateLimitError(LLMError):
    """Rate limit exceeded."""


class TimeoutError(LLMError):
    """Request timed out."""


class ValidationError(LLMError):
    """Invalid request data."""


class GenerationError(LLMError):
    """Error during generation."""
