"""Custom exceptions for text summarizer module."""


class SummarizerError(Exception):
    """Base exception for text summarizer module."""

    pass


class InvalidInputError(SummarizerError):
    """Raised when input is invalid (empty, non-UTF-8, etc.)."""

    pass


class LLMError(SummarizerError):
    """Raised when LLM client fails (API error, timeout, etc.)."""

    pass


class ValidationError(SummarizerError):
    """Raised when output validation fails (e.g., fewer than 3 tags)."""

    pass
