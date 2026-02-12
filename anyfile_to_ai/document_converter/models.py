"""Data models for document conversion routing."""

from dataclasses import dataclass
from enum import Enum
from typing import Any


class ConversionRoute(str, Enum):
    """Conversion backends supported by the document converter."""

    PDF = "pdf_extractor"
    IMAGE = "image_processor"
    AUDIO = "audio_processor"
    MARKITDOWN = "markitdown"


@dataclass
class ConversionResult:
    """Normalized conversion result returned by convert_document."""

    source: str
    route: ConversionRoute
    content: str
    metadata: dict[str, Any] | None = None
    raw_result: Any | None = None
