"""Routing strategy for document conversion inputs."""

from pathlib import Path
from urllib.parse import urlparse
from .exceptions import UnsupportedInputError
from .models import ConversionRoute

PDF_EXTENSIONS = {".pdf"}
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"}
AUDIO_EXTENSIONS = {".mp3", ".wav", ".m4a"}

OFFICE_EXTENSIONS = {
    ".doc",
    ".docx",
    ".ppt",
    ".pptx",
    ".xls",
    ".xlsx",
    ".odt",
    ".ods",
    ".odp",
    ".rtf",
}
MARKITDOWN_EXTENSIONS = OFFICE_EXTENSIONS | {".html", ".htm", ".epub", ".zip"}
YOUTUBE_HOSTS = {"youtube.com", "www.youtube.com", "youtu.be", "www.youtu.be", "m.youtube.com"}


def is_url(source: str) -> bool:
    """Check whether source is an HTTP/HTTPS URL."""
    parsed = urlparse(source)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def _normalized_suffix(source: str) -> str:
    if is_url(source):
        parsed = urlparse(source)
        return Path(parsed.path).suffix.lower()
    return Path(source).suffix.lower()


def determine_route(source: str) -> ConversionRoute:
    """Select a backend for the given input source."""
    if not source or not source.strip():
        msg = "Input source cannot be empty"
        raise UnsupportedInputError(msg)

    if is_url(source):
        host = (urlparse(source).netloc or "").lower()
        suffix = _normalized_suffix(source)

        if host in YOUTUBE_HOSTS:
            return ConversionRoute.MARKITDOWN

        if suffix in MARKITDOWN_EXTENSIONS or not suffix:
            return ConversionRoute.MARKITDOWN

        # Remote non-YouTube URLs are routed to MarkItDown by default.
        return ConversionRoute.MARKITDOWN

    suffix = _normalized_suffix(source)
    if suffix in PDF_EXTENSIONS:
        return ConversionRoute.PDF
    if suffix in IMAGE_EXTENSIONS:
        return ConversionRoute.IMAGE
    if suffix in AUDIO_EXTENSIONS:
        return ConversionRoute.AUDIO
    if suffix in MARKITDOWN_EXTENSIONS:
        return ConversionRoute.MARKITDOWN

    # Unknown local documents default to MarkItDown to avoid dropping valid formats.
    return ConversionRoute.MARKITDOWN
