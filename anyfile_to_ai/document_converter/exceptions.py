"""Exception hierarchy for document conversion."""


class DocumentConversionError(Exception):
    """Base exception for document conversion failures."""


class UnsupportedInputError(DocumentConversionError):
    """Raised when the input source cannot be routed."""


class MissingDependencyError(DocumentConversionError):
    """Raised when a required optional dependency is unavailable."""
