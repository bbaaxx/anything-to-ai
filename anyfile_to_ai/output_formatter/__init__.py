"""Shared output formatter package."""

from .errors import FormatterError, InvalidPayloadError, InvalidProfileError, UnsupportedFormatError
from .interfaces import format_json, format_markdown, format_output, format_plain
from .markdown import format_audio_timestamp
from .metadata import normalize_metadata
from .profiles import SUPPORTED_PROFILES, is_supported_profile, validate_profile

__all__ = [
    "SUPPORTED_PROFILES",
    "FormatterError",
    "InvalidPayloadError",
    "InvalidProfileError",
    "UnsupportedFormatError",
    "format_audio_timestamp",
    "format_json",
    "format_markdown",
    "format_output",
    "format_plain",
    "is_supported_profile",
    "normalize_metadata",
    "validate_profile",
]
