"""Unit tests for document converter routing and delegation."""

import pytest

from anyfile_to_ai.document_converter import ConversionResult, ConversionRoute, convert_document, determine_route
from anyfile_to_ai.document_converter.exceptions import DocumentConversionError, MissingDependencyError, UnsupportedInputError


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


def test_determine_route_whitespace_source_rejected():
    with pytest.raises(UnsupportedInputError, match="source cannot be empty"):
        determine_route("   ")


def test_url_precedence_over_pdf_suffix():
    assert determine_route("https://example.com/file.pdf") == ConversionRoute.MARKITDOWN


def test_unknown_extension_falls_back_to_markitdown():
    assert determine_route("/tmp/archive.custom") == ConversionRoute.MARKITDOWN


def test_non_http_scheme_uses_non_url_routing_rules():
    assert determine_route("ftp://files.local/path/file.pdf") == ConversionRoute.PDF


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


def test_local_routes_do_not_dispatch_to_markitdown(monkeypatch):
    called_routes: list[str] = []

    def _fake_pdf(source: str, include_metadata: bool):
        called_routes.append("pdf")
        return ConversionResult(source=source, route=ConversionRoute.PDF, content="ok")

    def _forbidden_markitdown(source: str):
        message = f"markitdown should not be called for {source}"
        raise AssertionError(message)

    monkeypatch.setattr("anyfile_to_ai.document_converter.converter._convert_with_pdf_extractor", _fake_pdf)
    monkeypatch.setattr("anyfile_to_ai.document_converter.converter._convert_with_markitdown", _forbidden_markitdown)

    result = convert_document("/tmp/local.pdf", include_metadata=False)

    assert result.route == ConversionRoute.PDF
    assert called_routes == ["pdf"]


def test_convert_document_wraps_unexpected_exceptions(monkeypatch):
    def _broken_markitdown(source: str):
        raise ValueError("boom")

    monkeypatch.setattr("anyfile_to_ai.document_converter.converter._convert_with_markitdown", _broken_markitdown)

    with pytest.raises(DocumentConversionError, match="Failed to convert 'input.docx' via route 'markitdown'") as exc:
        convert_document("input.docx")

    assert isinstance(exc.value.__cause__, ValueError)


def test_convert_document_does_not_rewrap_document_conversion_errors(monkeypatch):
    sentinel = MissingDependencyError("install markitdown[all]")

    def _typed_failure(source: str):
        raise sentinel

    monkeypatch.setattr("anyfile_to_ai.document_converter.converter._convert_with_markitdown", _typed_failure)

    with pytest.raises(MissingDependencyError) as exc:
        convert_document("input.docx")

    assert exc.value is sentinel


def test_convert_document_normalizes_required_output_fields(monkeypatch):
    backend_result = ConversionResult(source="different", route=ConversionRoute.PDF, content="backend-value")

    def _fake_pdf(source: str, include_metadata: bool):
        return backend_result

    monkeypatch.setattr("anyfile_to_ai.document_converter.converter._convert_with_pdf_extractor", _fake_pdf)

    result = convert_document("source.pdf")

    assert result.source == "source.pdf"
    assert result.route == ConversionRoute.PDF
    assert result.content == "backend-value"
