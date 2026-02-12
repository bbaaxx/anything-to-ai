"""Unit tests for document converter routing and delegation."""

import pytest

from anyfile_to_ai.document_converter import ConversionResult, ConversionRoute, convert_document, determine_route
from anyfile_to_ai.document_converter.exceptions import UnsupportedInputError


@pytest.mark.parametrize(
    ("source", "expected_route"),
    [
        ("/tmp/file.pdf", ConversionRoute.PDF),
        ("/tmp/photo.JPG", ConversionRoute.IMAGE),
        ("/tmp/audio.m4a", ConversionRoute.AUDIO),
        ("/tmp/report.docx", ConversionRoute.MARKITDOWN),
        ("/tmp/page.html", ConversionRoute.MARKITDOWN),
        ("/tmp/book.epub", ConversionRoute.MARKITDOWN),
        ("/tmp/archive.zip", ConversionRoute.MARKITDOWN),
        ("https://youtu.be/dQw4w9WgXcQ", ConversionRoute.MARKITDOWN),
        ("https://example.com/some-path", ConversionRoute.MARKITDOWN),
    ],
)
def test_determine_route_matrix(source, expected_route):
    assert determine_route(source) == expected_route


def test_determine_route_empty_source():
    with pytest.raises(UnsupportedInputError):
        determine_route("")


def test_convert_document_routes_to_pdf_backend(monkeypatch):
    expected = ConversionResult(source="input.pdf", route=ConversionRoute.PDF, content="pdf-content")

    def _fake_pdf(source: str, include_metadata: bool):
        assert source == "input.pdf"
        assert include_metadata is True
        return expected

    monkeypatch.setattr("anyfile_to_ai.document_converter.converter._convert_with_pdf_extractor", _fake_pdf)
    result = convert_document("input.pdf", include_metadata=True)
    assert result == expected


def test_convert_document_routes_to_image_backend(monkeypatch):
    expected = ConversionResult(source="image.png", route=ConversionRoute.IMAGE, content="image-content")

    def _fake_image(source: str, include_metadata: bool):
        assert source == "image.png"
        assert include_metadata is False
        return expected

    monkeypatch.setattr("anyfile_to_ai.document_converter.converter._convert_with_image_processor", _fake_image)
    result = convert_document("image.png")
    assert result == expected


def test_convert_document_routes_to_audio_backend(monkeypatch):
    expected = ConversionResult(source="audio.mp3", route=ConversionRoute.AUDIO, content="audio-content")

    def _fake_audio(source: str, include_metadata: bool):
        assert source == "audio.mp3"
        assert include_metadata is True
        return expected

    monkeypatch.setattr("anyfile_to_ai.document_converter.converter._convert_with_audio_processor", _fake_audio)
    result = convert_document("audio.mp3", include_metadata=True)
    assert result == expected


def test_convert_document_routes_to_markitdown_backend(monkeypatch):
    expected = ConversionResult(source="slides.pptx", route=ConversionRoute.MARKITDOWN, content="md-content")

    def _fake_markitdown(source: str):
        assert source == "slides.pptx"
        return expected

    monkeypatch.setattr("anyfile_to_ai.document_converter.converter._convert_with_markitdown", _fake_markitdown)
    result = convert_document("slides.pptx")
    assert result == expected
