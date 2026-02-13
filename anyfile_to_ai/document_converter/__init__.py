"""Document converter module with intelligent backend routing."""

from .converter import convert_document
from .exceptions import DocumentConversionError, MARKITDOWN_INSTALL_GUIDANCE, MissingDependencyError, UnsupportedInputError
from .models import ConversionResult, ConversionRoute
from .routing import determine_route, is_url

__all__ = [
    "MARKITDOWN_INSTALL_GUIDANCE",
    "ConversionResult",
    "ConversionRoute",
    "DocumentConversionError",
    "MissingDependencyError",
    "UnsupportedInputError",
    "convert_document",
    "determine_route",
    "is_url",
]
