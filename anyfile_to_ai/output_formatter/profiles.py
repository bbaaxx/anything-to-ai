"""Supported profile constants and validation helpers."""

from typing import Final

SUPPORTED_PROFILES: Final[set[str]] = {"pdf", "image", "audio", "text", "document_converter"}


def is_supported_profile(profile: str) -> bool:
    """Return True when the profile is supported."""
    return profile in SUPPORTED_PROFILES


def validate_profile(profile: str) -> str:
    """Validate and return a supported profile value."""
    from .errors import InvalidProfileError

    if not is_supported_profile(profile):
        raise InvalidProfileError(profile)
    return profile
