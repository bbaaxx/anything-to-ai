"""Unified document conversion API with backend routing."""

from typing import Any
from .exceptions import DocumentConversionError, MissingDependencyError
from .models import ConversionResult, ConversionRoute
from .routing import determine_route


def _extract_markitdown_text(result: Any) -> str:
    text = getattr(result, "text_content", None)
    if isinstance(text, str):
        return text
    if isinstance(result, str):
        return result
    if hasattr(result, "__str__"):
        return str(result)
    return ""


def _extract_markitdown_metadata(result: Any) -> dict[str, Any] | None:
    metadata: dict[str, Any] = {}

    for field_name in ("title", "source_path", "content_type", "url"):
        value = getattr(result, field_name, None)
        if value:
            metadata[field_name] = value

    if not metadata:
        return None
    return metadata


def _convert_with_pdf_extractor(source: str, include_metadata: bool) -> ConversionResult:
    from anyfile_to_ai.pdf_extractor import extract_text

    pdf_result = extract_text(source, include_metadata=include_metadata)
    content = "\n\n".join(page.text for page in pdf_result.pages if page.text).strip()
    return ConversionResult(source=source, route=ConversionRoute.PDF, content=content, metadata=pdf_result.metadata, raw_result=pdf_result)


def _convert_with_image_processor(source: str, include_metadata: bool) -> ConversionResult:
    from anyfile_to_ai.image_processor import process_image

    image_result = process_image(source, include_metadata=include_metadata)
    return ConversionResult(
        source=source,
        route=ConversionRoute.IMAGE,
        content=image_result.description,
        metadata=image_result.metadata,
        raw_result=image_result,
    )


def _convert_with_audio_processor(source: str, include_metadata: bool) -> ConversionResult:
    from anyfile_to_ai.audio_processor import process_audio

    audio_result = process_audio(source, include_metadata=include_metadata)
    return ConversionResult(
        source=source,
        route=ConversionRoute.AUDIO,
        content=audio_result.text,
        metadata=audio_result.metadata,
        raw_result=audio_result,
    )


def _convert_with_markitdown(source: str) -> ConversionResult:
    try:
        from markitdown import MarkItDown
    except ImportError as exc:
        msg = "markitdown is required for this input route. Install with: pip install 'markitdown[all]'"
        raise MissingDependencyError(msg) from exc

    converter = MarkItDown()
    md_result = converter.convert(source)

    return ConversionResult(
        source=source,
        route=ConversionRoute.MARKITDOWN,
        content=_extract_markitdown_text(md_result),
        metadata=_extract_markitdown_metadata(md_result),
        raw_result=md_result,
    )


def convert_document(source: str, include_metadata: bool = False) -> ConversionResult:
    """Convert a file path or URL into normalized text content."""
    route = determine_route(source)

    try:
        if route == ConversionRoute.PDF:
            return _convert_with_pdf_extractor(source, include_metadata)
        if route == ConversionRoute.IMAGE:
            return _convert_with_image_processor(source, include_metadata)
        if route == ConversionRoute.AUDIO:
            return _convert_with_audio_processor(source, include_metadata)
        return _convert_with_markitdown(source)
    except DocumentConversionError:
        raise
    except Exception as exc:
        msg = f"Failed to convert '{source}' via route '{route.value}': {exc!s}"
        raise DocumentConversionError(msg) from exc
