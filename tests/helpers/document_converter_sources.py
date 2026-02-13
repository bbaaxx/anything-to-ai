"""Shared source fixtures for converter routing tests."""

from anyfile_to_ai.document_converter.models import ConversionRoute

SOURCE_ROUTE_MATRIX: list[tuple[str, ConversionRoute]] = [
    ("/tmp/file.pdf", ConversionRoute.PDF),
    ("/tmp/photo.png", ConversionRoute.IMAGE),
    ("/tmp/speech.wav", ConversionRoute.AUDIO),
    ("/tmp/report.docx", ConversionRoute.MARKITDOWN),
    ("https://example.com/doc.pdf", ConversionRoute.MARKITDOWN),
    ("https://youtu.be/abc123", ConversionRoute.MARKITDOWN),
    ("/tmp/no-extension", ConversionRoute.MARKITDOWN),
]

LOCAL_ONLY_SOURCES: list[str] = [
    "/tmp/file.pdf",
    "/tmp/photo.png",
    "/tmp/speech.wav",
    "/tmp/report.docx",
]
