"""Formatter layer errors and error-response helpers."""

from dataclasses import dataclass


@dataclass(slots=True)
class FormatterError(Exception):
    """Base formatter error with stable code/message payload."""

    code: str
    message: str

    def to_dict(self) -> dict[str, str]:
        return {"code": self.code, "message": self.message}


class UnsupportedFormatError(FormatterError):
    """Raised when the requested output format is unsupported."""

    def __init__(self, output_format: str):
        super().__init__(code="unsupported_format", message=f"Unsupported output format: {output_format}")


class InvalidProfileError(FormatterError):
    """Raised when an unsupported profile is requested."""

    def __init__(self, profile: str):
        super().__init__(code="invalid_profile", message=f"Unsupported formatter profile: {profile}")


class InvalidPayloadError(FormatterError):
    """Raised when the payload does not satisfy formatter requirements."""

    def __init__(self, detail: str):
        super().__init__(code="invalid_payload", message=detail)


def map_exception(exc: Exception) -> FormatterError:
    """Map arbitrary exceptions into stable formatter-layer errors."""
    if isinstance(exc, FormatterError):
        return exc
    return InvalidPayloadError(str(exc) or "Invalid formatter payload")
