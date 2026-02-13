"""Exception hierarchy for document conversion."""

MARKITDOWN_INSTALL_GUIDANCE = "markitdown is required for this input route. Install with: pip install 'markitdown[all]'"


class DocumentConversionError(Exception):
    """Base exception for document conversion failures."""


class UnsupportedInputError(DocumentConversionError):
    """Raised when the input source cannot be routed."""


class MissingDependencyError(DocumentConversionError):
    """Raised when a required optional dependency is unavailable."""
